# DB 컬럼 사전 (V4)

V1 컬럼 정의 + V4 제약·인덱스 기준, 총 19개 테이블. 기존 타입·NULL·기본값은 변경하지 않는다.

금액 INT는 원 단위, 수량 DOUBLE은 소수 근사값이다. DATETIME은 시간대를 저장하지 않으며 앱에서 Asia/Seoul 기준으로 해석한다.
기본값 `—`는 SQL 기본값 없음이다. AUTO_INCREMENT와 앱의 @CreationTimestamp는 다른 동작이다.

정확한 추가 조건은 [설계서](../superpowers/specs/2026-10-28-database-design.md), 실행은 [운영 안내](operations.md), 관계는 [ERD](erd.mmd)를 참고한다.

## ingredient

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| name | VARCHAR(50) | 아니오 | UNIQUE | — | 표시 이름 |
| category | VARCHAR(20) | 아니오 | — | — | 채소 · 과일 · 육류 · 해산물 · 유제품·알 · 가공식품 · 반찬 · 곡류 · 기타 |
| fridge_days | INT | 아니오 | — | — | 냉장 보관 일수 (소비기한 자동 안내, 참고용) |
| unit | VARCHAR(10) | 아니오 | — | — | 수량 단위 |
| default_qty | DOUBLE | 아니오 | — | — | 입력 생략 시 기본 수량 |
| color | VARCHAR(7) | 예 | — | — | 접시 그림 색 |
| each_gram | INT | 예 | — | — | 영수증 무게 → 개수 환산 (1개당 g) |

## ingredient_alias

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| ingredient_id | BIGINT | 아니오 | FK → ingredient.id | — | 표준 재료 ID |
| alias | VARCHAR(100) | 아니오 | UNIQUE | — | 입력 표기 |
| source | VARCHAR(10) | 아니오 | — | — | SYNONYM · RECEIPT |

## avoid_group

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| name | VARCHAR(30) | 아니오 | UNIQUE | — | 표시 이름 |
| sort_no | INT | 아니오 | — | — | 표시 순서 |
| warning | VARCHAR(200) | 예 | — | — | 알레르기 안내 |

## avoid_group_term

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| group_id | BIGINT | 아니오 | PK; FK → avoid_group.id | — | 분류 ID |
| sort_no | INT | 아니오 | PK | — | 표시 순서 |
| term | VARCHAR(30) | 아니오 | — | — | 매칭할 식재료 표기 |

## recipe

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | — | seed에서 지정하는 레시피 ID(자동 증가 아님) |
| code | VARCHAR(40) | 아니오 | UNIQUE | — | 화면에서 쓰는 id (r1, kimchi-rice …) |
| title | VARCHAR(100) | 아니오 | — | — | 레시피 제목 |
| description | VARCHAR(500) | 예 | — | — | 레시피 소개 |
| cook_time_min | INT | 예 | — | — | 조리 시간(분) |
| difficulty | VARCHAR(20) | 예 | — | — | 초보환영 · 보통 · 어려움 · 쉬움 |
| servings | INT | 예 | — | — | 인분 |
| category | VARCHAR(50) | 예 | — | — | 밥 · 국 · 찌개/전골/스튜 · 볶음 … |
| cuisine | VARCHAR(30) | 예 | — | — | 한식 · 서양 · 중국 · 일본 … |
| kcal | VARCHAR(20) | 예 | — | — | 원본 칼로리 표기 |
| source | VARCHAR(100) | 예 | — | — | 등록 경로·출처 |
| video_id | VARCHAR(20) | 예 | — | — | YouTube 대표 영상 (YoutubeVideoCollector) |
| storage_days | INT | 예 | — | — | 만든 요리 냉장 보관 일수 (참고용) |
| image_url | VARCHAR(500) | 예 | — | — | 대표 이미지 URL |

