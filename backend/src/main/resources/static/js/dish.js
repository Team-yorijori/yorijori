/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 만든 요리 보관함 · 먹기/버리기 애니메이션 · 요리 기록 (v8) */

/* =====================================================================
 * v8) 만든 요리 보관함 · 요리 기록
 *   dish = { id, rid, name, serv(만든 인분), left(남은 인분), made, exp, colors[], saved[] }
 *   log  = { t: cook|eat|toss|tossIng, name, rid?, n?, saved?, d }
 * ===================================================================== */
const DISH_KEY = "yorijori-demo-dishes-v1", LOG_KEY = "yorijori-demo-log-v1";
// 조리한 음식 냉장 보관 일수(참고용) — 레시피 분류 기준, 분류가 없으면 이름으로
const DISH_DAYS = { "밥":1, "만두/면류":1, "도시락/간식":1, "음료":1, "샌드위치/햄버거":1, "나물/생채/샐러드":2, "볶음":2, "구이":2, "부침":2,
  "튀김/커틀릿":2, "떡/한과":2, "양식":2, "그라탕/리조또":2, "피자":2, "국":3, "찌개/전골/스튜":3, "찜":3, "빵/과자":3, "밑반찬/김치":4, "조림":4, "양념장":7 };
function dishDays(r){
  if (r.type && DISH_DAYS[r.type]) return DISH_DAYS[r.type];
  const n = r.name || "";
  return /찌개|국|탕|전골/.test(n) ? 3 : /볶음밥|덮밥|스무디|샐러드/.test(n) ? 1 : /조림|장아찌/.test(n) ? 4 : /무침|나물|생채/.test(n) ? 2 : 2;
}
const dishColors = r => { const c = [...new Set(r.ings.map(i => (MASTER[i[0]] || [])[4]).filter(Boolean))].slice(0, 5);
  while (c.length < 3) c.push(["#F3A46C", "#9CCB6B", "#F7C948"][c.length]); return c; };

function seedDishes(){
  const r = RECIPES.find(x => x.name === "된장찌개") || RECIPES[0];
  const made = addDays(-1);
  return { dishes: [{ id: "d0", rid: r.id, name: r.name, serv: 2, left: 2, made, exp: addDays(dishDays(r) - 1), colors: dishColors(r), saved: [] }],
           log: [{ t: "cook", name: r.name, rid: r.id, n: 2, saved: [], d: made }] };
}
let dishes, dishLog;
(() => {
  try { dishes = JSON.parse(localStorage.getItem(DISH_KEY) || "null"); dishLog = JSON.parse(localStorage.getItem(LOG_KEY) || "null"); } catch(e){}
  if (!dishes || !dishLog){ const sd = seedDishes(); dishes = dishes || sd.dishes; dishLog = dishLog || sd.log; }
})();
const saveDishes = () => { try { localStorage.setItem(DISH_KEY, JSON.stringify(dishes)); localStorage.setItem(LOG_KEY, JSON.stringify(dishLog)); } catch(e){} };
function logAdd(e){ dishLog.unshift({ d: iso(today0()), ...e }); if (dishLog.length > 300) dishLog.length = 300; saveDishes(); }
function recentCookDays(rid){
  const c = dishLog.find(l => l.t === "cook" && l.rid === rid);
  return c ? -dday(c.d) : null;
}

