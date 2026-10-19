#!/usr/bin/env python3
"""PART 6、PART 7「讀程式」的程式區塊產生器（沿用 ../fly_doom/scripts/make_code.py，改 SOURCES 與頁面清單）。

頁面裡用標記指定要放哪個檔案的哪幾行：

    <!-- code: model.py 131-143 hl=133,137 lab=133:①,137:② -->
    （中間由本程式填入）
    <!-- /code -->

本程式把標記之間換成帶行號的 <pre class="code">，hl 的行加底色，lab 在行號旁放一個標記。
行號與原檔一致。我們自己寫的檔案（pack/）與作者的檔案（fly-blackjack，MIT 授權）都只放講到的段落。

用法
  python3 scripts/make_code.py            重新產生所有區塊，並寫 out/code_meta.json（行數、sha256、常數）
  python3 scripts/make_code.py --check    只比對：頁面上的區塊和原檔現在的內容是否一致（規範第 10 節第 7 條）
"""
import hashlib, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
PAGES = [os.path.join(D, "part6-code.html"), os.path.join(D, "part7-model.html")]
AUTHOR = os.path.expanduser("~/claude_bscai/fly_play_game/blackjack/repo")
COMMIT = "004b2e3"

SOURCES = {
    # 我們自己寫的（下載包裡有）
    "setup_envs.sh":        ("ours",   os.path.join(D, "pack/setup_envs.sh"),                          "setup_envs.sh"),
    "run_all.sh":           ("ours",   os.path.join(D, "pack/blackjack/run_all.sh"),                   "blackjack/run_all.sh"),
    "check.py":             ("ours",   os.path.join(D, "pack/check.py"),                               "check.py"),
    "bj4_forage.py":        ("ours",   os.path.join(D, "pack/blackjack/scripts/bj4_forage.py"),        "blackjack/scripts/bj4_forage.py"),
    "bj4b_forage_s45.py":   ("ours",   os.path.join(D, "pack/blackjack/scripts/bj4b_forage_s45.py"),   "blackjack/scripts/bj4b_forage_s45.py"),
    "bj5_blackjack.py":     ("ours",   os.path.join(D, "pack/blackjack/scripts/bj5_blackjack.py"),     "blackjack/scripts/bj5_blackjack.py"),
    "bj5b_author_brain.py": ("ours",   os.path.join(D, "pack/blackjack/scripts/bj5b_author_brain.py"), "blackjack/scripts/bj5b_author_brain.py"),
    "bj_extra.py":          ("ours",   os.path.join(D, "pack/blackjack/scripts/bj_extra.py"),          "blackjack/scripts/bj_extra.py"),
    # 作者的（fly-blackjack @ 004b2e3，MIT 授權）
    "train.py":      ("author", os.path.join(AUTHOR, "flybrain/train.py"),         "flybrain/train.py"),
    "circuit.py":    ("author", os.path.join(AUTHOR, "flybrain/circuit.py"),       "flybrain/circuit.py"),
    "readout.py":    ("author", os.path.join(AUTHOR, "flybrain/readout.py"),       "flybrain/readout.py"),
    "envs.py":       ("author", os.path.join(AUTHOR, "flybrain/envs.py"),          "flybrain/envs.py"),
    "fetch.py":      ("author", os.path.join(AUTHOR, "flybrain/mb/fetch.py"),      "flybrain/mb/fetch.py"),
    "extract.py":    ("author", os.path.join(AUTHOR, "flybrain/mb/extract.py"),    "flybrain/mb/extract.py"),
    "model.py":      ("author", os.path.join(AUTHOR, "flybrain/mb/model.py"),      "flybrain/mb/model.py"),
    "odour.py":      ("author", os.path.join(AUTHOR, "flybrain/mb/odour.py"),      "flybrain/mb/odour.py"),
    "experiment.py": ("author", os.path.join(AUTHOR, "flybrain/mb/experiment.py"), "flybrain/mb/experiment.py"),
    "tmaze.py":      ("author", os.path.join(AUTHOR, "flybrain/mb/tmaze.py"),      "flybrain/mb/tmaze.py"),
    "embodied.py":   ("author", os.path.join(AUTHOR, "flybrain/mb/embodied.py"),   "flybrain/mb/embodied.py"),
    "blackjack.py":  ("author", os.path.join(AUTHOR, "flybrain/mb/blackjack.py"),  "flybrain/mb/blackjack.py"),
    "arenas.py":     ("author", os.path.join(AUTHOR, "flybrain/body/arenas.py"),   "flybrain/body/arenas.py"),
    "gait.py":       ("author", os.path.join(AUTHOR, "flybrain/body/gait.py"),     "flybrain/body/gait.py"),
}

MARK = re.compile(r'<!-- code: (\S+) (\d+)-(\d+)((?: \w+=\S+)*) -->\n(.*?)<!-- /code -->', re.S)


