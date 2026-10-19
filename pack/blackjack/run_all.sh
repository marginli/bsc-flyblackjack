#!/usr/bin/env bash
# fly-blackjack 的 21 點實驗一鍵重跑：BJ1–BJ3 ＋ 加做檢查 X1–X4。用法：bash run_all.sh（本課實測時間見 PART 2）
# 需要先跑過上一層的 setup_envs.sh。每步的終端輸出寫到 logs/，數字寫到 results/，最後由 ../check.py 驗收。
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$(conda info --base)/envs/flyplay_bj/bin/python"
export PYTHONNOUSERSITE=1 PYTHONPATH=.
cd "$HERE"
[ -d repo ] || git clone -q https://github.com/WilliamJones/fly-blackjack.git repo
git -C repo checkout -q 004b2e3e9ccb742f83c5bdc2717c97f5a64b420f
mkdir -p logs results
cd repo
echo "BJ1 下載並切出蕈狀體（下載約 107 MB）"; $PY -m flybrain.mb.fetch > ../logs/bj1_fetch.log 2>&1
for i in 1 2; do $PY -m flybrain.mb.extract > ../logs/bj1_extract_run$i.log 2>&1; md5sum data/mb_circuit.npz; done | tee ../logs/bj1_md5.txt
echo "BJ2 21 點 30,000 手 × 4 個條件 × 3 個種子"; $PY ../scripts/bj2_blackjack.py 30000 0 1 2 > ../logs/bj2_blackjack.log 2>&1
echo "BJ3 評分作者附的大腦";     $PY ../scripts/bj3_author_brain.py > ../logs/bj3_author_brain.log 2>&1
echo "加做檢查 X1–X4";            $PY ../scripts/bj_extra.py > ../logs/bj_extra.log 2>&1
cd "$HERE"; "$PY" ../check.py blackjack
