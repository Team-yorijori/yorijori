"""
기준 데이터 seed SQL 만들기 → backend/src/main/resources/db/migration/V2__seed_ingredient.sql, V3__seed_recipe.sql
  python ai/data/build_seed.py

입력
  ai/data/recipes.json       공공 레시피 537건 (RecipeFetch.java → normalize.py 결과)
  ai/data/master_data.json   데모 v9 의 기준값 (MASTER 재료표 · DEMO_RECIPES · RC_ALIAS · EACH_G · AVOID_GROUPS · DISH_DAYS · SCAN_* )
  ai/train/classes_v4.json, ai/train/history/classes_v3.json

주의: Flyway 는 이미 반영된 V 파일이 바뀌면 실행을 멈춘다(checksum).
      DB에 한 번 올린 뒤에는 이 스크립트로 V2/V3 를 다시 만들지 말고, 바뀐 부분만 V{다음 번호}__설명.sql 로 추가한다.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
import json, re
d = json.load(open(ROOT / 'ai/data/master_data.json', encoding='utf-8'))
pub = json.load(open(ROOT / 'ai/data/recipes.json', encoding='utf-8'))
M = d['MASTER']
OUT = str(ROOT / 'backend/src/main/resources/db/migration') + '/'

def q(s):
    if s is None: return 'NULL'
    s = str(s).replace('\\', '/').replace("'", "''")
    return "'" + s + "'"
def num(x):
    if x is None: return 'NULL'
    if isinstance(x, float) and x.is_integer(): return str(int(x)) if abs(x) < 1e15 else repr(x)
    return repr(x) if isinstance(x, float) else str(x)
def b(x): return 'TRUE' if x else 'FALSE'

def chunks(rows, n=200):
    for i in range(0, len(rows), n): yield rows[i:i+n]

# ---------------- V2: 재료 · 동의어 · 알레르기 · 스캔 클래스 ----------------
ing_id = {}
lines = ['-- =====================================================================',
         '-- 기준 데이터 1: 재료 기준표 · 동의어 · 알레르기 묶음 · 인식 모델 클래스',
         '-- 데모 v9 의 MASTER · RC_ALIAS · EACH_G · AVOID_GROUPS · SCAN_CLASSES · SCAN_AUTO · SCAN_CONFUSE 에서 생성',
         '-- 재료를 추가할 때는 이 파일을 고치지 말고 V{다음 번호}__add_ingredients.sql 로 추가한다.',
         '-- =====================================================================', '',
         '-- 재료 기준표 (데모 MASTER: 이름 → [분류, 냉장 보관일수, 단위, 기본수량, 접시 색])',
         'INSERT INTO ingredient (id, name, category, fridge_days, unit, default_qty, color, each_gram) VALUES']
rows = []
for i, (name, (cat, days, unit, dq, color)) in enumerate(M.items(), 1):
    ing_id[name] = i
    rows.append(f"({i}, {q(name)}, {q(cat)}, {days}, {q(unit)}, {num(float(dq))}, {q(color)}, {num(d['EACH_G'].get(name))})")
lines.append(',\n'.join(rows) + ';'); lines.append('')

# 동의어: 영수증 상품명 규칙 (데모 RC_ALIAS)
seen = set(); rows = []
for alias, canon in d['RC_ALIAS']:
    if alias in seen or alias in M or canon not in ing_id: continue
    seen.add(alias); rows.append(f"({ing_id[canon]}, {q(alias)}, 'RECEIPT')")
# 일반 동의어 (입력·레시피 표기)
for alias, canon in [('쇠고기','소고기'),('파','대파'),('쪽파','대파'),('홍고추','고추'),('청고추','고추'),('양배추잎','양배추'),('알감자','감자'),('미니양배추','양배추'),('메추리알','계란'),('계란노른자','계란'),('계란흰자','계란')]:
    if alias in seen or alias in M: continue
    seen.add(alias); rows.append(f"({ing_id[canon]}, {q(alias)}, 'SYNONYM')")
lines.append('-- 동의어 (RECEIPT: 영수증·주문내역 상품명 규칙 / SYNONYM: 일반 표기)')
lines.append('INSERT INTO ingredient_alias (ingredient_id, alias, source) VALUES')
lines.append(',\n'.join(rows) + ';'); lines.append('')

# 알레르기 묶음
WARN = {'대두': '대두는 간장·된장까지 빠져서 한식 레시피가 많이 줄어듭니다',
        '밀': '밀은 간장에도 들어 있으니 심한 알레르기면 제품 표시를 꼭 확인하세요'}
lines.append('-- v9 알레르기 묶음 (식품 알레르기 표시 대상 위주, 데모 AVOID_GROUPS)')
lines.append('INSERT INTO avoid_group (id, name, sort_no, warning) VALUES')
rows = []; trows = []
for gi, (g, terms) in enumerate(d['AVOID_GROUPS'].items(), 1):
    rows.append(f"({gi}, {q(g)}, {gi}, {q(WARN.get(g))})")
    for ti, t in enumerate(terms): trows.append(f"({gi}, {ti}, {q(t)})")
lines.append(',\n'.join(rows) + ';'); lines.append('')
lines.append('INSERT INTO avoid_group_term (group_id, sort_no, term) VALUES')
lines.append(',\n'.join(trows) + ';'); lines.append('')

# 스캔 클래스
MAP50 = {'양배추':.949,'대파':.808,'양파':.971,'감자':.970,'당근':.872,'애호박':.957,'오이':.888,'무':.891,'시금치':.924,'버섯':.901,
 '토마토':.830,'고추':.814,'마늘':.933,'계란':.852,'두부':.995,'우유':.925,'사과':.903,'바나나':.907,'레몬':.916,'파프리카':.946,
 '가지':.919,'브로콜리':.878,'옥수수':.936,'치즈':.712,'고구마':.904,'배추':.995,'배':.992,'귤':.995,'오렌지':.701,'라임':.885,
 '딸기':.929,'포도':.929,'키위':.933}
v3 = json.load(open(ROOT / 'ai/train/history/classes_v3.json', encoding='utf-8'))
lines.append('-- 인식 모델 클래스. v3(25종, 기준 60% 일괄) / v4(33종, v9 재료별 기준)')
lines.append('INSERT INTO scan_class (model_version, class_id, en_name, ingredient_id, auto_threshold, confuse_with, map50) VALUES')
rows = []
for c in v3:
    rows.append(f"('v3', {c['id']}, {q(c['en'])}, {ing_id[c['ko']]}, 0.6, NULL, NULL)")
for c in d['SCAN_CLASSES']:
    ko = c['ko']
    conf = d['SCAN_CONFUSE'].get(ko)
    rows.append(f"('v4', {c['id']}, {q(c['en'])}, {ing_id[ko]}, {d['SCAN_AUTO'].get(ko, 0.5)}, {q(','.join(conf)) if conf else 'NULL'}, {MAP50.get(ko, 'NULL')})")
lines.append(',\n'.join(rows) + ';'); lines.append('')
open(OUT + 'V2__seed_ingredient.sql', 'w', encoding='utf-8').write('\n'.join(lines))

# ---------------- V3: 레시피 ----------------
DD = d['DISH_DAYS']
def guess(name, typ):
    if typ and typ in DD: return DD[typ]
    if re.search('찌개|국|탕|전골', name): return 3
    if re.search('볶음밥|덮밥|스무디|샐러드', name): return 1
    if re.search('조림|장아찌', name): return 4
    if re.search('무침|나물|생채', name): return 2
    return 2
recipes = []
for r in pub:
    recipes.append((int(r['id'][1:]), r))
names = {r['name'] for r in pub}
nid = 1001
for r in d['DEMO_RECIPES']:
    if r['name'] in names: continue
    recipes.append((nid, r)); nid += 1

def pantry_name(t):
    m = re.match(r'^(.+?)\s+(?:[\d½⅓¼]|약간|적당|조금|한|두|반|少|적량|약)', t)
    n = (m.group(1) if m else t.split(' ')[0]).strip()
    return n[:50]

R = ['-- =====================================================================',
     f'-- 기준 데이터 2: 레시피 {len(recipes)}건',
     '--   id 1~537  : 공공 레시피 (농림수산식품교육문화정보원 레시피 기본·재료·과정정보) — code r1~r537',
     f'--   id 1001~ : 데모 레시피 중 이름이 겹치지 않는 {len(recipes)-len(pub)}건 — code 는 데모 id',
     '-- ingredient_type: MAIN 필수 · SUB 선택 · SEASONING 기본 양념 (추천 계산에서 있는 것으로 본다)',
     '-- storage_days: 만든 요리 냉장 보관 일수 (데모 v8 DISH_DAYS, 분류가 없으면 이름으로 추정)',
     '-- 생성: ai/data/build_seed.py (recipes.json + master_data.json). 직접 고치지 말고 새 V 파일로 덧붙인다.',
     '-- =====================================================================', '']
rows = []
for rid, r in recipes:
    rows.append(f"({rid}, {q(r['id'])}, {q(r['name'])}, {q(r.get('summary'))}, {num(r.get('time'))}, {q(r.get('diff'))}, {num(r.get('serv'))}, "
                f"{q(r.get('type'))}, {q(r.get('nation'))}, {q(r.get('kcal'))}, {q(r.get('src'))}, {guess(r['name'], r.get('type'))})")
for ch in chunks(rows):
    R.append('INSERT INTO recipe (id, code, title, description, cook_time_min, difficulty, servings, category, cuisine, kcal, source, storage_days) VALUES')
    R.append(',\n'.join(ch) + ';'); R.append('')
rows = []
for rid, r in recipes:
    k = 0
    for ing in r['ings']:
        name, amt, opt = ing[0], ing[1], (ing[2] if len(ing) > 2 else 0)
        text = ing[3] if len(ing) > 3 else None
        rows.append(f"({rid}, {num(ing_id.get(name))}, {q(name[:50])}, {num(float(amt)) if amt is not None else 'NULL'}, {q(text)}, {q('SUB' if opt else 'MAIN')}, {b(opt)}, {k})"); k += 1
    for p in r.get('pantry', []):
        rows.append(f"({rid}, NULL, {q(pantry_name(p))}, NULL, {q(p)}, 'SEASONING', TRUE, {k})"); k += 1
for ch in chunks(rows, 300):
    R.append('INSERT INTO recipe_ingredient (recipe_id, ingredient_id, ingredient_name, amount, amount_text, ingredient_type, is_optional, sort_no) VALUES')
    R.append(',\n'.join(ch) + ';'); R.append('')
rows = []
for rid, r in recipes:
    for i, s in enumerate(r['steps'], 1):
        rows.append(f"({rid}, {i}, {q(s)})")
for ch in chunks(rows, 300):
    R.append('INSERT INTO recipe_step (recipe_id, step_no, content) VALUES')
    R.append(',\n'.join(ch) + ';'); R.append('')
open(OUT + 'V3__seed_recipe.sql', 'w', encoding='utf-8').write('\n'.join(R))
print('recipes', len(recipes), 'ingredient rows', sum(len(r['ings'])+len(r.get('pantry',[])) for _, r in recipes))
