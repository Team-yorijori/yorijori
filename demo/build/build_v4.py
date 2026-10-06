"""v3 + 공공 레시피 537건 → 요리조리_데모_v4.html"""
import json
from pathlib import Path

SRC = Path('/home/claude/yorijori-demo/요리조리_데모_v3.html')
OUT = Path('/home/claude/yorijori-demo/요리조리_데모_v4.html')
RECIPES = Path('/home/claude/yorijori-recipe/recipes.json')

s = SRC.read_text(encoding='utf-8')
def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)

rep('<title>요리조리 v3</title>', '<title>요리조리 v4</title>')

# ---------- 1) 레시피: 기존 데모 레시피는 남기고, 공공 레시피를 앞에 붙인다 ----------
rep('// [재료, 수량, 선택재료여부]\nconst RECIPES = [', '// [재료, 수량, 선택재료여부]\nconst DEMO_RECIPES = [')
rep('\n/* ---------- 날짜 유틸 ---------- */', '''
// v4: 공공 레시피 537건(농림수산식품교육문화정보원 레시피 기본·재료·과정정보) + 이름이 겹치지 않는 데모 레시피
// 재료 형식: [표준 재료명, 냉장고 단위 수량, 선택재료(1)/필수(0), 원래 표기("양지머리 100g")]
const PUBLIC_RECIPES = JSON.parse(document.getElementById("recipeData").textContent);
const RECIPES = [...PUBLIC_RECIPES, ...DEMO_RECIPES.filter(d => !PUBLIC_RECIPES.some(p => p.name === d.name))];

/* ---------- 날짜 유틸 ---------- */''')

# ---------- 2) 재료 마스터: 레시피에 자주 나오는 냉장고 재료 추가 ----------
rep('''  "사과":["과일",30,"개",3,"#D9443A"],"바나나":["과일",5,"개",4,"#F4D35E"],"레몬":["과일",21,"개",2,"#F7E04B"]
};''', '''  "사과":["과일",30,"개",3,"#D9443A"],"바나나":["과일",5,"개",4,"#F4D35E"],"레몬":["과일",21,"개",2,"#F7E04B"],
  // v4 추가: 공공 레시피에 자주 나오는 재료
  "배추":["채소",14,"포기",1,"#DDEBB8"],"부추":["채소",5,"단",1,"#4E9A3F"],"미나리":["채소",5,"단",1,"#6DAA4F"],
  "깻잎":["채소",7,"묶음",1,"#3E7D3A"],"상추":["채소",5,"봉",1,"#8CC56B"],"숙주":["채소",3,"봉",1,"#F1EBC9"],
  "양상추":["채소",7,"통",1,"#B9DC8E"],"쑥갓":["채소",4,"단",1,"#5E9E4A"],"단호박":["채소",14,"개",1,"#3F6B3A"],
  "생강":["채소",30,"톨",1,"#D8B27A"],"배":["과일",21,"개",2,"#E9D9A6"],"밤":["과일",14,"g",300,"#9A6A3E"],
  "오징어":["해산물",2,"마리",2,"#F2DCD2"],"새우":["해산물",2,"g",300,"#F29C7B"],"바지락":["해산물",2,"g",500,"#CDBBA6"],
  "고등어":["해산물",2,"마리",1,"#6E8296"],"낙지":["해산물",2,"마리",1,"#C98A86"],"굴":["해산물",2,"g",300,"#D9D3C7"],
  "햄":["가공식품",14,"g",200,"#E9A3A3"],"베이컨":["가공식품",7,"g",200,"#D47B6E"],"게맛살":["가공식품",14,"g",150,"#F08A7A"],
  "버터":["유제품·알",60,"g",200,"#F6E3A1"],"생크림":["유제품·알",7,"ml",200,"#FBF7EE"]
};''')
rep('const CAT_ORDER = ["채소","과일","육류","유제품·알","가공식품","반찬","곡류","기타"];',
    'const CAT_ORDER = ["채소","과일","육류","해산물","유제품·알","가공식품","반찬","곡류","기타"];')

# ---------- 3) 매칭: 필수 재료가 없는 레시피는 전체 재료로 계산 ----------
rep('''function match(r){
  const req = r.ings.filter(i => !i[2]), opt = r.ings.filter(i => i[2]);''', '''function match(r){
  const req0 = r.ings.filter(i => !i[2]);
  const req = req0.length ? req0 : r.ings, opt = req0.length ? r.ings.filter(i => i[2]) : [];''')

# ---------- 4) 추천 목록: 검색 + 더 보기 ----------
rep('''        <h1>AI 매칭 레시피</h1>
        <div class="note" id="recNote"></div>
      </div>''', '''        <h1>AI 매칭 레시피</h1>
        <div class="note" id="recNote"></div>
      </div>
      <input class="field rec-search" id="recSearch" type="search" placeholder="요리 이름이나 재료로 찾기" aria-label="레시피 검색">''')
rep('''    <div class="grid" id="recGrid"></div>''', '''    <div class="grid" id="recGrid"></div>
    <div class="more-row"><button class="btn ghost" id="recMore" hidden>더 보기</button></div>''')
