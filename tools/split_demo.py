"""
데모 단일 HTML(v9) → Spring 프로젝트의 templates / static/css / static/js 로 나눈다.
  python tools/split_demo.py demo/요리조리_데모_v9.html backend/src/main/resources

원칙
- 데모 코드를 지우지 않고 원래 순서대로 잘라 파일만 나눈다 (전역 변수·함수 그대로, 일반 <script> 로 순서대로 불러온다)
- 바뀌는 곳만 손댄다: 모델을 base64 대신 /models/fridge.onnx 에서 받기, 로그인은 /api/auth, 주소(/fridge …)와 화면 연결
"""
import re, sys
from pathlib import Path

SRC = Path(sys.argv[1]); RES = Path(sys.argv[2])
html = SRC.read_text(encoding='utf-8')
T = RES / 'templates'; CSS = RES / 'static/css'; JS = RES / 'static/js'
for d in [T / 'fragments', T / 'pages', T / 'auth', CSS, JS / 'ai']: d.mkdir(parents=True, exist_ok=True)

def between(s, a, b, inclusive_a=True):
    i = s.index(a); j = s.index(b, i + len(a))
    return s[i if inclusive_a else i + len(a): j]

HEAD = '/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */\n'

# ---------------------------------------------------------------- CSS
style = between(html, '<style>\n/* 레이아웃', '</style>', True)[len('<style>\n'):]
css_parts = [
    ('base.css',          '/* 레이아웃', '공통 레이아웃 · 상단바 · 홈 · 냉장고 · 레시피 · 상세 · 표 · 모달/토스트'),
    ('preview.css',       '/* ---------- PC / 모바일 미리보기 전환', 'PC/모바일 미리보기 프레임 + 컨테이너 기준 반응형'),
    ('tabbar.css',        '/* ---------- 모바일 하단 탭바', '모바일 하단 탭바'),
    ('recipe.css',        '/* ---------- v4: 레시피 검색', '레시피 검색 · 더 보기 (v4)'),
    ('scan.css',          '/* ---------- v3: 실제 스캔', '재료 사진 스캔 창 (v3·v5)'),
    ('autocomplete.css',  '/* ---------- v6 ---------- */', '초성 자동완성 (v6) · 재료 분량 줄바꿈 수정'),
    ('fridge-edit.css',   '/* 재료 칩 → 수정 */', '소비기한·수량 수정 창 (v6)'),
    ('receipt.css',       '/* 등록 방법 전환 · 영수증 */', '영수증·주문내역 (v6)'),
    ('video.css',         '/* 레시피 영상 */', '레시피 영상 (v6)'),
    ('cart.css',          '/* 장보기 */', '장보기 (v6)'),
    ('anim.css',          '/* ---------- v7: 애니메이션', '애니메이션 (v7)'),
    ('dish.css',          '/* ---------- v8: 만든 요리', '만든 요리 (v8)'),
    ('scan-avoid.css',    '/* ---------- v9 ---------- */', '여러 장 스캔 · 대안 버튼 · 못 먹는 재료 (v9)'),
]
css_files = []
for k, (name, start, desc) in enumerate(css_parts):
    i = style.index(start)
    j = style.index(css_parts[k + 1][1]) if k + 1 < len(css_parts) else len(style)
    body = style[i:j]
    if name == 'base.css':
        body = '[hidden]{display:none!important}\nbody{margin:0}\nimg{max-width:100%}\n\n' + body
    (CSS / name).write_text(HEAD + f'/* {desc} — 순서대로 불러온다 (뒤 파일이 앞 파일을 덮어쓴다) */\n\n' + body.rstrip() + '\n', encoding='utf-8')
    css_files.append(name)

# ---------------------------------------------------------------- JS
lib = between(html, '<script>\n/*\n * fridge-scan.js', '</script>', True)[len('<script>\n'):]
(JS / 'ai/fridge-scan.js').write_text(lib.rstrip() + '\n', encoding='utf-8')

main = between(html, '<script>\n/* ---------- 기준 데이터', '\n</script>', True)[len('<script>\n'):]

