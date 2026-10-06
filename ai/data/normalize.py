"""
공공 레시피 3종(기본·재료·과정) → 우리 서비스용 레시피 데이터로 정리한다.

- 재료 이름 통일: 쇠고기/다진쇠고기 → 소고기, 홍고추/청고추/풋고추 → 고추 ...
- 기본 양념(소금, 간장, 물 ...)은 매칭에서 빼고 '기본 양념' 목록으로 따로 보관
- 주재료 = 필수, 부재료 = 선택, 양념 = 기본 양념
- 분량 문자열("1/2개", "200g", "1과1/2컵", "약간")을 숫자+단위로 해석
- 결과: recipes.json (데모용), recipe_seed.sql (Spring/MySQL 초기 데이터)
"""
import glob, json, re, collections
from pathlib import Path

RAW = Path(__file__).parent / 'raw' / 'recipe_data'
OUT = Path(__file__).parent

def rows(prefix):
    out = []
    for f in sorted(RAW.glob(f'{prefix}_*.json')):
        d = json.load(open(f, encoding='utf-8'))
        out += list(d.values())[0]['row']
    return out

# ---------- 재료 이름 통일 ----------
ALIAS = {
    '소고기': ['쇠고기', '다진쇠고기', '소고기', '다진소고기', '양지머리', '갈비', '쇠고기등심', '소고기등심', '사태', '안심', '등심', '차돌박이',
              '우둔', '우둔살', '홍두깨살', '불고기감', '쇠고기안심', '쇠고기우둔살', '소고기안심'],
    '돼지고기': ['돼지고기', '돼기고기', '다진돼지고기', '삼겹살', '돼지갈비', '돼지고기목살', '목살'],
    '닭고기': ['닭', '닭고기', '닭가슴살', '닭다리', '닭날개'],
    '계란': ['계란', '달걀', '계란노른자', '계란흰자', '달걀노른자', '달걀흰자', '삶은계란'],
    '대파': ['대파', '실파', '파', '쪽파', '다진파'],
    '고추': ['고추', '홍고추', '청고추', '풋고추', '청양고추', '다진풋고추', '다진홍고추', '다진청고추', '다진고추'],
    '마늘': ['마늘', '다진마늘', '통마늘', '깐마늘'],
    '생강': ['생강', '생강즙', '다진생강', '통생강'],
    '버섯': ['표고버섯', '느타리버섯', '팽이버섯', '양송이버섯', '양송이', '새송이버섯', '목이버섯', '석이버섯',
             '말린표고버섯', '싸리버섯', '버섯', '건표고버섯'],
    '애호박': ['애호박', '호박'],
    '파프리카': ['파프리카', '피망', '청피망', '홍피망', '노랑파프리카', '빨강파프리카'],
    '브로콜리': ['브로콜리', '브로코리'],
    '옥수수': ['옥수수', '옥수수통조림', '옥수수콘', '스위트콘'],
    '토마토': ['토마토', '방울토마토'],
    '레몬': ['레몬', '레몬즙'],
    '치즈': ['치즈', '모짜렐라치즈', '모차렐라치즈', '슬라이스치즈', '체다치즈'],
    '김치': ['김치', '배추김치', '신김치'],
    '떡': ['떡', '가래떡', '흰떡', '떡볶이떡'],
    '참치캔': ['참치', '참치캔', '참치통조림'],
    '배추': ['배추', '배춧잎', '알배추'],
    '양배추': ['양배추', '적채'],
    '상추': ['상추', '꽃상추'],
    '무': ['무', '동치미무'],
    '오징어': ['오징어', '갑오징어'],
    '새우': ['새우', '대하', '칵테일새우', '중하'],
    '밥': ['밥', '찬밥'],
    '우유': ['우유'],
    '감자': ['감자'], '양파': ['양파', '다진양파'], '당근': ['당근'], '오이': ['오이'], '두부': ['두부'],
    '시금치': ['시금치'], '가지': ['가지'], '고구마': ['고구마'], '사과': ['사과'], '바나나': ['바나나'],
    '콩나물': ['콩나물'], '숙주': ['숙주', '숙주나물'], '어묵': ['어묵', '사각어묵'], '게맛살': ['게맛살', '맛살'], '부추': ['부추'], '미나리': ['미나리'],
    '깻잎': ['깻잎'], '단호박': ['단호박'], '햄': ['햄'], '베이컨': ['베이컨'], '버터': ['버터'],
    '생크림': ['생크림'], '바지락': ['바지락', '모시조개'], '고등어': ['고등어'], '낙지': ['낙지'], '굴': ['굴'],
    '양상추': ['양상추'], '쑥갓': ['쑥갓'], '배': ['배'], '밤': ['밤', '깐밤'],
}
CANON = {}
for canon, names in ALIAS.items():
    for n in names:
        CANON[n.replace(' ', '')] = canon

