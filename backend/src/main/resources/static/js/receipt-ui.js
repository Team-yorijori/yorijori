/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 영수증·주문내역 창 (tesseract.js 글자 인식 · 결과 확인) */

let ocrWorker = null, ocrStatus = () => {};
async function ensureOcr(){
  if (ocrWorker) return ocrWorker;
  ocrStatus("글자 인식기를 준비하는 중… 처음 한 번만 몇 MB를 내려받습니다");
  if (!window.Tesseract) await loadScript("https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js").catch(() => { throw new Error("글자 인식기(tesseract.js)를 불러오지 못했습니다"); });
  ocrWorker = await Tesseract.createWorker(["kor", "eng"], 1, {
    logger: m => { if (m.status === "recognizing text") ocrStatus(`글자 읽는 중… ${Math.round(m.progress * 100)}%`); }
  });
  return ocrWorker;
}
// 사진 방향(EXIF)을 바로잡고 너무 크면 줄인다. 작은 캡처는 키워서 글자를 또렷하게
async function ocrCanvas(file){
  const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
  const long = Math.max(bmp.width, bmp.height), s = long > 2400 ? 2400 / long : long < 1000 ? 1.6 : 1;
  const cv = document.createElement("canvas"); cv.width = Math.round(bmp.width * s); cv.height = Math.round(bmp.height * s);
  const ctx = cv.getContext("2d"); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.filter = "grayscale(1) contrast(1.25)"; ctx.drawImage(bmp, 0, 0, cv.width, cv.height);
  return cv;
}

function showReceiptRows(items, raw){
  scanRowSeq = 0;
  const rows = items.map(it => scanRow({ name: it.name, qty: it.qty, checked: true, color: MASTER[it.name] ? MASTER[it.name][4] : "var(--muted)",
    tag: `<span class="tag t-ok">찾음</span>`, src: it.src }));
  $("#scanResult").innerHTML = `
    ${items.length ? "" : `<div class="empty" style="margin-top:12px">재료 이름을 찾지 못했습니다. 아래 '읽은 글자 전체 보기'를 확인하고 직접 추가하세요.</div>`}
    <div class="label" style="margin-top:12px">등록할 재료 · 수량은 상품 표기(1.5kg, 30구 등)로 계산했습니다</div>
    <ul class="scan-list" id="scanList">${rows.join("")}</ul>
    <div class="scan-add">
      <button class="btn ghost" type="button" id="scanAddRow">+ 빠진 재료 직접 추가</button>
    </div>`;
  if (raw != null){ $("#rcRaw").hidden = false; $("#rcRawText").textContent = raw.trim() || "(읽은 글자가 없습니다)"; }
  $("#scanOk").disabled = false;
}

function registerRows(){
  const picked = [...document.querySelectorAll(".scan-list li[data-row]")].filter(li => li.querySelector("input[type=checkbox]").checked)
    .map(li => ({ name: li.querySelector("input[type=text]").value.trim(), qty: parseFloat(li.querySelector("input[type=number]").value) || undefined }))
    .filter(p => p.name);
  if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
  const merged = new Map();
  picked.forEach(p => { const g = merged.get(p.name); g ? (g.qty = (g.qty || 0) + (p.qty || 0) || undefined) : merged.set(p.name, { ...p }); });
  merged.forEach(p => addItem(p.name, "", p.qty));
  const names = [...merged.keys()];
  const fromCart = cartBought(names);
  showScanRecipes(names);
  if (fromCart.length) toast(`장보기 목록에 있던 ${josa(fromCart.join(", "), "을", "를")} 산 것으로 처리했습니다.`);
}

function openReceipt(){
  scanRowSeq = 0;
  modal(`<h2>영수증·주문내역으로 등록</h2>
    <div class="seg scan-mode" role="group" aria-label="등록 방법"><button type="button" id="toPhoto" aria-pressed="false">재료 사진</button><button type="button" aria-pressed="true">영수증·주문내역</button></div>
    <div class="sub" style="margin-top:10px">마트 영수증 사진이나 쿠팡·마켓컬리·네이버쇼핑 주문내역 캡처를 올리세요. 글자는 이 기기 안에서 읽고 어디에도 보내지 않습니다.</div>
    <label class="drop" for="rcFile" id="rcDrop">영수증·주문내역 사진 고르기</label>
    <input type="file" id="rcFile" accept="image/*" hidden>
    <details class="rc-paste" id="rcPaste"><summary>주문내역 글자를 복사해서 붙여넣기 (더 정확)</summary>
      <textarea class="field rc-text" id="rcText" rows="5" placeholder="주문내역 화면에서 상품 목록을 길게 눌러 복사한 뒤 붙여넣으세요.&#10;예) 국내산 양파 1.5kg 1개  4,980원&#10;    무항생제 특란 30구  8,990원"></textarea>
      <div class="row" style="justify-content:flex-end;margin-top:8px"><button class="btn" type="button" id="rcParse">글자에서 재료 찾기</button></div>
    </details>
    <div class="scan-status" id="scanStatus"></div>
    <div id="scanResult"></div>
    <details class="rc-raw" id="rcRaw" hidden><summary>읽은 글자 전체 보기</summary><pre id="rcRawText"></pre></details>
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="scanOk" disabled>선택한 재료 등록</button></div>`);
  const status = (t, err) => { const el = $("#scanStatus"); if (!el) return; el.textContent = t; el.className = "scan-status" + (err ? " err" : ""); };
  ocrStatus = status;
  $("#toPhoto").onclick = openScan;
  bindScanList();
  $("#scanOk").onclick = registerRows;
  $("#rcParse").onclick = () => {
    const t = $("#rcText").value;
    if (!t.trim()){ status("붙여넣은 글자가 없습니다.", true); return; }
    const items = parseReceipt(t);
    status(`${items.length}가지 재료를 찾았습니다 · 이름과 수량을 확인하세요`);
    showReceiptRows(items, null);
  };
  $("#rcFile").onchange = async e => {
    const file = e.target.files[0]; if (!file) return;
    $("#rcDrop").textContent = "다른 사진으로 바꾸려면 누르세요";
    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true; $("#rcRaw").hidden = true;
    try {
      const w = await ensureOcr();
      status("글자 읽는 중…");
      const t0 = performance.now();
      const { data } = await w.recognize(await ocrCanvas(file));
      const items = parseReceipt(data.text);
      status(`${items.length}가지 재료를 찾았습니다 · ${((performance.now() - t0) / 1000).toFixed(1)}초 · 영수증 글자는 틀릴 수 있으니 확인하세요`);
      showReceiptRows(items, data.text);
    } catch (err) {
      status("글자를 읽지 못했습니다: " + (err.message || err) + " · 주문내역 글자를 붙여넣어 보세요", true);
      $("#rcPaste").open = true;
    }
  };
}
