"""v2 데모 + 실제 스캔 모델(v3) + 레시피 확장 → 요리조리_데모_v3.html"""
import base64, json
from pathlib import Path

SRC = Path('/home/claude/yorijori-demo/요리조리_데모_v2.html')
OUT = Path('/home/claude/yorijori-demo/요리조리_데모_v3.html')
MODEL = Path('/root/.claude/uploads/812b88c2-0a5f-5a54-b556-cc02749e5f94/b26b676f-fridge_v3.onnx')
CLASSES = Path('/root/.claude/uploads/812b88c2-0a5f-5a54-b556-cc02749e5f94/15a0d4c0-classes_v3.json')
SCANJS = Path('/home/claude/yorijori-scan/fridge-scan.js')

s = SRC.read_text(encoding='utf-8')

def rep(a, b, count=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, count)

rep('<title>요리조리 v2</title>', '<title>요리조리 v3</title>')

# ---------- 1) 재료 마스터: 스캔 모델 25종을 모두 포함 ----------
rep('''  "김치":["반찬",30,"g",1000,"#D9442E"],"밥":["곡류",2,"공기",2,"#FAF7F0"]
};''', '''  "김치":["반찬",30,"g",1000,"#D9442E"],"밥":["곡류",2,"공기",2,"#FAF7F0"],
  // v3 추가: 스캔 모델이 인식하는 재료
  "오이":["채소",7,"개",2,"#5DA34A"],"무":["채소",14,"개",1,"#F3F1E6"],"고추":["채소",10,"개",10,"#3F8A35"],
  "파프리카":["채소",10,"개",2,"#E8432F"],"가지":["채소",5,"개",2,"#6B3F7E"],"브로콜리":["채소",5,"송이",1,"#3F7F3A"],
  "옥수수":["채소",3,"개",2,"#F2C94C"],"고구마":["채소",14,"개",3,"#9A4E62"],
  "사과":["과일",30,"개",3,"#D9443A"],"바나나":["과일",5,"개",4,"#F4D35E"],"레몬":["과일",21,"개",2,"#F7E04B"]
};''')
rep('const CAT_ORDER = ["채소","육류","유제품·알","가공식품","반찬","곡류","기타"];',
    'const CAT_ORDER = ["채소","과일","육류","유제품·알","가공식품","반찬","곡류","기타"];')