def block_start(marker):
    """' * v6-1)' 처럼 큰 머리 주석 안의 글자면 그 주석 시작(/* ===)까지 거슬러 올라간다"""
    i = main.index(marker)
    if marker.startswith(' * '):
        i = main.rindex('/* =====', 0, i)
    return i

js_parts = [
    ('data.js',        '/* ---------- 기준 데이터', '재료 기준표(MASTER) · 데모 레시피 · 레시피 데이터 읽기'),
    ('util.js',        '/* ---------- 날짜 유틸', '날짜 · 숫자 · 글자 도우미'),
    ('store.js',       '/* ---------- 상태 ---------- */', '냉장고 상태 (지금은 localStorage. TODO: api.js 로 서버 저장)'),
    ('fridge.js',      '/* ---------- 재료 추가', '재료 추가'),
    ('recommend.js',   '/* ---------- 매칭', '레시피 매칭 · 추천 점수 (서버 RecommendService 와 같은 계산)'),
    ('plate.js',       '/* ---------- 접시 그림', '접시 그림 (SVG)'),
    ('render.js',      '/* ---------- 렌더', '화면 그리기 (홈 · 냉장고 · 레시피 · 상세 · 식재료)'),
    ('ui.js',          '/* ---------- 이동', '화면 이동 · 토스트 · 모달'),
    ('cook.js',        '/* 요리 완료 → 차감 확인 */', '요리 완료 → 재료 차감 확인 창'),
    ('scan-demo.js',   '/* 스캔(데모:', '예시 스캔 결과 (모델을 못 불러올 때 예비용)'),
    ('scan.js',        '/* ---------- v3~: 실제 재료 인식', '재료 사진 스캔 창 (모델 불러오기 · 결과 편집 · 등록 후 추천)'),
    ('choseong.js',    ' * v6-1)', '초성 검색 · 자동완성 (v6)'),
    ('edit.js',        ' * v6-2)', '소비기한·수량 수정 창 (v6)'),
    ('ai/receipt.js',  ' * v6-3)', '[AI] 영수증·주문내역 글자 → 재료 (상품명 규칙 · 수량 계산)'),
    ('receipt-ui.js',  'let ocrWorker = null', '영수증·주문내역 창 (tesseract.js 글자 인식 · 결과 확인)'),
    ('video.js',       ' * v6-4)', '레시피 영상 (v6)'),
    ('cart.js',        ' * v6-5)', '장보기 · 최저가 안내 (v6)'),
    ('anim.js',        ' * v7)', '애니메이션: 요리·버리기 · On/Off (v7)'),
    ('dish.js',        ' * v8)', '만든 요리 보관함 · 먹기/버리기 애니메이션 · 요리 기록 (v8)'),
    ('scan-rules.js',  ' * v9-1)', '재료별 인식 기준 · 헷갈리는 재료 (v9) — 값은 AI 파트가 정한다 (/api/scan/classes 와 같다)'),
    ('scan-multi.js',  ' * v9-2)', '여러 장 이어서 스캔 (v9)'),
    ('avoid.js',       ' * v9-3)', '못 먹는 재료 · 알레르기 (v9)'),
    ('auth.js',        '/* 로그인(데모) */', '로그인 (서버 /api/auth 연결)'),
    ('app.js',         '/* ---------- 이벤트 ---------- */', '이벤트 연결'),
    ('preview.js',     '/* PC / 모바일 미리보기 전환 */', 'PC/모바일 미리보기 · 프레임 크기 조절 · 첫 화면 그리기'),
]
starts = [block_start(m) for _, m, _ in js_parts]
assert starts == sorted(starts), '순서가 어긋났다'
js = {}
for k, (name, m, desc) in enumerate(js_parts):
    j = starts[k + 1] if k + 1 < len(js_parts) else len(main)
    js[name] = [desc, main[starts[k]:j]]

def rep(name, a, b):
    assert a in js[name][1], (name, a[:60])
    js[name][1] = js[name][1].replace(a, b, 1)

