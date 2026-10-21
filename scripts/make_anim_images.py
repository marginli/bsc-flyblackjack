"""PART 1 圖 2（三條式子走一遍）的投影片用圖與離線包。
用無頭 Chrome 開 anim.html?s=…&a=…&clean=1，逐一存下九個畫面（開始、第 1–5 步、第 6 步的三個動作）：
  downloads/anim/p1anim-*.png   高解析點陣圖（寬 3,200 像素），直接插進 PowerPoint
  downloads/anim/p1anim-*.svg   向量圖（PowerPoint 365 可插入、放大不糊）
  downloads/anim/flyblackjack-anim.zip   上面全部 ＋ anim.html ＋ 使用說明
anim.html 由 make_anim.py 產生；改了它就重跑本檔。
用法：python3 scripts/make_anim_images.py"""
import os
import pathlib
import zipfile

from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).resolve().parent.parent
OUT = D / "downloads/anim"
STATES = [(0, "hit", "s0-start", "開始（只有空的 PN、KC、MBON）"),
          (1, "hit", "s1", "第 1 步　牌面變成 PN 的活動"),
          (2, "hit", "s2", "第 2 步　每顆 KC 收到多少"),
          (3, "hit", "s3", "第 3 步　只留最高的 6%"),
          (4, "hit", "s4", "第 4 步　亮的 KC 推動 MBON"),
          (5, "hit", "s5", "第 5 步　加總成好惡值（配要牌）"),
          (6, "hit", "s6-hit", "第 6 步　三個動作比較，顯示要牌的 PN、KC、MBON"),
          (6, "stand", "s6-stand", "第 6 步　同上，顯示停牌"),
          (6, "double", "s6-double", "第 6 步　同上，顯示加倍")]
FONT = '"Microsoft JhengHei","Noto Sans TC","PingFang TC","Segoe UI",sans-serif'

OUT.mkdir(parents=True, exist_ok=True)
files = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1600, "height": 934}, device_scale_factor=2)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    for s, a, tag, _ in STATES:
        pg.goto(f"{(D / 'anim.html').as_uri()}?s={s}&a={a}&clean=1")
        el = pg.locator(".anim-svg")
        png = OUT / f"p1anim-{tag}.png"
        el.screenshot(path=str(png))
        svg = el.evaluate("""(e, font) => { const c = e.cloneNode(true); c.removeAttribute('class');
            c.setAttribute('width', '960'); c.setAttribute('height', '560'); c.setAttribute('font-family', font);
            c.querySelectorAll('[visibility=hidden]').forEach(n => n.remove());
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%'); bg.setAttribute('height', '100%'); bg.setAttribute('fill', '#fff');
            c.insertBefore(bg, c.firstChild);
            return '<?xml version="1.0" encoding="UTF-8"?>\\n' + c.outerHTML; }""", FONT)
        (OUT / f"p1anim-{tag}.svg").write_text(svg, encoding="utf-8")
        files += [png.name, f"p1anim-{tag}.svg"]
    b.close()
assert not errs, errs

README = "蕈狀體：三條式子走一遍（PART 1 圖 2）投影片用圖\n\n" + \
    "九個畫面，每個都有 PNG（點陣，寬 3,200 像素）與 SVG（向量）兩種，挑一種插進 PowerPoint 即可：\n" + \
    "".join(f"  p1anim-{tag}　{zh}\n" for _, _, tag, zh in STATES) + """
例子是第 1 手的第一個決定：硬 20 對莊家 8、前兩張。每一步的說明在 PART 1 第 3 節圖 2 下面。

要現場操作：用瀏覽器打開 anim.html（單一檔案、不需網路）。
  ← → 或 PageUp／PageDown：上一步、下一步；1 2 3：跳到第 6 步並切換要牌、停牌、加倍；
  D：顯示／隱藏這一步的說明；F：全螢幕；Home：回到開始。
  網址後面加 ?s=6&a=stand 可以指定一開始在第幾步、哪個動作。

線上版：https://marginli.github.io/bsc-flyblackjack/anim.html
說明：https://marginli.github.io/bsc-flyblackjack/part1-what.html#s3
"""
z = OUT / "flyblackjack-anim.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    root = "flyblackjack-anim/"
    zf.write(D / "anim.html", root + "anim.html")
    zf.writestr(root + "使用說明.txt", README)
    for f in files:
        zf.write(OUT / f, root + f)
print(len(files), "個圖檔；", z, z.stat().st_size // 1024, "KB")
