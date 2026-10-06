"""v4 + 스캔 결과에서 바로 재료 추가·후보 표시 → 요리조리_데모_v5.html"""
from pathlib import Path

SRC = Path('/home/claude/yorijori-demo/요리조리_데모_v4.html')
OUT = Path('/home/claude/yorijori-demo/요리조리_데모_v5.html')

s = SRC.read_text(encoding='utf-8')
def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)

rep('<title>요리조리 v4</title>', '<title>요리조리 v5</title>')

# ---------- 1) 모델이 아직 모르는 과일도 냉장고에 넣을 수 있게 재료 마스터 추가 ----------
rep('''"버터":["유제품·알",60,"g",200,"#F6E3A1"],"생크림":["유제품·알",7,"ml",200,"#FBF7EE"]
};''', '''"버터":["유제품·알",60,"g",200,"#F6E3A1"],"생크림":["유제품·알",7,"ml",200,"#FBF7EE"],
  // v5 추가: 스캔 모델에 아직 없는 과일 (직접 추가용)
  "오렌지":["과일",14,"개",3,"#F39A2B"],"귤":["과일",14,"개",10,"#F5A623"],"딸기":["과일",3,"g",500,"#E8424F"],
  "포도":["과일",7,"송이",1,"#6B3FA0"],"키위":["과일",14,"개",4,"#8BA33B"],"라임":["과일",21,"개",2,"#8CC63F"],
  "복숭아":["과일",5,"개",3,"#F7B7A3"],"체리":["과일",5,"g",300,"#A3182A"],"살구":["과일",5,"개",5,"#F5B461"],
  "블루베리":["과일",7,"g",200,"#4A5BA8"],"수박":["과일",7,"통",1,"#3F8F3A"],"참외":["과일",10,"개",3,"#F2D43D"]
};''')

# ---------- 2) 박스 그리기: 후보(35% 미만)는 점선 ----------
rep('''    ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    const label = `${d.ko} ${Math.round(d.score * 100)}%`, tw = ctx.measureText(label).width + 10;''',
'''    const weak = d.score < SCAN_MAIN;
    ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.setLineDash(weak ? [lw * 3, lw * 2] : []); ctx.strokeRect(x1, y1, x2 - x1, y2 - y1); ctx.setLineDash([]);
    const label = `${weak ? "후보 " : ""}${d.ko} ${Math.round(d.score * 100)}%`, tw = ctx.measureText(label).width + 10;''')

# ---------- 3) 스캔 결과 목록을 함수로 분리 + 직접 추가 ----------
rep('''function openScan(){''', '''/* v5: 스캔 결과 편집 — 인식 결과, 후보, 직접 추가를 한 목록에서 다룬다 */
const SCAN_MAIN = 0.35, SCAN_MIN = 0.15;
const SCAN_QUICK = ["오렌지","귤","딸기","포도","키위","배","라임","복숭아","계란","우유","두부","대파"];
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

function scanRow({ name = "", qty, checked = true, color = "var(--muted)", tag = "" }){
  const i = scanRowSeq++, q = qty ?? (name ? scanQty(name, 1) : 1);
  return `<li data-row="${i}">
    <input type="checkbox" ${checked ? "checked" : ""} aria-label="등록 여부">
    <span style="display:flex;align-items:center;min-width:0"><span class="sw" style="background:${color}"></span>
      <input type="text" list="masterList" value="${esc(name)}" placeholder="재료 이름" aria-label="재료 이름"></span>
    <span class="qty"><input type="number" min="0" step="any" value="${fmtQty(q)}" aria-label="수량"><span class="unit">${esc(unitOf(name))}</span></span>
    <span class="tagcell">${tag}<button class="row-x" type="button" aria-label="이 줄 지우기">×</button></span>
  </li>`;
}

function renderScanResult(groups, note){
  const main = groups.filter(g => !g.cand), cand = groups.filter(g => g.cand);
  const color = g => SCAN_COLORS[g.id % SCAN_COLORS.length];
  $("#scanResult").innerHTML = `
    ${note ? `<div class="empty" style="margin-top:12px">${note}</div>` : ""}
    <div class="label" style="margin-top:12px">등록할 재료 · 이름을 고치면 단위도 바뀝니다</div>
    <ul class="scan-list" id="scanList">
      ${main.map(g => scanRow({ name: g.ko, qty: scanQty(g.ko, g.count), checked: g.score >= 0.6, color: color(g),
        tag: `<span class="tag ${g.score >= 0.6 ? "t-ok" : "t-warn"}">${g.score >= 0.6 ? "" : "확인 필요 "}${Math.round(g.score * 100)}%</span>` })).join("")}
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

function openScan(){''')

