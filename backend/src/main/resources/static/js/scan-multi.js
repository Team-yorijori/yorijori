/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 여러 장 이어서 스캔 (v9) */

/* =====================================================================
 * v9-2) 여러 장 이어서 스캔 — 냉장고 칸마다 찍어도 한 목록에 모인다
 *   같은 재료는 수량을 더하고, 사진별로 몇 개였는지 줄 아래에 적는다
 * ===================================================================== */
let scanShots = [];
const rowOf = name => [...document.querySelectorAll("#scanList li[data-row]")].find(l => l.querySelector("input[type=text]").value.trim() === name);
function mergeScan(groups){
  const list = $("#scanList"), color = g => SCAN_COLORS[g.id % SCAN_COLORS.length];
  groups.forEach(g => {
    const li = rowOf(g.ko);
    if (li){
      const q = li.querySelector("input[type=number]");
      q.value = fmtQty((parseFloat(q.value) || 0) + scanQty(g.ko, g.count));
      if (g.score > +(li.dataset.score || 0) && !g.cand){
        li.querySelector(".tagcell").innerHTML = scoreTag(g) + `<button class="row-x" type="button" aria-label="이 줄 지우기">×</button>`;
      }
      if (!g.cand && g.score >= autoOf(g.ko)) li.querySelector("input[type=checkbox]").checked = true;
      const sep = list.querySelector(".scan-sep");          // 후보였는데 이번 사진에서 확실히 찾았으면 위로 올린다
      if (!g.cand && sep && (sep.compareDocumentPosition(li) & Node.DOCUMENT_POSITION_FOLLOWING)) list.insertBefore(li, sep);
      li.classList.remove("flash"); void li.offsetWidth; li.classList.add("flash");
    } else {
      const html = scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: !g.cand && g.score >= autoOf(g.ko), color: color(g),
        tag: g.cand ? `<span class="tag t-soft">후보 ${Math.round(g.score * 100)}%</span>` : scoreTag(g) });
      let sep = list.querySelector(".scan-sep");
      if (g.cand && !sep){ list.insertAdjacentHTML("beforeend", `<li class="scan-sep">혹시 이것도 있나요? · 자신 없는 후보라 꺼 두었습니다</li>`); sep = null; }
      if (!g.cand && sep) sep.insertAdjacentHTML("beforebegin", html); else list.insertAdjacentHTML("beforeend", html);
    }
  });
}
function noteShot(groups, no){
  groups.forEach(g => {
    const li = rowOf(g.ko); if (!li) return;
    li.dataset.score = Math.max(+(li.dataset.score || 0), g.cand ? 0 : g.score);
    const shots = JSON.parse(li.dataset.shots || "{}"); shots[no] = (shots[no] || 0) + g.count; li.dataset.shots = JSON.stringify(shots);
  });
  // 사진이 2장 이상이면 모든 줄에 "사진1 2개 · 사진3 1개"처럼 출처를 적는다
  document.querySelectorAll("#scanList li[data-shots]").forEach(li => {
    const shots = JSON.parse(li.dataset.shots);
    let el = li.querySelector(".shots");
    if (!el){ el = document.createElement("span"); el.className = "shots note"; li.appendChild(el); }
    el.textContent = scanShots.length > 1 ? Object.keys(shots).map(k => `사진${k} ${shots[k]}개`).join(" · ") : "";
  });
}
function renderShotStrip(active){
  const el = $("#shotStrip"); if (!el) return;
  el.hidden = scanShots.length < 2;
  el.innerHTML = scanShots.map((sh, i) => `<button type="button" data-shot="${i}" aria-pressed="${i === active}">사진 ${sh.no} · ${sh.groups.filter(g => !g.cand).length}종</button>`).join("");
  el.onclick = e => {
    const b = e.target.closest("[data-shot]"); if (!b) return;
    const st = $("#scanStage"); st.innerHTML = ""; st.appendChild(scanShots[+b.dataset.shot].cv); renderShotStrip(+b.dataset.shot);
  };
}
async function scanFilesV9(e, status){
  const files = [...e.target.files]; e.target.value = "";
  if (!files.length) return;
  if (!$("#scanList")) { scanShots = []; scanRowSeq = 0; }
  $("#scanOk").disabled = true;
  try {
    await ensureModel(status);
    for (const file of files){
      const no = scanShots.length + 1;
      status(`사진 ${no} · 재료를 찾는 중…`);
      const r = await FridgeScan.detect(file, { minScore: SCAN_MIN, confirmBelow: 0.6 });
      await drawScan(file, r);
      const groups = groupScan(r);
      scanShots.push({ no, groups, cv: $("#scanStage canvas") });
      if (!$("#scanList")) { renderScanResult(groups, groups.length ? "" : "이 사진에서는 재료를 찾지 못했습니다. 아래에서 직접 추가하거나 다른 각도로 다시 찍어 보세요.");
        $("#scanOk").disabled = true; }            // 남은 사진을 다 볼 때까지 등록 버튼은 잠가 둔다
      else mergeScan(groups);
      noteShot(groups, no);
      const nMain = groups.filter(g => !g.cand).length, nCand = groups.length - nMain;
      status(`사진 ${scanShots.length}장 · 이번 사진에서 ${nMain}종${nCand ? `(후보 ${nCand}종)` : ""} · ${r.ms}ms`
        + (scanShots.length > 1 ? " · 같은 재료는 수량을 합쳤습니다. 같은 물건을 두 번 찍었다면 수량을 줄이세요" : " · 다른 칸도 찍어서 추가할 수 있습니다 · 깻잎·콩나물처럼 아직 못 찾는 재료는 아래에서 직접 추가하세요"));
    }
    renderShotStrip(scanShots.length - 1);
    $("#dropBox").textContent = "+ 사진 더 추가 (냉장고 다른 칸도 찍으면 한 목록에 모입니다)";
    $("#scanOk").disabled = false;
  } catch (err) {
    status("인식에 실패했습니다: " + (err.message || err), true);
    if (!$("#scanList")){
      $("#scanResult").innerHTML = `<div class="actions" style="justify-content:flex-start"><button class="btn ghost" id="scanDemo">예시 결과로 둘러보기</button></div>`;
      $("#scanDemo").onclick = () => { closeModal(); openScanDemo(); };
    } else $("#scanOk").disabled = false;
  }
}
