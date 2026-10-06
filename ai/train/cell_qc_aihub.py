# =====================================================================
# 요리조리 · AI Hub 「농산물 품질(QC) 이미지」 → YOLO 학습 데이터
#   Colab에서 셀 단위로 실행한다 (# %% 가 셀 구분)
#   ① 준비  ② 파일 목록  ③ 받기+오려내기(파일 하나씩, 원본은 바로 삭제)  ④ 확인
#   ⑤ 배경에 합성 → YOLO 라벨  ⑥ data.yaml (기존 v3 데이터와 함께 학습)
#
#   결과는 구글 드라이브 MyDrive/yorijori/qc/ 에 저장된다 (수백 MB~1GB)
#   원본 29GB는 Colab 디스크에서만 잠깐 풀었다가 지운다
# =====================================================================

# %% ① 준비 ------------------------------------------------------------
from google.colab import drive, userdata
drive.mount('/content/drive')
import os, re, glob, json, random, shutil, subprocess, zipfile, time
import numpy as np, cv2
from pathlib import Path

ROOT = Path('/content/drive/MyDrive/yorijori/qc')       # 결과 저장 위치
WORK = Path('/content/qc_tmp')                           # 원본을 잠깐 푸는 곳(Colab 디스크)
CUT  = ROOT / 'cutouts'                                  # 오려 낸 재료 PNG(투명 배경)
ROOT.mkdir(parents=True, exist_ok=True); WORK.mkdir(exist_ok=True); CUT.mkdir(exist_ok=True)
DONE_LOG = ROOT / 'done_filekeys.txt'                    # 끝난 파일 기록 → 세션이 끊겨도 이어서 한다

AIHUB_KEY = userdata.get('AIHUB_API_KEY')                # Colab 왼쪽 열쇠 아이콘(Secrets)에 등록
DATASET_KEY = 149                                        # 농산물 품질(QC) 이미지

if not Path('/content/aihubshell').exists():
    subprocess.run('curl -s -o /content/aihubshell https://api.aihub.or.kr/api/aihubshell.do && chmod +x /content/aihubshell',
                   shell=True, check=True)
print('준비 완료')

# %% ② 파일 목록 --------------------------------------------------------
# AI Hub 목록을 받아 Validation(또는 전체)의 '원천데이터' zip과 filekey만 골라낸다 (라벨링 zip은 제외)
out = subprocess.run(f'/content/aihubshell -mode l -datasetkey {DATASET_KEY}', shell=True,
                     capture_output=True, text=True).stdout

FILES = []            # [(이름, 용량, filekey, 'train'|'val')]
split, kind = '', ''
for line in out.splitlines():
    if 'Training' in line: split = 'train'
    elif 'Validation' in line: split = 'val'
    if '원천데이터' in line: kind = 'src'
    elif '라벨링데이터' in line: kind = 'label'
    m = re.search(r'([\w\-\.]+\.zip)\s*\|\s*([\d\.]+\s*[KMGT]?B)\s*\|\s*(\d+)', line)
    if m and kind == 'src': FILES.append((m.group(1), m.group(2), m.group(3), split))

USE_SPLIT = 'val'      # 'val' = Validation 원천데이터만, 'all' = Training까지 (Training은 파일당 3~8GB라 오래 걸린다)
cands = [f for f in FILES if USE_SPLIT == 'all' or f[3] == USE_SPLIT]
print(f'원천데이터 zip {len(cands)}개')
for n, sz, k, sp in cands: print(f'{k:>8}  {sz:>6}  {sp:5}  {n}')
# ⚠ 아무것도 안 잡히면 위 aihubshell 출력에서 filekey를 아래에 직접 적는다
MANUAL_FILEKEYS = []   # 예: ['123456', '123457']

# %% ③ 받기 + 오려내기 ---------------------------------------------------
# 파일 이름 앞부분(품목) → 우리 클래스. 처음 보는 품목은 건너뛰고 이름을 출력한다 → 여기에 추가하면 된다
ITEM_MAP = {                     # AI Hub 파일 이름 앞부분(소문자) → 우리 클래스
    'radish': 'radish',          # 무 (기존 클래스, 한국 무로 보강)
    'onion': 'onion',            # 양파 (흰·적양파)
    'garlic': 'garlic',          # 마늘
    'potato': 'potato',          # 감자
    'apple': 'apple',            # 사과
    'cabbage': 'cabbage',        # 양배추 (Cabbage_green, cabbage_red)
    'chinese-cabbage': 'napa_cabbage',   # 배추 (새 클래스)
    'pear': 'pear',              # 배 (새 클래스)
    'mandarine': 'mandarin', 'mandarin': 'mandarin',   # 감귤·한라봉 (새 클래스)
    # 'persimmon': 'persimmon',  # 감 — 재료 기준표에 없어서 제외
}
ANGLES = {'1TOP', '2FR45', '4DI45'}   # 물건 하나당 쓸 각도 (5개 중 3개). 줄이면 빨라지고 비슷한 사진이 준다
MAX_PER_CLASS = 2500                  # 클래스당 오려 낸 사진 상한
CUT_SIZE = 480                        # 오려 낸 PNG 긴 변(px) — 합성 때 더 작게 줄여 쓴다
SOLIDITY = 0.93                       # 마스크가 볼록한 정도(1에 가까울수록 엄격). 무·감·배·귤은 대부분 0.95 이상

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

