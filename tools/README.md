# tools

`split_demo.py` — 데모 단일 HTML 을 Spring 의 templates · static/css · static/js 로 나눈다 (v9 → backend 화면을 만들 때 쓴 것).

```bash
python tools/split_demo.py demo/요리조리_데모_v9.html backend/src/main/resources
```

> 다시 돌리면 `templates/`, `static/css/`, `static/js/` 의 데모 유래 파일을 **덮어쓴다.** 그 뒤에 손으로 고친 것이 있으면 돌리지 않는다.
> (덮어쓰지 않는 파일: `static/js/api.js`, `static/js/init.js`, `templates/auth/*`)
