/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 레시피 영상 (v6) */

/* =====================================================================
 * v6-4) 레시피 영상 — 대표 영상(r.video)이 있으면 바로 재생, 없으면 검색으로 연결
 *   서비스: YouTube Data API로 레시피마다 대표 영상 ID를 한 번만 찾아 DB에 저장(하루 검색 한도 안에서 나눠서)
 * ===================================================================== */
function videoHTML(r){
  const q = encodeURIComponent(r.name + " 만들기");
  return `<div class="sec"><h2>영상으로 보기</h2>
    ${r.video ? `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(r.video)}" title="${esc(r.name)} 조리 영상" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>` : ""}
    <div class="video-links">
      <a class="vlink" href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener"><span class="yt" aria-hidden="true"></span>유튜브에서 '${esc(r.name)}' 영상 보기</a>
      <a class="vlink" href="https://www.10000recipe.com/recipe/list.html?q=${encodeURIComponent(r.name)}" target="_blank" rel="noopener">만개의레시피 사진 레시피</a>
    </div>
    <div class="note" style="margin-top:8px">새 창으로 열립니다.</div></div>`;
}
