"""PART 5 第 2 節「三條虛線」的誤差：照作者 reference_winrates() 的順序與種子（rng 種子 0、各 20,000 手）重打一次，
記下每手淨輸贏的標準差與 95% 信賴區間半寬（1.96 × 標準差 ÷ √20000）。平均應與 bj2 輸出的 reference 相同，用來確認重打的是同一批牌。
另算：完整模型 20 個種子（PART 4 X1）的平均比永遠停牌好多少，把兩邊的誤差都算進去的 95% 區間（標準誤平方和開根號）。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/reference_margin.json）"""
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/reference_margin.json")
rng, N = np.random.default_rng(0), 20000
pols = [("basic strategy", lambda t, s, u, f, L: bj.basic_strategy(t, s, u, f)),
        ("random", lambda t, s, u, f, L: int(rng.choice(L))),
        ("always stand", lambda t, s, u, f, L: bj.STAND)]
res = {"hands": N}
for name, pol in pols:
    x = np.array([bj.play_hand(pol, rng)[0] for _ in range(N)])
    sd = x.std(ddof=1)
    res[name] = {"mean": round(float(x.mean()), 6), "sd": round(float(sd), 3), "ci95_half": round(float(1.96 * sd / np.sqrt(N)), 3)}
x1 = np.array([r["last_block"] for r in json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))["X1_seeds20"]["connectome + dopamine"]["runs"]])
se_full = x1.std(ddof=1) / np.sqrt(len(x1)); se_ref = res["always stand"]["sd"] / np.sqrt(N)
diff = float(x1.mean() - res["always stand"]["mean"]); se = float(np.hypot(se_full, se_ref))
res["full20_minus_always_stand"] = {"diff": diff, "se": se, "ci95": [diff - 1.96 * se, diff + 1.96 * se], "z": diff / se}
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
