"""從 out/（本課實跑的結果）產生下載包的驗收表 pack/expected.json，check.py 拿它逐項比對。
預期值一律讀實跑產出，不手打；作者宣稱的值讀作者附的結果檔。用法：python3 scripts/make_expected.py"""
import json
import os
import re

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(D, "out")
J = lambda p: json.load(open(os.path.join(O, p)))


def blackjack():
    c = []
    log = open(os.path.join(O, "blackjack/logs/bj1_train.log")).read()
    rows = [l for l in log.splitlines() if re.match(r"^(connectome|SAME|untrained|uniform)", l)]
    c.append(dict(step="BJ1", what="Dino 四列結果與 README 相同（45／0／0／0 完成）", file="logs/bj1_train.log", kind="contains", value=rows))
    h = open(os.path.join(O, "blackjack/logs/bj2_md5.txt")).read().split()[0]
    c.append(dict(step="BJ2", what=f"切出蕈狀體跑兩次，md5 相同且 = {h}", file="logs/bj2_md5.txt", kind="md5_twice", value=h))
    r = J("blackjack/mb_results.json")["acquisition"]
    for k in ("connectome + plasticity", "KC->MBON shuffled", "dopamine disconnected"):
        m = round(sum(r[k]) / len(r[k]), 6)
        c.append(dict(step="BJ3", what=f"{k}：12 種子平均學習指數 {m:.3f}", file="results/mb_results.json",
                      keys=["acquisition", k], mean=True, kind="exact", value=m))
    f4 = J("blackjack/bj4_forage.json")
    for g in ("author_policy", "retrained"):
        for k in ("learning", "dopamine cut"):
            v = f4[g][k]["shocks"]
            c.append(dict(step="BJ4", what=f"{g}、{k}：每 90 秒電擊 {v}", file="results/bj4_forage.json", keys=[g, k, "shocks"], kind="exact", value=v))
    s45 = J("blackjack/bj4b_forage_s45_eval.json")
    for k in ("learning", "dopamine cut"):
        c.append(dict(step="BJ4b", what=f"seconds=45 重新訓練、{k}：電擊 {s45[k]['shocks']}", file="results/bj4b_forage_s45_eval.json",
                      keys=[k, "shocks"], kind="exact", value=s45[k]["shocks"]))
    c.append(dict(step="BJ4b", what=f"seconds=45 重新訓練的驗證分數 = 作者策略檔記錄的 {s45['validation']:.1f}",
                  file="results/bj4b_forage_s45_eval.json", keys=["validation"], kind="exact", value=s45["validation"]))
    b5 = J("blackjack/bj5_blackjack_30000.json")["conditions"]
    for k, v in b5.items():
        c.append(dict(step="BJ5", what=f"{k}：最後 2,000 手平均每手 {v['mean_last']:.4f}", file="results/bj5_blackjack_30000.json",
                      keys=["conditions", k, "mean_last"], kind="exact", value=v["mean_last"]))
    x = J("blackjack/bj_extra.json")
    c.append(dict(step="X1", what=f"50 種子學習指數 {x['X1_50_seeds']['none']['mean']:.3f}", file="results/bj_extra.json",
                  keys=["X1_50_seeds", "none", "mean"], kind="exact", value=x["X1_50_seeds"]["none"]["mean"]))
    c.append(dict(step="X2", what=f"DAN→MBON 打亂 10 組平均 {x['X2_dan_mbon_shuffled']['mean_of_means']:.3f}", file="results/bj_extra.json",
                  keys=["X2_dan_mbon_shuffled", "mean_of_means"], kind="exact", value=x["X2_dan_mbon_shuffled"]["mean_of_means"]))
    c.append(dict(step="X4", what=f"MBON 標記與文獻規則一致 {x['X4_mbon_valence']['agree']}/{x['X4_mbon_valence']['judged']}",
                  file="results/bj_extra.json", keys=["X4_mbon_valence", "agree"], kind="exact", value=x["X4_mbon_valence"]["agree"]))
    return c


exp = {"blackjack": blackjack()}
json.dump(exp, open(os.path.join(D, "pack/expected.json"), "w"), indent=1, ensure_ascii=False)
print({k: len(v) for k, v in exp.items()})