# ---------- 2) 레시피: 새 재료를 쓰는 요리 18개 추가 ----------
rep('''   steps:["양배추와 양파를 채 썬다.","기름 뺀 참치와 채소를 볶고 간장·굴소스로 간한다.","밥 위에 올린다."]}
];''', '''   steps:["양배추와 양파를 채 썬다.","기름 뺀 참치와 채소를 볶고 간장·굴소스로 간한다.","밥 위에 올린다."]},
  // v3 추가 레시피
  {id:"oi-muchim",name:"오이무침",time:10,diff:"쉬움",serv:2,ings:[["오이",1],["양파",0.3,1],["마늘",2,1]],
   steps:["오이를 반달 모양으로 썰어 소금에 10분 절인다.","물기를 짜고 고춧가루·식초·설탕·다진 마늘을 넣는다.","양파를 채 썰어 함께 무친다."]},
  {id:"mu-saengchae",name:"무생채",time:15,diff:"쉬움",serv:3,ings:[["무",0.5],["대파",0.2,1],["마늘",2,1]],
   steps:["무를 가늘게 채 썬다.","고춧가루로 먼저 버무려 색을 입힌다.","식초·설탕·소금·다진 마늘·대파를 넣고 무친다."]},
  {id:"beef-mu-guk",name:"소고기뭇국",time:30,diff:"보통",serv:3,ings:[["무",0.3],["소고기",150],["대파",0.3],["마늘",2,1]],
   steps:["소고기를 참기름에 볶다가 나박 썬 무를 넣고 함께 볶는다.","물 1L를 붓고 20분 끓인다.","국간장·다진 마늘로 간하고 대파를 넣는다."]},
  {id:"gaji-bokkeum",name:"가지볶음",time:15,diff:"쉬움",serv:2,ings:[["가지",2],["양파",0.5,1],["대파",0.3,1],["마늘",2,1]],
   steps:["가지를 길게 반 갈라 어슷 썬다.","기름에 다진 마늘·대파를 볶아 향을 낸다.","가지·양파를 넣고 간장·굴소스로 간해 숨이 죽을 때까지 볶는다."]},
  {id:"gaji-deopbap",name:"가지덮밥",time:20,diff:"보통",serv:1,ings:[["가지",1],["밥",1],["돼지고기",100,1],["대파",0.3,1]],
   steps:["가지를 깍둑 썬다.","돼지고기와 대파를 볶다가 가지를 넣는다.","간장·설탕·전분물로 걸쭉하게 만들어 밥 위에 올린다."]},
  {id:"broccoli-egg",name:"브로콜리 계란볶음",time:10,diff:"쉬움",serv:2,ings:[["브로콜리",1],["계란",2],["마늘",2,1]],
   steps:["브로콜리를 한입 크기로 잘라 끓는 물에 30초 데친다.","계란을 스크램블해 덜어둔다.","마늘·브로콜리를 볶고 계란을 넣어 소금으로 간한다."]},
  {id:"broccoli-chogochu",name:"브로콜리 숙회",time:5,diff:"쉬움",serv:2,ings:[["브로콜리",1]],
   steps:["브로콜리를 송이별로 자른다.","끓는 소금물에 1분 데친 뒤 찬물에 헹군다.","초고추장을 곁들인다."]},
  {id:"corn-cheese",name:"콘치즈",time:15,diff:"쉬움",serv:2,ings:[["옥수수",2],["치즈",2],["양파",0.3,1]],
   steps:["옥수수 알을 칼로 발라낸다(통조림 옥수수도 된다).","마요네즈·설탕과 섞고 다진 양파를 넣는다.","팬에 담고 치즈를 올려 뚜껑을 덮고 약불에서 녹인다."]},
  {id:"goguma-mattang",name:"고구마맛탕",time:25,diff:"보통",serv:3,ings:[["고구마",3]],
   steps:["고구마를 한입 크기로 썰어 물기를 닦는다.","기름에 노릇하게 튀기듯 굽는다.","설탕·물엿을 녹인 시럽에 버무리고 깨를 뿌린다."]},
  {id:"gamja-chae",name:"감자채볶음",time:15,diff:"쉬움",serv:2,ings:[["감자",2],["양파",0.5,1],["당근",0.3,1]],
   steps:["감자를 가늘게 채 썰어 찬물에 전분을 뺀다.","기름에 감자·당근을 볶는다.","양파를 넣고 소금으로 간한다."]},
  {id:"gyeranmari",name:"계란말이",time:15,diff:"보통",serv:2,ings:[["계란",4],["대파",0.3,1],["당근",0.2,1]],
   steps:["계란을 풀고 다진 대파·당근·소금을 넣는다.","약불에서 얇게 부쳐 끝에서부터 돌돌 만다.","남은 계란물을 부어가며 두께를 키운 뒤 썬다."]},
  {id:"beoseot-bokkeum",name:"버섯볶음",time:10,diff:"쉬움",serv:2,ings:[["버섯",1],["양파",0.5,1],["대파",0.2,1]],
   steps:["버섯을 먹기 좋게 찢거나 썬다.","센 불에 버섯·양파를 볶는다.","간장·참기름으로 간하고 대파를 넣는다."]},
  {id:"paprika-beef",name:"파프리카 소고기볶음",time:15,diff:"쉬움",serv:2,ings:[["파프리카",2],["소고기",200],["양파",0.5,1]],
   steps:["소고기를 간장·설탕·후추에 재운다.","파프리카·양파를 채 썬다.","고기를 볶다가 채소를 넣고 1분만 더 볶는다."]},
  {id:"gochu-muchim",name:"풋고추 된장무침",time:10,diff:"쉬움",serv:2,ings:[["고추",10]],
   steps:["풋고추를 씻어 꼭지를 떼고 한입 크기로 자른다.","된장·참기름·깨를 섞는다.","고추와 버무린다."]},
  {id:"apple-salad",name:"사과 양배추 샐러드",time:10,diff:"쉬움",serv:2,ings:[["사과",1],["양배추",0.2],["레몬",0.5,1]],
   steps:["양배추를 가늘게 채 썬다.","사과를 얇게 썰고 레몬즙을 뿌려 갈변을 막는다.","마요네즈·꿀을 넣고 버무린다."]},
  {id:"banana-milk",name:"바나나 우유 스무디",time:5,diff:"쉬움",serv:1,ings:[["바나나",2],["우유",300]],
   steps:["바나나를 썬다.","우유와 함께 믹서에 간다.","얼음이나 꿀을 취향대로 넣는다."]},
  {id:"tomato-lemon",name:"토마토 레몬 샐러드",time:10,diff:"쉬움",serv:2,ings:[["토마토",2],["레몬",0.5],["양파",0.3,1]],
   steps:["토마토를 웨지 모양으로 썬다.","양파를 얇게 채 썰어 찬물에 매운맛을 뺀다.","레몬즙·올리브유·소금·후추로 드레싱해 버무린다."]},
  {id:"sigeumchi-guk",name:"시금치 된장국",time:15,diff:"쉬움",serv:3,ings:[["시금치",1],["두부",0.5,1],["대파",0.2,1]],
   steps:["물 800ml에 된장 2큰술을 푼다.","끓으면 두부를 넣는다.","시금치·대파를 넣고 1분만 더 끓인다."]}
];''')

