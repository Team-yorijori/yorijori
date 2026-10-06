/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 날짜 · 숫자 · 글자 도우미 */

/* ---------- 날짜 유틸 ---------- */
const DAY = 86400000;
const today0 = () => { const d = new Date(); d.setHours(0,0,0,0); return d; };
const iso = d => { const z = new Date(d); return `${z.getFullYear()}-${String(z.getMonth()+1).padStart(2,"0")}-${String(z.getDate()).padStart(2,"0")}`; };
const addDays = (n, base=today0()) => iso(base.getTime() + n*DAY);
const parse = s => { const [y,m,d] = s.split("-").map(Number); return new Date(y, m-1, d); };
const dday = s => Math.round((parse(s) - today0()) / DAY);
const md = s => { const d = parse(s); return `${d.getMonth()+1}/${d.getDate()}`; };
function ddayTag(s){
  const n = dday(s);
  if (n < 0) return `<span class="tag t-danger">${-n}일 지남</span>`;
  if (n === 0) return `<span class="tag t-danger">오늘까지</span>`;
  if (n <= 3) return `<span class="tag t-danger">D-${n}</span>`;
  if (n <= 7) return `<span class="tag t-warn">D-${n}</span>`;
  return `<span class="tag t-ok">D-${n}</span>`;
}
const fmtQty = q => Number.isInteger(q) ? String(q) : String(Math.round(q*100)/100);
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

// 받침에 따라 을/를, 이/가 고르기
const josa = (w, a, b) => { const c = String(w).slice(-1).charCodeAt(0) - 0xAC00; return w + (c >= 0 && c < 11172 && c % 28 ? a : b); };
