"""PART 4：作者沒做、本課加做的四項檢查，全部在 21 點上做（X4 看的是電路本身的標記）。在 repo/ 目錄下以 PYTHONPATH=. 執行。
不改作者程式碼；需要不同電路或打亂時，把 blackjack 模組裡的 MushroomBody 名字換成指向我們版本的函式。
  X1 種子數：3 → 20。完整模型、切斷多巴胺、未訓練各 20 個種子，報告最後 2,000 手平均的平均、SD、95% CI
  X2 打亂哪一層：KC→MBON 打亂（作者 model.py 的 shuffle，5 個種子各一種打亂）；
     DAN→MBON 打亂（把每顆 DAN 連到的 MBON 欄位隨機置換，5 種置換 × 3 個種子）
  X3 KC 選法：作者用 1,200 顆「依排名等距取樣」；改成全部在路徑上的 KC ＋ 3 組隨機 1,200 顆，各 3 個種子
  X4 MBON 價值：作者依主要多巴胺輸入標 +1/−1；與 Aso 2014 的傳導物質規則
     （麩胺酸 MBON 活化 → 迴避；乙醯膽鹼 / GABA → 趨近）交叉比對
用法：python bj_extra.py [hands]（預設 30000；給小數字只是試跑）
"""
import json, sys, time
from pathlib import Path
from collections import Counter
import numpy as np
import scipy.sparse as sp

from flybrain.mb import blackjack as bj
from flybrain.mb.model import MushroomBody
from flybrain.mb.extract import extract

HANDS = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
OUT = Path("../results"); (OUT / "circuits").mkdir(parents=True, exist_ok=True)
res = {"hands": HANDS}


def stats(v):
    v = np.asarray(v, float); se = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0
    return dict(n=len(v), mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                ci95=[float(v.mean() - 1.96 * se), float(v.mean() + 1.96 * se)])


def use_circuit(path=None, post=None, **mb_kw):
    """讓 FlyPlayer 建蕈狀體時用指定的 npz 與設定，並可在建好後對 model 動手腳（post）。"""
    def make(**kw):
        mb = MushroomBody(path=path or "data/mb_circuit.npz", **mb_kw, **kw)
        if post: post(mb)
        return mb
    bj.MushroomBody = make


def play(seed, tag, **kw):
    """一個種子打 HANDS 手，回傳每 2,000 手一塊的平均與一致率。"""
    t0 = time.time()
    fly = bj.FlyPlayer(seed=seed, **kw)
    _, blocks, agree = bj.session(fly, hands=HANDS, seed=seed)
    r = dict(seed=seed, first_block=blocks[0], last_block=blocks[-1], agree_first=agree[0], agree_last=agree[-1], blocks=blocks, agree=agree)
    print(f"{tag:40s} seed {seed:2d}  winrate {blocks[0]:+.3f} -> {blocks[-1]:+.3f}  agree {agree[0]:.3f} -> {agree[-1]:.3f}  ({time.time() - t0:.0f}s)", flush=True)
    return r


def summarise(runs):
    return dict(runs=runs, last=stats([r["last_block"] for r in runs]), agree_last=stats([r["agree_last"] for r in runs]))


# ---------------- X1：種子 3 → 20
use_circuit()
SEEDS20 = list(range(20))
x1 = {}
for name, kw in [("connectome + dopamine", {}), ("dopamine cut + exploration decay", dict(dopamine=False)),
                 ("untrained greedy", dict(learn=False, explore=0.0, explore_floor=0.0))]:
    x1[name] = summarise([play(s, f"X1 {name}", **kw) for s in SEEDS20])
    x1[name]["first3"] = stats([r["last_block"] for r in x1[name]["runs"][:3]])
res["X1_seeds20"] = x1
print("X1", {k: round(v["last"]["mean"], 4) for k, v in x1.items()}, flush=True)

# ---------------- X2：打亂哪一層
x2 = {}
runs = []
for s in range(5):
    use_circuit(shuffle_kc_mbon=True, seed=s)        # 作者 model.py 的 degree-preserving 打亂，每個種子一種
    runs.append(play(s, "X2 KC->MBON shuffled"))