# 기본 양념·주방 상비품: 냉장고 재료 매칭에서 제외
PANTRY = set('''
물 생수 소금 맛소금 굵은소금 설탕 흑설탕 황설탕 흰설탕 식용유 포도씨유 튀김기름 식물성기름 올리브오일 올리브유 들기름 참기름
간장 진간장 국간장 양조간장 맛간장 후춧가루 후추 통후추 흰후춧가루 깨소금 통깨 깨 검은깨 고춧가루 고추가루 굵은고춧가루 고운고춧가루
식초 고추장 된장 쌈장 초고추장 밀가루 녹말 녹말가루 전분 감자전분 튀김가루 부침가루 빵가루 청주 정종 맛술 미림 조미술 술
물엿 올리고당 꿀 마요네즈 케첩 토마토케첩 토마토케찹 육수 다시물 쌀뜨물 멸칫국물 다시마 멸치 국물용멸치 육수용멸치 가쓰오브시
가쓰오브시국물 쇠고기육수 새우젓 멸치젓 멸치액젓 까나리액젓 액젓 굴소스 겨자 연겨자 와사비 고추냉이 머스터드 카레가루 실고추 마른고추
쌀 불린쌀 멥쌀 불린멥쌀 월계수잎 계핏가루 파슬리가루 고추기름 매실액
'''.split())

def clean_name(n):
    n = re.sub(r'\[.*?\]', '', n)          # [절임용 소금물] 소금 → 소금
    n = re.sub(r'\(.*?\)', '', n)
    return n.replace(' ', '').strip()

# ---------- 분량 해석 ----------
UNIT_ALIAS = {'T': '큰술', 't': '작은술', 'Ts': '큰술', 'ts': '작은술', 'kg': 'kg', 'g': 'g', 'G': 'g', 'ml': 'ml', 'cc': 'ml'}

def parse_qty(s):
    s = (s or '').strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)        # 엑셀이 1/3 을 날짜로 바꾼 경우
    if m:
        s = f'{int(m.group(2))}/{int(m.group(3))}'
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(?:과|와|\+)\s*(\d+)\s*/\s*(\d+)\s*(.*)$', s)   # 1과1/2컵
    if m:
        return float(m.group(1)) + int(m.group(2)) / int(m.group(3)), m.group(4).strip(), s
    m = re.match(r'^(\d+)\s*/\s*(\d+)\s*(.*)$', s)       # 1/2개
    if m:
        return int(m.group(1)) / int(m.group(2)), m.group(3).strip(), s
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(?:~\s*\d+(?:\.\d+)?)?\s*(.*)$', s)   # 200g, 2~3개
    if m:
        return float(m.group(1)), m.group(2).strip(), s
    return None, '', s                                     # 약간, 적당량

