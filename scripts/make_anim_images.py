"""PART 1 圖 2（三條式子走一遍）與圖 3（學習規則走一遍）的投影片用圖與離線包。
用無頭 Chrome 開單獨頁（anim.html、learn.html）?s=…&a=…&clean=1，逐一存下每個畫面：
  downloads/anim/p1anim-*.png、p1learn-*.png   高解析點陣圖（寬 3,200 像素），直接插進 PowerPoint
  downloads/anim/p1anim-*.svg、p1learn-*.svg   向量圖（PowerPoint 365 可插入、放大不糊）
  downloads/anim/flyblackjack-anim.zip、flyblackjack-learn.zip   各自的圖 ＋ 單獨頁 ＋ 使用說明
單獨頁由 make_anim.py、make_learn_anim.py 產生；改了它們就重跑本檔。
用法：python3 scripts/make_anim_images.py"""
import pathlib
import zipfile

from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).resolve().parent.parent
OUT = D / "downloads/anim"
FONT = '"Microsoft JhengHei","Noto Sans TC","PingFang TC","Segoe UI",sans-serif'
FIGS = [
    {"page": "anim.html", "prefix": "p1anim", "zip": "flyblackjack-anim.zip", "name": "三條式子走一遍（PART 1 圖 2）",
     "about": "例子是第 1 手的第一個決定：硬 20 對莊家 8、前兩張。每一步的說明在 PART 1 第 3 節圖 2 下面。",
     "keys": "← → 或 PageUp／PageDown：上一步、下一步；1 2 3：跳到第 6 步並切換要牌、停牌、加倍；",
     "param": "?s=6&a=stand", "anchor": "s3",
     "states": [(0, "hit", "s0-start", "開始（只有空的 PN、KC、MBON）"),
                (1, "hit", "s1", "第 1 步　牌面變成 PN 的活動"),
                (2, "hit", "s2", "第 2 步　每顆 KC 收到多少"),
                (3, "hit", "s3", "第 3 步　只留最高的 6%"),
                (4, "hit", "s4", "第 4 步　亮的 KC 推動 MBON"),
                (5, "hit", "s5", "第 5 步　加總成好惡值（配要牌）"),
                (6, "hit", "s6-hit", "第 6 步　三個動作比較，顯示要牌的 PN、KC、MBON"),
                (6, "stand", "s6-stand", "第 6 步　同上，顯示停牌"),
                (6, "double", "s6-double", "第 6 步　同上，顯示加倍")]},
    {"page": "learn.html", "prefix": "p1learn", "zip": "flyblackjack-learn.zip", "name": "學習規則走一遍（PART 1 圖 3）",
     "about": "例子接著圖 2：第 1 手硬 20 對莊家 8 選了要牌、爆牌輸一注之後的那一次學習。每一步的說明在 PART 1 第 4 節圖 3 下面。",
     "keys": "← → 或 PageUp／PageDown：上一步、下一步；",
     "param": "?s=3", "anchor": "s4",
     "states": [(0, "", "s0-start", "開始：第 1 手剛結束"),
                (1, "", "s1", "第 1 步　一手結束，重新呈現"),
                (2, "", "s2", "第 2 步　送懲罰多巴胺"),
                (3, "", "s3", "第 3 步　削弱"),
                (4, "", "s4", "第 4 步　回復"),
                (5, "", "s5", "第 5 步　好惡值變了")]},
]

OUT.mkdir(parents=True, exist_ok=True)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--disable-gpu"])
    pg = b.new_page(viewport={"width": 1600, "height": 934}, device_scale_factor=2)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    for F in FIGS:
        F["files"] = []
        for s, a, tag, _ in F["states"]:
            pg.goto(f"{(D / F['page']).as_uri()}?s={s}&a={a}&clean=1")
            el = pg.locator(".anim-svg")
            stem = f"{F['prefix']}-{tag}"
            el.screenshot(path=str(OUT / f"{stem}.png"))
            svg = el.evaluate("""(e, font) => { const c = e.cloneNode(true); c.removeAttribute('class');
                const vb = c.viewBox.baseVal; c.setAttribute('width', vb.width); c.setAttribute('height', vb.height);
                c.setAttribute('font-family', font);
                c.querySelectorAll('[visibility=hidden]').forEach(n => n.remove());
                const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                bg.setAttribute('width', '100%'); bg.setAttribute('height', '100%'); bg.setAttribute('fill', '#fff');
                c.insertBefore(bg, c.firstChild);
                return '<?xml version="1.0" encoding="UTF-8"?>\\n' + c.outerHTML; }""", FONT)
            (OUT / f"{stem}.svg").write_text(svg, encoding="utf-8")
            F["files"] += [f"{stem}.png", f"{stem}.svg"]
    b.close()
assert not errs, errs

for F in FIGS:
    n = len(F["states"])
    readme = (f"蕈狀體：{F['name']}投影片用圖\n\n"
              f"{n} 個畫面，每個都有 PNG（點陣，寬 3,200 像素）與 SVG（向量）兩種，挑一種插進 PowerPoint 即可：\n"
              + "".join(f"  {F['prefix']}-{tag}　{zh}\n" for _, _, tag, zh in F["states"])
              + f"\n{F['about']}\n\n"
              f"要現場操作：用瀏覽器打開 {F['page']}（單一檔案、不需網路）。\n"
              f"  {F['keys']}\n  D：顯示／隱藏這一步的說明；F：全螢幕；Home：回到開始。\n"
              f"  網址後面加 {F['param']} 可以指定一開始的畫面。\n\n"
              f"線上版：https://marginli.github.io/bsc-flyblackjack/{F['page']}\n"
              f"說明：https://marginli.github.io/bsc-flyblackjack/part1-what.html#{F['anchor']}\n")
    z = OUT / F["zip"]
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        root = z.stem + "/"
        zf.write(D / F["page"], root + F["page"])
        zf.writestr(root + "使用說明.txt", readme)
        for f in F["files"]:
            zf.write(OUT / f, root + f)
    print(F["page"], len(F["files"]), "個圖檔；", z.name, z.stat().st_size // 1024, "KB")
