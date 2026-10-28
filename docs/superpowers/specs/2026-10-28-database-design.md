# 요리조리 DB 보완 설계

- 작성일: 2026-10-28
- 상태: 구현 완료 — 최종 검토 및 push 진행 (2026-10-28)
- 기준: `develop` / `113d10bb5e9c2cbb687ce91bb09ef4faa2b7e9c2`
- 선택한 방향: 기존 테이블·Spring API·JPA 매핑을 유지하는 보완 설계

## 1. 목적과 범위

식재료 등록, 소비기한 관리, 레시피 추천, 요리·섭취·폐기 기록, 장보기,
인식 결과 수정 기록을 기존 서비스와 호환되도록 저장한다.
기존 19개 테이블을 재사용하며, DB 자체에서 잘못된 수량·가격·인분과
존재하지 않는 회원 참조를 차단하고 실제 조회 조건을 지원한다.

완료 산출물은 이 설계서, 새 Flyway 마이그레이션, DB 검증 테스트,
컬럼 사전·운영 안내와 최신 ERD이다. 최종 결과는 새로운 원격 브랜치에 push한다.
애플리케이션 API와 응답 형태, 화면, 추천 알고리즘은 변경하지 않는다.

## 2. 검토한 접근 방법

| 방법 | 장점 | 비용·한계 | 결정 |
|---|---|---|---|
| 기존 구조 + 추가 마이그레이션 | 기존 JPA/API 및 데이터 유지, 팀원 DB에 순차 적용 | 기존 이름 매칭·DOUBLE 수량 등은 유지 | 사용자가 선택 |
| 테이블 전면 재설계 | 명칭·자료형·정규화를 일괄 정비 | 여러 엔티티·API·프론트와 seed 수정이 필요 | 이번 범위에서 제외 |

현재 MySQL 8 계열과 Flyway를 이미 사용하므로 같은 기술을 사용한다.
구현 기준은 MySQL 8.4와 H2 MySQL 호환 모드, JDK 17, 기존 Gradle 구성이다.
CHECK 제약조건을 실제로 강제하는 MySQL 버전을 사용해야 한다.

## 3. 논리 모델과 데이터 소유권

| 테이블 | 책임 | 기본키 / 주요 관계 |
|---|---|---|
| ingredient | 표준 재료, 단위, 보관 기간, 기본 수량 | id; name 유일 |
| ingredient_alias | 동의어·영수증 상품명 변환 | id; ingredient_id → ingredient; alias 유일 |
| avoid_group | 알레르기 분류 기준 | id; name 유일 |
| avoid_group_term | 분류에 포함하는 실제 재료명 | (group_id, sort_no); group_id → avoid_group |
| recipe | 레시피 기본 정보 | id; code 유일 |
| recipe_ingredient | 재료별 분량과 필수 여부 | id; recipe_id → recipe; ingredient_id → ingredient, NULL 허용 |
| recipe_step | 레시피별 조리 순서 | id; recipe_id → recipe |
| scan_class | 모델 버전별 클래스와 표준 재료 연결 | id; (model_version, class_id) 유일; ingredient_id → ingredient |
| users | 회원과 환경 설정 | id; email 유일 |
| user_avoid | 회원별 회피 식재료·분류 | id; user_id → users; (user_id, kind, avoid_value) 유일 |
| fridge | 냉장고 | id |
| fridge_member | 회원과 냉장고의 N:M 연결 | id; fridge_id → fridge; user_id → users; 두 ID 조합 유일 |
| fridge_item | 구매·등록 건별 재료 수량과 소비기한 | id; fridge_id → fridge; ingredient_id → ingredient, NULL 허용 |
| dish | 보관 중인 요리 및 남은 인분 | id; fridge_id → fridge; recipe_id → recipe, NULL 허용 |
| cart_item | 회원별 장보기 목표와 최근 가격 | id; user_id → users; ingredient_id → ingredient, NULL 허용; (user_id, name) 유일 |
| cooking_log | 요리·먹음·버림 사건의 이력 | id; user_id → users; dish_id는 과거 요리 ID 스냅샷 |
| cooking_log_ingredient | 요리 당시 실제 사용 수량과 남은 일수 | id; log_id → cooking_log |
| price_history | 식재료별 쇼핑몰 가격 관측 이력 | id; 이름·가격·관측 시각 스냅샷 |
| scan_feedback | 사용자 인식 수정 기록과 학습 동의 | id; user_id → users 추가, NULL 허용 |

기준 데이터는 seed SQL과 정제 파이프라인으로 관리한다.
회원·냉장고·장보기 데이터는 API로 관리한다. 이력은 서비스 트랜잭션에서 생성한다.
전체 컬럼의 기존 정의는 `backend/src/main/resources/db/migration/V1__schema.sql`이 기준이다.
구현 단계에서 `docs/erd/data-dictionary.md`에 19개 테이블의 컬럼명·자료형·NULL·키·설명을 정리한다.

## 4. 유지할 업무 규칙

