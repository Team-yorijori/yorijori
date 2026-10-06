/* 요리조리 — 첫 화면과 주소 연결 [프론트]
 * 서버가 주소마다 처음 열 화면을 정해 준다 (PageController: / → home, /fridge → fridge, /recipes/r12 → detail)
 * 화면을 바꾸면 주소도 바꿔서, 새로고침·뒤로 가기·주소 공유가 된다.
 */
const PAGE_PATH = { home: "/", fridge: "/fridge", recipes: "/recipes", dishes: "/dishes", cart: "/cart", items: "/items" };
const _goDemo = go;
// 데모의 go(page) 는 화면만 바꿨다 → 주소도 바꾼다
go = function(page, push = true){
  _goDemo(page);
  const path = page === "detail" ? "/recipes/" + encodeURIComponent(currentRecipe) : PAGE_PATH[page];
  if (push && path && location.pathname !== path) history.pushState({ page, rid: currentRecipe }, "", path);
};
window.addEventListener("popstate", e => {
  const st = e.state || {};
  if (st.page === "detail" && st.rid && RECIPES.some(r => r.id === st.rid)) { currentRecipe = st.rid; renderDetail(); }
  go(st.page || pageFromPath(), false);
});
function pageFromPath(){
  const p = location.pathname;
  return Object.keys(PAGE_PATH).find(k => PAGE_PATH[k] === p) || "home";
}

(() => {
  const cfg = window.YORIJORI || {};
  if (cfg.page === "detail" && cfg.recipeCode && RECIPES.some(r => r.id === cfg.recipeCode)) {
    currentRecipe = cfg.recipeCode; renderDetail(); go("detail", false);
  } else if (cfg.page && cfg.page !== "detail") {
    go(cfg.page, false);
  }
  history.replaceState({ page: cfg.page || "home", rid: currentRecipe }, "", location.pathname);
})();