# 1) 모델: base64 → /models/fridge.onnx, 클래스 → /models/classes.json
rep('scan.js', '''    const b64 = document.getElementById("fridgeModel").textContent.trim();
    const buf = await (await fetch("data:application/octet-stream;base64," + b64)).arrayBuffer();
    return FridgeScan.load({ model: buf, classes: SCAN_CLASSES, wasmPaths: ORT_CDN });''',
'''    // 데모: HTML 안의 base64 모델을 썼다
    // const b64 = document.getElementById("fridgeModel").textContent.trim();
    // const buf = await (await fetch("data:application/octet-stream;base64," + b64)).arrayBuffer();
    // Spring: static/models/ 의 파일을 받는다 (브라우저가 캐시하므로 두 번째부터 빠르다)
    const cfg = window.YORIJORI || {};
    const res = await fetch(cfg.modelUrl || "/models/fridge.onnx");
    if (!res.ok) throw new Error("모델 파일이 없습니다 (static/models/fridge.onnx)");
    const buf = await res.arrayBuffer();
    const classes = await fetch(cfg.classesUrl || "/models/classes.json").then(r => r.ok ? r.json() : SCAN_CLASSES).catch(() => SCAN_CLASSES);
    return FridgeScan.load({ model: buf, classes, wasmPaths: ORT_CDN });''')

# 2) josa 는 여러 파일에서 쓰므로 util.js 로 옮긴다
JOSA = '''// 받침에 따라 을/를, 이/가 고르기
const josa = (w, a, b) => { const c = String(w).slice(-1).charCodeAt(0) - 0xAC00; return w + (c >= 0 && c < 11172 && c % 28 ? a : b); };'''
rep('ai/receipt.js', JOSA, '// josa(받침에 따라 을/를) 는 여러 화면에서 쓰므로 util.js 로 옮겼다')
js['util.js'][1] = js['util.js'][1].rstrip() + '\n\n' + JOSA + '\n\n'

# 3) 로그인: 데모(이메일만 확인) → 서버 /api/auth
old_login = js['auth.js'][1]
js['auth.js'][1] = '''/* 로그인 — 서버 세션 (/api/auth/login · /api/auth/logout · /api/auth/me) */
/* 데모 v1~v9 의 로그인 창(서버 없이 이메일 형식만 확인)은 아래 주석으로 남겨 둔다
''' + old_login.replace('*/', '* /') + '''*/

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
    if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(em)) { $("#lgErr").textContent = "이메일 형식을 확인하세요."; return; }
    if (pw.length < 8) { $("#lgErr").textContent = "비밀번호는 8자 이상입니다."; return; }
    try {
      const me = await Api.post("/api/auth/login", { email: em, password: pw });
      user = me; $("#loginBtn").textContent = `${me.nickname} 님`; closeModal(); toast(`${me.nickname} 님, 환영합니다.`);
    } catch (err) { $("#lgErr").textContent = err.message; }
  };
}
refreshLogin();
'''

for name, (desc, body) in js.items():
    (JS / name).write_text(HEAD + f'/* {desc} */\n\n' + body.rstrip() + '\n', encoding='utf-8')

# ---------------------------------------------------------------- 템플릿
body = between(html, '<body>\n', '\n<datalist id="masterList">', False)
header = between(body, '<header class="bar">', '</header>', True) + '</header>'
mainhtml = between(body, '<main>\n', '\n</main>', False)
tabbar = between(body, '<nav class="tabbar"', '</nav>', True) + '</nav>'
grips = between(body, '<div class="grip grip-l"', '<div class="app" id="app">', True).rstrip()
after_app = body[body.index('<div class="size-panel"'):].rstrip()

def dedupe_attrs(s):
    # 같은 속성이 두 번 있으면 Thymeleaf(AttoParser)가 거부할 수 있다 → 뒤엣것을 지운다
    return re.sub(r'(autocomplete="off")([^>]*?) autocomplete="off"', r'\1\2', s)

