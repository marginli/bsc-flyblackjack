"""PART 1 互動圖（圖 2、圖 3）單獨頁的共用版型：給簡報嵌入（PowerPoint 增益集）或離線用瀏覽器開。
make_anim.py 與 make_learn_anim.py 用它把頁面裡同一份 SVG、按鈕、步驟文字與腳本包成單一 html 檔。"""

TEMPLATE = '''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<link rel="icon" href="data:,">
<title>%TITLE%｜蕈狀體學 21 點</title>
<style>
/* %DOC%：給簡報嵌入（PowerPoint 增益集）或離線用瀏覽器全螢幕開。由 %GEN% 產生，不要手改。
   單一檔案、不依賴其他檔，file:// 也能用。版面照視窗大小縮放，16:9 剛好填滿。
   網址參數：%PARAMS% */
:root{--ink:#1b2733;--soft:#5a6b7b;--faint:#8b98a5;--border:#e4e8ee;--panel:#f7f8fa;--accent:#2563eb;--accent-soft:#eef3fe;--fs:clamp(11px,1.05vw,24px)}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{background:#fff;color:var(--ink);font-size:var(--fs);line-height:1.6;
  font-family:-apple-system,"Segoe UI","Noto Sans TC","Microsoft JhengHei","PingFang TC",Roboto,Helvetica,Arial,sans-serif;
  display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:.5em;padding:.7em 1em;overflow:hidden}
.anim-ctl{display:flex;flex-wrap:wrap;align-items:center;gap:.5em}
.name{font-weight:700;margin-right:.6em}
.anim-btn,.anim-act,.pbtn{font:inherit;font-size:.95em;padding:.2em .8em;border:1px solid var(--border);border-radius:8px;background:var(--panel);color:var(--ink);cursor:pointer}
.anim-btn:disabled{opacity:.4;cursor:default}
.anim-btn:hover:not(:disabled),.anim-act:hover,.pbtn:hover{border-color:var(--accent)}
.anim-btn:focus-visible,.anim-act:focus-visible,.pbtn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.anim-step{font-weight:700;color:var(--accent);min-width:6em;text-align:center}
.anim-acts{color:var(--soft);display:flex;gap:.35em;align-items:center}
.anim-act.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.right{margin-left:auto;display:flex;gap:.4em;align-items:center}
.pbtn[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.stage{min-height:0;display:flex;justify-content:center;align-items:center}
.anim-svg{display:block;height:100%;width:auto;max-width:100%;border:1px solid var(--border);border-radius:8px;background:#fff}
.desc{display:none;max-height:26vh;overflow:auto;border-top:1px solid var(--border);padding-top:.3em}
body.showdesc .desc{display:block}
.anim-steps{margin:0;padding:0;list-style:none;font-size:.95em}
.anim-steps li{display:none;padding:.2em .7em;border-left:3px solid var(--accent);background:var(--accent-soft)}
.anim-steps li.on{display:block}
.anim-steps li b{color:var(--ink)}
.desc .hint{color:var(--soft);margin:0}
body.clean{padding:0;grid-template-rows:minmax(0,1fr)}
body.clean .anim-ctl,body.clean .desc{display:none!important}
body.clean .anim-svg{border:0;border-radius:0}
</style>
</head>
<body>
%CTL%
<div class="stage">
%SVG%
</div>
<div class="desc" id="desc">
  <p class="hint" id="descHint">%HINT%</p>
  %OL%
</div>
%SCRIPT%
<script>
(function(){
  var $ = function(id){ return document.getElementById(id); };
  var next = $("%P%Next"), prev = $("%P%Prev"), q = new URLSearchParams(location.search);
  var curStep = function(){ var t = $("%P%Step").textContent; var m = t.match(/第 (\\d) 步/); return m ? +m[1] : 0; };
  function syncHint(){ $("descHint").style.display = curStep()===0 ? "block" : "none"; }
  next.addEventListener("click", syncHint); prev.addEventListener("click", syncHint);
  if(q.get("clean")==="1") document.body.classList.add("clean");
  if(q.get("d")==="1") document.body.classList.add("showdesc");
  var s0 = Math.max(0, Math.min(%N%, parseInt(q.get("s")||"0",10)||0));
  for(var i=0;i<s0;i++) next.click();
  var a0 = q.get("a"), btn = a0 && document.querySelector('#%P%Acts .anim-act[data-act="'+a0+'"]');
  if(btn && s0===%N%) btn.click();
  syncHint();
  var dBtn = $("%P%Desc");
  dBtn.onclick = function(){ var on = document.body.classList.toggle("showdesc"); dBtn.setAttribute("aria-pressed", on); };
  dBtn.setAttribute("aria-pressed", document.body.classList.contains("showdesc"));
  var fs = $("%P%Full"), de = document.documentElement;
  if(!(document.fullscreenEnabled||document.webkitFullscreenEnabled)) fs.style.display = "none";
  fs.onclick = function(){ if(document.fullscreenElement||document.webkitFullscreenElement)(document.exitFullscreen||document.webkitExitFullscreen).call(document); else (de.requestFullscreen||de.webkitRequestFullscreen).call(de); };
  document.addEventListener("keydown", function(e){
    if(e.altKey||e.ctrlKey||e.metaKey) return;
    var k = e.key;
    if(k==="ArrowRight"||k==="PageDown"||k===" "){ e.preventDefault(); if(!next.disabled) next.click(); }
    else if(k==="ArrowLeft"||k==="PageUp"){ e.preventDefault(); if(!prev.disabled) prev.click(); }
    else if(k==="Home"){ e.preventDefault(); while(!prev.disabled) prev.click(); }
    else if("123".indexOf(k)>=0 && k.length===1 && document.querySelectorAll("#%P%Acts .anim-act").length){ while(!next.disabled) next.click(); document.querySelectorAll("#%P%Acts .anim-act")[+k-1].click(); }
    else if(k==="d"||k==="D") dBtn.click();
    else if(k==="f"||k==="F") fs.click();
  });
})();
</script>
</body>
</html>
'''


def build(*, prefix, box_id, name, title, doc, gen, params, hint, n_steps, ctl, svg, ol, script):
    """prefix：按鈕 id 的開頭（anim、lrn）；box_id：頁面裡包住整張圖的 div id（p1anim、p1learn）。"""
    c = (ctl.replace(f'<div class="anim" id="{box_id}">\n', f'<div id="{box_id}" style="display:contents">\n')
         .replace('  <div class="anim-ctl">\n', f'  <div class="anim-ctl">\n    <span class="name">{name}</span>\n', 1))
    k = c.rindex("\n  </div>\n")
    c = (c[:k] + f'\n    <span class="right"><button type="button" class="pbtn" id="{prefix}Desc" aria-pressed="false">說明</button>'
         f'<button type="button" class="pbtn" id="{prefix}Full">全螢幕</button></span>\n  </div>\n</div>' + c[k + len("\n  </div>\n"):])
    assert c.count(f'id="{prefix}Desc"') == 1
    # 單獨頁裡 SVG 不在 box_id 底下，腳本的選擇器改成直接找 .anim-svg
    s = script.replace(f'document.querySelector("#{box_id} .anim-svg")', 'document.querySelector(".anim-svg")')
    assert s != script
    out = TEMPLATE
    for key, v in (("%TITLE%", title), ("%DOC%", doc), ("%GEN%", gen), ("%PARAMS%", params), ("%HINT%", hint),
                   ("%N%", str(n_steps)), ("%P%", prefix), ("%CTL%", c), ("%SVG%", svg), ("%OL%", ol), ("%SCRIPT%", s)):
        out = out.replace(key, v)
    return out
