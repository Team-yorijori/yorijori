/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 소비기한·수량 수정 창 (v6) */

/* =====================================================================
 * v6-2) 소비기한·수량 수정 창 — 재료 칩, 임박 목록, 식재료 표 이름을 누르면 열린다
 * ===================================================================== */
function openEdit(id){
  const f = fridge.find(x => x.id === id); if (!f) return;
  const m = MASTER[f.name];
  const autoExp = m ? iso(parse(f.reg).getTime() + m[1] * DAY) : null;
  modal(`<h2>${esc(f.name)}</h2>
    <div class="sub">${f.auto && m ? `등록일(${md(f.reg)})에 냉장 보관 ${m[1]}일을 더해 자동으로 안내한 날짜입니다. 보관 상태에 따라 다를 수 있으니 참고용으로 보고, 포장에 날짜가 있으면 그 날짜로 고치세요.`
      : f.auto ? `보관 기간 정보가 없어 7일로 잡아 둔 날짜입니다. 실제 날짜로 고치세요.` : `직접 입력한 날짜입니다.`}</div>
    <div class="ed-grid">
      <label class="label" for="edExp">소비기한</label>
      <input class="field" type="date" id="edExp" value="${f.exp}">
      <span></span>
      <div class="quick" id="edQuick">
        <button type="button" data-add="-1">-1일</button><button type="button" data-add="1">+1일</button>
        <button type="button" data-add="3">+3일</button><button type="button" data-add="7">+7일</button>
        <button type="button" data-set="today">오늘</button>
        ${autoExp ? `<button type="button" data-set="auto">자동 안내 날짜(${md(autoExp)})</button>` : ""}
      </div>
      <span></span>
      <div class="note" id="edPreview"></div>
      <label class="label" for="edQty">수량</label>
      <div class="ed-qty"><input class="field" type="number" id="edQty" min="0" step="any" value="${fmtQty(f.qty)}"><span class="sub">${esc(f.unit)}</span></div>
    </div>
    <div class="actions"><button class="btn danger" type="button" id="edDel" style="margin-right:auto">삭제</button><button class="btn ghost" data-close>취소</button><button class="btn strong" id="edOk">저장</button></div>`);
  const inp = $("#edExp");
  const preview = () => { $("#edPreview").innerHTML = inp.value ? `${ddayTag(inp.value)} ${inp.value === autoExp ? "· 자동 안내 날짜" : "· 직접 고친 날짜"}` : ""; };
  preview(); inp.addEventListener("input", preview);
  $("#edQuick").onclick = e => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.dataset.add) inp.value = addDays(+b.dataset.add, inp.value ? parse(inp.value) : today0());
    if (b.dataset.set === "today") inp.value = iso(today0());
    if (b.dataset.set === "auto") inp.value = autoExp;
    preview();
  };
  $("#edDel").onclick = () => { logAdd({ t: "tossIng", name: f.name }); if (animOn()) playTrash($(".modal h2").getBoundingClientRect(), f.name); fridge = fridge.filter(x => x.id !== id); save(); closeModal(); renderAll(); toast(`${josa(f.name, "을", "를")} 냉장고에서 뺐습니다.`); };
  $("#edOk").onclick = () => {
    if (!inp.value){ toast("소비기한 날짜를 고르세요."); return; }
    const before = f.exp;
    f.exp = inp.value; f.auto = !!autoExp && inp.value === autoExp;
    f.qty = Math.max(0, parseFloat($("#edQty").value) || 0);
    fridge = fridge.filter(x => x.qty > 0); save(); closeModal(); renderAll();
    toast(before === f.exp ? `${f.name} 수량을 고쳤습니다.` : `${f.name} 소비기한을 ${md(f.exp)}로 고쳤습니다.`);
  };
}