- 같은 식재료라도 등록일·소비기한이 다를 수 있으므로 fridge_item에 여러 행을 허용한다.
- 기준표에 없는 재료는 ingredient_id=NULL과 입력 이름으로 저장할 수 있다.
- 등록일 이전 소비기한도 허용한다. 이미 기한이 지난 재료의 등록·수정이 가능해야 한다.
- fridge_item.qty=0은 차감 후 정리되는 중간 상태로 허용한다.
- dish.servings_left=0은 마지막 인분을 먹고 행을 삭제하기 전의 중간 상태로 허용한다.
- 식재료와 요리 삭제 뒤에도 cooking_log와 사용 재료 이력은 남는다.
- cooking_log.dish_id에 외래키를 추가하지 않는다. DishService가 마지막 인분 섭취·폐기 시 dish를 실제 삭제하기 때문이다.
- cooking_log.recipe_code, ingredient_name 등은 당시 표시 내용을 보존하는 스냅샷이다.
- 기존 FK의 삭제 동작은 유지한다. 회원 탈퇴와 보존 기간, 이력 익명화는 이번 변경에서 새로 구현하지 않는다.
- 수량 DOUBLE과 금액 INT(원)는 기존 Java 타입과 호환되도록 유지한다. DECIMAL 전환은 별도 마이그레이션 대상으로 남긴다.
- 현재 이름 기반 레시피 재료 매칭과 쉼표 구분 표시 필드를 유지한다.
- 인식 피드백의 consent=false를 true로 변경하거나 사진을 수집하지 않는다.

## 5. 추가 무결성 규칙

새 `V4__harden_database_integrity.sql`에 아래 제약을 추가한다.
번호는 구현 직전 origin/develop을 갱신해 재확인하며, V4가 사용 중이면 다음 빈 번호를 사용한다.
V1~V3는 수정하지 않는다. 기존 데이터를 자동으로 보정·삭제하지 않는다.

| 제약조건 이름 | 테이블 | 허용 조건 |
|---|---|---|
| ck_ingredient_fridge_days | ingredient | fridge_days >= 0 |
| ck_ingredient_default_qty | ingredient | default_qty > 0 |
| ck_ingredient_each_gram | ingredient | each_gram IS NULL OR each_gram > 0 |
| ck_fridge_item_qty | fridge_item | qty >= 0 |
| ck_dish_servings | dish | servings > 0 |
| ck_dish_servings_left | dish | servings_left >= 0 AND servings_left <= servings |
| ck_cart_target_price | cart_item | target_price IS NULL OR target_price >= 0 |
| ck_cart_lowest_price | cart_item | lowest_price IS NULL OR lowest_price >= 0 |
| ck_cart_notified_price | cart_item | notified_price IS NULL OR notified_price >= 0 |
| ck_cooking_log_amount | cooking_log | amount >= 0 |
| ck_log_ingredient_qty | cooking_log_ingredient | qty >= 0 |
| ck_price_history_price | price_history | price >= 0 |
| ck_scan_class_id | scan_class | class_id >= 0 |
| ck_scan_auto_threshold | scan_class | auto_threshold BETWEEN 0 AND 1 |
| ck_scan_map50 | scan_class | map50 IS NULL OR map50 BETWEEN 0 AND 1 |

`scan_feedback.user_id`는 `users.id`를 참조하는 nullable FK
`fk_feedback_user`를 추가한다. ON DELETE/UPDATE는 명시적으로 NO ACTION으로 한다.
다른 회원 참조와 일치하게 부모 삭제를 막고, 사용자 없는 기록은 NULL로 표현한다.
탈퇴 정책을 추가할 때는 이 FK와 익명화 처리를 함께 재검토한다.

등록 경로 문자열, scan_feedback.score 범위, 회원 권한 등에는 이번에 새로운 CHECK를 추가하지 않는다.
외부 입력 검증이 함께 바뀌면 API 오류 계약에 영향을 주므로 별도 기능으로 다룬다.
기존 NOT NULL과 UNIQUE/FK는 그대로 적용된다.

## 6. 조회와 인덱스 설계

| 새 인덱스 | 컬럼 순서 | 사용하는 기존 조회 |
|---|---|---|
| idx_item_deduct | fridge_item(fridge_id, name, exp_date, id) | 이름별 재고를 소비기한·ID 순서로 차감 |
| idx_log_user_kind_date | cooking_log(user_id, kind, log_date) | 회원의 최근 30일 COOK 이력 |
| idx_log_user_id | cooking_log(user_id, id) | 회원의 최근 기록 8건, ID 역순 |

인덱스는 조회 조건에 근거한 설계이며 성능 향상을 측정했다고 주장하지 않는다.
기존 인덱스는 삭제하지 않는다. idx_item_fridge_name과 새 인덱스의 중복 접두어는
실제 운영 통계·EXPLAIN을 보고 후속 변경에서 정리한다.
MySQL이 FK용 인덱스를 자동 생성할 수 있으므로 FK 컬럼마다 별도 인덱스를 무조건 추가하지 않는다.
날짜만으로 모든 냉장고를 검색하는 알림은 아직 TODO라 전용 인덱스를 추가하지 않는다.

