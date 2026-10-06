/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 로그인 (서버 /api/auth 연결) */

/* 로그인 — 서버 세션 (/api/auth/login · /api/auth/logout · /api/auth/me) */
/* 데모 v1~v9 의 로그인 창(서버 없이 이메일 형식만 확인)은 아래 주석으로 남겨 둔다
/* 로그인(데모) * /
function openLogin(){
  if (user){ user = null; $("#loginBtn").textContent = "로그인"; toast("로그아웃했습니다."); return; }
  modal(`<h2>로그인</h2><div class="sub">로그인하면 내 냉장고를 어느 기기에서나 볼 수 있습니다.</div>
    <form class="form" id="loginForm" novalidate>
      <input class="field" type="email" id="lgEmail" placeholder="이메일" autocomplete="email">
      <input class="field" type="password" id="lgPw" placeholder="비밀번호 (8자 이상)" autocomplete="current-password">
      <div class="note" id="lgErr" style="color:var(--danger);min-height:18px"></div>
      <div class="actions" style="margin-top:0"><button class="btn ghost" type="button" data-close>취소</button><button class="btn strong" type="submit">로그인</button></div>
    </form>`);
  $("#loginForm").onsubmit = e => {
    e.preventDefault();
    const em = $("#lgEmail").value.trim(), pw = $("#lgPw").value;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { $("#lgErr").textContent = "이메일 형식을 확인하세요."; return; }
    if (pw.length < 8) { $("#lgErr").textContent = "비밀번호는 8자 이상입니다."; return; }
    user = em.split("@")[0]; $("#loginBtn").textContent = `${user} 님`; closeModal(); toast(`${user} 님, 환영합니다.`);
  };
}

*/

async function refreshLogin(){
  const me = await Api.get("/api/auth/me").catch(() => null);
  user = me && me.nickname ? me : null;
  $("#loginBtn").textContent = user ? `${user.nickname} 님` : "로그인";
}
function openLogin(){
  if (user){
    Api.post("/api/auth/logout").catch(() => {}).finally(() => { user = null; $("#loginBtn").textContent = "로그인"; toast("로그아웃했습니다."); });
    return;
  }
  modal(`<h2>로그인</h2><div class="sub">로그인하면 내 냉장고를 어느 기기에서나 볼 수 있습니다.</div>
    <form class="form" id="loginForm" novalidate>
      <input class="field" type="email" id="lgEmail" placeholder="이메일" autocomplete="email">
      <input class="field" type="password" id="lgPw" placeholder="비밀번호 (8자 이상)" autocomplete="current-password">
      <div class="note" id="lgErr" style="color:var(--danger);min-height:18px"></div>
      <div class="actions" style="margin-top:0"><a class="btn ghost" href="/signup" style="margin-right:auto">회원가입</a><button class="btn ghost" type="button" data-close>취소</button><button class="btn strong" type="submit">로그인</button></div>
    </form>`);
  $("#loginForm").onsubmit = async e => {
    e.preventDefault();
    const em = $("#lgEmail").value.trim(), pw = $("#lgPw").value;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { $("#lgErr").textContent = "이메일 형식을 확인하세요."; return; }
    if (pw.length < 8) { $("#lgErr").textContent = "비밀번호는 8자 이상입니다."; return; }
    try {
      const me = await Api.post("/api/auth/login", { email: em, password: pw });
      user = me; $("#loginBtn").textContent = `${me.nickname} 님`; closeModal(); toast(`${me.nickname} 님, 환영합니다.`);
    } catch (err) { $("#lgErr").textContent = err.message; }
  };
}
refreshLogin();
