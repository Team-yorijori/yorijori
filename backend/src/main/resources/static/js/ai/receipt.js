/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* [AI] 영수증·주문내역 글자 → 재료 (상품명 규칙 · 수량 계산) */

/* =====================================================================
 * v6-3) 영수증·주문내역 → 재료
 *   사진: tesseract.js(한국어)로 기기 안에서 글자를 읽는다 (서버·비용 없음)
 *   글자: 쿠팡·마켓컬리·네이버 주문내역을 복사해 붙여넣는다
 * ===================================================================== */
// [상품명에 나오는 표기, 표준 재료] — 긴 표기부터 찾는다
const RC_ALIAS = [
  ["달걀","계란"],["특란","계란"],["대란","계란"],["왕란","계란"],["구운란","계란"],
  ["삼겹","돼지고기"],["목살","돼지고기"],["앞다리","돼지고기"],["뒷다리","돼지고기"],["돈육","돼지고기"],["항정","돼지고기"],["대패","돼지고기"],["돼지","돼지고기"],
  ["한우","소고기"],["우육","소고기"],["등심","소고기"],["양지","소고기"],["차돌","소고기"],["우삼겹","소고기"],["사태","소고기"],
  ["닭가슴살","닭고기"],["닭다리","닭고기"],["닭안심","닭고기"],["닭볶음탕용","닭고기"],["생닭","닭고기"],["닭","닭고기"],
  ["방울토마토","토마토"],["대추방울","토마토"],["새송이","버섯"],["팽이","버섯"],["표고","버섯"],["느타리","버섯"],["양송이","버섯"],
  ["청양고추","고추"],["풋고추","고추"],["꽈리고추","고추"],["오이고추","고추"],["깐마늘","마늘"],["다진마늘","마늘"],["통마늘","마늘"],
  ["감귤","귤"],["한라봉","귤"],["샤인머스캣","포도"],["캠벨","포도"],["거봉","포도"],
  ["슬라이스치즈","치즈"],["체다","치즈"],["모짜렐라","치즈"],["참치","참치캔"],["오뎅","어묵"],
  ["떡볶이떡","떡"],["가래떡","떡"],["떡국떡","떡"],["즉석밥","밥"],["햇반","밥"],
  ["알배기","배추"],["알배추","배추"],["절임배추","배추"],["배추김치","김치"],["포기김치","김치"],["열무김치","김치"],["총각김치","김치"],["깍두기","김치"],
  ["흰우유","우유"],["저지방우유","우유"],["주키니","애호박"],["피망","파프리카"],["로메인","상추"],
  ["새우살","새우"],["칵테일새우","새우"],["흰다리","새우"],["무우","무"],["슬라이스햄","햄"]
];
const RC_DICT = [...RC_ALIAS, ...Object.keys(MASTER).map(k => [k, k])].sort((a, b) => b[0].length - a[0].length);
// 이런 줄은 상품이 아니다
const RC_SKIP_LINE = /배송|결제|합계|총액|소계|할인|쿠폰|포인트|적립|카드|부가세|과세|면세|주문번호|영수증|사업자|대표자|전화|주소|승인|거스름|받을|금액|반품|교환|문의/;
// 가공품(양파링, 마늘가루, 사과주스 …)은 재료로 보지 않는다
const RC_SKIP_WORD = /칩|링|스낵|과자|라면|주스|음료|소스|드레싱|시럽|분말|가루|향|맛우유|젤리|사탕|아이스/;
// '개' 단위 재료를 무게로 샀을 때 1개 무게(g) — 1.5kg 양파 → 약 8개
const EACH_G = { 양파:200, 감자:150, 고구마:200, 당근:200, 사과:250, 배:600, 토마토:150, 오이:200, 애호박:300, 파프리카:150,
  레몬:120, 오렌지:200, 귤:80, 키위:90, 복숭아:250, 가지:150, 바나나:120, 옥수수:300, 무:1200, 단호박:1000 };
const isHangul = c => !!c && /[가-힣]/.test(c);
// josa(받침에 따라 을/를) 는 여러 화면에서 쓰므로 util.js 로 옮겼다

function rcQty(line, canon){
  const m = MASTER[canon], unit = m ? m[2] : "개", def = m ? m[3] : 1;
  const L = line.replace(/(\d),(\d{3})/g, "$1$2");
  const w = L.match(/(\d+(?:\.\d+)?)\s*(kg|㎏|g|그램|ml|㎖|ℓ|l|리터)(?![a-z])/i);
  const c = L.match(/(\d+)\s*(구|개입|입|개|팩|봉|단|마리|송이|포기|모|캔|통|장|줄|알)/);
  const x = L.match(/[x×*]\s*(\d+)(?!\s*(?:g|kg|ml|㎏))/i);
  const packs = x ? +x[1] : 1;
  let grams = null;
  if (w){ const u = w[2].toLowerCase(); grams = +w[1] * (/^(kg|㎏|ℓ|l|리터)$/.test(u) ? 1000 : 1); }
  // 영수증 글자 인식에서 g가 8로 읽히는 경우(500g → 5008)
  else if (unit === "g"){ const o = L.match(/(\d{2,4}0)8(?!\d)/); if (o) grams = +o[1]; }
  if (unit === "g" || unit === "ml") return (grams ?? def) * (c && grams && /팩|봉|개|입/.test(c[2]) && !x ? +c[1] : packs);
  if (c && /구|입|개입/.test(c[2])) return +c[1] * packs;                     // 계란 30구, 귤 10입
  if (grams && EACH_G[canon]) return Math.max(1, Math.round(grams / EACH_G[canon])) * (c ? +c[1] : packs);
  if (c) return +c[1] * packs;
  return def * packs;
}

/** 글자 → [{ name, qty, src }] */
function parseReceipt(text){
  const out = new Map();
  text.split(/\r?\n/).map(l => l.replace(/\s+/g, " ").trim()).filter(l => l.length >= 2).forEach(line => {
    if (RC_SKIP_LINE.test(line)) return;
    const flat = line.replace(/\s+/g, "");
    if (RC_SKIP_WORD.test(flat)) return;
    const taken = new Array(flat.length).fill(false), found = [];
    for (const [tok, canon] of RC_DICT){
      let from = 0, i;
      while ((i = flat.indexOf(tok, from)) >= 0){
        from = i + 1;
        if (taken.slice(i, i + tok.length).some(Boolean)) continue;
        // 한 글자 재료(무, 배, 밤, 굴, 떡 …)는 앞뒤가 한글이 아닐 때만: '배송', '무농약' 제외
        if (tok.length === 1 && (isHangul(flat[i - 1]) || isHangul(flat[i + 1]))) continue;
        for (let k = i; k < i + tok.length; k++) taken[k] = true;
        if (!found.includes(canon)) found.push(canon);
      }
    }
    // 한 줄에 재료가 여럿이면(예: '양파 감자 세트') 각각 기본 수량
    found.forEach(canon => {
      const qty = found.length === 1 ? rcQty(line, canon) : (MASTER[canon] ? MASTER[canon][3] : 1);
      const g = out.get(canon);
      if (g){ g.qty += qty; g.src += " / " + line; } else out.set(canon, { name: canon, qty, src: line });
    });
  });
  return [...out.values()];
}
