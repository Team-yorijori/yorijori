"""v5 + 소비기한 수정 · 초성 검색 · 영수증/주문내역 인식 · 레시피 영상 · 장보기/최저가 안내 → 요리조리_데모_v6.html"""
from pathlib import Path

SRC = Path('/home/claude/yorijori-demo/요리조리_데모_v5.html')
OUT = Path('/home/claude/yorijori-demo/요리조리_데모_v6.html')

s = SRC.read_text(encoding='utf-8')
def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)

rep('<title>요리조리 v5</title>', '<title>요리조리 v6</title>')

# =====================================================================
# 0) 재료 입력칸: 브라우저 기본 목록(datalist) 대신 초성 자동완성(data-ac)을 쓴다
#    datalist 요소 자체는 남겨 둔다
# =====================================================================
s = s.replace('list="masterList"', 'data-ac autocomplete="off"')

# =====================================================================
# 1) 화면(HTML)
# =====================================================================
# 상단 메뉴에 장보기
rep('''      <button data-go="items">내 식재료</button>
    </nav>''', '''      <button data-go="items">내 식재료</button>
      <button data-go="cart">장보기</button>
    </nav>''')

# 하단 탭바: 식재료 자리에 장보기 (식재료는 냉장고 화면의 '식재료 관리'로 들어간다)
rep('''  <button data-go="items"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>식재료</button>
</nav>''', '''  <button data-go="items" hidden><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>식재료</button>
  <!-- v6: 식재료 탭 자리에 장보기. 식재료 관리는 냉장고 화면 버튼으로 들어간다 -->
  <button data-go="cart"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 4h2l2.4 11.2a1 1 0 0 0 1 .8h9.3a1 1 0 0 0 1-.8L20 8H6.2"/><circle cx="9.5" cy="19.5" r="1.3"/><circle cx="17" cy="19.5" r="1.3"/></svg>장보기</button>
</nav>''')

# 냉장고 화면: 영수증 등록 버튼
rep('''        <div class="hint" id="fridgeHint"></div>
        <div class="label">현재 입력된 재료 · 날짜를 비워두면 소비기한을 자동으로 안내합니다</div>''', '''        <div class="hint" id="fridgeHint"></div>
        <div class="row" style="flex-wrap:wrap;margin:-2px 0 12px">
          <button class="btn ghost" type="button" id="fridgeScan">재료 사진으로 추가</button>
          <button class="btn ghost" type="button" id="fridgeReceipt">영수증·주문내역으로 추가</button>
        </div>
        <div class="label">현재 입력된 재료 · 재료를 누르면 소비기한과 수량을 고칠 수 있습니다</div>''')

# 레시피 검색: 초성 안내
rep('placeholder="요리 이름이나 재료로 찾기" aria-label="레시피 검색"', 'placeholder="요리·재료 검색 (초성 가능: ㄱㅊㅉㄱ)" aria-label="레시피 검색"')

# 내 식재료: 검색칸
rep('''          <div class="note">소비기한이 가까운 순서입니다. '자동' 표시는 앱이 보관 기간으로 계산한 날짜이며, 직접 고칠 수 있습니다.</div>
        </div>
        <button class="btn ghost" id="resetBtn">예시 데이터로 초기화</button>''', '''          <div class="note">소비기한이 가까운 순서입니다. '자동' 표시는 앱이 보관 기간으로 계산한 참고용 날짜이며, 날짜 칸이나 재료 이름을 눌러 고칠 수 있습니다.</div>
        </div>
        <input class="field item-search" id="itemSearch" type="search" placeholder="재료 찾기 (초성 가능)" aria-label="식재료 검색">
        <button class="btn ghost" id="resetBtn">예시 데이터로 초기화</button>''')

# 장보기 화면
rep('''  <!-- 내 식재료 -->''', '''  <!-- v6: 장보기 -->
  <section data-page="cart" hidden>
    <div class="two">
      <div class="card">
        <h1 class="big">장보기</h1>
        <form class="add-row cart-add" id="cartForm">
          <input class="field" id="cartInput" data-ac autocomplete="off" placeholder="살 재료 (초성 가능)" aria-label="살 재료">
          <input class="field date" id="cartTarget" type="number" min="0" step="100" inputmode="numeric" placeholder="목표가(원, 선택)" aria-label="목표가">
          <button class="btn" type="submit">담기</button>
        </form>
        <div class="hint" id="cartHint"></div>
        <div class="label">살 재료 · 레시피 화면에서 부족한 재료를 한 번에 담을 수 있습니다</div>
        <ul class="cart-list" id="cartList"></ul>
      </div>
      <div class="card">
        <h2 style="font-size:20px">최저가 안내</h2>
        <p class="sub" style="margin:6px 0 0">담아 둔 재료의 가격을 매일 쇼핑몰과 비교해서, 목표가 아래로 내려가거나 최근 30일 중 가장 쌀 때 알려 줍니다.</p>
        <ol class="how cart-how">
          <li>필요한 재료를 담는다 (레시피의 부족한 재료도 한 번에)</li>
          <li>사고 싶은 가격(목표가)을 적는다</li>
          <li>서버가 하루 몇 번 가격을 확인하고, 조건이 맞으면 알림을 보낸다</li>
          <li>샀으면 '샀어요'를 눌러 바로 냉장고로 옮긴다</li>
        </ol>
        <div class="callout">데모에서는 실제 가격을 불러오지 않고, 쇼핑몰별 '낮은 가격순' 검색 결과로 바로 연결합니다. 가격 확인과 알림은 서버 연동 단계에서 붙입니다.</div>
      </div>
    </div>
  </section>

  <!-- 내 식재료 -->''')

