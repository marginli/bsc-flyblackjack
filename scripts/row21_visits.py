"""硬 21、軟 21 兩列在打牌時出不出現：作者 play_hand 要牌後只要沒爆就再問一次，所以補到 21 點時模型還要再選一次（這時不能加倍，first=False）。
每個種子照 X1 的完整模型重打 30,000 手（FlyPlayer(seed=s)、bj.session(seed=s)），數每一次決定落在 21 點的次數與選的動作，
以及學完的表在這 20 格（first=True、可加倍，評分用的格）各選了什麼；同一批 KC 的未訓練表也算一次。
需要作者 repo。用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/row21_visits.json）"""
import json
import os
from multiprocessing import Pool

import numpy as np
from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/row21_visits.json")
ROW21 = [(t, s, u) for (t, s, u) in bj.chart_cells() if t == 21]
NAMES = {bj.HIT: "hit", bj.STAND: "stand", bj.DOUBLE: "double"}


def row21_table(fly):
    got = [fly.greedy(t, s, u, True, [bj.HIT, bj.STAND, bj.DOUBLE]) for (t, s, u) in ROW21]
    return {n: got.count(a) for a, n in NAMES.items()}


def run(s):
    fly = bj.FlyPlayer(seed=s)
    seen = {"decisions": 0, "at21": 0, "at21_first": 0, "at21_hit": 0, "at21_stand": 0}
    pol = fly.policy

    def counting(pt, soft, up, first, legal):
        a = pol(pt, soft, up, first, legal)
        seen["decisions"] += 1
        if pt == 21:
            seen["at21"] += 1; seen["at21_first"] += int(first)
            seen["at21_hit" if a == bj.HIT else "at21_stand"] += 1
        return a
    fly.policy = counting
    bj.session(fly, hands=30000, seed=s)
    r = dict(seen, seed=s, table21=row21_table(fly))
    print(s, r, flush=True)
    return r


if __name__ == "__main__":
    with Pool(10) as p:
        runs = p.map(run, range(20))
    un = row21_table(bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0))
    at21 = np.array([r["at21"] for r in runs])
    res = {"note": "at21＝30,000 手裡決定落在 21 點（硬或軟）的次數；at21_first 應為 0（兩張牌的 21 是黑傑克，直接結算）；"
                   "table21＝學完的表在硬 21、軟 21 兩列 20 格（評分用 first=True）各選幾格。",
           "runs": runs, "untrained_table21": un,
           "at21_mean": float(at21.mean()), "at21_min": int(at21.min()), "at21_max": int(at21.max()),
           "at21_share_mean": float(np.mean([r["at21"] / r["decisions"] for r in runs])),
           "at21_first_total": int(sum(r["at21_first"] for r in runs)),
           "stand21_min": min(r["table21"]["stand"] for r in runs), "stand21_max": max(r["table21"]["stand"] for r in runs),
           "stand21_mean": float(np.mean([r["table21"]["stand"] for r in runs]))}
    json.dump(res, open(OUT, "w"), indent=1)
    print({k: v for k, v in res.items() if k != "runs"})
