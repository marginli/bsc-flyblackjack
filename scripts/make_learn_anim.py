"""PART 1 第 4 節的五步互動示意圖（圖 3）：第 1 手輸了之後，學習規則怎麼走一遍。
重新呈現 → 送多巴胺 → 削弱 → 回復 → 好惡值變了。
數字讀 out/blackjack/learn_anim_data.json（scripts/learn_anim_data.py 用作者的 FlyPlayer.outcome 算的）與
out/blackjack/anim_data.json（圖 2 的 72 顆 KC 與每顆 KC 推得最用力的 MBON）。
產出：part1-what.html 裡 <!-- learn:start --> … <!-- learn:end --> 之間的片段。
沒有 JavaScript 時看到的是第 3 步（削弱）的靜態圖。
用法：python3 scripts/make_learn_anim.py"""
import json
import os
import re

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(D, "out/blackjack/learn_anim_data.json")))
A = json.load(open(os.path.join(D, "out/blackjack/anim_data.json")))
PAGE = os.path.join(D, "part1-what.html")
BLUE, AMBER, INK, SOFT, FAINT, BORDER, RED, PURPLE = "#2563eb", "#d97706", "#1b2733", "#5a6b7b", "#8b98a5", "#e4e8ee", "#dc2626", "#7c3aed"
MAG = 50                                             # 減少量放大倍數

KC_COLS, KC_SP, KC_R, KC_X, KC_Y = 30, 5, 1.8, 40, 112
DA_X, DA_W = 300, 100
MB_X, MB_W = 450, 120
DR_X = 640
MB_Y, MB_H = 112, 4.2
VB_W, VB_H = 960, 580
n_kc, n_mbon = A["n_kc"], A["n_mbon"]
val = A["mbon_valence"]
order = [i for i in range(n_mbon) if val[i] > 0] + [i for i in range(n_mbon) if val[i] < 0]
row_of = {m: r for r, m in enumerate(order)}
n_plus = A["n_mbon_plus"]
hit = A["actions"]["hit"]
kcv = [hit["kc_values"].get(str(i), 0) for i in range(n_kc)]
b = L["mbon_before"]["hit"]; a = L["mbon_after"]["hit"]
drop = [x - y for x, y in zip(b, a)]
da = L["da"]
MB_MAX = max(b)
VA, VB = L["valence_after"], L["valence_before"]