# ---------- 4) 인식 처리: 15%까지 받아 후보로 보여주고, 0개여도 직접 추가 가능 ----------
rep('''    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true;''',
    '''    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true; scanRowSeq = 0;''')
rep('''      const r = await FridgeScan.detect(file, { minScore: 0.35, confirmBelow: 0.6 });
      await drawScan(file, r);
      status(`${r.items.length}종 찾음 · ${r.ms}ms · 60% 미만은 '확인 필요'로 꺼 두었습니다`);
      if (!r.items.length){
        $("#scanResult").innerHTML = `<div class="empty">찾은 재료가 없습니다. 재료가 크게 보이게 다시 찍거나 직접 입력하세요.</div>`;
        return;
      }''', '''      const r = await FridgeScan.detect(file, { minScore: SCAN_MIN, confirmBelow: 0.6 });
      await drawScan(file, r);
      const groups = groupScan(r), nMain = groups.filter(g => !g.cand).length, nCand = groups.length - nMain;
      status(`${nMain}종 찾음${nCand ? ` · 후보 ${nCand}종` : ""} · ${r.ms}ms · 아직 학습하지 않은 재료(오렌지, 딸기 등)는 아래에서 직접 추가하세요`);
      renderScanResult(groups, groups.length ? "" : "찾은 재료가 없습니다. 아래에서 직접 추가하거나 재료가 크게 보이게 다시 찍어 보세요.");
      return;
      /* v4 목록 (v5에서 renderScanResult로 대체) */''')
rep('''  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li")]''', '''  bindScanList();
  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li[data-row]")]''')
# 같은 재료를 두 줄로 넣었으면 합친다
rep('''    if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
    picked.forEach(p => addItem(p.name, "", p.qty));''', '''    if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
    const merged = new Map();
    picked.forEach(p => { const m = merged.get(p.name); m ? (m.qty = (m.qty || 0) + (p.qty || 0) || undefined) : merged.set(p.name, { ...p }); });
    picked.length = 0; picked.push(...merged.values());
    picked.forEach(p => addItem(p.name, "", p.qty));''')

# ---------- 5) 스타일 ----------
rep('''@container app (max-width:640px){ .scan-list li{grid-template-columns:auto minmax(0,1fr) auto} .scan-list .tagcell{grid-column:2 / -1} }''',
'''.scan-list li[data-row]{grid-template-columns:auto minmax(0,1fr) 108px 132px}
.scan-list .tagcell{display:flex;align-items:center;gap:6px;justify-content:flex-end}
.scan-list .row-x{border:0;background:transparent;color:var(--muted);font-size:18px;line-height:1;width:26px;height:26px;border-radius:8px;cursor:pointer}
.scan-list .row-x:hover{background:var(--bg);color:var(--danger)}
.scan-list li.scan-sep{display:block;background:transparent;padding:10px 2px 2px;font-size:13px;color:var(--muted)}
.scan-list li.flash{animation:rowflash .7s ease}
@keyframes rowflash{from{box-shadow:0 0 0 2px var(--accent, #4E9A3F)}to{box-shadow:0 0 0 2px transparent}}
.scan-add{margin-top:12px}
.scan-add .chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.scan-add .chip{border:1px solid var(--card-line);background:var(--card);color:inherit;border-radius:999px;padding:6px 11px;font-size:13px;cursor:pointer}
.scan-add .chip:hover{background:var(--field)}
@container app (max-width:640px){ .scan-list li, .scan-list li[data-row]{grid-template-columns:auto minmax(0,1fr) auto} .scan-list .tagcell{grid-column:2 / -1} }''')

OUT.write_text(s, encoding='utf-8')
print('written', OUT, round(OUT.stat().st_size / 1e6, 1), 'MB')
