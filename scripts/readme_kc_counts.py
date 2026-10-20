"""README 的兩個連結數（22,586 條 ALPN→KC、61,210 條 KC→MBON）從哪來：不篩「路徑上的 KC」、用資料裡全部 KC 數連結。
作者 extract.py 先只留同時收到 PN、又送到 MBON 的 KC（3,811 顆），本檔改成全部 KC（type 以 KC 開頭的全部），其餘照抄 extract.py。
PART 3 第 3 節引用。需要作者 repo 與它下載的 data/malecns。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/readme_kc_counts.json）"""
import json
import os

import numpy as np
from flybrain.mb.extract import load

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out/blackjack/readme_kc_counts.json")
M, meta = load()
t, cls = meta["type"].fillna(""), meta["class"].fillna("")
PN = meta.index[cls == "ALPN"].to_numpy()
KC = meta.index[t.str.match(r"^KC", na=False)].to_numpy()
MBON = meta.index[t.str.match(r"^MBON", na=False)].to_numpy()
a, b = M[PN][:, KC], M[KC][:, MBON]
pn_in, mbon_out = np.asarray(a.sum(axis=0)).ravel(), np.asarray(b.sum(axis=1)).ravel()
out = {"note": "全部 KC、不篩路徑時的連結條數（非零的格數），對 README 的 22,586 與 61,210。",
       "n_kc_all": int(len(KC)), "pn_kc_edges": int((a != 0).sum()), "kc_mbon_edges": int((b != 0).sum()),
       "readme": {"pn_kc_edges": 22586, "kc_mbon_edges": 61210},
       "kc_pn_only": int(((pn_in > 0) & (mbon_out == 0)).sum()), "kc_mbon_only": int(((pn_in == 0) & (mbon_out > 0)).sum())}
out["matches_readme"] = out["pn_kc_edges"] == 22586 and out["kc_mbon_edges"] == 61210
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(out)