## recipe_ingredient

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| recipe_id | BIGINT | 아니오 | FK → recipe.id | — | 레시피 ID |
| ingredient_id | BIGINT | 예 | FK → ingredient.id | — | 기준표에 있으면 연결 |
| ingredient_name | VARCHAR(50) | 아니오 | — | — | 표준 재료명. 냉장고 재료와 이 이름으로 매칭 |
| amount | DOUBLE | 예 | — | — | 냉장고 단위 수량 (차감 기본값) |
| amount_text | VARCHAR(200) | 예 | — | — | 원래 표기 (양지머리 100g) |
| ingredient_type | VARCHAR(10) | 아니오 | — | — | MAIN · SUB · SEASONING |
| is_optional | BOOLEAN | 아니오 | — | — | 선택 재료 여부 |
| sort_no | INT | 아니오 | — | — | 표시 순서 |

## recipe_step

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| recipe_id | BIGINT | 아니오 | FK → recipe.id | — | 레시피 ID |
| step_no | INT | 아니오 | — | — | 조리 순서 |
| content | VARCHAR(2000) | 아니오 | — | — | 조리 내용 |

## scan_class

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| model_version | VARCHAR(10) | 아니오 | — | — | v3 · v4 |
| class_id | INT | 아니오 | — | — | 모델 출력 classId |
| en_name | VARCHAR(40) | 아니오 | — | — | 영문 클래스명 |
| ingredient_id | BIGINT | 아니오 | FK → ingredient.id | — | 표준 재료 ID |
| auto_threshold | DOUBLE | 아니오 | — | — | 이 점수 이상이면 자동 체크 |
| confuse_with | VARCHAR(100) | 예 | — | — | "혹시 ○○?" 버튼 (쉼표 구분) |
| map50 | DOUBLE | 예 | — | — | 검증 mAP50 (참고) |

복합 UNIQUE: `(model_version, class_id)`.

## users

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| email | VARCHAR(100) | 아니오 | UNIQUE | — | 로그인 이메일 |
| password_hash | VARCHAR(100) | 아니오 | — | — | 비밀번호 해시 |
| nickname | VARCHAR(30) | 아니오 | — | — | 회원 표시 이름 |
| role | VARCHAR(10) | 아니오 | — | — | 역할 |
| avoid_show | BOOLEAN | 아니오 | — | FALSE | v9 못 먹는 재료: 빼지 않고 표시만 |
| anim_on | BOOLEAN | 아니오 | — | TRUE | v7 애니메이션 |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

## user_avoid

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| user_id | BIGINT | 아니오 | FK → users.id | — | 회원 ID |
| kind | VARCHAR(10) | 아니오 | — | — | 종류 |
| avoid_value | VARCHAR(50) | 아니오 | — | — | 회피 분류·재료명 |

복합 UNIQUE: `(user_id, kind, avoid_value)`.

## fridge

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| name | VARCHAR(50) | 아니오 | — | — | 표시 이름 |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

## fridge_member

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| fridge_id | BIGINT | 아니오 | FK → fridge.id | — | 냉장고 ID |
| user_id | BIGINT | 아니오 | FK → users.id | — | 회원 ID |
| role | VARCHAR(10) | 아니오 | — | — | OWNER · MEMBER |

복합 UNIQUE: `(fridge_id, user_id)`.

## fridge_item

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| fridge_id | BIGINT | 아니오 | FK → fridge.id | — | 냉장고 ID |
| ingredient_id | BIGINT | 예 | FK → ingredient.id | — | 표준 재료 ID |
| name | VARCHAR(50) | 아니오 | — | — | 표시 이름 |
| qty | DOUBLE | 아니오 | — | — | 수량 >= 0; 차감 중 0 허용 |
| unit | VARCHAR(10) | 아니오 | — | — | 수량 단위 |
| reg_date | DATE | 아니오 | — | — | 등록일 |
| exp_date | DATE | 아니오 | — | — | 소비·보관 기한 |
| exp_auto | BOOLEAN | 아니오 | — | — | TRUE: 보관 일수로 계산한 참고용 날짜 |
| source | VARCHAR(10) | 아니오 | — | — | MANUAL · SCAN · RECEIPT · CART |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

