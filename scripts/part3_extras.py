"""PART 3 的補充數字（不在下載包裡，只給課程頁用）：
(1) 作者附的大腦檔 data/brain_seed.json（載入方式照 blackjack/scripts/bj3_author_brain.py）和本課種子 0 學完的 260 格表逐格比，幾格選的動作不同；
    本課種子 0 的表取 fly_play_game/demo/rec/bj_fly.json 打完 30,000 手那張快照（與 BJ2 種子 0 逐塊核對過）。
(2) 作者大腦檔實際打牌的成績：不學、不探索，用 bj.session 打 20,000 手（發牌種子 0），附 95% 信賴區間（1.96 × 標準差 ÷ √20000）。
(3) 對照組頭 2,000 手為什麼比純亂選和純未訓練都好：未訓練的蕈狀體（不學）把探索機率固定在頭 2,000 手的平均 28.6%，
    每個決定照作者 policy() 擲一次，種子 0–2 各打 20,000 手。
(4) 20 個種子（PART 4 X1）頭 2,000 手的平均與標準差，和 3 個種子的值並列。
(5) 和作者大腦檔同條件比：本課種子 0 照 BJ2 的完整模型打 30,000 手學完，再關掉學習與探索、用發牌種子 0 打 20,000 手。
(6) 單一種子的一致率散多開：PART 4 X1 完整模型 20 個種子學完的一致率，最小、最大、幾個 ≥ 52%（README 的值取整前可能是 51.5% 以上）。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/part3_extras.json）"""
import base64
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/part3_extras.json")
REC = os.path.expanduser("~/claude_bscai/fly_play_game/demo/rec/bj_fly.json")
E = json.load(open(os.path.join(D, "out/blackjack/explore_schedule.json")))
N = 20000


def ci(x):
    x = np.asarray(x, float); h = 1.96 * x.std(ddof=1) / np.sqrt(len(x))
    return {"mean": float(x.mean()), "ci95": [float(x.mean() - h), float(x.mean() + h)], "hands": len(x)}


# (1)(2) 作者大腦檔
b = json.load(open("data/brain_seed.json"))
w = json.load(open("site/mb.json"))["w_kc_mbon"]
g = np.frombuffer(base64.b64decode(b["gain"]), np.uint8) / 255.0
fly = bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0)
gain = np.ones_like(fly.mb.gain); gain[w["r"], w["c"]] = g
fly.mb.gain = gain
cells = bj.chart_cells()
brain = [int(fly.greedy(t, s, u, True, [bj.HIT, bj.STAND, bj.DOUBLE])) for (t, s, u) in cells]
rec = json.load(open(REC))
assert [tuple(c) for c in rec["chart_cells"]] == [(t, int(s), u) for (t, s, u) in cells]
ours = {sn["h"]: sn["cells"] for sn in rec["snaps"]}[30000]
diff = sum(a != c for a, c in zip(brain, ours))
nets, _, _ = bj.session(fly, hands=N, seed=0)
res = {"brain_vs_seed0_cells_differ": int(diff), "brain_vs_seed0_cells_same": 260 - int(diff),
       "brain_counts": {"hit": brain.count(0), "stand": brain.count(1), "double": brain.count(2)},
       "brain_play": ci(nets), "brain_stored_units_per_hand": b["units"] / b["hands"]}

# (3) 固定 28.6% 逐個決定亂選的未訓練蕈狀體
p = E["pct_mean_first_2000"] / 100
mix = []
for s in range(3):
    f = bj.FlyPlayer(seed=s, learn=False, explore=p, explore_floor=p)
    nets, _, _ = bj.session(f, hands=N, seed=s)
    mix.append(ci(nets))
res["untrained_with_fixed_explore"] = {"explore": p, "by_seed": mix, "mean_of_seeds": float(np.mean([m["mean"] for m in mix]))}
# (4) 頭 2,000 手那一塊在 20 個種子間散多開（PART 4 X1 的 first_block），看 3 個種子的 −42.7% 是不是落在雜訊裡
x1 = json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))["X1_seeds20"]
res["first_block_20_seeds"] = {}
for c in ("dopamine cut + exploration decay", "untrained greedy"):
    fb = np.array([r["first_block"] for r in x1[c]["runs"]])
    lb = np.array([r["last_block"] for r in x1[c]["runs"]])
    res["first_block_20_seeds"][c] = {"first_mean": float(fb.mean()), "first_sd": float(fb.std(ddof=1)),
                                      "first_3": [float(v) for v in fb[:3]], "first_3_mean": float(fb[:3].mean()),
                                      "last_mean": float(lb.mean()), "drop": float(lb.mean() - fb.mean())}
# (5) 種子 0 學完後凍結、不探索實打
f = bj.FlyPlayer(seed=0)
bj.session(f, hands=30000, seed=0)
f.learn, f.explore0, f.explore_floor = False, 0.0, 0.0
nets, _, _ = bj.session(f, hands=N, seed=0)
res["seed0_frozen_play"] = ci(nets)
res["seed0_frozen_play"]["agree"] = float(f.agreement())
# (6) 20 個種子學完的一致率
al = sorted(r["agree_last"] for r in x1["connectome + dopamine"]["runs"])
res["agree_last_20_seeds"] = {"min": al[0], "max": al[-1], "n_ge_515": sum(a >= 0.515 for a in al), "n": len(al), "sorted": al}
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