def frag(path, name, content, note):
    content = dedupe_attrs(content)
    (T / path).write_text(f'<!-- {note} -->\n<!DOCTYPE html>\n<html xmlns:th="http://www.thymeleaf.org" lang="ko">\n<body>\n' + content + '\n</body>\n</html>\n', encoding='utf-8')

frag('fragments/header.html', 'header', header.replace('<header class="bar">', '<header class="bar" th:fragment="header">', 1),
     '상단바: 로고 · 메뉴 · 스캔 · 애니 On/Off · 로그인 [프론트]')
frag('fragments/tabbar.html', 'tabbar', tabbar.replace('<nav class="tabbar"', '<nav class="tabbar" th:fragment="tabbar"', 1),
     '모바일 하단 탭: 냉장고 · 레시피 · [스캔] · 만든 요리 · 장보기 [프론트]')
frag('fragments/preview.html', 'preview',
     '<th:block th:fragment="grips">\n' + grips + '\n</th:block>\n\n<th:block th:fragment="panel">\n' + after_app + '\n</th:block>',
     'PC/모바일 미리보기 (데모 발표용 도구). 실제 서비스에서 빼려면 index.html 에서 이 두 조각을 지운다 [프론트]')

sections = re.findall(r'(  <!-- ([^\n]*?) -->\n  <section data-page="(\w+)"(.*?)\n  </section>)', mainhtml, re.S)
pages = []
for whole, comment, page, _ in sections:
    sec = whole[whole.index('<section'):]
    sec = sec.replace(f'<section data-page="{page}"', f'<section data-page="{page}" th:fragment="page"', 1)
    frag(f'pages/{page}.html', 'page', '  ' + sec, f'{comment.strip()} 화면 [프론트]')
    pages.append(page)
assert pages == ['home', 'fridge', 'recipes', 'detail', 'dishes', 'cart', 'items'], pages

title = '요리조리'
links = '\n'.join(f'<link rel="stylesheet" th:href="@{{/css/{c}}}" href="/css/{c}">' for c in css_files)
order = ['ai/fridge-scan.js', 'api.js'] + list(js.keys()) + ['init.js']
scripts = '\n'.join(f'<script th:src="@{{/js/{n}}}" src="/js/{n}"></script>' for n in order)
index = f'''<!DOCTYPE html>
<!-- 요리조리 — 한 페이지 안에서 화면을 바꾼다 (데모 v9 와 같은 구조). 화면별 HTML 은 pages/*.html 조각 -->
<html xmlns:th="http://www.thymeleaf.org" lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap">
{links}
</head>
<body>

<div class="frame" id="frame">
<th:block th:replace="~{{fragments/preview :: grips}}"></th:block>
<div class="app" id="app">
<header th:replace="~{{fragments/header :: header}}"></header>

<main>
''' + '\n'.join(f'  <section th:replace="~{{pages/{p} :: page}}"></section>' for p in pages) + f'''
</main>
<nav th:replace="~{{fragments/tabbar :: tabbar}}"></nav>
</div>
</div>

<th:block th:replace="~{{fragments/preview :: panel}}"></th:block>

<datalist id="masterList"></datalist>
<div id="modalRoot"></div>
<div class="toast" id="toast" hidden></div>

<!-- 서버 설정: 처음 열 화면, 모델 파일 위치 -->
<script th:inline="javascript">
  window.YORIJORI = {{
    page: /*[[${{page}}]]*/ "home",
    recipeCode: /*[[${{recipeCode}}]]*/ null,
    modelUrl: /*[[@{{${{modelUrl}}}}]]*/ "/models/fridge.onnx",
    classesUrl: /*[[@{{${{classesUrl}}}}]]*/ "/models/classes.json"
  }};
</script>
<!-- 레시피 데이터: DB(recipe·recipe_ingredient·recipe_step)를 데모 recipeData 형식 JSON 으로 (RecipeService.recipeDataJson) -->
<script id="recipeData" type="application/json" th:utext="${{recipeJson}}">[]</script>

{scripts}
</body>
</html>
'''
(T / 'index.html').write_text(index, encoding='utf-8')
print('css', len(css_files), 'js', len(js) + 2, 'pages', pages)