# =====================================================================
# 2) 스타일
# =====================================================================
rep('''@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}''', '''/* ---------- v6 ---------- */
/* 레시피 재료 분량: 글자 단위로 쪼개지던 줄바꿈 수정 */
.ing .amt{overflow-wrap:normal;word-break:keep-all;max-width:12em}
/* 초성 자동완성 */
.ac{position:fixed;z-index:80;list-style:none;margin:0;padding:6px;max-height:264px;overflow:auto;background:var(--bg);border:1px solid var(--card-line);border-radius:12px;box-shadow:0 12px 32px rgba(30,18,12,.22)}
.ac li{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:14px}
.ac li:hover,.ac li[aria-selected="true"]{background:var(--field)}
.ac mark{background:none;color:var(--accent-strong)}
/* 재료 칩 → 수정 */
.chip-edit{background:none;border:0;padding:0;display:inline-flex;align-items:center;gap:6px;color:inherit;font:inherit;cursor:pointer}
.chip-edit:hover{text-decoration:underline;text-underline-offset:3px}
.urgent-list .chip-edit{gap:4px}
.quick{display:flex;flex-wrap:wrap;gap:6px}
.quick button{border:1px solid var(--card-line);background:var(--card);border-radius:999px;padding:5px 11px;font-size:13px}
.quick button:hover{background:var(--field)}
.ed-grid{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px 12px;align-items:center;margin-top:14px}
.ed-grid .field{border-radius:12px}
.ed-qty{display:flex;align-items:center;gap:8px}
.ed-qty .field{width:120px}
.item-search{max-width:220px}
td .name-edit{background:none;border:0;padding:0;color:inherit;font:inherit;text-decoration:underline;text-decoration-color:var(--card-line);text-underline-offset:4px}
/* 등록 방법 전환 · 영수증 */
.scan-mode{margin-top:10px}
.rc-paste{margin-top:12px}
.rc-paste summary,.rc-raw summary{cursor:pointer;color:var(--muted);font-size:14px}
.rc-text{font:inherit;color:inherit;border-radius:12px;margin-top:8px;resize:vertical;min-height:110px;line-height:1.5}
.rc-raw pre{white-space:pre-wrap;font:inherit;font-size:12px;color:var(--muted);background:var(--field);border-radius:10px;padding:10px;max-height:180px;overflow:auto}
.scan-list .src{grid-column:2 / -1;font-size:12px;line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
/* 레시피 영상 */
.video{aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:var(--field);margin-bottom:10px}
.video iframe{width:100%;height:100%;border:0;display:block}
.video-links{display:flex;flex-wrap:wrap;gap:8px}
.vlink{display:inline-flex;align-items:center;gap:8px;padding:9px 14px;border-radius:10px;text-decoration:none;color:var(--ink);box-shadow:inset 0 0 0 1px var(--card-line);font-size:14px}
.vlink:hover{background:var(--field)}
.vlink .yt{width:22px;height:16px;border-radius:4px;background:#E62117;display:grid;place-items:center}
.vlink .yt::after{content:"";border-left:6px solid #fff;border-top:4px solid transparent;border-bottom:4px solid transparent;margin-left:1px}
.cart-row{margin-top:10px}
/* 장보기 */
.cart-list{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:10px}
.cart-list li{background:var(--tint-surface);border-radius:14px;padding:12px 14px;display:grid;gap:10px}
.cart-top{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}
.cart-top b{font-weight:400;font-size:17px}
.cart-shops{display:flex;flex-wrap:wrap;gap:6px}
.shop{display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:999px;background:var(--card);border:1px solid var(--card-line);color:var(--ink);text-decoration:none;font-size:13px}
.shop i{width:8px;height:8px;border-radius:50%;display:inline-block}
.shop:hover{background:var(--field)}
.cart-bottom{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px}
.cart-bottom label{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
.cart-bottom input[type=number]{width:96px;background:var(--bg);border:0;border-radius:8px;padding:6px 8px;font-variant-numeric:tabular-nums}
.cart-top .x{margin-left:auto;background:none;border:0;color:var(--muted);font-size:18px;width:28px;height:28px;border-radius:8px}
.cart-top .x:hover{background:var(--bg);color:var(--danger)}
.cart-how{margin:14px 0;font-size:14px}
.cart-add .date{width:170px}
@container app (max-width:640px){
  .item-search{max-width:none;width:100%;order:3}
  .cart-add .date{width:100%}
  .ed-grid{grid-template-columns:minmax(0,1fr)}
}

@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}''')

# =====================================================================
# 3) 기존 화면 코드 수정
# =====================================================================
# 재료 칩을 누르면 수정 창
rep('''  return items.map(f => `<span class="chip">${esc(f.name)} ${ddayTag(f.exp)}${removable?''',
    '''  return items.map(f => `<span class="chip"><button class="chip-edit" type="button" data-edit="${f.id}" title="소비기한·수량 고치기">${esc(f.name)} ${ddayTag(f.exp)}</button>${removable?''')
# 임박 목록도 누르면 수정
rep('''  $("#urgentList").innerHTML = urg.length ? urg.map(f => `<li><span>${esc(f.name)} <span class="note">''',
    '''  $("#urgentList").innerHTML = urg.length ? urg.map(f => `<li><span><button class="chip-edit" type="button" data-edit="${f.id}">${esc(f.name)}</button> <span class="note">''')

# 레시피 검색: 초성 + 부분 일치
rep('''  const all = ranked().filter(m => !q || m.r.name.includes(q) || m.r.ings.some(i => i[0].includes(q) || (i[3] || "").includes(q)));''',
    '''  // v6: 초성(ㄱㅊㅉㄱ)이나 섞어 쓰기(김ㅊ)도 찾는다
  const all = ranked().filter(m => !q || koHas(m.r.name, q) || m.r.ings.some(i => koHas(i[0], q) || koHas(i[3] || "", q)));''')

