#!/usr/bin/env python3
"""PART 1 第 3 節附註「連結權重的精確定義」的數字來源：直接讀作者切好的 data/mb_circuit.npz。

   用作者 model.py 的 _dense 與 _normalise 重做一次，存 out/weight_def.json：
   每一層的大小、突觸數範圍、正規化後每欄加總是不是 1、一個實例。
   用法：python3 scripts/weight_def_probe.py
"""
import json, sys
from pathlib import Path
import numpy as np

R = Path.home() / "claude_bscai/fly_play_game/blackjack/repo"
OUT = Path(__file__).resolve().parent.parent / "out/weight_def.json"
sys.path.insert(0, str(R))
from flybrain.mb.model import _dense, _normalise, MushroomBody  # noqa: E402

z = np.load(R / "data/mb_circuit.npz")
cells = json.loads((R / "data/mb_cells.json").read_text())
res = {"_note": "權重定義的實測（作者 flybrain/mb/model.py 的 _dense、_normalise、present）", "layers": {}}
for name in ["pn_kc", "kc_mbon", "dan_mbon", "mbon_mbon"]:
    n = _dense(z, name)
    w = _normalise(n)
    col = n.sum(axis=0)
    res["layers"][name] = {
        "shape": list(n.shape), "edges": int((n > 0).sum()),
        "synapses_min": int(n[n > 0].min()), "synapses_max": int(n.max()),
        "is_integer": bool((n == np.round(n)).all()), "negative": int((n < 0).sum()),
        "post_total_min": int(col.min()), "post_total_max": int(col.max()),
        "post_with_zero_input": int((col == 0).sum()),
        "colsum_max_dev_from_1": float(np.abs(w.sum(axis=0) - 1).max()),
    }
mm = _dense(z, "mbon_mbon")
auto = np.flatnonzero(np.diag(mm))
res["layers"]["mbon_mbon"]["autapses"] = [
    {"mbon": cells["types"]["mbon"][i], "synapses": int(mm[i, i]), "col_total": int(mm[:, i].sum()),
     "weight": round(float(mm[i, i] / mm[:, i].sum()), 4)} for i in auto]

# 實例：KC→MBON 那層裡，收到 KC 突觸總數最多的那顆 MBON，和連到它最強的那條
km = _dense(z, "kc_mbon")
j = int(km.sum(axis=0).argmax())
i = int(km[:, j].argmax())
res["example_kc_mbon"] = {"mbon": cells["types"]["mbon"][j], "kc_index": i,
                          "synapses": int(km[i, j]), "mbon_total_from_kc": int(km[:, j].sum()),
                          "n_kc_inputs": int((km[:, j] > 0).sum()),
                          "weight": round(float(km[i, j] / km[:, j].sum()), 5)}
# 作者模型裡實際用的矩陣和這裡重做的一樣
mb = MushroomBody(path=str(R / "data/mb_circuit.npz"))
res["matches_model"] = bool(np.allclose(mb.W_kc_mbon, _normalise(km)) and
                            np.allclose(mb.W_pn_kc, _normalise(_dense(z, "pn_kc"))))
res["lateral"] = mb.lateral
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(res, ensure_ascii=False, indent=1))
