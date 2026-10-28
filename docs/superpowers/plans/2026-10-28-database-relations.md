# DB 관계·이력 보완 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Independent module implementation follows superpowers:dispatching-parallel-agents; parent owns schema and integration.

**Goal:** 기존 기능에서 누락된 관계와 이력 저장을 실제 서비스에 연결하고 한국어 커밋을 남긴다.
**Architecture:** V5가 4개 신규 테이블과 nullable 참조를 추가·이관한다. 알레르기/상품·모델 모듈은 파일 경계를 나누어 구현하고 재고 흐름과 통합 검증은 부모가 담당한다.
**Tech Stack:** Java 17, Spring Boot 3.5.6, Flyway, MySQL 8.4, H2.
**Spec:** docs/superpowers/specs/2026-10-28-database-relations-design.md

## Global Constraints

- 기존 V1~V4 수정 금지, 미등록 재료와 기록용 원문 보존.
- 기존 API 응답 형식 유지, 기존 수량 0·요리 삭제 동작 유지.
- 추측으로 과거 관계·상품 패키지를 채우지 않음.
- 단일 체크아웃 Loe/db-design에서 작업, 한국어 커밋 메시지.

## Review Focus

- V4 데이터 이관의 누락·모호한 매칭: Task 1 JDBC fixture 검증.
- 그룹 삭제·이름 변경과 설정 롤백: Task 2 서비스 테스트.
- 삭제되는 재고의 원장·요리 기록 보존: Task 3 흐름 테스트.
- 동시 수정의 원장 불일치: Task 3 행 잠금과 동시 수정 테스트.
- 외부 상품 ID·등록되지 않은 모델: Task 4 서비스 테스트.

### Task 1: V5 migration과 기존 계약 검증

Files: V5__complete_database_relations.sql, DatabaseRelationsMigrationTest.java, DatabaseIntegrityTest.java.
Produces: spec의 4개 테이블과 새 FK, 안전한 데이터 이관.
- [x] V4 fixture→V5 이관 검증을 먼저 작성, 기존 DB에서 실패 확인.
- [x] V4 전용 테스트의 target을 4로 고정하고 V5 구현.
- [x] JDBC migration과 기존 테스트 통과 확인.

### Task 2: 알레르기 분류 연결

Files: user/UserService.java, UserAvoidGroup.java, UserAvoidGroupRepository.java, 관련 테스트.
Consumes: user_avoid_group(id,user_id,group_id), 기존 ITEM 데이터.
- [x] 이름 변경·그룹 설정 roundtrip·잘못된 그룹 롤백 테스트 RED.
- [x] ID 기반 그룹 조회/저장/추천 용어 연동, API 형태 유지.
- [x] 테스트 GREEN, 변경 목록 보고. 커밋은 부모가 한국어로 수행.

### Task 3: 재고 원장과 요리 이력 관계

Files: fridge/InventoryMovement*, FridgeService.java, FridgeItemRepository.java, dish/DishService.java, Dish.java, CookingLog.java, CookingLogIngredient.java, 관련 테스트.
Consumes: inventory_movement와 cooking_log.fridge_id, cooking_log_ingredient.ingredient_id.
- [x] 실제 서비스 호출로 ADD/ADJUST/COOK/TOSS·롤백·동시성 테스트 RED.
- [x] 같은 트랜잭션에 이벤트 기록, 행 잠금, 요리/사용재료 FK 설정.
- [x] 전체 흐름 GREEN, 기존 API 테스트 유지.

### Task 4: 상품·모델 레지스트리 연결

Files: cart/Product*, PriceHistory.java, price/*, ingredient/ScanModel*, ScanController.java, ScanFeedback.java, ScanClassRepository.java, dto/ScanFeedbackRequest.java, 관련 테스트.
Consumes: spec의 product/scan_model 및 참조 컬럼.
- [x] 상품 ID 재사용·가격 참조·모델 피드백 검증 테스트 RED.
- [x] 수집 결과와 서비스의 실제 쓰기 연결, 원문 보존.
- [x] 테스트 GREEN. migration/문서는 부모 소유, 커밋은 한국어로 부모가 수행.

### Task 5: 문서·실제 MySQL·검토·커밋

Files: docs/erd/*, docs/api.md, spec/plan.
- [x] H2 전체와 새 빈 MySQL의 전체·증분 migration/API 검증.
- [x] 23개 테이블 ERD·사전·사전 점검 갱신.
- [x] 독립 검토, 중요한 문제 회귀 테스트 후 수정.
- [x] 기존 migration 보존·diff check·비밀파일 검사 후 한국어 커밋.
