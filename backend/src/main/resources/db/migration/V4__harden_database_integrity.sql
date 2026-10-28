-- 기존 V1~V3를 유지하는 추가 마이그레이션. MySQL 8.4 / H2 MySQL 모드.
-- 기존 데이터가 있다면 먼저 docs/erd/preflight.sql을 실행한다.
-- 위반 데이터는 자동으로 수정하거나 삭제하지 않는다.

ALTER TABLE ingredient ADD CONSTRAINT ck_ingredient_fridge_days CHECK (fridge_days >= 0);
ALTER TABLE ingredient ADD CONSTRAINT ck_ingredient_default_qty CHECK (default_qty > 0);
ALTER TABLE ingredient ADD CONSTRAINT ck_ingredient_each_gram CHECK (each_gram IS NULL OR each_gram > 0);

-- 차감·삭제 트랜잭션의 중간 상태인 0은 허용한다.
ALTER TABLE fridge_item ADD CONSTRAINT ck_fridge_item_qty CHECK (qty >= 0);
ALTER TABLE dish ADD CONSTRAINT ck_dish_servings CHECK (servings > 0);
ALTER TABLE dish ADD CONSTRAINT ck_dish_servings_left CHECK (servings_left >= 0 AND servings_left <= servings);

ALTER TABLE cart_item ADD CONSTRAINT ck_cart_target_price CHECK (target_price IS NULL OR target_price >= 0);
ALTER TABLE cart_item ADD CONSTRAINT ck_cart_lowest_price CHECK (lowest_price IS NULL OR lowest_price >= 0);
ALTER TABLE cart_item ADD CONSTRAINT ck_cart_notified_price CHECK (notified_price IS NULL OR notified_price >= 0);
ALTER TABLE cooking_log ADD CONSTRAINT ck_cooking_log_amount CHECK (amount >= 0);
ALTER TABLE cooking_log_ingredient ADD CONSTRAINT ck_log_ingredient_qty CHECK (qty >= 0);
ALTER TABLE price_history ADD CONSTRAINT ck_price_history_price CHECK (price >= 0);

ALTER TABLE scan_class ADD CONSTRAINT ck_scan_class_id CHECK (class_id >= 0);
ALTER TABLE scan_class ADD CONSTRAINT ck_scan_auto_threshold CHECK (auto_threshold BETWEEN 0 AND 1);
ALTER TABLE scan_class ADD CONSTRAINT ck_scan_map50 CHECK (map50 IS NULL OR map50 BETWEEN 0 AND 1);

-- 회원 없는 기록은 NULL, 존재하지 않는 회원 ID는 거절한다.
ALTER TABLE scan_feedback ADD CONSTRAINT fk_feedback_user
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- cooking_log.dish_id는 삭제된 요리도 가리키는 스냅샷이므로 FK를 추가하지 않는다.
CREATE INDEX idx_item_deduct ON fridge_item (fridge_id, name, exp_date, id);
CREATE INDEX idx_log_user_kind_date ON cooking_log (user_id, kind, log_date);
CREATE INDEX idx_log_user_id ON cooking_log (user_id, id);
