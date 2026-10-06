"""
여러 YOLO 형식 데이터셋을 우리 클래스 목록 하나로 합친다.

- 각 데이터셋의 클래스 이름을 우리 클래스(영문 id)로 다시 매핑한다.
- 매핑에 없는 클래스의 박스는 버린다.
- 박스가 하나도 남지 않은 이미지는 '배경 이미지'로 일부만 남긴다(오탐 줄이기용).
- 결과: merged/{train,val,test}/{images,labels} + data.yaml
"""
import json, random, shutil
from pathlib import Path

import yaml

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_classes(path="classes.json"):
    """classes.json → [{'id':0,'en':'cabbage','ko':'양배추'}, ...]"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def find_split_dirs(root: Path):
    """Roboflow/Label Studio/CVAT YOLO 내보내기의 흔한 폴더 구조를 모두 찾는다."""
    pairs = []
    for img_dir in root.rglob("images"):
        if not img_dir.is_dir():
            continue
        lbl_dir = img_dir.parent / "labels"
        if lbl_dir.is_dir():
            pairs.append((img_dir, lbl_dir))
    return pairs


def source_names(root: Path):
    """data.yaml 또는 classes.txt에서 원본 클래스 이름 목록을 읽는다."""
    y = next(iter(root.rglob("data.yaml")), None)
    if y:
        names = yaml.safe_load(y.read_text(encoding="utf-8"))["names"]
        return [names[k] for k in sorted(names)] if isinstance(names, dict) else list(names)
    t = next(iter(root.rglob("classes.txt")), None)
    if t:
        return [l.strip() for l in t.read_text(encoding="utf-8").splitlines() if l.strip()]
    raise FileNotFoundError(f"{root}: data.yaml / classes.txt 가 없다")


def merge(sources, classes, out="merged", split=(0.7, 0.2, 0.1), keep_background=0.1, seed=42):
    """
    sources: [{'path': 'datasets/roboflow_a', 'map': {'Cabbage': 'cabbage', 'egg': 'egg', ...}}, ...]
             map의 키는 원본 클래스 이름, 값은 우리 클래스 en id
    """
    rnd = random.Random(seed)
    en2id = {c["en"]: c["id"] for c in classes}
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    for s in ("train", "val", "test"):
        (out / s / "images").mkdir(parents=True)
        (out / s / "labels").mkdir(parents=True)

    items, counts, dropped = [], {c["en"]: 0 for c in classes}, {}
    for si, src in enumerate(sources):
        root = Path(src["path"])
        names = source_names(root)
        cmap = {}
        for i, n in enumerate(names):
            tgt = src["map"].get(n)
            if tgt is None:
                dropped[n] = dropped.get(n, 0)
                continue
            if tgt not in en2id:
                raise ValueError(f"'{tgt}' 는 classes.json 에 없는 클래스다")
            cmap[i] = en2id[tgt]

        for img_dir, lbl_dir in find_split_dirs(root):
            for img in img_dir.iterdir():
                if img.suffix.lower() not in IMG_EXT:
                    continue
                lbl = lbl_dir / (img.stem + ".txt")
                lines = []
                if lbl.exists():
                    for line in lbl.read_text().splitlines():
                        p = line.split()
                        if len(p) != 5:  # 폴리곤(세그멘테이션) 라벨은 건너뜀
                            continue
                        c = int(p[0])
                        if c in cmap:
                            lines.append(" ".join([str(cmap[c])] + p[1:]))
                            counts[classes[cmap[c]]["en"]] += 1
                        else:
                            n = names[c] if c < len(names) else str(c)
                            dropped[n] = dropped.get(n, 0) + 1
                if not lines and rnd.random() > keep_background:
                    continue
                items.append((img, lines, f"s{si}_{img_dir.parent.name}_{img.stem}"))

    rnd.shuffle(items)
    n = len(items)
    n_tr, n_va = int(n * split[0]), int(n * split[1])
    buckets = {"train": items[:n_tr], "val": items[n_tr:n_tr + n_va], "test": items[n_tr + n_va:]}
    for s, rows in buckets.items():
        for img, lines, stem in rows:
            shutil.copy(img, out / s / "images" / (stem + img.suffix.lower()))
            (out / s / "labels" / (stem + ".txt")).write_text("\n".join(lines))

    data = {
        "path": str(out.resolve()),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "names": {c["id"]: c["en"] for c in classes},
    }
    (out / "data.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print(f"이미지 {n}장 → train {len(buckets['train'])} / val {len(buckets['val'])} / test {len(buckets['test'])}")
    print("클래스별 박스 수:")
    for c in classes:
        k = counts[c["en"]]
        warn = "  ← 부족(최소 150개 권장)" if k < 150 else ""
        print(f"  {c['id']:>2} {c['ko']}({c['en']}): {k}{warn}")
    if dropped:
        print("매핑하지 않아 버린 원본 클래스:", ", ".join(sorted(dropped)))
    return out / "data.yaml"
