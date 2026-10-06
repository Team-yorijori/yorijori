-- =====================================================================
-- 요리조리 스키마 v1 (데모 v9 기준)
-- MySQL 8 · H2(MySQL 모드) 둘 다에서 돈다. 표준 SQL 위주로 쓰고 엔진·문자셋 옵션은 DB 기본값(utf8mb4)을 따른다.
--   CREATE DATABASE yorijori CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
-- 규칙: 이미 반영된 V 파일은 고치지 않는다. 바꿀 것은 V{다음 번호}__설명.sql 로 추가한다.
-- 그룹: [기준] 팀이 seed SQL로 관리 · [사용자] 회원 데이터 · [기록] 통계·재학습용
-- =====================================================================

-- [기준] 재료 기준표 (데모 MASTER)
CREATE TABLE ingredient (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(50)  NOT NULL,
  category     VARCHAR(20)  NOT NULL,          -- 채소 · 과일 · 육류 · 해산물 · 유제품·알 · 가공식품 · 반찬 · 곡류 · 기타
  fridge_days  INT          NOT NULL,          -- 냉장 보관 일수 (소비기한 자동 안내, 참고용)
  unit         VARCHAR(10)  NOT NULL,
  default_qty  DOUBLE       NOT NULL,
  color        VARCHAR(7),                     -- 접시 그림 색
  each_gram    INT,                            -- 영수증 무게 → 개수 환산 (1개당 g)
  CONSTRAINT uk_ingredient_name UNIQUE (name)
);

-- [기준] 동의어·상품명 표기 (달걀 → 계란, 삼겹 → 돼지고기)
CREATE TABLE ingredient_alias (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  ingredient_id  BIGINT       NOT NULL,
  alias          VARCHAR(100) NOT NULL,
  source         VARCHAR(10)  NOT NULL,        -- SYNONYM · RECEIPT
  CONSTRAINT uk_ingredient_alias UNIQUE (alias),
  CONSTRAINT fk_alias_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
);

-- [기준] v9 알레르기 묶음 (식품 알레르기 표시 대상 위주)
CREATE TABLE avoid_group (
  id       BIGINT AUTO_INCREMENT PRIMARY KEY,
  name     VARCHAR(30)  NOT NULL,
  sort_no  INT          NOT NULL,
  warning  VARCHAR(200),
  CONSTRAINT uk_avoid_group_name UNIQUE (name)
);

CREATE TABLE avoid_group_term (
  group_id  BIGINT      NOT NULL,
  sort_no   INT         NOT NULL,
  term      VARCHAR(30) NOT NULL,
  PRIMARY KEY (group_id, sort_no),
  CONSTRAINT fk_avoid_term_group FOREIGN KEY (group_id) REFERENCES avoid_group (id)
);

-- [기준] 레시피 (공공 537건 id 1~537 + 데모 레시피 id 1001~)
CREATE TABLE recipe (
  id             BIGINT       PRIMARY KEY,
  code           VARCHAR(40)  NOT NULL,        -- 화면에서 쓰는 id (r1, kimchi-rice …)
  title          VARCHAR(100) NOT NULL,
  description    VARCHAR(500),
  cook_time_min  INT,
  difficulty     VARCHAR(20),                  -- 초보환영 · 보통 · 어려움 · 쉬움
  servings       INT,
  category       VARCHAR(50),                  -- 밥 · 국 · 찌개/전골/스튜 · 볶음 …
  cuisine        VARCHAR(30),                  -- 한식 · 서양 · 중국 · 일본 …
  kcal           VARCHAR(20),
  source         VARCHAR(100),
  video_id       VARCHAR(20),                  -- YouTube 대표 영상 (YoutubeVideoCollector)
  storage_days   INT,                          -- 만든 요리 냉장 보관 일수 (참고용)
  image_url      VARCHAR(500),
  CONSTRAINT uk_recipe_code UNIQUE (code)
);

