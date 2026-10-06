/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* PC/모바일 미리보기 · 프레임 크기 조절 · 첫 화면 그리기 */

/* PC / 모바일 미리보기 전환 */
const isMobileView = () => document.documentElement.classList.contains("view-mobile");
function scroller(){ return isMobileView() ? $("#app") : window; }
const VIEW_KEY = "yorijori-demo-view";
function setView(mobile, animate){
  const app = $("#app");
  if (animate){ app.classList.remove("morphing"); void app.offsetWidth; app.classList.add("morphing"); setTimeout(() => app.classList.remove("morphing"), 650); }
  document.documentElement.classList.toggle("view-mobile", mobile);
  $("#viewToggle").setAttribute("aria-pressed", mobile);
  $("#viewLabel").textContent = mobile ? "PC로 보기" : "모바일로 보기";
  try { localStorage.setItem(VIEW_KEY, mobile ? "mobile" : "pc"); } catch(e){}
  if (animate){ window.scrollTo({top:0}); $("#app").scrollTo({top:0}); }
}
$("#viewToggle").onclick = () => setView(!document.documentElement.classList.contains("view-mobile"), true);
try { if (localStorage.getItem(VIEW_KEY) === "mobile") setView(true, false); } catch(e){}

/* 미리보기 프레임 크기 조절 */
const SIZE_KEY = "yorijori-demo-frame";
const MIN_W = 320, MIN_H = 480;
const maxW = () => Math.max(MIN_W, Math.min(1280, window.innerWidth - 100));
const maxH = () => Math.max(MIN_H, window.innerHeight - 56);
const kindOf = w => w <= 640 ? "모바일" : w <= 900 ? "태블릿" : "PC";
// 높이 자동: 폰은 세로 비율(19.5:9), 태블릿은 3:4, PC는 16:10
const autoH = w => w <= 640 ? w * 2.16 : w <= 900 ? w * 1.33 : w * 0.625;
let frameW = 390, frameH = 844, hAuto = true;
function applyFrame(persist=true){
  frameW = Math.round(Math.max(MIN_W, Math.min(maxW(), frameW)));
  if (hAuto) frameH = autoH(frameW);
  frameH = Math.round(Math.max(MIN_H, Math.min(maxH(), frameH)));
  const root = document.documentElement.style;
  root.setProperty("--frame-w", frameW + "px"); root.setProperty("--frame-h", frameH + "px");
  $("#sizeVal").textContent = `${frameW} × ${frameH}`;
  $("#sizeKind").textContent = kindOf(frameW) + " 레이아웃" + (hAuto ? " · 높이 자동" : "");
  const r = $("#sizeRange"); r.max = maxW(); r.value = frameW;
  document.querySelectorAll("#sizePresets [data-w]").forEach(b => {
    b.setAttribute("aria-pressed", +b.dataset.w === frameW && (hAuto || Math.min(+b.dataset.h, maxH()) === frameH));
    b.disabled = +b.dataset.w > maxW();
  });
  document.querySelectorAll(".grip").forEach(g => {
    const h = g.dataset.axis === "h";
    g.setAttribute("aria-valuenow", h ? frameH : frameW); g.setAttribute("aria-valuemin", h ? MIN_H : MIN_W); g.setAttribute("aria-valuemax", h ? maxH() : maxW());
  });
  if (persist) { try { localStorage.setItem(SIZE_KEY, JSON.stringify({w:frameW, h:frameH, auto:hAuto})); } catch(e){} }
}
function setFrameW(w, persist=true){ frameW = w; applyFrame(persist); }
function setFrameH(h, persist=true){ hAuto = false; frameH = h; applyFrame(persist); }
document.querySelectorAll(".grip").forEach(g => {
  const vertical = g.dataset.axis === "h";
  g.addEventListener("pointerdown", e => {
    e.preventDefault();
    const side = +g.dataset.side || 1, x0 = e.clientX, y0 = e.clientY, w0 = frameW, h0 = frameH, fr = $("#frame");
    fr.classList.add("resizing"); g.setPointerCapture(e.pointerId);
    // 프레임이 화면 가운데 있으므로 높이는 2배로 반영
    const move = ev => vertical ? setFrameH(h0 + (ev.clientY - y0) * 2, false) : setFrameW(w0 + side * (ev.clientX - x0) * 2, false);
    const up = () => { fr.classList.remove("resizing"); applyFrame(); g.removeEventListener("pointermove", move); g.removeEventListener("pointerup", up); g.removeEventListener("pointercancel", up); };
    g.addEventListener("pointermove", move); g.addEventListener("pointerup", up); g.addEventListener("pointercancel", up);
  });
  g.addEventListener("keydown", e => {
    const step = e.shiftKey ? 50 : 10, side = +g.dataset.side || 1;
    if (vertical){
      if (e.key === "ArrowDown") { e.preventDefault(); setFrameH(frameH + step); }
      if (e.key === "ArrowUp") { e.preventDefault(); setFrameH(frameH - step); }
    } else {
      if (e.key === "ArrowRight") { e.preventDefault(); setFrameW(frameW + step * side); }
      if (e.key === "ArrowLeft") { e.preventDefault(); setFrameW(frameW - step * side); }
    }
  });
});
$(".grip-b").addEventListener("dblclick", () => { hAuto = true; applyFrame(); });
$("#sizeRange").addEventListener("input", e => { $("#frame").classList.add("resizing"); setFrameW(+e.target.value, false); });
$("#sizeRange").addEventListener("change", e => { $("#frame").classList.remove("resizing"); setFrameW(+e.target.value); });
$("#sizePresets").addEventListener("click", e => {
  const b = e.target.closest("[data-w]"); if (!b || b.disabled) return;
  frameW = +b.dataset.w; frameH = +b.dataset.h; hAuto = false; applyFrame();
});
window.addEventListener("resize", () => applyFrame(false));
try {
  const sv = JSON.parse(localStorage.getItem(SIZE_KEY) || "null");
  if (sv && sv.w >= MIN_W){ frameW = sv.w; frameH = sv.h || 844; hAuto = sv.auto !== false; }
} catch(e){}
applyFrame(false);

renderAll();
const start = (location.hash || "").slice(1);
go(["home","fridge","recipes","items","cart","dishes"].includes(start) ? start : "home");
