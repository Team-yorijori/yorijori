# 요리조리 협업 규칙

팀원 3명(노형석 · 김민서 · 박가람)이 한 저장소에서 같이 작업하기 위한 규칙이다.
규칙을 바꾸고 싶으면 이 파일을 고치는 PR을 올리고, 셋 다 확인한 뒤 머지한다.

---

## 0. 한눈에 보기

```
1. develop 최신화           git switch develop && git pull
2. 작업 브랜치 만들기       git switch -c feature/back-fridge-api
3. 작업 · 커밋              git commit -m "feat(back): 냉장고 재료 수정 API 추가"
4. 올리기                   git push -u origin feature/back-fridge-api
5. GitHub에서 PR            develop ← feature/back-fridge-api, 템플릿 채우기
6. 리뷰 1명 승인 + CI 통과   초록 체크가 떠야 머지 버튼이 켜진다
7. Squash and merge         머지 후 작업 브랜치 삭제
```

`main`과 `develop`에는 직접 push하지 않는다. 모든 변경은 PR로 들어간다.

---

## 1. 브랜치

| 브랜치 | 용도 | 어디서 따고 어디로 보내나 |
|---|---|---|
| `main` | 발표·제출·배포용 완성본 | `develop`에서 PR로만 들어온다 |
| `develop` | 통합본. 평소 작업의 기준 | 작업 브랜치의 PR이 여기로 들어온다 |
| `feature/{파트}-{기능}` | 새 기능 | `develop` → `develop` |
| `fix/{파트}-{내용}` | 버그 수정 | `develop` → `develop` |
| `hotfix/{내용}` | 발표 직전 `main`의 급한 수정 | `main` → `main`, 머지 후 `develop`에도 반영 |

**파트 이름**: `back` · `front` · `ai` · `docs` · `demo`

```
feature/back-fridge-api      feature/front-dish-anim      feature/ai-model-v5
fix/back-login-redirect      fix/front-tabbar-overlap     fix/ai-receipt-qty
hotfix/demo-crash
```

- 브랜치 이름은 영어 소문자와 `-`만 쓴다.
- 브랜치 하나에는 기능 하나만 담는다. 일이 커지면 브랜치를 나눈다.
- 머지된 브랜치는 지운다. GitHub PR 화면의 **Delete branch** 버튼을 누르면 된다.

---

## 2. 커밋 메시지

```
타입(파트): 무엇을 했는지 한 줄

(선택) 왜 바꿨는지, 주의할 점
```

| 타입 | 언제 |
|---|---|
| `feat` | 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 동작은 그대로, 구조만 정리 |
| `style` | CSS·디자인 변경, 코드 포맷 |
| `docs` | README · 명세 · 회의록 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드 설정, 라이브러리, CI |

예시

```
feat(back): 냉장고 재료 수량 수정 API 추가
fix(front): 모바일에서 하단 탭바가 버튼을 가리는 문제 수정
feat(ai): 인식 모델 v5 교체 (33종 → 40종)
docs: 9월 24일 회의록 추가
chore: GitHub Actions에 Gradle 캐시 추가
```

- 요약은 한국어로 쓰고, 50자 안쪽으로 줄인다.
- 파트는 생략해도 된다 (`docs:`, `chore:`처럼 전체에 걸친 것).
- 커밋은 작게, 자주 한다. "작업중", "수정" 같은 메시지는 쓰지 않는다.

---

## 3. PR (Pull Request)

**보내는 곳**: 평소에는 `develop`. 제목은 커밋 메시지 형식을 따른다.

**PR 본문**: 템플릿이 자동으로 뜬다. 무엇을·왜·확인 방법을 채운다. 화면이 바뀌면 스크린샷을 붙인다.

**머지 조건**

1. 팀원 1명 이상 **Approve**
2. CI(빌드·테스트) 초록 체크
3. 리뷰 코멘트가 남아 있으면 해결(Resolve)한 뒤 머지

**머지 방식**: `develop`으로는 **Squash and merge**. 작업 브랜치의 자잘한 커밋이 하나로 합쳐져 `develop` 기록이 깔끔해진다.

**크기**: 변경 300줄 안쪽을 권장한다. seed SQL, 모델 파일, 데모 HTML처럼 자동 생성된 큰 파일은 줄 수에 넣지 않는다.

**충돌이 나면**: 내 브랜치에서 `git pull origin develop`으로 최신 `develop`을 합치고, 충돌을 풀고, 다시 push한다.

---

## 4. 코드 리뷰

- PR이 올라오면 **24시간 안에** 한 번은 본다. 바쁘면 "내일 볼게"라도 남긴다.
- 보는 것: 의도대로 동작하는지, 파트 약속(아래 6번)을 지켰는지, 비밀 값이 없는지.
- 코멘트는 제안으로 쓴다. 예) "여기서 null이면 500이 날 것 같은데, 체크를 넣으면 어떨까?"
- 꼭 고쳐야 하는 것은 **Request changes**, 취향 차이는 그냥 코멘트로 남긴다.
- 리뷰어를 못 정하겠으면 그 파일 담당자(README 6절 "파일별 담당")를 지정한다.

