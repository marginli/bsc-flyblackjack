"""產生本專題的真實資料圖，數字全部讀 out/（由 collect_out.py 從實跑產出收來）。
圖內一律英文，說明寫在 HTML 的 figcaption。用法：~/anaconda3/bin/python scripts/make_figures.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(D, "out")
A = os.path.join(D, "assets")
J = lambda p: json.load(open(os.path.join(O, p)))
INK, SOFT, FAINT = "#1b2733", "#5a6b7b", "#c9d1da"
BLUE, AMBER, GREEN, RED, PURPLE = "#2563eb", "#d97706", "#16a34a", "#dc2626", "#9333ea"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": SOFT, "axes.labelcolor": INK, "xtick.color": SOFT,
                     "ytick.color": SOFT, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 160, "savefig.bbox": "tight"})
meta = {}


def save(fig, name):
    fig.savefig(os.path.join(A, name))
    plt.close(fig)
    print("寫出", name)


def forage():
    """覓食：電擊次數。作者策略／照 README 重新訓練／加 seconds=45 重新訓練。（PART 3 圖 1）"""
    a, s45 = J("blackjack/bj4_forage.json"), J("blackjack/bj4b_forage_s45_eval.json")
    conds = ["learning", "dopamine cut", "plasticity off"]
    groups = [("author's policy", a["author_policy"]), ("retrained with\nREADME command", a["retrained"]),
              ("retrained with\nseconds=45", s45)]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    w = .26
    for i, (c, col) in enumerate(zip(conds, [GREEN, RED, AMBER])):
        v = [g[c]["shocks"] for _, g in groups]
        b = ax.bar(np.arange(3) + (i - 1) * w, v, w * .92, color=col, label=c)
        ax.bar_label(b, fmt="%.2f", fontsize=8.5, color=SOFT, padding=2)
    ax.set_xticks(range(3), [g for g, _ in groups]); ax.set_ylabel("shocks per 90 s (mean of 40 seeds)")
    ax.legend(frameon=False, fontsize=9.5, ncol=3, loc="upper right"); ax.set_ylim(0, 9.5)
    save(fig, "p3-forage-shocks.png")


def blackjack():
    """21 點學習曲線（PART 3 圖 2）。"""
    d = J("blackjack/bj5_blackjack_30000.json")
    blocks = d["hands"] // len(d["conditions"]["connectome + dopamine"]["runs"][0]["blocks"])
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    style = {"connectome + dopamine": (GREEN, "-", 2.4), "dopamine cut + exploration decay": (RED, "-", 1.6),
             "no learning + exploration decay": (AMBER, "--", 1.6), "untrained greedy": (SOFT, ":", 1.6)}
    for k, (c, ls, lw) in style.items():
        m = np.mean([r["blocks"] for r in d["conditions"][k]["runs"]], 0)
        x = (np.arange(len(m)) + 1) * blocks / 1000
        ax.plot(x, m, ls, color=c, lw=lw, label=k)
    for k, lab in [("basic strategy", "basic strategy"), ("always stand", "always stand"), ("random", "random")]:
        y = d["reference"][k]
        ax.axhline(y, color=FAINT, lw=1, ls=(0, (2, 3)))
        ax.text(30.4, y, f" {lab} {y:.3f}", va="center", fontsize=8.5, color=SOFT)
    ax.set_xlabel("hands played (thousands; each point = mean of a 2,000-hand block, 3 seeds)")
    ax.set_ylabel("net payoff per hand")
    ax.set_xlim(0, 30); ax.set_ylim(-0.56, 0.03)
    ax.legend(frameon=False, fontsize=8.5, loc="center", bbox_to_anchor=(0.55, 0.47))
    save(fig, "p3-blackjack-curve.png")


def mb_shuffle():
    """打亂不同層接線對學習指數的影響（PART 4 圖 1）。"""
    x = J("blackjack/bj_extra.json")
    full, kc = x["X1_50_seeds"]["none"], x["X1_50_seeds"]["shuffled"]
    perms = x["X2_dan_mbon_shuffled"]["per_permutation"]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, (lab, s, c) in enumerate([("intact (50 seeds)", full, GREEN), ("KC->MBON shuffled (50 seeds)", kc, PURPLE)]):
        ax.plot(s["ci95"], [i, i], color=c, lw=4); ax.plot(s["mean"], i, "o", color=INK, ms=6)
        ax.text(s["ci95"][1] + .03, i, f"{s['mean']:.2f}", va="center", fontsize=9)
    pm = [p["mean"] for p in perms]
    ax.scatter(pm, [2] * len(pm), color=RED, s=26, alpha=.75, zorder=3)
    mm = x["X2_dan_mbon_shuffled"]["mean_of_means"]
    ax.plot(mm, 2, "|", color=INK, ms=16, mew=2); ax.text(max(pm) + .03, 2, f"{mm:.2f}", va="center", fontsize=9)
    ax.axvline(0, color=FAINT, lw=1)
    ax.set_yticks(range(3), ["intact (50 seeds)", "KC->MBON shuffled (50 seeds)", "DAN->MBON shuffled (10 perms x 12)"])
    ax.set_xlabel("learning index (more negative = stronger avoidance learning)")
    ax.set_xlim(-1.65, 0.12); ax.set_ylim(-.6, 2.6); ax.invert_yaxis()
    save(fig, "p4-mb-shuffle.png")


for f in (forage, blackjack, mb_shuffle):
    f()
json.dump(meta, open(os.path.join(O, "figures.json"), "w"), indent=1)
