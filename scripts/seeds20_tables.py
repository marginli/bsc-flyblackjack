"""PART 4 X1 的 20 個種子補存逐格表（bj_extra.py 只記了勝率與一致率）。每個種子照 X1 的完整模型重打 30,000 手
（FlyPlayer(seed=s)、bj.session(seed=s)），存學完的 260 格表各動作格數、一致率（應與 X1 的 agree_last 逐位相同），
以及扣掉硬 21、軟 21 兩列（打牌時從不會是第一個決定的 20 格）之後的一致率；同一批 KC 的未訓練表也照樣算一次。
需要作者 repo。用法：cd <repo> && PYTHONPATH=. python <本檔> [--summary]   （輸出 out/blackjack/seeds20_tables.json；--summary 只用已存的表重算摘要）"""
import json
import os
import sys
from multiprocessing import Pool

from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/seeds20_tables.json")
CELLS = bj.chart_cells()
WANT = [bj.basic_strategy(t, s, u, True) for (t, s, u) in CELLS]
LIVE = [t != 21 for (t, s, u) in CELLS]


def table(fly):
    got = [fly.greedy(t, s, u, True, [bj.HIT, bj.STAND, bj.DOUBLE]) for (t, s, u) in CELLS]
    hit = [g == w for g, w in zip(got, WANT)]
    return {"hit": got.count(bj.HIT), "stand": got.count(bj.STAND), "double": got.count(bj.DOUBLE),
            "agree": sum(hit) / 260, "agree_no21": sum(h for h, l in zip(hit, LIVE) if l) / sum(LIVE)}


def run(s):
    fly = bj.FlyPlayer(seed=s)
    _, blocks, agree = bj.session(fly, hands=30000, seed=s)
    r = table(fly); r.update(seed=s, last_block=blocks[-1], agree_last_session=agree[-1])
    print(s, r, flush=True)
    return r


def summarise(runs, un):
    import numpy as np
    from scipy import stats as st
    x1 = json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))["X1_seeds20"]["connectome + dopamine"]["runs"]
    same = all(abs(r["agree"] - x["agree_last"]) < 1e-12 and r["last_block"] == x["last_block"] for r, x in zip(runs, x1))
    n21 = np.array([r["agree_no21"] for r in runs]); se = n21.std(ddof=1) / np.sqrt(len(n21)); q = st.t.ppf(0.975, len(n21) - 1)
    res = {"runs": runs, "untrained": un, "matches_x1": same}
    for k in ("hit", "stand", "double"):
        v = [r[k] for r in runs]; res[f"{k}_min"], res[f"{k}_max"] = min(v), max(v)
    res.update(agree_no21_mean=float(n21.mean()), agree_no21_ci_t=[float(n21.mean() - q * se), float(n21.mean() + q * se)],
               agree_no21_min=float(n21.min()), agree_no21_max=float(n21.max()),
               n_agree_no21_below_untrained=int((n21 < un["agree_no21"]).sum()),
               corr_hit_vs_last_block=float(np.corrcoef([r["hit"] for r in runs], [r["last_block"] for r in runs])[0, 1]))
    return res


if __name__ == "__main__":
    if "--summary" in sys.argv:       # 不重打，只用已存的逐格表重算摘要
        old = json.load(open(OUT)); runs, un = old["runs"], old["untrained"]
    else:
        with Pool(10) as p:
            runs = p.map(run, range(20))
        un = table(bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0))
    res = summarise(runs, un)
    json.dump(res, open(OUT, "w"), indent=1)
    print({k: v for k, v in res.items() if k != "runs"})
