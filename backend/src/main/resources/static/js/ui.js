/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 화면 이동 · 토스트 · 모달 */

/* ---------- 이동 ---------- */
function go(page){
  document.querySelectorAll("[data-page]").forEach(s => s.hidden = s.dataset.page !== page);
  document.querySelectorAll(".nav [data-go], .tabbar [data-go]").forEach(b => b.toggleAttribute("aria-current", false));
  const nav = page === "detail" ? "recipes" : page;
  document.querySelectorAll(`.nav [data-go="${nav}"], .tabbar [data-go="${nav}"]`).forEach(c => c.setAttribute("aria-current","page"));
  if (page === "items") document.querySelectorAll('.tabbar [data-go="fridge"]').forEach(c => c.setAttribute("aria-current","page"));
  acClose();
  scroller().scrollTo({top:0});
}

/* ---------- 토스트 · 모달 ---------- */
let tt;
function toast(msg){ const t = $("#toast"); t.textContent = msg; t.hidden = false; clearTimeout(tt); tt = setTimeout(() => t.hidden = true, 2800); }
function modal(html){
  $("#modalRoot").innerHTML = `<div class="scrim" id="scrim"><div class="modal" role="dialog" aria-modal="true">${html}</div></div>`;
  $("#scrim").addEventListener("click", e => { if (e.target.id === "scrim" || e.target.dataset.close != null) closeModal(); });
  const f = $("#modalRoot").querySelector("input,button:not([data-close])"); if (f) f.focus();
}
function closeModal(){ $("#modalRoot").innerHTML = ""; }
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
