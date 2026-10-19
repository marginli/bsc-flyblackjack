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


def blackjack():
    """21 點學習曲線（PART 3 圖 2）。"""
    d = J("blackjack/bj2_blackjack_30000.json")
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


def seeds20():
    """X1：三個條件各 20 個種子，最後 2,000 手的平均每手輸贏（PART 4 圖 1）。"""
    x = J("blackjack/bj_extra.json")["X1_seeds20"]
    ref = J("blackjack/bj2_blackjack_30000.json")["reference"]
    rows = [("connectome + dopamine", GREEN), ("dopamine cut + exploration decay", RED), ("untrained greedy", SOFT)]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    rng = np.random.default_rng(0)
    for i, (k, c) in enumerate(rows):
        v = [r["last_block"] for r in x[k]["runs"]]
        ax.scatter(v, i + rng.uniform(-.18, .18, len(v)), s=22, color=c, alpha=.55, zorder=2, linewidths=0)
        s = x[k]["last"]
        ax.plot(s["ci95"], [i, i], color=INK, lw=3.2, zorder=3)
        ax.plot(s["mean"], i, "o", color=INK, ms=6.5, zorder=4)
        ax.text(s["mean"], i - .36, f"{s['mean']:.3f}", ha="center", fontsize=9, color=INK)
        meta[f"X1_{k}_mean"] = s["mean"]
    for k, lab in [("always stand", "always stand"), ("random", "random")]:
        ax.axvline(ref[k], color=FAINT, lw=1, ls=(0, (2, 3)))
        ax.text(ref[k], 2.62, f"{lab} {ref[k]:.3f}", ha="center", fontsize=8.5, color=SOFT)
    ax.set_yticks(range(3), ["connectome + dopamine", "dopamine cut", "untrained"])
    ax.set_xlabel("net payoff per hand, last 2,000 hands (each dot = one seed; bar = 95% CI of the 20-seed mean)")
    ax.set_xlim(-0.56, -0.03); ax.set_ylim(-.6, 2.85); ax.invert_yaxis()
    save(fig, "p4-bj-seeds.png")


def layers():
    """X2：打亂哪一層接線，21 點才學不會（PART 4 圖 2）。"""
    x = J("blackjack/bj_extra.json")
    ref = J("blackjack/bj2_blackjack_30000.json")["reference"]
    full = x["X1_seeds20"]["connectome + dopamine"]["last"]
    unt = x["X1_seeds20"]["untrained greedy"]["last"]
    kc = x["X2_layers"]["kc_mbon_shuffled"]["last"]
    perms = x["X2_layers"]["dan_mbon_shuffled"]["per_permutation"]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for i, (lab, s, c) in enumerate([("intact (20 seeds)", full, GREEN), ("KC->MBON shuffled (5 seeds)", kc, PURPLE)]):
        ax.plot(s["ci95"], [i, i], color=c, lw=4); ax.plot(s["mean"], i, "o", color=INK, ms=6)
        ax.text(s["ci95"][1] + .012, i, f"{s['mean']:.3f}", va="center", fontsize=9)
    pm = [p["last"]["mean"] for p in perms]
    ax.scatter(pm, [2] * len(pm), color=RED, s=30, alpha=.8, zorder=3)
    mm = x["X2_layers"]["dan_mbon_shuffled"]["mean_of_means"]
    ax.plot(mm, 2, "|", color=INK, ms=16, mew=2); ax.text(max(pm) + .012, 2, f"{mm:.3f}", va="center", fontsize=9)
    ax.plot(unt["ci95"], [3, 3], color=SOFT, lw=4); ax.plot(unt["mean"], 3, "o", color=INK, ms=6)
    ax.text(unt["ci95"][1] + .012, 3, f"{unt['mean']:.3f}", va="center", fontsize=9)
    for k, lab in [("always stand", "always stand"), ("random", "random")]:
        ax.axvline(ref[k], color=FAINT, lw=1, ls=(0, (2, 3)))
        ax.text(ref[k], -.55, f"{lab} {ref[k]:.3f}", ha="center", fontsize=8.5, color=SOFT)
    ax.set_yticks(range(4), ["intact (20 seeds)", "KC->MBON shuffled\n(5 seeds)", "DAN->MBON shuffled\n(5 permutations x 3 seeds)", "untrained (20 seeds)"])
    ax.set_xlabel("net payoff per hand, last 2,000 hands (bar = 95% CI; red dot = one permutation's 3-seed mean)")
    ax.set_xlim(-0.70, -0.05); ax.set_ylim(-.8, 3.6); ax.invert_yaxis()
    meta["X2_dan_perm_means"] = pm
    save(fig, "p4-bj-layers.png")


for f in (blackjack, seeds20, layers):
    f()
json.dump(meta, open(os.path.join(O, "figures.json"), "w"), indent=1)