# 내 식재료 표: 검색 · 이름 눌러 수정 · 자동 표시 설명
rep('''function renderItems(){
  const list = sortedFridge();''', '''let itemQuery = "";
function renderItems(){
  const list = sortedFridge().filter(f => !itemQuery.trim() || koHas(f.name, itemQuery.trim()));''')
rep('''      <td>${esc(f.name)}</td>
      <td class="sub">${MASTER[f.name] ? MASTER[f.name][0] : "기타"}</td>''', '''      <td><button class="name-edit" type="button" data-edit="${f.id}">${esc(f.name)}</button></td>
      <td class="sub">${MASTER[f.name] ? MASTER[f.name][0] : "기타"}</td>''')
rep('''${f.auto ? `<span class="tag t-soft">자동</span>` : ""}</td>''',
    '''${f.auto ? `<span class="tag t-soft" title="보관 기간으로 계산한 참고용 날짜">자동</span>` : `<span class="tag t-ok">직접</span>`}</td>''')
rep('''    </tr>`).join("") : `<tr><td colspan="7" class="empty">등록된 식재료가 없습니다.</td></tr>`;''',
    '''    </tr>`).join("") : `<tr><td colspan="7" class="empty">${itemQuery.trim() ? "찾는 재료가 없습니다." : "등록된 식재료가 없습니다."}</td></tr>`;''')

# 레시피 상세: 부족 재료 장보기 + 영상
rep('''      <div class="sec"><h2>조리 순서</h2><ol class="how">${r.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol></div>''',
    '''      ${m.missing.length ? `<div class="cart-row"><button class="btn ghost" type="button" id="toCart">부족한 재료 ${m.missing.length}개 장보기 목록에 담기</button></div>` : ""}
      <div class="sec"><h2>조리 순서</h2><ol class="how">${r.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol></div>
      ${videoHTML(r)}''')
rep('''  $("#doneBtn").onclick = () => openDeduct(r);''', '''  $("#doneBtn").onclick = () => openDeduct(r);
  const tc = $("#toCart"); if (tc) tc.onclick = () => cartAdd(m.missing.map(i => i[0]), r.name);''')

rep('''function renderAll(){ renderHome(); renderFridge(); renderRecipes(); renderDetail(); renderItems(); }''',
    '''function renderAll(){ renderHome(); renderFridge(); renderRecipes(); renderDetail(); renderItems(); renderCart(); }''')

# 이동: 모바일 탭바에서 식재료 화면은 냉장고 탭을 켠다
rep('''  document.querySelectorAll(`.nav [data-go="${nav}"], .tabbar [data-go="${nav}"]`).forEach(c => c.setAttribute("aria-current","page"));''',
    '''  document.querySelectorAll(`.nav [data-go="${nav}"], .tabbar [data-go="${nav}"]`).forEach(c => c.setAttribute("aria-current","page"));
  if (page === "items") document.querySelectorAll('.tabbar [data-go="fridge"]').forEach(c => c.setAttribute("aria-current","page"));
  acClose();''')
rep('''go(["home","fridge","recipes","items"].includes(start) ? start : "home");''',
    '''go(["home","fridge","recipes","items","cart"].includes(start) ? start : "home");''')

# 스캔 창: 사진 ↔ 영수증 전환
rep('''  modal(`<h2>재료 사진 스캔</h2>
    <div class="sub">냉장고나 장바구니''', '''  modal(`<h2>재료 사진 스캔</h2>
    <div class="seg scan-mode" role="group" aria-label="등록 방법"><button type="button" aria-pressed="true">재료 사진</button><button type="button" id="toReceipt" aria-pressed="false">영수증·주문내역</button></div>
    <div class="sub" style="margin-top:10px">냉장고나 장바구니''')
rep('''  // 사진을 고르기 전에 모델을 미리 준비한다''', '''  $("#toReceipt").onclick = openReceipt;
  // 사진을 고르기 전에 모델을 미리 준비한다''')

# 스캔 목록 줄: 영수증에서 읽은 원문을 함께 보여줄 수 있게
rep('''function scanRow({ name = "", qty, checked = true, color = "var(--muted)", tag = "" }){''',
    '''function scanRow({ name = "", qty, checked = true, color = "var(--muted)", tag = "", src = "" }){''')
rep('''    <span class="tagcell">${tag}<button class="row-x" type="button" aria-label="이 줄 지우기">×</button></span>
  </li>`;''', '''    <span class="tagcell">${tag}<button class="row-x" type="button" aria-label="이 줄 지우기">×</button></span>
    ${src ? `<span class="src note" title="${esc(src)}">읽은 글자: ${esc(src)}</span>` : ""}
  </li>`;''')

