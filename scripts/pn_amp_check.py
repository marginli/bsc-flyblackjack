#!/usr/bin/env python3
"""PN 活動「0.7 到 1」這個人設重不重要：換成別的範圍再打 21 點。

   作者 flybrain/mb/blackjack.py 第 161 行：pn[cells] = amp * rng.uniform(0.7, 1.0, size=len(cells))，
   0.7、1.0 沒有說明。這裡只換這兩個數，其餘逐行照抄作者的 Situation.__init__；
   rng.uniform 不論範圍都消耗同樣多的亂數，所以每個值選中哪些 PN 完全不變，變的只有活動量。
     author   0.7–1.0（作者原值；應與 PART 4 X1 的 20 個種子逐位相同，當作核對）
     flat     1.0–1.0（選中的 PN 全部一樣強，沒有起伏）
     odour    0.45–1.0（同一個 repo 的 T 迷宮氣味 odour.py 用的強度範圍）
   每種範圍：完整模型（連結體＋多巴胺）與未訓練（不學、不探索）各 20 個種子 × 30,000 手。
   在作者 repo 目錄下執行：cd <repo> && PYTHONPATH=. python3 <本檔>，寫 out/blackjack/pn_amp_check.json。
"""
import json, os, sys, time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "out/blackjack/pn_amp_check.json"
HANDS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30000
SEEDS = list(range(20))
RANGES = {"author": (0.7, 1.0), "flat": (1.0, 1.0), "odour": (0.45, 1.0)}
CONDS = {"connectome + dopamine": {}, "untrained greedy": dict(learn=False, explore=0.0, explore_floor=0.0)}


def patch(lo, hi):
    from flybrain.mb import blackjack as bj

    def __init__(self, mb, seed=20260914):            # 照抄作者 Situation.__init__，只換 0.7、1.0
        self.mb = mb
        rng = np.random.default_rng(seed)
        n = mb.n_pn
        self.drive = {}
        for feature, levels, ordered in [("total", 18, True), ("upcard", 10, True),
                                         ("action", 3, False), ("soft", 2, False),
                                         ("first", 2, False)]:
            width = self.WIDTH[feature]
            pool = rng.permutation(n)
            for level in range(levels):
                pn = np.zeros(n)
                if ordered:
                    start = int(level * width * 0.55)
                    cells = pool[start:start + width]
                else:
                    cells = rng.choice(n, width, replace=False)
                amp = 1.3 if feature == "action" else 1.0
                pn[cells] = amp * rng.uniform(lo, hi, size=len(cells))
                self.drive[(feature, level)] = mb.pn_drive(pn)
    bj.Situation.__init__ = __init__
    return bj


def job(args):
    rname, cname, seed = args
    bj = patch(*RANGES[rname])
    t0 = time.time()
    fly = bj.FlyPlayer(seed=seed, **CONDS[cname])
    _, blocks, agree = bj.session(fly, hands=HANDS, seed=seed)
    print(f"{rname:7s} {cname:22s} seed {seed:2d}  last {blocks[-1]:+.4f}  agree {agree[-1]:.3f}  ({time.time() - t0:.0f}s)", flush=True)
    return rname, cname, dict(seed=seed, first_block=blocks[0], last_block=blocks[-1],
                              agree_first=agree[0], agree_last=agree[-1])


def stats(v):
    v = np.asarray(v, float); se = v.std(ddof=1) / np.sqrt(len(v))
    return dict(n=len(v), mean=float(v.mean()), sd=float(v.std(ddof=1)),
                ci95=[float(v.mean() - 1.96 * se), float(v.mean() + 1.96 * se)])


def derive(res):
    """和「永遠停牌」比（reference_margin.json，20,000 手）；差的 95% CI 照 reference_margin 的算法。"""
    ref = json.loads((OUT.parent / "reference_margin.json").read_text())["always stand"]
    se_ref = ref["sd"] / np.sqrt(json.loads((OUT.parent / "reference_margin.json").read_text())["hands"])
    res["always_stand"] = ref["mean"]
    for r, v in res["results"].items():
        f = v["connectome + dopamine"]["last"]
        se = np.hypot(f["sd"] / np.sqrt(f["n"]), se_ref)
        diff = f["mean"] - ref["mean"]
        v["minus_always_stand"] = dict(diff=round(float(diff), 4), ci95=[round(float(diff - 1.96 * se), 4), round(float(diff + 1.96 * se), 4)])
    return res


if __name__ == "__main__" and sys.argv[1:] == ["--derive"]:      # 不重跑，只補比較欄位
    OUT.write_text(json.dumps(derive(json.loads(OUT.read_text())), indent=1, ensure_ascii=False))
    sys.exit()

if __name__ == "__main__":
    jobs = [(r, c, s) for r in RANGES for c in CONDS for s in SEEDS]
    with Pool(min(12, os.cpu_count())) as p:
        got = p.map(job, jobs, chunksize=1)
    res = {"hands": HANDS, "seeds": SEEDS, "ranges": {k: list(v) for k, v in RANGES.items()}, "results": {}}
    for r in RANGES:
        res["results"][r] = {}
        for c in CONDS:
            runs = sorted((x for rr, cc, x in got if rr == r and cc == c), key=lambda x: x["seed"])
            res["results"][r][c] = dict(runs=runs, last=stats([x["last_block"] for x in runs]),
                                        agree_last=stats([x["agree_last"] for x in runs]))
        full, un = (res["results"][r][c] for c in CONDS)
        res["results"][r]["learning_gain"] = round(full["last"]["mean"] - un["last"]["mean"], 4)
        res["results"][r]["agree_gain"] = round(full["agree_last"]["mean"] - un["agree_last"]["mean"], 4)
    # 核對：author 應與 PART 4 X1 逐位相同
    x1 = json.loads((OUT.parent / "bj_extra.json").read_text())["X1_seeds20"]
    res["author_matches_X1"] = {c: [x["last_block"] for x in res["results"]["author"][c]["runs"]] ==
                                   [x["last_block"] for x in x1[c]["runs"]] for c in CONDS}
    OUT.write_text(json.dumps(derive(res), indent=1, ensure_ascii=False))
    for r in RANGES:
        print(r, {c: (round(res["results"][r][c]["last"]["mean"], 4), round(res["results"][r][c]["agree_last"]["mean"], 4)) for c in CONDS})
    print("author_matches_X1", res["author_matches_X1"])
