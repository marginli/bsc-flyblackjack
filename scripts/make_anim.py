"""PART 1 第 3 節的六步互動示意圖（圖 2）：PN → KC → 只留 6% → MBON → 好惡值 → 三個動作比較。
數字全部讀 out/blackjack/anim_data.json（scripts/anim_data.py 用作者的模型算的，第 1 手第一個決定，三個好惡值與錄檔相同）。
產出：part1-what.html 裡 <!-- anim:start --> … <!-- anim:end --> 之間的片段（SVG ＋ 按鈕 ＋ 六步文字 ＋ 腳本）。
沒有 JavaScript 時看到的是第 5 步配「要牌」的靜態圖（屬性直接寫死在 SVG 上）。
用法：python3 scripts/make_anim.py"""
import json
import os
import re

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = json.load(open(os.path.join(D, "out/blackjack/anim_data.json")))
PAGE = os.path.join(D, "part1-what.html")
ACTS = [("hit", "要牌"), ("stand", "停牌"), ("double", "加倍")]
RULES = '莊家：發牌、和你對賭的那一方（賭場）；一手 21 點只有你和莊家兩方比。一手牌的時間線：押一注（注：賭注的單位）→ 你拿兩張、莊家拿兩張但只翻開一張給你看（明牌）→ 你做決定（要牌、停牌或加倍，下面解釋），可以重複好幾次 → 你停了之後莊家補牌 → 比大小結算。點數：2 到 10 照面值，J、Q、K 算 10，A 算 1 或 11（哪個對你有利算哪個）；手上有 A 算成 11 而沒爆的叫軟手，其餘叫硬手；超過 21 叫爆牌、直接輸。三個動作：要牌 ＝ 再抽一張，沒爆就再決定一次；停牌 ＝ 不抽了；加倍 ＝ 只在第一個決定（手上還只有發的兩張）能選，再押一注、只再發你一張就強制停牌，輸贏都算兩注。莊家補牌：翻開蓋牌，不到 17 點一定抽、到了就停；莊家爆了而你沒爆就是你贏。結算：贏了淨賺一注、輸了賠一注、平手原注拿回。'
BLUE, AMBER, INK, SOFT, FAINT, BORDER = "#2563eb", "#d97706", "#1b2733", "#5a6b7b", "#8b98a5", "#e4e8ee"

# ── 版面 ───────────────────────────────────────────────────────────
PN_COLS, PN_SP, PN_R, PN_X, PN_Y = 22, 6, 2.2, 34, 96
KC_COLS, KC_SP, KC_R, KC_X, KC_Y = 30, 5, 1.8, 318, 96
MB_X, MB_Y, MB_H, MB_W = 640, 104, 4.2, 110          # 97 條長條，長度照活動量
VB_W, VB_H = 960, 560
n_pn, n_kc, n_mbon = A["n_pn"], A["n_kc"], A["n_mbon"]
val = A["mbon_valence"]
order = [i for i in range(n_mbon) if val[i] > 0] + [i for i in range(n_mbon) if val[i] < 0]   # +1 在上、−1 在下
row_of = {m: r for r, m in enumerate(order)}
n_plus = A["n_mbon_plus"]