CREATE TABLE recipe_ingredient (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  recipe_id        BIGINT       NOT NULL,
  ingredient_id    BIGINT,                     -- 기준표에 있으면 연결
  ingredient_name  VARCHAR(50)  NOT NULL,      -- 표준 재료명. 냉장고 재료와 이 이름으로 매칭
  amount           DOUBLE,                     -- 냉장고 단위 수량 (차감 기본값)
  amount_text      VARCHAR(200),               -- 원래 표기 (양지머리 100g)
  ingredient_type  VARCHAR(10)  NOT NULL,      -- MAIN · SUB · SEASONING
  is_optional      BOOLEAN      NOT NULL,
  sort_no          INT          NOT NULL,
  CONSTRAINT fk_ri_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (id),
  CONSTRAINT fk_ri_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
);
CREATE INDEX idx_ri_recipe ON recipe_ingredient (recipe_id);
CREATE INDEX idx_ri_name ON recipe_ingredient (ingredient_name);

CREATE TABLE recipe_step (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  recipe_id  BIGINT        NOT NULL,
  step_no    INT           NOT NULL,
  content    VARCHAR(2000) NOT NULL,
  CONSTRAINT fk_step_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (id)
);
CREATE INDEX idx_step_recipe ON recipe_step (recipe_id);

-- [기준] 인식 모델 클래스 ↔ 재료 (모델 버전별) · v9 재료별 인식 기준
CREATE TABLE scan_class (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  model_version   VARCHAR(10)  NOT NULL,       -- v3 · v4
  class_id        INT          NOT NULL,       -- 모델 출력 classId
  en_name         VARCHAR(40)  NOT NULL,
  ingredient_id   BIGINT       NOT NULL,
  auto_threshold  DOUBLE       NOT NULL,       -- 이 점수 이상이면 자동 체크
  confuse_with    VARCHAR(100),                -- "혹시 ○○?" 버튼 (쉼표 구분)
  map50           DOUBLE,                      -- 검증 mAP50 (참고)
  CONSTRAINT uk_scan_class UNIQUE (model_version, class_id),
  CONSTRAINT fk_scan_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
);

-- [사용자] 회원
CREATE TABLE users (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  email          VARCHAR(100) NOT NULL,
  password_hash  VARCHAR(100) NOT NULL,
  nickname       VARCHAR(30)  NOT NULL,
  role           VARCHAR(10)  NOT NULL,
  avoid_show     BOOLEAN      NOT NULL DEFAULT FALSE,   -- v9 못 먹는 재료: 빼지 않고 표시만
  anim_on        BOOLEAN      NOT NULL DEFAULT TRUE,    -- v7 애니메이션
  created_at     DATETIME,
  CONSTRAINT uk_users_email UNIQUE (email)
);

-- [사용자] v9 못 먹는 재료 (GROUP: 알레르기 묶음 이름 / ITEM: 직접 넣은 재료)
CREATE TABLE user_avoid (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id      BIGINT      NOT NULL,
  kind         VARCHAR(10) NOT NULL,
  avoid_value  VARCHAR(50) NOT NULL,
  CONSTRAINT uk_user_avoid UNIQUE (user_id, kind, avoid_value),
  CONSTRAINT fk_avoid_user FOREIGN KEY (user_id) REFERENCES users (id)
);

-- [사용자] 냉장고와 구성원 (가족 공유 대비)
CREATE TABLE fridge (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  created_at  DATETIME
);

CREATE TABLE fridge_member (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  fridge_id  BIGINT      NOT NULL,
  user_id    BIGINT      NOT NULL,
  role       VARCHAR(10) NOT NULL,             -- OWNER · MEMBER
  CONSTRAINT uk_fridge_member UNIQUE (fridge_id, user_id),
  CONSTRAINT fk_member_fridge FOREIGN KEY (fridge_id) REFERENCES fridge (id),
  CONSTRAINT fk_member_user FOREIGN KEY (user_id) REFERENCES users (id)
);
CREATE INDEX idx_member_user ON fridge_member (user_id);

-- [사용자] 냉장고 재료
CREATE TABLE fridge_item (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  fridge_id      BIGINT      NOT NULL,
  ingredient_id  BIGINT,
  name           VARCHAR(50) NOT NULL,
  qty            DOUBLE      NOT NULL,
  unit           VARCHAR(10) NOT NULL,
  reg_date       DATE        NOT NULL,
  exp_date       DATE        NOT NULL,
  exp_auto       BOOLEAN     NOT NULL,          -- TRUE: 보관 일수로 계산한 참고용 날짜
  source         VARCHAR(10) NOT NULL,          -- MANUAL · SCAN · RECEIPT · CART
  created_at     DATETIME,
  CONSTRAINT fk_item_fridge FOREIGN KEY (fridge_id) REFERENCES fridge (id),
  CONSTRAINT fk_item_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
);
CREATE INDEX idx_item_fridge_exp ON fridge_item (fridge_id, exp_date);
CREATE INDEX idx_item_fridge_name ON fridge_item (fridge_id, name);

