"""v8 + 인식 모델 v4(33종) · 재료별 인식 기준 · 여러 장 이어서 스캔 · 못 먹는 재료 → 요리조리_데모_v9.html"""
import base64, json, re
from pathlib import Path

SRC = Path('/home/claude/yorijori-demo/요리조리_데모_v8.html')
OUT = Path('/home/claude/yorijori-demo/요리조리_데모_v9.html')
UP = Path('/root/.claude/uploads/812b88c2-0a5f-5a54-b556-cc02749e5f94')
MODEL = UP / 'd97d8e25-fridge_v4.onnx'
CLASSES = json.loads((UP / '2d74ca48-classes_v4.json').read_text(encoding='utf-8'))
assert len(CLASSES) == 33

s = SRC.read_text(encoding='utf-8')
def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)

rep('<title>요리조리 v8</title>', '<title>요리조리 v9</title>')

# =====================================================================
# 1) 인식 모델 v4 (33종)
# =====================================================================
b64 = base64.b64encode(MODEL.read_bytes()).decode()
m = re.search(r'(<script id="fridgeModel" type="application/octet-stream">)(.*?)(</script>)', s, re.S)
s = s[:m.start(2)] + b64 + s[m.end(2):]
old_cls = re.search(r'const SCAN_CLASSES = \[.*?\];', s).group(0)
rep(old_cls, '// v3(25종) 클래스 목록은 v4로 교체했다\n'
    '// v4: fridge_v4.onnx — 33종 (v3 25종 + 배추·배·귤·오렌지·라임·딸기·포도·키위). 검증 mAP50 0.905\n'
    'const SCAN_CLASSES = ' + json.dumps(CLASSES, ensure_ascii=False) + ';')
rep('/* ---------- v3: 실제 재료 인식 (YOLO26 fridge_v3.onnx, 브라우저에서 실행) ---------- */',
    '/* ---------- v3~: 실제 재료 인식 (YOLO26, 브라우저에서 실행) · v9부터 fridge_v4.onnx ---------- */')

# 빠른 추가 버튼: 모델이 이제 찾는 과일은 빼고, 아직 못 찾는 재료로
rep('const SCAN_QUICK = ["오렌지","귤","딸기","포도","키위","배","라임","복숭아","계란","우유","두부","대파"];',
    '// v5 목록: ["오렌지","귤","딸기","포도","키위","배","라임","복숭아","계란","우유","두부","대파"]\n'
    '// v9: 모델 v4가 과일 8종을 직접 찾으므로, 아직 못 찾거나 약한 재료로 바꾼다\n'
    'const SCAN_QUICK = ["깻잎","콩나물","두부","대파","부추","상추","숙주","복숭아","블루베리","돼지고기","김치","어묵"];')

# 인식 결과 줄: 재료별 기준으로 자동 체크 + 헷갈리는 재료 대안 버튼
rep('''      ${main.map(g => scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: g.score >= 0.6, color: color(g),
        tag: `<span class="tag ${g.score >= 0.6 ? "t-ok" : "t-warn"}">${g.score >= 0.6 ? "" : "확인 필요 "}${Math.round(g.score * 100)}%</span>` })).join("")}''',
    '''      ${main.map(g => scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: g.score >= autoOf(g.ko), color: color(g),
        tag: scoreTag(g) })).join("")}''')

# 여러 장: 파일 여러 개 고르기 허용 + 새 처리 함수로 교체 (예전 처리 코드는 남겨 둔다)
rep('''    <input type="file" id="scanFile" accept="image/*" capture="environment" hidden>
    <div class="scan-stage" id="scanStage" hidden></div>''', '''    <input type="file" id="scanFile" accept="image/*" multiple hidden>
    <div class="scan-stage" id="scanStage" hidden></div>
    <div class="shot-strip" id="shotStrip" hidden></div>''')
rep('''    <div class="sub" style="margin-top:10px">냉장고나 장바구니 사진을 올리면 재료를 찾아냅니다. 사진은 이 기기 안에서만 분석하고 어디에도 보내지 않습니다.</div>''',
    '''    <div class="sub" style="margin-top:10px">냉장고나 장바구니 사진을 올리면 재료를 찾아냅니다. 냉장고 칸마다 여러 장 찍어도 한 목록에 모입니다. 사진은 이 기기 안에서만 분석하고 어디에도 보내지 않습니다.</div>''')
