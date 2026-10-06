/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 장보기 · 최저가 안내 (v6) */

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
