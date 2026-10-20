"""PART 1 第 5 節輸入編碼的補充數字：五個特徵各自抽 PN，組與組會不會重疊、682 顆裡總共用到幾顆。
抽法逐行照作者 blackjack.py 的 SituationCode.__init__（同一個種子 20260914，同一個亂數呼叫順序），只是把抽到的 PN 記下來。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/encoding_pn.json）"""
import json
import os

import numpy as np
from flybrain.mb.blackjack import Situation as SituationCode

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/encoding_pn.json")
n = 682
rng = np.random.default_rng(20260914)
sets = {}
for feature, levels, ordered in [("total", 18, True), ("upcard", 10, True),
                                 ("action", 3, False), ("soft", 2, False), ("first", 2, False)]:
    width = SituationCode.WIDTH[feature]
    pool = rng.permutation(n)
    for level in range(levels):
        if ordered:
            start = int(level * width * 0.55)
            cells = pool[start:start + width]
        else:
            cells = rng.choice(n, width, replace=False)
        rng.uniform(0.7, 1.0, size=len(cells))     # 作者這裡抽活動量，照樣抽一次讓亂數序列對齊
        sets[(feature, level)] = set(int(c) for c in cells)

by_feature = {f: set().union(*[s for (g, _), s in sets.items() if g == f]) for f in ("total", "upcard", "action", "soft", "first")}
used = set().union(*by_feature.values())
feats = list(by_feature)
cross = {f"{a}&{b}": len(by_feature[a] & by_feature[b]) for i, a in enumerate(feats) for b in feats[i + 1:]}
res = {
    "pn_total": n, "pn_used": len(used), "pn_unused": n - len(used),
    "per_feature_union": {f: len(v) for f, v in by_feature.items()},
    "cross_feature_overlap": cross,
    "action_pairwise_overlap": {f"{a}&{b}": len(sets[("action", a)] & sets[("action", b)]) for a, b in ((0, 1), (0, 2), (1, 2))},
    "soft_overlap": len(sets[("soft", 0)] & sets[("soft", 1)]),
    "first_overlap": len(sets[("first", 0)] & sets[("first", 1)]),
    "total_neighbour_overlap": len(sets[("total", 0)] & sets[("total", 1)]),
    "upcard_neighbour_overlap": len(sets[("upcard", 0)] & sets[("upcard", 1)]),
}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
