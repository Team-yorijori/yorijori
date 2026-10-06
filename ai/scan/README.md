# 모델 테스트 페이지

`scan_test.html` 을 브라우저로 열고 → 모델 파일(`backend/src/main/resources/static/models/fridge.onnx`) → 클래스 목록에서 `classes.json` 선택 → 사진.
사진은 브라우저 안에서만 분석하고 어디에도 보내지 않는다. 인식 엔진(onnxruntime-web)은 처음 한 번 CDN 에서 받는다.