-- [사용자] 만든 요리 (v8)
CREATE TABLE dish (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  fridge_id      BIGINT       NOT NULL,
  recipe_id      BIGINT,
  recipe_code    VARCHAR(40),
  name           VARCHAR(100) NOT NULL,
  servings       INT          NOT NULL,
  servings_left  INT          NOT NULL,
  made_date      DATE         NOT NULL,
  exp_date       DATE         NOT NULL,
  colors         VARCHAR(100),
  saved_names    VARCHAR(500),                  -- 이 요리로 살린 임박 재료
  created_at     DATETIME,
  CONSTRAINT fk_dish_fridge FOREIGN KEY (fridge_id) REFERENCES fridge (id),
  CONSTRAINT fk_dish_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (id)
);
CREATE INDEX idx_dish_fridge ON dish (fridge_id, exp_date);

-- [사용자] 장보기 (v6)
CREATE TABLE cart_item (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id            BIGINT      NOT NULL,
  ingredient_id      BIGINT,
  name               VARCHAR(50) NOT NULL,
  target_price       INT,
  notify             BOOLEAN     NOT NULL DEFAULT TRUE,
  lowest_price       INT,
  lowest_shop        VARCHAR(30),
  lowest_url         VARCHAR(500),
  lowest_checked_at  DATETIME,
  notified_price     INT,
  created_at         DATETIME,
  CONSTRAINT uk_cart_user_name UNIQUE (user_id, name),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_cart_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
);
CREATE INDEX idx_cart_name ON cart_item (name);

-- [기록] 요리 기록 (COOK · EAT · TOSS · TOSS_ING)
CREATE TABLE cooking_log (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id      BIGINT       NOT NULL,
  kind         VARCHAR(10)  NOT NULL,
  recipe_code  VARCHAR(40),
  dish_id      BIGINT,
  name         VARCHAR(100) NOT NULL,
  amount       DOUBLE       NOT NULL,          -- 인분 또는 재료 수량
  saved_names  VARCHAR(500),
  log_date     DATE         NOT NULL,
  created_at   DATETIME,
  CONSTRAINT fk_log_user FOREIGN KEY (user_id) REFERENCES users (id)
);
CREATE INDEX idx_log_user_date ON cooking_log (user_id, log_date);

CREATE TABLE cooking_log_ingredient (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  log_id           BIGINT      NOT NULL,
  ingredient_name  VARCHAR(50) NOT NULL,
  qty              DOUBLE      NOT NULL,
  days_left        BIGINT,                     -- 그때 남은 소비기한 일수
  CONSTRAINT fk_logi_log FOREIGN KEY (log_id) REFERENCES cooking_log (id)
);

-- [기록] 가격 이력 (네이버 쇼핑, 쿠팡은 승인 후)
CREATE TABLE price_history (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  ingredient_name  VARCHAR(50)  NOT NULL,
  channel          VARCHAR(20)  NOT NULL,
  mall_name        VARCHAR(50),
  price            INT          NOT NULL,
  product_title    VARCHAR(300),
  product_url      VARCHAR(500),
  checked_at       DATETIME     NOT NULL
);
CREATE INDEX idx_price_name_time ON price_history (ingredient_name, checked_at);

-- [기록] 인식 결과 수정 기록 (재학습 동의 여부 포함, 사진은 저장하지 않는다)
CREATE TABLE scan_feedback (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id        BIGINT,
  model_version  VARCHAR(10) NOT NULL,
  predicted      VARCHAR(50) NOT NULL,
  corrected      VARCHAR(50) NOT NULL,
  score          DOUBLE,
  consent        BOOLEAN     NOT NULL,
  created_at     DATETIME
);
CREATE INDEX idx_feedback_pair ON scan_feedback (predicted, corrected);
