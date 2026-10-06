/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 재료 사진 스캔 창 (모델 불러오기 · 결과 편집 · 등록 후 추천) */

/* ---------- v3~: 실제 재료 인식 (YOLO26, 브라우저에서 실행) · v9부터 fridge_v4.onnx ---------- */
// v3(25종) 클래스 목록은 v4로 교체했다
// v4: fridge_v4.onnx — 33종 (v3 25종 + 배추·배·귤·오렌지·라임·딸기·포도·키위). 검증 mAP50 0.905
const SCAN_CLASSES = [{"id": 0, "en": "cabbage", "ko": "양배추"}, {"id": 1, "en": "green_onion", "ko": "대파"}, {"id": 2, "en": "onion", "ko": "양파"}, {"id": 3, "en": "potato", "ko": "감자"}, {"id": 4, "en": "carrot", "ko": "당근"}, {"id": 5, "en": "zucchini", "ko": "애호박"}, {"id": 6, "en": "cucumber", "ko": "오이"}, {"id": 7, "en": "radish", "ko": "무"}, {"id": 8, "en": "spinach", "ko": "시금치"}, {"id": 9, "en": "mushroom", "ko": "버섯"}, {"id": 10, "en": "tomato", "ko": "토마토"}, {"id": 11, "en": "chili_pepper", "ko": "고추"}, {"id": 12, "en": "garlic", "ko": "마늘"}, {"id": 13, "en": "egg", "ko": "계란"}, {"id": 14, "en": "tofu", "ko": "두부"}, {"id": 15, "en": "milk", "ko": "우유"}, {"id": 16, "en": "apple", "ko": "사과"}, {"id": 17, "en": "banana", "ko": "바나나"}, {"id": 18, "en": "lemon", "ko": "레몬"}, {"id": 19, "en": "bell_pepper", "ko": "파프리카"}, {"id": 20, "en": "eggplant", "ko": "가지"}, {"id": 21, "en": "broccoli", "ko": "브로콜리"}, {"id": 22, "en": "corn", "ko": "옥수수"}, {"id": 23, "en": "cheese", "ko": "치즈"}, {"id": 24, "en": "sweet_potato", "ko": "고구마"}, {"id": 25, "en": "napa_cabbage", "ko": "배추"}, {"id": 26, "en": "pear", "ko": "배"}, {"id": 27, "en": "mandarin", "ko": "귤"}, {"id": 28, "en": "orange", "ko": "오렌지"}, {"id": 29, "en": "lime", "ko": "라임"}, {"id": 30, "en": "strawberry", "ko": "딸기"}, {"id": 31, "en": "grape", "ko": "포도"}, {"id": 32, "en": "kiwi", "ko": "키위"}];
const ORT_CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/";
const SCAN_COLORS = ["#E2483A","#3F8F3A","#E39A1E","#2F6FB5","#8E44AD","#C8682C","#16A085","#D35400","#7F8C8D","#B03A2E"];
let modelReady = null;

function loadScript(src){
  return new Promise((ok, no) => {
    const el = document.createElement("script");
    el.src = src; el.onload = ok; el.onerror = () => no(new Error("onnxruntime-web 을 불러오지 못했다"));
    document.head.appendChild(el);
  });
}
function ensureModel(onStatus){
  if (!modelReady) modelReady = (async () => {
    onStatus && onStatus("인식 엔진을 불러오는 중…");
    if (!window.ort) await loadScript(ORT_CDN + "ort.min.js");
    onStatus && onStatus("재료 인식 모델을 준비하는 중… (처음 한 번만 10~20초)");
    // 데모: HTML 안의 base64 모델을 썼다
    // const b64 = document.getElementById("fridgeModel").textContent.trim();
    // const buf = await (await fetch("data:application/octet-stream;base64," + b64)).arrayBuffer();
    // Spring: static/models/ 의 파일을 받는다 (브라우저가 캐시하므로 두 번째부터 빠르다)
    const cfg = window.YORIJORI || {};
    const res = await fetch(cfg.modelUrl || "/models/fridge.onnx");
    if (!res.ok) throw new Error("모델 파일이 없습니다 (static/models/fridge.onnx)");
    const buf = await res.arrayBuffer();
    const classes = await fetch(cfg.classesUrl || "/models/classes.json").then(r => r.ok ? r.json() : SCAN_CLASSES).catch(() => SCAN_CLASSES);
    return FridgeScan.load({ model: buf, classes, wasmPaths: ORT_CDN });
  })().catch(e => { modelReady = null; throw e; });
  return modelReady;
}

function scanQty(name, count){
  const m = MASTER[name];
  if (!m) return count;
  return ["개","쪽"].includes(m[2]) ? Math.max(1, count) : m[3] * Math.max(1, count);
}

