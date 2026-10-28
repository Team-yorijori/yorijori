-- 읽기 전용 V4 사전 점검. V3 이상 DB에서 실행한다.
-- 반환 행이 없으면 이 SQL이 검사하는 15개 CHECK 및 회원 FK 조건을 만족한다.
-- 중복 키·권한·문자셋·Flyway 체크섬·동시 쓰기 문제까지 검증하는 것은 아니다.
-- 마이그레이션 중 쓰기를 중지하고, 위반 데이터의 원인을 확인한 뒤 정정한다.
SELECT 'ck_ingredient_fridge_days' AS rule_name, id AS row_id FROM ingredient WHERE fridge_days < 0
UNION ALL
SELECT 'ck_ingredient_default_qty', id FROM ingredient WHERE default_qty <= 0
UNION ALL
SELECT 'ck_ingredient_each_gram', id FROM ingredient WHERE each_gram <= 0
UNION ALL
SELECT 'ck_fridge_item_qty', id FROM fridge_item WHERE qty < 0
UNION ALL
SELECT 'ck_dish_servings', id FROM dish WHERE servings <= 0
UNION ALL
SELECT 'ck_dish_servings_left', id FROM dish WHERE servings_left < 0 OR servings_left > servings
UNION ALL
SELECT 'ck_cart_target_price', id FROM cart_item WHERE target_price < 0
UNION ALL
SELECT 'ck_cart_lowest_price', id FROM cart_item WHERE lowest_price < 0
UNION ALL
SELECT 'ck_cart_notified_price', id FROM cart_item WHERE notified_price < 0
UNION ALL
SELECT 'ck_cooking_log_amount', id FROM cooking_log WHERE amount < 0
UNION ALL
SELECT 'ck_log_ingredient_qty', id FROM cooking_log_ingredient WHERE qty < 0
UNION ALL
SELECT 'ck_price_history_price', id FROM price_history WHERE price < 0
UNION ALL
SELECT 'ck_scan_class_id', id FROM scan_class WHERE class_id < 0
UNION ALL
SELECT 'ck_scan_auto_threshold', id FROM scan_class WHERE auto_threshold < 0 OR auto_threshold > 1
UNION ALL
SELECT 'ck_scan_map50', id FROM scan_class WHERE map50 < 0 OR map50 > 1
UNION ALL
SELECT 'fk_feedback_user', f.id FROM scan_feedback f
LEFT JOIN users u ON u.id = f.user_id
WHERE f.user_id IS NOT NULL AND u.id IS NULL;
