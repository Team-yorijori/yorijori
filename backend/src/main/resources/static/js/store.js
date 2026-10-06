/* 요리조리 — 데모 v9 에서 나눈 파일. 원본: demo/요리조리_데모_v9.html */
/* 냉장고 상태 (지금은 localStorage. TODO: api.js 로 서버 저장) */

/* ---------- 상태 ---------- */
const KEY = "yorijori-demo-fridge-v1";
function seed(){
  // [이름, 등록 며칠 전, 남은 일수(null이면 자동 계산), 수량]
  const rows = [["양배추",1,null,1],["두부",4,null,1],["돼지고기",1,null,600],["계란",6,null,10],["대파",4,null,1],
                ["양파",5,null,3],["김치",10,null,1000],["밥",1,null,2],["애호박",4,null,1],["감자",10,null,4],["토마토",5,null,3]];
  return rows.map(([name, ago, left, qty], i) => {
    const m = MASTER[name], reg = addDays(-ago);
    return {id:"s"+i, name, qty, unit:m[2], reg, exp: left==null ? iso(parse(reg).getTime() + m[1]*DAY) : addDays(left), auto: left==null};
  });
}
let fridge = load();
let sortMode = "urgent";
let user = null;
function load(){ try { const s = localStorage.getItem(KEY); if (s) return JSON.parse(s); } catch(e){} return seed(); }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(fridge)); } catch(e){} }
const uid = () => Math.random().toString(36).slice(2,9);
const stock = name => fridge.filter(f => f.name === name && f.qty > 0);
const stockQty = name => stock(name).reduce((a,f) => a + f.qty, 0);
const soonest = name => stock(name).map(f => dday(f.exp)).sort((a,b) => a-b)[0];