function makeDish(r, serv, saved){
  const d = { id: uid(), rid: r.id, name: r.name, serv, left: serv, made: iso(today0()), exp: addDays(dishDays(r)), colors: dishColors(r), saved };
  dishes.unshift(d);
  logAdd({ t: "cook", name: r.name, rid: r.id, n: serv, saved });
  renderAll();
  return d;
}
function eatDish(id, el){
  const d = dishes.find(x => x.id === id); if (!d) return;
  d.left = Math.max(0, d.left - 1);
  logAdd({ t: "eat", name: d.name, rid: d.rid, n: 1 });
  if (d.left <= 0) dishes = dishes.filter(x => x !== d);
  saveDishes();
  const msg = d.left ? `${d.name} 1인분을 먹었습니다 · ${d.left}인분 남음` : `${josa(d.name, "을", "를")} 다 먹었습니다`;
  if (animOn()) playEat(d).then(() => { renderAll(); toast(msg); });
  else { renderAll(); toast(msg); }
}
function tossDish(id, el){
  const d = dishes.find(x => x.id === id); if (!d) return;
  if (animOn() && el) playTrash(el.getBoundingClientRect(), `${d.name} ${d.left}인분`, d.colors[0]);
  dishes = dishes.filter(x => x !== d);
  logAdd({ t: "toss", name: d.name, rid: d.rid, n: d.left });
  saveDishes(); renderAll();
  toast(`${d.name} ${d.left}인분을 버렸습니다.`);
}

function dishPlate(d){
  const n = d.colors.length;
  const dots = d.colors.map((c, k) => { const a = k / n * Math.PI * 2 - Math.PI / 2, rad = n === 1 ? 0 : 26;
    return `<circle cx="${80 + Math.cos(a) * rad}" cy="${80 + Math.sin(a) * rad}" r="17" fill="${c}" stroke="rgba(0,0,0,.12)" opacity="${k < Math.ceil(n * d.left / d.serv) ? 1 : .15}"/>`; }).join("");
  return `<svg viewBox="0 0 160 160" aria-hidden="true"><ellipse cx="84" cy="88" rx="70" ry="70" fill="rgba(60,30,15,.12)"/><circle cx="80" cy="80" r="72" fill="#FFFDFB"/><circle cx="80" cy="80" r="56" fill="#F6F0EA" stroke="rgba(120,90,70,.14)" stroke-width="1.5"/>${dots}</svg>`;
}
function renderDishes(){
  const grid = $("#dishGrid"); if (!grid) return;
  const list = dishes.slice().sort((a, b) => dday(a.exp) - dday(b.exp));
  const servLeft = list.reduce((a, d) => a + d.left, 0);
  $("#dishNote").textContent = list.length ? `${list.length}가지 · ${servLeft}인분 보관 중 · 보관 기한이 가까운 순서 · 기한은 조리 음식 냉장 보관 기준(참고용)` : "";
  grid.innerHTML = list.length ? list.map(d => {
    const n = dday(d.exp);
    return `<div class="dish" data-dish="${d.id}">
      <div class="plate" style="--tint:${d.colors[0]}">${dishPlate(d)}${n <= 0 ? `<span class="badge tag t-danger">${n < 0 ? "기한 지남" : "오늘까지 드세요"}</span>` : n === 1 ? `<span class="badge tag t-danger">내일까지 드세요</span>` : ""}</div>
      <h3><span>${esc(d.name)}</span>${ddayTag(d.exp)}</h3>
      <div class="meta"><span>${d.left}/${d.serv}인분 남음</span><span class="serv-dots" aria-hidden="true">${Array.from({ length: d.serv }, (_, k) => `<i class="${k < d.left ? "" : "off"}"></i>`).join("")}</span><span>· ${md(d.made)} 만듦</span></div>
      <div class="acts">
        <button class="btn strong" type="button" data-eat="${d.id}">1인분 먹기</button>
        <button class="btn danger" type="button" data-toss="${d.id}">버리기</button>
        ${RECIPES.some(r => r.id === d.rid) ? `<button class="link" type="button" data-open="${d.rid}">레시피</button>` : ""}
      </div>
    </div>`;
  }).join("") : `<div class="empty" style="grid-column:1/-1">보관 중인 요리가 없습니다.<br>레시피에서 '요리 완료'를 누르면 여기에 담깁니다.</div>`;

  // 이번 달 기록
  const ym = iso(today0()).slice(0, 7), mon = dishLog.filter(l => l.d.slice(0, 7) === ym);
  const cooked = mon.filter(l => l.t === "cook"), eaten = mon.filter(l => l.t === "eat").reduce((a, l) => a + (l.n || 1), 0);
  const saved = cooked.reduce((a, l) => a + (l.saved || []).length, 0);
  const tossed = mon.filter(l => l.t === "toss" || l.t === "tossIng").length;
  $("#cookStats").innerHTML = `<div class="stat"><span class="label">만든 요리</span><b>${cooked.length}</b></div>
    <div class="stat"><span class="label">먹은 인분</span><b>${eaten}</b></div>
    <div class="stat"><span class="label">살린 임박 재료</span><b style="color:var(--ok)">${saved}</b></div>
    <div class="stat"><span class="label">버린 것</span><b style="color:var(--danger)">${tossed}</b></div>`;
  const ic = { cook: ["cook", "만듦"], eat: ["eat", "먹음"], toss: ["toss", "버림"], tossIng: ["toss", "버림"] };
  $("#cookLog").innerHTML = dishLog.length ? dishLog.slice(0, 8).map(l => `<li>
      <span class="ic ${ic[l.t][0]}">${ic[l.t][1].slice(0, 1)}</span>
      <span>${esc(l.name)} ${l.t === "cook" ? `${l.n}인분 만듦${(l.saved || []).length ? ` <span class="note">· 임박 ${l.saved.map(esc).join(", ")} 활용</span>` : ""}` : l.t === "eat" ? `${l.n || 1}인분 먹음` : l.t === "toss" ? `${l.n}인분 버림` : "재료 버림"} <span class="note">${md(l.d)}</span></span>
      ${l.t === "cook" && RECIPES.some(r => r.id === l.rid) ? `<button class="again" type="button" data-open="${l.rid}">다시 만들기</button>` : "<span></span>"}
    </li>`).join("") : `<li><span></span><span class="sub">아직 기록이 없습니다.</span><span></span></li>`;

  // 냉장고 선반 맨 위에 '만든 요리' 줄
  const shelf = $("#shelf");
  if (shelf && list.length){
    const row = `<div class="dish-shelf"><h4>만든 요리</h4><div class="chips">${list.map(d => `<span class="chip dish-chip"><button class="chip-edit" type="button" data-go="dishes">${esc(d.name)} <span class="note">${d.left}인분</span> ${ddayTag(d.exp)}</button></span>`).join("")}</div></div>`;
    const old = shelf.querySelector(".dish-shelf"); if (old) old.remove();
    if (shelf.querySelector(".empty")) shelf.innerHTML = row; else shelf.insertAdjacentHTML("afterbegin", row);
  }
}

