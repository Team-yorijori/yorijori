/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 화면 그리기 (홈 · 냉장고 · 레시피 · 상세 · 식재료) */

/* ---------- 렌더 ---------- */
const $ = s => document.querySelector(s);
function chipsHTML(items, removable=true){
  return items.map(f => `<span class="chip"><button class="chip-edit" type="button" data-edit="${f.id}" title="소비기한·수량 고치기">${esc(f.name)} ${ddayTag(f.exp)}</button>${removable?`<button class="x" data-del="${f.id}" aria-label="${esc(f.name)} 삭제">×</button>`:""}</span>`).join("");
}
function sortedFridge(){ return fridge.filter(f => f.qty > 0).slice().sort((a,b) => dday(a.exp) - dday(b.exp)); }

function renderHome(){
  const list = sortedFridge();
  $("#homeChips").innerHTML = list.length ? chipsHTML(list) : `<span style="opacity:.8">아직 재료가 없습니다. 위에서 추가하거나 스캔해 보세요.</span>`;
}
function renderFridge(){
  const list = sortedFridge();
  const groups = {};
  list.forEach(f => { const c = MASTER[f.name] ? MASTER[f.name][0] : "기타"; (groups[c] ||= []).push(f); });
  const cats = CAT_ORDER.filter(c => groups[c]);
  $("#shelf").innerHTML = cats.length ? cats.map(c => `<div><h4>${c}</h4><div class="chips">${chipsHTML(groups[c])}</div></div>`).join("")
    : `<div class="empty" style="color:inherit;opacity:.8">냉장고가 비어 있습니다.</div>`;
  const over = list.filter(f => dday(f.exp) < 0).length, soon = list.filter(f => { const d = dday(f.exp); return d >= 0 && d <= 3; }).length;
  $("#stats").innerHTML = `<div class="stat"><span class="label">전체 재료</span><b>${list.length}</b></div>
    <div class="stat"><span class="label">3일 이내</span><b style="color:var(--danger)">${soon}</b></div>
    <div class="stat"><span class="label">기한 지남</span><b>${over}</b></div>`;
  const urg = list.filter(f => dday(f.exp) <= 5);
  $("#urgentList").innerHTML = urg.length ? urg.map(f => `<li><span><button class="chip-edit" type="button" data-edit="${f.id}">${esc(f.name)}</button> <span class="note">${fmtQty(f.qty)}${esc(f.unit)} · ${md(f.exp)}까지${f.auto?" (자동)":""}</span></span>${ddayTag(f.exp)}</li>`).join("")
    : `<li><span class="sub">5일 안에 기한이 끝나는 재료가 없습니다.</span></li>`;
}
let recLimit = 12, recQuery = "";
function renderRecipes(){
  const q = recQuery.trim();
  // v6: 초성(ㄱㅊㅉㄱ)이나 섞어 쓰기(김ㅊ)도 찾는다
  const all = ranked().filter(m => !q || koHas(m.r.name, q) || m.r.ings.some(i => koHas(i[0], q) || koHas(i[3] || "", q)));
  const list = all.slice(0, recLimit);
  $("#recNote").textContent = `레시피 ${RECIPES.length}개 중 보유 재료 ${sortedFridge().length}개로 만들 수 있는 ${all.length}개 · 간장, 소금 등 기본 양념은 있는 것으로 봅니다`;
  $("#recMore").hidden = all.length <= recLimit;
  $("#recMore").textContent = `더 보기 (${all.length - list.length}개 남음)`;
  document.querySelectorAll("[data-sort]").forEach(b => b.setAttribute("aria-pressed", b.dataset.sort === sortMode));
  $("#recGrid").innerHTML = list.length ? list.map(m => `
    <button class="card rcard" data-open="${m.r.id}">
      <div class="plate" style="--tint:${tint(m.r)}">${plate(m.r)}${m.urgent && m.urgent.d <= 3 ? `<span class="badge tag t-danger">${esc(m.urgent.name)} ${m.urgent.d<0?"기한 지남":"D-"+m.urgent.d} 활용</span>` : ""}</div>
      <h3>${esc(m.r.name)}</h3>
      <div class="rmeta">
        ${m.missing.length ? `<span class="tag t-warn">${m.missing.length}개 부족</span>` : `<span class="tag t-ok">바로 가능</span>`}
        <span class="tag t-soft">보유 ${m.have.length}/${m.have.length + m.missing.length}</span>
        <span class="tag t-soft">${m.r.time}분</span>
        ${m.recent != null ? `<span class="tag t-soft">${m.recent === 0 ? "오늘" : m.recent + "일 전"} 만듦</span>` : ""}
        ${m.avoid && m.avoid.length ? `<span class="tag t-danger">못 먹는 재료: ${esc(m.avoid.join(", "))}</span>` : ""}
      </div>
    </button>`).join("") : `<div class="card empty" style="grid-column:1/-1">냉장고 재료로 만들 수 있는 레시피가 없습니다. 재료를 추가해 보세요.</div>`;
}
let currentRecipe = null;
function renderDetail(){
  if (!currentRecipe) return;
  const m = match(RECIPES.find(r => r.id === currentRecipe));
  const r = m.r;
  const rows = r.ings.map(([name, amt, opt, label]) => {
    const have = stockQty(name), unit = MASTER[name] ? MASTER[name][2] : "";
    if (label) {
      const st = have >= amt ? `<span class="tag t-ok">보유</span>` : have > 0 ? `<span class="tag t-warn">조금 부족</span>` : opt ? `<span class="tag t-soft">선택</span>` : `<span class="tag t-danger">부족</span>`;
      return `<li><span>${esc(name)}${opt?` <span class="note">(선택)</span>`:""}${have>0?` <span class="note">· ${md(stock(name)[0].exp)}까지</span>`:""}</span><span class="amt">${esc(label)}</span>${st}</li>`;
    }
    const st = have >= amt ? `<span class="tag t-ok">보유</span>` : have > 0 ? `<span class="tag t-warn">조금 부족</span>` : opt ? `<span class="tag t-soft">선택</span>` : `<span class="tag t-danger">부족</span>`;
    return `<li><span>${esc(name)}${opt?` <span class="note">(선택)</span>`:""}${have>0?` <span class="note">· ${md(stock(name)[0].exp)}까지</span>`:""}</span><span class="amt">${fmtQty(amt)}${unit}</span>${st}</li>`;
  }).join("");
  $("#detail").innerHTML = `
    <div class="detail-left">
      <h1>${esc(r.name)}</h1>
      ${r.summary ? `<p class="sub" style="margin:-4px 0 12px">${esc(r.summary)}</p>` : ""}
      <div class="plate" style="--tint:${tint(r)}">${plate(r)}</div>
      ${avoidHits(r).length ? `<div class="callout avoid-callout">못 먹는 재료로 설정한 ${esc(josa(avoidHits(r).join(", "), "이", "가"))} 들어갑니다. 재료를 빼거나 바꿔서 만드세요.</div>` : ""}
      ${m.urgent && m.urgent.d <= 5 ? `<div class="callout">소비기한이 ${m.urgent.d<0?"지난":"가까운"} <b style="font-weight:400">${esc(m.urgent.name)}</b>(${m.urgent.d<0?-m.urgent.d+"일 지남":"D-"+m.urgent.d})을 쓰는 요리라 먼저 추천했습니다.</div>` : ""}
    </div>
    <div class="card">
      <div class="sec"><div class="chips"><span class="tag t-soft">${r.time}분</span><span class="tag t-soft">${r.diff}</span><span class="tag t-soft">${r.serv}인분</span>${r.type ? `<span class="tag t-soft">${esc(r.type)}</span>` : ""}${r.kcal ? `<span class="tag t-soft">${esc(r.kcal)}</span>` : ""}
        ${m.missing.length ? `<span class="tag t-warn">${m.missing.map(i=>i[0]).join(", ")} 필요</span>` : `<span class="tag t-ok">지금 바로 만들 수 있음</span>`}</div></div>
      <div class="sec"><h2>재료</h2><ul class="ing">${rows}</ul>${r.pantry && r.pantry.length ? `<div class="note" style="margin-top:8px">기본 양념: ${r.pantry.map(esc).join(", ")}</div>` : `<div class="note" style="margin-top:6px">간장, 소금, 설탕, 고추장 등 기본 양념은 생략했습니다.</div>`}</div>
      ${m.missing.length ? `<div class="cart-row"><button class="btn ghost" type="button" id="toCart">부족한 재료 ${m.missing.length}개 장보기 목록에 담기</button></div>` : ""}
      <div class="sec"><h2>조리 순서</h2><ol class="how">${r.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol></div>
      ${videoHTML(r)}
      ${r.src ? `<div class="note" style="margin-top:14px">레시피 출처: ${esc(r.src)} (공공데이터)</div>` : ""}
      <div class="done-row"><button class="btn strong" id="doneBtn">요리 완료 · 사용 재료 차감</button></div>
    </div>`;
  $("#doneBtn").onclick = () => openDeduct(r);
  const tc = $("#toCart"); if (tc) tc.onclick = () => cartAdd(m.missing.map(i => i[0]), r.name);
}
let itemQuery = "";
function renderItems(){
  const list = sortedFridge().filter(f => !itemQuery.trim() || koHas(f.name, itemQuery.trim()));
  $("#itemRows").innerHTML = list.length ? list.map(f => `
    <tr>
      <td><button class="name-edit" type="button" data-edit="${f.id}">${esc(f.name)}</button></td>
      <td class="sub">${MASTER[f.name] ? MASTER[f.name][0] : "기타"}</td>
      <td><input type="number" min="0" step="any" value="${fmtQty(f.qty)}" data-qty="${f.id}" id="q-${f.id}" aria-label="${esc(f.name)} 수량"> ${esc(f.unit)}</td>
      <td class="sub">${md(f.reg)}</td>
      <td><input type="date" value="${f.exp}" data-exp="${f.id}" id="e-${f.id}" aria-label="${esc(f.name)} 소비기한"> ${f.auto ? `<span class="tag t-soft" title="보관 기간으로 계산한 참고용 날짜">자동</span>` : `<span class="tag t-ok">직접</span>`}</td>
      <td>${ddayTag(f.exp)}</td>
      <td><button class="btn danger" data-del="${f.id}">삭제</button></td>
    </tr>`).join("") : `<tr><td colspan="7" class="empty">${itemQuery.trim() ? "찾는 재료가 없습니다." : "등록된 식재료가 없습니다."}</td></tr>`;
}
function renderAll(){ renderHome(); renderFridge(); renderRecipes(); renderDetail(); renderItems(); renderCart(); renderDishes(); }
