/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 재료별 인식 기준 · 헷갈리는 재료 (v9) — 값은 AI 파트가 정한다 (/api/scan/classes 와 같다) */

/* =====================================================================
 * v9-1) 재료별 인식 기준 — v4 모델 평가(mAP50)로 정한다
 *   잘 맞히는 재료는 50%부터 자동 체크, 약한 재료는 70% 이상이어야 자동 체크
 * ===================================================================== */
const SCAN_AUTO = {
  // 약함 (mAP50 0.85 미만, 또는 검증 데이터가 거의 없음)
  "오렌지": .7, "치즈": .7, "대파": .7, "고추": .7, "토마토": .7, "계란": .65, "두부": .7,
  // 보통 (0.85~0.90)
  "당근": .6, "브로콜리": .6, "라임": .6, "오이": .6, "무": .6,
  // AI Hub 합성으로만 배운 재료 — 검증 점수는 높지만 실제 사진은 아직 확인 전이라 조금 높게
  "배추": .6, "배": .6, "귤": .6
};
const autoOf = ko => SCAN_AUTO[ko] ?? .5;
// 서로 헷갈리기 쉬운 재료 → 결과 줄에 "혹시 ○○?" 버튼
const SCAN_CONFUSE = {
  // 감은 아직 학습 안 함 → 귤·오렌지로 잡히는 경우가 많다
  "오렌지": ["귤", "레몬", "감"], "귤": ["오렌지", "감"], "레몬": ["라임", "오렌지"], "라임": ["레몬"],
  "양배추": ["배추"], "배추": ["양배추"], "애호박": ["오이"], "오이": ["애호박"],
  "감자": ["고구마"], "고구마": ["감자"], "토마토": ["파프리카"], "파프리카": ["토마토"], "치즈": ["두부"], "두부": ["치즈"]
};
function scoreTag(g){
  const ok = g.score >= autoOf(g.ko), alts = SCAN_CONFUSE[g.ko] || [];
  const av = isAvoided(g.ko);
  return `<span class="tag ${ok ? "t-ok" : "t-warn"}" data-score>${ok ? "" : "확인 필요 "}${Math.round(g.score * 100)}%</span>`
    + (av ? `<span class="tag t-danger">못 먹는 재료</span>` : "")
    + alts.map(a => `<button type="button" class="alt" data-alt="${esc(a)}" title="이름을 ${esc(a)}(으)로 바꾸기">${esc(a)}?</button>`).join("");
}
document.addEventListener("click", e => {
  const b = e.target.closest(".scan-list .alt"); if (!b) return;
  const li = b.closest("li"), inp = li.querySelector("input[type=text]"), old = inp.value.trim();
  inp.value = b.dataset.alt; b.dataset.alt = old; b.textContent = old + "?";
  inp.dispatchEvent(new Event("change", { bubbles: true }));
});
