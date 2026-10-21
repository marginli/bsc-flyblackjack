"""APL（蕈狀體裡負責壓抑 KC 的抑制神經元）在 MaleCNS 裡有幾顆、和 KC 連得多密：作者沒收它，用「只留最高的 6%」代替。
PART 1 第 3 節「APL 是什麼、規則和它差在哪」引用。需要作者 repo 與它下載的 data/malecns。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/apl_counts.json）"""
import json
import os

import numpy as np
from flybrain.mb.fetch import load

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out/blackjack/apl_counts.json")
M, meta = load()
M = M.tocsr()
t = meta["type"].fillna("")
apl = meta.index[t.str.match(r"^APL")].to_numpy()
kc = meta.index[t.str.match(r"^KC")].to_numpy()
kc2apl, apl2kc = M[kc][:, apl], M[apl][:, kc]
res = {
    "apl_cells": int(len(apl)),
    "apl_soma_sides": sorted(meta.loc[apl, "somaSide"].fillna("").tolist()),
    "kc_all": int(len(kc)),
    "kc_to_apl_synapses": int(kc2apl.sum()),
    "kc_to_apl_kcs": int((np.asarray(kc2apl.sum(axis=1)).ravel() > 0).sum()),
    "apl_to_kc_synapses": int(apl2kc.sum()),
    "apl_to_kc_kcs": int((np.asarray(apl2kc.sum(axis=0)).ravel() > 0).sum()),
}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
