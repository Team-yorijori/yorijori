# API 명세 (v9 기준)

- 주소 앞부분: `http://localhost:8080` (로컬) · 배포 후 AWS 주소
- 형식: JSON, UTF-8. 날짜는 `2026-10-06`, 시각은 `2026-10-06T20:30:00`
- 로그인: 세션 쿠키 (`/api/auth/login` 성공하면 `JSESSIONID`). 화면에서는 `fetch(url, { credentials: "same-origin" })` → `static/js/api.js` 의 `Api.get/post/...` 사용
- 바뀌면 이 파일을 **먼저** 고치고 PR 설명에 기록

## 공통 응답

```json
{ "ok": true,  "data": { ... }, "message": "두부 추가 · 소비기한 10/11 자동 안내 (냉장 5일 기준)", "code": null }
{ "ok": false, "data": null,     "message": "로그인이 필요합니다.", "code": "UNAUTHORIZED" }
```

| code | HTTP | 뜻 |
|---|---|---|
| INVALID_INPUT | 400 | 입력값 오류 (`message` 에 이유) |
| UNAUTHORIZED / LOGIN_FAILED | 401 | 로그인 필요 / 이메일·비밀번호 틀림 |
| DUPLICATE_EMAIL | 409 | 이미 가입한 이메일 |
| *_NOT_FOUND | 404 | 냉장고 재료·레시피·만든 요리·장보기 항목 없음 |
| EXTERNAL_API_ERROR | 502 | 네이버·YouTube 응답 없음 |

로그인 없이 쓸 수 있는 것 : 화면(`/`, `/fridge` …), `GET /api/ingredients/**`, `GET /api/recipes/{code}`, `GET /api/recipes/data`, `GET /api/scan/classes`, `/api/auth/**`

---

## 1. 회원 `user`

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/auth/signup` | 가입 + 바로 로그인 + 기본 냉장고 생성 |
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 로그인한 회원 (없으면 `data: null`) |
| GET | `/api/me/avoid` | v9 못 먹는 재료 |
| PUT | `/api/me/avoid` | v9 못 먹는 재료 저장 (전체 교체) |
| PUT | `/api/me/anim` | v7 애니메이션 On/Off |

```http
POST /api/auth/signup
{ "email": "cook@yorijori.kr", "password": "password1", "nickname": "요리왕" }
→ { "ok": true, "data": { "id": 1, "email": "cook@yorijori.kr", "nickname": "요리왕", "animOn": true }, "message": "요리왕 님, 가입을 환영합니다." }
```

```http
PUT /api/me/avoid
{ "groups": ["계란", "대두"], "items": ["오이"], "show": false }
```
- `groups`: 알레르기 묶음 이름 (`GET /api/ingredients/avoid-groups` 목록 중)
- `items`: 직접 넣은 재료
- `show`: `false` 면 추천에서 제외, `true` 면 제외하지 않고 표시만 (목록 맨 뒤)

## 2. 재료 기준표 `ingredient`

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/ingredients?q=ㅇㅍ` | 자동완성 (초성 가능, 최대 20개). q 없으면 전체 |
| GET | `/api/ingredients/avoid-groups` | 알레르기 묶음 16개 `{ name, terms[], warning }` |
| GET | `/api/scan/classes?version=v4` | 인식 모델 클래스 `{ id, en, ko, auto, confuse[] }` |
| POST | `/api/scan/feedback` | 인식 결과를 고친 기록 |

```http
POST /api/scan/feedback
{ "modelVersion": "v4", "consent": true, "rows": [ { "predicted": "귤", "corrected": "감", "score": 0.98 } ] }
→ { "data": 1 }   // 저장한 줄 수 (predicted == corrected 인 줄은 건너뜀)
```

## 3. 냉장고 `fridge`

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/fridge/items` | 내 냉장고 (소비기한 가까운 순) |
| POST | `/api/fridge/items` | 등록 (직접 1개, 스캔·영수증 여러 개) |
| PATCH | `/api/fridge/items/{id}` | 수량·소비기한 수정 |
| DELETE | `/api/fridge/items/{id}` | 버리기 (기록 남김) |

```http
POST /api/fridge/items
{ "items": [
  { "name": "달걀", "qty": 10, "source": "RECEIPT" },
  { "name": "두부" },
  { "name": "청경채", "expDate": "2026-10-12" }
] }
→ { "data": {
    "items": [
      { "item": { "id": 7, "name": "계란", "category": "유제품·알", "qty": 10, "unit": "개", "regDate": "2026-10-06",
                  "expDate": "2026-10-27", "expAuto": true, "dday": 21, "source": "RECEIPT" },
        "message": "계란 추가 · 소비기한 10/27 자동 안내 (냉장 21일 기준)" }, …
    ],
    "removedFromCart": ["두부"]          // 장보기 목록에 있던 재료는 자동 삭제
} }
```
- 이름은 표준 이름으로 변환 (`ingredient_alias`: 달걀 → 계란)
- 소비기한: `expDate` 직접 입력 > 기준표 보관 일수 > 7일
- `qty` 가 없으면 기준표 기본 수량
- 못 먹는 재료면 `message` 끝에 ` · 못 먹는 재료로 설정된 재료입니다`

```http
PATCH /api/fridge/items/7
{ "qty": 6 }                         // 수량
{ "expDate": "2026-10-20" }          // 직접 고친 날짜 (expAuto=false)
{ "resetAuto": true }                // 자동 안내 날짜로 되돌리기
{ "qty": 0 }                         // 다 씀 → 지우고 data: null
```

## 4. 레시피 `recipe`

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/recipes/recommend?sort=urgent&q=&page=0&size=12` | 추천 (로그인) |
| GET | `/api/recipes/{code}` | 상세 (로그인하면 보유 상태 포함) |
| GET | `/api/recipes/data` | 전체 레시피, 데모 recipeData 형식 (응답 감싸기 없이 배열) |

