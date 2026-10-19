"""PART 4 兩個補充數字：(1) X3 每一種 KC 選法「沒學過」的一致率（agreement of the untrained greedy policy），
讓 X3 的一致率有自己的基準；(2) X4 若標記與傳導物質無關、只保留 56／41 的比例時，預期的一致顆數（機率基準）。
需要作者 repo（~/claude_bscai/fly_play_game/blackjack/repo，commit 004b2e3）與實跑存下的電路檔 results/circuits/。
用法：cd <repo> && PYTHONPATH=. python scripts/part4_extras.py   （輸出 out/blackjack/part4_extras.json）"""
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj
from flybrain.mb.model import MushroomBody

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/part4_extras.json")
CIRC = os.path.expanduser("~/claude_bscai/fly_play_game/blackjack/results/circuits")
x = json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))

# (1) 沒學過的一致率：每種電路，建一個不學、不探索的 FlyPlayer，直接算 agreement()
agree = {}
for name, path in [("author_1200", "data/mb_circuit.npz")] + [(k, os.path.join(CIRC, f"mb_{k}.npz")) for k in x["X3_kc_subsets"]["variants"]]:
    bj.MushroomBody = lambda path=path, **kw: MushroomBody(path=path, **kw)
    fly = bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0)
    agree[name] = float(fly.agreement())

# 學完的一致率散佈：完整模型 20 種子 ＋ X3 四種選法各 3 種子 ＋ KC→MBON 打亂 5 種子，對 DAN→MBON 打亂 15 次
learned = [r["agree_last"] for r in x["X1_seeds20"]["connectome + dopamine"]["runs"]]
learned += [r["agree_last"] for v in x["X3_kc_subsets"]["variants"].values() for r in v["runs"]]
learned += [r["agree_last"] for r in x["X2_layers"]["kc_mbon_shuffled"]["runs"]]
dan = [r["agree_last"] for p in x["X2_layers"]["dan_mbon_shuffled"]["per_permutation"] for r in p["runs"]]

# (2) X4 的機率基準：交叉表的列（傳導物質）與欄（作者標記）獨立時的期望一致數
tab = x["X4_mbon_valence"]["crosstab"]
n = sum(tab.values())
n_plus = sum(v for k, v in tab.items() if k.endswith("+1")); n_minus = n - n_plus
rows = {}
for k, v in tab.items():
    nt = k.split("|")[0]; rows[nt] = rows.get(nt, 0) + v
rule = {"glutamate": "-1", "acetylcholine": "+1", "gaba": "+1"}
expected = sum(rows[nt] * (n_plus if rule[nt] == "+1" else n_minus) / n for nt in rows)

res = {"untrained_agreement": agree,
       "learned_agreement": {"n": len(learned), "min": min(learned), "max": max(learned)},
       "dan_shuffled_agreement": {"n": len(dan), "min": min(dan), "max": max(dan)},
       "x4_chance": {"n_mbon": n, "n_approach": n_plus, "n_avoid": n_minus, "by_nt": rows,
                     "expected_agree": expected, "expected_share": expected / n,
                     "observed_agree": x["X4_mbon_valence"]["agree"], "observed_share": x["X4_mbon_valence"]["agree"] / n}}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
