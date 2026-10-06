# ===== ③+④ 데이터 받기 + 자동 매칭 + 합치기 (v2) =====
from roboflow import Roboflow
from google.colab import userdata
import json, random, re, shutil, glob, yaml
from pathlib import Path
from collections import Counter

ROBOFLOW_SOURCES = [
    # 1차에 쓴 데이터
    ('vegetables-19jw7', 'vegetables-2a164', 1),
    ('quiz2pcvk', 'vegetables-8jovr', 1),
    ('robouserflow', 'vegetables-cg8tb', 6),
    # 이번에 추가
    ('vegetables-gdugj', 'vegetables-y393s', 1),
    ('vegetables', 'vegetables-el4g6', 1),
    ('09yolosophie', 'vegetables-zvz0j', 3),
    ('dijital-gen', 'vegetables-345nt', 1),
    ('jasur-vkjtq', 'vegetables-tzoje', 1),
    ('leal-jun-fzre6', 'vegetables-9mixn', 1),
    ('jesus-sduc5', 'vegetables-gywcv', 1),
    ('news', 'vegetables-mr0jj', 4),
    ('gian-mwaaw', 'vegetables-fekan', 1),
    ('marvin-sumper', 'vegetables-spshw', 2),
    ('power-k17io', 'vegetables-xrtxa', 1),
    ('myworkspace-tfvkf', 'vegetables-zynnx', 2),
    ('test-lgzia', 'vegetables-7kfdk', 2),
    ('test-on9hk', 'vegetables-kacga', 5),
    ('robosidekick', 'vegetables-2xirf', 3),
    ('shakhob', 'vegetables-e2juh', 1),
    ('monash-university-dkmtq', 'vegetables-guwbg', 3),
    ('workspace-a52as', 'vegetables-zzsys', 1),
    ('2024718', 'vegetables-fkkxs', 6),
    ('raw-food', 'vegetables-mmdn7', 3),
    ('tushar-panwar-xvpdx', 'vegetables-mdufw', 1),
]

# 데이터셋마다 다른 이름(영어 복수형, 스페인어, 터키어, 인도네시아어 등)을 우리 클래스로 자동 연결한다
SYNONYMS = {
    'cabbage': ['cabbage', 'cabbages', 'white_cabbage', 'green_cabbage', 'repollo', 'lahana', 'kubis', 'kol'],
    'green_onion': ['green_onion', 'green_onions', 'spring_onion', 'spring_onions', 'scallion', 'scallions', 'welsh_onion', 'daun_bawang'],
    'onion': ['onion', 'onions', 'red_onion', 'white_onion', 'yellow_onion', 'cebolla', 'sogan', 'bawang_bombay', 'bawang_merah'],
    'potato': ['potato', 'potatoes', 'patata', 'papa', 'patates', 'kentang'],
    'carrot': ['carrot', 'carrots', 'zanahoria', 'havuc', 'wortel'],
    'zucchini': ['zucchini', 'zucchinis', 'courgette', 'calabacin', 'kabak'],
    'cucumber': ['cucumber', 'cucumbers', 'pepino', 'salatalik', 'timun', 'mentimun'],
    'radish': ['daikon', 'white_radish', 'korean_radish'],  # 'radish'(빨간 래디시)는 일부러 뺌
    'spinach': ['spinach', 'espinaca', 'ispanak', 'bayam'],
    'mushroom': ['mushroom', 'mushrooms', 'champignon', 'hongo', 'mantar', 'jamur'],
    'tomato': ['tomato', 'tomatoes', 'tomate', 'domates', 'tomat', 'cherry_tomato'],
    'chili_pepper': ['chili', 'chilli', 'chili_pepper', 'chilli_pepper', 'green_chili', 'green_chilli', 'red_chili',
                     'red_chilli', 'hot_pepper', 'jalapeno', 'cabai', 'cili', 'cabe', 'aji'],
    'garlic': ['garlic', 'ajo', 'sarimsak', 'bawang_putih'],
    'egg': ['egg', 'eggs', 'huevo'],
    'tofu': ['tofu'],
    'milk': ['milk', 'milk_carton'],
    'apple': ['apple', 'apples', 'manzana', 'elma', 'apel'],
    'banana': ['banana', 'bananas', 'platano', 'muz', 'pisang'],
    'lemon': ['lemon', 'lemons', 'limon', 'lemon_fruit'],
    'bell_pepper': ['bell_pepper', 'bell_peppers', 'capsicum', 'paprika', 'sweet_pepper', 'red_bell_pepper',
                    'green_bell_pepper', 'yellow_bell_pepper', 'orange_bell_pepper'],
}
# 자동 매칭이 안 된 이름을 직접 연결하고 싶으면 여기에 추가한다. 예: {'Brokoli': None, 'pepper': 'bell_pepper'}
EXTRA_MAP = {}

def norm(s):
    return re.sub(r'[\s\-]+', '_', str(s).strip().lower())

classes = json.load(open('classes.json', encoding='utf-8'))
EN2ID = {c['en']: c['id'] for c in classes}
SYN = {norm(s): en for en, ss in SYNONYMS.items() for s in ss}
SYN.update({norm(k): v for k, v in EXTRA_MAP.items()})

