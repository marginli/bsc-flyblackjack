"""PART 1 第 5 節的小圖（圖 4）：點數的 18 個值在「682 顆 PN 排成的一列」上各取連續 26 顆。
每一列是一個點數，框住它取的座位；最下面一條是每個座位被幾個點數用到（2／1／0）。
數字讀 out/blackjack/encoding_pn.json（scripts/encoding_pn.py 照作者 Situation 的抽法算的）。
產出：part1-what.html 裡 <!-- pnstrip:start --> … <!-- pnstrip:end --> 之間的 <figure>。
用法：python3 scripts/make_pn_strip.py"""
import json
import os
import re

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(D, "out/blackjack/encoding_pn.json")))
PAGE = os.path.join(D, "part1-what.html")
BLUE, INK, SOFT, FAINT, BORDER = "#2563eb", "#1b2733", "#5a6b7b", "#8b98a5", "#e4e8ee"

N, W = E["pn_total"], E["total_width"]
starts = E["total_starts"]
X0, X1 = 70, 930                       # 座位 0 到 682 畫在這段
sx = (X1 - X0) / N
ROW, Y0 = 13, 40
VB_W = 960
cov = [0] * N
for s in starts:
    for i in range(s, s + W):
        cov[i] += 1
assert cov.count(2) == E["total_pn_used_twice"] and cov.count(1) == E["total_pn_used_once"]
last = starts[-1] + W                  # 269

S = []
yb = Y0 + len(starts) * ROW + 14       # 覆蓋條的 y
VB_H = yb + 70
S.append(f'<svg viewBox="0 0 {VB_W} {VB_H}" role="img" aria-labelledby="pnsTitle" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;border:1px solid {BORDER};border-radius:10px;background:#fff">')
S.append(f'<title id="pnsTitle">點數 4 到 21 各取 26 顆 PN：在 682 顆排成的一列上，起點每次往後挪 14 或 15 顆，18 個框一共蓋住前 {last} 個位置</title>')
S.append(f'<text x="{X0}" y="24" font-size="12" font-weight="700" fill="{SOFT}">682 顆 PN 用亂數排成一條隊伍（位置 0 到 681，每顆只出現一次；建立模型時排一次，之後不再變）</text>')
# 點數用不到的區域
S.append(f'<rect x="{X0 + last * sx:.1f}" y="{Y0 - 4}" width="{(N - last) * sx:.1f}" height="{len(starts) * ROW + 4}" fill="#f1f5f9"/>')
S.append(f'<text x="{X0 + (last + N) / 2 * sx:.0f}" y="{Y0 + len(starts) * ROW / 2:.0f}" text-anchor="middle" font-size="12" fill="{FAINT}">位置 {last}–{N - 1}：點數用不到（{N - last} 顆）</text>')
for r, s in enumerate(starts):
    y = Y0 + r * ROW
    S.append(f'<text x="{X0 - 8}" y="{y + 9}" text-anchor="end" font-size="10.5" fill="{SOFT}">點數 {r + 4}</text>')
    S.append(f'<rect x="{X0 + s * sx:.1f}" y="{y}" width="{W * sx:.1f}" height="{ROW - 3}" rx="2" fill="{BLUE}" fill-opacity="0.75"/>')
    if r < 3 or r == len(starts) - 1:
        S.append(f'<text x="{X0 + (s + W) * sx + 4:.1f}" y="{y + 9}" font-size="10" fill="{SOFT}">位置 {s}–{s + W - 1}</text>')
# 覆蓋條
S.append(f'<text x="{X0 - 8}" y="{yb + 10}" text-anchor="end" font-size="10.5" font-weight="700" fill="{INK}">被用幾次</text>')
i = 0
while i < N:
    j = i
    while j < N and cov[j] == cov[i]:
        j += 1
    col = {2: INK, 1: "#93c5fd", 0: "#f1f5f9"}[cov[i]]
    S.append(f'<rect x="{X0 + i * sx:.2f}" y="{yb}" width="{(j - i) * sx:.2f}" height="12" fill="{col}"/>')
    i = j
for x, lab in ((0, "0"), (last, str(last)), (N, str(N))):
    S.append(f'<line x1="{X0 + x * sx:.1f}" y1="{yb + 14}" x2="{X0 + x * sx:.1f}" y2="{yb + 20}" stroke="{FAINT}"/>')
    S.append(f'<text x="{X0 + x * sx:.1f}" y="{yb + 32}" text-anchor="middle" font-size="10.5" fill="{SOFT}">{lab}</text>')
lx = X0
for col, lab in ((INK, f"2 次：{E['total_pn_used_twice']} 顆"), ("#93c5fd", f"1 次：{E['total_pn_used_once']} 顆"), ("#f1f5f9", f"0 次：{N - last} 顆")):
    S.append(f'<rect x="{lx}" y="{yb + 44}" width="12" height="10" fill="{col}" stroke="{BORDER}"/>')
    S.append(f'<text x="{lx + 17}" y="{yb + 53}" font-size="11" fill="{SOFT}">{lab}</text>')
    lx += 130
S.append('</svg>')
svg = "\n".join(S)

cap = (f'<figcaption><b>圖 4　點數的 18 個值怎麼取 PN。</b>18 橫排畫的都是同一條隊伍、同樣的位置 0 到 {N - 1}，只是把每個點數的框分開畫在自己那一排；藍框是那個點數取的連續 {W} 個位置。下一個點數的框往右挪 {" 或 ".join(map(str, E["total_shift"]))} 格，'
       f'所以相鄰兩框重疊 {" 或 ".join(map(str, E["total_neighbour_overlaps"]))} 格。18 個框一共取 {E["total_picks"]} 次，只蓋到前 {last} 個位置，也就是 {last} 顆不同的 PN：{E["total_pn_used_twice"]} 顆各被取 2 次、{E["total_pn_used_once"]} 顆各取 1 次（{E["total_pn_used_twice"]} × 2 ＋ {E["total_pn_used_once"]} ＝ {E["total_picks"]}）；'
       f'最下面那條是每個位置被幾個點數用到，最多 2 次。明牌照同樣的方法，在另一條重新亂排的 682 顆隊伍上取。兩條隊伍都只在建立模型時排一次，整個訓練、換打牌種子都不再變。'
       f'<span class="figsrc">位置由 <code>scripts/encoding_pn.py</code> 照作者 <code>Situation</code> 的抽法算出，存在 <code>out/blackjack/encoding_pn.json</code>；圖由 <code>scripts/make_pn_strip.py</code> 產生。</span></figcaption>')
frag = '<!-- pnstrip:start -->\n  <figure class="fig">\n' + svg + '\n  ' + cap + '\n  </figure>\n<!-- pnstrip:end -->'
page = open(PAGE, encoding="utf-8").read()
if "<!-- pnstrip:start -->" in page:
    page = re.sub(r"<!-- pnstrip:start -->.*?<!-- pnstrip:end -->", lambda m: frag, page, flags=re.S)
else:
    anchor = "  <p>哪些 PN 分給哪個值，由一個固定的亂數種子"
    assert page.count(anchor) == 1
    page = page.replace(anchor, frag + "\n" + anchor)
open(PAGE, "w", encoding="utf-8").write(page)
print("寫入 part1-what.html")
