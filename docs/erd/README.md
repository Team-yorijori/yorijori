# DB 설계와 ERD (Flyway V4)

기존 19개 테이블과 API를 유지하면서 수량·가격·인분의 무결성과 회원 참조를 보완한다.

- [보완 설계서](../superpowers/specs/2026-10-28-database-design.md): 업무 규칙, 제약조건, 조회 설계와 변경 근거
- [컬럼 사전](data-dictionary.md): 19개 테이블의 타입·NULL·키·기본값·설명
- [운영 안내](operations.md): MySQL 실행, 사전 점검, 백업·복구, 테스트
- [사전 점검 SQL](preflight.sql): V4 적용 전 위반 데이터 조회
- [ERD Mermaid 원본](erd.mmd): V1 + V4의 실제 FK 관계

![ERD](erd.png)

이미지를 확대하면 컬럼을 읽을 수 있다. `erd_초안.*`는 기획 단계 참고 자료이다.

## 데이터 그룹

| 그룹 | 테이블 | 관리 주체 |
|---|---|---|
| 기준 | ingredient, ingredient_alias, avoid_group, avoid_group_term, recipe, recipe_ingredient, recipe_step, scan_class | 팀: Flyway seed SQL |
| 사용자 | users, user_avoid, fridge, fridge_member, fridge_item, dish, cart_item | API |
| 기록 | cooking_log, cooking_log_ingredient, price_history, scan_feedback | 시스템 |

## 주요 설계 결정

- 미등록 재료의 ingredient_id는 NULL을 허용하며 입력 이름을 함께 저장한다.
- 같은 재료라도 소비기한이 다르면 fridge_item에 별도 행으로 보관한다.
- fridge_member로 회원과 냉장고를 연결해 가족 공유로 확장할 수 있다.
- dish는 냉장고 단위, cooking_log는 회원 단위로 관리한다.
- 요리를 모두 먹거나 버리면 dish가 삭제된다. cooking_log.dish_id는 당시 ID 스냅샷이며 FK를 두지 않는다.
- scan_feedback.user_id는 NULL 허용 FK이다. 존재하지 않는 회원 ID는 거절하고 참조 중인 회원의 삭제는 차단한다.
- 레시피 재료 매칭은 기존 표준 이름을 사용한다. 식재료 동의어는 ingredient_alias에서 변환한다.
- user_avoid와 avoid_group_term은 못 먹는 재료를 분류·이름으로 매칭한다.
- 데이터 변경 시 이미 머지된 V1~V3는 수정하지 않고 새 마이그레이션을 추가한다.

## V4 추가 사항

CHECK 15개, 피드백 회원 FK 1개, 복합 인덱스 3개를 추가한다.

- 수량·가격은 음수를 차단한다. 기본 수량과 만든 인분은 양수여야 한다.
- 남은 인분은 0 이상 원래 인분 이하이며, 모델 인식 기준·mAP50은 0~1이다.
- 수량·남은 인분의 0은 삭제 전 중간 상태로 허용한다.
- 과거 소비기한과 nullable 값은 기존대로 허용한다.
- 이름별 소비기한 순 차감, 최근 COOK 기록, 최신 기록 목록의 조회 조건을 지원한다.

## 검증 결과 (2026-10-28)

- H2: 기존 API·seed 테스트와 JDBC DB 무결성·사전 점검 테스트 통과.
- MySQL 8.4: 빈 전용 DB의 V3→V4 업그레이드와 데이터 보존, 26개 JDBC 테스트 통과.
- 별도 빈 MySQL DB: V1~V4 전체 초기화, seed 로딩 및 Spring API 흐름 테스트 통과.
- MySQL에서 사전 점검 SQL 결과 0행 확인.

수행 환경의 검증 결과이며 운영 데이터에 대한 점검·성능 측정을 대체하지 않는다.

## ERD 재생성

Mermaid CLI와 Chrome/Chromium이 있는 환경에서 프로젝트 루트 기준으로 실행한다.

```bash
npx --yes @mermaid-js/mermaid-cli@11.12.0 -i docs/erd/erd.mmd -o docs/erd/erd.png -w 2400 -s 3 -b white
```

CLI가 Chrome을 찾지 못하면 `-p`로 Puppeteer의 executablePath 설정 JSON을 지정한다.