x2["kc_mbon_shuffled"] = summarise(runs)
perms = []
for k in range(5):
    def perm_dan(mb, k=k):
        rng = np.random.default_rng(1000 + k)
        mb.W_dan_mbon = mb.W_dan_mbon[:, rng.permutation(mb.n_mbon)]
    use_circuit(post=perm_dan)
    runs = [play(s, f"X2 DAN->MBON perm {k}") for s in range(3)]
    perms.append(dict(perm=k, **summarise(runs)))
x2["dan_mbon_shuffled"] = dict(per_permutation=perms, mean_of_means=float(np.mean([p["last"]["mean"] for p in perms])),
                               agree_mean_of_means=float(np.mean([p["agree_last"]["mean"] for p in perms])))
res["X2_layers"] = x2
print("X2", round(x2["kc_mbon_shuffled"]["last"]["mean"], 4), round(x2["dan_mbon_shuffled"]["mean_of_means"], 4), flush=True)

# ---------------- X3：KC 選法
blocks, info = extract(kenyon=None)          # 全部在路徑上的 KC
n_live = blocks["pn_kc"].shape[1]


def save_npz(path, bl, info):
    arrays = {}
    for name, b in bl.items():
        coo = sp.coo_matrix(b)
        arrays[f"{name}_row"] = coo.row.astype(np.int32); arrays[f"{name}_col"] = coo.col.astype(np.int32)
        arrays[f"{name}_val"] = coo.data.astype(np.float32); arrays[f"{name}_shape"] = np.array(b.shape, np.int32)
    arrays["mbon_valence"] = np.array(info["mbon_valence"], np.int8)
    arrays["dan_is_punishment"] = np.array(info["dan_is_punishment"], np.int8)
    np.savez_compressed(path, **arrays)


x3 = {}
variants = {"all_live_kc": np.arange(n_live)}
for k in range(3):
    variants[f"random1200_{k}"] = np.sort(np.random.default_rng(500 + k).choice(n_live, 1200, replace=False))
for name, idx in variants.items():
    bl = dict(blocks); bl["pn_kc"] = blocks["pn_kc"][:, idx]; bl["kc_mbon"] = blocks["kc_mbon"][idx, :]
    p = OUT / "circuits" / f"mb_{name}.npz"; save_npz(p, bl, info)
    use_circuit(path=str(p))
    x3[name] = dict(n_kc=int(len(idx)), **summarise([play(s, f"X3 {name}") for s in range(3)]))
res["X3_kc_subsets"] = dict(n_live_kc=int(n_live), variants=x3)
print("X3", {k: round(v["last"]["mean"], 4) for k, v in x3.items()}, flush=True)

# ---------------- X4：MBON 標記對文獻規則
cells = json.loads(Path("data/mb_cells.json").read_text())
types, nts, val = cells["types"]["mbon"], cells["nt"]["mbon"], cells["mbon_valence"]
lit = {"glutamate": -1, "acetylcholine": 1, "gaba": 1}
rows, tab = [], Counter()
for t, nt, v in zip(types, nts, val):
    exp = lit.get(nt.lower())
    tab[(nt, v)] += 1
    rows.append(dict(type=t, nt=nt, author=v, nt_rule=exp, agree=(exp == v) if exp is not None and v != 0 else None))
judged = [r for r in rows if r["agree"] is not None]
res["X4_mbon_valence"] = dict(
    rule="Aso et al. 2014 eLife：麩胺酸 MBON 活化促迴避（−1），乙醯膽鹼／GABA 促趨近（+1）；簡化規則，有已知例外",
    crosstab={f"{nt}|{v:+d}": n for (nt, v), n in sorted(tab.items())},
    judged=len(judged), agree=sum(r["agree"] for r in judged),
    disagree=[r for r in judged if not r["agree"]], cells=rows)
print("X4", res["X4_mbon_valence"]["crosstab"], res["X4_mbon_valence"]["agree"], "/", len(judged), flush=True)

(OUT / "bj_extra.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
print("wrote ../results/bj_extra.json")