def read(name):
    kind, path, shown = SOURCES[name]
    with open(path, encoding="utf-8") as f:
        return kind, shown, f.read().split("\n")


def colour(line):
    """註解上色：shell 與 python 都用 #。字串裡若有 #（例如 "# leg order"）會被誤判，這些檔案裡講到的段落沒有。"""
    e = html.escape(line)
    m = re.search(r'(^|\s)(#.*)$', e)
    if m and not e.lstrip().startswith("#!"):
        return e[:m.start(2)] + '<span class="cm">' + e[m.start(2):] + '</span>'
    if e.lstrip().startswith("#"):
        return '<span class="cm">' + e + '</span>'
    return e


def block(name, a, b, opts):
    kind, shown, lines = read(name)
    assert 1 <= a <= b <= len(lines), (name, a, b, len(lines))
    hl = set()
    for part in opts.get("hl", "").split(","):
        if not part:
            continue
        if "-" in part:
            x, y = part.split("-"); hl.update(range(int(x), int(y) + 1))
        else:
            hl.add(int(part))
    lab = dict(p.split(":") for p in opts.get("lab", "").split(",") if p)
    out = []
    for n in range(a, b + 1):
        ln = f'<span class="ln">{n:>3}</span>'
        tag = lab.get(str(n))
        mk = f'<span class="mk">{tag}</span>' if tag else '<span class="mk"> </span>'
        body = colour(lines[n - 1])
        row = f"{ln}{mk}{body}"
        # 標記行是 display:block 的 span，本身就會換行；後面不能再接 \n，否則多一個空行
        out.append(f'<span class="hl">{row}</span>' if n in hl else row + "\n")
    code = "".join(out).rstrip("\n")
    if kind == "ours":
        cap = f'下載包的 <code>{shown}</code> 第 {a}–{b} 行'
    else:
        cap = (f'fly-blackjack 的 <code>{shown}</code> 第 {a}–{b} 行（commit <code>{COMMIT}</code>，MIT 授權；'
               f'run_all.sh 會把整個 repo 放在 <code>blackjack/repo/</code>，同一個檔案在那裡）')
    return (f'<figure class="code"><pre class="code">{code}</pre>'
            f'<figcaption class="figsrc">{cap}</figcaption></figure>\n')


def render(src):
    def sub(m):
        name, a, b, optstr, _ = m.groups()
        opts = dict(kv.split("=", 1) for kv in optstr.split())
        head = f'<!-- code: {name} {a}-{b}{optstr} -->\n'
        return head + block(name, int(a), int(b), opts) + '<!-- /code -->'
    return MARK.sub(sub, src)


def grab(name, pattern, conv=float):
    txt = open(SOURCES[name][1], encoding="utf-8").read()
    return {k: conv(v) for k, v in re.findall(pattern, txt, flags=re.M)}


