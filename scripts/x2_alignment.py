"""X2 的原因量測：DAN→MBON 每一種重排之後，懲罰訊號落在趨近型（+1）MBON 的比例、獎賞落在迴避型（−1）MBON 的比例。
原始接線對照。PART 4 第 3 節引用；bj_extra.py 的 5 種重排用同樣的亂數（default_rng(1000 + k)）重建。
需要作者 repo（~/claude_bscai/fly_play_game/blackjack/repo，commit 004b2e3）與它的 data/mb_circuit.npz。
用法：cd <repo> && PYTHONPATH=. python scripts/x2_alignment.py   （輸出 out/blackjack/x2_alignment.json）"""
import json
import os

import numpy as np
from flybrain.mb.model import MushroomBody

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out/blackjack/x2_alignment.json")
mb = MushroomBody()
W, v, pm = mb.W_dan_mbon, mb.valence, mb.punish_mask


def shares(Wm):
    dan = np.zeros(mb.n_dan); dan[pm] = 1; dp = Wm.T @ dan          # 單位懲罰送到各 MBON 的量
    dan = np.zeros(mb.n_dan); dan[~pm] = 1; dr = Wm.T @ dan         # 單位獎賞送到各 MBON 的量
    return dict(punish_to_approach=float(dp[v > 0].sum() / dp.sum()), reward_to_avoid=float(dr[v < 0].sum() / dr.sum()))


out = {"note": "W_dan_mbon（每顆 DAN 的列正規化後）：單位懲罰（PPL1）與單位獎賞（PAM）送到各 MBON 的量，分子是落在趨近型（+1）／迴避型（−1）MBON 的總和，分母是全部。"
               "原始接線裡兩個比例接近 1，因為作者的標記本來就是從同一個矩陣數出來的。",
       "n_mbon": int(mb.n_mbon), "n_approach": int((v > 0).sum()), "n_avoid": int((v < 0).sum()),
       "n_punish_dan": int(pm.sum()), "n_reward_dan": int((~pm).sum()),
       "original": shares(W), "permutations": {}}
for k in range(5):
    perm = np.random.default_rng(1000 + k).permutation(mb.n_mbon)   # 與 bj_extra.py 的 perm_dan 相同
    out["permutations"][str(k)] = shares(W[:, perm])
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