## 7. 마이그레이션과 운영

1. 적용 전 백업 및 기존 Flyway 이력·체크섬을 확인한다.
2. 구현할 읽기 전용 사전 점검 SQL로 위 조건 위반과 피드백 orphan 회원을 조회한다.
3. 위반 건이 있으면 적용을 중단하고 원인별로 정정한 뒤 재점검한다. 자동 삭제는 하지 않는다.
4. 빈 DB에서 V1→V2→V3→V4 전체 적용과, V3 데이터가 있는 DB에 V4 추가 적용을 각각 검증한다.
5. MySQL DDL 전체가 하나의 트랜잭션으로 롤백된다고 가정하지 않는다.
   일부 ALTER가 성공한 후 실패하면 서버 시작을 중단하고 실제 적용된 제약·인덱스와 Flyway 상태를 조사한다.
   단순 재실행·체크섬 변경·무조건 repair를 복구 절차로 사용하지 않는다.
6. 새 마이그레이션 번호와 적용 결과를 브랜치의 운영 문서에 기록한다.

새 로컬 MySQL은 Docker Compose로 독립 실행하도록 구성한다.
기존 개발 DB를 덮어쓰거나 데이터를 삭제하지 않는다. 볼륨을 사용해 재시작 후에도 데이터를 유지한다.
연결 비밀번호는 환경변수로 받고 실제 값을 커밋하지 않는다.
Compose 설정·실행법·사전 점검 SQL·백업/복구 순서는 `docs/erd/operations.md`에 정리한다.
H2 테스트 성공과 실제 MySQL 검증 성공을 구분해 기록한다.

## 8. 검증 기준

- 기존 Gradle 전체 테스트 통과: seed 70종, 클래스 33종, 레시피 560건 및 API 흐름 보존.
- 무효한 값의 직접 JDBC INSERT/UPDATE가 CHECK/FK 위반으로 실패한다.
- qty=0, servings_left=0, NULL 가격·NULL each_gram·NULL map50 등 허용 경계값은 성공한다.
- 음수·초과 인분과 음수 가격, 잘못된 회원 FK는 실패한다.
- 미등록 재료, 동일 재료의 여러 소비기한, 과거 소비기한은 저장할 수 있다.
- 실제 dish 삭제 후 cooking_log가 남으며 FK 추가로 기존 삭제 흐름이 깨지지 않는다.
- 기존 seed가 새 제약을 만족하며 V1~V3 변경 없이 업그레이드된다.
- 새 인덱스가 존재하고 컬럼 순서가 설계와 일치한다.
- 사전 점검 SQL이 정상 DB에서는 위반을 반환하지 않고 의도적으로 만든 무효 데이터를 찾아낸다.
- 새 MySQL 인스턴스에서 전체/증분 마이그레이션을 검증한다. Docker 데몬 등 환경 제약으로
  실행하지 못하면 미검증 사실을 명시하고 실행 절차를 남긴다.
- git diff --check와 비밀 파일 추적 검사를 통과한다.

## 9. 구현 담당자에게 맡기는 선택과 제외 범위

위 업무 규칙·제약·컬럼 순서·호환성은 고정한다. 테스트 픽스처 ID,
사전 점검 결과의 출력 형식, Compose 서비스명, 문서 목차 등은 구현자가 결정한다.
애플리케이션의 동시 차감·공유 냉장고 권한·회원 탈퇴·알림 재시도·외부 API 품질은 별도 작업이다.
CHECK만으로 동시 요청의 lost update나 중복 소비를 해결했다고 주장하지 않는다.

## 10. 승인 후 작업 순서

1. 새 브랜치 생성과 검증 가능한 구현 계획 작성.
2. 기존 스키마에서 실패하는 DB 무결성 테스트 작성·실행.
3. 추가 마이그레이션, 사전 점검 SQL, 운영 구성 작성.
4. 전체 테스트와 MySQL 검증, 컬럼 사전·ERD·운영 안내 갱신.
5. diff 검토 후 커밋하고 origin의 새 브랜치로 push.

main/develop에는 직접 push하지 않으며, 병합·배포는 이 작업에 포함하지 않는다.

## 11. 구현 검증 기록 (2026-10-28)

- 실제 V4에 CHECK 15개, 회원 FK 1개, 인덱스 3개를 구현했다.
- H2 전체 Gradle 테스트 통과. 사전 점검 테스트는 실제 V3 DB에 위반 데이터를 넣어 탐지 결과를 검증한다.
- MySQL 8.4의 빈 전용 DB에서 V3→V4 업그레이드, fixture 보존 및 JDBC 무결성 26개 테스트 통과.
- 별도 빈 MySQL DB에서 V1~V4 일괄 적용과 기존 Spring seed/API 흐름 테스트 통과.
- MySQL에서 사전 점검 SQL 결과 0행. 기존 V1~V3는 변경하지 않았다.
- 성능 개선 측정과 실제 운영 데이터 적용은 하지 않았다.
