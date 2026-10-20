"""PART 1 第 5 節「探索」的時間表：作者 FlyPlayer.exploration() 在幾個手數的值。
常數直接讀 FlyPlayer 的預設值（explore 0.35、explore_floor 0.03、explore_halflife 3000），公式照 exploration() 原樣。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/explore_schedule.json）"""
import json
import os

from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/explore_schedule.json")
fly = bj.FlyPlayer(seed=0)
res = {"explore0": fly.explore0, "floor": fly.explore_floor, "halflife": fly.halflife, "pct": {}}
for h in (0, 1500, 3000, 6000, 9000, 15000, 30000):
    fly.hands = h
    res["pct"][str(h)] = round(fly.exploration() * 100, 2)
fly.hands = 2000; res["pct"]["2000"] = round(fly.exploration() * 100, 1)
_v = []
for h in range(2000):
    fly.hands = h; _v.append(fly.exploration())
res["pct_mean_first_2000"] = round(sum(_v) / len(_v) * 100, 1)                # 頭 2,000 手的平均探索機率
res["pct_3000_if_total_halved"] = round(fly.explore0 / 2 * 100, 1)   # 對照：若整個機率減半會是 17.5%
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