---

## 5. develop → main (발표·제출 전)

1. GitHub에서 `main ← develop` PR을 만든다. 제목 예) `release: v1.0 중간 발표`
2. 셋 다 로컬에서 실행해 보고 Approve한다.
3. **Create a merge commit**으로 머지한다 (Squash 하지 않는다. `main`과 `develop` 기록이 어긋나지 않게).
4. 머지 후 태그를 단다: GitHub **Releases → Draft a new release** → `v1.0` 같은 태그 이름 → 바뀐 점 요약.

| 시점 | 태그 예시 |
|---|---|
| 중간 발표 | `v1.0` |
| 기말 발표·제출 | `v2.0` |
| 발표 후 급한 수정 | `v2.0.1` |

---

## 6. 파트 사이의 약속

README 6절 "파트 사이의 약속"에 더해 아래를 지킨다.

**DB 마이그레이션 (Flyway)**

- 이미 `develop`에 머지된 `V*.sql`은 **절대 고치지 않는다**. 고치면 팀원 DB와 서버 DB에서 체크섬 오류로 서버가 안 뜬다.
- 바꿀 게 있으면 새 번호 파일을 추가한다. 예) `V4__add_fridge_memo.sql`
- 두 사람이 같은 번호를 쓰지 않게, 새 V 파일을 만들기 전에 `develop`을 최신화하고 PR 설명에 번호를 적는다.

**API**

- 요청·응답 형식이 바뀌면 `docs/api.md`를 같은 PR에서 고친다.
- 프론트가 쓰는 API를 바꾸는 PR은 프론트 담당자를 리뷰어로 넣는다.

**AI 모델**

- 모델을 바꿀 때는 `static/models/fridge.onnx`와 `classes.json`을 같은 PR에서 함께 바꾼다.
- 입력 `[1,3,640,640]`, 출력 `[1,300,6]` 형식이 바뀌면 `fridge-scan.js` 수정과 프론트 리뷰가 필요하다.
- 학습 노트북·스크립트는 `ai/train/`에 두고, 예전 버전은 `ai/train/history/`로 옮긴다.

**재료 이름**

- `ingredient` 테이블의 표준 이름만 쓴다. 다른 표기는 `ingredient_alias`에 추가한다.

---

## 7. 올리지 않는 것

| 올리지 않는 것 | 이유 · 대신 어디에 |
|---|---|
| `application-secret.yml`, `.env`, API 키, 비밀번호 | 공개 저장소다. `application-secret.example.yml`을 복사해 각자 만든다 |
| 학습 데이터셋 원본 (`ai/train/datasets/`) | AI Hub 데이터는 재배포 금지 |
| 학습 결과 (`runs/`, `*.pt`) | 용량. 최종 모델은 `.onnx`로 변환해서만 올린다 |
| `*.zip`, 데모 v1~v8 | 용량. 팀 드라이브에 둔다 |
| `.idea/`, `build/`, `out/` | 사람마다 다른 IDE·빌드 결과물 |

**실수로 키를 올렸다면**: 커밋을 지워도 이미 공개된 것으로 본다. 바로 그 키를 **폐기하고 새로 발급**한 뒤 팀에 알린다.

**파일 크기**: GitHub은 파일 하나당 100MB가 한도이고 50MB부터 경고가 뜬다. 20MB가 넘는 파일을 올릴 때는 PR 설명에 이유를 적는다.

---

## 8. 이슈

- 할 일·버그는 GitHub **Issues**에 남긴다. 템플릿(기능 / 버그)이 뜬다.
- 담당자(Assignees)를 정하고, 라벨로 파트를 표시한다: `back` · `front` · `ai` · `docs` · `bug` · `feature`
- PR 본문에 `Closes #12`라고 쓰면 머지될 때 그 이슈가 자동으로 닫힌다.

---

## 9. 회의록

- `docs/회의록/YYYY-MM-DD.md`로 만든다. 형식은 `docs/회의록/_템플릿.md`를 복사한다.
- 회의에서 정한 할 일은 이슈로도 만든다.

---

## 10. 처음 시작할 때

```bash
git clone https://github.com/yuyoungwoo/yorijori.git
cd yorijori
git config user.name "본인 이름"
git config user.email "GitHub 가입 이메일"
git switch develop
```

- IntelliJ에서 `backend/` 폴더를 열고 Gradle 프로젝트로 불러온다.
- `application-secret.example.yml`을 같은 폴더에 `application-secret.yml`로 복사하고 필요한 키만 채운다 (없어도 local 프로필로 실행된다).
- 실행: `cd backend` → `./gradlew bootRun` (윈도우는 `gradlew.bat bootRun`) → http://localhost:8080
- 줄바꿈은 `.gitattributes`가 맞춰 준다. 윈도우에서 따로 설정할 것은 없다.