rep('''    <label class="drop" for="scanFile" id="dropBox">사진을 찍거나 고르세요 (JPG, PNG)</label>
    <input type="file" id="scanFile" accept="image/*" multiple hidden>''', '''    <label class="drop" for="scanFile" id="dropBox">사진을 찍거나 고르세요 (여러 장 가능)</label>
    <input type="file" id="scanFile" accept="image/*" multiple hidden>''')
rep('''  bindScanList();
  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li[data-row]")]''', '''  // v9: 여러 장 이어서 스캔 — 위의 한 장짜리 처리 대신 이 함수를 쓴다
  scanShots = [];
  $("#scanFile").onchange = e => scanFilesV9(e, status);

  bindScanList();
  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li[data-row]")]''')

# 레시피 목록: 제외 재료 표시, 상단에 설정 버튼
rep('''        ${m.recent != null ? `<span class="tag t-soft">${m.recent === 0 ? "오늘" : m.recent + "일 전"} 만듦</span>` : ""}''',
    '''        ${m.recent != null ? `<span class="tag t-soft">${m.recent === 0 ? "오늘" : m.recent + "일 전"} 만듦</span>` : ""}
        ${m.avoid && m.avoid.length ? `<span class="tag t-danger">못 먹는 재료: ${esc(m.avoid.join(", "))}</span>` : ""}''')
rep('''      <input class="field rec-search" id="recSearch"''', '''      <button class="btn ghost avoid-btn" id="avoidBtn" type="button">못 먹는 재료</button>
      <input class="field rec-search" id="recSearch"''')
# 레시피 상세: 경고
rep('''      <div class="plate" style="--tint:${tint(r)}">${plate(r)}</div>''', '''      <div class="plate" style="--tint:${tint(r)}">${plate(r)}</div>
      ${avoidHits(r).length ? `<div class="callout avoid-callout">못 먹는 재료로 설정한 ${esc(josa(avoidHits(r).join(", "), "이", "가"))} 들어갑니다. 재료를 빼거나 바꿔서 만드세요.</div>` : ""}''')

# =====================================================================
# 2) 스타일
# =====================================================================
rep('''@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}''', '''/* ---------- v9 ---------- */
.scan-list .alt{border:1px dashed var(--card-line);background:var(--bg);color:var(--ink);border-radius:999px;padding:2px 8px;font-size:12px;cursor:pointer}
.scan-list .alt:hover{background:var(--field)}
.scan-list .shots{grid-column:2 / -1;font-size:12px;line-height:1.35}
.scan-list .tagcell{flex-wrap:wrap}
.shot-strip{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.shot-strip button{border:1px solid var(--card-line);background:var(--card);border-radius:999px;padding:5px 11px;font-size:13px;color:var(--ink)}
.shot-strip button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:transparent}
.avoid-btn[data-on="true"]{box-shadow:inset 0 0 0 1px var(--danger);color:var(--danger)}
.avoid-callout{background:var(--danger-bg);color:var(--danger)}
.avoid-groups .chip{cursor:pointer;padding:6px 12px}
.avoid-groups .chip[aria-pressed="true"]{background:var(--danger-bg);color:var(--danger);border-color:transparent}
.avoid-mine .chip{background:var(--danger-bg);color:var(--danger);border-color:transparent}
.avoid-opt{display:flex;align-items:center;gap:8px;margin-top:14px;font-size:14px}
@container app (max-width:640px){ .avoid-btn{order:2} }
/* v5~v8 버그 수정: 스캔 창(모달)은 app 컨테이너 밖이라 휴대폰 화면에서 이름 칸이 0px로 찌그러졌다 → 화면 폭 기준으로도 맞춘다 */
@media (max-width:640px){
  .scan-list li, .scan-list li[data-row]{grid-template-columns:auto minmax(0,1fr) auto}
  .scan-list .tagcell{grid-column:2 / -1;justify-content:flex-start}
}

@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}''')

