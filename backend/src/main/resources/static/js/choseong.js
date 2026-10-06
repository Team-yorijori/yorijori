/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 초성 검색 · 자동완성 (v6) */

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