# ---------- 3) 스캔 결과 화면용 스타일 ----------
rep('''@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>''', '''/* ---------- v3: 실제 스캔 ---------- */
.scan-stage{margin-top:12px;border-radius:12px;overflow:hidden;background:var(--field)}
.scan-stage canvas{display:block;width:100%;height:auto}
.scan-status{margin-top:10px;font-size:13px;color:var(--muted);min-height:20px}
.scan-status.err{color:var(--danger)}
.scan-list{list-style:none;padding:0;margin:12px 0 0;display:grid;gap:6px}
.scan-list li{display:grid;grid-template-columns:auto minmax(0,1fr) auto auto;gap:8px;align-items:center;padding:8px 10px;border-radius:10px;background:var(--field)}
.scan-list .sw{width:10px;height:10px;border-radius:3px;display:inline-block;margin-right:6px}
.scan-list input[type=text]{background:var(--bg);border:0;border-radius:8px;padding:6px 8px;width:100%;min-width:0}
.scan-list .qty{display:flex;align-items:center;gap:4px;font-size:13px;color:var(--muted)}
.scan-list .qty input{width:56px;background:var(--bg);border:0;border-radius:8px;padding:6px 6px;font-variant-numeric:tabular-nums}
.scan-recs{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:6px}
.scan-recs button{width:100%;text-align:left;border:1px solid var(--card-line);background:var(--card);border-radius:12px;padding:10px 12px;display:flex;justify-content:space-between;gap:8px;align-items:center}
@container app (max-width:640px){ .scan-list li{grid-template-columns:auto minmax(0,1fr) auto} .scan-list .tagcell{grid-column:2 / -1} }

@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>''')

# ---------- 4) 기존 데모 스캔은 예비용으로 이름만 바꿔 남긴다 ----------
rep('/* 스캔(데모: 업로드한 사진 대신 예시 인식 결과를 보여줌) */\nfunction openScan(){',
    '/* 스캔(데모: 업로드한 사진 대신 예시 인식 결과를 보여줌) — v3부터는 모델을 못 불러올 때만 쓰는 예비용 */\nfunction openScanDemo(){')

