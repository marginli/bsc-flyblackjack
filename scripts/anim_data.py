"""PART 1 第 3 節動畫的數字：完整模型（種子 0）第 1 手的第一個決定（硬 20 對莊家 8、前兩張），
三個候選動作各走一次「PN → KC → MBON → 好惡值」，逐層記下活動量。
這是訓練的第一個決定，增益全是 1，所以用作者的模型可以逐位重算；三個好惡值要等於 out/bj_demo_summary.json 錄到的
0.2432／0.1681／0.0185。
需要作者 repo（~/claude_bscai/fly_play_game/blackjack/repo，data/mb_circuit.npz 是作者附的電路檔）。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/anim_data.json）"""
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj
from flybrain.mb.model import MushroomBody

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/anim_data.json")
REC = json.load(open(os.path.join(D, "out/bj_demo_summary.json")))["conditions"]["bj_fly"]["hands"]["1"]["decisions"][0]

mb = MushroomBody()                      # 作者的預設電路檔 data/mb_circuit.npz，增益全 1
sit = bj.Situation(mb)                   # 編碼，種子照作者預設
pt, soft, up, first = REC["total"], REC["soft"], REC["upcard"], REC["first"]
ACT = {"hit": bj.HIT, "stand": bj.STAND, "double": bj.DOUBLE}

# 重做 Situation.__init__ 的抽法，把每個特徵、每個值選中的 PN 記下來（亂數順序與作者一致）
rng = np.random.default_rng(20260914)
n = mb.n_pn
pn_sets, pn_amp = {}, {}
for feature, levels, ordered in [("total", 18, True), ("upcard", 10, True),
                                 ("action", 3, False), ("soft", 2, False), ("first", 2, False)]:
    width = sit.WIDTH[feature]
    pool = rng.permutation(n)
    for level in range(levels):
        cells = pool[int(level * width * 0.55):int(level * width * 0.55) + width] if ordered else rng.choice(n, width, replace=False)
        amp = (1.3 if feature == "action" else 1.0) * rng.uniform(0.7, 1.0, size=len(cells))
        pn_sets[(feature, level)] = cells
        pn_amp[(feature, level)] = amp

def pn_vector(action):
    v = np.zeros(n)
    for key in [("total", int(np.clip(pt - 4, 0, 17))), ("upcard", up - 2), ("action", action), ("soft", int(soft)), ("first", int(first))]:
        v[pn_sets[key]] += pn_amp[key]
    return v

res = {"hand": 1, "decision": {"total": pt, "soft": soft, "upcard": up, "first": first}, "recorded_values": REC["values"],
       "n_pn": int(mb.n_pn), "n_kc": int(mb.n_kc), "n_mbon": int(mb.n_mbon), "k_winners": int(mb.k),
       "mbon_valence": mb.valence.astype(int).tolist(), "actions": {}}