# =====================================================================
# 4) v6 기능 코드
# =====================================================================
V6_JS = r'''
/* =====================================================================
 * v6-1) 초성 검색 — "ㅇㅍ" → 양파, "김ㅊ" → 김치찌개
 * ===================================================================== */
const CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ";
const choOf = ch => { const c = ch.charCodeAt(0) - 0xAC00; return c >= 0 && c < 11172 ? CHO[Math.floor(c / 588)] : ch; };
// 한 글자 비교: 질의 글자가 자음(ㄱ~ㅎ)이면 초성끼리, 아니면 그대로
const chEq = (t, q) => t === q || (CHO.includes(q) && choOf(t) === q);
/** text 안에서 q가 시작하는 위치(공백 무시). 없으면 -1 */
function koIndex(text, q){
  const t = String(text).replace(/\s+/g, ""), k = String(q).replace(/\s+/g, "");
  if (!k) return 0;
  outer: for (let i = 0; i + k.length <= t.length; i++){
    for (let j = 0; j < k.length; j++) if (!chEq(t[i + j], k[j])) continue outer;
    return i;
  }
  return -1;
}
const koHas = (text, q) => koIndex(text, q) >= 0;

/* 재료 입력칸 자동완성 (data-ac가 붙은 입력칸 전부: 홈·냉장고·스캔 결과·장보기) */
const AC_NAMES = [...new Set([...Object.keys(MASTER), ...RECIPES.flatMap(r => r.ings.map(i => i[0]))])];
let acBox = null, acInput = null, acIdx = -1;
function acClose(){ if (acBox) acBox.hidden = true; acInput = null; acIdx = -1; }
function acOpen(inp){
  const q = inp.value.trim();
  if (!q){ acClose(); return; }
  // 초성만 쳤을 때는 레시피 재료명(굵은파, 삶은팥…)이 너무 많이 걸리므로 앞에서부터 맞는 것만
  const onlyCho = [...q.replace(/\s+/g, "")].every(c => CHO.includes(c));
  const hits = AC_NAMES.map(n => ({ n, i: koIndex(n, q) })).filter(h => h.i >= 0 && (!onlyCho || h.i === 0 || MASTER[h.n]))
    .sort((a, b) => a.i - b.i || (!MASTER[a.n]) - (!MASTER[b.n]) || a.n.length - b.n.length || a.n.localeCompare(b.n, "ko")).slice(0, 8);
  if (!hits.length || (hits.length === 1 && hits[0].n === q)){ acClose(); return; }
  if (!acBox){
    acBox = document.createElement("ul"); acBox.className = "ac"; acBox.setAttribute("role", "listbox"); acBox.hidden = true;
    document.body.appendChild(acBox);
    acBox.addEventListener("pointerdown", e => { const li = e.target.closest("li[data-v]"); if (li){ e.preventDefault(); acPick(li.dataset.v); } });
  }
  acInput = inp; acIdx = -1;
  acBox.innerHTML = hits.map(h => {
    const k = q.replace(/\s+/g, "").length, n = h.n;
    const name = h.i >= 0 && !/\s/.test(n) ? `${esc(n.slice(0, h.i))}<mark>${esc(n.slice(h.i, h.i + k))}</mark>${esc(n.slice(h.i + k))}` : esc(n);
    return `<li role="option" data-v="${esc(n)}"><span>${name}</span>${MASTER[n] ? `<span class="note">${MASTER[n][0]} · ${MASTER[n][2]}</span>` : ""}</li>`;
  }).join("");
  acBox.hidden = false;
  const r = inp.getBoundingClientRect(), h = acBox.offsetHeight;
  const below = r.bottom + 4 + h <= window.innerHeight || r.top < h + 8;
  Object.assign(acBox.style, { left: Math.max(8, Math.min(r.left, window.innerWidth - Math.max(r.width, 200) - 8)) + "px",
    top: (below ? r.bottom + 4 : r.top - 4 - h) + "px", width: Math.max(r.width, 200) + "px" });
}
function acPick(v){
  const inp = acInput; if (!inp) return;
  inp.value = v; acClose(); inp.focus();
  inp.dispatchEvent(new Event("change", { bubbles: true }));
}
document.addEventListener("input", e => { if (e.target.matches && e.target.matches("input[data-ac]")) acOpen(e.target); });
document.addEventListener("keydown", e => {
  if (!acBox || acBox.hidden || e.target !== acInput) return;
  const items = [...acBox.children];
  if (e.key === "ArrowDown" || e.key === "ArrowUp"){
    e.preventDefault();
    acIdx = (acIdx + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
    items.forEach((li, i) => li.setAttribute("aria-selected", i === acIdx));
    items[acIdx].scrollIntoView({ block: "nearest" });
  } else if (e.key === "Enter" && acIdx >= 0){ e.preventDefault(); e.stopPropagation(); acPick(items[acIdx].dataset.v); }
  else if (e.key === "Escape"){ e.stopPropagation(); acClose(); }
}, true);
document.addEventListener("focusout", e => { if (e.target === acInput) setTimeout(() => { if (document.activeElement !== acInput) acClose(); }, 120); });
window.addEventListener("resize", acClose);
document.addEventListener("scroll", e => { if (acBox && !acBox.hidden && !acBox.contains(e.target)) acClose(); }, true);

/* =====================================================================
 * v6-2) 소비기한·수량 수정 창 — 재료 칩, 임박 목록, 식재료 표 이름을 누르면 열린다
 * ===================================================================== */
function openEdit(id){
  const f = fridge.find(x => x.id === id); if (!f) return;
  const m = MASTER[f.name];
  const autoExp = m ? iso(parse(f.reg).getTime() + m[1] * DAY) : null;
  modal(`<h2>${esc(f.name)}</h2>
    <div class="sub">${f.auto && m ? `등록일(${md(f.reg)})에 냉장 보관 ${m[1]}일을 더해 자동으로 안내한 날짜입니다. 보관 상태에 따라 다를 수 있으니 참고용으로 보고, 포장에 날짜가 있으면 그 날짜로 고치세요.`
      : f.auto ? `보관 기간 정보가 없어 7일로 잡아 둔 날짜입니다. 실제 날짜로 고치세요.` : `직접 입력한 날짜입니다.`}</div>
    <div class="ed-grid">
      <label class="label" for="edExp">소비기한</label>
      <input class="field" type="date" id="edExp" value="${f.exp}">
      <span></span>
      <div class="quick" id="edQuick">
        <button type="button" data-add="-1">-1일</button><button type="button" data-add="1">+1일</button>
        <button type="button" data-add="3">+3일</button><button type="button" data-add="7">+7일</button>
        <button type="button" data-set="today">오늘</button>
        ${autoExp ? `<button type="button" data-set="auto">자동 안내 날짜(${md(autoExp)})</button>` : ""}
      </div>
      <span></span>
      <div class="note" id="edPreview"></div>
      <label class="label" for="edQty">수량</label>
      <div class="ed-qty"><input class="field" type="number" id="edQty" min="0" step="any" value="${fmtQty(f.qty)}"><span class="sub">${esc(f.unit)}</span></div>
    </div>
    <div class="actions"><button class="btn danger" type="button" id="edDel" style="margin-right:auto">삭제</button><button class="btn ghost" data-close>취소</button><button class="btn strong" id="edOk">저장</button></div>`);
  const inp = $("#edExp");
  const preview = () => { $("#edPreview").innerHTML = inp.value ? `${ddayTag(inp.value)} ${inp.value === autoExp ? "· 자동 안내 날짜" : "· 직접 고친 날짜"}` : ""; };
  preview(); inp.addEventListener("input", preview);
  $("#edQuick").onclick = e => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.dataset.add) inp.value = addDays(+b.dataset.add, inp.value ? parse(inp.value) : today0());
    if (b.dataset.set === "today") inp.value = iso(today0());
    if (b.dataset.set === "auto") inp.value = autoExp;
    preview();
  };
  $("#edDel").onclick = () => { fridge = fridge.filter(x => x.id !== id); save(); closeModal(); renderAll(); toast(`${josa(f.name, "을", "를")} 냉장고에서 뺐습니다.`); };
  $("#edOk").onclick = () => {
    if (!inp.value){ toast("소비기한 날짜를 고르세요."); return; }
    const before = f.exp;
    f.exp = inp.value; f.auto = !!autoExp && inp.value === autoExp;
    f.qty = Math.max(0, parseFloat($("#edQty").value) || 0);
    fridge = fridge.filter(x => x.qty > 0); save(); closeModal(); renderAll();
    toast(before === f.exp ? `${f.name} 수량을 고쳤습니다.` : `${f.name} 소비기한을 ${md(f.exp)}로 고쳤습니다.`);
  };
}

/* =====================================================================
 * v6-3) 영수증·주문내역 → 재료
 *   사진: tesseract.js(한국어)로 기기 안에서 글자를 읽는다 (서버·비용 없음)
 *   글자: 쿠팡·마켓컬리·네이버 주문내역을 복사해 붙여넣는다
 * ===================================================================== */
// [상품명에 나오는 표기, 표준 재료] — 긴 표기부터 찾는다
const RC_ALIAS = [
  ["달걀","계란"],["특란","계란"],["대란","계란"],["왕란","계란"],["구운란","계란"],
  ["삼겹","돼지고기"],["목살","돼지고기"],["앞다리","돼지고기"],["뒷다리","돼지고기"],["돈육","돼지고기"],["항정","돼지고기"],["대패","돼지고기"],["돼지","돼지고기"],
  ["한우","소고기"],["우육","소고기"],["등심","소고기"],["양지","소고기"],["차돌","소고기"],["우삼겹","소고기"],["사태","소고기"],
  ["닭가슴살","닭고기"],["닭다리","닭고기"],["닭안심","닭고기"],["닭볶음탕용","닭고기"],["생닭","닭고기"],["닭","닭고기"],
  ["방울토마토","토마토"],["대추방울","토마토"],["새송이","버섯"],["팽이","버섯"],["표고","버섯"],["느타리","버섯"],["양송이","버섯"],
  ["청양고추","고추"],["풋고추","고추"],["꽈리고추","고추"],["오이고추","고추"],["깐마늘","마늘"],["다진마늘","마늘"],["통마늘","마늘"],
  ["감귤","귤"],["한라봉","귤"],["샤인머스캣","포도"],["캠벨","포도"],["거봉","포도"],
  ["슬라이스치즈","치즈"],["체다","치즈"],["모짜렐라","치즈"],["참치","참치캔"],["오뎅","어묵"],
  ["떡볶이떡","떡"],["가래떡","떡"],["떡국떡","떡"],["즉석밥","밥"],["햇반","밥"],
  ["알배기","배추"],["알배추","배추"],["절임배추","배추"],["배추김치","김치"],["포기김치","김치"],["열무김치","김치"],["총각김치","김치"],["깍두기","김치"],
  ["흰우유","우유"],["저지방우유","우유"],["주키니","애호박"],["피망","파프리카"],["로메인","상추"],
  ["새우살","새우"],["칵테일새우","새우"],["흰다리","새우"],["무우","무"],["슬라이스햄","햄"]
];
const RC_DICT = [...RC_ALIAS, ...Object.keys(MASTER).map(k => [k, k])].sort((a, b) => b[0].length - a[0].length);
// 이런 줄은 상품이 아니다
const RC_SKIP_LINE = /배송|결제|합계|총액|소계|할인|쿠폰|포인트|적립|카드|부가세|과세|면세|주문번호|영수증|사업자|대표자|전화|주소|승인|거스름|받을|금액|반품|교환|문의/;
// 가공품(양파링, 마늘가루, 사과주스 …)은 재료로 보지 않는다
const RC_SKIP_WORD = /칩|링|스낵|과자|라면|주스|음료|소스|드레싱|시럽|분말|가루|향|맛우유|젤리|사탕|아이스/;
// '개' 단위 재료를 무게로 샀을 때 1개 무게(g) — 1.5kg 양파 → 약 8개
const EACH_G = { 양파:200, 감자:150, 고구마:200, 당근:200, 사과:250, 배:600, 토마토:150, 오이:200, 애호박:300, 파프리카:150,
  레몬:120, 오렌지:200, 귤:80, 키위:90, 복숭아:250, 가지:150, 바나나:120, 옥수수:300, 무:1200, 단호박:1000 };
const isHangul = c => !!c && /[가-힣]/.test(c);
// 받침에 따라 을/를, 이/가 고르기
const josa = (w, a, b) => { const c = String(w).slice(-1).charCodeAt(0) - 0xAC00; return w + (c >= 0 && c < 11172 && c % 28 ? a : b); };

function rcQty(line, canon){
  const m = MASTER[canon], unit = m ? m[2] : "개", def = m ? m[3] : 1;
  const L = line.replace(/(\d),(\d{3})/g, "$1$2");
  const w = L.match(/(\d+(?:\.\d+)?)\s*(kg|㎏|g|그램|ml|㎖|ℓ|l|리터)(?![a-z])/i);
  const c = L.match(/(\d+)\s*(구|개입|입|개|팩|봉|단|마리|송이|포기|모|캔|통|장|줄|알)/);
  const x = L.match(/[x×*]\s*(\d+)(?!\s*(?:g|kg|ml|㎏))/i);
  const packs = x ? +x[1] : 1;
  let grams = null;
  if (w){ const u = w[2].toLowerCase(); grams = +w[1] * (/^(kg|㎏|ℓ|l|리터)$/.test(u) ? 1000 : 1); }
  // 영수증 글자 인식에서 g가 8로 읽히는 경우(500g → 5008)
  else if (unit === "g"){ const o = L.match(/(\d{2,4}0)8(?!\d)/); if (o) grams = +o[1]; }
  if (unit === "g" || unit === "ml") return (grams ?? def) * (c && grams && /팩|봉|개|입/.test(c[2]) && !x ? +c[1] : packs);
  if (c && /구|입|개입/.test(c[2])) return +c[1] * packs;                     // 계란 30구, 귤 10입
  if (grams && EACH_G[canon]) return Math.max(1, Math.round(grams / EACH_G[canon])) * (c ? +c[1] : packs);
  if (c) return +c[1] * packs;
  return def * packs;
}

/** 글자 → [{ name, qty, src }] */
function parseReceipt(text){
  const out = new Map();
  text.split(/\r?\n/).map(l => l.replace(/\s+/g, " ").trim()).filter(l => l.length >= 2).forEach(line => {
    if (RC_SKIP_LINE.test(line)) return;
    const flat = line.replace(/\s+/g, "");
    if (RC_SKIP_WORD.test(flat)) return;
    const taken = new Array(flat.length).fill(false), found = [];
    for (const [tok, canon] of RC_DICT){
      let from = 0, i;
      while ((i = flat.indexOf(tok, from)) >= 0){
        from = i + 1;
        if (taken.slice(i, i + tok.length).some(Boolean)) continue;
        // 한 글자 재료(무, 배, 밤, 굴, 떡 …)는 앞뒤가 한글이 아닐 때만: '배송', '무농약' 제외
        if (tok.length === 1 && (isHangul(flat[i - 1]) || isHangul(flat[i + 1]))) continue;
        for (let k = i; k < i + tok.length; k++) taken[k] = true;
        if (!found.includes(canon)) found.push(canon);
      }
    }
    // 한 줄에 재료가 여럿이면(예: '양파 감자 세트') 각각 기본 수량
    found.forEach(canon => {
      const qty = found.length === 1 ? rcQty(line, canon) : (MASTER[canon] ? MASTER[canon][3] : 1);
      const g = out.get(canon);
      if (g){ g.qty += qty; g.src += " / " + line; } else out.set(canon, { name: canon, qty, src: line });
    });
  });
  return [...out.values()];
}

let ocrWorker = null, ocrStatus = () => {};
async function ensureOcr(){
  if (ocrWorker) return ocrWorker;
  ocrStatus("글자 인식기를 준비하는 중… 처음 한 번만 몇 MB를 내려받습니다");
  if (!window.Tesseract) await loadScript("https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js").catch(() => { throw new Error("글자 인식기(tesseract.js)를 불러오지 못했습니다"); });
  ocrWorker = await Tesseract.createWorker(["kor", "eng"], 1, {
    logger: m => { if (m.status === "recognizing text") ocrStatus(`글자 읽는 중… ${Math.round(m.progress * 100)}%`); }
  });
  return ocrWorker;
}
// 사진 방향(EXIF)을 바로잡고 너무 크면 줄인다. 작은 캡처는 키워서 글자를 또렷하게
async function ocrCanvas(file){
  const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
  const long = Math.max(bmp.width, bmp.height), s = long > 2400 ? 2400 / long : long < 1000 ? 1.6 : 1;
  const cv = document.createElement("canvas"); cv.width = Math.round(bmp.width * s); cv.height = Math.round(bmp.height * s);
  const ctx = cv.getContext("2d"); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.filter = "grayscale(1) contrast(1.25)"; ctx.drawImage(bmp, 0, 0, cv.width, cv.height);
  return cv;
}

function showReceiptRows(items, raw){
  scanRowSeq = 0;
  const rows = items.map(it => scanRow({ name: it.name, qty: it.qty, checked: true, color: MASTER[it.name] ? MASTER[it.name][4] : "var(--muted)",
    tag: `<span class="tag t-ok">찾음</span>`, src: it.src }));
  $("#scanResult").innerHTML = `
    ${items.length ? "" : `<div class="empty" style="margin-top:12px">재료 이름을 찾지 못했습니다. 아래 '읽은 글자 전체 보기'를 확인하고 직접 추가하세요.</div>`}
    <div class="label" style="margin-top:12px">등록할 재료 · 수량은 상품 표기(1.5kg, 30구 등)로 계산했습니다</div>
    <ul class="scan-list" id="scanList">${rows.join("")}</ul>
    <div class="scan-add">
      <button class="btn ghost" type="button" id="scanAddRow">+ 빠진 재료 직접 추가</button>
    </div>`;
  if (raw != null){ $("#rcRaw").hidden = false; $("#rcRawText").textContent = raw.trim() || "(읽은 글자가 없습니다)"; }
  $("#scanOk").disabled = false;
}

function registerRows(){
  const picked = [...document.querySelectorAll(".scan-list li[data-row]")].filter(li => li.querySelector("input[type=checkbox]").checked)
    .map(li => ({ name: li.querySelector("input[type=text]").value.trim(), qty: parseFloat(li.querySelector("input[type=number]").value) || undefined }))
    .filter(p => p.name);
  if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
  const merged = new Map();
  picked.forEach(p => { const g = merged.get(p.name); g ? (g.qty = (g.qty || 0) + (p.qty || 0) || undefined) : merged.set(p.name, { ...p }); });
  merged.forEach(p => addItem(p.name, "", p.qty));
  const names = [...merged.keys()];
  const fromCart = cartBought(names);
  showScanRecipes(names);
  if (fromCart.length) toast(`장보기 목록에 있던 ${josa(fromCart.join(", "), "을", "를")} 산 것으로 처리했습니다.`);
}

function openReceipt(){
  scanRowSeq = 0;
  modal(`<h2>영수증·주문내역으로 등록</h2>
    <div class="seg scan-mode" role="group" aria-label="등록 방법"><button type="button" id="toPhoto" aria-pressed="false">재료 사진</button><button type="button" aria-pressed="true">영수증·주문내역</button></div>
    <div class="sub" style="margin-top:10px">마트 영수증 사진이나 쿠팡·마켓컬리·네이버쇼핑 주문내역 캡처를 올리세요. 글자는 이 기기 안에서 읽고 어디에도 보내지 않습니다.</div>
    <label class="drop" for="rcFile" id="rcDrop">영수증·주문내역 사진 고르기</label>
    <input type="file" id="rcFile" accept="image/*" hidden>
    <details class="rc-paste" id="rcPaste"><summary>주문내역 글자를 복사해서 붙여넣기 (더 정확)</summary>
      <textarea class="field rc-text" id="rcText" rows="5" placeholder="주문내역 화면에서 상품 목록을 길게 눌러 복사한 뒤 붙여넣으세요.&#10;예) 국내산 양파 1.5kg 1개  4,980원&#10;    무항생제 특란 30구  8,990원"></textarea>
      <div class="row" style="justify-content:flex-end;margin-top:8px"><button class="btn" type="button" id="rcParse">글자에서 재료 찾기</button></div>
    </details>
    <div class="scan-status" id="scanStatus"></div>
    <div id="scanResult"></div>
    <details class="rc-raw" id="rcRaw" hidden><summary>읽은 글자 전체 보기</summary><pre id="rcRawText"></pre></details>
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="scanOk" disabled>선택한 재료 등록</button></div>`);
  const status = (t, err) => { const el = $("#scanStatus"); if (!el) return; el.textContent = t; el.className = "scan-status" + (err ? " err" : ""); };
  ocrStatus = status;
  $("#toPhoto").onclick = openScan;
  bindScanList();
  $("#scanOk").onclick = registerRows;
  $("#rcParse").onclick = () => {
    const t = $("#rcText").value;
    if (!t.trim()){ status("붙여넣은 글자가 없습니다.", true); return; }
    const items = parseReceipt(t);
    status(`${items.length}가지 재료를 찾았습니다 · 이름과 수량을 확인하세요`);
    showReceiptRows(items, null);
  };
  $("#rcFile").onchange = async e => {
    const file = e.target.files[0]; if (!file) return;
    $("#rcDrop").textContent = "다른 사진으로 바꾸려면 누르세요";
    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true; $("#rcRaw").hidden = true;
    try {
      const w = await ensureOcr();
      status("글자 읽는 중…");
      const t0 = performance.now();
      const { data } = await w.recognize(await ocrCanvas(file));
      const items = parseReceipt(data.text);
      status(`${items.length}가지 재료를 찾았습니다 · ${((performance.now() - t0) / 1000).toFixed(1)}초 · 영수증 글자는 틀릴 수 있으니 확인하세요`);
      showReceiptRows(items, data.text);
    } catch (err) {
      status("글자를 읽지 못했습니다: " + (err.message || err) + " · 주문내역 글자를 붙여넣어 보세요", true);
      $("#rcPaste").open = true;
    }
  };
}

/* =====================================================================
 * v6-4) 레시피 영상 — 대표 영상(r.video)이 있으면 바로 재생, 없으면 검색으로 연결
 *   서비스: YouTube Data API로 레시피마다 대표 영상 ID를 한 번만 찾아 DB에 저장(하루 검색 한도 안에서 나눠서)
 * ===================================================================== */
function videoHTML(r){
  const q = encodeURIComponent(r.name + " 만들기");
  return `<div class="sec"><h2>영상으로 보기</h2>
    ${r.video ? `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(r.video)}" title="${esc(r.name)} 조리 영상" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>` : ""}
    <div class="video-links">
      <a class="vlink" href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener"><span class="yt" aria-hidden="true"></span>유튜브에서 '${esc(r.name)}' 영상 보기</a>
      <a class="vlink" href="https://www.10000recipe.com/recipe/list.html?q=${encodeURIComponent(r.name)}" target="_blank" rel="noopener">만개의레시피 사진 레시피</a>
    </div>
    <div class="note" style="margin-top:8px">새 창으로 열립니다.</div></div>`;
}

/* =====================================================================
 * v6-5) 장보기 목록 · 최저가 안내
 * ===================================================================== */
const CART_KEY = "yorijori-demo-cart-v1";
let cart = (() => { try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); } catch(e){ return []; } })();
const saveCart = () => { try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch(e){} };
const SHOPS = [
  { name: "쿠팡", dot: "#E52528", url: q => `https://www.coupang.com/np/search?q=${q}&sorter=salePriceAsc`, label: "쿠팡 낮은가격순" },
  { name: "네이버", dot: "#03C75A", url: q => `https://search.shopping.naver.com/search/all?query=${q}&sort=price_asc`, label: "네이버쇼핑 낮은가격순" },
  { name: "컬리", dot: "#5F0080", url: q => `https://www.kurly.com/search?sword=${q}`, label: "마켓컬리" }
];
function cartAdd(names, from, target){
  const added = [];
  names.forEach(n => {
    const name = n.trim(); if (!name) return;
    let it = cart.find(c => c.name === name);
    if (!it){ it = { id: uid(), name, from: [], target: target || null, watch: true, added: iso(today0()) }; cart.push(it); added.push(name); }
    if (from && !it.from.includes(from)) it.from.push(from);
    if (target) it.target = target;
  });
  saveCart(); renderCart();
  toast(added.length ? `장보기 목록에 ${josa(added.join(", "), "을", "를")} 담았습니다.` : "이미 장보기 목록에 있습니다.");
  return added;
}
/** 냉장고에 넣은 재료 중 장보기 목록에 있던 것을 빼고, 뺀 이름을 돌려준다 */
function cartBought(names){
  const hit = cart.filter(c => names.includes(c.name)).map(c => c.name);
  if (hit.length){ cart = cart.filter(c => !names.includes(c.name)); saveCart(); renderCart(); }
  return hit;
}
function renderCart(){
  const el = $("#cartList"); if (!el) return;
  el.innerHTML = cart.length ? cart.map(c => {
    const q = encodeURIComponent(c.name), have = stockQty(c.name), unit = MASTER[c.name] ? MASTER[c.name][2] : "";
    return `<li>
      <div class="cart-top"><b>${esc(c.name)}</b>
        <span class="note">${c.from.length ? esc(c.from.join(", ")) + "에 필요" : "직접 담음"}</span>
        ${have > 0 ? `<span class="tag t-ok">냉장고에 ${fmtQty(have)}${esc(unit)} 있음</span>` : ""}
        <button class="x" type="button" data-cartdel="${c.id}" aria-label="${esc(c.name)} 빼기">×</button></div>
      <div class="cart-shops">${SHOPS.map(sh => `<a class="shop" href="${sh.url(q)}" target="_blank" rel="noopener"><i style="background:${sh.dot}"></i>${sh.label}</a>`).join("")}</div>
      <div class="cart-bottom">
        <label>목표가 <input type="number" min="0" step="100" inputmode="numeric" data-target="${c.id}" value="${c.target ?? ""}" placeholder="없음" aria-label="${esc(c.name)} 목표가">원</label>
        <label><input type="checkbox" data-watch="${c.id}" ${c.watch ? "checked" : ""}> 최저가 알림 받기</label>
        <button class="btn" type="button" data-bought="${c.id}">샀어요 → 냉장고</button>
      </div>
    </li>`;
  }).join("") : `<li class="empty" style="background:transparent">담은 재료가 없습니다. 위에서 담거나, 레시피 화면에서 부족한 재료를 담아 보세요.</li>`;
}
'''
rep('''/* 로그인(데모) */''', V6_JS + '''
/* 로그인(데모) */''')