def meta():
    files = {}
    for name, (kind, path, shown) in SOURCES.items():
        raw = open(path, "rb").read()
        files[name] = {"kind": kind, "path": shown, "lines": raw.decode("utf-8").count("\n") + (0 if raw.endswith(b"\n") else 1),
                       "sha256_8": hashlib.sha256(raw).hexdigest()[:8]}
    # 頁面上會以文字引用的常數，直接從原始碼抓，讓 number_audit 對得到（它掃 out/ 底下所有 JSON 的值）
    c = {}
    c["model"] = grab("model.py", r'^([A-Z_]+) = ([\d.]+)')
    c["odour"] = grab("odour.py", r'^([A-Z_]+) = ([\d.]+)')
    c["tmaze"] = grab("tmaze.py", r'^([A-Z_]+) = ([\d.]+)')
    c["readout"] = grab("readout.py", r'^([A-Z_]+) = ([\d.]+)')
    c["embodied"] = grab("embodied.py", r'^([A-Z_]+) = ([\d.]+)')
    c["envs"] = grab("envs.py", r'^    ([A-Z_]+) = ([\d.]+)')
    c["fetch_files_bytes"] = grab("fetch.py", r'"([\w.]+)": ([\d_]+),', lambda v: int(v.replace("_", "")))
    c["fetch_expected"] = grab("fetch.py", r'"(\w+)": ([\d_]+),\n', lambda v: int(v.replace("_", "")))
    cp = open(SOURCES["circuit.py"][1], encoding="utf-8").read()
    m = re.search(r'gain: float = ([\d.]+), leak: float = ([\d.]+), steps: int = (\d+)', cp)
    c["circuit"] = {"gain": float(m.group(1)), "leak": float(m.group(2)), "steps": int(m.group(3))}
    tp = open(SOURCES["train.py"][1], encoding="utf-8").read()
    m = re.search(r'def train\(seed=(\d+), generations=(\d+), population=(\d+), elites=(\d+),\n\s+episode_seconds=([\d.]+), courses=(\d+)', tp)
    c["train"] = {"seed": int(m.group(1)), "generations": int(m.group(2)), "population": int(m.group(3)), "elites": int(m.group(4)),
                  "episode_seconds": float(m.group(5)), "courses": int(m.group(6)),
                  "sigma0": 0.8, "champion_sd": 0.7, "sigma_floor": 0.07, "keep": 0.3, "move": 0.7,
                  "validation_seeds": [1100001, 1100002, 1100003, 1100004], "benchmark_start": 2100001, "benchmark_n": 50,
                  "untrained_seed": 7, "random_seed": 11, "course_seed_max": 900000, "benchmark_last": 2100050}
    ep = open(SOURCES["embodied.py"][1], encoding="utf-8").read()
    m = re.search(r'def train\(seed=(\d+), generations=(\d+), population=(\d+), elites=(\d+),\n\s+seconds=([\d.]+), courses=(\d+)', ep)
    c["embodied_train"] = {"seed": int(m.group(1)), "generations": int(m.group(2)), "population": int(m.group(3)), "elites": int(m.group(4)),
                           "seconds": float(m.group(5)), "courses": int(m.group(6)), "validation_seeds": [1100001, 1100002, 1100003],
                           "evaluate_seed0": 2100001, "shock_cooldown": 1.5, "spot_r": [120, 190], "spot_tries": 40,
                           "sense_gain": [12.0, 60.0], "forage_default_seconds": 40.0}
    bp = open(SOURCES["blackjack.py"][1], encoding="utf-8").read()
    c["blackjack_width"] = {k: int(v) for k, v in re.findall(r'"(\w+)": (\d+)', bp.split("WIDTH = ")[1].split("\n")[0])}
    m = re.search(r'def __init__\(self, seed=(\d+), lr=([\d.]+), decay=([\d.]+), explore=([\d.]+),\n\s+explore_floor=([\d.]+), explore_halflife=(\d+)', bp)
    c["blackjack_player"] = {"seed": int(m.group(1)), "lr": float(m.group(2)), "decay": float(m.group(3)), "explore": float(m.group(4)),
                             "explore_floor": float(m.group(5)), "explore_halflife": int(m.group(6)),
                             "situation_seed": 20260914, "ordered_overlap": 0.55, "action_amp": 1.3, "pn_uniform": [0.7, 1.0],
                             "strength_min": 0.15, "strength_div": 2.0, "block": 2000, "session_hands_default": 20000,
                             "chart_cells": 260, "hard_totals": 17, "soft_totals": 9, "upcards": 10, "blackjack_pays": 1.5}
    c["arena"] = {"ARENA": 220.0, "side": 440.0, "DT": 1 / 60, "CONTROL_EVERY": 2, "N_OBS": 8}
    c["envs"]["speed0"], c["envs"]["speed_max"], c["envs"]["TICK"] = 200.0, 620.0, 1 / 60
    c["walker"] = {"MAX_SPEED": 22.0, "MAX_TURN": 4.2, "RESPONSE": 0.28, "N_ACTIONS": 5, "speeds": [0.0, 1.0, 0.75, -0.6]}
    c["experiment"] = {"seeds": 12, "trials": 20, "odours": 8, "glomeruli": 83}
    c["tmaze"]["flies"] = 100
    c["readout"]["dino_params"] = 16 * 12 + 12 + 12 * 3 + 3
    c["readout"]["forage_params"] = 16 * 12 + 12 + 12 * 5 + 5
    c["derived"] = {"kc_active": round(1200 * c["model"]["KC_SPARSITY"]), "mb_hz": 30 / c["embodied"]["MB_EVERY"],
                    "control_hz": 30, "physics_hz": 60, "dino_decision_hz": 30, "byte_max": 255, "live_kc_last_rank": 3810, "tick": 1/60}
    return {"author_commit": COMMIT, "files": files, "constants": c,
            "ours_total_lines": sum(v["lines"] for v in files.values() if v["kind"] == "ours"),
            "author_total_lines": sum(v["lines"] for v in files.values() if v["kind"] == "author")}


def main():
    total = 0
    for page in PAGES:
        if not os.path.exists(page):
            continue
        src = open(page, encoding="utf-8").read()
        new = render(src)
        n = len(MARK.findall(src))
        if "--check" in sys.argv:
            if new != src:
                print(f"[程式區塊] {os.path.basename(page)} 的區塊與原檔不一致，重跑 scripts/make_code.py"); return 1
            print(f"=== {os.path.basename(page)}：{n} 個程式區塊對回原檔，全部一致")
        else:
            open(page, "w", encoding="utf-8").write(new)
            print(f"{os.path.basename(page)}：產生 {n} 個區塊")
        total += n
    if "--check" not in sys.argv:
        os.makedirs(os.path.join(D, "out"), exist_ok=True)
        json.dump(meta(), open(os.path.join(D, "out/code_meta.json"), "w"), indent=1, ensure_ascii=False)
        print(f"共 {total} 個區塊；out/code_meta.json 已更新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
