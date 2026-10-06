# backend — Spring Boot (백엔드 + 화면)

Spring Boot 3.5 · Java 17 · Spring Data JPA · Spring Security(세션) · Thymeleaf · Flyway · MySQL 8 / H2

## 실행

```bash
./gradlew bootRun                                        # local: H2 메모리 DB (설치 필요 없음)
./gradlew bootRun --args='--spring.profiles.active=mysql' # MySQL (application-mysql.yml)
./gradlew test                                           # 시드 확인 + API 전체 흐름 테스트
```

- http://localhost:8080 화면 · http://localhost:8080/h2-console (local, JDBC URL `jdbc:h2:mem:yorijori`, 사용자 `sa`)
- 비밀 값: `application-secret.example.yml` → `application-secret.yml` 로 복사해서 채운다 (깃에 올리지 않음)
- IntelliJ: `backend` 폴더를 Gradle 프로젝트로 연다. JDK 17 이상

## 패키지 (`com.yorijori`)

| 패키지 | 내용 | 주요 클래스 |
|---|---|---|
| `user` | 회원가입·로그인·못 먹는 재료(v9)·애니 설정 | `AuthController`, `UserController`, `UserService`, `User`, `UserAvoid` |
| `fridge` | 냉장고·재료 등록(동의어·소비기한 자동 안내)·수정·버리기·차감 | `FridgeController`, `FridgeService`, `FridgeItem`, `FridgeMember` |
| `ingredient` | 재료 기준표·동의어·알레르기 묶음·인식 모델 클래스·인식 수정 기록 | `IngredientController`, `ScanController`, `IngredientService`, `AvoidGroupService` |
| `recipe` | 레시피 메모리 목록·추천 점수·상세·영상 ID 수집 | `RecommendService`, `RecipeService`, `RecipeCatalog`, `AvoidMatcher`, `video/YoutubeVideoCollector` |
| `dish` | 요리 완료(차감 + 보관 + 기록)·먹기·버리기·이번 달 통계 | `DishController`, `DishService`, `CookingLogService` |
| `cart` | 장보기·샀어요·최저가 확인 스케줄러 | `CartController`, `CartService`, `price/PriceCheckScheduler`, `price/NaverShoppingClient` |
| `common` | 보안·예외·공통 응답·초성 검색·화면 주소 | `SecurityConfig`, `GlobalExceptionHandler`, `ApiResponse`, `Hangul`, `web/PageController` |

## 코드 규칙

- 요청·응답은 `dto/` 의 `record`. 엔티티를 그대로 내보내지 않는다
- 응답은 `ApiResponse.ok(data, "안내 문구")` — 화면이 `message` 를 그대로 토스트로 띄운다
- 오류는 `throw new ApiException(ErrorCode.XXX)` — 메시지는 사용자에게 보이는 한국어
- 로그인한 회원: 컨트롤러 파라미터 `@AuthenticationPrincipal LoginUser me`
- 날짜 기준은 `Clock`(Asia/Seoul) 빈 — 테스트에서 고정 시계로 바꿔 끼울 수 있다
- DB 변경은 `db/migration/V{번호}__설명.sql` 추가 (이미 반영된 파일은 고치지 않는다)
- 패키지 사이 의존: `user → fridge`, `recipe → fridge·dish(로그)·user`, `dish → fridge·recipe`, `cart → fridge`. 순환을 만들지 않는다

## 화면 (`resources/templates`, `static`)

- 데모 v9 를 그대로 나눈 것이라 한 페이지(`index.html`) 안에서 화면을 바꾼다. 화면별 HTML 은 `templates/pages/*.html`
- 주소 `/fridge`, `/recipes/r12` 등은 `PageController` 가 처음 열 화면만 정해 준다 (`static/js/init.js` 가 주소와 화면을 맞춘다)
- 레시피 데이터: 서버가 DB 레시피를 데모 형식 JSON 으로 페이지에 넣는다 (`RecipeService.recipeDataJson`)
- **지금 화면은 냉장고·만든 요리·장보기를 아직 브라우저(localStorage)에 저장한다.** 서버 API 는 다 만들어 두었으니 `static/js/api.js` 의 TODO 순서대로 바꾼다
- 로그인은 서버와 연결되어 있다 (상단 로그인 버튼, `/login`, `/signup`)

## 남은 일 (TODO 로 검색)

- `TODO(프론트)` 화면 저장소 → API (api.js), `scan-rules.js` → `/api/scan/classes`
- `TODO(백)` CSRF 토큰 방식, 가족 공유 냉장고, 최저가 알림 방식(웹 푸시/메일), 추천 후보 SQL 로 줄이기(레시피가 많아지면)
- `TODO(AI)` 영상 검색 결과 검수, 네이버 쇼핑 검색 결과에서 가공품 거르기

> 이 프로젝트는 Maven Central 에 접속할 수 없는 환경에서 만들어져 실제 Gradle 빌드·테스트를 돌려 보지 못했다.
> Java 코드는 컴파일 검사, SQL 은 MySQL 문법 검사와 SQLite 실행, 화면은 브라우저 테스트까지 했다. 처음 `./gradlew test` 에서 오류가 나면 알려 달라.
