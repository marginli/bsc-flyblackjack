# 蕈狀體學 21 點：程式包

BSC 專題課程〈蕈狀體學 21 點：重現 fly-blackjack〉的下載包。
網頁：https://marginli.github.io/bsc-flyblackjack/ （PART 2 有逐步說明）

這一包只有本課自己寫的程式。被重現的 repo 由 `run_all.sh` 自己 clone，資料也由它下載：

| 被重現的 repo | 固定的版本 | 授權 |
|---|---|---|
| https://github.com/WilliamJones/fly-blackjack | commit 004b2e3 | MIT |

## 兩個指令

```
bash setup_envs.sh              # 建一個 conda 環境（只需一次）
bash blackjack/run_all.sh       # BJ1–BJ3、加做檢查 X1–X4
```

`run_all.sh` 跑完會自動執行 `check.py`，逐項對照 `expected.json`（本課實跑的結果），
最後一行印出「幾項通過、幾項不符」。

## 目錄

| 路徑 | 內容 |
|---|---|
| `setup_envs.sh` | 建環境，套件版本照本課實跑時固定 |
| `check.py`、`expected.json` | 驗收程式與預期值 |
| `blackjack/run_all.sh` | 一鍵重跑 |
| `blackjack/scripts/` | 作者沒有命令列入口的步驟（21 點、評分作者的大腦檔）與加做檢查 X1–X4 |

跑完之後，每一步的終端輸出在 `blackjack/logs/`，數字在 `blackjack/results/`。

## 需要什麼

Linux 或 macOS、conda（Anaconda 或 Miniconda）、git、curl、網路。不需要 GPU。
所有指令都會設 `PYTHONNOUSERSITE=1`，讓家目錄 `~/.local` 裡的套件不會混進環境。

教學用途，非營利。
