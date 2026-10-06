/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 예시 스캔 결과 (모델을 못 불러올 때 예비용) */

/* 스캔(데모: 업로드한 사진 대신 예시 인식 결과를 보여줌) — v3부터는 모델을 못 불러올 때만 쓰는 예비용 */
function openScanDemo(){
  modal(`<h2>재료 사진 스캔</h2><div class="sub">냉장고 속 사진을 올리면 재료를 찾아냅니다. 결과를 확인하고 고친 뒤 등록하세요.</div>
    <label class="drop" for="scanFile" id="dropBox">사진을 선택하세요 (JPG, PNG)</label>
    <input type="file" id="scanFile" accept="image/*" hidden>
    <div id="scanResult"></div>
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="scanOk" disabled>선택한 재료 등록</button></div>`);
  $("#scanFile").onchange = e => {
    const file = e.target.files[0]; if (!file) return;
    const rd = new FileReader();
    rd.onload = () => { $("#dropBox").innerHTML = `<img src="${rd.result}" alt="올린 냉장고 사진">다른 사진으로 바꾸려면 누르세요`; };
    rd.readAsDataURL(file);
    $("#scanResult").innerHTML = `<div class="note" style="margin-top:12px">재료를 찾는 중…</div>`;
    setTimeout(() => {
      const pool = ["양배추","계란","우유","당근","버섯","두부","대파","토마토","치즈","어묵","시금치","콩나물"];
      const seedN = file.size % 997, picks = [];
      for (let k = 0; picks.length < 4; k++){ const n = pool[(seedN + k*5) % pool.length]; if (!picks.includes(n)) picks.push(n); }
      const confs = [96, 91, 82, 63];
      $("#scanResult").innerHTML = `<div class="label" style="margin-top:14px">인식 결과 ${picks.length}개 · 이름을 고칠 수 있습니다</div>
        <ul class="det">${picks.map((n,i) => `<li><input type="checkbox" id="ck${i}" ${confs[i] >= 70 ? "checked" : ""} aria-label="등록 여부"><input type="text" data-ac autocomplete="off" value="${n}" id="nm${i}" aria-label="재료 이름">
          <span class="tag ${confs[i] >= 70 ? "t-ok" : "t-warn"}">${confs[i] >= 70 ? confs[i]+"%" : "확인 필요 "+confs[i]+"%"}</span></li>`).join("")}</ul>
        <div class="note" style="margin-top:8px">데모에서는 예시 인식 결과를 보여줍니다. 신뢰도 70% 미만은 기본으로 꺼져 있습니다.</div>`;
      $("#scanOk").disabled = false;
    }, 900);
  };
  $("#scanOk").onclick = () => {
    const names = [...document.querySelectorAll(".det li")].filter(li => li.querySelector("input[type=checkbox]").checked).map(li => li.querySelector("input[type=text]").value.trim()).filter(Boolean);
    names.forEach(n => addItem(n));
    closeModal(); toast(names.length ? `${names.join(", ")} 등록 · 소비기한을 자동으로 안내했습니다.` : "선택한 재료가 없습니다.");
  };
}
