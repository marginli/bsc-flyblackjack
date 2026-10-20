"""PART 5 第 3 節「進步從哪來」的粗估：完整模型種子 0 從頭 2,000 手到末 2,000 手的進步，有多少能用「亂選變少」解釋。
假設：亂選那部分的成績等於三個動作亂選的參考值（bj2 輸出的 reference.random），不亂選那部分在頭 2,000 手的水準若一直不變。
探索機率逐手照作者 FlyPlayer.exploration() 的公式取平均。只用 out/ 裡的數字，不重跑。
用法：python3 scripts/part5_progress_split.py   （輸出 out/blackjack/part5_progress_split.json）"""
import json
import os

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = json.load(open(os.path.join(D, "out/blackjack/bj2_blackjack_30000.json")))
E = json.load(open(os.path.join(D, "out/blackjack/explore_schedule.json")))
run = [r for r in B["conditions"]["connectome + dopamine"]["runs"] if r["seed"] == 0][0]
rand = B["reference"]["random"]
f = lambda h: E["floor"] + (E["explore0"] - E["floor"]) * 0.5 ** (h / E["halflife"])
p1 = sum(f(h) for h in range(2000)) / 2000
p2 = sum(f(h) for h in range(28000, 30000)) / 2000
first, last = run["first_block"], run["last_block"]
greedy1 = (first - p1 * rand) / (1 - p1)              # 頭 2,000 手不亂選那部分的平均
if_same = p2 * rand + (1 - p2) * greedy1              # 不亂選那部分不變時，末 2,000 手應有的平均
greedy2 = (last - p2 * rand) / (1 - p2)
res = {"first": first, "last": last, "random": rand, "p_first": round(p1, 4), "p_last": round(p2, 4),
       "greedy_first": round(greedy1, 3), "greedy_last": round(greedy2, 3), "if_greedy_unchanged": round(if_same, 3),
       "total_gain": round(last - first, 3), "gain_from_less_random": round(if_same - first, 3),
       "gain_from_better_greedy": round(last - if_same, 3),
       "share_less_random_pct": round((if_same - first) / (last - first) * 100)}
# 換一個終點：不用末 2,000 手一塊，改用第 2 到第 15 塊（2,000 到 30,000 手）的平均，看拆法對終點怎麼選有多敏感
late = sum(run["blocks"][1:]) / len(run["blocks"][1:])
p_late = sum(f(h) for h in range(2000, 30000)) / 28000
if_same_late = p_late * rand + (1 - p_late) * greedy1
res["alt_end_blocks_2_15"] = {"mean": round(late, 3), "p": round(p_late, 4), "if_greedy_unchanged": round(if_same_late, 3),
                              "total_gain": round(late - first, 3), "gain_from_less_random": round(if_same_late - first, 3),
                              "gain_from_better_greedy": round(late - if_same_late, 3)}
# 兩部分各帶多少誤差：每個 2,000 手區塊約 ±0.05（95%，part1_extras 的 block_ci95_half），兩區塊誤差互相獨立，照線性傳遞
e = 0.05
k = (1 - p2) / (1 - p1)                               # if_same 對 first 的斜率
res["err95"] = {"block": e, "gain_from_less_random": round(abs(k - 1) * e, 3),
                "gain_from_better_greedy": round((e ** 2 + (k * e) ** 2) ** 0.5, 3)}
json.dump(res, open(os.path.join(D, "out/blackjack/part5_progress_split.json"), "w"), indent=1)
print(json.dumps(res))
