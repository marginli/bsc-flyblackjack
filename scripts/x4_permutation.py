"""PART 4 X4 的顯著性：作者的 56／41 標記若和傳導物質毫無關係，隨機把標記重新分給 97 顆 MBON（保留 56 顆 +1、41 顆 −1），
一致顆數 ≥ 實測 62 顆的機率多大。讀 out/blackjack/bj_extra.json 的 X4_mbon_valence.cells，重排 100,000 次（亂數種子 0）。
用法：python3 scripts/x4_permutation.py   （輸出 out/blackjack/x4_permutation.json）"""
import json
import os

import numpy as np

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cells = json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))["X4_mbon_valence"]["cells"]
rule = np.array([c["nt_rule"] for c in cells])
lab = np.array([c["author"] for c in cells])
obs = int((rule == lab).sum())
rng = np.random.default_rng(0)
N = 100000
null = np.array([(rule == rng.permutation(lab)).sum() for _ in range(N)])
res = {"n_mbon": len(cells), "observed_agree": obs, "permutations": N, "null_mean": float(null.mean()),
       "null_sd": float(null.std()), "p_ge_observed": float((null >= obs).mean())}
json.dump(res, open(os.path.join(D, "out/blackjack/x4_permutation.json"), "w"), indent=1)
print(res)