- `sort`: `urgent` 임박 재료 우선 · `ready` 바로 만들 수 있는 순
- `q`: 요리·재료 이름, 초성 가능 (`ㄱㅊㅉㄱ`)
- 점수 = 보유율 × 60 + 임박 가산점(D-1 이하 +40 · D-3 이하 +25 · D-5 이하 +10) − 2일 안에 만든 요리 15

```json
{ "data": {
  "items": [ {
    "code": "r212", "title": "두부조림", "cookTimeMin": 20, "difficulty": "초보환영", "category": "조림",
    "score": 100.0, "ratio": 1.0, "have": ["두부", "대파"], "missing": [], "optional": [],
    "urgent": { "name": "두부", "dday": 1 }, "recent": null, "avoid": []
  } ],
  "page": 0, "size": 12, "total": 215, "recipeCount": 560, "avoidHidden": 0, "avoidShow": false
} }
```

값은 예시. 상세의 재료 `status`: `HAVE` 보유 · `LOW` 조금 부족 · `MISSING` 부족 · `OPTIONAL` 선택 재료

## 5. 만든 요리 `dish`

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/recipes/{code}/cook` | 요리 완료: 재료 차감(임박한 것부터) + 만든 요리 보관 + 기록 |
| GET | `/api/dishes` | 만든 요리 (보관 기한 가까운 순) |
| POST | `/api/dishes/{id}/eat` | 1인분 먹기 (0인분이 되면 지우고 `data: null`) |
| DELETE | `/api/dishes/{id}` | 버리기 |
| GET | `/api/stats/monthly?month=2026-10` | 이번 달: 만든 요리 · 먹은 인분 · 살린 임박 재료 · 버린 것 + 최근 기록 8개 |

```http
POST /api/recipes/r212/cook
{ "servings": 2, "uses": [ { "name": "두부", "qty": 1 }, { "name": "대파", "qty": 0.3 } ] }
→ { "data": { "dish": { "id": 3, "name": "두부조림", "servings": 2, "left": 2, "made": "2026-10-06", "exp": "2026-10-10", … },
              "deducted": 2, "saved": ["두부"] },
    "message": "두부조림 2인분을 만든 요리에 보관했습니다 · 재료 2종 차감 · 임박 재료 1개 살림" }
```
- `qty: 0` 인 재료는 차감 안 함. `uses` 가 비어 있으면 보관만
- 보관 기한: 레시피 분류별 (밥 1일, 볶음 2일, 국·찌개 3일, 조림 4일 …, `recipe.storage_days`)
- 살린 임박 재료: 쓴 재료 중 소비기한 D-3 이내

## 6. 장보기 `cart`

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/cart` | 목록 (마지막으로 확인한 최저가 포함) |
| POST | `/api/cart` | 담기 `{ "names": ["양파"], "targetPrice": 3000 }` · 부족한 재료 한 번에 `{ "names": ["양파","대파"] }` |
| PATCH | `/api/cart/{id}` | `{ "targetPrice": 2500, "alert": true }` (targetPrice 0 = 해제) |
| DELETE | `/api/cart/{id}` | 빼기 |
| POST | `/api/cart/{id}/bought` | 샀어요 → 냉장고로 |

최저가: 서버 스케줄러(`PriceCheckScheduler`)가 하루 3번 네이버 쇼핑 검색 API로 확인해 `lowestPrice` 입력 (`yorijori.naver.enabled=true` + 키 필요). 목표가 이하로 내려가면 알림 — 알림 방식은 미정(TODO).

## 7. 화면 주소

| 주소 | 화면 |
|---|---|
| `/` | 홈 |
| `/fridge` · `/recipes` · `/dishes` · `/cart` · `/items` | My 냉장고 · AI 매칭 레시피 · 만든 요리 · 장보기 · 내 식재료 |
| `/recipes/{code}` | 레시피 상세 |
| `/login` · `/signup` | 로그인 · 회원가입 |