async function drawScan(file, r){
  const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
  const s = Math.min(1, 1000 / bmp.width);
  const cv = document.createElement("canvas"); cv.width = Math.round(bmp.width * s); cv.height = Math.round(bmp.height * s);
  const ctx = cv.getContext("2d"); ctx.drawImage(bmp, 0, 0, cv.width, cv.height);
  const lw = Math.max(2, cv.width / 260), fs = Math.max(14, Math.round(cv.width / 36));
  ctx.font = `${fs}px "Gowun Dodum", sans-serif`; ctx.textBaseline = "top";
  r.detections.forEach(d => {
    const [x1, y1, x2, y2] = d.box.map(v => v * s), col = SCAN_COLORS[d.id % SCAN_COLORS.length];
    const weak = d.score < SCAN_MAIN;
    ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.setLineDash(weak ? [lw * 3, lw * 2] : []); ctx.strokeRect(x1, y1, x2 - x1, y2 - y1); ctx.setLineDash([]);
    const label = `${weak ? "후보 " : ""}${d.ko} ${Math.round(d.score * 100)}%`, tw = ctx.measureText(label).width + 10;
    const ty = y1 - fs - 8 < 0 ? y1 : y1 - fs - 8;
    ctx.fillStyle = col; ctx.fillRect(x1, ty, tw, fs + 8); ctx.fillStyle = "#fff"; ctx.fillText(label, x1 + 5, ty + 4);
  });
  const st = $("#scanStage"); st.innerHTML = ""; st.appendChild(cv); st.hidden = false;
}

/* v5: 스캔 결과 편집 — 인식 결과, 후보, 직접 추가를 한 목록에서 다룬다 */
const SCAN_MAIN = 0.35, SCAN_MIN = 0.15;
// v5 목록: ["오렌지","귤","딸기","포도","키위","배","라임","복숭아","계란","우유","두부","대파"]
// v9: 모델 v4가 과일 8종을 직접 찾으므로, 아직 못 찾거나 약한 재료로 바꾼다
const SCAN_QUICK = ["깻잎","콩나물","두부","대파","부추","상추","숙주","복숭아","블루베리","돼지고기","김치","어묵"];
let scanRowSeq = 0;
const unitOf = name => MASTER[name] ? MASTER[name][2] : "개";

// detections → 재료별로 묶기. 35% 이상 박스가 있으면 본 결과, 없으면 후보
function groupScan(r){
  const by = new Map();
  r.detections.forEach(d => {
    const g = by.get(d.ko) || { ko: d.ko, id: d.id, strong: 0, weak: 0, score: 0 };
    d.score >= SCAN_MAIN ? g.strong++ : g.weak++;
    g.score = Math.max(g.score, d.score); by.set(d.ko, g);
  });
  return [...by.values()].map(g => ({ ...g, count: g.strong || g.weak, cand: !g.strong })).sort((a, b) => a.cand - b.cand || b.score - a.score);
}

function scanRow({ name = "", qty, checked = true, color = "var(--muted)", tag = "", src = "" }){
  const i = scanRowSeq++, q = qty ?? (name ? scanQty(name, 1) : 1);
  return `<li data-row="${i}">
    <input type="checkbox" ${checked ? "checked" : ""} aria-label="등록 여부">
    <span style="display:flex;align-items:center;min-width:0"><span class="sw" style="background:${color}"></span>
      <input type="text" data-ac autocomplete="off" value="${esc(name)}" placeholder="재료 이름" aria-label="재료 이름"></span>
    <span class="qty"><input type="number" min="0" step="any" value="${fmtQty(q)}" aria-label="수량"><span class="unit">${esc(unitOf(name))}</span></span>
    <span class="tagcell">${tag}<button class="row-x" type="button" aria-label="이 줄 지우기">×</button></span>
    ${src ? `<span class="src note" title="${esc(src)}">읽은 글자: ${esc(src)}</span>` : ""}
  </li>`;
}

function renderScanResult(groups, note){
  const main = groups.filter(g => !g.cand), cand = groups.filter(g => g.cand);
  const color = g => SCAN_COLORS[g.id % SCAN_COLORS.length];
  $("#scanResult").innerHTML = `
    ${note ? `<div class="empty" style="margin-top:12px">${note}</div>` : ""}
    <div class="label" style="margin-top:12px">등록할 재료 · 이름을 고치면 단위도 바뀝니다</div>
    <ul class="scan-list" id="scanList">
      ${main.map(g => scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: g.score >= autoOf(g.ko), color: color(g),
        tag: scoreTag(g) })).join("")}
      ${cand.length ? `<li class="scan-sep">혹시 이것도 있나요? · 자신 없는 후보라 꺼 두었습니다</li>` : ""}
      ${cand.map(g => scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: false, color: color(g),
        tag: `<span class="tag t-soft">후보 ${Math.round(g.score * 100)}%</span>` })).join("")}
    </ul>
    <div class="scan-add">
      <button class="btn ghost" type="button" id="scanAddRow">+ 빠진 재료 직접 추가</button>
      <div class="note" style="margin-top:10px">자주 놓치는 재료 · 누르면 바로 추가됩니다</div>
      <div class="chips" id="scanChips">${SCAN_QUICK.map(n => `<button type="button" class="chip" data-name="${esc(n)}">+ ${esc(n)}</button>`).join("")}</div>
    </div>`;
  $("#scanOk").disabled = false;
}

