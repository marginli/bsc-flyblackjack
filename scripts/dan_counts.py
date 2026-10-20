"""PART 1 第 2 節的補充數字：PAM 與 PPL1 兩群多巴胺神經元為什麼顆數差二十倍。
從 MaleCNS 的神經元表數每一型有幾顆、分左右各幾顆；再從突觸矩陣數兩群各送多少突觸到 MBON、接到幾顆 MBON。
需要作者 repo（~/claude_bscai/fly_play_game/blackjack/repo）與它下載好的 data/malecns/。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/dan_counts.json）"""
import json
import os

import numpy as np
from flybrain.mb.fetch import load

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/dan_counts.json")

M, meta = load()
t = meta["type"].fillna("")
side = meta["somaSide"].fillna("")
where = lambda pat: meta.index[t.str.match(pat, na=False)].to_numpy()
MBON = where(r"^MBON")

res = {}
for name, pat in (("PAM", r"^PAM"), ("PPL1", r"^PPL1")):
    idx = where(pat)
    types = t[idx].value_counts().sort_index()
    per_side_per_type = {k: int(v) // 2 for k, v in types.items()}   # 每型左右對稱
    sub = M[idx][:, MBON]
    to_mbon = np.asarray(sub.sum(axis=0)).ravel()
    res[name] = {
        "cells": int(len(idx)),
        "by_side": {k: int(v) for k, v in side[idx].value_counts().items()},
        "n_types": int(len(types)),
        "cells_per_type": {k: int(v) for k, v in types.items()},
        "per_side_per_type_min": min(per_side_per_type.values()),
        "per_side_per_type_max": max(per_side_per_type.values()),
        "per_side_per_type_mean": round(float(np.mean(list(per_side_per_type.values()))), 1),
        "synapses_to_mbon": int(sub.sum()),
        "synapses_to_mbon_per_cell": round(float(sub.sum()) / len(idx), 1),
        "mbons_reached": int((to_mbon > 0).sum()),
        "mbons_total": int(len(MBON)),
    }
res["ppl1_per_cell_over_pam_per_cell"] = round(res["PPL1"]["synapses_to_mbon_per_cell"] / res["PAM"]["synapses_to_mbon_per_cell"], 1)
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
