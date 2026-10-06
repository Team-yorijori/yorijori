/* 요리조리 — 서버 API 호출 도우미 [프론트 ↔ 백]
 * 응답 형식: { ok, data, message, code } (common/response/ApiResponse.java)
 * 실패하면 message 를 담은 Error 를 던진다 → 화면에서 toast(err.message)
 *
 * 지금 화면(데모 v9 코드)은 냉장고·만든 요리·장보기를 localStorage 에 저장한다.
 * 서버로 옮길 때는 아래 순서로 store.js / dish.js / cart.js / avoid.js 의 save·load 를 Api 호출로 바꾼다.
 *   TODO(프론트) 1. 로그인한 경우 store.js load() → Api.get(API.fridge)            , addItem() → Api.post(API.fridge, { items:[…] })
 *   TODO(프론트) 2. cook.js 차감 → Api.post(API.cook(code), { servings, uses:[{name, qty}] })
 *   TODO(프론트) 3. dish.js eatDish / tossDish → Api.post(API.eat(id)) / Api.del(API.dish(id)), 통계 → Api.get(API.stats)
 *   TODO(프론트) 4. cart.js → API.cart, avoid.js → API.avoid
 *   로그인하지 않은 사람은 지금처럼 localStorage 로 둘러보게 둔다 (데모 모드)
 * API 명세: docs/api.md
 */
const API = {
  me: "/api/auth/me", login: "/api/auth/login", logout: "/api/auth/logout", signup: "/api/auth/signup",
  ingredients: q => "/api/ingredients" + (q ? "?q=" + encodeURIComponent(q) : ""),
  avoidGroups: "/api/ingredients/avoid-groups",
  fridge: "/api/fridge/items", fridgeItem: id => `/api/fridge/items/${id}`,
  recommend: (sort = "urgent", q = "", page = 0, size = 12) => `/api/recipes/recommend?sort=${sort}&q=${encodeURIComponent(q)}&page=${page}&size=${size}`,
  recipe: code => `/api/recipes/${encodeURIComponent(code)}`,
  cook: code => `/api/recipes/${encodeURIComponent(code)}/cook`,
  dishes: "/api/dishes", dish: id => `/api/dishes/${id}`, eat: id => `/api/dishes/${id}/eat`,
  stats: "/api/stats/monthly",
  cart: "/api/cart", cartItem: id => `/api/cart/${id}`, bought: id => `/api/cart/${id}/bought`,
  avoid: "/api/me/avoid", anim: "/api/me/anim",
  scanClasses: "/api/scan/classes", scanFeedback: "/api/scan/feedback"
};

const Api = (() => {
  async function req(method, url, body){
    const opt = { method, credentials: "same-origin", headers: { "Accept": "application/json" } };
    if (body !== undefined){ opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(body); }
    const res = await fetch(url, opt);
    let json = null;
    try { json = await res.json(); } catch (e) {}
    if (!res.ok || (json && json.ok === false)) {
      const err = new Error((json && json.message) || (res.status === 401 ? "로그인이 필요합니다." : `서버 응답 오류 (${res.status})`));
      err.status = res.status; err.code = json && json.code;
      throw err;
    }
    return json && "data" in json ? json.data : json;
  }
  return {
    get:   url => req("GET", url),
    post:  (url, body = {}) => req("POST", url, body),
    put:   (url, body = {}) => req("PUT", url, body),
    patch: (url, body = {}) => req("PATCH", url, body),
    del:   url => req("DELETE", url)
  };
})();
