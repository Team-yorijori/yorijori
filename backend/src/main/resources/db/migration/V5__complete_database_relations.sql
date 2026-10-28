-- 관계와 이력 보완. 기존 migration은 유지한다.
-- 운영 적용 전 쓰기를 멈추고 docs/erd/preflight-v5.sql로 점검한다.

CREATE TABLE user_avoid_group (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    CONSTRAINT uk_user_avoid_group UNIQUE (user_id, group_id),
    CONSTRAINT fk_uag_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_uag_group FOREIGN KEY (group_id) REFERENCES avoid_group(id)
);
-- 이름을 찾지 못하면 group_id NOT NULL 위반으로 중단한다. 선택을 버리지 않는다.
INSERT INTO user_avoid_group (user_id,group_id)
SELECT a.user_id,(SELECT g.id FROM avoid_group g WHERE g.name=a.avoid_value)
FROM user_avoid a WHERE a.kind='GROUP';
DELETE FROM user_avoid WHERE kind='GROUP';
ALTER TABLE user_avoid ADD CONSTRAINT ck_user_avoid_item CHECK (kind='ITEM');

CREATE TABLE scan_model (
    version VARCHAR(10) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    artifact_path VARCHAR(500),
    released_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- 과거 모델의 배포일·파일 경로를 추정하지 않는다.
INSERT INTO scan_model(version,display_name)
SELECT model_version,model_version FROM scan_class
UNION SELECT model_version,model_version FROM scan_feedback;
ALTER TABLE scan_class ADD CONSTRAINT fk_class_model FOREIGN KEY(model_version) REFERENCES scan_model(version);
ALTER TABLE scan_feedback ADD CONSTRAINT fk_feedback_model FOREIGN KEY(model_version) REFERENCES scan_model(version);
ALTER TABLE scan_feedback ADD COLUMN predicted_class_id BIGINT;
ALTER TABLE scan_feedback ADD COLUMN corrected_ingredient_id BIGINT;
ALTER TABLE scan_feedback ADD CONSTRAINT fk_feedback_class FOREIGN KEY(predicted_class_id) REFERENCES scan_class(id) ON DELETE SET NULL;
ALTER TABLE scan_feedback ADD CONSTRAINT fk_feedback_corrected FOREIGN KEY(corrected_ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL;
UPDATE scan_feedback SET predicted_class_id=(
    SELECT MIN(s.id) FROM scan_class s JOIN ingredient i ON i.id=s.ingredient_id
    WHERE s.model_version=scan_feedback.model_version AND i.name=scan_feedback.predicted HAVING COUNT(*)=1
);
UPDATE scan_feedback SET corrected_ingredient_id=(SELECT i.id FROM ingredient i WHERE i.name=scan_feedback.corrected);

CREATE TABLE product (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    channel VARCHAR(20) NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    title VARCHAR(300) NOT NULL,
    product_url VARCHAR(500),
    ingredient_id BIGINT,
    package_qty DECIMAL(12,3),
    package_unit VARCHAR(20),
    CONSTRAINT uk_product_external UNIQUE(channel,external_id),
    CONSTRAINT fk_product_ingredient FOREIGN KEY(ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL,
    CONSTRAINT ck_product_package CHECK (
        (package_qty IS NULL AND package_unit IS NULL) OR
        (package_qty IS NOT NULL AND package_qty>0 AND package_unit IS NOT NULL AND LENGTH(TRIM(package_unit))>0)
    )
);
ALTER TABLE price_history ADD COLUMN ingredient_id BIGINT;
ALTER TABLE price_history ADD COLUMN product_id BIGINT;
ALTER TABLE price_history ADD CONSTRAINT fk_price_ingredient FOREIGN KEY(ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL;
ALTER TABLE price_history ADD CONSTRAINT fk_price_product FOREIGN KEY(product_id) REFERENCES product(id) ON DELETE SET NULL;
UPDATE price_history SET ingredient_id=(SELECT i.id FROM ingredient i WHERE i.name=price_history.ingredient_name);
CREATE INDEX idx_price_product_time ON price_history(product_id,checked_at);

ALTER TABLE cooking_log ADD COLUMN fridge_id BIGINT;
ALTER TABLE cooking_log ADD CONSTRAINT fk_log_fridge FOREIGN KEY(fridge_id) REFERENCES fridge(id) ON DELETE SET NULL;
-- 살아 있는 요리에서 확인되는 냉장고만 이관한다. 현재 회원의 냉장고를 과거 사실로 추정하지 않는다.
UPDATE cooking_log SET fridge_id=(SELECT d.fridge_id FROM dish d WHERE d.id=cooking_log.dish_id);
CREATE INDEX idx_log_fridge_date ON cooking_log(fridge_id,log_date);
ALTER TABLE cooking_log_ingredient ADD COLUMN ingredient_id BIGINT;
ALTER TABLE cooking_log_ingredient ADD CONSTRAINT fk_logi_ingredient FOREIGN KEY(ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL;
UPDATE cooking_log_ingredient SET ingredient_id=(SELECT i.id FROM ingredient i WHERE i.name=cooking_log_ingredient.ingredient_name);

CREATE TABLE inventory_movement (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fridge_id BIGINT NOT NULL,
    fridge_item_id BIGINT,
    item_ref_id BIGINT NOT NULL,
    ingredient_id BIGINT,
    actor_user_id BIGINT,
    cooking_log_id BIGINT,
    item_name VARCHAR(50) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    event_type VARCHAR(16) NOT NULL,
    qty_before DOUBLE NOT NULL,
    qty_after DOUBLE NOT NULL,
    qty_delta DOUBLE NOT NULL,
    source VARCHAR(10),
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movement_fridge FOREIGN KEY(fridge_id) REFERENCES fridge(id),
    CONSTRAINT fk_movement_item FOREIGN KEY(fridge_item_id) REFERENCES fridge_item(id) ON DELETE SET NULL,
    CONSTRAINT fk_movement_ingredient FOREIGN KEY(ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL,
    CONSTRAINT fk_movement_actor FOREIGN KEY(actor_user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_movement_log FOREIGN KEY(cooking_log_id) REFERENCES cooking_log(id) ON DELETE SET NULL,
    CONSTRAINT ck_movement_type CHECK(event_type IN ('OPENING','ADD','ADJUST','COOK','TOSS')),
    CONSTRAINT ck_movement_qty CHECK(qty_before>=0 AND qty_after>=0),
    CONSTRAINT ck_movement_balance CHECK(ABS(qty_delta-(qty_after-qty_before))<0.000001),
    CONSTRAINT ck_movement_direction CHECK(
        (event_type IN ('OPENING','ADD') AND qty_before=0 AND qty_delta>=0) OR
        (event_type IN ('COOK','TOSS') AND qty_delta<=0) OR event_type='ADJUST'
    )
);
CREATE INDEX idx_movement_fridge_time ON inventory_movement(fridge_id,occurred_at,id);
CREATE INDEX idx_movement_log ON inventory_movement(cooking_log_id);
INSERT INTO inventory_movement(fridge_id,fridge_item_id,item_ref_id,ingredient_id,item_name,unit,event_type,qty_before,qty_after,qty_delta,source)
SELECT fridge_id,id,id,ingredient_id,name,unit,'OPENING',0,qty,qty,source FROM fridge_item;