/* ---------- 애니메이션 공통 무대 ---------- */
function stage(svg, firstCap, label){
  const st = document.createElement("div");
  st.className = "anim-stage"; st.setAttribute("role", "status"); st.setAttribute("aria-label", label);
  st.innerHTML = `<div class="anim-card"><svg viewBox="0 0 240 230" aria-hidden="true">${svg}</svg>
    <div class="anim-cap">${firstCap}</div><div class="anim-skip">누르면 건너뜁니다</div></div>`;
  document.body.appendChild(st);
  const anims = [], timers = [], cap = st.querySelector(".anim-cap");
  const api = {
    st, q: s => st.querySelector(s), qa: s => [...st.querySelectorAll(s)],
    add: (el, kf, o) => { const a = A(el, kf, o); anims.push(a); return a; },
    say: (ms, t) => timers.push(setTimeout(() => cap.textContent = t, ms)),
    run: (ms, lastCap) => new Promise(done => {
      let ended = false;
      const end = () => { if (ended) return; ended = true; timers.forEach(clearTimeout); anims.forEach(a => a.finish()); if (lastCap) cap.textContent = lastCap;
        A(st, [{ opacity: 1 }, { opacity: 0 }], { duration: 220, delay: 120 }).finished.then(() => { st.remove(); done(); }); };
      timers.push(setTimeout(end, ms)); st.addEventListener("click", end);
    })
  };
  return api;
}
const dishSVG = (colors, cls = "dish") => `<g class="${cls}">
  <ellipse cx="124" cy="140" rx="84" ry="52" fill="rgba(60,30,15,.12)"/><ellipse cx="120" cy="134" rx="84" ry="52" fill="#FFFDFB"/>
  <ellipse cx="120" cy="134" rx="64" ry="38" fill="#F6F0EA" stroke="rgba(120,90,70,.14)" stroke-width="1.5"/>
  ${colors.map((c, k) => { const a = k / colors.length * Math.PI * 2 - Math.PI / 2, rr = colors.length > 1 ? 20 : 0;
    return `<circle class="bite" cx="${120 + Math.cos(a) * rr}" cy="${134 + Math.sin(a) * rr * .7}" r="17" fill="${c}" stroke="rgba(0,0,0,.12)"/>`; }).join("")}</g>`;

