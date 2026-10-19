"""從 out/（本課實跑的結果）產生下載包的驗收表 pack/expected.json，check.py 拿它逐項比對。
預期值一律讀實跑產出，不手打。用法：python3 scripts/make_expected.py"""
import json
import os

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(D, "out")
J = lambda p: json.load(open(os.path.join(O, p)))


def blackjack():
    c = []
    h = open(os.path.join(O, "blackjack/logs/bj1_md5.txt")).read().split()[0]
    c.append(dict(step="BJ1", what=f"切出蕈狀體跑兩次，md5 相同且 = {h}", file="logs/bj1_md5.txt", kind="md5_twice", value=h))
    b2 = J("blackjack/bj2_blackjack_30000.json")["conditions"]
    for k, v in b2.items():
        c.append(dict(step="BJ2", what=f"{k}：最後 2,000 手平均每手 {v['mean_last']:.4f}", file="results/bj2_blackjack_30000.json",
                      keys=["conditions", k, "mean_last"], kind="exact", value=v["mean_last"]))
    b3 = J("blackjack/bj3_author_brain.json")
    c.append(dict(step="BJ3", what=f"作者的大腦檔載入 Python 重新評分，一致率 {b3['python_agreement']:.4f}", file="results/bj3_author_brain.json",
                  keys=["python_agreement"], kind="exact", value=b3["python_agreement"]))
    c.append(dict(step="BJ3", what="作者網頁版電路的連結位置與本機切出的相同", file="results/bj3_author_brain.json",
                  keys=["same_edges"], kind="exact", value=True))
    x = J("blackjack/bj_extra.json")
    for k, v in x["X1_seeds20"].items():
        c.append(dict(step="X1", what=f"{k}：20 個種子最後 2,000 手平均 {v['last']['mean']:.4f}", file="results/bj_extra.json",
                      keys=["X1_seeds20", k, "last", "mean"], kind="exact", value=v["last"]["mean"]))
    c.append(dict(step="X2", what=f"KC→MBON 打亂 5 個種子平均 {x['X2_layers']['kc_mbon_shuffled']['last']['mean']:.4f}", file="results/bj_extra.json",
                  keys=["X2_layers", "kc_mbon_shuffled", "last", "mean"], kind="exact", value=x["X2_layers"]["kc_mbon_shuffled"]["last"]["mean"]))
    c.append(dict(step="X2", what=f"DAN→MBON 打亂 5 種重排平均 {x['X2_layers']['dan_mbon_shuffled']['mean_of_means']:.4f}", file="results/bj_extra.json",
                  keys=["X2_layers", "dan_mbon_shuffled", "mean_of_means"], kind="exact", value=x["X2_layers"]["dan_mbon_shuffled"]["mean_of_means"]))
    for k, v in x["X3_kc_subsets"]["variants"].items():
        c.append(dict(step="X3", what=f"KC 選法 {k}（{v['n_kc']} 顆）3 個種子平均 {v['last']['mean']:.4f}", file="results/bj_extra.json",
                      keys=["X3_kc_subsets", "variants", k, "last", "mean"], kind="exact", value=v["last"]["mean"]))
    c.append(dict(step="X4", what=f"MBON 標記與文獻規則一致 {x['X4_mbon_valence']['agree']}/{x['X4_mbon_valence']['judged']}",
                  file="results/bj_extra.json", keys=["X4_mbon_valence", "agree"], kind="exact", value=x["X4_mbon_valence"]["agree"]))
    return c


exp = {"blackjack": blackjack()}
json.dump(exp, open(os.path.join(D, "pack/expected.json"), "w"), indent=1, ensure_ascii=False)
print({k: len(v) for k, v in exp.items()})