# 데모 MASTER 단위(재료 → 냉장고에서 쓰는 단위, 기본 수량)
MASTER_UNIT = {
    '양배추': ('통', 1), '대파': ('단', 1), '양파': ('개', 3), '감자': ('개', 4), '당근': ('개', 2), '애호박': ('개', 1),
    '시금치': ('단', 1), '콩나물': ('봉', 1), '버섯': ('팩', 1), '토마토': ('개', 3), '마늘': ('쪽', 10), '계란': ('개', 10),
    '우유': ('ml', 1000), '치즈': ('장', 10), '두부': ('모', 1), '어묵': ('장', 4), '참치캔': ('캔', 2), '떡': ('g', 500),
    '돼지고기': ('g', 600), '닭고기': ('g', 1000), '소고기': ('g', 400), '김치': ('g', 1000), '밥': ('공기', 2),
    '오이': ('개', 2), '무': ('개', 1), '고추': ('개', 10), '파프리카': ('개', 2), '가지': ('개', 2), '브로콜리': ('송이', 1),
    '옥수수': ('개', 2), '고구마': ('개', 3), '사과': ('개', 3), '바나나': ('개', 4), '레몬': ('개', 2),
    '배추': ('포기', 1), '부추': ('단', 1), '미나리': ('단', 1), '깻잎': ('묶음', 1), '상추': ('봉', 1), '숙주': ('봉', 1),
    '생강': ('톨', 1), '오징어': ('마리', 2), '새우': ('g', 300), '햄': ('g', 200), '베이컨': ('g', 200), '버터': ('g', 200),
    '생크림': ('ml', 200), '단호박': ('개', 1), '바지락': ('g', 500), '고등어': ('마리', 1), '낙지': ('마리', 1), '굴': ('g', 300),
    '양상추': ('통', 1), '쑥갓': ('단', 1), '배': ('개', 2), '밤': ('g', 300),
}
COUNT_UNITS = {'개', '단', '모', '송이', '장', '통', '봉', '팩', '포기', '마리', '공기', '쪽', '캔', '묶음', '톨', '뿌리', '줌', '대'}

def to_amount(canon, num, unit):
    """레시피 분량을 냉장고 단위로 바꾼다. 못 바꾸면 무난한 추정값을 쓴다(사용자가 차감 화면에서 고칠 수 있음)."""
    mu = MASTER_UNIT.get(canon)
    unit = UNIT_ALIAS.get(unit, unit)
    if mu:
        mu_unit, mu_def = mu
        if num is not None:
            if unit == mu_unit: return round(num, 2)
            if unit == 'kg' and mu_unit == 'g': return round(num * 1000, 2)
            if mu_unit == 'ml' and unit == '컵': return round(num * 200, 2)
            if mu_unit in COUNT_UNITS and unit in COUNT_UNITS: return round(num, 2)
            if mu_unit == '쪽' and unit in ('큰술',): return round(num * 3, 2)   # 다진마늘 1큰술 ≈ 3쪽
        return 1 if mu_unit in COUNT_UNITS else round(mu_def * 0.25, 2)
    return round(num, 2) if num is not None else 1

def to_int(s, default):
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else default

# ---------- 조립 ----------
B, I, P = rows('basic'), rows('ingredient'), rows('process')
basic = {r['RECIPE_ID']: r for r in B}
ings = collections.defaultdict(list)
for r in sorted(I, key=lambda r: (r['RECIPE_ID'], r['IRDNT_SN'])):
    if r['RECIPE_ID'] in basic: ings[r['RECIPE_ID']].append(r)
steps = collections.defaultdict(list)
for r in sorted(P, key=lambda r: (r['RECIPE_ID'], r['COOKING_NO'])):
    if r['RECIPE_ID'] in basic: steps[r['RECIPE_ID']].append(r)

