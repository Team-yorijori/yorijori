-- recipe_seed.sql 을 넣기 위한 레시피 테이블 (MySQL 8)
CREATE TABLE recipes (
  recipe_id      BIGINT PRIMARY KEY,
  title          VARCHAR(100) NOT NULL,
  description    VARCHAR(500),
  cook_time_min  INT,
  difficulty     VARCHAR(20),          -- 초보환영 / 보통 / 어려움
  servings       INT,
  category       VARCHAR(50),          -- 밥, 국, 볶음 ...
  cuisine        VARCHAR(30),          -- 한식, 서양 ...
  image_url      VARCHAR(500)
);

CREATE TABLE recipe_ingredients (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  recipe_id        BIGINT NOT NULL,
  ingredient_name  VARCHAR(50) NOT NULL, -- 표준 재료명 (예: 소고기, 고추). 냉장고 재료와 이 이름으로 매칭
  amount           DECIMAL(10,2),        -- 냉장고 단위로 환산한 수량 (차감용 기본값)
  amount_text      VARCHAR(200),         -- 원래 표기 (예: 양지머리 100g)
  ingredient_type  VARCHAR(10) NOT NULL, -- MAIN / SUB / SEASONING
  is_optional      BOOLEAN NOT NULL,
  INDEX idx_ri_recipe (recipe_id),
  INDEX idx_ri_name (ingredient_name),
  FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
);

CREATE TABLE recipe_steps (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  recipe_id BIGINT NOT NULL,
  step_no   INT NOT NULL,
  content   TEXT NOT NULL,
  FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
);