# =====================================================================
# 5) 이벤트
# =====================================================================
rep('''$("#loginBtn").onclick = openLogin;''', '''$("#loginBtn").onclick = openLogin;

/* ---------- v6 이벤트 ---------- */
document.addEventListener("click", e => {
  const ed = e.target.closest("[data-edit]"); if (ed){ e.stopPropagation(); openEdit(ed.dataset.edit); }
}, true);
$("#fridgeScan").onclick = openScan;
$("#fridgeReceipt").onclick = openReceipt;
$("#itemSearch").addEventListener("input", e => { itemQuery = e.target.value; renderItems(); });
$("#cartForm").onsubmit = e => {
  e.preventDefault();
  const name = $("#cartInput").value.trim(), target = parseInt($("#cartTarget").value, 10) || null;
  if (!name){ $("#cartHint").textContent = "살 재료 이름을 입력하세요."; return; }
  cartAdd([name], null, target); $("#cartHint").textContent = "";
  $("#cartInput").value = ""; $("#cartTarget").value = "";
};
$("#cartList").addEventListener("change", e => {
  const t = e.target.dataset.target, w = e.target.dataset.watch;
  if (t){ const c = cart.find(c => c.id === t); c.target = parseInt(e.target.value, 10) || null; saveCart(); toast(c.target ? `${c.name} 목표가 ${c.target.toLocaleString()}원` : `${c.name} 목표가를 지웠습니다.`); }
  if (w){ const c = cart.find(c => c.id === w); c.watch = e.target.checked; saveCart(); }
});
$("#cartList").addEventListener("click", e => {
  const b = e.target.closest("[data-bought]"), d = e.target.closest("[data-cartdel]");
  if (b){ const c = cart.find(c => c.id === b.dataset.bought); cart = cart.filter(x => x !== c); saveCart(); addItem(c.name); renderCart(); const f = fridge[fridge.length - 1]; toast(`${josa(c.name, "을", "를")} 냉장고에 넣었습니다 · 소비기한 ${md(f.exp)}${f.auto ? " 자동 안내" : ""}`); }
  if (d){ cart = cart.filter(x => x.id !== d.dataset.cartdel); saveCart(); renderCart(); }
});
renderCart();''')

OUT.write_text(s, encoding='utf-8')
print('written', OUT, round(OUT.stat().st_size / 1e6, 1), 'MB')
