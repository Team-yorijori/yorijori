/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 못 먹는 재료 · 알레르기 (v9) */

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
