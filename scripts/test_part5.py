"""無頭瀏覽器測 PART 5 播放台：六頁載入無錯誤、三個分頁可切換、讀數跟影片格數對得上、時間軸點擊可跳轉。
用法：~/anaconda3/bin/python scripts/test_part5.py   （會自己起一個 http.server，需要 playwright 與 google-chrome）
截圖存到 _notes/shots/（不進網站）。"""
import json
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(D, "_notes", "shots")
PORT = 8767


def main():
    os.makedirs(SHOTS, exist_ok=True)
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=D,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    data = json.load(open(os.path.join(D, "assets/demo/data.json")))
    errors = []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--autoplay-policy=no-user-gesture-required"])
            pg = br.new_page(viewport={"width": 1280, "height": 900})
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.on("response", lambda r: errors.append(f"HTTP {r.status} {r.url}") if r.status >= 400 and "favicon" not in r.url else None)
            for page in ("index.html", "part1-what.html", "part2-setup.html", "part3-repro.html", "part4-checks.html"):
                pg.goto(f"http://127.0.0.1:{PORT}/{page}", wait_until="networkidle")
            pg.goto(f"http://127.0.0.1:{PORT}/part5-demo.html", wait_until="networkidle")
            pg.wait_for_function("typeof D!=='undefined' && D.bj_episodes")
            for key in ("bj_fly", "bj_nodopa", "bj_untrained"):
                E = data["bj_episodes"][key]
                pg.click(f"#btab-{key}")
                pg.wait_for_function("document.querySelector('#bjVid').readyState>=1")
                ff = [i for i, s in enumerate(E["st"]) if s == 7]
                mid = ff[len(ff) // 2]
                pg.evaluate(f"bjSeek({mid})")
                time.sleep(0.3)
                h = int("".join(ch for ch in pg.inner_text("#bjHudH") if ch.isdigit())) - 1
                assert h == E["h"][mid], (key, h, E["h"][mid])
                assert abs(float(pg.inner_text("#bjHudC")) - E["cum"][mid]) < 1e-3
                assert "快轉" in pg.inner_text("#bjStage")
                last_out = max(i for i, s in enumerate(E["st"]) if s == 6)
                pg.evaluate(f"bjSeek({last_out})")
                time.sleep(0.3)
                assert pg.inner_text("#bjOut") != "—", key
                print(f"{key}: ff frame {mid} → 第 {h + 1:,} 手; last outcome frame {last_out}: {pg.inner_text('#bjOut')}", flush=True)
            pg.locator("#bjTl").scroll_into_view_if_needed()
            box = pg.locator("#bjTl").bounding_box()
            pg.mouse.click(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5)
            time.sleep(0.3)
            i = int(pg.evaluate("bidx"))
            assert 0 < i < data["bj_episodes"]["bj_untrained"]["n"] - 1, i
            pg.evaluate("bjSeek(0)")
            pg.click("#bjPlay")
            time.sleep(2.0)
            i2 = int(pg.evaluate("bidx"))
            assert i2 > 20, i2
            pg.click("#bjPlay")
            print(f"timeline click → frame {i}; play 2 s → frame {i2}")
            top = pg.evaluate("document.querySelector('#s2').getBoundingClientRect().top+window.scrollY")
            pg.screenshot(path=os.path.join(SHOTS, "part5.png"), full_page=True, clip={"x": 0, "y": top, "width": 1280, "height": 760})
            pg.set_viewport_size({"width": 390, "height": 844})
            time.sleep(0.5)
            assert pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), "horizontal scroll at 390px"
            br.close()
    finally:
        srv.terminate()
    errors = [e for e in errors if not e.startswith("Failed to load resource")]
    assert not errors, errors
    print("PASS: no console errors; shots in", SHOTS)


if __name__ == "__main__":
    main()
