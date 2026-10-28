-- V4 데이터에 실행하는 읽기 전용 V5 사전 점검.
-- GROUP 선택의 이름이 기준 분류에 없으면 이관을 중단해야 한다.
SELECT 'unknown_avoid_group' AS rule_name,a.id AS row_id
FROM user_avoid a LEFT JOIN avoid_group g ON g.name=a.avoid_value
WHERE a.kind='GROUP' AND g.id IS NULL
UNION ALL
SELECT 'invalid_avoid_kind',id FROM user_avoid WHERE kind NOT IN ('GROUP','ITEM');