def cutout(path):
    """재료만 남긴 RGBA (테두리 살짝 부드럽게). 마스크가 이상하면 None"""
    img = cv2.imread(str(path))
    if img is None: return None
    m = qc_mask(img); area = m.mean()
    if not (0.08 < area < 0.93): return None                     # 거의 비었거나 배경까지 잡힌 경우 버림
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.contourArea(cv2.convexHull(max(cnts, key=cv2.contourArea)))
    if hull and m.sum() / hull < SOLIDITY: return None             # 흰 부분이 배경으로 먹혀 움푹 파인 마스크는 버림
    ys, xs = np.where(m); x1, y1, x2, y2 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    alpha = cv2.GaussianBlur((m * 255).astype(np.uint8), (5, 5), 0)
    rgba = np.dstack([img, alpha])[y1:y2, x1:x2]
    k = CUT_SIZE / max(rgba.shape[:2])
    if k < 1: rgba = cv2.resize(rgba, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    return rgba

def count_cut(cls): return len(list((CUT / cls).glob('*.png'))) if (CUT / cls).exists() else 0
done = set(DONE_LOG.read_text().split()) if DONE_LOG.exists() else set()
todo = MANUAL_FILEKEYS or [k for n, sz, k, sp in cands if n.split('_')[0].lower() in ITEM_MAP]   # 감 등 안 쓰는 품목은 아예 받지 않는다
unknown = set()
for i, key in enumerate(todo, 1):
    if key in done: continue
    t0 = time.time()
    shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
    r = subprocess.run(f'cd {WORK} && /content/aihubshell -mode d -datasetkey {DATASET_KEY} -filekey {key} -aihubapikey "{AIHUB_KEY}"',
                       shell=True, capture_output=True, text=True)
    for z in WORK.rglob('*.zip'):                                 # 남은 zip이 있으면 직접 푼다
        try: zipfile.ZipFile(z).extractall(z.parent); z.unlink()
        except zipfile.BadZipFile: pass
    pngs = sorted(WORK.rglob('*.png'))
    if not pngs:
        print(f'[{i}/{len(todo)}] {key}: 사진 없음 → 건너뜀\n', r.stdout[-300:], r.stderr[-300:])
        if '해외' in r.stdout + r.stderr:
            print('⛔ AI Hub가 해외(Colab) 다운로드를 막고 있다 → 내 PC에서 qc_local.py로 처리하고 셀 ③-B를 쓴다'); break
        continue                                                   # 실패한 건 기록하지 않는다 → 다음에 다시 시도
    item = pngs[0].name.split('_')[0].lower()
    cls = ITEM_MAP.get(item)
    if not cls:
        unknown.add(item); print(f'[{i}/{len(todo)}] {key}: 품목 "{item}" 은 ITEM_MAP에 없음 → 건너뜀')
    else:
        (CUT / cls).mkdir(exist_ok=True)
        n_ok = n_bad = 0
        for p in pngs:
            if count_cut(cls) >= MAX_PER_CLASS: break
            ang = p.stem.split('_')[-1]
            if ang not in ANGLES: continue
            rgba = cutout(p)
            if rgba is None: n_bad += 1; continue
            cv2.imwrite(str(CUT / cls / (p.stem + '.png')), rgba); n_ok += 1
        print(f'[{i}/{len(todo)}] {key} {item}→{cls}: 오려냄 {n_ok}, 버림 {n_bad}, 누적 {count_cut(cls)} · {time.time()-t0:.0f}초')
    shutil.rmtree(WORK, ignore_errors=True)                       # 원본 삭제
    with open(DONE_LOG, 'a') as f: f.write(key + '\n')
if unknown: print('\nITEM_MAP에 없는 품목:', sorted(unknown))
print({c.name: count_cut(c.name) for c in CUT.iterdir() if c.is_dir()})

# %% ③-B (AI Hub가 해외 다운로드를 막을 때) 내 PC에서 만든 qc_cutouts.zip 풀기 ----
# 내 PC: AI Hub 웹에서 Validation/원천데이터 zip을 받고 → python qc_local.py "zip폴더"
#        → 만들어진 qc_out/qc_cutouts.zip 을 구글 드라이브 MyDrive/yorijori/qc/ 에 올린다
# 그다음 이 셀 → ④ → ⑤ → ⑥ 순서로 실행한다 (①은 먼저 실행, ②·③은 건너뛴다)
zp = ROOT / 'qc_cutouts.zip'
assert zp.exists(), f'{zp} 가 없다 — 드라이브에 올렸는지 확인'
zipfile.ZipFile(zp).extractall(ROOT)        # → ROOT/cutouts/<클래스>/*.png
print({c.name: len(list(c.glob('*.png'))) for c in CUT.iterdir() if c.is_dir()})

# %% ④ 확인: 오려 낸 결과 훑어보기 --------------------------------------
import matplotlib.pyplot as plt
for c in sorted(p for p in CUT.iterdir() if p.is_dir()):
    fs = random.sample(sorted(c.glob('*.png')), min(12, count_cut(c.name)))
    fig, ax = plt.subplots(1, len(fs), figsize=(len(fs) * 1.6, 1.9))
    fig.suptitle(c.name)
    for a, f in zip(np.atleast_1d(ax), fs):
        im = cv2.imread(str(f), cv2.IMREAD_UNCHANGED); bg = np.full(im.shape[:2] + (3,), 40, np.uint8)
        al = im[..., 3:] / 255; a.imshow(cv2.cvtColor((im[..., :3] * al + bg * (1 - al)).astype(np.uint8), cv2.COLOR_BGR2RGB)); a.axis('off')
    plt.show()
# 이상한 사진은 드라이브 cutouts 폴더에서 지우면 된다

# %% ⑤ 배경에 합성 → YOLO 라벨 -------------------------------------------
# 클래스 33개 — cell_v4_data.py 와 같은 순서 (0~24 = v3, 25~ = 새 클래스). 순서를 바꾸면 안 된다
CLASSES_V4 = [
    ('cabbage', '양배추'), ('green_onion', '대파'), ('onion', '양파'), ('potato', '감자'), ('carrot', '당근'),
    ('zucchini', '애호박'), ('cucumber', '오이'), ('radish', '무'), ('spinach', '시금치'), ('mushroom', '버섯'),
    ('tomato', '토마토'), ('chili_pepper', '고추'), ('garlic', '마늘'), ('egg', '계란'), ('tofu', '두부'),
    ('milk', '우유'), ('apple', '사과'), ('banana', '바나나'), ('lemon', '레몬'), ('bell_pepper', '파프리카'),
    ('eggplant', '가지'), ('broccoli', '브로콜리'), ('corn', '옥수수'), ('cheese', '치즈'), ('sweet_potato', '고구마'),
    ('napa_cabbage', '배추'), ('pear', '배'), ('mandarin', '귤'), ('orange', '오렌지'),
    ('lime', '라임'), ('strawberry', '딸기'), ('grape', '포도'), ('kiwi', '키위'),
]
NAMES = [en for en, ko in CLASSES_V4]
CID = {n: i for i, n in enumerate(NAMES)}

# 배경: ① 직접 찍은 냉장고·식탁 사진 폴더(있으면) ② 없으면 무늬·색을 만들어 쓴다
BG_DIR = Path('/content/drive/MyDrive/yorijori/backgrounds')   # 여기에 사진을 넣어 두면 우선 사용
N_SYNTH = 6000            # 만들 합성 사진 수
OUT = ROOT / 'synth'
SZ = 640
random.seed(0); np.random.seed(0)
bgs = sorted(BG_DIR.glob('*.jpg')) + sorted(BG_DIR.glob('*.png')) if BG_DIR.exists() else []
cuts = {c.name: sorted(c.glob('*.png')) for c in CUT.iterdir() if c.is_dir() and c.name in CID}
print('배경 사진', len(bgs), '장 · 재료', {k: len(v) for k, v in cuts.items()})

def make_bg():
    if bgs and random.random() < 0.8:
        im = cv2.imread(str(random.choice(bgs)))
        h, w = im.shape[:2]; s = random.uniform(0.5, 1.0) * min(h, w)
        x, y = random.randint(0, int(w - s)), random.randint(0, int(h - s))
        return cv2.resize(im[y:y + int(s), x:x + int(s)], (SZ, SZ))
    # 냉장고 선반(흰·회색), 도마·식탁(나무색), 장바구니(밝은 단색) 위주의 차분한 색
    kind = random.random()
    if kind < .5:   hsv = (random.randint(0, 179), random.randint(0, 25), random.randint(170, 250))   # 흰·회색
    elif kind < .8: hsv = (random.randint(8, 22), random.randint(60, 150), random.randint(110, 220)) # 나무색
    else:           hsv = (random.randint(0, 179), random.randint(20, 90), random.randint(90, 230))  # 기타 단색
    base = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0, 0]
    bg = np.full((SZ, SZ, 3), base, np.uint8).astype(np.int16)
    bg += (np.random.randn(SZ, SZ, 1) * random.uniform(3, 14)).astype(np.int16)
    g = np.linspace(-random.randint(0, 50), random.randint(0, 50), SZ)[:, None, None]
    bg = np.clip(bg + (g if random.random() < .5 else g.transpose(1, 0, 2)), 0, 255).astype(np.uint8)
    if random.random() < .4:                                                      # 선반·도마 느낌의 줄무늬
        for y in range(0, SZ, random.randint(60, 200)):
            cv2.line(bg, (0, y), (SZ, y), tuple(int(v) for v in np.clip(base.astype(int) - 40, 0, 255)), random.randint(2, 8))
    return cv2.GaussianBlur(bg, (0, 0), random.uniform(0.5, 2))

