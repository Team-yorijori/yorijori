# ===== ③+④ 데이터 받기 + 자동 매칭 + 합치기 (v4 · 33종) =====
# v3와 같은 Roboflow 데이터를 쓰되, 그때 버려졌던 과일(오렌지·라임·딸기·포도·키위·배)을 새 클래스로 살린다.
# 배추·배·귤의 한국 사진은 AI Hub QC 합성 데이터(cell_qc_aihub.py ⑤)로 따로 들어간다.
# classes.json은 이 셀이 직접 만든다 (손으로 만들 필요 없음).
from roboflow import Roboflow
from google.colab import userdata
import json, random, re, shutil, glob, yaml
from pathlib import Path
from collections import Counter

ROBOFLOW_SOURCES = [
    # --- 냉장고 혼합 사진 (가장 중요) ---
    ('smart-fridge-mvi88', 'smart-fridge-co7ul', 6),
    ('recipe-recomendation-app', 'fridge-detection-merged', 4),
    ('bottles-0ds2b', 'fridge-qjtyj', 1),
    ('fridge-0keux', 'fridge-0fckr', 1),
    ('adam-barnett', 'fridge-jlbwq', 1),
    ('cs131', 'fridge-5ep2w', 4),
    ('fridge-fesjh', 'fridge-eamqk', 3),
    # --- 대파 ---
    ('curry', 'green-zecem', 1),
    ('shabishko', 'onion-leaves-99kwc', 1),
    ('foodanno', 'leek', 1),
    # --- 무 ---
    ('olrnd', 'radish-d1ugk', 1),
    ('dolazy7-gmail-com-3vj05', 'radish', 2),
    ('yeoworm', 'radish-akkqa', 3),
    ('stones-workspace', 'radish-y3ll3', 1),
    ('curry', 'radish-2lmfh', 1),
    # --- 두부 ---
    ('stones-workspace', 'tofu-tdnu5', 1),
    ('graduation-project-3v6ak', 'tofu-nmvji', 1),
    ('chen-xieyu', 'tofu-8punk', 1),
    # --- 우유 ---
    ('mateo-ojeda', 'milk-zum2p', 1),
    ('robocup2022-kogzd', 'milk-i3u51', 2),
    ('bosslnwza', 'milk-fzwnn', 1),
    ('dheebanmilk', 'milk-yxalp', 15),
    ('dolazy7-gmail-com-3vj05', 'milk-acvg1', 2),
    # --- 버섯 ---
    ('test-zq0fq', 'mushroom-3zqg7', 2),
    ('mushroom28', 'mushroom-nksu4', 6),
    ('huurhuntergel', 'mushroom-e8f6k', 3),
    ('yueyue-fob5l', 'mushroom-xtwbh', 1),
    ('mushroom-9xzfs', 'mushroom-jlp5g', 3),
    ('mushroom-r8avj', 'mushroom-syqui', 1),
    ('davifina', 'mushroom-eob88', 2),
    ('genet-xx587', 'mushroom-7whbq', 2),
    # --- 바나나 ---
    ('kipleytaylor', 'banana-rzonz', 1),
    ('jim-pepvn', 'banana-9nmv2', 2),
    ('object-detection-djcen', 'banana-nlcck', 1),
    ('mtfs-workspace-ktra5', 'banana-p8z1q', 5),
    ('train-0beej', 'banana-qlroc', 1),
    # --- 레몬 ---
    ('ai-wfddm', 'lemon-ezutg', 1),
    ('ece4078-mpxui', 'lemon-jlkzg', 2),
    ('mueanfan', 'lemon-orwgb', 2),
    ('riyadh-lakadimu-uhlb5', 'lemon-pknhy', 12),
    ('haniftesting', 'lemon-aer5f', 2),
    ('dcu-oiu8y', 'lemon-gzrja', 2),
    # --- 고추 ---
    ('olrnd', 'green-chili', 1),
    ('abhichal-rajput', 'chili-2jwcr', 1),
    ('gun-yfmsv', 'chili-3apfs', 3),
    ('abhichal-rajput', 'green-chilli', 1),
    # --- 파프리카 (토마토와 구분용) ---
    ('mvi-n1mve', 'bell-pepper-ydvso', 5),
    ('bell-pepper-vpkx5', 'bell-pepper-rld1g', 1),
    ('khuyennguyen', 'bell-pepper-wu9ic', 1),
    ('bellpepper', 'bell-pepper-wxxwg', 4),
    ('thanakrit23', 'bell-pepper-rtzwb', 1),
    # --- 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) ---
    ('cv-jaka4', 'tomato-detection-ku6fz', 2),
    ('olrnd', 'onion-yhzc7', 1),
    ('fruits-hfscm', 'onion-n278m', 1),
    ('robocup2022-kogzd', 'onion-9renr', 2),
    ('vision-6bf8h', 'onion-yol1h', 1),
    # --- 1·2차에 쓴 데이터 ---
    ('vegetables-19jw7', 'vegetables-2a164', 1),
    ('quiz2pcvk', 'vegetables-8jovr', 1),
    ('robouserflow', 'vegetables-cg8tb', 6),
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
    'green_onion': ['green_onion', 'green_onions', 'spring_onion', 'spring_onions', 'scallion', 'scallions', 'welsh_onion',
                    'daun_bawang', 'leek', 'leeks', 'onion_leaves', 'onion_leaf', 'green_onion_leaves'],
    'onion': ['onion', 'onions', 'red_onion', 'white_onion', 'yellow_onion', 'cebolla', 'sogan', 'bawang_bombay', 'bawang_merah'],
    'potato': ['potato', 'potatoes', 'patata', 'papa', 'patates', 'kentang'],
    'carrot': ['carrot', 'carrots', 'zanahoria', 'havuc', 'wortel'],
    'zucchini': ['zucchini', 'zucchinis', 'courgette', 'calabacin', 'kabak'],
    'cucumber': ['cucumber', 'cucumbers', 'pepino', 'salatalik', 'timun', 'mentimun'],
    'radish': ['daikon', 'white_radish', 'korean_radish'],  # 'radish'(빨간 래디시)는 일부러 뺌
    'spinach': ['spinach', 'espinaca', 'ispanak', 'bayam'],
    'mushroom': ['mushroom', 'mushrooms', 'champignon', 'hongo', 'mantar', 'jamur', 'enoki', 'enoki_mushroom',
                 'shiitake', 'shiitake_mushroom', 'oyster_mushroom', 'button_mushroom', 'king_oyster_mushroom'],
    'tomato': ['tomato', 'tomatoes', 'tomate', 'domates', 'tomat', 'cherry_tomato', 'ripe_tomato', 'red_tomato', 'fresh_tomato'],
    'chili_pepper': ['chili', 'chilli', 'chili_pepper', 'chilli_pepper', 'green_chili', 'green_chilli', 'red_chili',
                     'red_chilli', 'hot_pepper', 'jalapeno', 'cabai', 'cili', 'cabe', 'aji', 'chilies', 'chillies',
                     'green_chilies', 'green_chillies', 'hot_peppers'],
    'garlic': ['garlic', 'ajo', 'sarimsak', 'bawang_putih'],
    'egg': ['egg', 'eggs', 'huevo'],
    'tofu': ['tofu', 'bean_curd', 'tofu_package', 'dubu'],
    'milk': ['milk', 'milk_carton', 'milk_bottle', 'milk_box', 'milk_pack', 'dairy_milk'],
    'apple': ['apple', 'apples', 'manzana', 'elma', 'apel'],
    'banana': ['banana', 'bananas', 'banana_bunch', 'platano', 'muz', 'pisang'],
    'lemon': ['lemon', 'lemons', 'limon', 'lemon_fruit'],
    'bell_pepper': ['bell_pepper', 'bell_peppers', 'capsicum', 'paprika', 'sweet_pepper', 'red_bell_pepper',
                    'green_bell_pepper', 'yellow_bell_pepper', 'orange_bell_pepper'],
    # ---- v4 추가 ----
    'napa_cabbage': ['napa_cabbage', 'chinese_cabbage', 'kimchi_cabbage', 'baechu', 'napa'],
    'pear': ['pear', 'pears', 'asian_pear', 'korean_pear', 'nashi', 'pera', 'armut', 'pir'],
    'mandarin': ['mandarin', 'mandarins', 'mandarin_orange', 'tangerine', 'tangerines', 'clementine', 'clementines',
                 'satsuma', 'mikan', 'jeruk_mandarin'],
    'orange': ['orange', 'oranges', 'naranja', 'portakal', 'jeruk', 'orange_fruit', 'navel_orange'],
    'lime': ['lime', 'limes', 'green_lemon', 'lima', 'jeruk_nipis'],
    'strawberry': ['strawberry', 'strawberries', 'fresa', 'frutilla', 'cilek', 'stroberi'],
    'grape': ['grape', 'grapes', 'green_grape', 'green_grapes', 'red_grape', 'red_grapes', 'grape_bunch', 'uva', 'uvas',
              'uzum', 'anggur'],
    'kiwi': ['kiwi', 'kiwis', 'kiwifruit', 'kiwi_fruit', 'kivi'],
}
# ---- v4 보강: 지난 실행에서 매칭 안 된 이름 중 쓸 수 있는 것 ----
SYNONYMS['cheese'] = ['cheese', 'cheeses', 'cheddar', 'mozzarella', 'sliced_cheese', 'cheese_slice', 'queso', 'peynir', 'keju']
SYNONYMS['sweet_potato'] = ['sweet_potato', 'sweet_potatoes', 'camote', 'batata', 'tatli_patates', 'ubi_jalar', 'goguma']
SYNONYMS['mushroom'] += ['lentinus_edodes',            # 표고
                         'pleurotus_eryngii',          # 새송이
                         'flammulina_velutiper', 'flammulina_velutipes',   # 팽이
                         'hypsizygus_marmoreus',       # 만가닥
                         'pleurotus_ostreatus',        # 느타리
                         'pleurotus_citrinopileatus',  # 노랑느타리
                         'agaricus_bisporus']          # 양송이
