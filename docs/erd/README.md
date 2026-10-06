# ERD (v9 기준 · Flyway V1)

![ERD](erd.png)

- `erd.mmd`: `backend/src/main/resources/db/migration/V1__schema.sql` 에서 만든 Mermaid 원본. 스키마를 바꾸면 다시 만든다
- `erd_초안.*`: 기획 단계 초안 (참고용)

## 그룹

| 그룹 | 테이블 | 누가 바꾸나 |
|---|---|---|
| 기준 | ingredient, ingredient_alias, avoid_group(_term), recipe, recipe_ingredient, recipe_step, scan_class | 팀 (seed SQL, `ai/data/build_seed.py`) |
| 사용자 | users, user_avoid, fridge, fridge_member, fridge_item, dish, cart_item | 사용자 |
| 기록 | cooking_log, cooking_log_ingredient, price_history, scan_feedback | 시스템 (통계·재학습) |

## 설계 메모

- 재료는 `ingredient_id` 로 연결하되, 기준표에 없는 재료도 등록할 수 있게 `name` 을 같이 저장한다 (`fridge_item.ingredient_id` 는 NULL 가능)
- 레시피 재료 매칭은 `recipe_ingredient.ingredient_name` (표준 이름) 기준. 동의어는 등록할 때 `ingredient_alias` 로 표준 이름으로 바꾼다
- 냉장고는 회원과 직접 묶지 않고 `fridge_member` 로 연결 → 가족 공유 냉장고로 넓힐 수 있다
- 만든 요리(`dish`)는 냉장고 단위, 기록(`cooking_log`)은 회원 단위
- v9 못 먹는 재료: `user_avoid`(GROUP/ITEM) + `users.avoid_show`. 묶음 → 실제 이름은 `avoid_group_term`
- v9 재료별 인식 기준: `scan_class.auto_threshold`, `confuse_with`
