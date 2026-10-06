/*
 * fridge-scan.js — 브라우저에서 식재료를 인식한다.
 *
 * 모델: YOLO26 ONNX, export(format="onnx", imgsz=640, nms=False)
 *   입력  images  [1, 3, 640, 640]  RGB, 0~1
 *   출력  output0 [1, 300, 6]       x1, y1, x2, y2, score, classId (640×640 기준 좌표)
 *
 * 필요: onnxruntime-web (전역 ort) 를 먼저 불러온다.
 *   https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/ort.min.js  (script 태그로)
 *   또는 Spring static/ort/ 에 dist 파일을 복사해 자체 호스팅한다.
 *
 * 사용:
 *   await FridgeScan.load({ model: "/models/fridge.onnx", classes: "/models/classes.json" });
 *   const r = await FridgeScan.detect(file, { minScore: 0.35 });
 *   r.items  → [{ id, en, ko, count, score, boxes:[...] }]  재료별로 묶인 결과(점수순)
 */
(function (global) {
  "use strict";

  const SIZE = 640;
  const PAD = 114 / 255; // Ultralytics letterbox 패딩 색(회색 114)
  let session = null;
  let classes = [];
  let backend = "";

  async function toBuffer(src) {
    if (src instanceof ArrayBuffer) return new Uint8Array(src);
    if (src instanceof Uint8Array) return src;
    if (src instanceof Blob) return new Uint8Array(await src.arrayBuffer());
    const res = await fetch(src);
    if (!res.ok) throw new Error(`모델 파일을 불러오지 못했다 (${res.status}): ${src}`);
    return new Uint8Array(await res.arrayBuffer());
  }

  async function toClasses(src) {
    if (Array.isArray(src)) return src;
    if (src instanceof Blob) return JSON.parse(await src.text());
    const res = await fetch(src);
    if (!res.ok) throw new Error(`클래스 파일을 불러오지 못했다 (${res.status}): ${src}`);
    return res.json();
  }

  /**
   * 모델을 불러온다. 한 번만 부르면 된다.
   * @param {object} o
   * @param {string|ArrayBuffer|Uint8Array|Blob} o.model  ONNX 모델
   * @param {string|Array|Blob} o.classes  classes.json (URL, 배열, 파일)
   * @param {string} [o.wasmPaths]  onnxruntime-web wasm 파일 위치(자체 호스팅 시 "/ort/")
   * @param {boolean} [o.preferWebGPU=true]  WebGPU 가 되면 쓰고, 안 되면 wasm(CPU)로 돈다
   */
  async function load(o) {
    if (!global.ort) throw new Error("onnxruntime-web(ort) 을 먼저 불러와야 한다");
    if (o.wasmPaths) ort.env.wasm.wasmPaths = o.wasmPaths;
    const [buf, cls] = await Promise.all([toBuffer(o.model), toClasses(o.classes)]);
    classes = cls;

    const tryList = [];
    if (o.preferWebGPU !== false && "gpu" in navigator) tryList.push("webgpu");
    tryList.push("wasm");
    let lastErr;
    for (const ep of tryList) {
      try {
        session = await ort.InferenceSession.create(buf, { executionProviders: [ep], graphOptimizationLevel: "all" });
        backend = ep;
        break;
      } catch (e) { lastErr = e; }
    }
    if (!session) throw lastErr;

    // 출력 형식 확인: [1,300,6] 이 아니면 export 옵션(nms=False)을 다시 확인해야 한다
    const out = session.outputNames[0];
    const meta = session.outputMetadata ? session.outputMetadata.find?.(m => m.name === out) : null;
    if (meta && meta.shape && meta.shape[2] !== 6) {
      throw new Error(`출력 형식이 [1,300,6] 이 아니다: [${meta.shape}] — export(nms=False) 로 다시 내보낸다`);
    }

    // 첫 추론은 느리므로 빈 이미지로 미리 한 번 돌려둔다
    const warm = new ort.Tensor("float32", new Float32Array(3 * SIZE * SIZE).fill(PAD), [1, 3, SIZE, SIZE]);
    await session.run({ [session.inputNames[0]]: warm });
    return { backend, classes: classes.length };
  }

  /** 이미지(파일·Blob·img·canvas·ImageBitmap)를 ImageBitmap 으로. 폰 사진의 EXIF 회전도 반영한다. */
  async function toBitmap(src) {
    if (src instanceof ImageBitmap) return src;
    if (src instanceof Blob) return createImageBitmap(src, { imageOrientation: "from-image" });
    return createImageBitmap(src);
  }

  /** 비율을 유지한 채 640×640 에 맞추고 남는 곳은 회색으로 채운다(letterbox). */
  function letterbox(bmp) {
    const scale = Math.min(SIZE / bmp.width, SIZE / bmp.height);
    const w = Math.round(bmp.width * scale), h = Math.round(bmp.height * scale);
    const dx = Math.floor((SIZE - w) / 2), dy = Math.floor((SIZE - h) / 2);
    const cv = typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(SIZE, SIZE) : Object.assign(document.createElement("canvas"), { width: SIZE, height: SIZE });
    const ctx = cv.getContext("2d", { willReadFrequently: true });
    ctx.fillStyle = "rgb(114,114,114)";
    ctx.fillRect(0, 0, SIZE, SIZE);
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(bmp, dx, dy, w, h);
    const px = ctx.getImageData(0, 0, SIZE, SIZE).data;
    const N = SIZE * SIZE, data = new Float32Array(3 * N);
    for (let i = 0, j = 0; i < N; i++, j += 4) {
      data[i] = px[j] / 255;          // R
      data[i + N] = px[j + 1] / 255;  // G
      data[i + 2 * N] = px[j + 2] / 255; // B
    }
    return { tensor: new ort.Tensor("float32", data, [1, 3, SIZE, SIZE]), scale, dx, dy };
  }

  /**
   * 사진 한 장에서 재료를 찾는다.
   * @param {Blob|HTMLImageElement|HTMLCanvasElement|ImageBitmap} image
   * @param {object} [opt]
   * @param {number} [opt.minScore=0.35]  이 점수 미만은 버린다
   * @param {number} [opt.confirmBelow=0.6]  이 점수 미만은 '확인 필요'로 표시한다
   */
  async function detect(image, opt = {}) {
    if (!session) throw new Error("load() 를 먼저 호출해야 한다");
    const minScore = opt.minScore ?? 0.35, confirmBelow = opt.confirmBelow ?? 0.6;
    const bmp = await toBitmap(image);
    const t0 = performance.now();
    const { tensor, scale, dx, dy } = letterbox(bmp);
    const out = await session.run({ [session.inputNames[0]]: tensor });
    const d = out[session.outputNames[0]].data;
    const ms = Math.round(performance.now() - t0);

    const detections = [];
    for (let i = 0; i + 5 < d.length; i += 6) {
      const score = d[i + 4];
      if (score < minScore) continue;
      const id = Math.round(d[i + 5]);
      const c = classes[id] || { id, en: `class_${id}`, ko: `알 수 없음(${id})` };
      // 640 좌표 → 원본 사진 좌표
      const x1 = Math.max(0, (d[i] - dx) / scale), y1 = Math.max(0, (d[i + 1] - dy) / scale);
      const x2 = Math.min(bmp.width, (d[i + 2] - dx) / scale), y2 = Math.min(bmp.height, (d[i + 3] - dy) / scale);
      detections.push({ id, en: c.en, ko: c.ko, score, box: [x1, y1, x2, y2] });
    }
    detections.sort((a, b) => b.score - a.score);

    // 같은 재료끼리 묶는다(계란 6개 → 계란 1줄, count 6)
    const byId = new Map();
    for (const det of detections) {
      let g = byId.get(det.id);
      if (!g) byId.set(det.id, g = { id: det.id, en: det.en, ko: det.ko, count: 0, score: 0, boxes: [] });
      g.count++; g.score = Math.max(g.score, det.score); g.boxes.push(det.box);
    }
    const items = [...byId.values()].sort((a, b) => b.score - a.score)
      .map(g => ({ ...g, needsConfirm: g.score < confirmBelow }));

    return { items, detections, width: bmp.width, height: bmp.height, ms, backend };
  }

  global.FridgeScan = { load, detect, get backend() { return backend; }, get classes() { return classes; } };
})(window);
