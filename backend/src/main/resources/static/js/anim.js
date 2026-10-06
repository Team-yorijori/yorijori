/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 애니메이션: 요리·버리기 · On/Off (v7) */

/* =====================================================================
 * v7) 애니메이션 — 요리 완료(요리 → 먹기), 버리기(쓰레기통), On/Off
 *   Web Animations API(element.animate)로 2~3초 안에 끝난다. 외부 파일 없음
 * ===================================================================== */
const ANIM_KEY = "yorijori-demo-anim";
let animPref = (() => {
  try { const v = localStorage.getItem(ANIM_KEY); if (v) return v === "on"; } catch(e){}
  return !(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);  // '동작 줄이기'면 꺼진 채로 시작
})();
const animOn = () => animPref;
function setAnim(on, say){
  animPref = on;
  try { localStorage.setItem(ANIM_KEY, on ? "on" : "off"); } catch(e){}
  $("#animBtn").setAttribute("aria-pressed", on);
  $("#animLabel").textContent = on ? "애니 ON" : "애니 OFF";
  if (say) toast(on ? "애니메이션을 켰습니다." : "애니메이션을 껐습니다.");
}
const wait = ms => new Promise(ok => setTimeout(ok, ms));
const A = (el, kf, o) => el.animate(kf, { fill: "both", easing: "cubic-bezier(.3,.7,.3,1)", ...o });

