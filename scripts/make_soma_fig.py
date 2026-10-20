"""PART 1 第 2 節的細胞體位置圖：本課用到的四群神經元（PN、KC、MBON、DAN）的細胞體在腦裡的位置，
底圖是 MaleCNS 全部有座標的細胞體（果蠅的細胞體都在腦表面，點一多腦的輪廓就出來）。
只畫細胞體，不畫神經元的形狀：本機只有作者下載的神經元表（有細胞體座標）與突觸矩陣，沒有骨架。
KC 分兩種：作者抽中的 1,200 顆（抽法逐行照 extract.py）與沒抽中的。
需要作者 repo（~/claude_bscai/fly_play_game/blackjack/repo）與它下載好的 data/malecns/。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （寫 assets/p1-soma-front.png、assets/p1-soma-top.png、out/blackjack/soma_fig.json）

座標軸（用已知方位的細胞群算出來，數字存進 json 的 axis_check）：
  x 往果蠅的左側增加（somaSide L 的平均 x 大於 R）；y 往腹側增加（KC 細胞體在背側、GNG 在腹側）；
  z 往後側增加（觸角葉投射神經元在前、KC 與 T4/T5 在後）。
  A 前視：站在果蠅正前方看，背側朝上，果蠅的左邊在圖的右邊（x 照原值、y 反轉）。
  B 上視：從背側往下看，前側朝上，果蠅的左邊在圖的左邊（x 反轉、z 反轉）。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from flybrain.mb.fetch import load

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(D, "assets")
OUT = os.path.join(D, "out/blackjack/soma_fig.json")
SPAN = 46000                 # 兩個面板縱向都畫 46,000 個座標單位（腦的高度約 40,000、前後厚度約 35,000）
BRAIN_Z_MAX = 50000          # z 的直方圖在 45,000–60,000 之間是空的（腦與腹神經索之間的頸部）
KENYON, SEED = 1200, 20260913  # extract.py 的預設

M, meta = load()
t = meta["type"].fillna("")
cls = meta["class"].fillna("")
where = lambda pat: meta.index[t.str.match(pat, na=False)].to_numpy()


def xyz(s):
    try:
        v = [float(x) for x in str(s).strip("[] ").split()]
        return v if len(v) == 3 else None
    except ValueError:
        return None


soma = meta["somaLocation"].map(xyz)
has = soma.notna().to_numpy()
P = np.full((len(meta), 3), np.nan)
P[has] = np.array(soma[has].tolist())

# 四群，KC 的抽法逐行照 extract.py（排名用 stable sort，等距取 1,200）
PN = meta.index[cls == "ALPN"].to_numpy()
KC_all = where(r"^KC")
MBON = where(r"^MBON")
PAM, PPL1 = where(r"^PAM"), where(r"^PPL1")
pn_in = np.asarray(M[PN][:, KC_all].sum(axis=0)).ravel()
mbon_out = np.asarray(M[KC_all][:, MBON].sum(axis=1)).ravel()
live = (pn_in > 0) & (mbon_out > 0)
KC_live = KC_all[live]
order = np.argsort(-(pn_in[live] + mbon_out[live]), kind="stable")
KC = KC_live[np.sort(order[np.linspace(0, len(order) - 1, KENYON).astype(int)])]
# 證明抽到的和作者的檔案是同一批：邊數要等於 PART 1 第 2 節的 7,182 與 18,183
edges_pn_kc = int(M[PN][:, KC].nnz)
edges_kc_mbon = int(M[KC][:, MBON].nnz)
assert (edges_pn_kc, edges_kc_mbon) == (7182, 18183), (edges_pn_kc, edges_kc_mbon)

brain = has & (P[:, 2] < BRAIN_Z_MAX)
groups = [  # (名字, index, 顏色, 點大小, 圖例)
    ("KC_other", np.setdiff1d(KC_all, KC), "#b9c3cf", 3, "KC not sampled"),
    ("KC", KC, "#4b5563", 4, "KC sampled"),
    ("PN", PN, "#2563eb", 6, "PN"),
    ("PAM", PAM, "#16a34a", 7, "DAN: PAM"),
    ("MBON", MBON, "#d97706", 12, "MBON"),
    ("PPL1", PPL1, "#dc2626", 16, "DAN: PPL1"),
]
counts = {}
for name, idx, *_ in groups:
    m = has[idx]
    counts[name] = {"cells": int(len(idx)), "with_soma": int(m.sum()), "without_soma": int((~m).sum())}

side = meta["somaSide"].fillna("")
mean = lambda idx: P[idx][has[idx]].mean(axis=0).round(0).tolist()
axis_check = {
    "somaSide_L_mean_xyz": mean(meta.index[side == "L"].to_numpy()),
    "somaSide_R_mean_xyz": mean(meta.index[side == "R"].to_numpy()),
    "KC_mean_xyz": mean(KC_all), "ALPN_mean_xyz": mean(PN),
    "GNG_mean_xyz": mean(where(r"^SEZ|^GNG")), "T4T5_mean_xyz": mean(where(r"^T4|^T5")),
}


def panel(fname, ix, iy, flipx, flipy, label):
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    B = P[brain]
    sx = -1 if flipx else 1
    sy = -1 if flipy else 1
    ax.scatter(sx * B[:, ix], sy * B[:, iy], s=0.25, c="#e3e7ec", lw=0, rasterized=True)
    for name, idx, col, sz, leg in groups:
        Q = P[idx][has[idx]]
        ax.scatter(sx * Q[:, ix], sy * Q[:, iy], s=sz, c=col, lw=0, label=f"{leg} ({len(Q):,})")
    # 兩個面板用同樣的畫幅（同一個 x 範圍、同樣高的 y 範圍），放在網頁上才會一樣高、圖說對得齊
    xs = sx * B[:, ix]; ys = sy * B[:, iy]
    ax.set_xlim(xs.min() - 1500, xs.max() + 1500)
    yc = (ys.min() + ys.max()) / 2
    ax.set_ylim(yc - SPAN / 2, yc + SPAN / 2)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(label, fontsize=11, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=9, markerscale=2.2, frameon=False)
    fig.savefig(os.path.join(A, fname), dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("寫出", fname)


panel("p1-soma-front.png", 0, 1, False, True, "A  front view (viewer in front of the fly, dorsal up; fly's left on the right)")
panel("p1-soma-top.png", 0, 2, True, True, "B  top view (viewer above the fly, anterior up; fly's left on the left)")

res = {"brain_somas_drawn": int(brain.sum()), "all_somas_with_coords": int(has.sum()),
       "brain_z_max": BRAIN_Z_MAX, "kc_live": int(len(KC_live)), "kc_sampled": int(len(KC)),
       "edges_pn_kc": edges_pn_kc, "edges_kc_mbon": edges_kc_mbon,
       "counts": counts, "axis_check": axis_check}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
