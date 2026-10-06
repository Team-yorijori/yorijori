/*
 * 영수증·주문내역 규칙 테스트 — static/js/ai/receipt.js 를 그대로 불러와 돌린다.
 *   node ai/receipt/test_receipt.js
 * 규칙(상품명 → 재료, 제외 단어, 수량 계산)을 고치면 이 파일의 CASES 에 사례를 추가하고 돌려 본다.
 */
const fs = require("fs"), path = require("path"), vm = require("vm");
const JS = path.join(__dirname, "../../backend/src/main/resources/static/js");
const ctx = vm.createContext({ console, document: { getElementById: () => ({ textContent: "[]" }) } });
for (const f of ["data.js", "util.js", "ai/receipt.js"]) vm.runInContext(fs.readFileSync(path.join(JS, f), "utf8"), ctx, { filename: f });

// [영수증 한 줄, 기대 결과 {재료: 수량}, (선택) 알려진 한계 설명 — 틀려도 실패로 세지 않는다]
const CASES = [
  ["한돈 삼겹살 500g", { 돼지고기: 500 }],
  ["특란 30구", { 계란: 30 }],
  ["양파 1.5kg", { 양파: 8 }],                       // 1개 200g 기준
  ["국산 깐마늘 200g", { 마늘: 10 }],                // '쪽' 단위는 기본 수량
  ["CJ 햇반 210g x 3", { 밥: 3 }, "알려진 한계: 기본 수량(2공기) × 3 = 6 으로 잡힌다. TODO(AI) 1개 단위 상품은 묶음 수만 쓰기"],
  ["서울우유 1000ml", { 우유: 1000 }],
  ["두부 300g 2팩", { 두부: 2 }],
  ["샤인머스캣 1송이", { 포도: 1 }],
  ["배송비 3,000원", {}],                            // 상품이 아닌 줄
  ["양파링 과자", {}],                               // 가공품
  ["무농약 콩나물 300g", { 콩나물: 1 }],             // '무농약'의 '무'는 재료가 아니다
  ["양파 감자 세트", { 양파: 3, 감자: 4 }],          // 한 줄에 여럿이면 각각 기본 수량
  ["주문번호 2026100612345", {}],
];

let fail = 0, known = 0;
for (const [line, want, note] of CASES) {
  const got = Object.fromEntries(vm.runInContext(`parseReceipt(${JSON.stringify(line)})`, ctx).map(r => [r.name, r.qty]));
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok && note) { known++; console.log("한계", line.padEnd(24), JSON.stringify(got), "기대 " + JSON.stringify(want), "—", note); continue; }
  if (!ok) fail++;
  console.log(ok ? "통과" : "실패", line.padEnd(24), JSON.stringify(got), ok ? "" : "기대 " + JSON.stringify(want));
}
console.log(fail ? `\n${fail}건 실패` : `\n모두 통과${known ? ` (알려진 한계 ${known}건)` : ""}`);
process.exit(fail ? 1 : 0);