# ---------- 5) 실제 스캔 ----------
classes = json.loads(CLASSES.read_text(encoding='utf-8'))
real_scan = r'''
/* ---------- v3: 실제 재료 인식 (YOLO26 fridge_v3.onnx, 브라우저에서 실행) ---------- */
const SCAN_CLASSES = __CLASSES__;
const ORT_CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/";
const SCAN_COLORS = ["#E2483A","#3F8F3A","#E39A1E","#2F6FB5","#8E44AD","#C8682C","#16A085","#D35400","#7F8C8D","#B03A2E"];
let modelReady = null;

function loadScript(src){
  return new Promise((ok, no) => {
    const el = document.createElement("script");
    el.src = src; el.onload = ok; el.onerror = () => no(new Error("onnxruntime-web 을 불러오지 못했다"));
    document.head.appendChild(el);
  });
}
function ensureModel(onStatus){
  if (!modelReady) modelReady = (async () => {
    onStatus && onStatus("인식 엔진을 불러오는 중…");
    if (!window.ort) await loadScript(ORT_CDN + "ort.min.js");
    onStatus && onStatus("재료 인식 모델을 준비하는 중… (처음 한 번만 10~20초)");
    const b64 = document.getElementById("fridgeModel").textContent.trim();
    const buf = await (await fetch("data:application/octet-stream;base64," + b64)).arrayBuffer();
    return FridgeScan.load({ model: buf, classes: SCAN_CLASSES, wasmPaths: ORT_CDN });
  })().catch(e => { modelReady = null; throw e; });
  return modelReady;
}

function scanQty(name, count){
  const m = MASTER[name];
  if (!m) return count;
  return ["개","쪽"].includes(m[2]) ? Math.max(1, count) : m[3] * Math.max(1, count);
}

async function drawScan(file, r){
  const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
  const s = Math.min(1, 1000 / bmp.width);
  const cv = document.createElement("canvas"); cv.width = Math.round(bmp.width * s); cv.height = Math.round(bmp.height * s);
  const ctx = cv.getContext("2d"); ctx.drawImage(bmp, 0, 0, cv.width, cv.height);
  const lw = Math.max(2, cv.width / 260), fs = Math.max(14, Math.round(cv.width / 36));
  ctx.font = `${fs}px "Gowun Dodum", sans-serif`; ctx.textBaseline = "top";
  r.detections.forEach(d => {
    const [x1, y1, x2, y2] = d.box.map(v => v * s), col = SCAN_COLORS[d.id % SCAN_COLORS.length];
    ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    const label = `${d.ko} ${Math.round(d.score * 100)}%`, tw = ctx.measureText(label).width + 10;
    const ty = y1 - fs - 8 < 0 ? y1 : y1 - fs - 8;
    ctx.fillStyle = col; ctx.fillRect(x1, ty, tw, fs + 8); ctx.fillStyle = "#fff"; ctx.fillText(label, x1 + 5, ty + 4);
  });
  const st = $("#scanStage"); st.innerHTML = ""; st.appendChild(cv); st.hidden = false;
}

function openScan(){
  modal(`<h2>재료 사진 스캔</h2>
    <div class="sub">냉장고나 장바구니 사진을 올리면 재료를 찾아냅니다. 사진은 이 기기 안에서만 분석하고 어디에도 보내지 않습니다.</div>
    <label class="drop" for="scanFile" id="dropBox">사진을 찍거나 고르세요 (JPG, PNG)</label>
    <input type="file" id="scanFile" accept="image/*" capture="environment" hidden>
    <div class="scan-stage" id="scanStage" hidden></div>
    <div class="scan-status" id="scanStatus"></div>
    <div id="scanResult"></div>
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="scanOk" disabled>선택한 재료 등록</button></div>`);
  const status = (t, err) => { const el = $("#scanStatus"); if (!el) return; el.textContent = t; el.className = "scan-status" + (err ? " err" : ""); };
  // 사진을 고르기 전에 모델을 미리 준비한다
  ensureModel(status).then(info => status(`준비됨 · ${info.backend === "webgpu" ? "그래픽카드(WebGPU)" : "CPU(WASM)"}로 인식합니다`))
    .catch(e => status("인식 모델을 불러오지 못했습니다: " + (e.message || e) + " · 인터넷 연결을 확인하세요", true));

  $("#scanFile").onchange = async e => {
    const file = e.target.files[0]; if (!file) return;
    $("#dropBox").textContent = "다른 사진으로 바꾸려면 누르세요";
    $("#scanResult").innerHTML = ""; $("#scanOk").disabled = true;
    try {
      await ensureModel(status);
      status("재료를 찾는 중…");
      const r = await FridgeScan.detect(file, { minScore: 0.35, confirmBelow: 0.6 });
      await drawScan(file, r);
      status(`${r.items.length}종 찾음 · ${r.ms}ms · 60% 미만은 '확인 필요'로 꺼 두었습니다`);
      if (!r.items.length){
        $("#scanResult").innerHTML = `<div class="empty">찾은 재료가 없습니다. 재료가 크게 보이게 다시 찍거나 직접 입력하세요.</div>`;
        return;
      }
      $("#scanResult").innerHTML = `<div class="label" style="margin-top:12px">인식 결과 · 이름과 수량을 고칠 수 있습니다</div>
        <ul class="scan-list">${r.items.map((it, i) => {
          const name = it.ko, unit = MASTER[name] ? MASTER[name][2] : "개";
          return `<li>
            <input type="checkbox" id="sc${i}" ${it.needsConfirm ? "" : "checked"} aria-label="${esc(name)} 등록 여부">
            <span style="display:flex;align-items:center;min-width:0"><span class="sw" style="background:${SCAN_COLORS[it.id % SCAN_COLORS.length]}"></span>
              <input type="text" list="masterList" value="${esc(name)}" id="sn${i}" aria-label="재료 이름"></span>
            <span class="qty"><input type="number" min="0" step="any" value="${fmtQty(scanQty(name, it.count))}" id="sq${i}" aria-label="수량">${esc(unit)}</span>
            <span class="tagcell"><span class="tag ${it.needsConfirm ? "t-warn" : "t-ok"}">${it.needsConfirm ? "확인 필요 " : ""}${Math.round(it.score * 100)}%</span></span>
          </li>`; }).join("")}</ul>`;
      $("#scanOk").disabled = false;
    } catch (err) {
      status("인식에 실패했습니다: " + (err.message || err), true);
      $("#scanResult").innerHTML = `<div class="actions" style="justify-content:flex-start"><button class="btn ghost" id="scanDemo">예시 결과로 둘러보기</button></div>`;
      $("#scanDemo").onclick = () => { closeModal(); openScanDemo(); };
    }
  };

  $("#scanOk").onclick = () => {
    const picked = [...document.querySelectorAll(".scan-list li")].filter(li => li.querySelector("input[type=checkbox]").checked)
      .map(li => ({ name: li.querySelector("input[type=text]").value.trim(), qty: parseFloat(li.querySelector("input[type=number]").value) || undefined }))
      .filter(p => p.name);
    if (!picked.length){ toast("선택한 재료가 없습니다."); return; }
    picked.forEach(p => addItem(p.name, "", p.qty));
    showScanRecipes(picked.map(p => p.name));
  };
}

/* 등록 직후: 방금 넣은 재료로 만들 수 있는 레시피를 바로 보여준다 */
function showScanRecipes(names){
  const list = ranked().filter(m => m.r.ings.some(i => names.includes(i[0]))).slice(0, 4);
  modal(`<h2>${names.length}가지 재료를 등록했습니다</h2>
    <div class="sub">${names.map(esc).join(", ")} · 소비기한은 재료별 보관 기간으로 자동 안내했습니다.</div>
    ${list.length ? `<div class="label" style="margin-top:14px">방금 넣은 재료로 만들 수 있는 요리</div>
      <ul class="scan-recs">${list.map(m => `<li><button data-open="${m.r.id}" data-close-after>
        <span>${esc(m.r.name)} <span class="note">${m.r.time}분</span></span>
        ${m.missing.length ? `<span class="tag t-warn">${m.missing.length}개 부족</span>` : `<span class="tag t-ok">바로 가능</span>`}
      </button></li>`).join("")}</ul>` : `<div class="empty">이 재료로 만들 수 있는 레시피가 아직 없습니다.</div>`}
    <div class="actions"><button class="btn ghost" data-close>닫기</button><button class="btn strong" id="goRecipes">추천 레시피 전체 보기</button></div>`);
  $("#goRecipes").onclick = () => { closeModal(); go("recipes"); };
  document.querySelectorAll("[data-close-after]").forEach(b => b.addEventListener("click", () => setTimeout(closeModal, 0)));
}
'''.replace('__CLASSES__', json.dumps(classes, ensure_ascii=False))

rep('/* 로그인(데모) */\nfunction openLogin(){', real_scan + '\n/* 로그인(데모) */\nfunction openLogin(){')

# ---------- 6) 인식 모듈 + 모델 데이터 ----------
scanjs = SCANJS.read_text(encoding='utf-8')
assert '</script>' not in scanjs
b64 = base64.b64encode(MODEL.read_bytes()).decode()
rep('<script>\n/* ---------- 기준 데이터 ---------- */',
    '<script>\n' + scanjs + '\n</script>\n<script>\n/* ---------- 기준 데이터 ---------- */')
rep('</body>', f'<script id="fridgeModel" type="application/octet-stream">{b64}</script>\n</body>')

OUT.write_text(s, encoding='utf-8')
print('written', OUT, round(OUT.stat().st_size / 1e6, 1), 'MB')
