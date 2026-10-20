"""PART 1 第 4、5 節的補充數字（不在下載包裡，只給課程頁用）：
(1) 97 顆 MBON 收到哪幾群多巴胺：兩群都接、只接 PPL1、只接 PAM、都沒接的顆數，與只接 PAM 那幾顆的標記；
(2) 種子 0 的 30,000 手裡實際出現過幾種局面（點數、軟硬、明牌、是不是前兩張），分第一個決定與之後的決定；
(3) 照 README 文字描述的打法（只在硬 10、硬 11 要牌，其餘停牌）填 260 格，一致率是多少；
(5) 相鄰點數、換動作時亮的 KC 共用幾顆；(6) 扣掉硬 21、軟 21 兩列後的一致率；
(4) 一個種子最後 2,000 手的勝率本身有多少抽樣誤差：完整模型種子 0 最後 2,000 手每手淨輸贏的標準差，與 1.96 × 標準差 ÷ √2000。
種子 0 的逐手紀錄取 fly_play_game/demo/rec/bj_fly.json（與 BJ2 種子 0 逐塊核對過）。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/part1_extras.json）"""
import json
import os

import numpy as np
from flybrain.mb import blackjack as bj

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/part1_extras.json")
REC = os.path.expanduser("~/claude_bscai/fly_play_game/demo/rec/bj_fly.json")

mb = bj.FlyPlayer(seed=0).mb
W, pun = np.asarray(mb.W_dan_mbon), mb.punish_mask
p, r = (W[pun] > 0).any(axis=0), (W[~pun] > 0).any(axis=0)
res = {"mbon_dan": {"ppl1": int(p.sum()), "pam": int(r.sum()), "both": int((p & r).sum()), "ppl1_only": int((p & ~r).sum()),
                    "pam_only": int((r & ~p).sum()), "neither": int((~p & ~r).sum()),
                    "pam_only_valence": [int(v) for v in mb.valence[r & ~p]]}}

rec = json.load(open(REC))
S = {(d["pt"], d["soft"], d["up"], d["first"]) for h in rec["hand"] for d in h["dec"]}
res["situations_seen"] = {"total": len(S), "first": sum(s[3] for s in S), "later": sum(not s[3] for s in S)}

m = sum((bj.HIT if (not s and t in (10, 11)) else bj.STAND) == bj.basic_strategy(t, s, u, True) for (t, s, u) in bj.chart_cells())
res["readme_policy_agreement"] = {"cells": int(m), "share": m / 260}

nets = np.array([h["net"] for h in rec["hand"][-2000:]])
sd = float(nets.std(ddof=1))
res["last2000_seed0"] = {"mean": float(nets.mean()), "sd": sd, "ci95_half": 1.96 * sd / np.sqrt(2000)}
# (5) 相鄰點數聞起來多像：同明牌、同動作（要牌）、第一個決定，硬 14／15／16 各點亮的 72 顆 KC 共用幾顆；對照換動作
fly = bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0)
kc = lambda pt, soft, up, first, a: set(np.flatnonzero(fly.mb.present(None, learn=False, drive=fly.sit.encode(pt, soft, up, first, a))["kc"] > 0))
k14, k15, k16 = (kc(t, False, 8, True, bj.HIT) for t in (14, 15, 16))
res["kc_overlap"] = {"hard14_vs_15_hit_up8": len(k14 & k15), "hard15_vs_16_hit_up8": len(k15 & k16),
                     "hard14_vs_16_hit_up8": len(k14 & k16), "hard15_hit_vs_stand_up8": len(k15 & kc(15, False, 8, True, bj.STAND))}
# (6) 扣掉打牌時從不出現的 20 格（硬 21、軟 21 的「前兩張」）後的一致率：未訓練與種子 0 學完
cells = bj.chart_cells()
keep = [i for i, (t, s, u) in enumerate(cells) if t != 21]
bs = [bj.basic_strategy(t, s, u, True) for (t, s, u) in cells]
untr = [int(fly.greedy(t, s, u, True, [bj.HIT, bj.STAND, bj.DOUBLE])) for (t, s, u) in cells]
seed0 = {sn["h"]: sn["cells"] for sn in rec["snaps"]}[30000]
agree = lambda tab, idx: sum(tab[i] == bs[i] for i in idx)
res["agreement_without_21_rows"] = {"cells": len(keep),
                                    "untrained": agree(untr, keep), "untrained_share": agree(untr, keep) / len(keep),
                                    "seed0": agree(seed0, keep), "seed0_share": agree(seed0, keep) / len(keep),
                                    "untrained_in_21_rows": agree(untr, range(260)) - agree(untr, keep),
                                    "seed0_in_21_rows": agree(seed0, range(260)) - agree(seed0, keep)}
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