# 자동 매칭이 안 된 이름을 직접 연결한다 (None 이면 버림)
EXTRA_MAP = {
    'Fresh_Tomato': 'tomato', 'Fresh_Potato': 'potato', 'Fresh_Carrot': 'carrot',
    'vegetable marrow': 'zucchini', 'chillies': 'chili_pepper',
    'red pepper': 'bell_pepper', 'yellow pepper': 'bell_pepper', 'green pepper': 'bell_pepper',
    'eggplant': 'eggplant', 'Eggplant1': 'eggplant',
    'broccoli': 'broccoli', 'brokoli': 'broccoli',
    'corn': 'corn',
}
# 특정 데이터셋에서만 쓰는 매핑. 'radish'는 빨간 래디시일 수 있어서 무 데이터셋에서만 무로 인정한다
_RADISH = {'radish': 'radish', 'radishes': 'radish', 'daikon': 'radish'}
PER_SOURCE = {
    'radish-d1ugk': _RADISH, 'radish': _RADISH, 'radish-akkqa': _RADISH,
    'radish-y3ll3': _RADISH, 'radish-2lmfh': _RADISH,
}
# 재료별 박스 상한: 이미 이만큼 모인 재료'만' 있는 사진은 건너뛴다 (학습 시간 관리)
MAX_BOXES_PER_CLASS = 12000

