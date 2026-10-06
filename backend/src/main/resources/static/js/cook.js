/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 요리 완료 → 재료 차감 확인 창 */

/* 요리 완료 → 차감 확인 */
function openDeduct(r){
  const used = r.ings.filter(i => stockQty(i[0]) > 0);
  // v8: 냉장고에 재료가 없어도 만든 요리는 보관할 수 있게 창을 연다
  modal(`<h2>요리 완료</h2><div class="sub">${used.length ? "실제로 쓴 양으로 고친 뒤 차감하세요. 0으로 두면 차감하지 않습니다." : "냉장고에서 뺄 재료는 없습니다. 만든 요리만 보관합니다."}</div>
    <ul class="det deduct">${used.map(([name, amt]) => {
      const have = stockQty(name), unit = MASTER[name] ? MASTER[name][2] : "";
      return `<li><span>${esc(name)} <span class="note">보유 ${fmtQty(have)}${unit}</span></span><input type="number" min="0" step="any" value="${fmtQty(Math.min(amt, have))}" data-name="${esc(name)}" id="d-${esc(name)}" aria-label="${esc(name)} 사용량"><span class="note">${unit}</span></li>`;
    }).join("")}</ul>
    <div class="serv-row"><label for="cookServ">만든 양</label><input type="number" id="cookServ" min="1" max="20" step="1" value="${r.serv || 2}"> 인분
      <span class="note">만든 요리에 보관하고, 먹을 때마다 1인분씩 줄어듭니다 · 보관 ${dishDays(r)}일(참고용)</span></div>
    <div class="actions"><button class="btn ghost" data-close>취소</button><button class="btn strong" id="deductOk">${used.length ? "차감하고 보관" : "보관하기"}</button></div>`);
  $("#deductOk").onclick = () => {
    // v8: 인분, 이번 요리로 살린 임박 재료(D-3 이내)
    const servN = Math.max(1, Math.min(20, parseInt($("#cookServ").value, 10) || r.serv || 1));
    const savedUrgent = [...document.querySelectorAll(".deduct input")].filter(i => (parseFloat(i.value) || 0) > 0 && soonest(i.dataset.name) <= 3).map(i => i.dataset.name);
    let n = 0;
    document.querySelectorAll(".deduct input").forEach(inp => {
      let need = Math.max(0, parseFloat(inp.value) || 0); if (!need) return; n++;
      stock(inp.dataset.name).sort((a,b) => dday(a.exp) - dday(b.exp)).forEach(f => { const take = Math.min(f.qty, need); f.qty = Math.round((f.qty - take)*100)/100; need -= take; });
    });
    fridge = fridge.filter(f => f.qty > 0); save(); closeModal(); renderAll();
    const doneMsg = n ? `재료 ${n}종을 냉장고에서 차감했습니다. 다 쓴 재료는 목록에서 빠집니다.` : "차감한 재료가 없습니다.";
    // v7: 요리 → 먹기 애니메이션이 끝난 뒤 안내 (v8부터는 아래 보관 흐름을 쓴다)
    // if (n && animOn()) playCook(r).then(() => toast(doneMsg)); else toast(doneMsg);
    // v8: 만든 요리 보관 → 보관함에 담는 애니메이션 → 안내
    const dish = makeDish(r, servN, savedUrgent);
    const keepMsg = `${r.name} ${servN}인분을 만든 요리에 보관했습니다${n ? ` · 재료 ${n}종 차감` : ""}${savedUrgent.length ? ` · 임박 재료 ${savedUrgent.length}개 살림` : ""}`;
    if (animOn()) playCookStore(r, dish).then(() => toast(keepMsg)); else toast(keepMsg);
  };
}
