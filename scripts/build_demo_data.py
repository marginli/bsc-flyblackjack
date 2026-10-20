"""PART 5 的影片與逐手資料：從 fly_play_game/demo/ 的錄製結果整理成本課要用的三份檔。

  assets/demo/bj_*.mp4        三支影片（render_bj.py 畫的），直接複製
  assets/demo/data.json       播放台用的逐格資料（只取 bj_episodes 與 blackjack 兩個鍵；out/demo_data.json 是同一份）
  out/bj_demo_summary.json    頁面上引用的檢查點：各條件開頭與結尾各 6 手的紀錄、幾個時點的 260 格統計、基本策略表各動作的格數

錄製與畫圖的程式在 ~/claude_bscai/fly_play_game/demo/（record_bj.py、render_bj.py），錄製時已對照 BJ2 的種子 0 結果。
用法：python3 scripts/build_demo_data.py
"""
import collections
import json
import os
import shutil

SRC = os.path.expanduser("~/claude_bscai/fly_play_game/demo")
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("bj_fly", "bj_nodopa", "bj_untrained")
ACT = ["hit", "stand", "double"]


def main():
    os.makedirs(os.path.join(D, "assets/demo"), exist_ok=True)
    for k in KEYS:
        shutil.copy2(os.path.join(SRC, "site", f"{k}.mp4"), os.path.join(D, "assets/demo", f"{k}.mp4"))
    site = json.load(open(os.path.join(SRC, "site/data.json")))
    data = {"bj_episodes": site["bj_episodes"], "blackjack": site["blackjack"]}
    s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for p in ("assets/demo/data.json", "out/demo_data.json"):
        open(os.path.join(D, p), "w").write(s)
    summary = {"source": "fly_play_game/demo/rec/bj_*.json（record_bj.py，seed 0，30,000 手，與 bj2 結果逐塊核對）", "conditions": {}}
    for k in KEYS:
        r = json.load(open(os.path.join(SRC, "rec", f"{k}.json")))
        n = r["hands"]
        hands = {}
        for h in list(range(6)) + list(range(n - 6, n)):
            hd = r["hand"][h]
            hands[str(h + 1)] = {"net": hd["net"], "how": hd["how"], "player": hd["p"], "dealer": hd["d"],
                                 "explore_rate": hd["explore_rate"],
                                 "decisions": [{"total": x["pt"], "soft": x["soft"], "upcard": x["up"], "first": x["first"],
                                                "values": {ACT[a]: v for a, v in zip(x["legal"], x["v"])},
                                                "chosen": ACT[x["a"]], "explored": x["explored"], "basic_strategy": ACT[x["bs"]]}
                                               for x in hd["dec"]],
                                 "dopamine": hd.get("dopamine", {}).get("sign"),
                                 "dopamine_strength": hd.get("dopamine", {}).get("strength")}
        snaps = {}
        for sn in r["snaps"]:
            if sn["h"] in (0, 200, 2000, 10000, 30000):
                c = collections.Counter(sn["cells"])
                snaps[str(sn["h"])] = {"hit": c.get(0, 0), "stand": c.get(1, 0), "double": c.get(2, 0),
                                       "agree": round(sn["agree"], 4), "depression": round(sn["depression"], 4)}
        last = r["snaps"][-1]
        hit_cells = sorted({(t, s) for (t, s, u), a in zip(r["chart_cells"], last["cells"]) if a == 0})
        by_h = {sn["h"]: sn["cells"] for sn in r["snaps"]}
        moved = collections.Counter((ACT[x], ACT[y]) for x, y in zip(by_h[2000], by_h[30000]) if x != y)   # PART 5：格數穩不等於表沒變
        summary["conditions"][k] = {"name": r["name"], "blocks": r["blocks"], "agree": r["agree"], "hands": hands,
                                    "chart_counts_after_hands": snaps,
                                    "still_hit_totals_at_end": [("soft " if s else "hard ") + str(t) for t, s in hit_cells],
                                    "cells_changed_2000_to_30000": {"total": sum(moved.values()),
                                                                    "moves": {f"{x}->{y}": n for (x, y), n in sorted(moved.items())}}}
        if k == "bj_fly":
            bs = collections.Counter(r["chart_bs"])
            summary["basic_strategy_cells"] = {"hit": bs[0], "stand": bs[1], "double": bs[2], "total": len(r["chart_bs"])}
            summary["reference"] = r["reference"]
            summary["params"] = r["params"]
            summary["kc_active_per_situation"] = r["circuit"]["k"]
    json.dump(summary, open(os.path.join(D, "out/bj_demo_summary.json"), "w"), indent=1, ensure_ascii=False)
    print("assets/demo/data.json", len(s), "bytes;", "summary conditions", list(summary["conditions"]))


main()