def norm(s):
    return re.sub(r'[\s\-]+', '_', str(s).strip().lower())

# 클래스 33개 — 0~24는 v3와 같은 번호, 25부터 새 클래스 (번호를 바꾸면 기존 라벨이 틀어지므로 순서 고정)
CLASSES_V4 = [
    ('cabbage', '양배추'), ('green_onion', '대파'), ('onion', '양파'), ('potato', '감자'), ('carrot', '당근'),
    ('zucchini', '애호박'), ('cucumber', '오이'), ('radish', '무'), ('spinach', '시금치'), ('mushroom', '버섯'),
    ('tomato', '토마토'), ('chili_pepper', '고추'), ('garlic', '마늘'), ('egg', '계란'), ('tofu', '두부'),
    ('milk', '우유'), ('apple', '사과'), ('banana', '바나나'), ('lemon', '레몬'), ('bell_pepper', '파프리카'),
    ('eggplant', '가지'), ('broccoli', '브로콜리'), ('corn', '옥수수'), ('cheese', '치즈'), ('sweet_potato', '고구마'),
    ('napa_cabbage', '배추'), ('pear', '배'), ('mandarin', '귤'), ('orange', '오렌지'),
    ('lime', '라임'), ('strawberry', '딸기'), ('grape', '포도'), ('kiwi', '키위'),
]
classes = [{'id': i, 'en': en, 'ko': ko} for i, (en, ko) in enumerate(CLASSES_V4)]
json.dump(classes, open('classes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
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
box_count, unmapped, per_source, dup, capped = Counter(), Counter(), [], 0, 0
for loc in ok:
    y = glob.glob(f'{loc}/**/data.yaml', recursive=True)[0]
    names = yaml.safe_load(open(y))['names']
    names = [names[k] for k in sorted(names)] if isinstance(names, dict) else list(names)
    per = {norm(k): v for k, v in PER_SOURCE.get(Path(loc).name, {}).items()}
    def target(n):
        k = norm(n)
        return per[k] if k in per else SYN.get(k)
    cmap = {i: EN2ID[target(n)] for i, n in enumerate(names) if target(n) in EN2ID}
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
            mine = [(cmap[c], b) for c, b in boxes if c in cmap]
            for c, b in boxes:
                if c not in cmap and c < len(names): unmapped[names[c]] += 1
            if mine and all(box_count[k] >= MAX_BOXES_PER_CLASS for k, _ in mine):
                capped += 1; continue                       # 이미 충분한 재료만 있는 사진
            for k, b in mine:
                lines.append(f'{k} ' + ' '.join(f'{x:.6f}' for x in b)); box_count[k] += 1
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
shutil.copy('classes.json', OUT / 'classes.json')
try:                                                         # 드라이브에도 보관 (웹 데모에 넣을 파일)
    Path('/content/drive/MyDrive/yorijori').mkdir(parents=True, exist_ok=True)
    shutil.copy('classes.json', '/content/drive/MyDrive/yorijori/classes_v4.json')
except Exception: pass

# ---------- 3) 결과 ----------
print('\n===== 아래 내용을 복사해서 보내주세요 =====')
print(f'받은 데이터셋 {len(ok)}개, 실패 {len(failed)}개')
for p, e in failed: print('  실패:', p, '-', e)
print(f'사용한 이미지 {n}장 (중복 제거 {dup}장, 상한으로 건너뜀 {capped}장) → train {n_tr} / val {n_va} / test {n - n_tr - n_va}')
print('\n재료별 박스 수:')
for c in classes:
    k = box_count[c['id']]
    note = '  ← AI Hub 합성으로 채움' if c['en'] in ('napa_cabbage',) and k == 0 else '  ← 없음' if k == 0 else '  ← 부족' if k < 150 else ''
    print(f"  {c['id']:>2} {c['ko']}({c['en']}): {k}" + note)
print('\n매칭 안 된 원본 이름(박스 수):')
print('  ' + ', '.join(f'{k}({v})' for k, v in unmapped.most_common(80)) if unmapped else '  없음')
