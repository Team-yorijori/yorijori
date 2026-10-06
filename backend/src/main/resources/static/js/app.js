/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 이벤트 연결 */

/* ---------- 이벤트 ---------- */
$("#masterList").innerHTML = Object.keys(MASTER).map(n => `<option value="${n}">`).join("");
document.addEventListener("click", e => {
  const g = e.target.closest("[data-go]"); if (g){ go(g.dataset.go); return; }
  const d = e.target.closest("[data-del]"); if (d){ const it = fridge.find(f => f.id === d.dataset.del); fridge = fridge.filter(f => f.id !== d.dataset.del); save(); renderAll(); if (it) toast(`${josa(it.name, "을", "를")} 냉장고에서 뺐습니다.`); return; }
  const o = e.target.closest("[data-open]"); if (o){ currentRecipe = o.dataset.open; renderDetail(); go("detail"); return; }
  const s = e.target.closest("[data-sort]"); if (s){ sortMode = s.dataset.sort; renderRecipes(); }
});
$("#homeForm").onsubmit = e => { e.preventDefault(); const r = addItem($("#homeInput").value); $("#homeHint").textContent = r.err || r.msg; if (!r.err) $("#homeInput").value = ""; };
$("#fridgeForm").onsubmit = e => { e.preventDefault(); const r = addItem($("#fridgeInput").value, $("#fridgeDate").value); $("#fridgeHint").textContent = r.err || r.msg; if (!r.err){ $("#fridgeInput").value = ""; $("#fridgeDate").value = ""; } };
$("#itemRows").addEventListener("change", e => {
  const q = e.target.dataset.qty, x = e.target.dataset.exp;
  if (q){ const f = fridge.find(f => f.id === q); f.qty = Math.max(0, parseFloat(e.target.value) || 0); }
  if (x && e.target.value){ const f = fridge.find(f => f.id === x); f.exp = e.target.value; f.auto = false; }
  fridge = fridge.filter(f => f.qty > 0); save(); renderAll();
});
$("#resetBtn").onclick = () => { fridge = seed(); save(); renderAll(); toast("예시 데이터로 되돌렸습니다."); };
$("#scanBtn").onclick = openScan;
$("#recSearch").addEventListener("input", e => { recQuery = e.target.value; recLimit = 12; renderRecipes(); });
$("#recMore").onclick = () => { recLimit += 12; renderRecipes(); };
$("#tabScan").onclick = openScan;
$("#loginBtn").onclick = openLogin;

/* ---------- v9 이벤트 ---------- */
$("#avoidBtn").onclick = openAvoid;
renderRecipes();

/* ---------- v8 이벤트 ---------- */
$("#dishGrid").addEventListener("click", e => {
  const a = e.target.closest("[data-eat]"), t = e.target.closest("[data-toss]");
  if (a) eatDish(a.dataset.eat, a.closest(".dish"));
  if (t) tossDish(t.dataset.toss, t.closest(".dish"));
});
// 냉장고 재료를 버리면 기록 (칩 ×, 식재료 표 '삭제')
document.addEventListener("click", e => {
  const d = e.target.closest("[data-del]"); if (!d) return;
  const it = fridge.find(f => f.id === d.dataset.del); if (it) logAdd({ t: "tossIng", name: it.name });
}, true);

/* ---------- v7 이벤트 ---------- */
setAnim(animPref, false);
$("#animBtn").onclick = () => setAnim(!animPref, true);
// 냉장고 재료 삭제(칩 ×, 식재료 표 '삭제')는 지우기 전에 위치를 잡아 쓰레기통으로 날린다
document.addEventListener("click", e => {
  const d = e.target.closest("[data-del]"); if (!d || !animOn()) return;
  const it = fridge.find(f => f.id === d.dataset.del); if (!it) return;
  playTrash((d.closest(".chip, tr") || d).getBoundingClientRect(), it.name);
}, true);

/* ---------- v6 이벤트 ---------- */
document.addEventListener("click", e => {
  const ed = e.target.closest("[data-edit]"); if (ed){ e.stopPropagation(); openEdit(ed.dataset.edit); }
}, true);
$("#fridgeScan").onclick = openScan;
$("#fridgeReceipt").onclick = openReceipt;
$("#itemSearch").addEventListener("input", e => { itemQuery = e.target.value; renderItems(); });
$("#cartForm").onsubmit = e => {
  e.preventDefault();
  const name = $("#cartInput").value.trim(), target = parseInt($("#cartTarget").value, 10) || null;
  if (!name){ $("#cartHint").textContent = "살 재료 이름을 입력하세요."; return; }
  cartAdd([name], null, target); $("#cartHint").textContent = "";
  $("#cartInput").value = ""; $("#cartTarget").value = "";
};
$("#cartList").addEventListener("change", e => {
  const t = e.target.dataset.target, w = e.target.dataset.watch;
  if (t){ const c = cart.find(c => c.id === t); c.target = parseInt(e.target.value, 10) || null; saveCart(); toast(c.target ? `${c.name} 목표가 ${c.target.toLocaleString()}원` : `${c.name} 목표가를 지웠습니다.`); }
  if (w){ const c = cart.find(c => c.id === w); c.watch = e.target.checked; saveCart(); }
});
$("#cartList").addEventListener("click", e => {
  const b = e.target.closest("[data-bought]"), d = e.target.closest("[data-cartdel]");
  if (b){ const c = cart.find(c => c.id === b.dataset.bought); cart = cart.filter(x => x !== c); saveCart(); addItem(c.name); renderCart(); const f = fridge[fridge.length - 1]; toast(`${josa(c.name, "을", "를")} 냉장고에 넣었습니다 · 소비기한 ${md(f.exp)}${f.auto ? " 자동 안내" : ""}`); }
  if (d){ cart = cart.filter(x => x.id !== d.dataset.cartdel); saveCart(); renderCart(); }
});
renderCart();
