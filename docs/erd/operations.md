# DB 실행·점검·마이그레이션

## 로컬 MySQL 8.4

Docker Desktop과 Docker Compose가 필요하다. 프로젝트 루트에서 실행한다.
비밀번호는 본인 개발 환경에서 정해 환경변수에만 넣는다.

```bash
export MYSQL_ROOT_PASSWORD='본인이_정한_관리자_비밀번호'
export MYSQL_PASSWORD='본인이_정한_앱_비밀번호'
export MYSQL_PORT=3306
# 이미 3306을 사용하면 MYSQL_PORT=3307 등 다른 포트를 지정한다.
docker compose -f compose.db.yml up -d --wait
```

`docker compose version`이 인식되지 않는 macOS 환경에서는 Docker Desktop의
`/Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose` 실행 파일로
`docker compose` 부분을 대체할 수 있다. CLI 플러그인 경로를 올바르게 설정하는 것도 방법이다.

DB는 127.0.0.1에만 노출되고 named volume에 저장된다.
앱은 최소 권한 범위를 해당 개발 DB로 제한한 `yorijori` 계정을 사용하며 root로 연결하지 않는다.
Compose는 MySQL 서버만 시작한다. 테이블과 seed는 Spring 시작 시 Flyway가 적용한다.
최초 볼륨 초기화 이후 환경변수만 바꿔도 기존 DB의 계정 비밀번호가 변경되지는 않는다.

```bash
export DB_URL="jdbc:mysql://localhost:${MYSQL_PORT}/yorijori?serverTimezone=Asia/Seoul&characterEncoding=UTF-8"
export DB_USERNAME=yorijori
export DB_PASSWORD="$MYSQL_PASSWORD"
cd backend
bash ./gradlew bootRun --args='--spring.profiles.active=mysql'
```

종료는 프로젝트 루트에서 `docker compose -f compose.db.yml stop`을 사용한다.
컨테이너를 다시 만들더라도 named volume을 재사용하면 데이터는 유지된다.

## 적용 전 사전 점검

- V1~V3는 변경하지 않는다. 이번 변경은 V4이며 최신 develop에 같은 번호가 없는지 먼저 확인한다.
- 운영에 적용하기 전에 백업과 복구 확인을 마치고 애플리케이션 쓰기를 중단한다.
- Flyway 이력의 버전·성공 상태와 체크섬을 확인한다.
- V3 이상 DB에 다음 읽기 전용 SQL을 실행한다.

```bash
docker compose -f compose.db.yml exec -T db sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -uyorijori yorijori' < docs/erd/preflight.sql
```

결과는 `rule_name`, `row_id`이다. 행이 있으면 V4를 적용하지 말고 해당 데이터를 검토한다.
예를 들어 ck_dish_servings_left는 남은 인분이 음수이거나 원래 인분을 초과한 행이다.
NULL이 가능한 값과 수량 0, 기한이 지난 재료는 위반으로 취급하지 않는다.
정상 상태는 결과 행 0개다. 이것만으로 모든 운영 조건을 확인한 것은 아니다.
데이터를 자동 삭제하거나 일괄 0으로 덮어쓰는 절차는 제공하지 않는다.

## 백업과 복구

다음은 로컬 개발용 예시다. 백업에 회원 데이터가 포함될 수 있으므로 Git 밖의 지정 경로에 보관한다.
쓰기 중단 후 실행하고, 백업 파일이 생성되어 내용이 읽히는지 확인한다.

```bash
umask 077
docker compose -f compose.db.yml exec -T db sh -c \
  'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot --single-transaction --no-tablespaces yorijori' \
  > /tmp/yorijori-backup.sql
```

복구 검증은 원본 DB가 아닌 **별도로 생성한 빈 DB**에 수행한다.
DB 클라이언트로 백업 SQL을 불러온 후 테이블 수·회원/재고 건수·Flyway 이력과 주요 조회를 확인한다.
운영 복구에서는 운영 환경의 백업 보관·접근 정책을 사용한다.

MySQL의 여러 ALTER TABLE 문장은 전체가 하나의 트랜잭션으로 롤백되지 않는다.
부분 실패 시 쓰기를 계속 중단하고 실제 제약·인덱스 목록과 flyway_schema_history를 조사한다.
복구 방법은 백업을 별도 DB에 복원해 검증 후 연결을 전환하거나, 확인된 적용 상태에 맞춘
전진 복구를 검토하는 것이다. 무조건 재실행·repair·V1~V3 수정으로 해결하지 않는다.

## 자동 검증

```bash
cd backend
bash ./gradlew test --no-daemon
```

기본값은 H2이며 DB 무결성, 전체 migration, V3 데이터 보존, 사전 점검 탐지와 기존 API를 검증한다.
MySQL 방언 검증은 반드시 별도로 만든 **빈 전용 테스트 DB**에서 실행한다.
다음 테스트는 테이블과 fixture를 생성하고 그대로 남긴다. 실행 전에 빈 DB인지 검사한다.
개발·운영 DB의 접속 정보를 넣지 않는다.

```bash
export YORIJORI_TEST_DB_URL='jdbc:mysql://127.0.0.1:3307/yorijori?serverTimezone=Asia/Seoul&characterEncoding=UTF-8'
export YORIJORI_TEST_DB_USERNAME=yorijori
export YORIJORI_TEST_DB_PASSWORD="$MYSQL_PASSWORD"
bash ./gradlew test --tests '*DatabaseIntegrityTest' --rerun-tasks --no-daemon
unset YORIJORI_TEST_DB_URL YORIJORI_TEST_DB_USERNAME YORIJORI_TEST_DB_PASSWORD
```