// 같은 이름이 이미 있으면 수량만 올리고, 없으면 새 줄
function scanAdd(name){
  const list = $("#scanList"); if (!list) return;
  const li = [...list.querySelectorAll("li[data-row]")].find(l => l.querySelector("input[type=text]").value.trim() === name);
  if (li){
    const q = li.querySelector("input[type=number]"), cb = li.querySelector("input[type=checkbox]");
    if (cb.checked) q.value = fmtQty((parseFloat(q.value) || 0) + scanQty(name, 1)); else cb.checked = true;
    li.classList.remove("flash"); void li.offsetWidth; li.classList.add("flash");
    return li;
  }
  list.insertAdjacentHTML("beforeend", scanRow({ name, tag: `<span class="tag t-soft">직접</span>` }));
  return list.lastElementChild;
}

function bindScanList(){
  const box = $("#scanResult");
  box.onclick = e => {
    const x = e.target.closest(".row-x"); if (x){ x.closest("li").remove(); return; }
    const chip = e.target.closest("#scanChips .chip"); if (chip){ scanAdd(chip.dataset.name); return; }
    if (e.target.id === "scanAddRow"){
      $("#scanList").insertAdjacentHTML("beforeend", scanRow({ tag: `<span class="tag t-soft">직접</span>` }));
      $("#scanList").lastElementChild.querySelector("input[type=text]").focus();
    }
  };
  // 이름을 바꾸면 단위와 기본 수량을 그 재료에 맞춘다 (예: 레몬 1개 → 딸기 500g)
  box.onchange = e => {
    if (!e.target.matches(".scan-list input[type=text]")) return;
    const li = e.target.closest("li"), name = e.target.value.trim(), old = li.dataset.unit ?? li.querySelector(".unit").textContent;
    const unit = unitOf(name); li.querySelector(".unit").textContent = unit; li.dataset.unit = unit;
    if (unit !== old) li.querySelector("input[type=number]").value = fmtQty(scanQty(name, 1));
    if (name) li.querySelector("input[type=checkbox]").checked = true;
  };
}

