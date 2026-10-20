"""PART 4 X3：每種 KC 選法「沒學過」時 260 格各選什麼（要牌／停牌／加倍的格數），用來解釋各選法未訓練成績差很多的原因
（例如隨機一 −85%：一手最多輸 2 注，常加倍就可能輸得比亂選多）。電路檔同 part4_extras.py。
用法：cd <repo> && PYTHONPATH=. python <本檔>   （輸出 out/blackjack/x3_untrained_tables.json）"""
import json
import os

from flybrain.mb import blackjack as bj
from flybrain.mb.model import MushroomBody

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "out/blackjack/x3_untrained_tables.json")
CIRC = os.path.expanduser("~/claude_bscai/fly_play_game/blackjack/results/circuits")
x = json.load(open(os.path.join(D, "out/blackjack/bj_extra.json")))
res = {}
for name, path in [("author_1200", "data/mb_circuit.npz")] + [(k, os.path.join(CIRC, f"mb_{k}.npz")) for k in x["X3_kc_subsets"]["variants"]]:
    bj.MushroomBody = lambda path=path, **kw: MushroomBody(path=path, **kw)
    fly = bj.FlyPlayer(seed=0, learn=False, explore=0.0, explore_floor=0.0)
    got = [fly.greedy(t, s, u, True, [bj.HIT, bj.STAND, bj.DOUBLE]) for (t, s, u) in bj.chart_cells()]
    res[name] = {"hit": got.count(bj.HIT), "stand": got.count(bj.STAND), "double": got.count(bj.DOUBLE)}
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
