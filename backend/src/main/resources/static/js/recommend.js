/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 레시피 매칭 · 추천 점수 (서버 RecommendService 와 같은 계산) */

/* ---------- 매칭 ---------- */
function match(r){
  const req0 = r.ings.filter(i => !i[2]);
  const req = req0.length ? req0 : r.ings, opt = req0.length ? r.ings.filter(i => i[2]) : [];
  const have = req.filter(i => stockQty(i[0]) > 0), missing = req.filter(i => stockQty(i[0]) <= 0);
  const used = r.ings.filter(i => stockQty(i[0]) > 0);
  const ratio = have.length / req.length;
  let urgent = null;
  used.forEach(i => { const d = soonest(i[0]); if (urgent == null || d < urgent.d) urgent = {name:i[0], d}; });
  const bonus = !urgent ? 0 : urgent.d <= 1 ? 40 : urgent.d <= 3 ? 25 : urgent.d <= 5 ? 10 : 0;
  // v8: 최근 2일 안에 만든 요리는 15점 낮춘다 (같은 요리 연속 추천 방지)
  const recent = recentCookDays(r.id);
  return {r, have, missing, opt, ratio, urgent, recent, score: ratio*60 + bonus - (recent != null && recent <= 2 ? 15 : 0)};
}
function ranked(){
  const list = RECIPES.map(match).filter(m => m.ratio > 0);
  if (sortMode === "urgent") list.sort((a,b) => b.score - a.score || a.missing.length - b.missing.length);
  else list.sort((a,b) => a.missing.length - b.missing.length || b.score - a.score);
  return list;
}