`DatabaseIntegrityTest`는 V3까지 적용한 후 유효한 사용자 데이터를 삽입하고 V4로 업그레이드한다.
빈 DB의 V1~V4 일괄 적용은 기본 H2 테스트와 별도 MySQL 앱 기동 검증으로 확인한다.
같은 MySQL DB에 테스트를 다시 실행하려면 새 빈 테스트 DB를 준비한다.
테스트에서 기존 DB를 자동 삭제·초기화하지 않는다.

## 범위와 남은 과제

- 스키마 CHECK는 마지막 방어선이다. 새로운 API 입력 오류 처리나 동시 요청의 lost update는 해결하지 않는다.
- 회원 삭제는 기존 FK 및 새 피드백 FK가 차단할 수 있다. 탈퇴·익명화는 별도 정책과 구현이 필요하다.
- 현재 수량은 DOUBLE이다. 정확한 단위·분수 연산을 확장할 때 Java와 함께 DECIMAL 전환을 검토한다.
- 신규 인덱스는 현재 조회 조건에 맞춘 것이다. 운영 데이터의 EXPLAIN과 지연 시간을 보고 평가한다.
- 재학습은 consent=true인 기록만 사용한다. 이번 변경은 학습 데이터 추출이나 동의 변경을 구현하지 않는다.

## V5 관계·이력 이관

V1~V4를 수정하지 않고 V5를 적용한다. 구버전 앱은 GROUP 선택을 user_avoid에 쓰므로,
쓰기 중단 후 V5와 새 애플리케이션을 함께 배포한다. V5 DB에 구버전 앱을 그대로 연결하지 않는다.
적용 전 V4 점검에 더해 다음 SQL을 실행한다.

```bash
docker compose -f compose.db.yml exec -T db sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -uyorijori yorijori' < docs/erd/preflight-v5.sql
```

결과가 있으면 분류 이름·종류를 확인한 후 이관한다. V5는 알 수 없는 GROUP 선택을
조용히 버리지 않고 NOT NULL 위반으로 중단한다. GROUP 선택은 user_avoid_group으로
옮겨지고 user_avoid에는 ITEM만 남는다. 원본 백업과 새 분류 선택 건수를 비교한다.

기존 재고는 OPENING(0→현재 수량) 1건씩 기록한다. 시각은 migration 적용 시각이며
과거 등록·수정 이력이나 행위자를 복원한 것이 아니다. 이후 ADD/ADJUST/COOK/TOSS를
변경과 같은 트랜잭션에서 기록한다. 행 잠금으로 같은 재고 행의 수정·차감을 직렬화한다.
단위를 바꾸거나 다른 재고를 합산할 때는 원장의 단위 스냅샷을 함께 확인한다.
원장이 참조하는 냉장고는 삭제가 차단된다. 재고 행이 삭제되면 fridge_item_id만 NULL이 되고
item_ref_id·이름·단위·수량 변화는 보존된다.

과거 요리 기록의 냉장고는 현재 남아 있는 dish로 확인되는 경우만 연결한다.
재료 ID도 표준 이름이 정확히 일치하는 경우만 연결한다. 알 수 없는 과거 관계를
현재 회원의 소속으로 추정하지 않는다. 과거 가격에는 외부 상품 ID를 추정해 채우지 않는다.

scan_model에는 기존 클래스/피드백의 모든 버전을 이관한다. 새 모델은 클래스와 피드백보다
먼저 scan_model에 등록한다. artifact_path와 released_at은 확인된 값만 입력한다.
미등록 모델 피드백은 400 INVALID_INPUT으로 거절한다. 모호한 예측 클래스는 NULL로 둔다.
상품 포장 수량·단위는 확인 후 함께 입력하며, 현재 가격은 포장 수량당으로 정규화하지 않는다.
외부 상품 ID가 없거나 길이가 범위를 벗어나면 product_id=NULL로 가격 관측 자체는 보존한다.

V5 이관 테스트는 별도 빈 DB에서 다음처럼 실행한다. 기본 H2 외에 MySQL을 선택할 수 있다.

```bash
export YORIJORI_RELATION_DB_URL='jdbc:mysql://127.0.0.1:3307/yorijori?serverTimezone=Asia/Seoul&characterEncoding=UTF-8'
export YORIJORI_RELATION_DB_USERNAME=yorijori
export YORIJORI_RELATION_DB_PASSWORD="$MYSQL_PASSWORD"
cd backend
bash ./gradlew test --tests '*DatabaseRelationsMigrationTest' --rerun-tasks --no-daemon
unset YORIJORI_RELATION_DB_URL YORIJORI_RELATION_DB_USERNAME YORIJORI_RELATION_DB_PASSWORD
```

MySQL은 DDL 부분 적용을 자동 롤백하지 않는다. 특히 GROUP 이관 뒤 후속 단계가 실패했다면
선택 건수·실제 테이블·Flyway 이력과 백업을 조사하고 검증된 복구 절차를 따른다.
원장 및 새 테이블을 지워서 단순 재실행하는 방식은 사용하지 않는다.
