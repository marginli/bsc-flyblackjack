#!/usr/bin/env python3
"""PART 1 圖 1 圖說「MBON 為什麼散開」的數字來源：MBON 細胞體的前後分布與樹突所在的蕈狀體分區。

   讀作者下載的 MaleCNS 神經元表（data/malecns/mcns_all_neuron_meta.csv），
   instance 欄括號裡是樹突所在的蕈狀體分區（例如 MBON01(y5B'2a)_R）。
   前後用 somaLocation 的 z（往後增加，軸向見 make_soma_fig.py）：MBON 的 z 中間有一段最大的空檔，
   以空檔切成前、後兩群。存 out/blackjack/mbon_soma.json。
   用法：python3 scripts/mbon_soma_probe.py
"""
import json, re
from pathlib import Path
import numpy as np
import pandas as pd

R = Path.home() / "claude_bscai/fly_play_game/blackjack/repo"
OUT = Path(__file__).resolve().parent.parent / "out/blackjack/mbon_soma.json"
m = pd.read_csv(R / "data/malecns/mcns_all_neuron_meta.csv", low_memory=False)
t = m["type"].fillna("")


def z_of(s):
    return float(str(s).strip("[] ").split()[2]) if isinstance(s, str) else np.nan


med = {k: round(float(np.nanmedian([z_of(s) for s in m[t.str.match(p)].somaLocation])))
       for k, p in [("MBON", "^MBON"), ("KC", "^KC"), ("PAM", "^PAM"), ("PPL1", "^PPL1")]}
d = m[t.str.match("^MBON")].copy()
d["z"] = [z_of(s) for s in d.somaLocation]
d["comp"] = [re.search(r"\((.*)\)", i).group(1) for i in d.instance]
z = np.sort(d.z.dropna().to_numpy())
k = int(np.diff(z).argmax())
lo, hi = z[k], z[k + 1]
d["grp"] = np.where(d.z.isna(), "no_soma", np.where(d.z <= lo, "anterior", "posterior"))
res = {"_note": "MBON 細胞體前後分布；comp＝instance 括號裡的蕈狀體分區（樹突所在）。z 往後增加。",
       "median_z": med, "gap": [int(lo), int(hi)], "n_mbon": len(d),
       "counts": {g: int(n) for g, n in d.grp.value_counts().items()}}
for g in ["anterior", "posterior", "no_soma"]:
    x = d[d.grp == g]
    res[g] = sorted({f"{ty}({c})" for ty, c in zip(x.type, x.comp)})
res["calyx_mbon"] = {f"{r.type}_{r.somaSide}": r.grp for r in d[d.comp == "calyx"].itertuples()}
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(res, ensure_ascii=False, indent=1))
