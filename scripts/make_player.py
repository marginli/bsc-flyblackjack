"""播放台單獨版（player.html）的資料與離線包。
  assets/demo/data.js                         data.json 包成 window.BJ_DATA（file:// 開網頁時 fetch 讀不到 JSON，<script> 可以）
  downloads/player/flyblackjack-player.zip    player.html ＋ assets/demo/（data.js、三支影片）＋ 使用說明，解壓後直接用瀏覽器開
放在 downloads/player/ 而不是 downloads/：README 的重打包指令會 rm downloads/*.zip。
data.json 或影片改了（build_demo_data.py 之後）就重跑。
用法：python3 scripts/make_player.py"""
import json
import os
import zipfile

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(D, "assets/demo")
VIDEOS = ["bj_fly.mp4", "bj_nodopa.mp4", "bj_untrained.mp4"]
README = """蕈狀體玩 21 點：播放台離線版

用法：解壓縮後，用瀏覽器（Chrome、Edge、Safari、Firefox）打開 player.html。
不需要網路，也不用裝任何東西。player.html 旁邊的 assets 資料夾要一起留著。

簡報時：在投影片上插入超連結，連到這個 player.html，點了就開瀏覽器；按「全螢幕」放大整頁。
指定一開始的條件與手數：在網址後面加 ?b=bj_nodopa&h=6
  b：bj_fly（連結體＋多巴胺）、bj_nodopa（切斷多巴胺）、bj_untrained（未訓練）
  h：從第幾手開始
鍵盤：空白鍵 播放／暫停、← → 一格、Shift＋← → 一手、1 2 3 換條件

線上版：https://marginli.github.io/bsc-flyblackjack/player.html
說明：https://marginli.github.io/bsc-flyblackjack/part5-demo.html
"""

data = json.load(open(os.path.join(DEMO, "data.json"), encoding="utf-8"))
js = "window.BJ_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
open(os.path.join(DEMO, "data.js"), "w", encoding="utf-8").write(js)

out = os.path.join(D, "downloads/player/flyblackjack-player.zip")
os.makedirs(os.path.dirname(out), exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    root = "flyblackjack-player/"
    z.write(os.path.join(D, "player.html"), root + "player.html")
    z.writestr(root + "使用說明.txt", README)
    z.write(os.path.join(DEMO, "data.js"), root + "assets/demo/data.js")
    for v in VIDEOS:
        z.write(os.path.join(DEMO, v), root + "assets/demo/" + v, compress_type=zipfile.ZIP_STORED)
print("data.js", len(js) // 1024, "KB;", out, os.path.getsize(out) // 1024, "KB")
