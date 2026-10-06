# AI 파트

| 폴더 | 내용 | 결과물이 들어가는 곳 |
|---|---|---|
| `train/` | 재료 인식 모델 학습 (Colab 노트북, 데이터 병합, AI Hub 컷아웃·합성) | `backend/.../static/models/fridge.onnx`, `classes.json` |
| `scan/` | 모델 테스트 페이지 (모델 파일을 골라 사진으로 바로 확인) | — |
| `receipt/` | 영수증·주문내역 상품명 → 재료 규칙 사본과 테스트 | 규칙 코드는 `backend/.../static/js/ai/receipt.js` |
| `data/` | 공공 레시피 수집·정제, seed SQL 생성 | `backend/.../db/migration/V2·V3` |

모델 입출력 규칙·성능·인식 기준: [docs/ai-model.md](../docs/ai-model.md)

> 키는 코드에 쓰지 않는다. Colab 은 왼쪽 열쇠 아이콘(Secrets)에 `ROBOFLOW_API_KEY`, `AIHUB_API_KEY` 를 넣고 `userdata.get()` 으로 읽는다.
> 학습 원본 데이터(특히 AI Hub)와 `runs/` 결과 폴더는 저장소에 올리지 않는다.

---

## 1. 모델 학습 `train/`

| 파일 | 설명 |
|---|---|
| `train_fridge_yolo_v4.ipynb` | **현재 노트북** (33종). 셀 ①~⑩ 순서대로 |
| `cell_v4_data.py` | ③ Roboflow 데이터셋 80개를 받아 33종으로 이름 통일·병합 (노트북 셀과 같은 코드) |
| `qc_local.py` | AI Hub QC 데이터에서 재료만 오려 낸다 — **내 PC에서** 실행 (AI Hub 는 해외 다운로드 차단) |
| `cell_qc_aihub.py` | Colab 용 QC 처리 셀 (해외 차단으로 지금은 참고용) |
| `merge_datasets.py` | 데이터셋 병합 도우미 (v2 부터 사용) |
| `classes_v4.json` | v4 클래스 33종 |
| `DATASETS.md` | 학습 데이터 출처 |
| `history/` | v2·v3 노트북과 셀, `classes_v3.json` |

### 순서

1. **(PC)** AI Hub 「농산물 품질(QC) 이미지」 Validation 원천데이터 zip 을 받는다
   ```bash
   pip install opencv-python numpy
   python qc_local.py "D:\aihub\QC"          # → qc_out/qc_cutouts.zip
   ```
   `qc_cutouts.zip` 을 구글 드라이브 `MyDrive/yorijori/qc/` 에 올린다
2. **(Colab, 런타임 T4 GPU)** `train_fridge_yolo_v4.ipynb`
   - ① 설정 → ② 클래스 33종 → ③ Roboflow 병합(`/content/merged`) → ④ 컷아웃 풀기 → ⑤ 미리보기 → ⑥ 합성 6,000장 → ⑦ data_v4.yaml
   - ⑧ 학습: v3 best.pt 에서 이어서 25 epoch (T4 기준 약 7시간). 끊기면 resume 셀
   - ⑨ 평가 → ⑩ ONNX 변환: `fridge_v4.onnx`, `classes_v4.json`
3. 결과 두 파일을 `backend/src/main/resources/static/models/` 에 `fridge.onnx`, `classes.json` 이름으로 넣는다
4. 클래스가 바뀌었으면 `scan_class` 새 버전 행을 넣는 Flyway 파일(V4__scan_class_v5.sql 등)을 추가하고 `yorijori.scan.model-version` 을 바꾼다

### 주의 (겪은 문제)

- Colab 은 런타임이 끊기면 변수가 사라진다 → ①②부터 다시. `/content/merged` 가 남아 있으면 ③은 건너뛴다
- 드라이브에서 사진을 한 장씩 읽고 쓰면 매우 느리다 → Colab 디스크(`/content`)에서 작업하고 zip 으로 백업
- `fraction` 옵션은 매 epoch 랜덤이 아니라 고정된 일부만 쓴다

## 2. 모델 테스트 `scan/`

`scan_test.html` 을 브라우저로 열고 모델 파일(`fridge.onnx`)과 `classes.json` 을 고른 뒤 사진을 넣는다. 최소 점수를 바꿔 가며 확인할 수 있다.

## 3. 영수증 규칙 `receipt/`

- 실제 코드: `backend/src/main/resources/static/js/ai/receipt.js` (브라우저에서 tesseract.js 로 글자를 읽은 뒤 이 규칙으로 재료를 찾는다)
- `receipt_rules.json`: 규칙 값 사본 (상품명 표기 73개, 제외할 줄·단어, 1개당 무게)
- `test_receipt.js`: 규칙 테스트 — `node ai/receipt/test_receipt.js`

규칙을 고칠 때

1. `receipt.js` 의 `RC_ALIAS`(표기 → 재료), `RC_SKIP_LINE`(상품이 아닌 줄), `RC_SKIP_WORD`(가공품), `EACH_G`(무게 → 개수)를 고친다
2. `test_receipt.js` 의 `CASES` 에 실제 영수증 줄을 추가하고 돌린다
3. 서버에서도 같은 이름으로 바꾸게 하려면 `ingredient_alias` 에 넣는 Flyway 파일을 추가한다

## 4. 레시피 데이터 `data/`

| 파일 | 설명 |
|---|---|
| `RecipeFetch.java` | 농림축산식품 공공데이터 레시피 API 3종(기본·재료·과정) 전부 받기 — `java RecipeFetch.java 인증키` (승인된 IP 에서만) |
| `normalize.py` | 재료 이름 표준화, 분량 파싱, 기본 양념 분리 → `recipes.json` (537건) |
| `master_data.json` | 데모 v9 기준값: 재료 기준표 70종, 데모 레시피, 영수증 규칙, 알레르기 묶음, 보관 일수, 인식 기준 |
| `build_seed.py` | `recipes.json` + `master_data.json` → `V2__seed_ingredient.sql`, `V3__seed_recipe.sql` |
| `legacy/` | 처음 만든 스키마와 seed (참고용) |

> Flyway 는 이미 반영된 V 파일이 바뀌면 멈춘다. DB 에 올린 뒤에는 `build_seed.py` 로 V2·V3 를 다시 만들지 말고 바뀐 부분만 새 V 파일로 추가한다.