rep('''function renderRecipes(){
  const list = ranked().slice(0,6);
  $("#recNote").textContent = `보유 재료 ${sortedFridge().length}개 기준 · 간장, 소금 등 기본 양념은 있는 것으로 봅니다`;''', '''let recLimit = 12, recQuery = "";
function renderRecipes(){
  const q = recQuery.trim();
  const all = ranked().filter(m => !q || m.r.name.includes(q) || m.r.ings.some(i => i[0].includes(q) || (i[3] || "").includes(q)));
  const list = all.slice(0, recLimit);
  $("#recNote").textContent = `레시피 ${RECIPES.length}개 중 보유 재료 ${sortedFridge().length}개로 만들 수 있는 ${all.length}개 · 간장, 소금 등 기본 양념은 있는 것으로 봅니다`;
  $("#recMore").hidden = all.length <= recLimit;
  $("#recMore").textContent = `더 보기 (${all.length - list.length}개 남음)`;''')

# ---------- 5) 레시피 상세: 원래 분량 표기, 요약, 기본 양념, 출처 ----------
rep('''  const rows = r.ings.map(([name, amt, opt]) => {
    const have = stockQty(name), unit = MASTER[name] ? MASTER[name][2] : "";''', '''  const rows = r.ings.map(([name, amt, opt, label]) => {
    const have = stockQty(name), unit = MASTER[name] ? MASTER[name][2] : "";
    if (label) {
      const st = have >= amt ? `<span class="tag t-ok">보유</span>` : have > 0 ? `<span class="tag t-warn">조금 부족</span>` : opt ? `<span class="tag t-soft">선택</span>` : `<span class="tag t-danger">부족</span>`;
      return `<li><span>${esc(name)}${opt?` <span class="note">(선택)</span>`:""}${have>0?` <span class="note">· ${md(stock(name)[0].exp)}까지</span>`:""}</span><span class="amt">${esc(label)}</span>${st}</li>`;
    }''')
rep('''      <h1>${esc(r.name)}</h1>
      <div class="plate" style="--tint:${tint(r)}">${plate(r)}</div>''', '''      <h1>${esc(r.name)}</h1>
      ${r.summary ? `<p class="sub" style="margin:-4px 0 12px">${esc(r.summary)}</p>` : ""}
      <div class="plate" style="--tint:${tint(r)}">${plate(r)}</div>''')
rep('''<span class="tag t-soft">${r.serv}인분</span>''', '''<span class="tag t-soft">${r.serv}인분</span>${r.type ? `<span class="tag t-soft">${esc(r.type)}</span>` : ""}${r.kcal ? `<span class="tag t-soft">${esc(r.kcal)}</span>` : ""}''')
rep('''<div class="note" style="margin-top:6px">간장, 소금, 설탕, 고추장 등 기본 양념은 생략했습니다.</div></div>''',
    '''${r.pantry && r.pantry.length ? `<div class="note" style="margin-top:8px">기본 양념: ${r.pantry.map(esc).join(", ")}</div>` : `<div class="note" style="margin-top:6px">간장, 소금, 설탕, 고추장 등 기본 양념은 생략했습니다.</div>`}</div>''')
rep('''      <div class="done-row"><button class="btn strong" id="doneBtn">요리 완료 · 사용 재료 차감</button></div>''',
    '''      ${r.src ? `<div class="note" style="margin-top:14px">레시피 출처: ${esc(r.src)} (공공데이터)</div>` : ""}
      <div class="done-row"><button class="btn strong" id="doneBtn">요리 완료 · 사용 재료 차감</button></div>''')

# ---------- 6) 스타일 ----------
rep('''/* ---------- v3: 실제 스캔 ---------- */''', '''/* ---------- v4: 레시피 검색 · 더 보기 ---------- */
.rec-search{max-width:260px;border-radius:999px}
.more-row{display:flex;justify-content:center;margin-top:18px}
.ing .amt{text-align:right;max-width:46%;line-height:1.35}
@container app (max-width:640px){ .rec-search{max-width:none;width:100%} }

/* ---------- v3: 실제 스캔 ---------- */''')

# ---------- 7) 이벤트 ----------
rep('''$("#scanBtn").onclick = openScan;''', '''$("#scanBtn").onclick = openScan;
$("#recSearch").addEventListener("input", e => { recQuery = e.target.value; recLimit = 12; renderRecipes(); });
$("#recMore").onclick = () => { recLimit += 12; renderRecipes(); };''')

# ---------- 8) 레시피 데이터 (본문 스크립트보다 앞에) ----------
data = RECIPES.read_text(encoding='utf-8').replace('</', '<\\/')
first_script = s.index('<script>\n/*\n * fridge-scan.js')
s = s[:first_script] + f'<script id="recipeData" type="application/json">{data}</script>\n' + s[first_script:]

OUT.write_text(s, encoding='utf-8')
print('written', OUT, round(OUT.stat().st_size / 1e6, 1), 'MB')