function openScan(){
  modal(`<h2>재료 사진 스캔</h2>
    <div class="seg scan-mode" role="group" aria-label="등록 방법"><button type="button" aria-pressed="true">재료 사진</button><button type="button" id="toReceipt" aria-pressed="false">영수증·주문내역</button></div>
    <div class="sub" style="margin-top:10px">냉장고나 장바구니 사진을 올리면 재료를 찾아냅니다. 냉장고 칸마다 여러 장 찍어도 한 목록에 모입니다. 사진은 이 기기 안에서만 분석하고 어디에도 보내지 않습니다.</div>
    <label class="drop" for="scanFile" id="dropBox">사진을 찍거나 고르세요 (여러 장 가능)</label>
    <input type="file" id="scanFile" accept="image/*" multiple hidden>
    <div class="scan-stage" id="scanStage" hidden></div>
    <div class="shot-strip" id="shotStrip" hidden></div>
    <div class="scan-status" id="scanStatus"></div>
    <div id="scanResult"></div>
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="scanOk" disabled>선택한 재료 등록</button></div>`);
  const status = (t, err) => { const el = $("#scanStatus"); if (!el) return; el.textContent = t; el.className = "scan-status" + (err ? " err" : ""); };
  $("#toReceipt").onclick = openReceipt;
  // 사진을 고르기 전에 모델을 미리 준비한다
  ensureModel(status).then(info => status(`준비됨 · ${info.backend === "webgpu" ? "그래픽카드(WebGPU)" : "CPU(WASM)"}로 인식합니다`))
    .catch(e => status("인식 모델을 불러오지 못했습니다: " + (e.message || e) + " · 인터넷 연결을 확인하세요", true));

  $("#scanFile").onchange = async e => {
    const file = e.target.files[0]; if (!file) return;
    $("#dropBox").textContent = "다른 사진으로 바꾸려면 누르세요";
    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true; scanRowSeq = 0;
    try {
      await ensureModel(status);
      status("재료를 찾는 중…");
      const r = await FridgeScan.detect(file, { minScore: SCAN_MIN, confirmBelow: 0.6 });
      await drawScan(file, r);
      const groups = groupScan(r), nMain = groups.filter(g => !g.cand).length, nCand = groups.length - nMain;
      status(`${nMain}종 찾음${nCand ? ` · 후보 ${nCand}종` : ""} · ${r.ms}ms · 아직 학습하지 않은 재료(오렌지, 딸기 등)는 아래에서 직접 추가하세요`);
      renderScanResult(groups, groups.length ? "" : "찾은 재료가 없습니다. 아래에서 직접 추가하거나 재료가 크게 보이게 다시 찍어 보세요.");
      return;
      /* v4 목록 (v5에서 renderScanResult로 대체) */
      $("#scanResult").innerHTML = `<div class="label" style="margin-top:12px">인식 결과 · 이름과 수량을 고칠 수 있습니다</div>
        <ul class="scan-list">${r.items.map((it, i) => {
          const name = it.ko, unit = MASTER[name] ? MASTER[name][2] : "개";
          return `<li>
            <input type="checkbox" id="sc${i}" ${it.needsConfirm ? "" : "checked"} aria-label="${esc(name)} 등록 여부">
            <span style="display:flex;align-items:center;min-width:0"><span class="sw" style="background:${SCAN_COLORS[it.id % SCAN_COLORS.length]}"></span>
              <input type="text" data-ac autocomplete="off" value="${esc(name)}" id="sn${i}" aria-label="재료 이름"></span>
            <span class="qty"><input type="number" min="0" step="any" value="${fmtQty(scanQty(name, it.count))}" id="sq${i}" aria-label="수량">${esc(unit)}</span>
            <span class="tagcell"><span class="tag ${it.needsConfirm ? "t-warn" : "t-ok"}">${it.needsConfirm ? "확인 필요 " : ""}${Math.round(it.score * 100)}%</span></span>
          </li>`; }).join("")}</ul>`;
      $("#scanOk").disabled = false;
    } catch (err) {
      status("인식에 실패했습니다: " + (err.message || err), true);
      $("#scanResult").innerHTML = `<div class="actions" style="justify-content:flex-start"><button class="btn ghost" id="scanDemo">예시 결과로 둘러보기</button></div>`;
      $("#scanDemo").onclick = () => { closeModal(); openScanDemo(); };
    }
  };

  // v9: 여러 장 이어서 스캔 — 위의 한 장짜리 처리 대신 이 함수를 쓴다
  scanShots = [];
  $("#scanFile").onchange = e => scanFilesV9(e, status);

  bindScanList();
  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li[data-row]")].filter(li => li.querySelector("input[type=checkbox]").checked)
      .map(li => ({ name: li.querySelector("input[type=text]").value.trim(), qty: parseFloat(li.querySelector("input[type=number]").value) || undefined }))
      .filter(p => p.name);
    if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
    const merged = new Map();
    picked.forEach(p => { const m = merged.get(p.name); m ? (m.qty = (m.qty || 0) + (p.qty || 0) || undefined) : merged.set(p.name, { ...p }); });
    picked.length = 0; picked.push(...merged.values());
    picked.forEach(p => addItem(p.name, "", p.qty));
    showScanRecipes(picked.map(p => p.name));
  };
}

/* 등록 직후: 방금 넣은 재료로 만들 수 있는 레시피를 바로 보여준다 */
function showScanRecipes(names){
  const list = ranked().filter(m => m.r.ings.some(i => names.includes(i[0]))).slice(0, 4);
  modal(`<h2>${names.length}가지 재료를 등록했습니다</h2>
    <div class="sub">${names.map(esc).join(", ")} · 소비기한은 재료별 보관 기간으로 자동 안내했습니다.</div>
    ${list.length ? `<div class="label" style="margin-top:14px">방금 넣은 재료로 만들 수 있는 요리</div>
      <ul class="scan-recs">${list.map(m => `<li><button data-open="${m.r.id}" data-close-after>
        <span>${esc(m.r.name)} <span class="note">${m.r.time}분</span></span>
        ${m.missing.length ? `<span class="tag t-warn">${m.missing.length}개 부족</span>` : `<span class="tag t-ok">바로 가능</span>`}
      </button></li>`).join("")}</ul>` : `<div class="empty">이 재료로 만들 수 있는 레시피가 아직 없습니다.</div>`}
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="goRecipes">추천 레시피 전체 보기</button></div>`);
  $("#goRecipes").onclick = () => { closeModal(); go("recipes"); };
  document.querySelectorAll("[data-close-after]").forEach(b => b.addEventListener("click", () => setTimeout(closeModal, 0)));
}