/** 요리 → 먹기 (약 2.7초). 누르면 건너뛴다 */
function playCook(r){
  return new Promise(done => {
    const cols = [...new Set(r.ings.map(i => (MASTER[i[0]] || [])[4]).filter(Boolean))].slice(0, 5);
    while (cols.length < 3) cols.push(["#F3A46C", "#9CCB6B", "#F7C948"][cols.length]);
    const drops = cols.map((c, k) => `<circle class="drop" cx="${84 + k * (72 / (cols.length - 1 || 1))}" cy="40" r="11" fill="${c}" stroke="rgba(0,0,0,.12)"/>`).join("");
    const food = cols.map((c, k) => { const a = k / cols.length * Math.PI * 2 - Math.PI / 2, rr = cols.length > 1 ? 20 : 0;
      return `<circle class="bite" cx="${120 + Math.cos(a) * rr}" cy="${134 + Math.sin(a) * rr * .7}" r="17" fill="${c}" stroke="rgba(0,0,0,.12)"/>`; }).join("");
    const st = document.createElement("div");
    st.className = "anim-stage";
    st.setAttribute("role", "status"); st.setAttribute("aria-label", `${r.name} 요리 완료`);
    st.innerHTML = `<div class="anim-card">
      <svg viewBox="0 0 240 230" aria-hidden="true">
        <g class="steam" fill="none" stroke="#C9B5AA" stroke-width="4" stroke-linecap="round" opacity="0">
          <path d="M92 92c-8-10 8-16 0-28"/><path d="M120 88c-8-10 8-16 0-28"/><path d="M148 92c-8-10 8-16 0-28"/></g>
        <g class="pot">
          ${drops}
          <rect x="52" y="104" width="136" height="84" rx="18" fill="#6F4F42"/>
          <rect x="44" y="98" width="152" height="14" rx="7" fill="#8A6656"/>
          <rect x="26" y="116" width="22" height="10" rx="5" fill="#8A6656"/><rect x="192" y="116" width="22" height="10" rx="5" fill="#8A6656"/>
          <path d="M84 206c6-10 12-10 18 0M114 206c6-10 12-10 18 0M144 206c6-10 12-10 18 0" stroke="#F3A46C" stroke-width="5" fill="none" stroke-linecap="round" class="fire"/>
        </g>
        <g class="dish" opacity="0">
          <ellipse cx="124" cy="140" rx="84" ry="52" fill="rgba(60,30,15,.12)"/>
          <ellipse cx="120" cy="134" rx="84" ry="52" fill="#FFFDFB"/>
          <ellipse cx="120" cy="134" rx="64" ry="38" fill="#F6F0EA" stroke="rgba(120,90,70,.14)" stroke-width="1.5"/>
          ${food}
        </g>
        <g class="spoon" opacity="0"><ellipse cx="0" cy="0" rx="13" ry="9" fill="#C9B5AA"/><rect x="10" y="-3" width="58" height="6" rx="3" fill="#C9B5AA"/></g>
        <g class="heart" opacity="0"><path d="M120 60c-10-16-34-8-26 10 4 9 26 22 26 22s22-13 26-22c8-18-16-26-26-10z" fill="#E8424F"/></g>
      </svg>
      <div class="anim-cap" id="animCap">재료를 넣는 중…</div>
      <div class="anim-skip">누르면 건너뜁니다</div></div>`;
    document.body.appendChild(st);
    const $$ = q => [...st.querySelectorAll(q)], cap = st.querySelector("#animCap");
    const anims = [], timers = [];
    const add = a => (anims.push(a), a), later = (ms, f) => timers.push(setTimeout(f, ms));
    // 0.0~0.9 재료가 냄비로
    $$(".drop").forEach((d, k) => add(A(d, [{ transform: "translateY(-60px)", opacity: 0 }, { transform: "translateY(0)", opacity: 1, offset: .35 }, { transform: "translateY(92px) scale(.7)", opacity: 1 }],
      { duration: 620, delay: k * 90, easing: "cubic-bezier(.5,0,.8,.6)" })));
    // 불꽃 깜빡, 냄비 흔들, 김
    add(A(st.querySelector(".fire"), [{ opacity: .4 }, { opacity: 1 }, { opacity: .5 }, { opacity: 1 }], { duration: 1400, easing: "linear" }));
    add(A(st.querySelector(".pot"), [{ transform: "rotate(0)" }, { transform: "rotate(-2.5deg)" }, { transform: "rotate(2.5deg)" }, { transform: "rotate(-2deg)" }, { transform: "rotate(0)" }],
      { duration: 600, delay: 800, easing: "ease-in-out" }));
    add(A(st.querySelector(".steam"), [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "translateY(0)", offset: .4 }, { opacity: 0, transform: "translateY(-18px)" }],
      { duration: 700, delay: 800, easing: "ease-out" }));
    later(800, () => cap.textContent = "보글보글 끓는 중…");
    // 1.4~1.75 냄비 → 접시
    add(A(st.querySelector(".pot"), [{ opacity: 1, transform: "scale(1)" }, { opacity: 0, transform: "scale(.8)" }], { duration: 260, delay: 1400 }));
    add(A(st.querySelector(".dish"), [{ opacity: 0, transform: "scale(.6)" }, { opacity: 1, transform: "scale(1.06)", offset: .7 }, { opacity: 1, transform: "scale(1)" }],
      { duration: 340, delay: 1480 }));
    later(1480, () => cap.textContent = `${r.name} 완성!`);
    // 1.85~2.45 숟가락으로 한입씩
    const bites = $$(".bite"), sp = st.querySelector(".spoon");
    add(A(sp, [{ opacity: 0, transform: "translate(250px,150px) rotate(-20deg)" }, { opacity: 1, transform: "translate(150px,135px) rotate(-20deg)", offset: .25 },
      ...bites.map((b, k) => ({ opacity: 1, transform: `translate(${+b.getAttribute("cx") + 8}px,${+b.getAttribute("cy")}px) rotate(-20deg)`, offset: .3 + .6 * (k + 1) / bites.length })),
      { opacity: 0, transform: "translate(250px,40px) rotate(-40deg)" }], { duration: 760, delay: 1780, easing: "ease-in-out" }));
    later(1850, () => cap.textContent = "냠냠, 맛있게 먹는 중…");
    bites.forEach((b, k) => add(A(b, [{ transform: "scale(1)", opacity: 1 }, { transform: "scale(.2)", opacity: 0 }], { duration: 160, delay: 1900 + k * (520 / bites.length) })));
    // 2.45~2.75 잘 먹었습니다
    add(A(st.querySelector(".heart"), [{ opacity: 0, transform: "translateY(20px) scale(.5)" }, { opacity: 1, transform: "translateY(0) scale(1.1)", offset: .6 }, { opacity: 1, transform: "translateY(-4px) scale(1)" }],
      { duration: 320, delay: 2400 }));
    later(2420, () => cap.textContent = "잘 먹었습니다!");
    let ended = false;
    const end = () => {
      if (ended) return; ended = true;
      timers.forEach(clearTimeout); anims.forEach(a => a.finish()); cap.textContent = "잘 먹었습니다!";
      A(st, [{ opacity: 1 }, { opacity: 0 }], { duration: 200 }).finished.then(() => { st.remove(); done(); });
    };
    later(2750, end);
    st.addEventListener("click", end);
  });
}