def pn_xy(i):
    return PN_X + (i % PN_COLS) * PN_SP, PN_Y + (i // PN_COLS) * PN_SP


def kc_xy(i):
    return KC_X + (i % KC_COLS) * KC_SP, KC_Y + (i // KC_COLS) * KC_SP


def mb_y(m):
    return MB_Y + row_of[m] * MB_H


def pn_op(v):      # 亮度照活動量；超過 1.3 的一律全亮
    return 0 if v <= 0 else round(min(1.0, 0.25 + 0.75 * min(v, 1.3) / 1.3), 2)


def kc_op(v):
    return 0 if v <= 0 else round(0.3 + 0.7 * v, 2)


hit = A["actions"]["hit"]
pnv = [hit["pn_values"].get(str(i), 0) for i in range(n_pn)]
kcv = [hit["kc_values"].get(str(i), 0) for i in range(n_kc)]

# ── SVG（第 5 步配要牌的靜態狀態寫死在屬性上） ─────────────────────────
S = []
S.append(f'<svg class="anim-svg" viewBox="0 0 {VB_W} {VB_H}" role="img" aria-labelledby="animTitle" xmlns="http://www.w3.org/2000/svg">')
S.append(f'<title id="animTitle">第 1 手第一個決定（硬 20 對莊家 8、前兩張）配「要牌」：PN、KC、MBON 的活動量與好惡值</title>')
S.append(f'<text id="animHead" x="24" y="34" font-size="17" font-weight="700" fill="{INK}">第 5 步　加總成好惡值：硬 20 對莊家 8、前兩張，配「要牌」</text>')
for x, lab in ((PN_X + PN_COLS * PN_SP / 2, f"PN　{n_pn} 顆"), (KC_X + KC_COLS * KC_SP / 2, f"KC　{n_kc:,} 顆"), (MB_X + 55, f"MBON　{n_mbon} 顆"), (872, "好惡值")):
    S.append(f'<text x="{x:.0f}" y="76" text-anchor="middle" font-size="13" font-weight="700" fill="{SOFT}">{lab}</text>')
# 箭頭
for x1, x2, y, lab in ((PN_X + PN_COLS * PN_SP + 10, KC_X - 12, 190, "× 權重，加總"), (KC_X + KC_COLS * KC_SP + 10, MB_X - 10, 190, "× 權重 × 增益，加總")):
    S.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{FAINT}" stroke-width="1.5" marker-end="url(#animArrow)"/>')
    S.append(f'<text x="{(x1 + x2) / 2:.0f}" y="{y - 8}" text-anchor="middle" font-size="11" fill="{FAINT}">{lab}</text>')
S.append(f'<defs><marker id="animArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{FAINT}"/></marker></defs>')
# KC→MBON 線（第 4 步起）
S.append('<g id="animLines" stroke="#94a3b8" stroke-width="0.6" stroke-opacity="0.45">')
for k, m in hit["kc_top_mbon"].items():
    x, y = kc_xy(int(k))
    S.append(f'<line x1="{x}" y1="{y}" x2="{MB_X}" y2="{mb_y(m) + MB_H / 2:.1f}"/>')
S.append('</g>')
# PN 點
S.append(f'<g id="animPN" fill="{BLUE}">')
for i in range(n_pn):
    x, y = pn_xy(i)
    S.append(f'<circle cx="{x}" cy="{y}" r="{PN_R}" fill-opacity="{pn_op(pnv[i])}" stroke="{BORDER}" stroke-width="0.4"/>')
S.append('</g>')
# KC 點
S.append(f'<g id="animKC" fill="{INK}">')
for i in range(n_kc):
    x, y = kc_xy(i)
    S.append(f'<circle cx="{x}" cy="{y}" r="{KC_R}" fill-opacity="{kc_op(kcv[i]) or 0.08}"/>')
S.append('</g>')
# MBON 長條（依標記排兩堆）
S.append('<g id="animMB">')
scale = MB_W / A["mbon_max_all"]
for m in order:
    y = mb_y(m)
    col = BLUE if val[m] > 0 else AMBER
    S.append(f'<rect x="{MB_X}" y="{y:.1f}" width="{hit["mbon"][m] * scale:.1f}" height="{MB_H - 1:.1f}" fill="{col}" fill-opacity="0.85"/>')
div_y = MB_Y + n_plus * MB_H
S.append(f'<line x1="{MB_X - 6}" y1="{div_y:.1f}" x2="{MB_X + MB_W + 6}" y2="{div_y:.1f}" stroke="{FAINT}" stroke-dasharray="3 3"/>')
S.append(f'<text id="animLabPlus" x="{MB_X}" y="{MB_Y - 6}" font-size="11" fill="{BLUE}">上面 {n_plus} 顆：標記 +1（趨近型）</text>')
S.append(f'<text id="animLabMinus" x="{MB_X}" y="{MB_Y + n_mbon * MB_H + 12:.0f}" font-size="11" fill="{AMBER}">下面 {n_mbon - n_plus} 顆：標記 −1（迴避型）</text>')
S.append('</g>')
# 好惡值框（第 5 步：兩堆相減；第 6 步：三個動作並排）
vx = 812
S.append(f'<g id="animVal" font-size="13" fill="{INK}">')
S.append(f'<text x="{vx}" y="300" fill="{BLUE}">加分堆 ＋{hit["sum_plus_3dp"]}</text>')
S.append(f'<text x="{vx}" y="322" fill="{AMBER}">扣分堆 {hit["sum_minus_3dp"]}</text>')
S.append(f'<text x="{vx}" y="350" font-weight="700">相減＝好惡值 {hit["valence_3dp"]}</text>')
S.append('</g>')
S.append(f'<g id="animCmp" font-size="13" fill="{INK}" visibility="hidden">')
for j, (a, zh) in enumerate(ACTS):
    v = A["actions"][a]["valence"]
    y = 280 + j * 44
    S.append(f'<text x="{vx}" y="{y}" font-weight="{"700" if a == "hit" else "400"}">{zh}　{v:.4f}</text>')
    S.append(f'<rect x="{vx}" y="{y + 6}" width="{v / 0.25 * 130:.1f}" height="10" fill="{BLUE if a == "hit" else FAINT}"/>')
S.append(f'<text x="{vx}" y="420" font-size="12" fill="{SOFT}">選最高：要牌</text>')
S.append('</g>')
S.append(f'<text id="animNote" x="24" y="{VB_H - 16}" font-size="12" fill="{FAINT}">PN、KC 每顆一點，MBON 每顆一條，全部畫出；亮度與長度照活動量。線：每顆亮的 KC 只畫它推得最用力的那一條。</text>')
S.append('</svg>')
svg = "\n".join(S)

# ── 六步文字 ─────────────────────────────────────────────────────────
st, sd = A["actions"]["stand"], A["actions"]["double"]
by = hit["pn_lit_by_feature"]
steps = [
    ("牌面變成 PN 的活動",
     f"這手的局面（本頁用詞：<b>牌面</b>＝自己手上的點數配莊家明牌；<b>局面</b>＝牌面再加上軟硬、是不是前兩張；<b>氣味</b>＝局面配一個候選動作）。硬 20：你手上 10＋10，沒有 A 算成 11；硬 20 再抽除了 A 以外都爆，軟手再抽一張不會爆（A 可以改算 1）。莊家 8：翻開的那張是 8，你做決定時只看得到它。前兩張：你還沒抽過牌，所以加倍也能選，三個動作都開著。編碼。這個局面拆成五項資訊：硬 20 是兩項（點數 20、硬手），加上明牌 8、前兩張、候選動作「要牌」，各選中一組 PN（哪一組對哪個值，是作者事先用固定亂數抽定的，人設，和這些 PN 在真果蠅裡聞什麼無關；第 5 節講）：點數 {by['total']} 顆、明牌 {by['upcard']} 顆、動作 {by['action']} 顆、軟硬 {by['soft']} 顆、前兩張 {by['first']} 顆，五組共 {hit['pn_lit'] + hit['pn_overlap']} 顆，其中 {hit['pn_overlap']} 顆被兩項資訊同時選中、只算一次，實際亮 {hit['pn_lit']} 顆，其餘 {hit['pn_dark']} 顆是 0。每顆被選中的 PN 各有一個 0.7 到 1 的固定數當活動量，動作那組乘 1.3，被同時選中的把兩邊相加；整欄超過 1 的有 {hit['pn_over_1']} 顆，多數是動作那組。圖上亮度照活動量。"),
    ("每顆 KC 收到多少",
     f"每顆 KC 把「收到的每顆 PN 的活動 × 那條連結的權重」加總；權重是突觸數除以該 KC 收到的 PN 突觸總數。1,200 顆裡 {hit['kc_drive_nonzero']} 顆收到非零的量（接到亮的 PN 才有），最高 {hit['kc_drive_max_3dp']}。圖上 KC 欄變成深淺不一。"),
    ("只留最高的 6%",
     f"1,200 顆只留最高的 {A['k_winners']} 顆，其餘歸 0；留下的 {A['k_winners']} 顆除以其中最大值，變成 0 到 1。這 {A['k_winners']} 顆就是「硬 20 對 8 配要牌」這種氣味的代碼。這一步是作者用規則代替真果蠅的 APL，是人為設定。"),
    ("亮的 KC 推動 MBON",
     f"每顆 MBON 把「每顆亮的 KC 的活動 × KC→MBON 權重 × 增益」加總（這是訓練的第一手，增益全是 1，什麼都還沒學），再加上 0.25 × 其他 MBON 推過來的量。圖上 97 顆 MBON 各一條長條，長度是活動量，最高 {A['mbon_max_all_3dp']}；每顆亮的 KC 只畫它推得最用力的那一條線。"),
    ("加總成好惡值",
     f"每顆 MBON 乘它的標記再全部加起來。圖上 MBON 依標記排成兩堆：上面 {n_plus} 顆 +1（趨近型）、下面 {n_mbon - n_plus} 顆 −1（迴避型）。加分堆 {hit['sum_plus_3dp']}、扣分堆 {hit['sum_minus_3dp']}，相減得到配「要牌」的好惡值 {hit['valence_3dp']}。"),
    ("三個動作各算一次，選最高",
     f"同一手牌配停牌、配加倍再各走一遍步驟 1 到 5：PN 只換「動作」那組。三個好惡值：要牌 {hit['valence']}、停牌 {st['valence']}、加倍 {sd['valence']}，選最高的要牌。用上面的按鈕切換三個動作，看 PN、KC、MBON 怎麼跟著換；細節在六步下面的「第 6 步的細節」。"),
]

ctl = '''<div class="anim" id="p1anim">
  <div class="anim-ctl">
    <button type="button" class="anim-btn" id="animPrev">← 上一步</button>
    <span class="anim-step" id="animStep">第 5 步／6</span>
    <button type="button" class="anim-btn" id="animNext">下一步 →</button>
    <span class="anim-acts" id="animActs">候選動作：''' + "".join(f'<button type="button" class="anim-act{" on" if a == "hit" else ""}" data-act="{a}">{zh}</button>' for a, zh in ACTS) + '''</span>
  </div>
'''
ON = ' class="on"'
ol = '<ol class="anim-steps" id="animSteps">\n' + "\n".join(f'    <li{ON if i == 4 else ""}><b>第 {i + 1} 步　{t}。</b>{d}</li>' for i, (t, d) in enumerate(steps)) + '\n  </ol>'
cap = (f'<p class="anim-cap"><b>圖 2　三條式子走一遍：第 1 手的第一個決定（硬 20 對莊家 8、前兩張）。</b>按「上一步」「下一步」一步一步走，每一步的說明在圖下。'
       f'<span class="figsrc">例子出自一次正常的訓練（有學習、有探索，第 5 節叫它完整模型）、打牌種子 0（種子：給亂數產生器的起始數字，第 5 節講）的第 1 手；因為是整個訓練的第一個決定、增益還全是 1，不必重放整段訓練，直接用作者的模型就能重算每一欄，三個好惡值與 PART 5 錄下的實跑相同。PN、KC、MBON 全部畫出，不是示意。沒有 JavaScript 時看到的是第 5 步配「要牌」的靜態圖。數字由 <code>scripts/anim_data.py</code> 用作者的 <code>flybrain/mb/model.py</code> 算出，存在 <code>out/blackjack/anim_data.json</code>；圖由 <code>scripts/make_anim.py</code> 產生。</span></p>')

# ── 腳本資料：三個動作的逐顆數值 ─────────────────────────────────────
data = {"pnMax": 1.3, "mbonMax": A["mbon_max_all"], "order": order, "val": val, "kcMax": {}, "acts": {}}
for a, _ in ACTS:
    x = A["actions"][a]
    data["acts"][a] = {
        "pn": [x["pn_values"].get(str(i), 0) for i in range(n_pn)],
        "drive": x["kc_drive_max"],
        "kc": [x["kc_values"].get(str(i), 0) for i in range(n_kc)], "kcd": x["kc_drive_values"],
        "mbon": x["mbon"], "top": [[int(k), m] for k, m in x["kc_top_mbon"].items()],
        "plus": x["sum_plus_3dp"], "minus": x["sum_minus_3dp"], "v3": x["valence_3dp"],
        "lit": x["pn_lit"], "dark": x["pn_dark"], "nz": x["kc_drive_nonzero"], "dmax": x["kc_drive_max_3dp"],
    }
js_data = json.dumps(data, separators=(",", ":"))
script = '''<script>
(function(){
  var D = %s;
  var ZH = {hit:"要牌", stand:"停牌", double:"加倍"};
  var TITLES = ["牌面變成 PN 的活動","每顆 KC 收到多少","只留最高的 6%%","亮的 KC 推動 MBON","加總成好惡值","三個動作各算一次，選最高"];
  var svg = document.querySelector("#p1anim .anim-svg"); if(!svg) return;
  var pn = svg.querySelectorAll("#animPN circle"), kc = svg.querySelectorAll("#animKC circle"), mb = svg.querySelectorAll("#animMB rect");
  var lines = svg.querySelector("#animLines"), valG = svg.querySelector("#animVal"), cmpG = svg.querySelector("#animCmp"), head = svg.querySelector("#animHead");
  var KC_COLS=%d, KC_SP=%d, KC_X=%d, KC_Y=%d, MB_X=%d, MB_Y=%g, MB_H=%g, MB_W=%d;
  var step = 5, act = "hit";
  function pnOp(v){ return v<=0?0:Math.min(1,0.25+0.75*Math.min(v,1.3)/1.3); }
  function kcOp(v){ return v<=0?0:0.3+0.7*v; }
  function render(){
    var a = D.acts[act], i;
    for(i=0;i<pn.length;i++) pn[i].setAttribute("fill-opacity", step>=1 ? pnOp(a.pn[i]) : 0);
    for(i=0;i<kc.length;i++){
      var o = 0.08;
      if(step===2) o = a.kcd[i]>0 ? 0.15+0.85*a.kcd[i]/a.drive : 0.08;
      else if(step>=3) o = a.kc[i]>0 ? kcOp(a.kc[i]) : 0.08;
      kc[i].setAttribute("fill-opacity", o);
    }
    svg.querySelector("#animLabPlus").setAttribute("visibility", step>=5 ? "visible" : "hidden");
    svg.querySelector("#animLabMinus").setAttribute("visibility", step>=5 ? "visible" : "hidden");
    for(i=0;i<mb.length;i++){
      var m = D.order[i];
      mb[i].setAttribute("width", step>=4 ? (a.mbon[m]/D.mbonMax*MB_W).toFixed(1) : 0);
      mb[i].setAttribute("fill", step>=5 ? (D.val[m]>0?"#2563eb":"#d97706") : "#5a6b7b");
    }
    while(lines.firstChild) lines.removeChild(lines.firstChild);
    if(step>=4){
      var rowOf = {}; for(i=0;i<D.order.length;i++) rowOf[D.order[i]] = i;
      a.top.forEach(function(t){
        var k=t[0], m=t[1], l=document.createElementNS("http://www.w3.org/2000/svg","line");
        l.setAttribute("x1", KC_X+(k%%KC_COLS)*KC_SP); l.setAttribute("y1", KC_Y+Math.floor(k/KC_COLS)*KC_SP);
        l.setAttribute("x2", MB_X); l.setAttribute("y2", (MB_Y+rowOf[m]*MB_H+MB_H/2).toFixed(1));
        lines.appendChild(l);
      });
    }
    valG.setAttribute("visibility", step===5 ? "visible" : "hidden");
    cmpG.setAttribute("visibility", step===6 ? "visible" : "hidden");
    var vt = valG.querySelectorAll("text");
    vt[0].textContent = "加分堆 ＋" + a.plus; vt[1].textContent = "扣分堆 " + a.minus; vt[2].textContent = "相減＝好惡值 " + a.v3;
    head.textContent = (step===0 ? "開始　" : "第 " + step + " 步　" + TITLES[step-1] + "：") + "硬 20 對莊家 8、前兩張，配「" + ZH[act] + "」";
    document.getElementById("animStep").textContent = step===0 ? "開始／6" : "第 " + step + " 步／6";
    document.getElementById("animPrev").disabled = step<=0;
    document.getElementById("animNext").disabled = step>=6;
    document.getElementById("animActs").style.visibility = step>=6 ? "visible" : "hidden";
    var lis = document.querySelectorAll("#animSteps li");
    for(i=0;i<lis.length;i++) lis[i].className = (i===step-1) ? "on" : "";
    var acts = document.querySelectorAll("#animActs .anim-act");
    for(i=0;i<acts.length;i++) acts[i].className = "anim-act" + (acts[i].getAttribute("data-act")===act ? " on" : "");
  }
  document.getElementById("animPrev").onclick = function(){ if(step>0){ step--; if(step<6) act="hit"; render(); } };
  document.getElementById("animNext").onclick = function(){ if(step<6){ step++; render(); } };
  var acts = document.querySelectorAll("#animActs .anim-act");
  for(var i=0;i<acts.length;i++) acts[i].onclick = function(){ act = this.getAttribute("data-act"); render(); };
  step = 0; render();
})();
</script>'''

script = script % (js_data, KC_COLS, KC_SP, KC_X, KC_Y, MB_X, MB_Y, MB_H, MB_W)
detail6 = (f'<details class="note"><summary>第 6 步的細節</summary>'
           f'<p>PN 怎麼換：不換的四組共 {A["pn_fixed_sum"]} 顆，其中被兩組同時選中的只算一次，是 {A["pn_fixed_union"]} 顆，加上要牌與停牌的動作組碰巧撞到的 {A["pn_action_shared_hit_stand"]} 顆，所以要牌與停牌亮的 PN 有 {A["pn_shared_hit_stand"]} 顆相同。</p>'
           f'<p>KC 為什麼幾乎全換（{A["k_winners"]} 顆裡只有 {A["kc_shared_hit_stand"]} 顆相同）：動作那組乘了 1.3，是推得最用力的一組，換動作等於換掉最強的 36 顆輸入，每顆 KC 收到的總量都跟著動，前 {A["k_winners"]} 名的名單就大洗牌；作者在 Situation（作者程式裡把牌面變成 PN 輸入的那一段）的註解裡寫，動作給最寬的代碼，「因為選擇正是要學的東西」；三種氣味只差在動作、代碼卻差很多，就是這個設計的結果。</p>'
           f'<p>這一手的後續：模型有時會不看好惡值、隨機選一個動作（第 5 節叫探索），實跑裡這個決定沒有亂選，是照好惡值選的。接著抽到 6，爆牌，輸一注，懲罰多巴胺送出去（第 4 節）。基本策略（賭場數學算出來的公開最佳打法表，第 5 節）在 20 點該停牌；沒學過的果蠅在 20 點還要牌：它幾乎每格都選要牌，為什麼偏要牌，見第 5 節「未訓練的對照值」那段。</p>'
           f'</details>')
rules_html = '  <p><b>先懂這手牌（沒玩過 21 點的人看這段；第 5 節有作者簡化的幾條）。</b>' + RULES + '</p>\n'
frag = "<!-- anim:start -->\n" + rules_html + ctl + svg + "\n  " + ol + "\n  " + detail6 + "\n  " + cap + "\n</div>\n" + script + "\n<!-- anim:end -->"
print("fragment chars:", len(frag))
page = open(PAGE, encoding="utf-8").read()
if "<!-- anim:start -->" in page:
    page = re.sub(r"<!-- anim:start -->.*?<!-- anim:end -->", lambda m: frag, page, flags=re.S)
else:
    anchor = '  <p class="figsrc">算法出自'
    assert page.count(anchor) == 1
    page = page.replace(anchor, frag + "\n" + anchor)
open(PAGE, "w", encoding="utf-8").write(page)
print("寫入 part1-what.html")

# ── 單獨頁 anim.html：給簡報嵌入或離線開（同一份 SVG、按鈕、六步文字與腳本；版型在 standalone_page.py） ─────────
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standalone_page import build

alone = build(prefix="anim", box_id="p1anim", name="蕈狀體：三條式子走一遍", title="三條式子走一遍",
              doc="PART 1 圖 2 的單獨版", gen="scripts/make_anim.py",
              params="?s=0..6（從第幾步開始）&a=hit|stand|double（第 6 步的動作）&clean=1（只留圖，截圖用）",
              hint="按「下一步 →」開始。六步走完同一手牌的第一個決定：硬 20 對莊家 8、前兩張。",
              n_steps=6, ctl=ctl, svg=svg, ol=ol, script=script)
open(os.path.join(D, "anim.html"), "w", encoding="utf-8").write(alone)
print("寫入 anim.html", len(alone) // 1024, "KB")