/** 요리 → 완성 → 보관함에 담기 (약 2.8초) */
function playCookStore(r, d){
  const drops = d.colors.map((c, k) => `<circle class="drop" cx="${84 + k * (72 / (d.colors.length - 1 || 1))}" cy="40" r="11" fill="${c}" stroke="rgba(0,0,0,.12)"/>`).join("");
  const S = stage(`
    <g class="steam" fill="none" stroke="#C9B5AA" stroke-width="4" stroke-linecap="round" opacity="0"><path d="M92 92c-8-10 8-16 0-28"/><path d="M120 88c-8-10 8-16 0-28"/><path d="M148 92c-8-10 8-16 0-28"/></g>
    <g class="pot">${drops}
      <rect x="52" y="104" width="136" height="84" rx="18" fill="#6F4F42"/><rect x="44" y="98" width="152" height="14" rx="7" fill="#8A6656"/>
      <rect x="26" y="116" width="22" height="10" rx="5" fill="#8A6656"/><rect x="192" y="116" width="22" height="10" rx="5" fill="#8A6656"/>
      <path class="fire" d="M84 206c6-10 12-10 18 0M114 206c6-10 12-10 18 0M144 206c6-10 12-10 18 0" stroke="#F3A46C" stroke-width="5" fill="none" stroke-linecap="round"/></g>
    ${dishSVG(d.colors)}
    <g class="box" opacity="0">
      <rect x="46" y="128" width="148" height="78" rx="16" fill="rgba(255,255,255,.45)" stroke="#C9B5AA" stroke-width="3"/>
      <g class="lid"><rect x="38" y="112" width="164" height="18" rx="9" fill="#F3A46C"/><rect x="104" y="104" width="32" height="10" rx="5" fill="#C8682C"/></g>
      <g class="tag"><rect x="78" y="170" width="84" height="24" rx="12" fill="#FFFDFB" stroke="#C9B5AA"/><text x="120" y="186" text-anchor="middle" font-size="12" fill="#6F4F42">${d.serv}인분 · D-${dday(d.exp)}</text></g>
    </g>`, "재료를 넣는 중…", `${r.name} 요리 완료`);
  S.qa(".drop").forEach((el, k) => S.add(el, [{ transform: "translateY(-60px)", opacity: 0 }, { transform: "translateY(0)", opacity: 1, offset: .35 }, { transform: "translateY(92px) scale(.7)", opacity: 1 }],
    { duration: 620, delay: k * 90, easing: "cubic-bezier(.5,0,.8,.6)" }));
  S.add(S.q(".fire"), [{ opacity: .4 }, { opacity: 1 }, { opacity: .5 }, { opacity: 1 }], { duration: 1400, easing: "linear" });
  S.add(S.q(".pot"), [{ transform: "rotate(0)" }, { transform: "rotate(-2.5deg)" }, { transform: "rotate(2.5deg)" }, { transform: "rotate(-2deg)" }, { transform: "rotate(0)" }], { duration: 600, delay: 800, easing: "ease-in-out" });
  S.add(S.q(".steam"), [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "translateY(0)", offset: .4 }, { opacity: 0, transform: "translateY(-18px)" }], { duration: 700, delay: 800, easing: "ease-out" });
  S.say(800, "보글보글 끓는 중…");
  // 1.4 완성
  S.add(S.q(".pot"), [{ opacity: 1, transform: "scale(1)" }, { opacity: 0, transform: "scale(.8)" }], { duration: 260, delay: 1400 });
  S.add(S.q(".dish"), [{ opacity: 0, transform: "scale(.6)" }, { opacity: 1, transform: "scale(1.06)", offset: .7 }, { opacity: 1, transform: "scale(1)" }], { duration: 340, delay: 1480 });
  S.say(1480, `${r.name} 완성!`);
  // 1.95 보관함에 담기
  S.add(S.q(".box"), [{ opacity: 0, transform: "translateY(30px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 240, delay: 1950 });
  S.add(S.q(".dish"), [{ transform: "translate(0,0) scale(1)" }, { transform: "translate(0,26px) scale(.62)" }], { duration: 300, delay: 2080, fill: "forwards", composite: "replace" });
  S.add(S.q(".box .lid"), [{ transform: "translateY(-46px) rotate(-8deg)" }, { transform: "translateY(4px) rotate(0)", offset: .75 }, { transform: "translateY(0) rotate(0)" }], { duration: 300, delay: 2300 });
  S.add(S.q(".box .tag"), [{ opacity: 0, transform: "scale(.6)" }, { opacity: 1, transform: "scale(1)" }], { duration: 200, delay: 2500 });
  S.say(2300, `만든 요리에 보관했어요 · ${d.serv}인분`);
  return S.run(2850, `만든 요리에 보관했어요 · ${d.serv}인분`);
}

/** 1인분 먹기 (약 2.2초) */
function playEat(d){
  const S = stage(`${dishSVG(d.colors)}
    <g class="spoon" opacity="0"><ellipse cx="0" cy="0" rx="13" ry="9" fill="#C9B5AA"/><rect x="10" y="-3" width="58" height="6" rx="3" fill="#C9B5AA"/></g>
    <g class="heart" opacity="0"><path d="M120 60c-10-16-34-8-26 10 4 9 26 22 26 22s22-13 26-22c8-18-16-26-26-10z" fill="#E8424F"/></g>`,
    `${d.name} 1인분`, `${d.name} 먹기`);
  S.add(S.q(".dish"), [{ opacity: 0, transform: "scale(.7)" }, { opacity: 1, transform: "scale(1)" }], { duration: 260 });
  const bites = S.qa(".bite");
  S.add(S.q(".spoon"), [{ opacity: 0, transform: "translate(250px,150px) rotate(-20deg)" }, { opacity: 1, transform: "translate(150px,135px) rotate(-20deg)", offset: .2 },
    ...bites.map((b, k) => ({ opacity: 1, transform: `translate(${+b.getAttribute("cx") + 8}px,${+b.getAttribute("cy")}px) rotate(-20deg)`, offset: .25 + .65 * (k + 1) / bites.length })),
    { opacity: 0, transform: "translate(250px,40px) rotate(-40deg)" }], { duration: 1100, delay: 300, easing: "ease-in-out" });
  bites.forEach((b, k) => S.add(b, [{ transform: "scale(1)", opacity: 1 }, { transform: "scale(.2)", opacity: 0 }], { duration: 180, delay: 420 + k * (780 / bites.length) }));
  S.say(400, "냠냠, 맛있게 먹는 중…");
  S.add(S.q(".heart"), [{ opacity: 0, transform: "translateY(20px) scale(.5)" }, { opacity: 1, transform: "translateY(0) scale(1.1)", offset: .6 }, { opacity: 1, transform: "translateY(-4px) scale(1)" }], { duration: 320, delay: 1500 });
  const last = d.left ? `잘 먹었습니다! · ${d.left}인분 남음` : "잘 먹었습니다! · 다 먹었어요";
  S.say(1500, last);
  return S.run(2250, last);
}
