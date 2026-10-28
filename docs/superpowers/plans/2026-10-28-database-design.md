# DB 보완 설계 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 API와 호환되는 DB 무결성·조회·운영 구성을 검증하고 새 브랜치에 push한다.

**Architecture:** V1~V3는 유지하고 V4에 CHECK 15개, nullable 회원 FK, 인덱스 3개를 추가한다. JDBC/Flyway 테스트는 실제 SQL을 실행하고 H2 및 선택한 빈 MySQL 테스트 DB를 검증한다.

**Tech Stack:** JDK 17, Spring Boot 3.5.6, Flyway, H2, MySQL 8.4, Docker Compose.

**Spec:** docs/superpowers/specs/2026-10-28-database-design.md

## Global Constraints

- 기존 19개 테이블·Java 타입·API 형식 유지.
- V1~V3 수정 금지; 최신 develop에서 V4 번호 재확인.
- 수량 0·잔여 인분 0·과거 소비기한·미등록 재료 허용.
- dish 삭제 후 cooking_log 보존; cooking_log.dish_id FK 추가 금지.
- 실제 비밀번호 커밋 금지; 기존 데이터 자동 보정·삭제 금지.
- 사용자 지정 /Users/leo/VibeCodingProjects/Yorijori에서 Loe/db-design 브랜치로 작업.

## Review Focus

- CHECK 추가 시 기존 seed와 V3 실데이터가 손상되지 않는지: Task 1의 증분 migration·fixture 보존 검증.
- 값이 0인 중간 상태로 인해 API 삭제가 실패하는지: Task 1 경계값·기존 ApiFlowTest.
- FK가 추가되며 NULL 피드백이 막히거나 이력이 사라지는지: Task 1 nullable FK·dish 삭제 테스트.
- MySQL과 H2의 DDL·FK 동작 차이: Task 1 같은 JDBC 테스트를 빈 MySQL DB에서 실행.
- 사전 점검이 잘못된 값을 놓치는지: Task 2 V3 fixture를 이용해 SQL 결과 확인.

---

### Task 1: DB 제약과 마이그레이션

**Files:**
- Create: backend/src/test/java/com/yorijori/database/DatabaseIntegrityTest.java
- Create: backend/src/main/resources/db/migration/V4__harden_database_integrity.sql

**Interfaces:**
- Consumes: V1~V3, 19개 테이블과 기존 컬럼.
- Produces: 설계서의 named CHECK 15개, fk_feedback_user, 인덱스 3개.
- Test DB: 기본 H2; YORIJORI_TEST_DB_URL/USERNAME/PASSWORD 지정 시 반드시 빈 별도 MySQL DB.

- [ ] Step 1: INSERT/UPDATE 음수·범위 초과 거절, 허용 경계값, nullable FK, 고아 회원 거절, 스냅샷 보존 테스트 작성.
- [ ] Step 2: `cd backend && bash ./gradlew test --tests '*DatabaseIntegrityTest' --no-daemon` 실행.
  Expected: 제약 부재로 ASSERTION 실패. 컴파일·설정 오류는 먼저 해결.
- [ ] Step 3: V4 SQL 구현. 테스트에서 V3에 유효 fixture 삽입 → 최신 migrate → fixture 보존과 Flyway 4 확인.
- [ ] Step 4: 같은 명령 및 전체 `bash ./gradlew test --no-daemon` 실행.
  Expected: 모든 테스트 통과, seed 70/33/560 유지.
- [ ] Step 5: `git add`로 이 작업 파일과 승인된 spec/plan을 명시해 커밋.

### Task 2: 사전 점검과 MySQL 운영 구성

**Files:**
- Create: docs/erd/preflight.sql
- Create: compose.db.yml
- Create: backend/src/test/java/com/yorijori/database/DatabasePreflightTest.java
- Create: docs/erd/operations.md

**Interfaces:**
- Consumes: Task 1의 V4 제약 조건.
- Produces: rule_name, row_id를 반환하는 읽기 전용 점검 SQL, MySQL 8.4 영속 볼륨·healthcheck, 실행·복구 안내.

- [ ] Step 1: V3 DB에 무효 수량·가격·인분·모델 점수·고아 회원을 삽입하고 점검이 각 위반을 반환하는 테스트 작성.
- [ ] Step 2: 테스트 실행; Expected: 점검 SQL 부재로 실패.
- [ ] Step 3: UNION ALL 점검 SQL과 Docker Compose 작성. root 비밀번호는 환경변수 필수, 포트는 127.0.0.1, 볼륨 유지.
- [ ] Step 4: preflight 테스트·전체 suite·`docker compose -f compose.db.yml config --quiet` 실행.
  Expected: 정상 DB 무위반, fixture 위반 탐지, Compose 유효.
- [ ] Step 5: Docker 데몬 사용 가능하면 새 전용 테스트 DB에서 Task 1 suite 실행. 기존 DB는 사용하지 않는다. 불가하면 명시.
- [ ] Step 6: 이 작업 파일만 커밋.

### Task 3: 설계 문서·ERD와 최종 검증·push

**Files:**
- Create: docs/erd/data-dictionary.md
- Modify: docs/erd/README.md, docs/erd/erd.mmd, docs/erd/erd.png
- Modify: docs/superpowers/specs/2026-10-28-database-design.md (구현 상태·검증 결과)

**Interfaces:**
- Consumes: V1 컬럼과 V4 제약·FK·인덱스.
- Produces: 일치하는 컬럼 사전, nullable 관계를 반영한 ERD, 검증 결과.

- [ ] Step 1: V1에서 19개 테이블 컬럼 사전 작성; V4 규칙과 참조 링크 추가.
- [ ] Step 2: Mermaid의 선택 관계 수정 및 피드백 회원 관계 추가; PNG를 새 Mermaid에서 렌더링.
- [ ] Step 3: 전체 테스트·git diff --check·비밀 파일 검사·V1~V3 diff 검증.
  Expected: 전체 통과, 기존 migration diff 없음.
- [ ] Step 4: 새 검토자가 전체 diff와 spec/plan을 검토. 중요한 문제는 회귀 테스트 후 수정하고 전체 suite 실행.
- [ ] Step 5: 문서와 최종 변경 커밋 후 `git push -u origin Loe/db-design`.
  Expected: 원격 브랜치와 로컬 HEAD SHA 일치; main/develop 변경 없음.
