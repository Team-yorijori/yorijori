# 학습 데이터 출처

인식 모델 v4 학습에 쓴 데이터. **원본 이미지는 저장소에 올리지 않는다** (용량·라이선스). 다시 받으려면 `train_fridge_yolo_v4.ipynb` 를 실행한다.

## 1. Roboflow Universe 공개 데이터셋

라이선스는 데이터셋마다 다르므로 링크의 데이터셋 페이지에서 확인하고, 발표·보고서에 출처를 적는다.

| 그룹 | workspace / project | 버전 | 링크 |
|---|---|---|---|
| 냉장고 혼합 사진 (가장 중요) | smart-fridge-mvi88 / smart-fridge-co7ul | 6 | https://universe.roboflow.com/smart-fridge-mvi88/smart-fridge-co7ul/dataset/6 |
| 냉장고 혼합 사진 (가장 중요) | recipe-recomendation-app / fridge-detection-merged | 4 | https://universe.roboflow.com/recipe-recomendation-app/fridge-detection-merged/dataset/4 |
| 냉장고 혼합 사진 (가장 중요) | bottles-0ds2b / fridge-qjtyj | 1 | https://universe.roboflow.com/bottles-0ds2b/fridge-qjtyj/dataset/1 |
| 냉장고 혼합 사진 (가장 중요) | fridge-0keux / fridge-0fckr | 1 | https://universe.roboflow.com/fridge-0keux/fridge-0fckr/dataset/1 |
| 냉장고 혼합 사진 (가장 중요) | adam-barnett / fridge-jlbwq | 1 | https://universe.roboflow.com/adam-barnett/fridge-jlbwq/dataset/1 |
| 냉장고 혼합 사진 (가장 중요) | cs131 / fridge-5ep2w | 4 | https://universe.roboflow.com/cs131/fridge-5ep2w/dataset/4 |
| 냉장고 혼합 사진 (가장 중요) | fridge-fesjh / fridge-eamqk | 3 | https://universe.roboflow.com/fridge-fesjh/fridge-eamqk/dataset/3 |
| 대파 | curry / green-zecem | 1 | https://universe.roboflow.com/curry/green-zecem/dataset/1 |
| 대파 | shabishko / onion-leaves-99kwc | 1 | https://universe.roboflow.com/shabishko/onion-leaves-99kwc/dataset/1 |
| 대파 | foodanno / leek | 1 | https://universe.roboflow.com/foodanno/leek/dataset/1 |
| 무 | olrnd / radish-d1ugk | 1 | https://universe.roboflow.com/olrnd/radish-d1ugk/dataset/1 |
| 무 | dolazy7-gmail-com-3vj05 / radish | 2 | https://universe.roboflow.com/dolazy7-gmail-com-3vj05/radish/dataset/2 |
| 무 | yeoworm / radish-akkqa | 3 | https://universe.roboflow.com/yeoworm/radish-akkqa/dataset/3 |
| 무 | stones-workspace / radish-y3ll3 | 1 | https://universe.roboflow.com/stones-workspace/radish-y3ll3/dataset/1 |
| 무 | curry / radish-2lmfh | 1 | https://universe.roboflow.com/curry/radish-2lmfh/dataset/1 |
| 두부 | stones-workspace / tofu-tdnu5 | 1 | https://universe.roboflow.com/stones-workspace/tofu-tdnu5/dataset/1 |
| 두부 | graduation-project-3v6ak / tofu-nmvji | 1 | https://universe.roboflow.com/graduation-project-3v6ak/tofu-nmvji/dataset/1 |
| 두부 | chen-xieyu / tofu-8punk | 1 | https://universe.roboflow.com/chen-xieyu/tofu-8punk/dataset/1 |
| 우유 | mateo-ojeda / milk-zum2p | 1 | https://universe.roboflow.com/mateo-ojeda/milk-zum2p/dataset/1 |
| 우유 | robocup2022-kogzd / milk-i3u51 | 2 | https://universe.roboflow.com/robocup2022-kogzd/milk-i3u51/dataset/2 |
| 우유 | bosslnwza / milk-fzwnn | 1 | https://universe.roboflow.com/bosslnwza/milk-fzwnn/dataset/1 |
| 우유 | dheebanmilk / milk-yxalp | 15 | https://universe.roboflow.com/dheebanmilk/milk-yxalp/dataset/15 |
| 우유 | dolazy7-gmail-com-3vj05 / milk-acvg1 | 2 | https://universe.roboflow.com/dolazy7-gmail-com-3vj05/milk-acvg1/dataset/2 |
| 버섯 | test-zq0fq / mushroom-3zqg7 | 2 | https://universe.roboflow.com/test-zq0fq/mushroom-3zqg7/dataset/2 |
| 버섯 | mushroom28 / mushroom-nksu4 | 6 | https://universe.roboflow.com/mushroom28/mushroom-nksu4/dataset/6 |
| 버섯 | huurhuntergel / mushroom-e8f6k | 3 | https://universe.roboflow.com/huurhuntergel/mushroom-e8f6k/dataset/3 |
| 버섯 | yueyue-fob5l / mushroom-xtwbh | 1 | https://universe.roboflow.com/yueyue-fob5l/mushroom-xtwbh/dataset/1 |
| 버섯 | mushroom-9xzfs / mushroom-jlp5g | 3 | https://universe.roboflow.com/mushroom-9xzfs/mushroom-jlp5g/dataset/3 |
| 버섯 | mushroom-r8avj / mushroom-syqui | 1 | https://universe.roboflow.com/mushroom-r8avj/mushroom-syqui/dataset/1 |
| 버섯 | davifina / mushroom-eob88 | 2 | https://universe.roboflow.com/davifina/mushroom-eob88/dataset/2 |
| 버섯 | genet-xx587 / mushroom-7whbq | 2 | https://universe.roboflow.com/genet-xx587/mushroom-7whbq/dataset/2 |
| 바나나 | kipleytaylor / banana-rzonz | 1 | https://universe.roboflow.com/kipleytaylor/banana-rzonz/dataset/1 |
| 바나나 | jim-pepvn / banana-9nmv2 | 2 | https://universe.roboflow.com/jim-pepvn/banana-9nmv2/dataset/2 |
| 바나나 | object-detection-djcen / banana-nlcck | 1 | https://universe.roboflow.com/object-detection-djcen/banana-nlcck/dataset/1 |
| 바나나 | mtfs-workspace-ktra5 / banana-p8z1q | 5 | https://universe.roboflow.com/mtfs-workspace-ktra5/banana-p8z1q/dataset/5 |
| 바나나 | train-0beej / banana-qlroc | 1 | https://universe.roboflow.com/train-0beej/banana-qlroc/dataset/1 |
| 레몬 | ai-wfddm / lemon-ezutg | 1 | https://universe.roboflow.com/ai-wfddm/lemon-ezutg/dataset/1 |
| 레몬 | ece4078-mpxui / lemon-jlkzg | 2 | https://universe.roboflow.com/ece4078-mpxui/lemon-jlkzg/dataset/2 |
| 레몬 | mueanfan / lemon-orwgb | 2 | https://universe.roboflow.com/mueanfan/lemon-orwgb/dataset/2 |
| 레몬 | riyadh-lakadimu-uhlb5 / lemon-pknhy | 12 | https://universe.roboflow.com/riyadh-lakadimu-uhlb5/lemon-pknhy/dataset/12 |
| 레몬 | haniftesting / lemon-aer5f | 2 | https://universe.roboflow.com/haniftesting/lemon-aer5f/dataset/2 |
| 레몬 | dcu-oiu8y / lemon-gzrja | 2 | https://universe.roboflow.com/dcu-oiu8y/lemon-gzrja/dataset/2 |
| 고추 | olrnd / green-chili | 1 | https://universe.roboflow.com/olrnd/green-chili/dataset/1 |
| 고추 | abhichal-rajput / chili-2jwcr | 1 | https://universe.roboflow.com/abhichal-rajput/chili-2jwcr/dataset/1 |
| 고추 | gun-yfmsv / chili-3apfs | 3 | https://universe.roboflow.com/gun-yfmsv/chili-3apfs/dataset/3 |
| 고추 | abhichal-rajput / green-chilli | 1 | https://universe.roboflow.com/abhichal-rajput/green-chilli/dataset/1 |
| 파프리카 (토마토와 구분용) | mvi-n1mve / bell-pepper-ydvso | 5 | https://universe.roboflow.com/mvi-n1mve/bell-pepper-ydvso/dataset/5 |
| 파프리카 (토마토와 구분용) | bell-pepper-vpkx5 / bell-pepper-rld1g | 1 | https://universe.roboflow.com/bell-pepper-vpkx5/bell-pepper-rld1g/dataset/1 |
| 파프리카 (토마토와 구분용) | khuyennguyen / bell-pepper-wu9ic | 1 | https://universe.roboflow.com/khuyennguyen/bell-pepper-wu9ic/dataset/1 |
| 파프리카 (토마토와 구분용) | bellpepper / bell-pepper-wxxwg | 4 | https://universe.roboflow.com/bellpepper/bell-pepper-wxxwg/dataset/4 |
| 파프리카 (토마토와 구분용) | thanakrit23 / bell-pepper-rtzwb | 1 | https://universe.roboflow.com/thanakrit23/bell-pepper-rtzwb/dataset/1 |
| 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) | cv-jaka4 / tomato-detection-ku6fz | 2 | https://universe.roboflow.com/cv-jaka4/tomato-detection-ku6fz/dataset/2 |
| 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) | olrnd / onion-yhzc7 | 1 | https://universe.roboflow.com/olrnd/onion-yhzc7/dataset/1 |
| 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) | fruits-hfscm / onion-n278m | 1 | https://universe.roboflow.com/fruits-hfscm/onion-n278m/dataset/1 |
| 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) | robocup2022-kogzd / onion-9renr | 2 | https://universe.roboflow.com/robocup2022-kogzd/onion-9renr/dataset/2 |
| 이미 충분한 재료 (상한에 걸리면 자동으로 덜 쓰임) | vision-6bf8h / onion-yol1h | 1 | https://universe.roboflow.com/vision-6bf8h/onion-yol1h/dataset/1 |
| 1·2차에 쓴 데이터 | vegetables-19jw7 / vegetables-2a164 | 1 | https://universe.roboflow.com/vegetables-19jw7/vegetables-2a164/dataset/1 |
| 1·2차에 쓴 데이터 | quiz2pcvk / vegetables-8jovr | 1 | https://universe.roboflow.com/quiz2pcvk/vegetables-8jovr/dataset/1 |
| 1·2차에 쓴 데이터 | robouserflow / vegetables-cg8tb | 6 | https://universe.roboflow.com/robouserflow/vegetables-cg8tb/dataset/6 |
| 1·2차에 쓴 데이터 | vegetables-gdugj / vegetables-y393s | 1 | https://universe.roboflow.com/vegetables-gdugj/vegetables-y393s/dataset/1 |
| 1·2차에 쓴 데이터 | vegetables / vegetables-el4g6 | 1 | https://universe.roboflow.com/vegetables/vegetables-el4g6/dataset/1 |
| 1·2차에 쓴 데이터 | 09yolosophie / vegetables-zvz0j | 3 | https://universe.roboflow.com/09yolosophie/vegetables-zvz0j/dataset/3 |
| 1·2차에 쓴 데이터 | dijital-gen / vegetables-345nt | 1 | https://universe.roboflow.com/dijital-gen/vegetables-345nt/dataset/1 |
| 1·2차에 쓴 데이터 | jasur-vkjtq / vegetables-tzoje | 1 | https://universe.roboflow.com/jasur-vkjtq/vegetables-tzoje/dataset/1 |
| 1·2차에 쓴 데이터 | leal-jun-fzre6 / vegetables-9mixn | 1 | https://universe.roboflow.com/leal-jun-fzre6/vegetables-9mixn/dataset/1 |
| 1·2차에 쓴 데이터 | jesus-sduc5 / vegetables-gywcv | 1 | https://universe.roboflow.com/jesus-sduc5/vegetables-gywcv/dataset/1 |
| 1·2차에 쓴 데이터 | news / vegetables-mr0jj | 4 | https://universe.roboflow.com/news/vegetables-mr0jj/dataset/4 |
| 1·2차에 쓴 데이터 | gian-mwaaw / vegetables-fekan | 1 | https://universe.roboflow.com/gian-mwaaw/vegetables-fekan/dataset/1 |
| 1·2차에 쓴 데이터 | marvin-sumper / vegetables-spshw | 2 | https://universe.roboflow.com/marvin-sumper/vegetables-spshw/dataset/2 |
| 1·2차에 쓴 데이터 | power-k17io / vegetables-xrtxa | 1 | https://universe.roboflow.com/power-k17io/vegetables-xrtxa/dataset/1 |
| 1·2차에 쓴 데이터 | myworkspace-tfvkf / vegetables-zynnx | 2 | https://universe.roboflow.com/myworkspace-tfvkf/vegetables-zynnx/dataset/2 |
| 1·2차에 쓴 데이터 | test-lgzia / vegetables-7kfdk | 2 | https://universe.roboflow.com/test-lgzia/vegetables-7kfdk/dataset/2 |
| 1·2차에 쓴 데이터 | test-on9hk / vegetables-kacga | 5 | https://universe.roboflow.com/test-on9hk/vegetables-kacga/dataset/5 |
| 1·2차에 쓴 데이터 | robosidekick / vegetables-2xirf | 3 | https://universe.roboflow.com/robosidekick/vegetables-2xirf/dataset/3 |
| 1·2차에 쓴 데이터 | shakhob / vegetables-e2juh | 1 | https://universe.roboflow.com/shakhob/vegetables-e2juh/dataset/1 |
| 1·2차에 쓴 데이터 | monash-university-dkmtq / vegetables-guwbg | 3 | https://universe.roboflow.com/monash-university-dkmtq/vegetables-guwbg/dataset/3 |
| 1·2차에 쓴 데이터 | workspace-a52as / vegetables-zzsys | 1 | https://universe.roboflow.com/workspace-a52as/vegetables-zzsys/dataset/1 |
| 1·2차에 쓴 데이터 | 2024718 / vegetables-fkkxs | 6 | https://universe.roboflow.com/2024718/vegetables-fkkxs/dataset/6 |
| 1·2차에 쓴 데이터 | raw-food / vegetables-mmdn7 | 3 | https://universe.roboflow.com/raw-food/vegetables-mmdn7/dataset/3 |
| 1·2차에 쓴 데이터 | tushar-panwar-xvpdx / vegetables-mdufw | 1 | https://universe.roboflow.com/tushar-panwar-xvpdx/vegetables-mdufw/dataset/1 |

총 80개. 목록 원본: `cell_v4_data.py` 의 데이터셋 목록.

## 2. AI Hub 「농산물 품질(QC) 이미지」

- https://www.aihub.or.kr (dataSetSn=149). **국내에서만 받을 수 있다** (Colab 등 해외 서버는 차단)
- 이용 조건: 연구·학습 목적, **원본 재배포 금지** → 원본·오려 낸 사진·합성 사진 모두 저장소와 공개 장소에 올리지 않는다
- 사용: Validation 원천데이터 중 무·양파·마늘·감자·사과·양배추·배추·배·귤 9종, 위·앞45°·대각45° 각도
- 처리: PC에서 `qc_local.py` 로 배경을 지우고 재료만 오려 냄(8,310장) → Colab 에서 냉장고·식탁 느낌 배경에 합성 6,000장

## 3. 직접 찍은 사진 (v5 예정)

- 팀원이 찍은 사진은 `ai/train/own_photos/` 가 아니라 팀 드라이브에 둔다. 사람 얼굴·개인정보가 찍히지 않게 한다
