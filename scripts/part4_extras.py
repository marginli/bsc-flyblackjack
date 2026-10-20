"""PART 4 的補充數字：(1) X3 每一種 KC 選法「沒學過」的一致率（agreement of the untrained greedy policy），
讓 X3 的一致率有自己的基準；(2) X4 若標記與傳導物質無關、只保留 56／41 的比例時，預期的一致顆數（機率基準）；
(3) X3 每一種 KC 選法自己的未訓練成績（照 bj_extra.py 的 play()：種子 0–2、各 30,000 手、取最後 2,000 手），
讓 X3 的成績也有自己的對照組；(4) 小樣本的 95% 信賴區間改用 t 分布的係數，和 bj_extra.py 用的 1.96 並列；
(5) X2 打亂 KC→MBON 的 5 種打亂各自的未訓練成績與一致率（打亂方式與 bj_extra.py 相同：作者 model.py 的 shuffle_kc_mbon，種子 s 打亂、發牌也用種子 s，30,000 手、取最後 2,000 手）。
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

# (3) X3 每種選法自己的未訓練成績
untrained_x3 = {}
for name, path in [("author_1200", "data/mb_circuit.npz")] + [(k, os.path.join(CIRC, f"mb_{k}.npz")) for k in x["X3_kc_subsets"]["variants"]]:
    bj.MushroomBody = lambda path=path, **kw: MushroomBody(path=path, **kw)
    last = []
    for s in range(3):
        fly = bj.FlyPlayer(seed=s, learn=False, explore=0.0, explore_floor=0.0)
        _, blocks, _ = bj.session(fly, hands=30000, seed=s)
        last.append(float(blocks[-1]))
    untrained_x3[name] = {"last_by_seed": last, "mean": float(np.mean(last))}
    print("X3 untrained", name, [round(v, 4) for v in last], flush=True)

# (4) t 分布係數的 95% 區間（n 小時 1.96 偏窄）
from scipy import stats as st


def tci(v):
    v = np.asarray(v, float); n = len(v); se = v.std(ddof=1) / np.sqrt(n); q = float(st.t.ppf(0.975, n - 1))
    return {"n": n, "t": q, "mean": float(v.mean()), "half_196": float(1.96 * se), "half_t": float(q * se),
            "ci_t": [float(v.mean() - q * se), float(v.mean() + q * se)]}


tint = {"X1_full_20": tci([r["last_block"] for r in x["X1_seeds20"]["connectome + dopamine"]["runs"]]),
        "X1_full_first3": tci([r["last_block"] for r in x["X1_seeds20"]["connectome + dopamine"]["runs"][:3]]),
        "X2_kc_shuffled_5": tci([r["last_block"] for r in x["X2_layers"]["kc_mbon_shuffled"]["runs"]])}
for k, v in x["X3_kc_subsets"]["variants"].items():
    tint[f"X3_{k}"] = tci([r["last_block"] for r in v["runs"]])

# (5) X2 打亂 KC→MBON 的未訓練起點
untrained_kcshuf = []
for s in range(5):
    bj.MushroomBody = lambda s=s, **kw: MushroomBody(path="data/mb_circuit.npz", shuffle_kc_mbon=True, seed=s, **kw)
    fly = bj.FlyPlayer(seed=s, learn=False, explore=0.0, explore_floor=0.0)
    a0 = float(fly.agreement())
    _, blocks, _ = bj.session(fly, hands=30000, seed=s)
    untrained_kcshuf.append({"seed": s, "last": float(blocks[-1]), "agree": a0})
    print("X2 kc shuffled untrained", s, round(blocks[-1], 4), round(a0, 4), flush=True)
kcs = {"by_seed": untrained_kcshuf, "mean_last": float(np.mean([r["last"] for r in untrained_kcshuf])),
       "mean_agree": float(np.mean([r["agree"] for r in untrained_kcshuf])),
       "learned_mean_last": x["X2_layers"]["kc_mbon_shuffled"]["last"]["mean"],
       "learned_mean_agree": x["X2_layers"]["kc_mbon_shuffled"]["agree_last"]["mean"]}

res = {"untrained_kc_shuffled": kcs, "untrained_agreement": agree, "untrained_score_x3": untrained_x3, "t_intervals": tint,
       "learned_agreement": {"n": len(learned), "min": min(learned), "max": max(learned)},
       "dan_shuffled_agreement": {"n": len(dan), "min": min(dan), "max": max(dan)},
       "x4_chance": {"n_mbon": n, "n_approach": n_plus, "n_avoid": n_minus, "by_nt": rows,
                     "expected_agree": expected, "expected_share": expected / n,
                     "observed_agree": x["X4_mbon_valence"]["agree"], "observed_share": x["X4_mbon_valence"]["agree"] / n}}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
