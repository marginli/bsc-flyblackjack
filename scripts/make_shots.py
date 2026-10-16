"""從 PART 5 的影片抽幾張畫面給說明影片的投影片用（assets/p5-shot-bj-*.png）。
時間點由 assets/demo/data.json 的逐格資料算出：第 1 手聞候選動作、第 6 手結果、快轉段中間。
用法：python3 scripts/make_shots.py"""
import json
import os
import subprocess

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(D, "assets/demo/data.json")))["bj_episodes"]["bj_fly"]
FPS = E["fps"]


def frames(cond):
    return [i for i in range(E["n"]) if cond(i)]


picks = {
    "hand1": frames(lambda i: E["h"][i] == 0 and E["st"][i] == 1)[-3],          # 第 1 手，聞最後一個候選動作
    "hand6": frames(lambda i: E["h"][i] == 5 and E["st"][i] == 6)[8],           # 第 6 手，結果出來、多巴胺閃
    "ff": frames(lambda i: E["st"][i] == 7)[len(frames(lambda i: E["st"][i] == 7)) // 2],   # 快轉中段
}
for name, f in picks.items():
    out = os.path.join(D, "assets", f"p5-shot-bj-{name}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{(f + 0.5) / FPS:.3f}", "-i",
                    os.path.join(D, "assets/demo/bj_fly.mp4"), "-frames:v", "1", out], check=True)
    print(name, "frame", f, "→", out)