def kc_xy(i):
    return KC_X + (i % KC_COLS) * KC_SP, KC_Y + (i // KC_COLS) * KC_SP


def mb_y(m):
    return MB_Y + row_of[m] * MB_H


S = []
S.append(f'<svg class="anim-svg" viewBox="0 0 {VB_W} {VB_H}" role="img" aria-labelledby="lrnTitle" xmlns="http://www.w3.org/2000/svg">')
S.append('<title id="lrnTitle">第 1 手輸了之後的一次學習：72 顆亮的 KC、每顆 MBON 收到的多巴胺、MBON 活動與它減少的量</title>')
S.append(f'<text id="lrnHead" x="24" y="34" font-size="17" font-weight="700" fill="{INK}">第 3 步　削弱</text>')
S.append(f'<text x="24" y="58" font-size="13" fill="{SOFT}">第 1 手：硬 20 對莊家 8 選了要牌 → 抽到 6 爆牌 → 輸一注 → 懲罰強度 0.5</text>')
for x, lab in ((KC_X + KC_COLS * KC_SP / 2, f"KC　{n_kc:,} 顆"), (DA_X + DA_W / 2, "收到的多巴胺"), (MB_X + MB_W / 2, f"MBON 活動　{n_mbon} 顆"), (DR_X + 60, f"活動減少的量 ×{MAG}"), (850, "好惡值")):
    S.append(f'<text x="{x:.0f}" y="92" text-anchor="middle" font-size="13" font-weight="700" fill="{SOFT}">{lab}</text>')
# KC → MBON 線（第 3 步）
S.append(f'<g id="lrnLines" stroke="{RED}" stroke-width="0.6" stroke-opacity="0.4">')
for k, m in hit["kc_top_mbon"].items():
    x, y = kc_xy(int(k))
    S.append(f'<line x1="{x}" y1="{y}" x2="{MB_X}" y2="{mb_y(m) + MB_H / 2:.1f}"/>')
S.append('</g>')
S.append(f'<g id="lrnKC" fill="{INK}">')
for i in range(n_kc):
    x, y = kc_xy(i)
    S.append(f'<circle cx="{x}" cy="{y}" r="{KC_R}" fill-opacity="{round(0.3 + 0.7 * kcv[i], 2) if kcv[i] > 0 else 0.08}"/>')
S.append('</g>')
S.append(f'<text id="lrnKCnote" x="{KC_X}" y="{KC_Y + 40 * KC_SP + 18}" font-size="11" fill="{FAINT}">亮的 72 顆＝「硬 20 對 8</text>')
S.append(f'<text id="lrnKCnote2" x="{KC_X}" y="{KC_Y + 40 * KC_SP + 33}" font-size="11" fill="{FAINT}">配要牌」的代碼（圖 2 第 3 步）</text>')
# 多巴胺長條
S.append(f'<g id="lrnDA" fill="{PURPLE}">')
for m in order:
    S.append(f'<rect x="{DA_X}" y="{mb_y(m):.1f}" width="{da[m] / 0.5 * DA_W:.1f}" height="{MB_H - 1:.1f}" fill-opacity="0.8"/>')
S.append('</g>')
# MBON 活動
S.append('<g id="lrnMB">')
for m in order:
    col = BLUE if val[m] > 0 else AMBER
    S.append(f'<rect x="{MB_X}" y="{mb_y(m):.1f}" width="{a[m] / MB_MAX * MB_W:.1f}" height="{MB_H - 1:.1f}" fill="{col}" fill-opacity="0.85"/>')
S.append('</g>')
# 減少量（放大）
S.append(f'<g id="lrnDR" fill="{RED}">')
for m in order:
    S.append(f'<rect x="{DR_X}" y="{mb_y(m):.1f}" width="{drop[m] * MAG / MB_MAX * MB_W:.1f}" height="{MB_H - 1:.1f}" fill-opacity="0.85"/>')
S.append('</g>')
div_y = MB_Y + n_plus * MB_H
S.append(f'<line x1="{DA_X - 6}" y1="{div_y:.1f}" x2="{DR_X + 126}" y2="{div_y:.1f}" stroke="{FAINT}" stroke-dasharray="3 3"/>')
S.append(f'<text x="{DA_X}" y="{MB_Y - 6}" font-size="11" fill="{BLUE}">上面 {n_plus} 顆：標記 +1（趨近型）</text>')
S.append(f'<text x="{DA_X}" y="{MB_Y + n_mbon * MB_H + 12:.0f}" font-size="11" fill="{AMBER}">下面 {n_mbon - n_plus} 顆：標記 −1（迴避型）</text>')
# 回復說明（第 4 步）
S.append(f'<g id="lrnDecay" font-size="12" fill="{INK}" visibility="hidden">')
S.append(f'<text x="770" y="150">全部 {L["n_links_total"]:,} 條連結</text>')
S.append(f'<text x="770" y="170">各往 1 拉回一點：</text>')
S.append(f'<text x="770" y="190">0.00005 × (1 − 增益)</text>')
S.append(f'<text x="770" y="214" fill="{SOFT}">增益還是 1 的：不變</text>')
S.append(f'<text x="770" y="234" fill="{SOFT}">剛被削到 0.975 的：</text>')
S.append(f'<text x="770" y="254" fill="{SOFT}">拉回約 {L["decay_on_min_2sf"]}</text>')
S.append('</g>')
# 好惡值（第 5 步）
S.append(f'<g id="lrnVal" font-size="13" fill="{INK}" visibility="hidden">')
S.append(f'<text x="770" y="140" font-size="11" fill="{SOFT}">學之前 → 學之後</text>')
for j, (k, zh) in enumerate((("hit", "要牌"), ("stand", "停牌"), ("double", "加倍"))):
    y = 170 + j * 64
    S.append(f'<text x="770" y="{y}" font-weight="{"700" if k == "hit" else "400"}">{zh}　{VB[k]:.4f} → {VA[k]:.4f}</text>')
    S.append(f'<rect x="770" y="{y + 8}" width="{VB[k] / 0.25 * 160:.1f}" height="8" fill="none" stroke="{FAINT}"/>')
    S.append(f'<rect x="770" y="{y + 8}" width="{VA[k] / 0.25 * 160:.1f}" height="8" fill="{BLUE if k == "hit" else FAINT}"/>')
S.append(f'<text x="770" y="370" font-size="12" fill="{SOFT}">要牌仍最高</text>')
S.append('</g>')
S.append(f'<text x="24" y="{VB_H - 14}" font-size="12" fill="{FAINT}">KC 每顆一點、MBON 每顆一條，全部畫出。線：每顆亮的 KC 只畫它推得最用力的那一條。最右欄放大 {MAG} 倍，原尺寸看不出來。</text>')
S.append('</svg>')
svg = "\n".join(S)

steps = [
    ("一手結束，重新呈現",
     "這手輸了。把這手唯一的決定「硬 20 對 8 配要牌」再送進蕈狀體一次：亮的還是圖 2 那 72 顆 KC，MBON 活動也和當時一樣。"),
    ("送懲罰多巴胺",
     f"輸一注，懲罰強度 0.5。每顆 MBON 收到 0.5 × 它的「來自 PPL1 的比例」：{L['n_mbon_da_pos']} 顆收到、{L['n_mbon_da_zero']} 顆是 0；送出的多巴胺總量有 {round(L['da_share_plus'] * 100)}% 落在上面的趨近型。"),
    ("削弱",
     f"上面式子的第一行：亮的 KC 通往「收到多巴胺的 MBON」的連結，增益減掉 0.05 × KC 活動 × 多巴胺。這次動到 {L['n_links_cut']} 條，最多從 1 減到 {L['gain_min_after']}；其餘連結不動。下次再送同一個牌面，MBON 活動會變小，最右欄是少掉的量（放大 {MAG} 倍）。細節在下面。"),
    ("回復",
     "式子的第二行：所有連結都往 1 拉回一點。增益還是 1 的不變；剛被削弱的只拉回百萬分之一左右，這一次看不出來，要累積很多次呈現才有作用。"),
    ("好惡值變了",
     f"被削弱的多半是趨近型（加分），所以要牌的好惡值從 {VB['hit']} 降到 {VA['hit']}。停牌、加倍也降了一點（{VB['stand']} → {VA['stand']}、{VB['double']} → {VA['double']}），因為它們的代碼和要牌共用十幾顆 KC。要牌仍最高，細節在下面。"),
]
TITLES = [t for t, _ in steps]
ON = ' class="on"'
ctl = '''<div class="anim" id="p1learn">
  <div class="anim-ctl">
    <button type="button" class="anim-btn" id="lrnPrev">← 上一步</button>
    <span class="anim-step" id="lrnStep">第 3 步／5</span>
    <button type="button" class="anim-btn" id="lrnNext">下一步 →</button>
  </div>
'''
ol = '<ol class="anim-steps" id="lrnSteps">\n' + "\n".join(f'    <li{ON if i == 2 else ""}><b>第 {i + 1} 步　{t}。</b>{d}</li>' for i, (t, d) in enumerate(steps)) + '\n  </ol>'
sp, sm = L["sum_plus_before"], L["sum_minus_before"]
detail = (f'<details class="note"><summary>圖 3 的細節</summary>'
          f'<p>迴避型也會被削嗎：會，只是很少。懲罰時 97 顆 MBON 裡 {L["n_mbon_da_pos"]} 顆收到多巴胺：趨近型 {L["da_plus_n"]} 顆全收到，平均 {L["da_plus_mean"]}（滿額是 0.5）；迴避型 {L["da_minus_n"]} 顆裡 {L["da_minus_pos"]} 顆收到，但平均只有 {L["da_minus_mean"]}；中位數 {L["da_minus_median"]}，約是趨近型中位數（{L["da_plus_median"]}）的百分之一。所以「亮的 KC ＋ 收到多巴胺」這個條件，兩型的連結幾乎都滿足，差別在削多少：趨近型的連結被削得多，迴避型的只削一點點。第 4 節「作者的標記就是這樣定的」那段的 97%／3%，講的就是這個量的比例，不是「只有一部分 MBON 收到」。</p>'
          f'<p>為什麼只動到 {L["n_links_cut"]} 條：一顆 KC 只連到少數幾顆 MBON，72 顆亮的 KC 一共連出 {L["n_links_kc_lit"]} 條，其中 {L["n_links_cut"]} 條通往收到多巴胺的 MBON。最多減 {L["cut_max"]} ＝ 0.05 × KC 活動 1 × 多巴胺 0.5：出現在最亮的 KC（活動 1）通往只接 PPL1 的 MBON（多巴胺是滿的 0.5）的連結上。</p>'
          f'<p>為什麼好惡值往負走：好惡值＝加分堆 − 扣分堆。學之前加分堆 {sp:.3f}、扣分堆 {sm:.3f}；學之後加分堆 {L["sum_plus_after"]:.3f}、扣分堆 {L["sum_minus_after"]:.3f}。懲罰多巴胺多半送到趨近型，所以加分堆少得多、扣分堆幾乎不動，相減就變小。</p>'
          f'<p>停牌、加倍為什麼也跟著降：削弱的是「亮的 KC → MBON」這些連結本身，不是「要牌」這個動作。停牌的 72 顆 KC 有 {L["kc_shared_hit_stand"]} 顆和要牌相同、加倍有 {L["kc_shared_hit_double"]} 顆，這些 KC 的連結被削弱了，停牌、加倍算好惡值時也會用到。共用得少，所以降得少。</p>'
          f'<p>一次學習改變多少：要牌只降了 {VB["hit"] - VA["hit"]:.4f}，仍比停牌高 {VA["hit"] - VA["stand"]:.4f}。單看這一次，下次遇到同樣的局面還是會選要牌；要多輸幾次、把差距削掉，選擇才會換。這就是為什麼一次訓練要打 30,000 手。</p>'
          f'<p>回復的量：0.00005 × (1 − {L["gain_min_after"]}) ＝ {L["decay_on_min_txt"]}。制約實驗那組（0.012）回復得快 240 倍，所以 21 點刻意放慢，見本節「兩個作者設定的數」。</p>'
          f'</details>')
cap = (f'<p class="anim-cap"><b>圖 3　學習規則走一遍：第 1 手輸了之後的一次呈現。</b>按「上一步」「下一步」一步一步走，每一步的說明在圖下。'
       f'<span class="figsrc">例子接著圖 2：同一次訓練（打牌種子 0）的第 1 手，選了要牌、爆牌輸一注。這是整個訓練的第一次學習，學之前增益全是 1，所以每個數都能重算；學之前的三個好惡值與 PART 5 錄下的實跑相同；學之後的三個值實跑沒有錄（PART 5 只錄了前 6 手與最後 6 手的決定），是用作者這支學習程式直接算的。數字由 <code>scripts/learn_anim_data.py</code> 呼叫作者的 <code>FlyPlayer.outcome</code>（<code>flybrain/mb/blackjack.py</code>）算出，存在 <code>out/blackjack/learn_anim_data.json</code>；圖由 <code>scripts/make_learn_anim.py</code> 產生。沒有 JavaScript 時看到的是第 3 步的靜態圖。</span></p>')
script = '''<script>
(function(){
  var TITLES = %s;
  var svg = document.querySelector("#p1learn .anim-svg"); if(!svg) return;
  var kc = svg.querySelector("#lrnKC"), da = svg.querySelector("#lrnDA"), mb = svg.querySelector("#lrnMB"), dr = svg.querySelector("#lrnDR");
  var lines = svg.querySelector("#lrnLines"), dec = svg.querySelector("#lrnDecay"), vl = svg.querySelector("#lrnVal"), head = svg.querySelector("#lrnHead");
  var step = 0;
  function vis(el, on){ el.setAttribute("visibility", on ? "visible" : "hidden"); }
  function render(){
    vis(kc, step>=1); vis(svg.querySelector("#lrnKCnote"), step>=1); vis(svg.querySelector("#lrnKCnote2"), step>=1); vis(mb, step>=1);
    vis(da, step>=2); vis(lines, step===3); vis(dr, step>=3); vis(dec, step===4); vis(vl, step===5);
    head.textContent = step===0 ? "開始：第 1 手剛結束" : "第 " + step + " 步　" + TITLES[step-1];
    document.getElementById("lrnStep").textContent = step===0 ? "開始／5" : "第 " + step + " 步／5";
    document.getElementById("lrnPrev").disabled = step<=0;
    document.getElementById("lrnNext").disabled = step>=5;
    var lis = document.querySelectorAll("#lrnSteps li");
    for(var i=0;i<lis.length;i++) lis[i].className = (i===step-1) ? "on" : "";
  }
  document.getElementById("lrnPrev").onclick = function(){ if(step>0){ step--; render(); } };
  document.getElementById("lrnNext").onclick = function(){ if(step<5){ step++; render(); } };
  render();
})();
</script>''' % json.dumps(TITLES, ensure_ascii=False)
frag = "<!-- learn:start -->\n" + ctl + svg + "\n  " + ol + "\n  " + detail + "\n  " + cap + "\n</div>\n" + script + "\n<!-- learn:end -->"
page = open(PAGE, encoding="utf-8").read()
if "<!-- learn:start -->" in page:
    page = re.sub(r"<!-- learn:start -->.*?<!-- learn:end -->", lambda m: frag, page, flags=re.S)
else:
    anchor = '  <p class="figsrc">學習規則與兩組參數出自'
    assert page.count(anchor) == 1
    page = page.replace(anchor, "  <p><b>整條規則走一遍。</b>下面圖 3 接著圖 2 的那一手：硬 20 對 8 選了要牌、爆牌輸了，看一次呈現怎麼改動連結、好惡值怎麼跟著變。</p>\n" + frag + "\n" + anchor)
open(PAGE, "w", encoding="utf-8").write(page)
print("寫入 part1-what.html，片段", len(frag), "字元")
