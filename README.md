# 蕈狀體學 21 點：重現 fly-blackjack

BSC 專題課程（**重現型**，規範見 `../types/repro.md`）。對象是公開的果蠅連結體模擬專案
[fly-blackjack](https://github.com/WilliamJones/fly-blackjack)（commit 004b2e3，MIT）。
2026-10-16 從原本合在一起的「果蠅大腦玩遊戲：重現兩個連結體模擬」拆出來；另一半（fruitfly-lab，Doom）在 `../fly_doom/`，
線上版 https://marginli.github.io/bsc-flysimu/ 。

線上版：https://marginli.github.io/bsc-flyblackjack/ （`robots.txt` 擋掉搜尋引擎索引）

## 頁面

| 頁面 | 內容 |
|---|---|
| `index.html` | 首頁 |
| `part1-what.html` | PART 1　這個專案在做什麼：四個零件、從 MaleCNS 切出蕈狀體、活動量算法、學習規則、四個實驗、哪些來自資料 |
| `part2-setup.html` | PART 2　準備環境與資料（一個環境、兩個指令） |
| `part3-repro.html` | PART 3　重現 fly-blackjack（BJ1–BJ5）；三種判定標準的定義處 |
| `part4-checks.html` | PART 4　作者沒做的檢查（X1–X4） |
| `part5-demo.html` | PART 5　逐手看蕈狀體怎麼打（三支影片的互動播放） |

## 目錄

| 路徑 | 內容 |
|---|---|
| `assets/flybj.css` | 共用樣式，與 `../fly_doom/assets/flysimu.css`、`../VFB/assets/vfb.css`、`../LPU/assets/lpu.css`、`../hub/assets/bsc.css` 用同一組設計變數 |
| `assets/p3-*.png`、`p4-*.png` | 真實資料圖，由 `scripts/make_figures.py` 產生 |
| `assets/demo/` | PART 5 的三支影片與逐格資料，由 `scripts/build_demo_data.py` 從 `~/claude_bscai/fly_play_game/demo/` 的錄製結果整理（錄製與畫影片的程式是那邊的 `record_bj.py`、`render_bj.py`） |
| `out/` | **頁面上每個數字的出處**：實跑的 JSON 與 log（`collect_out.py`）、可攜測試（`porttest.json`）、PART 5 的檢查點（`bj_demo_summary.json`） |
| `pack/` | 學員下載包的原始檔（`setup_envs.sh`、`blackjack/run_all.sh`、`blackjack/scripts/`、`check.py`、`expected.json`） |
| `downloads/flyblackjack-code.zip` | `pack/` 打包，附 `SHA256SUMS.txt`。改了 `pack/` 任何檔案都要重打包 |
| `scripts/` | 收資料、產圖、產驗收表、整理影片資料、記錄可攜測試，以及四道稽核（`page_audit.py`、`content_audit.py`、`svg_audit.py`、`number_audit.py`） |
| `_notes/` | 修正紀錄。**進 repo，但由 workflow 的 `rm -rf _notes` 擋在網站之外** |

## 重產

```
~/anaconda3/bin/python scripts/collect_out.py     # 實跑資料夾 → out/（保留 porttest.json、demo_data.json、bj_demo_summary.json）
python3 scripts/build_demo_data.py                # fly_play_game/demo → assets/demo/、out/demo_data.json、out/bj_demo_summary.json
~/anaconda3/bin/python scripts/make_figures.py    # out/ → assets/*.png
python3 scripts/make_expected.py                  # out/ → pack/expected.json，接著重打包 downloads/
python3 scripts/record_porttest.py <測試資料夾> blackjack   # 可攜測試 → out/porttest.json
python3 scripts/number_audit.py                   # 頁面數字對回 out/
python3 scripts/page_audit.py                     # 標籤平衡、連結與錨點、中英夾雜
```

重打包：`cd pack && rm -f SHA256SUMS.txt && find . -type f | sort | xargs sha256sum > SHA256SUMS.txt && rm -f ../downloads/*.zip && zip -qr ../downloads/flyblackjack-code.zip . && cp SHA256SUMS.txt ../downloads/`

實跑資料夾是本機的 `~/claude_bscai/fly_play_game/blackjack/`，結構與下載包解開後相同。

## 授權

fly-blackjack 與它用的 MaleCNS 整理版（connectome_data_prep）都是開放授權（MIT／CC BY 4.0）；下載包仍不附作者的檔案，由 `run_all.sh` 自己 clone 到固定的 commit。

教學用途，非營利。
