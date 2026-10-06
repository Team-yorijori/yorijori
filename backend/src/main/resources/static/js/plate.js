/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 접시 그림 (SVG) */

/* ---------- 접시 그림 ---------- */
function plate(r){
  const main = r.ings.filter(i => !i[2]).slice(0,5);
  const n = main.length;
  const dots = main.map((i, k) => {
    const a = (k / n) * Math.PI * 2 - Math.PI/2, rad = n === 1 ? 0 : 26;
    const c = (MASTER[i[0]] || [,,,,"#ddd"])[4];
    return `<circle cx="${80 + Math.cos(a)*rad}" cy="${80 + Math.sin(a)*rad}" r="${n===1?24:17}" fill="${c}" stroke="rgba(0,0,0,.12)"/>`;
  }).join("");
  return `<svg viewBox="0 0 160 160" aria-hidden="true"><ellipse cx="84" cy="88" rx="70" ry="70" fill="rgba(60,30,15,.12)"/><circle cx="80" cy="80" r="72" fill="#FFFDFB"/><circle cx="80" cy="80" r="56" fill="#F6F0EA" stroke="rgba(120,90,70,.14)" stroke-width="1.5"/>${dots}</svg>`;
}
const tint = r => (MASTER[r.ings[0][0]] || [,,,,"#C9A27E"])[4];
