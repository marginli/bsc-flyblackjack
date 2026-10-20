"""PART 1 第 4 節動畫（圖 3）的數字：完整模型（種子 0）第 1 手。硬 20 對莊家 8 選要牌、抽到 6 爆牌、輸一注，
懲罰強度 0.5。手結束後把「硬 20 對 8 配要牌」呈現一次（作者 FlyPlayer.outcome 的做法），逐步記下：
每顆 MBON 收到的多巴胺、72 顆亮 KC 通往各 MBON 的增益怎麼變、回復、三個動作學之前與學之後的好惡值。
學之後的三個好惡值要等於 out/bj_demo_summary.json 第 2 手以前的狀態算出來的值（這裡直接用作者的 present 重算比對）。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/learn_anim_data.json）"""
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj
from flybrain.mb.model import MushroomBody

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/learn_anim_data.json")
HAND = json.load(open(os.path.join(D, "out/bj_demo_summary.json")))["conditions"]["bj_fly"]["hands"]["1"]
REC = HAND["decisions"][0]
assert HAND["net"] == -1.0 and REC["chosen"] == "hit"

fly = bj.FlyPlayer(seed=0)                 # 21 點的設定：lr 0.05、decay 0.00005
mb, sit = fly.mb, fly.sit
pt, soft, up, first = REC["total"], REC["soft"], REC["upcard"], REC["first"]
ACT = {"hit": bj.HIT, "stand": bj.STAND, "double": bj.DOUBLE}
drive = {k: sit.encode(pt, soft, up, first, a) for k, a in ACT.items()}

def snapshot():
    r = {}
    for k in ACT:
        o = mb.present(None, learn=False, drive=drive[k])
        r[k] = {"valence": float(o["valence"]), "mbon": o["mbon"].copy(), "kc": o["kc"].copy()}
    return r

before = snapshot()
for k in ACT:
    assert round(before[k]["valence"], 4) == REC["values"][k]

strength = float(np.clip(abs(HAND["net"]) / 2.0, 0.15, 1.0))
assert strength == HAND["dopamine_strength"] == 0.5
da = mb.dopamine(strength, 0.0)            # 每顆 MBON 收到的多巴胺＝強度 × 來自 PPL1 的比例
kc = before["hit"]["kc"]
g0 = mb.gain.copy()
cut = mb.lr * np.outer(kc, da)             # 第一行：削弱量
fly.outcome(HAND["net"], [((pt, soft, up, first), bj.HIT)])   # 作者自己的學習流程
g1 = mb.gain.copy()
assert np.allclose(g1, np.clip((g0 - cut) + mb.decay * (1 - (g0 - cut)), 0, 1))
after = snapshot()

lit = np.flatnonzero(kc > 0)
val = mb.valence.astype(int)
changed = (g1 < 1 - 1e-12)
res = {
    "strength": strength, "lr": mb.lr, "decay": mb.decay,
    "n_kc_lit": int(len(lit)),
    "da": [round(float(x), 4) for x in da],
    "n_mbon_da_pos": int((da > 0).sum()), "n_mbon_da_zero": int((da == 0).sum()),
    "da_max": round(float(da.max()), 4),
    "da_share_plus": round(float(da[val > 0].sum() / da.sum()), 3),
    "kc_values": {int(i): round(float(kc[i]), 3) for i in lit},
    "kc_max": round(float(kc.max()), 3),
    "cut_max": round(float(cut.max()), 4),
    "gain_min_after": round(float(g1.min()), 4),
    "n_links_cut": int(((cut > 0) & (mb.W_kc_mbon > 0)).sum()),
    "n_links_kc_lit": int((mb.W_kc_mbon[lit] > 0).sum()),
    "n_links_total": int((mb.W_kc_mbon > 0).sum()),
    "decay_one_step_on_min": float(mb.decay * (1 - (g0 - cut).min())),
    # 每顆 MBON 的增益平均（只看亮 KC 連過來的，有接線的）學前／學後
    "mbon_before": {k: [round(float(x), 4) for x in before[k]["mbon"]] for k in ACT},
    "mbon_after": {k: [round(float(x), 4) for x in after[k]["mbon"]] for k in ACT},
    "valence_before": {k: round(before[k]["valence"], 4) for k in ACT},
    "valence_after": {k: round(after[k]["valence"], 4) for k in ACT},
    "sum_plus_before": round(float(before["hit"]["mbon"][val > 0].sum()), 4),
    "sum_minus_before": round(float(before["hit"]["mbon"][val < 0].sum()), 4),
    "sum_plus_after": round(float(after["hit"]["mbon"][val > 0].sum()), 4),
    "sum_minus_after": round(float(after["hit"]["mbon"][val < 0].sum()), 4),
    "kc_shared_hit_stand": int(len(set(np.flatnonzero(before["hit"]["kc"] > 0)) & set(np.flatnonzero(before["stand"]["kc"] > 0)))),
    "kc_shared_hit_double": int(len(set(np.flatnonzero(before["hit"]["kc"] > 0)) & set(np.flatnonzero(before["double"]["kc"] > 0)))),
}
_rec = mb.decay * (1 - (g0 - cut).min())          # 剛被削到最低的那條，回復一步拉回的量
res["decay_on_min_txt"] = f"{_rec:.8f}".rstrip("0"); res["decay_on_min_2sf"] = f"{_rec:.7f}"
res["hit_drop"] = round(res["valence_before"]["hit"] - res["valence_after"]["hit"], 4)
res["hit_minus_stand_after"] = round(res["valence_after"]["hit"] - res["valence_after"]["stand"], 4)
json.dump(res, open(OUT, "w"), ensure_ascii=False)
brief = {k: v for k, v in res.items() if k not in ("da", "kc_values", "mbon_before", "mbon_after")}
print(json.dumps(brief, ensure_ascii=False, indent=1))
