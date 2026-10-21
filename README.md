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
| `part1-what.html` | PART 1　這個專案在做什麼：四個零件、從 MaleCNS 切出蕈狀體、活動量算法、學習規則、21 點實驗、哪些來自資料；另外三個實驗只簡介 |
| `part2-setup.html` | PART 2　準備環境與資料（一個環境、兩個指令） |
| `part3-repro.html` | PART 3　重現 21 點（BJ1–BJ3）；三種判定標準的定義處 |
| `part4-checks.html` | PART 4　作者沒做的檢查（X1–X4，都在 21 點上做） |
| `part5-demo.html` | PART 5　逐手看蕈狀體怎麼打（三支影片的互動播放） |
| `part6-code.html` | PART 6　讀程式：一鍵重跑的三層（兩支 shell script → 六支 Python 程式 → model.py、blackjack.py）；程式區塊由 `scripts/make_code.py` 產生 |
| `player.html` | PART 5 播放台的單獨頁（給簡報嵌入或離線開）：版面配合 16:9、網址參數 `?b=` `&h=`、鍵盤操作；播放邏輯照抄 `part5-demo.html`，改那邊要一起改這裡 |
| `anim.html`、`learn.html` | PART 1 圖 2（三條式子走一遍）、圖 3（學習規則走一遍）的單獨頁（給簡報嵌入或離線開，單一檔案）：版面配合 16:9、網址參數 `?s=`（圖 2 另有 `&a=`）`&clean=1`、鍵盤操作；分別由 `scripts/make_anim.py`、`make_learn_anim.py` 和 PART 1 的片段一起產生，共用版型在 `scripts/standalone_page.py`，不要手改。**圖 2、圖 3 的文字要改在產生程式裡，直接改頁面會在下次重產時被蓋掉** |

## 目錄

| 路徑 | 內容 |
|---|---|
| `assets/flybj.css` | 共用樣式，與 `../fly_doom/assets/flysimu.css`、`../VFB/assets/vfb.css`、`../LPU/assets/lpu.css`、`../hub/assets/bsc.css` 用同一組設計變數 |
| `assets/p3-*.png`、`p4-*.png` | 真實資料圖，由 `scripts/make_figures.py` 產生 |
| `assets/demo/` | PART 5 的三支影片與逐格資料，由 `scripts/build_demo_data.py` 從 `~/claude_bscai/fly_play_game/demo/` 的錄製結果整理（錄製與畫影片的程式是那邊的 `record_bj.py`、`render_bj.py`） |
| `out/` | **頁面上每個數字的出處**：實跑的 JSON 與 log（`collect_out.py`）、可攜測試（`porttest.json`）、PART 5 的檢查點（`bj_demo_summary.json`）；`out/code_meta.json` 是 PART 6 用的行數與常數，由 `make_code.py` 從原檔抓 |
| `pack/` | 學員下載包的原始檔（`setup_envs.sh`、`blackjack/run_all.sh`、`blackjack/scripts/`、`check.py`、`expected.json`）。2026-10-19 起只跑 21 點：BJ1 下載並切出蕈狀體、BJ2 21 點、BJ3 評分作者大腦檔、X1–X4 |
| `downloads/flyblackjack-code.zip` | `pack/` 打包，附 `SHA256SUMS.txt`。改了 `pack/` 任何檔案都要重打包 |
| `downloads/anim/` | PART 1 圖 2、圖 3 的投影片用圖：`p1anim-*`（九個畫面）、`p1learn-*`（六個畫面）的 PNG 與 SVG，加上 `flyblackjack-anim.zip`、`flyblackjack-learn.zip`（各含自己的單獨頁），由 `scripts/make_anim_images.py` 用無頭 Chrome 截出 |
| `scripts/` | 收資料、產圖、產驗收表、整理影片資料、記錄可攜測試，四道稽核（`page_audit.py`、`content_audit.py`、`svg_audit.py`、`number_audit.py`），以及首頁說明影片的產生器（`video_slides.py` 投影片要點＋旁白稿、`make_video.py`、`video_check.py` 查旁白覆蓋、`video_verify.py` 查影音同步與辨識回填、`make_shots.py` 抽影片畫面） |
| `_notes/` | 修正紀錄。**進 repo，但由 workflow 的 `rm -rf _notes` 擋在網站之外** |

## 重產

```
~/anaconda3/bin/python scripts/collect_out.py     # 實跑資料夾 → out/（保留 porttest.json、demo_data.json、bj_demo_summary.json）
python3 scripts/build_demo_data.py                # fly_play_game/demo → assets/demo/、out/demo_data.json、out/bj_demo_summary.json
python3 scripts/make_player.py                    # assets/demo/data.json → assets/demo/data.js；打包 downloads/player/flyblackjack-player.zip（離線播放台）
python3 scripts/make_anim.py                      # PART 1 圖 2 的片段 ＋ anim.html（單獨頁）
python3 scripts/make_learn_anim.py                # PART 1 圖 3 的片段 ＋ learn.html（單獨頁）
~/anaconda3/bin/python scripts/make_anim_images.py   # anim.html、learn.html → downloads/anim/（PNG、SVG 與兩個 zip）
~/anaconda3/bin/python scripts/make_figures.py    # out/ → assets/*.png
python3 scripts/make_expected.py                  # out/ → pack/expected.json，接著重打包 downloads/
python3 scripts/make_code.py                      # PART 6 的程式區塊：從 pack/ 與本機 clone 的作者 repo（~/claude_bscai/fly_play_game/blackjack/repo）照抄；--check 只比對
bash ~/claude_bscai/porttest_bj/run_porttest.sh downloads/flyblackjack-code.zip   # 可攜測試（解到空資料夾、從零建環境計時、跑 run_all.sh 計時）
python3 scripts/record_porttest.py <測試資料夾> blackjack   # 可攜測試 → out/porttest.json
cd ~/claude_bscai/fly_play_game/blackjack/repo && PYTHONPATH=. ~/anaconda3/bin/python <本資料夾>/scripts/x2_alignment.py   # X2 的原因量測 → out/blackjack/x2_alignment.json
cd ~/claude_bscai/fly_play_game/blackjack/repo && PYTHONPATH=. ~/anaconda3/bin/python <本資料夾>/scripts/part4_extras.py   # X3 沒學過的一致率、X4 機率基準 → out/blackjack/part4_extras.json
python3 scripts/video_check.py                    # 投影片上寫的每一點，旁白有沒有講到
~/.venvs/tts/bin/python scripts/make_video.py     # 重做首頁的說明影片（assets/flybj-overview.mp4 + .vtt + poster.jpg、out/video_meta.json）
~/.venvs/asr/bin/python scripts/video_verify.py   # 影音同步 + 辨識回填（報告在 _video/verify.txt）
python3 scripts/number_audit.py                   # 頁面數字對回 out/
python3 scripts/page_audit.py                     # 標籤平衡、連結與錨點、中英夾雜
```

重打包：`cd pack && rm -f SHA256SUMS.txt && find . -type f | sort | xargs sha256sum > SHA256SUMS.txt && rm -f ../downloads/*.zip && zip -qr ../downloads/flyblackjack-code.zip . && cp SHA256SUMS.txt ../downloads/`

實跑資料夾是本機的 `~/claude_bscai/fly_play_game/blackjack/`，結構與下載包解開後相同。

## 授權

fly-blackjack 與它用的 MaleCNS 整理版（connectome_data_prep）都是開放授權（MIT／CC BY 4.0）；下載包仍不附作者的檔案，由 `run_all.sh` 自己 clone 到固定的 commit。

教學用途，非營利。
