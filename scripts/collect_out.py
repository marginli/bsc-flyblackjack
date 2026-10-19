"""把 fly-blackjack 重現實跑的產出收進 out/，頁面上每個數字都要對得回這裡（scripts/number_audit.py 會掃）。

來源是本機的實跑資料夾 ~/claude_bscai/fly_play_game/blackjack/（run_all.sh 跑出來的 logs/ 與 results/）。
只收數字（JSON、log 文字）與作者 commit 進 repo 的紀錄檔；fly-blackjack 是 MIT 授權，README 照收，作者宣稱的數字以它為準。
PART 5 的逐手資料另由 scripts/build_demo_data.py 產生，可攜測試由 scripts/record_porttest.py 產生；重收時這幾個檔保留。
用法：~/anaconda3/bin/python scripts/collect_out.py（需要 numpy）
"""
import glob
import json
import os
import shutil
import subprocess

import numpy as np

SRC = os.path.expanduser("~/claude_bscai/fly_play_game")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

PLAN = [
    ("blackjack/results", "blackjack", ("*.json",)),
    ("blackjack/logs", "blackjack/logs", ("*.log", "*.txt")),
    ("blackjack", "blackjack", ("env.txt", "runall_test.out")),
    ("blackjack/repo", "upstream", ("README.md",)),          # MIT 授權，作者宣稱的數字以這份為準
]


def main():
    keep = {}
    for f in ("porttest.json", "demo_data.json", "bj_demo_summary.json", "figures.json"):   # 另幾支程式產生的檔案，收資料時保留
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            keep[f] = open(p, "rb").read()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    n = 0
    for src, dst, pats in PLAN:
        for pat in pats:
            for f in sorted(glob.glob(os.path.join(SRC, src, pat))):
                rel = os.path.relpath(f, os.path.join(SRC, src))
                if dst == "upstream":
                    rel = "blackjack_README.md"
                t = os.path.join(OUT, dst, rel)
                os.makedirs(os.path.dirname(t), exist_ok=True)
                shutil.copy2(f, t)
                n += 1
    # 作者 commit 進 repo 的蕈狀體 manifest，以及 blackjack.py 檔尾的 RESULT 註解
    man = subprocess.run(["git", "-C", os.path.join(SRC, "blackjack/repo"), "show", "HEAD:data/mb_manifest.json"],
                         capture_output=True, text=True, check=True).stdout
    open(os.path.join(OUT, "upstream/blackjack_mb_manifest_committed.json"), "w").write(man)
    src = open(os.path.join(SRC, "blackjack/repo/flybrain/mb/blackjack.py"), encoding="utf-8").read().splitlines()
    i = next(k for k, t in enumerate(src) if t.startswith("# RESULT"))
    open(os.path.join(OUT, "upstream/blackjack_py_RESULT_comment.txt"), "w").write(
        f"# flybrain/mb/blackjack.py lines {i + 1}-{i + 24} @ 004b2e3\n" + "\n".join(src[i:i + 24]) + "\n")
    # BJ1：README 的連結數對不上 1,200 顆 KC 的電路；量一下用全部 KC 切出的電路（加做檢查 X3 存下的）有幾條
    cnt = {}
    for tag, f in [("kc1200_committed_circuit", "blackjack/repo/data/mb_circuit.npz"),
                   ("all_live_kc_circuit", "blackjack/results/circuits/mb_all_live_kc.npz")]:
        z = np.load(os.path.join(SRC, f))
        cnt[tag] = {k: int(z[k + "_val"].size) for k in ("pn_kc", "kc_mbon", "dan_mbon", "mbon_mbon")}
    json.dump(cnt, open(os.path.join(OUT, "blackjack/bj1_edge_counts.json"), "w"), indent=1)
    n += 3
    for f, b in keep.items():
        open(os.path.join(OUT, f), "wb").write(b)
    meta = {"source": "~/claude_bscai/fly_play_game/blackjack", "files": n,
            "blackjack_commit": "004b2e3e9ccb742f83c5bdc2717c97f5a64b420f"}
    json.dump(meta, open(os.path.join(OUT, "_manifest.json"), "w"), indent=1)
    print(f"收進 out/：{n} 個檔案（保留 {sorted(keep)}）")


main()