# ---------- 1) 받기 ----------
rf = Roboflow(api_key=userdata.get('ROBOFLOW_API_KEY'))
ok, failed = [], []
for ws, proj, ver in ROBOFLOW_SOURCES:
    loc = f'/content/datasets/{proj}'
    if glob.glob(f'{loc}/**/data.yaml', recursive=True):
        ok.append(loc); continue                      # 이미 받은 건 건너뜀
    try:
        rf.workspace(ws).project(proj).version(ver).download('yolov8', location=loc)
        ok.append(loc)
    except Exception as e:
        failed.append((proj, str(e)[:120]))

# ---------- 2) 합치기 ----------
IMG_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
OUT = Path('/content/merged')
if OUT.exists(): shutil.rmtree(OUT)
for s in ('train', 'val', 'test'):
    (OUT / s / 'images').mkdir(parents=True); (OUT / s / 'labels').mkdir(parents=True)

def to_box(parts):
    """'c x y w h' 는 그대로, 폴리곤 'c x1 y1 x2 y2 ...' 는 감싸는 박스로 바꾼다"""
    v = list(map(float, parts[1:]))
    if len(v) == 4: return v
    if len(v) >= 6 and len(v) % 2 == 0:
        xs, ys = v[0::2], v[1::2]
        x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
        return [(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1]
    return None

rnd = random.Random(42)
items, seen = [], set()
box_count, unmapped, per_source, dup = Counter(), Counter(), [], 0
for loc in ok:
    y = glob.glob(f'{loc}/**/data.yaml', recursive=True)[0]
    names = yaml.safe_load(open(y))['names']
    names = [names[k] for k in sorted(names)] if isinstance(names, dict) else list(names)
    cmap = {i: EN2ID[SYN[norm(n)]] for i, n in enumerate(names) if SYN.get(norm(n)) in EN2ID}
    for i, n in enumerate(names):
        if i not in cmap: unmapped[n] += 0
    used = 0
    for img_dir in Path(loc).rglob('images'):
        lbl_dir = img_dir.parent / 'labels'
        if not lbl_dir.is_dir(): continue
        for img in img_dir.iterdir():
            if img.suffix.lower() not in IMG_EXT: continue
            lines = []
            lbl = lbl_dir / (img.stem + '.txt')
            boxes = []
            if lbl.exists():
                for line in lbl.read_text().split('\n'):
                    p = line.split()
                    if len(p) < 5: continue
                    b = to_box(p)
                    if b is not None: boxes.append((int(float(p[0])), b))
            # 같은 원본 파일명 + 같은 박스 위치 = 포크로 복사된 중복 사진 → 제거
            key = (img.name.split('.rf.')[0].lower(), tuple(sorted(tuple(round(x, 2) for x in b) for _, b in boxes)))
            if key in seen: dup += 1; continue
            for c, b in boxes:
                if c in cmap:
                    lines.append(f'{cmap[c]} ' + ' '.join(f'{x:.6f}' for x in b)); box_count[cmap[c]] += 1
                elif c < len(names):
                    unmapped[names[c]] += 1
            if not lines and rnd.random() > 0.05: continue  # 우리 재료가 없는 사진은 5%만 남김
            seen.add(key); used += 1
            items.append((img, lines, f'{Path(loc).name}_{len(items)}'))
    per_source.append((Path(loc).name, used, [n for i, n in enumerate(names) if i in cmap]))

rnd.shuffle(items)
n = len(items); n_tr, n_va = int(n * 0.8), int(n * 0.15)
for split, rows in (('train', items[:n_tr]), ('val', items[n_tr:n_tr + n_va]), ('test', items[n_tr + n_va:])):
    for img, lines, stem in rows:
        shutil.copy(img, OUT / split / 'images' / (stem + img.suffix.lower()))
        (OUT / split / 'labels' / (stem + '.txt')).write_text('\n'.join(lines))
yaml.safe_dump({'path': str(OUT), 'train': 'train/images', 'val': 'val/images', 'test': 'test/images',
                'names': {c['id']: c['en'] for c in classes}}, open(OUT / 'data.yaml', 'w'), sort_keys=False)
DATA_YAML = OUT / 'data.yaml'

# ---------- 3) 결과 ----------
print('\n===== 아래 내용을 복사해서 보내주세요 =====')
print(f'받은 데이터셋 {len(ok)}개, 실패 {len(failed)}개')
for p, e in failed: print('  실패:', p, '-', e)
print(f'사용한 이미지 {n}장 (중복 제거 {dup}장) → train {n_tr} / val {n_va} / test {n - n_tr - n_va}')
print('\n재료별 박스 수:')
for c in classes:
    k = box_count[c['id']]
    print(f"  {c['ko']}({c['en']}): {k}" + ('  ← 없음' if k == 0 else '  ← 부족' if k < 150 else ''))
print('\n매칭 안 된 원본 이름(박스 수):')
print('  ' + ', '.join(f'{k}({v})' for k, v in unmapped.most_common()) if unmapped else '  없음')
