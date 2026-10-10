# AI 파트

| 폴더 | 내용 | 결과물이 들어가는 곳 |
|---|---|---|
| `train/` | 재료 인식 모델 학습 (Colab 노트북, 데이터 병합, AI Hub 컷아웃·합성) | `backend/.../static/models/fridge.onnx`, `classes.json` |
| `scan/` | 모델 테스트 페이지 (모델 파일을 골라 사진으로 바로 확인) | — |
| `receipt/` | 영수증·주문내역 상품명 → 재료 규칙 사본과 테스트 | 규칙 코드는 `backend/.../static/js/ai/receipt.js` |
| `data/` | 공공 레시피 수집·정제, seed SQL 생성 | `backend/.../db/migration/V2·V3` |

모델 입출력 규칙·성능·인식 기준 : [docs/ai-model.md](../docs/ai-model.md) · 학습 데이터 출처 : [train/DATASETS.md](train/DATASETS.md)

> 키는 코드에 쓰지 않음. Colab은 왼쪽 열쇠 아이콘(Secrets)에 `ROBOFLOW_API_KEY`, `AIHUB_API_KEY`를 넣고 `userdata.get()`으로 읽기
> 학습 원본 데이터(특히 AI Hub)와 `runs/` 결과 폴더는 저장소에 올리지 않음

---

## 1. 모델 학습 `train/`

| 파일 | 설명 |
|---|---|
| `train_fridge_yolo_v4.ipynb` | **현재 노트북** (33종). 셀 ①~⑩ 순서대로 실행 |
| `cell_v4_data.py` | ③ Roboflow 데이터셋 80개를 받아 33종으로 이름 통일·병합 (노트북 셀과 같은 코드) |
| `qc_local.py` | AI Hub QC 데이터에서 재료만 오려 내기 — **내 PC에서** 실행 (AI Hub는 해외 다운로드 차단) |
| `cell_qc_aihub.py` | Colab용 QC 처리 셀 (해외 차단으로 지금은 참고용) |
| `merge_datasets.py` | 데이터셋 병합 도우미 (v2부터 사용) |
| `classes_v4.json` | v4 클래스 33종 |
| `qc_synth_preview.png` | 합성 사진 미리보기 |
| `DATASETS.md` | 학습 데이터 출처 |
| `history/` | v2·v3 노트북과 셀, `classes_v3.json` |

### 순서

1. **(PC)** AI Hub 「농산물 품질(QC) 이미지」 Validation 원천데이터 zip 받기
   ```bash
   pip install opencv-python numpy
   python qc_local.py "D:\aihub\QC"          # → qc_out/qc_cutouts.zip
   ```
   `qc_cutouts.zip`을 구글 드라이브 `MyDrive/yorijori/qc/`에 업로드
2. **(Colab, 런타임 T4 GPU)** `train_fridge_yolo_v4.ipynb`
   - ① 설정 → ② 클래스 33종 → ③ Roboflow 병합(`/content/merged`) → ④ 컷아웃 풀기 → ⑤ 미리보기 → ⑥ 합성 6,000장 → ⑦ data_v4.yaml
   - ⑧ 학습 : v3 best.pt에서 이어서 25 epoch (T4 기준 약 7시간). 끊기면 resume 셀
   - ⑨ 평가 → ⑩ ONNX 변환 : `fridge_v4.onnx`, `classes_v4.json`
3. 결과 두 파일을 `backend/src/main/resources/static/models/`에 `fridge.onnx`, `classes.json` 이름으로 넣기
4. 클래스가 바뀌었으면 `scan_class` 새 버전 행을 넣는 Flyway 파일(V4__scan_class_v5.sql 등) 추가, `yorijori.scan.model-version` 변경

### 주의 (겪은 문제)

- Colab은 런타임이 끊기면 변수가 사라짐 → ①②부터 다시. `/content/merged`가 남아 있으면 ③은 건너뛰기
- 드라이브에서 사진을 한 장씩 읽고 쓰면 매우 느림 → Colab 디스크(`/content`)에서 작업하고 zip으로 백업
- `fraction` 옵션은 매 epoch 랜덤이 아니라 고정된 일부만 사용

## 2. 모델 테스트 `scan/`

- `scan_test.html`을 브라우저로 열기 → 모델 파일(`backend/src/main/resources/static/models/fridge.onnx`) → `classes.json` 선택 → 사진
- 최소 점수를 바꿔 가며 확인 가능
- 사진은 브라우저 안에서만 분석, 어디에도 보내지 않음. 인식 엔진(onnxruntime-web)은 처음 한 번 CDN에서 받음

## 3. 영수증 규칙 `receipt/`

- 실제 코드 : `backend/src/main/resources/static/js/ai/receipt.js` (브라우저에서 tesseract.js로 글자를 읽은 뒤 이 규칙으로 재료 찾기)
- `receipt_rules.json` : 규칙 값 사본 (상품명 표기 73개, 제외할 줄·단어, 1개당 무게)
- `test_receipt.js` : 규칙 테스트 — `node ai/receipt/test_receipt.js` (PR마다 CI에서 자동 실행)

규칙을 고칠 때

1. `receipt.js`의 `RC_ALIAS`(표기 → 재료), `RC_SKIP_LINE`(상품이 아닌 줄), `RC_SKIP_WORD`(가공품), `EACH_G`(무게 → 개수) 수정
2. `test_receipt.js`의 `CASES`에 실제 영수증 줄을 추가하고 실행
3. 서버에서도 같은 이름으로 바꾸게 하려면 `ingredient_alias`에 넣는 Flyway 파일 추가

## 4. 레시피 데이터 `data/`

수집(`RecipeFetch.java`) → 정제(`normalize.py` → `recipes.json`) → seed SQL(`build_seed.py`)

| 파일 | 설명 |
|---|---|
| `RecipeFetch.java` | 농림축산식품 공공데이터 레시피 API 3종(기본·재료·과정) 전부 받기 — `java RecipeFetch.java 인증키` (승인된 IP에서만) |
| `normalize.py` | 재료 이름 표준화, 분량 파싱, 기본 양념 분리 → `recipes.json` (537건) |
| `master_data.json` | 데모 v9 기준값 : 재료 기준표 70종, 데모 레시피, 영수증 규칙, 알레르기 묶음, 보관 일수, 인식 기준 |
| `build_seed.py` | `recipes.json` + `master_data.json` → `V2__seed_ingredient.sql`, `V3__seed_recipe.sql` |
| `legacy/` | 처음 만든 스키마와 seed (참고용) |

```bash
python ai/data/build_seed.py      # 프로젝트 루트에서
```

> Flyway는 이미 반영된 V 파일이 바뀌면 멈춤. DB에 올린 뒤에는 `build_seed.py`로 V2·V3를 다시 만들지 말고 바뀐 부분만 새 V 파일로 추가