unmapped = collections.Counter()
recipes = []
for rid, b in basic.items():
    merged, pantry = {}, []
    for it in ings[rid]:
        raw_name = it['IRDNT_NM'].strip()
        name = clean_name(raw_name)
        num, unit, qtxt = parse_qty(it['IRDNT_CPCTY'])
        ty = it['IRDNT_TY_NM']
        if ty == '양념' or name in PANTRY:
            pantry.append(f"{raw_name} {qtxt}".strip()); continue
        canon = CANON.get(name)
        if canon is None:
            canon = name; unmapped[name] += 1
        optional = 1 if ty == '부재료' else 0
        amt = to_amount(canon, num, unit)
        label = f"{raw_name} {qtxt}".strip()
        if canon in merged:                       # 홍고추+청고추 → 고추 하나로
            m = merged[canon]
            m[1] = round(m[1] + amt, 2); m[2] = min(m[2], optional); m[3] += f" · {label}"
        else:
            merged[canon] = [canon, amt, optional, label]
    ing_list = list(merged.values())
    if not ing_list:
        continue
    if all(i[2] for i in ing_list):               # 주재료가 전부 양념뿐인 레시피 → 부재료를 필수로
        for i in ing_list: i[2] = 0
    ing_list.sort(key=lambda i: i[2])             # 필수 재료 먼저
    st = []
    for s in steps[rid]:
        t = re.sub(r'\s+', ' ', s['COOKING_DC'] or '').strip()
        tip = (s.get('STEP_TIP') or '').strip()
        if t: st.append(t + (f' (팁: {tip})' if tip and len(tip) <= 80 else ''))
    recipes.append({
        'id': f"r{rid}", 'name': b['RECIPE_NM_KO'].strip(), 'time': to_int(b['COOKING_TIME'], 30),
        'diff': b['LEVEL_NM'] or '보통', 'serv': to_int(b['QNT'], 2), 'ings': ing_list, 'steps': st,
        'summary': (b['SUMRY'] or '').strip(), 'type': b['TY_NM'], 'nation': b['NATION_NM'],
        'kcal': b['CALORIE'], 'pantry': pantry, 'src': '농림수산식품교육문화정보원',
    })

json.dump(recipes, open(OUT / 'recipes.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ---------- Spring/MySQL 초기 데이터 ----------
def q(s): return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"
sql = ["-- 공공 레시피 537건 정리본 (농림수산식품교육문화정보원 레시피 기본·재료·과정정보)",
       "-- ingredient_type: MAIN(주재료) / SUB(부재료) / SEASONING(기본 양념)", ""]
sql.append("INSERT INTO recipes (recipe_id, title, description, cook_time_min, difficulty, servings, category, cuisine) VALUES")
sql.append(",\n".join(f"({r['id'][1:]}, {q(r['name'])}, {q(r['summary'])}, {r['time']}, {q(r['diff'])}, {r['serv']}, {q(r['type'])}, {q(r['nation'])})" for r in recipes) + ";")
sql.append("")
sql.append("INSERT INTO recipe_ingredients (recipe_id, ingredient_name, amount, amount_text, ingredient_type, is_optional) VALUES")
vals = []
for r in recipes:
    for name, amt, opt, label in r['ings']:
        vals.append(f"({r['id'][1:]}, {q(name)}, {amt}, {q(label)}, {q('SUB' if opt else 'MAIN')}, {'TRUE' if opt else 'FALSE'})")
    for p in r['pantry']:
        vals.append(f"({r['id'][1:]}, {q(p.split(' ')[0])}, NULL, {q(p)}, 'SEASONING', TRUE)")
sql.append(",\n".join(vals) + ";")
sql.append("")
sql.append("INSERT INTO recipe_steps (recipe_id, step_no, content) VALUES")
sql.append(",\n".join(f"({r['id'][1:]}, {n+1}, {q(s)})" for r in recipes for n, s in enumerate(r['steps'])) + ";")
(OUT / 'recipe_seed.sql').write_text("\n".join(sql), encoding='utf-8')

# ---------- 보고 ----------
print(f"레시피 {len(recipes)}개 (재료 {sum(len(r['ings']) for r in recipes)}줄, 단계 {sum(len(r['steps']) for r in recipes)}개)")
used = collections.Counter(i[0] for r in recipes for i in r['ings'])
print("가장 많이 쓰이는 재료:", ", ".join(f"{k}({v})" for k, v in used.most_common(40)))
print("통일하지 않고 원래 이름으로 둔 재료(상위):", ", ".join(f"{k}({v})" for k, v in unmapped.most_common(40)))
SCAN25 = ['양배추','대파','양파','감자','당근','애호박','오이','무','시금치','버섯','토마토','고추','마늘','계란','두부','우유','사과','바나나','레몬','파프리카','가지','브로콜리','옥수수','치즈','고구마']
print("스캔 재료별 레시피 수:", ", ".join(f"{k}({sum(1 for r in recipes if any(i[0]==k for i in r['ings']))})" for k in SCAN25))
