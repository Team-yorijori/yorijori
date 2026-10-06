/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 재료 추가 */

/* ---------- 재료 추가 ---------- */
function addItem(rawName, manualDate, qty){
  const name = rawName.trim();
  if (!name) return {err:"재료 이름을 입력하세요."};
  const m = MASTER[name];
  let exp, auto, msg;
  if (manualDate){ exp = manualDate; auto = false; msg = `${name} 추가 · 소비기한 ${md(exp)} (직접 입력)`; }
  else if (m){ exp = addDays(m[1]); auto = true; msg = `${name} 추가 · 소비기한 ${md(exp)} 자동 안내 (냉장 ${m[1]}일 기준)`; }
  else { exp = addDays(7); auto = true; msg = `${name}은(는) 보관 기간 정보가 없어 7일로 잡았습니다. 내 식재료에서 고칠 수 있습니다.`; }
  fridge.push({id:uid(), name, qty: qty ?? (m ? m[3] : 1), unit: m ? m[2] : "개", reg: iso(today0()), exp, auto});
  save(); renderAll();
  return {msg};
}