# =====================================================================
# 3) v9 코드
# =====================================================================
V9_JS = r'''
/* =====================================================================
 * v9-1) 재료별 인식 기준 — v4 모델 평가(mAP50)로 정한다
 *   잘 맞히는 재료는 50%부터 자동 체크, 약한 재료는 70% 이상이어야 자동 체크
 * ===================================================================== */
const SCAN_AUTO = {
  // 약함 (mAP50 0.85 미만, 또는 검증 데이터가 거의 없음)
  "오렌지": .7, "치즈": .7, "대파": .7, "고추": .7, "토마토": .7, "계란": .65, "두부": .7,
  // 보통 (0.85~0.90)
  "당근": .6, "브로콜리": .6, "라임": .6, "오이": .6, "무": .6,
  // AI Hub 합성으로만 배운 재료 — 검증 점수는 높지만 실제 사진은 아직 확인 전이라 조금 높게
  "배추": .6, "배": .6, "귤": .6
};
const autoOf = ko => SCAN_AUTO[ko] ?? .5;
// 서로 헷갈리기 쉬운 재료 → 결과 줄에 "혹시 ○○?" 버튼
const SCAN_CONFUSE = {
  // 감은 아직 학습 안 함 → 귤·오렌지로 잡히는 경우가 많다
  "오렌지": ["귤", "레몬", "감"], "귤": ["오렌지", "감"], "레몬": ["라임", "오렌지"], "라임": ["레몬"],
  "양배추": ["배추"], "배추": ["양배추"], "애호박": ["오이"], "오이": ["애호박"],
  "감자": ["고구마"], "고구마": ["감자"], "토마토": ["파프리카"], "파프리카": ["토마토"], "치즈": ["두부"], "두부": ["치즈"]
};
function scoreTag(g){
  const ok = g.score >= autoOf(g.ko), alts = SCAN_CONFUSE[g.ko] || [];
  const av = isAvoided(g.ko);
  return `<span class="tag ${ok ? "t-ok" : "t-warn"}" data-score>${ok ? "" : "확인 필요 "}${Math.round(g.score * 100)}%</span>`
    + (av ? `<span class="tag t-danger">못 먹는 재료</span>` : "")
    + alts.map(a => `<button type="button" class="alt" data-alt="${esc(a)}" title="이름을 ${esc(a)}(으)로 바꾸기">${esc(a)}?</button>`).join("");
}
document.addEventListener("click", e => {
  const b = e.target.closest(".scan-list .alt"); if (!b) return;
  const li = b.closest("li"), inp = li.querySelector("input[type=text]"), old = inp.value.trim();
  inp.value = b.dataset.alt; b.dataset.alt = old; b.textContent = old + "?";
  inp.dispatchEvent(new Event("change", { bubbles: true }));
});

/* =====================================================================
 * v9-2) 여러 장 이어서 스캔 — 냉장고 칸마다 찍어도 한 목록에 모인다
 *   같은 재료는 수량을 더하고, 사진별로 몇 개였는지 줄 아래에 적는다
 * ===================================================================== */
let scanShots = [];
const rowOf = name => [...document.querySelectorAll("#scanList li[data-row]")].find(l => l.querySelector("input[type=text]").value.trim() === name);
function mergeScan(groups){
  const list = $("#scanList"), color = g => SCAN_COLORS[g.id % SCAN_COLORS.length];
  groups.forEach(g => {
    const li = rowOf(g.ko);
    if (li){
      const q = li.querySelector("input[type=number]");
      q.value = fmtQty((parseFloat(q.value) || 0) + scanQty(g.ko, g.count));
      if (g.score > +(li.dataset.score || 0) && !g.cand){
        li.querySelector(".tagcell").innerHTML = scoreTag(g) + `<button class="row-x" type="button" aria-label="이 줄 지우기">×</button>`;
      }
      if (!g.cand && g.score >= autoOf(g.ko)) li.querySelector("input[type=checkbox]").checked = true;
      const sep = list.querySelector(".scan-sep");          // 후보였는데 이번 사진에서 확실히 찾았으면 위로 올린다
      if (!g.cand && sep && (sep.compareDocumentPosition(li) & Node.DOCUMENT_POSITION_FOLLOWING)) list.insertBefore(li, sep);
      li.classList.remove("flash"); void li.offsetWidth; li.classList.add("flash");
    } else {
      const html = scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: !g.cand && g.score >= autoOf(g.ko), color: color(g),
        tag: g.cand ? `<span class="tag t-soft">후보 ${Math.round(g.score * 100)}%</span>` : scoreTag(g) });
      let sep = list.querySelector(".scan-sep");
      if (g.cand && !sep){ list.insertAdjacentHTML("beforeend", `<li class="scan-sep">혹시 이것도 있나요? · 자신 없는 후보라 꺼 두었습니다</li>`); sep = null; }
      if (!g.cand && sep) sep.insertAdjacentHTML("beforebegin", html); else list.insertAdjacentHTML("beforeend", html);
    }
  });
}
function noteShot(groups, no){
  groups.forEach(g => {
    const li = rowOf(g.ko); if (!li) return;
    li.dataset.score = Math.max(+(li.dataset.score || 0), g.cand ? 0 : g.score);
    const shots = JSON.parse(li.dataset.shots || "{}"); shots[no] = (shots[no] || 0) + g.count; li.dataset.shots = JSON.stringify(shots);
  });
  // 사진이 2장 이상이면 모든 줄에 "사진1 2개 · 사진3 1개"처럼 출처를 적는다
  document.querySelectorAll("#scanList li[data-shots]").forEach(li => {
    const shots = JSON.parse(li.dataset.shots);
    let el = li.querySelector(".shots");
    if (!el){ el = document.createElement("span"); el.className = "shots note"; li.appendChild(el); }
    el.textContent = scanShots.length > 1 ? Object.keys(shots).map(k => `사진${k} ${shots[k]}개`).join(" · ") : "";
  });
}
function renderShotStrip(active){
  const el = $("#shotStrip"); if (!el) return;
  el.hidden = scanShots.length < 2;
  el.innerHTML = scanShots.map((sh, i) => `<button type="button" data-shot="${i}" aria-pressed="${i === active}">사진 ${sh.no} · ${sh.groups.filter(g => !g.cand).length}종</button>`).join("");
  el.onclick = e => {
    const b = e.target.closest("[data-shot]"); if (!b) return;
    const st = $("#scanStage"); st.innerHTML = ""; st.appendChild(scanShots[+b.dataset.shot].cv); renderShotStrip(+b.dataset.shot);
  };
}
async function scanFilesV9(e, status){
  const files = [...e.target.files]; e.target.value = "";
  if (!files.length) return;
  if (!$("#scanList")) { scanShots = []; scanRowSeq = 0; }
  $("#scanOk").disabled = true;
  try {
    await ensureModel(status);
    for (const file of files){
      const no = scanShots.length + 1;
      status(`사진 ${no} · 재료를 찾는 중…`);
      const r = await FridgeScan.detect(file, { minScore: SCAN_MIN, confirmBelow: 0.6 });
      await drawScan(file, r);
      const groups = groupScan(r);
      scanShots.push({ no, groups, cv: $("#scanStage canvas") });
      if (!$("#scanList")) { renderScanResult(groups, groups.length ? "" : "이 사진에서는 재료를 찾지 못했습니다. 아래에서 직접 추가하거나 다른 각도로 다시 찍어 보세요.");
        $("#scanOk").disabled = true; }            // 남은 사진을 다 볼 때까지 등록 버튼은 잠가 둔다
      else mergeScan(groups);
      noteShot(groups, no);
      const nMain = groups.filter(g => !g.cand).length, nCand = groups.length - nMain;
      status(`사진 ${scanShots.length}장 · 이번 사진에서 ${nMain}종${nCand ? `(후보 ${nCand}종)` : ""} · ${r.ms}ms`
        + (scanShots.length > 1 ? " · 같은 재료는 수량을 합쳤습니다. 같은 물건을 두 번 찍었다면 수량을 줄이세요" : " · 다른 칸도 찍어서 추가할 수 있습니다 · 깻잎·콩나물처럼 아직 못 찾는 재료는 아래에서 직접 추가하세요"));
    }
    renderShotStrip(scanShots.length - 1);
    $("#dropBox").textContent = "+ 사진 더 추가 (냉장고 다른 칸도 찍으면 한 목록에 모입니다)";
    $("#scanOk").disabled = false;
  } catch (err) {
    status("인식에 실패했습니다: " + (err.message || err), true);
    if (!$("#scanList")){
      $("#scanResult").innerHTML = `<div class="actions" style="justify-content:flex-start"><button class="btn ghost" id="scanDemo">예시 결과로 둘러보기</button></div>`;
      $("#scanDemo").onclick = () => { closeModal(); openScanDemo(); };
    } else $("#scanOk").disabled = false;
  }
}

/* =====================================================================
 * v9-3) 못 먹는 재료 (알레르기·기피) — 추천에서 빼거나 빨갛게 표시
 *   알레르기 묶음은 식품 알레르기 표시 대상 위주. 레시피 재료와 기본 양념까지 확인한다
 * ===================================================================== */
const AVOID_GROUPS = {
  "계란": ["계란", "달걀", "메추리알", "마요네즈"],
  "우유·유제품": ["우유", "치즈", "버터", "생크림", "요거트", "요구르트", "연유"],
  "밀": ["밀가루", "부침가루", "튀김가루", "빵가루", "국수", "소면", "라면", "우동", "파스타", "스파게티", "만두", "빵"],
  "대두": ["두부", "콩", "된장", "간장", "두유", "유부"],
  "땅콩·견과": ["땅콩", "호두", "잣", "아몬드", "캐슈넛", "피스타치오"],
  "메밀": ["메밀"],
  "새우": ["새우"],
  "게": ["게", "꽃게", "대게", "게맛살"],
  "조개류": ["조개", "바지락", "굴", "전복", "홍합", "가리비", "꼬막"],
  "오징어": ["오징어"],
  "고등어": ["고등어"],
  "돼지고기": ["돼지고기", "삼겹살", "베이컨", "햄", "스팸"],
  "닭고기": ["닭고기", "닭"],
  "소고기": ["소고기", "쇠고기"],
  "복숭아": ["복숭아"],
  "토마토": ["토마토", "케첩"]
};
const AVOID_KEY = "yorijori-demo-avoid-v1";
let avoid = (() => { try { return JSON.parse(localStorage.getItem(AVOID_KEY) || "null") || { groups: [], items: [], show: false }; } catch(e){ return { groups: [], items: [], show: false }; } })();
const saveAvoid = () => { try { localStorage.setItem(AVOID_KEY, JSON.stringify(avoid)); } catch(e){} AVOID_CACHE.clear(); };
const AVOID_CACHE = new Map();
const avoidTerms = () => [...new Set([...avoid.groups.flatMap(g => AVOID_GROUPS[g] || []), ...avoid.items])];
const isAvoided = name => !!name && avoidTerms().some(t => name.includes(t));
/** 레시피에 들어 있는 못 먹는 재료(설정한 이름 기준) */
function avoidHits(r){
  const terms = avoidTerms(); if (!terms.length) return [];
  if (AVOID_CACHE.has(r.id)) return AVOID_CACHE.get(r.id);
  const texts = [...r.ings.map(i => i[0] + " " + (i[3] || "")), ...(r.pantry || [])].join(" | ");
  const hits = terms.filter(t => texts.includes(t));
  AVOID_CACHE.set(r.id, hits); return hits;
}
// 추천 목록: 못 먹는 재료가 든 레시피는 빼거나(기본) 표시만 한다
const _rankedV8 = ranked;
ranked = function(){
  const list = _rankedV8();
  list.forEach(m => m.avoid = avoidHits(m.r));
  // 표시만 하는 모드에서는 못 먹는 재료가 든 레시피를 뒤로 보낸다
  return avoid.show ? [...list.filter(m => !m.avoid.length), ...list.filter(m => m.avoid.length)] : list.filter(m => !m.avoid.length);
};
const _renderRecipesV8 = renderRecipes;
renderRecipes = function(){
  _renderRecipesV8();
  const n = avoidTerms().length, btn = $("#avoidBtn");
  if (btn){ btn.dataset.on = n > 0; btn.textContent = n ? `못 먹는 재료 ${avoid.groups.length + avoid.items.length}` : "못 먹는 재료"; }
  if (n){
    const hidden = _rankedV8().filter(m => avoidHits(m.r).length).length;
    $("#recNote").textContent += avoid.show ? ` · 못 먹는 재료가 든 레시피 ${hidden}개는 빨갛게 표시` : ` · 못 먹는 재료가 든 레시피 ${hidden}개 제외`;
  }
};
// 냉장고에 못 먹는 재료를 넣으면 알려 준다
const _addItemV8 = addItem;
addItem = function(rawName, manualDate, qty){
  const r = _addItemV8(rawName, manualDate, qty);
  if (r && r.msg && isAvoided(rawName.trim())) r.msg += " · 못 먹는 재료로 설정된 재료입니다";
  return r;
};

function openAvoid(){
  const draw = () => {
    $("#avoidGroups").innerHTML = Object.keys(AVOID_GROUPS).map(g => `<button type="button" class="chip" data-g="${esc(g)}" aria-pressed="${avoid.groups.includes(g)}">${esc(g)}</button>`).join("");
    $("#avoidExpand").textContent = (avoid.groups.length ? "확인하는 이름: " + avoid.groups.flatMap(g => AVOID_GROUPS[g]).join(", ") : "")
      + (avoid.groups.includes("대두") ? " · 대두는 간장·된장까지 빠져서 한식 레시피가 많이 줄어듭니다" : "")
      + (avoid.groups.includes("밀") ? " · 밀은 간장에도 들어 있으니 심한 알레르기면 제품 표시를 꼭 확인하세요" : "");
    $("#avoidMine").innerHTML = avoid.items.length ? avoid.items.map(t => `<span class="chip">${esc(t)}<button class="x" type="button" data-rm="${esc(t)}" aria-label="${esc(t)} 빼기">×</button></span>`).join("")
      : `<span class="note">직접 추가한 재료가 없습니다.</span>`;
    $("#avoidShow").checked = !!avoid.show;
  };
  modal(`<h2>못 먹는 재료</h2>
    <div class="sub">알레르기가 있거나 싫어하는 재료를 고르면, 그 재료가 들어간 레시피를 추천에서 뺍니다. 레시피 재료와 기본 양념(간장·된장 등)까지 확인합니다.</div>
    <div class="label" style="margin-top:14px">알레르기 (식품 알레르기 표시 대상 위주)</div>
    <div class="chips avoid-groups" id="avoidGroups" style="margin-top:6px"></div>
    <div class="note" id="avoidExpand" style="margin-top:6px"></div>
    <div class="label" style="margin-top:14px">재료 직접 추가 (예: 오이, 가지, 고수)</div>
    <form class="row" id="avoidForm" style="margin-top:6px"><input class="field" id="avoidInput" data-ac autocomplete="off" placeholder="재료 이름 (초성 가능)" aria-label="못 먹는 재료"><button class="btn" type="submit">추가</button></form>
    <div class="chips avoid-mine" id="avoidMine" style="margin-top:8px"></div>
    <label class="avoid-opt"><input type="checkbox" id="avoidShow"> 빼지 말고 빨갛게 표시만 하기</label>
    <div class="actions"><button class="btn ghost" type="button" id="avoidClear" style="margin-right:auto">모두 지우기</button><button class="btn strong" data-close>완료</button></div>`);
  draw();
  const changed = () => { saveAvoid(); draw(); renderAll(); };
  $("#avoidGroups").onclick = e => {
    const b = e.target.closest("[data-g]"); if (!b) return;
    const g = b.dataset.g; avoid.groups = avoid.groups.includes(g) ? avoid.groups.filter(x => x !== g) : [...avoid.groups, g]; changed();
  };
  $("#avoidForm").onsubmit = e => {
    e.preventDefault(); const t = $("#avoidInput").value.trim(); if (!t) return;
    if (!avoid.items.includes(t)) avoid.items.push(t); $("#avoidInput").value = ""; acClose(); changed();
  };
  $("#avoidMine").onclick = e => { const b = e.target.closest("[data-rm]"); if (!b) return; avoid.items = avoid.items.filter(x => x !== b.dataset.rm); changed(); };
  $("#avoidShow").onchange = e => { avoid.show = e.target.checked; changed(); };
  $("#avoidClear").onclick = () => { avoid = { groups: [], items: [], show: false }; changed(); };
}
'''
rep('''/* 로그인(데모) */''', V9_JS + '''
/* 로그인(데모) */''')

# 이벤트
rep('''/* ---------- v8 이벤트 ---------- */''', '''/* ---------- v9 이벤트 ---------- */
$("#avoidBtn").onclick = openAvoid;
renderRecipes();

/* ---------- v8 이벤트 ---------- */''')

OUT.write_text(s, encoding='utf-8')
print('written', OUT, round(OUT.stat().st_size / 1e6, 1), 'MB')