def paste(bg, rgba, cx, cy, long_side):
    h, w = rgba.shape[:2]; k = long_side / max(h, w)
    o = cv2.resize(rgba, (max(4, int(w * k)), max(4, int(h * k))), interpolation=cv2.INTER_AREA)
    if random.random() < .5: o = cv2.flip(o, 1)
    ang = random.uniform(-25, 25); M = cv2.getRotationMatrix2D((o.shape[1] / 2, o.shape[0] / 2), ang, 1)
    cos, sin = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(o.shape[0] * sin + o.shape[1] * cos), int(o.shape[0] * cos + o.shape[1] * sin)
    M[0, 2] += nw / 2 - o.shape[1] / 2; M[1, 2] += nh / 2 - o.shape[0] / 2
    o = cv2.warpAffine(o, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    rgb = o[..., :3].astype(np.float32) * random.uniform(.7, 1.15) + random.uniform(-15, 15)   # 냉장고 조명 차이
    al = o[..., 3:].astype(np.float32) / 255
    x1, y1 = int(cx - nw / 2), int(cy - nh / 2)
    X1, Y1, X2, Y2 = max(0, x1), max(0, y1), min(SZ, x1 + nw), min(SZ, y1 + nh)
    if X2 - X1 < 8 or Y2 - Y1 < 8: return None
    sx, sy = X1 - x1, Y1 - y1
    a = al[sy:sy + Y2 - Y1, sx:sx + X2 - X1]
    if a.mean() < .15: return None
    # 바닥 그림자 (물건 아래로 살짝 어둡게)
    sh = cv2.GaussianBlur(a[..., 0], (0, 0), 6) * .35
    oy = 6; Ys2 = min(SZ, Y2 + oy); hh = Ys2 - (Y1 + oy)
    if hh > 0: bg[Y1 + oy:Ys2, X1:X2] = (bg[Y1 + oy:Ys2, X1:X2] * (1 - sh[:hh, :, None])).astype(np.uint8)
    reg = bg[Y1:Y2, X1:X2].astype(np.float32)
    bg[Y1:Y2, X1:X2] = np.clip(rgb[sy:sy + Y2 - Y1, sx:sx + X2 - X1] * a + reg * (1 - a), 0, 255).astype(np.uint8)
    ys, xs = np.where(a[..., 0] > .5)
    if len(xs) < 20: return None
    return X1 + xs.min(), Y1 + ys.min(), X1 + xs.max(), Y1 + ys.max()

def iou_cover(b, others):  # b가 앞 물건에 얼마나 가려졌는지(뒤에 붙인 게 위에 온다 → 앞 물건 기준으로 검사)
    for o in others:
        ix = max(0, min(b[2], o[2]) - max(b[0], o[0])); iy = max(0, min(b[3], o[3]) - max(b[1], o[1]))
        if ix * iy > 0.45 * (o[2] - o[0]) * (o[3] - o[1]): return True
    return False

for split in ('train', 'val'):
    (OUT / 'images' / split).mkdir(parents=True, exist_ok=True); (OUT / 'labels' / split).mkdir(parents=True, exist_ok=True)
classes = list(cuts)
for n in range(N_SYNTH):
    split = 'val' if n % 10 == 0 else 'train'
    bg = make_bg(); boxes = []
    for _ in range(random.randint(1, 6)):
        c = random.choice(classes); rgba = cv2.imread(str(random.choice(cuts[c])), cv2.IMREAD_UNCHANGED)
        long_side = random.uniform(70, 330)
        tmp = bg.copy()
        b = paste(tmp, rgba, random.uniform(60, SZ - 60), random.uniform(60, SZ - 60), long_side)
        if b is None: continue
        if iou_cover(b, [x[1:] for x in boxes]): continue      # 앞 물건을 절반 가까이 가리면 붙이지 않는다
        bg = tmp
        boxes.append((CID[c], *b))
    if not boxes: continue
    if random.random() < .3: bg = cv2.GaussianBlur(bg, (0, 0), random.uniform(.6, 1.4))       # 흔들림·초점
    if random.random() < .3: bg = cv2.imdecode(cv2.imencode('.jpg', bg, [cv2.IMWRITE_JPEG_QUALITY, random.randint(45, 85)])[1], 1)
    name = f'qc_{n:05d}'
    cv2.imwrite(str(OUT / 'images' / split / f'{name}.jpg'), bg, [cv2.IMWRITE_JPEG_QUALITY, 92])
    with open(OUT / 'labels' / split / f'{name}.txt', 'w') as f:
        for c, x1, y1, x2, y2 in boxes:
            f.write(f'{c} {(x1+x2)/2/SZ:.6f} {(y1+y2)/2/SZ:.6f} {(x2-x1)/SZ:.6f} {(y2-y1)/SZ:.6f}\n')
    if n % 500 == 0: print(n, '장')
print('합성 완료:', len(list((OUT / 'images' / 'train').glob('*.jpg'))), '/', len(list((OUT / 'images' / 'val').glob('*.jpg'))))

# 확인용 몇 장
fig, ax = plt.subplots(2, 4, figsize=(16, 8))
for a, f in zip(ax.flat, random.sample(sorted((OUT / 'images' / 'train').glob('*.jpg')), 8)):
    im = cv2.cvtColor(cv2.imread(str(f)), cv2.COLOR_BGR2RGB)
    for line in open(OUT / 'labels' / 'train' / (f.stem + '.txt')):
        c, x, y, w, h = map(float, line.split()); x1, y1 = int((x - w/2) * SZ), int((y - h/2) * SZ)
        cv2.rectangle(im, (x1, y1), (int((x + w/2) * SZ), int((y + h/2) * SZ)), (0, 255, 0), 2)
        cv2.putText(im, NAMES[int(c)], (x1, max(12, y1 - 3)), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1)
    a.imshow(im); a.axis('off')
plt.show()

# %% ⑥ data_v4.yaml + classes_v4.json ------------------------------------
# 먼저 같은 세션에서 cell_v4_data.py(③+④ v4)를 실행해 /content/merged 를 만든다 (33종 기준 Roboflow 데이터)
import yaml
V4_DIR = Path('/content/merged')
assert (V4_DIR / 'data.yaml').exists(), '/content/merged 가 없다 — cell_v4_data.py 를 먼저 실행'
assert yaml.safe_load(open(V4_DIR / 'data.yaml'))['names'][32] == 'kiwi', 'merged 가 v3(25종) 기준이다 — cell_v4_data.py 로 다시 만든다'
data = {
    'path': '/',
    'train': [str(V4_DIR / 'train' / 'images'), str(OUT / 'images' / 'train')],
    'val':   [str(V4_DIR / 'val' / 'images'), str(OUT / 'images' / 'val')],
    'names': {i: n for i, n in enumerate(NAMES)},
}
yaml.safe_dump(data, open(ROOT / 'data_v4.yaml', 'w'), allow_unicode=True, sort_keys=False)
json.dump([{'id': i, 'en': en, 'ko': ko} for i, (en, ko) in enumerate(CLASSES_V4)],
          open(ROOT / 'classes_v4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
n_tr = len(list((V4_DIR / 'train' / 'images').iterdir())) + len(list((OUT / 'images' / 'train').glob('*.jpg')))
print(open(ROOT / 'data_v4.yaml').read())
print(f'학습 사진 합계 {n_tr}장 (Roboflow + AI Hub 합성)')
DATA_YAML = ROOT / 'data_v4.yaml'
print('→ 학습 셀에서 DATA_YAML =', DATA_YAML, ' · v3 가중치(fridge_v3.pt)에서 이어 학습한다')
