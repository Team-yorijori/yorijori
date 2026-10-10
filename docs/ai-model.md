# 재료 인식 모델 (v4) · 파트 사이 약속

## 모델 파일 규칙 (AI ↔ 프론트)

| 항목 | 값 |
|---|---|
| 파일 | `backend/src/main/resources/static/models/fridge.onnx` (지금 v4, 9.8MB) · `classes.json` |
| 모델 | YOLO26n (Ultralytics 8.4) → `export(format="onnx", imgsz=640, nms=False)` |
| 입력 | `images` `[1, 3, 640, 640]` RGB 0~1 (긴 변 640, 회색 114 패딩) |
| 출력 | `output0` `[1, 300, 6]` = x1, y1, x2, y2, score, classId (640×640 기준) |
| classes.json | `[{ "id": 0, "en": "cabbage", "ko": "양배추" }, …]` — `ko` 는 `ingredient.name` 과 같아야 함 |
| 실행 | 브라우저 onnxruntime-web 1.30 (WebGPU 우선, 안 되면 WASM) — `static/js/ai/fridge-scan.js` |

이 규칙만 지키면 **모델 파일 두 개만 바꿔 끼우면 끝.** 클래스가 바뀌면 `scan_class` 에 새 버전 행을 넣는 V 파일 추가, `application.yml` 의 `yorijori.scan.model-version` 변경

## v4 성능 (검증 mAP50 0.905)

| 재료 | mAP50 | 자동 체크 기준 | 비고 |
|---|---|---|---|
| 양배추 · 양파 · 감자 · 애호박 · 파프리카 · 마늘 · 옥수수 · 키위 · 딸기 · 포도 · 시금치 · 가지 · 레몬 · 우유 · 바나나 · 고구마 · 사과 · 버섯 | 0.90 이상 | 50% | |
| 당근 · 브로콜리 · 라임 · 오이 · 무 | 0.87~0.89 | 60% | |
| 배추 · 배 · 귤 | 0.99 | 60% | 합성 사진으로 채점해서 부풀려진 값. 실제 사진 확인 전 |
| 계란 | 0.85 | 65% | |
| 오렌지 0.70 · 치즈 0.71 · 대파 0.81 · 고추 0.81 · 토마토 0.83 · 두부(검증 8개뿐) | 낮음 | 70% | 다음 학습 우선 |

헷갈리는 재료 (결과 줄에 "혹시 ○○?" 버튼): 오렌지↔귤↔레몬↔라임, 귤·오렌지→감(미학습), 양배추↔배추, 애호박↔오이, 감자↔고구마, 토마토↔파프리카, 치즈↔두부

값은 `scan_class` 테이블(V2) 과 `static/js/scan-rules.js` 두 곳에 있음. 바꿀 때 둘 다 수정 (TODO(프론트) `scan-rules.js` 가 `/api/scan/classes` 를 읽게 바꾸면 한 곳만 수정)

## 다음 학습 (v5) 계획

1. 직접 찍은 사진: 대파 묶음, 고추, 포장 두부, 깻잎, 콩나물, 감 (팀원 냉장고·마트, 영상에서 프레임 추출)
2. `scan_feedback` 에 쌓인 "자주 헷갈리는 쌍" 을 보고 우선순위 조정 (`ScanFeedbackRepository.confusionCounts`)
3. v4 best.pt 에서 이어 학습 → 같은 규칙으로 ONNX 변환 → `static/models/` 교체

학습 방법 : [ai/README.md](../ai/README.md)
