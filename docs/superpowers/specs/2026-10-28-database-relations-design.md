# DB 관계·이력 보완 설계

사용자가 기존 검토에서 확인한 부족 사항의 해결과 한국어 커밋을 위임했다.
기존 Loe/db-design 브랜치, Spring Boot/JPA/Flyway/MySQL 8.4/H2를 유지한다.
기존 구조를 확장하는 V5를 선택한다. 전면 재설계는 기존 API·seed와 충돌하므로 하지 않는다.

## 완료 범위

1. user_avoid_group: id BIGINT PK auto, user_id FK users, group_id FK avoid_group,
   UNIQUE(user_id,group_id). GROUP 선택을 이관하고 user_avoid에는 ITEM만 남긴다.
   알 수 없는 기존 GROUP은 NOT NULL 이관 실패로 중단한다. 선택을 조용히 버리지 않는다.
   GET/PUT /api/me/avoid의 그룹 이름 배열 계약은 유지하고 이름 변경 뒤에도 ID 관계를 유지한다.
2. inventory_movement: 재고 등록·수량 수정·요리 차감·폐기를 기록한다.
   id BIGINT PK auto, fridge_id BIGINT NOT NULL FK fridge(NO ACTION),
   fridge_item_id BIGINT nullable FK fridge_item(SET NULL), item_ref_id BIGINT NOT NULL snapshot,
   ingredient_id BIGINT nullable FK ingredient(SET NULL), actor_user_id BIGINT nullable FK users(SET NULL),
   cooking_log_id BIGINT nullable FK cooking_log(SET NULL), item_name VARCHAR(50), unit VARCHAR(10),
   event_type VARCHAR(16): OPENING/ADD/ADJUST/COOK/TOSS,
   qty_before/qty_after/qty_delta DOUBLE NOT NULL, source VARCHAR(10) nullable,
   occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
   before/after >=0, ABS(qty_delta-(qty_after-qty_before))<0.000001.
   기존 재고는 OPENING(0→현재 수량)으로 이관하고 과거 변경 이력은 만들지 않는다.
   ADD는 0→재고, COOK/TOSS는 감소, ADJUST는 실제 변화만 기록한다.
   모든 이벤트는 재고 변경과 같은 트랜잭션에서 저장한다. 재고 삭제 뒤에도 snapshot과 이력을 보존한다.
   수량 변경은 행 잠금으로 직렬화한다. 냉장고 소유권은 기존 서비스 검증을 유지한다.
3. product: id BIGINT PK auto, channel VARCHAR(20), external_id VARCHAR(100),
   title VARCHAR(300), product_url VARCHAR(500) nullable,
   ingredient_id BIGINT nullable FK ingredient(SET NULL),
   package_qty DECIMAL(12,3) nullable, package_unit VARCHAR(20) nullable,
   UNIQUE(channel,external_id), 패키지 정보는 둘 다 NULL 또는 수량 양수·단위 필수.
   가격 수집 응답의 상품 ID가 있을 때 동일 채널·ID를 재사용한다. ID가 없으면 product_id=NULL로 이력을 보존한다.
   포장 수량을 상품 제목에서 추정하지 않는다. 무게당 최저가를 구현했다고 주장하지 않는다.
   price_history에 ingredient_id와 product_id nullable FK(SET NULL)를 추가한다.
4. scan_model: version VARCHAR(10) PK, display_name VARCHAR(100) NOT NULL,
   artifact_path VARCHAR(500) nullable, released_at DATETIME nullable,
   created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
   기존 scan_class/scan_feedback의 version은 모두 레지스트리에 이관하고 두 테이블에서 FK로 참조한다.
   scan_feedback에 predicted_class_id(nullable FK scan_class SET NULL),
   corrected_ingredient_id(nullable FK ingredient SET NULL)를 추가한다.
   새 피드백은 등록된 모델 버전을 검증하며 원문 predicted/corrected를 유지한다.
   표준명·동의어로 확실히 확인되는 재료만 연결하고 모델 클래스 매칭이 모호하면 NULL로 둔다.
5. cooking_log.fridge_id nullable FK fridge SET NULL을 추가한다.
   살아 있는 dish에서 알 수 있는 과거 기록만 backfill하고 나머지는 NULL로 보존한다.
   앞으로 생성하는 COOK/EAT/TOSS/TOSS_ING에는 실제 냉장고를 기록한다.
   cooking_log_ingredient.ingredient_id nullable FK ingredient SET NULL도 추가한다.
   기존 이름과 수량을 보존하고 표준명과 정확히 일치하는 과거 재료만 연결한다.

## 유지할 동작

미등록 재료, 동일 이름의 여러 소비기한, 과거 소비기한, 0 수량의 삭제 전 상태,
마지막 인분 삭제 후 요리 기록, 기존 API 응답을 유지한다. 기존 V1~V4는 수정하지 않는다.
테스트의 V4 전용 검증은 target(4)를 고정해 이전 계약을 계속 검증한다.
새 V5는 빈 DB와 V4 데이터가 있는 DB에서 검증한다.

## 검증·문서·완료

- 이관 시 기존 그룹·재고·가격·피드백·요리 이력이 보존되는지 JDBC 테스트.
- 이름 변경 이후 알레르기 선택·추천 유지, 잘못된 설정 전체 롤백 테스트.
- 재고 등록→수정→요리→폐기 이벤트, FK 삭제 후 snapshot 보존, 트랜잭션 롤백 테스트.
- 수집 상품 ID 재사용과 가격 이력 연결, 모델 등록 검증과 피드백 원문 보존 테스트.
- H2 전체 테스트 및 격리된 MySQL 8.4 전체/증분 마이그레이션·API 검증.
- ERD, 컬럼 사전, 새 migration 사전 점검 및 API의 검증 오류 안내 갱신.
- 독립 최종 검토 후 한국어 메시지로 커밋한다. 원격 push의 기존 인증 문제는 별도이며 commit 완료와 구분한다.

## 구현 중 확인한 경계 사례와 처리

- 기존 take는 실제 재고가 반올림 후 그대로여도 요청량을 차감으로 반환했다. 실제 전후 차이를 반환하도록 수정했다.
- 같은 재고를 동시에 수정할 때 원장 전후 수량이 연결되도록 PESSIMISTIC_WRITE를 적용했다.
- 직접 입력 회피 재료는 trim 이후 중복을 합치고 NULL·빈 입력을 제외한다. 분류 설정 오류는 전체를 롤백한다.
- 외부 상품 ID는 자르지 않는다. 없거나 공백이거나 100자를 넘으면 상품 참조 없이 가격 관측을 보존한다.
- 상품 포장 수량 자동 추정, 무게당 가격 비교, 회원 탈퇴 UI, 신규 원장 조회 API는 이번 작업 범위가 아니다.

## 검증 기록

- H2 전체 74개 테스트 통과. 기존 API·seed·V4 회귀와 V5 이관·서비스 연동을 함께 검증했다.
- MySQL 8.4의 V4→V5 이관 테스트 6개 통과.
- 별도 빈 MySQL에서 Spring mysql 프로필 전체 74개 테스트 통과. 독립 JDBC 테스트 중 자체 H2 사용 항목도 포함한다.
- 미지의 기존 GROUP은 사전 점검에 표시되고, V5 실패 뒤에도 원래 선택 행이 남는 것을 검증했다.
- 행 잠금을 제거한 회귀 실행은 동시 변경 원장 연결 불일치로 실패했고, 복원 후 통과했다.
- 원장·재고의 동시 롤백과 삭제 후 snapshot 보존을 검증했다.