/** 버리기: 재료 칩이 쓰레기통으로 (약 2.2초). 화면을 막지 않는다 */
function playTrash(rect, name, color0){
  const box = (isMobileView() ? $("#app") : document.documentElement).getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  const L = Math.max(box.left, 0), R = Math.min(box.right, vw), B = Math.min(box.bottom, vh);
  const can = document.createElement("div"); can.className = "trash";
  can.innerHTML = `<svg viewBox="0 0 76 92" aria-hidden="true">
    <path d="M10 26h56l-6 60a6 6 0 0 1-6 6H22a6 6 0 0 1-6-6z" fill="#957A6F"/>
    <path d="M28 38v40M38 38v40M48 38v40" stroke="#FFF4EC" stroke-width="3" stroke-linecap="round" opacity=".55"/>
    <g class="lid"><rect x="4" y="14" width="68" height="10" rx="5" fill="#6F4F42"/><rect x="28" y="6" width="20" height="10" rx="4" fill="#6F4F42"/></g></svg>`;
  // 모바일 하단 탭바가 보이면 그 위에 놓는다
  const tb = document.querySelector(".tabbar"), tbr = tb ? tb.getBoundingClientRect() : null;
  const floor = tbr && tbr.height && getComputedStyle(tb).display !== "none" ? Math.min(B, tbr.top) : B - 60;
  const cx = (L + R) / 2, top = floor - 92 - 44;
  Object.assign(can.style, { left: (cx - 38) + "px", top: top + "px" });
  const chip = document.createElement("div"); chip.className = "fly-chip";
  const color = color0 || (MASTER[name] || [])[4] || "#C9A27E";
  chip.innerHTML = `<i style="background:${color}"></i>${esc(name)}`;
  document.body.append(can, chip);
  const cw = chip.offsetWidth, ch = chip.offsetHeight;
  const sx = Math.min(Math.max(rect.left + rect.width / 2, L + cw / 2), R - cw / 2), sy = Math.min(Math.max(rect.top + rect.height / 2, 0), vh);
  Object.assign(chip.style, { left: (sx - cw / 2) + "px", top: (sy - ch / 2) + "px" });
  const dx = cx - sx, dy = top + 30 - sy;
  const cap = document.createElement("div"); cap.className = "trash-cap"; cap.textContent = `${name} 버림`;
  document.body.append(cap);
  Object.assign(cap.style, { left: (cx - cap.offsetWidth / 2) + "px", top: (top + 98) + "px" });
  A(can, [{ opacity: 0, transform: "translateY(24px) scale(.6)" }, { opacity: 1, transform: "translateY(0) scale(1)" }], { duration: 260 });
  const lid = can.querySelector(".lid");
  A(lid, [{ transform: "rotate(0)" }, { transform: "rotate(-38deg)" }], { duration: 200, delay: 220 });
  A(lid, [{ transform: "rotate(-38deg)" }, { transform: "rotate(0)" }], { duration: 180, delay: 1330, fill: "forwards" });
  A(chip, [
    { transform: "translate(0,0) scale(1) rotate(0)", opacity: 1 },
    { transform: "translate(0,-26px) scale(1.05) rotate(-6deg)", opacity: 1, offset: .18 },
    { transform: `translate(${dx * .6}px,${Math.min(dy, 0) - 70}px) scale(.8) rotate(90deg)`, opacity: 1, offset: .5 },
    { transform: `translate(${dx}px,${dy - 20}px) scale(.5) rotate(200deg)`, opacity: 1, offset: .82 },
    { transform: `translate(${dx}px,${dy + 18}px) scale(.3) rotate(240deg)`, opacity: 0 }
  ], { duration: 1050, delay: 260, easing: "cubic-bezier(.45,.05,.55,.95)" });
  A(can, [{ transform: "rotate(0)" }, { transform: "rotate(-7deg)" }, { transform: "rotate(6deg)" }, { transform: "rotate(-3deg)" }, { transform: "rotate(0)" }], { duration: 380, delay: 1420, fill: "none" });
  A(cap, [{ opacity: 0, transform: "translateY(6px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 200, delay: 1420 });
  const out = [{ opacity: 1 }, { opacity: 0 }];
  Promise.all([A(can, out, { duration: 300, delay: 1900 }).finished, A(cap, out, { duration: 300, delay: 1900 }).finished])
    .then(() => { can.remove(); chip.remove(); cap.remove(); });
}
