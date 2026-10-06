"""
요리조리 · AI Hub 「농산물 품질(QC) 이미지」 → 재료만 오려 낸 PNG  (내 PC에서 실행)

AI Hub는 해외 IP(Colab 포함)에서 다운로드를 막는다. 그래서
  1) AI Hub 웹에서 Validation/원천데이터 zip을 내 PC에 받는다 (한 폴더에 모아 둔다)
  2) 이 스크립트로 zip 안의 사진을 바로 읽어 재료만 오려 낸다 (압축을 풀지 않아 디스크를 더 쓰지 않는다)
  3) 결과 qc_cutouts.zip(수백 MB~1GB)만 구글 드라이브 MyDrive/yorijori/qc/ 에 올린다
  4) Colab에서 셀 ③-B(압축 풀기) → ④ 확인 → ⑤ 합성 → ⑥ data.yaml

준비 (한 번만):
  pip install opencv-python numpy

실행:
  python qc_local.py  "D:\\aihub\\원천데이터"      ← zip들이 들어 있는 폴더
  (중간에 꺼도 다시 실행하면 이미 만든 파일은 건너뛴다)
"""
import sys, zipfile, time
from pathlib import Path
import numpy as np, cv2

ZIP_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
OUT = Path(__file__).resolve().parent / 'qc_out'
CUT = OUT / 'cutouts'

ITEM_MAP = {                     # AI Hub 파일 이름 앞부분(소문자) → 우리 클래스
    'radish': 'radish',          # 무
    'onion': 'onion',            # 양파
    'garlic': 'garlic',          # 마늘
    'potato': 'potato',          # 감자
    'apple': 'apple',            # 사과
    'cabbage': 'cabbage',        # 양배추 (Cabbage_green, cabbage_red)
    'chinese-cabbage': 'napa_cabbage',   # 배추 (새 클래스)
    'pear': 'pear',              # 배 (새 클래스)
    'mandarine': 'mandarin', 'mandarin': 'mandarin',   # 감귤·한라봉 (새 클래스)
    # 'persimmon': 'persimmon',  # 감 — 재료 기준표에 없어서 제외
}
ANGLES = {'1TOP', '2FR45', '4DI45'}   # 물건 하나당 쓸 각도 (5개 중 3개)
MAX_PER_CLASS = 2500                  # 클래스당 상한
CUT_SIZE = 360                        # 오려 낸 PNG 긴 변(px) — 합성 때는 70~330px로 줄여 쓴다
SOLIDITY = 0.93                       # 마스크가 움푹 파이면 버리는 기준


def qc_mask(img, S=500):
    """연회색 스튜디오 배경에서 재료만 오려 낸 마스크(0/1)"""
    h, w = img.shape[:2]; s = cv2.resize(img, (S, S))
    lab = cv2.cvtColor(s, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv = cv2.cvtColor(s, cv2.COLOR_BGR2HSV)
    edge = np.concatenate([lab[:6].reshape(-1, 3), lab[:, :6].reshape(-1, 3), lab[:, -6:].reshape(-1, 3)])
    d = np.linalg.norm(lab - np.median(edge, 0), axis=2)
    rowbg = np.median(np.concatenate([lab[:, :12], lab[:, -12:]], 1), axis=1)   # 배경 위아래 밝기 차이 보정
    d = np.minimum(d, np.linalg.norm(lab - rowbg[:, None, :], axis=2))
    gc = np.full((S, S), cv2.GC_PR_BGD, np.uint8)
    gc[d > 9] = cv2.GC_PR_FGD; gc[d > 22] = cv2.GC_FGD
    gc[((hsv[..., 1] < 25) & (d < 14)) & (gc != cv2.GC_FGD)] = cv2.GC_PR_BGD
    b = 6; gc[:b, :] = cv2.GC_BGD; gc[:, :b] = cv2.GC_BGD; gc[:, -b:] = cv2.GC_BGD
    try: cv2.grabCut(s, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
    except cv2.error: pass
    m = ((gc == 1) | (gc == 3)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    if m.any() and np.median(hsv[..., 1][m > 0]) > 70:          # 색이 진한 재료는 흰 받침대를 뺀다
        m[(hsv[..., 1] < 45) & (hsv[..., 2] > 140)] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, l, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1: m = (l == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    m = np.zeros_like(m); cv2.drawContours(m, cnts, -1, 1, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)


def cutout(img):
    """재료만 남긴 RGBA. 마스크가 이상하면 None"""
    m = qc_mask(img); area = m.mean()
    if not (0.08 < area < 0.93): return None
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.contourArea(cv2.convexHull(max(cnts, key=cv2.contourArea)))
    if hull and m.sum() / hull < SOLIDITY: return None
    ys, xs = np.where(m); x1, y1, x2, y2 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    alpha = cv2.GaussianBlur((m * 255).astype(np.uint8), (5, 5), 0)
    rgba = np.dstack([img, alpha])[y1:y2, x1:x2]
    k = CUT_SIZE / max(rgba.shape[:2])
    if k < 1: rgba = cv2.resize(rgba, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    return rgba


def main():
    zips = sorted(ZIP_DIR.glob('*.zip'))
    if not zips:
        print(f'zip 파일이 없습니다: {ZIP_DIR}'); return
    CUT.mkdir(parents=True, exist_ok=True)
    count = lambda c: len(list((CUT / c).glob('*.png'))) if (CUT / c).exists() else 0
    for i, z in enumerate(zips, 1):
        item = z.name.split('_')[0].lower(); cls = ITEM_MAP.get(item)
        if not cls:
            print(f'[{i}/{len(zips)}] {z.name}: 쓰지 않는 품목 → 건너뜀'); continue
        (CUT / cls).mkdir(exist_ok=True)
        t0 = time.time(); ok = bad = skip = 0
        try:
            zf = zipfile.ZipFile(z)
        except zipfile.BadZipFile:
            print(f'[{i}/{len(zips)}] {z.name}: zip이 깨졌습니다 (다시 받기)'); continue
        names = [n for n in zf.namelist() if n.lower().endswith('.png') and Path(n).stem.split('_')[-1] in ANGLES]
        if not names:
            print(f'[{i}/{len(zips)}] {z.name}: 사진이 없습니다 (라벨링 zip인지 확인)'); continue
        for n in names:
            if count(cls) >= MAX_PER_CLASS: break
            dst = CUT / cls / (Path(n).stem + '.png')
            if dst.exists(): skip += 1; continue
            img = cv2.imdecode(np.frombuffer(zf.read(n), np.uint8), cv2.IMREAD_COLOR)
            rgba = None if img is None else cutout(img)
            if rgba is None: bad += 1; continue
            cv2.imencode('.png', rgba)[1].tofile(str(dst)); ok += 1   # 한글 경로에서도 저장되게
        print(f'[{i}/{len(zips)}] {z.name} → {cls}: 오려냄 {ok}, 버림 {bad}, 이미 있음 {skip}, 누적 {count(cls)} · {time.time()-t0:.0f}초')

    print('\n클래스별:', {c.name: count(c.name) for c in CUT.iterdir() if c.is_dir()})
    out_zip = OUT / 'qc_cutouts.zip'
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_STORED) as zf:      # PNG는 이미 압축돼 있어 그대로 묶는다
        for p in CUT.rglob('*.png'): zf.write(p, p.relative_to(OUT))
    print(f'\n완료 → {out_zip}  ({out_zip.stat().st_size/1e6:.0f} MB)')
    print('이 파일을 구글 드라이브 MyDrive/yorijori/qc/ 에 올린 뒤 Colab 셀 ③-B를 실행한다')


if __name__ == '__main__':
    main()