for name, a in ACT.items():
    pn = pn_vector(a)
    drive_ours = mb.pn_drive(pn)
    drive_author = sit.encode(pt, soft, up, first, a)
    assert np.allclose(drive_ours, drive_author), "PN 抽法與作者對不上"
    out = mb.present(None, learn=False, drive=drive_author)
    kc, mbon = out["kc"], out["mbon"]
    kc_only = (mb.W_kc_mbon * mb.gain).T @ kc           # MBON 式子的第一項（KC 推的）
    lateral = mb.lateral * (mb.W_mbon_mbon.T @ kc_only)  # 第二項（其他 MBON 推的）
    assert np.allclose(kc_only + lateral, mbon)
    v = float(mbon @ mb.valence)
    assert round(v, 4) == REC["values"][name], (name, v, REC["values"][name])
    lit = np.flatnonzero(pn > 0)
    res["actions"][name] = {
        "valence": round(v, 4),
        "pn_lit": int(len(lit)), "pn_max": round(float(pn.max()), 3), "pn_over_1": int((pn > 1).sum()),
        "pn_lit_by_feature": {f: int(len(pn_sets[k])) for f, k in [("total", ("total", int(np.clip(pt - 4, 0, 17)))), ("upcard", ("upcard", up - 2)), ("action", ("action", a)), ("soft", ("soft", int(soft))), ("first", ("first", int(first)))]},
        "pn_values": {int(i): round(float(pn[i]), 3) for i in lit},
        "kc_drive_nonzero": int((drive_author > 0).sum()), "kc_drive_max": round(float(drive_author.max()), 4),
        "kc_lit": [int(i) for i in np.flatnonzero(kc > 0)], "kc_values": {int(i): round(float(kc[i]), 3) for i in np.flatnonzero(kc > 0)},
        "mbon": [round(float(x), 4) for x in mbon], "mbon_from_kc": [round(float(x), 4) for x in kc_only], "mbon_lateral": [round(float(x), 4) for x in lateral],
        "sum_plus": round(float(mbon[mb.valence > 0].sum()), 4), "sum_minus": round(float(mbon[mb.valence < 0].sum()), 4),
        "sum_plus_3dp": round(float(mbon[mb.valence > 0].sum()), 3), "sum_minus_3dp": round(float(mbon[mb.valence < 0].sum()), 3),
        "valence_3dp": round(v, 3), "mbon_max": round(float(mbon.max()), 4),
        "pn_dark": int((pn == 0).sum()), "kc_drive_max_3dp": round(float(drive_author.max()), 3),
        "pn_overlap": int(sum(len(pn_sets[k]) for k in [("total", int(np.clip(pt - 4, 0, 17))), ("upcard", up - 2), ("action", a), ("soft", int(soft)), ("first", int(first))]) - len(lit)),  # 被兩項資訊同時選中的顆數（五組顆數加總 − 實際亮的） "kc_drive_max_3dp": round(float(drive_author.max()), 3),
        "kc_drive_values": [round(float(x), 4) for x in drive_author],     # 第 2 步：每顆 KC 收到的量（6% 規則之前）
        # 每顆亮的 KC 推得最用力的那顆 MBON（活動 × 權重 × 增益 最大者），動畫只畫這 72 條線
        "kc_top_mbon": {int(i): int(np.argmax(mb.W_kc_mbon[i] * mb.gain[i])) for i in np.flatnonzero(kc > 0)},
    }
hit, stand = res["actions"]["hit"], res["actions"]["stand"]
res["kc_shared_hit_stand"] = len(set(hit["kc_lit"]) & set(stand["kc_lit"]))
_fixed = [("total", int(np.clip(pt - 4, 0, 17))), ("upcard", up - 2), ("soft", int(soft)), ("first", int(first))]
res["pn_fixed_sum"] = int(sum(len(pn_sets[k]) for k in _fixed))                      # 四組不換的 PN 顆數加總
res["pn_fixed_union"] = int(len(set().union(*[set(pn_sets[k].tolist()) for k in _fixed])))   # 同一顆只算一次
res["pn_action_shared_hit_stand"] = int(len(set(pn_sets[("action", bj.HIT)].tolist()) & set(pn_sets[("action", bj.STAND)].tolist())))
res["mbon_max_all"] = max(a["mbon_max"] for a in res["actions"].values())
res["mbon_max_all_3dp"] = round(res["mbon_max_all"], 3)
res["pn_max_all"] = max(a["pn_max"] for a in res["actions"].values())
res["n_mbon_plus"] = int((mb.valence > 0).sum()); res["n_mbon_minus"] = int((mb.valence < 0).sum())
res["pn_shared_hit_stand"] = len(set(hit["pn_values"]) & set(stand["pn_values"]))
json.dump(res, open(OUT, "w"), ensure_ascii=False)
brief = {k: v for k, v in res.items() if k not in ("actions", "mbon_valence")}
for name, a in res["actions"].items():
    brief[name] = {k: v for k, v in a.items() if k not in ("pn_values", "kc_lit", "kc_values", "mbon", "mbon_from_kc", "mbon_lateral")}
print(json.dumps(brief, ensure_ascii=False, indent=1))