## dish

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| fridge_id | BIGINT | 아니오 | FK → fridge.id | — | 냉장고 ID |
| recipe_id | BIGINT | 예 | FK → recipe.id | — | 레시피 ID |
| recipe_code | VARCHAR(40) | 예 | — | — | 레시피 코드 스냅샷 |
| name | VARCHAR(100) | 아니오 | — | — | 표시 이름 |
| servings | INT | 아니오 | — | — | 인분 |
| servings_left | INT | 아니오 | — | — | 0 이상 servings 이하 |
| made_date | DATE | 아니오 | — | — | 요리 생성일 |
| exp_date | DATE | 아니오 | — | — | 소비·보관 기한 |
| colors | VARCHAR(100) | 예 | — | — | 표시 색상 목록(쉼표 구분) |
| saved_names | VARCHAR(500) | 예 | — | — | 이 요리로 살린 임박 재료 |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

## cart_item

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| user_id | BIGINT | 아니오 | FK → users.id | — | 회원 ID |
| ingredient_id | BIGINT | 예 | FK → ingredient.id | — | 표준 재료 ID |
| name | VARCHAR(50) | 아니오 | — | — | 표시 이름 |
| target_price | INT | 예 | — | — | 목표 가격(원) |
| notify | BOOLEAN | 아니오 | — | TRUE | 가격 알림 사용 |
| lowest_price | INT | 예 | — | — | 최근 최저가(원) |
| lowest_shop | VARCHAR(30) | 예 | — | — | 최근 최저가 쇼핑몰 |
| lowest_url | VARCHAR(500) | 예 | — | — | 최근 최저가 상품 URL |
| lowest_checked_at | DATETIME | 예 | — | — | 최근 가격 조회 시각 |
| notified_price | INT | 예 | — | — | 마지막 알림 가격(원) |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

복합 UNIQUE: `(user_id, name)`.

## cooking_log

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| user_id | BIGINT | 아니오 | FK → users.id | — | 회원 ID |
| kind | VARCHAR(10) | 아니오 | — | — | 종류 |
| recipe_code | VARCHAR(40) | 예 | — | — | 레시피 코드 스냅샷 |
| dish_id | BIGINT | 예 | — | — | 당시 요리 ID 스냅샷(FK 없음) |
| name | VARCHAR(100) | 아니오 | — | — | 표시 이름 |
| amount | DOUBLE | 아니오 | — | — | 인분 또는 재료 수량 |
| saved_names | VARCHAR(500) | 예 | — | — | 살린 임박 재료명 목록(쉼표 구분) |
| log_date | DATE | 아니오 | — | — | 기록 날짜 |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |

## cooking_log_ingredient

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| log_id | BIGINT | 아니오 | FK → cooking_log.id | — | 상위 기록 ID |
| ingredient_name | VARCHAR(50) | 아니오 | — | — | 식재료 이름 스냅샷 |
| qty | DOUBLE | 아니오 | — | — | 식재료 수량 |
| days_left | BIGINT | 예 | — | — | 그때 남은 소비기한 일수 |

## price_history

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| ingredient_name | VARCHAR(50) | 아니오 | — | — | 식재료 이름 스냅샷 |
| channel | VARCHAR(20) | 아니오 | — | — | 가격 수집 채널 |
| mall_name | VARCHAR(50) | 예 | — | — | 쇼핑몰명 |
| price | INT | 아니오 | — | — | 관측 가격(원) |
| product_title | VARCHAR(300) | 예 | — | — | 관측 상품명 |
| product_url | VARCHAR(500) | 예 | — | — | 관측 상품 URL |
| checked_at | DATETIME | 아니오 | — | — | 관측 시각 |

## scan_feedback

| 컬럼 | 타입 | NULL 허용 | 키·참조 | DB 기본값 | 설명 |
|---|---|---|---|---|---|
| id | BIGINT | 아니오 | PK | AUTO_INCREMENT | 행 식별자 |
| user_id | BIGINT | 예 | FK → users.id (V4) | — | NULL 허용; V4부터 users 참조·부모 삭제 차단 |
| model_version | VARCHAR(10) | 아니오 | — | — | 모델 버전 |
| predicted | VARCHAR(50) | 아니오 | — | — | 인식 재료명 |
| corrected | VARCHAR(50) | 아니오 | — | — | 수정 재료명 |
| score | DOUBLE | 예 | — | — | 인식 점수 |
| consent | BOOLEAN | 아니오 | — | — | 재학습 사용 동의 |
| created_at | DATETIME | 예 | — | — | 생성 시각(앱 기록) |
