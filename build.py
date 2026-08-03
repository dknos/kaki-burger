"""Assemble BORGIR NIGHT into one self-contained page."""
import json
import re
import os

from orders import CUSTOMERS, INGREDIENTS, MOLD_LINE, RANKS, SERVICES

# the day runs breakfast -> lunch -> dinner, in clock order inside each service
_svc = {v['key']: i for i, v in enumerate(SERVICES)}
CUSTOMERS = sorted(CUSTOMERS, key=lambda c: (_svc[c['service']], c['clock']))

HERE = os.path.dirname(os.path.abspath(__file__))
ART = json.load(open(os.path.join(HERE, 'art', 'atlas.json')))
CELL_W, CELL_H = ART['cell_w'], ART['cell_h']


def scene(name):
    return open(os.path.join(HERE, 'scenes', name)).read()


scenes = [('scene-burger', scene('burger.css'))]
for c in CUSTOMERS:
    scenes.append((f'scene-{c["key"]}', scene(f'cust-{c["key"]}.css')))
bundle = open(os.path.join(HERE, 'vendor', 'popkorn.bundle.js')).read()
for name, text in scenes:
    assert '</script' not in text, name
assert '</script' not in bundle

KEYS = '1234567890-='          # same order the keyboard handler uses
rack = ''.join(
    f'<button class="ing" data-ing="{key}" style="--n:{i}" '
    f'title="{label}"><b>{KEYS[i] if i < len(KEYS) else ""}</b>'
    f'<span>{label}</span></button>'
    for i, (key, label) in enumerate(INGREDIENTS))

MARQUEE = ('&#9734; WELCOME TO BORGIR NIGHT &#9734; YOU HAVE THE GRILL ALL WEEKEND &#9734; '
           'FRIDAY &#183; SATURDAY &#183; SUNDAY NIGHT &#9734; NINE KAKIS &#183; NINE TICKETS &#9734; '
           'GET IT EXACTLY RIGHT AND SHE GOES UP ON THE WALL &#9734; '
           'NO POPUPS &#183; NO DOWNLOADS &#183; JUST BURGERS &nbsp;&nbsp;')

DATA = json.dumps({
    'customers': [{k: v for k, v in c.items()} for c in CUSTOMERS],
    'ingredients': [{'id': k, 'label': l} for k, l in INGREDIENTS],
    'ranks': [{'at': a, 'title': t, 'blurb': b} for a, t, b in RANKS],
    'services': SERVICES,
    'mold_line': MOLD_LINE,
    'cell': [CELL_W, CELL_H],
}, ensure_ascii=False)

HTML = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Borgir Night — breakfast, lunch and dinner</title>
<link rel="icon" type="image/png" sizes="64x64" href="favicon.png">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<meta name="description" content="You have the grill all weekend. Nine pixel-art Kakis come in one at a time, each with a different idea of what a burger is.">
<meta property="og:type" content="website">
<meta property="og:title" content="Borgir Night">
<meta property="og:description" content="You have the grill all weekend: Friday, Saturday and Sunday night, three Kakis each night, nine in all. Every one wants something slightly different.">
<meta property="og:url" content="https://dknos.github.io/kaki-burger/">
<meta property="og:image" content="https://dknos.github.io/kaki-burger/og-weekend.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="672">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#c9dcfb">
<style>
@font-face {{ font-family: 'Pixelify'; src: url('fonts/PixelifySans-400.woff2') format('woff2');
              font-weight: 400; font-display: swap; }}
@font-face {{ font-family: 'Pixelify'; src: url('fonts/PixelifySans-700.woff2') format('woff2');
              font-weight: 700; font-display: swap; }}
@font-face {{ font-family: 'Silkscreen'; src: url('fonts/Silkscreen-400.woff2') format('woff2');
              font-weight: 400; font-display: swap; }}
@font-face {{ font-family: 'Silkscreen'; src: url('fonts/Silkscreen-700.woff2') format('woff2');
              font-weight: 700; font-display: swap; }}
@font-face {{ font-family: 'VT323'; src: url('fonts/VT323-400.woff2') format('woff2');
              font-weight: 400; font-display: swap; }}
:root {{
  --ink: #3d2445;          /* every border and every dark letter */
  --paper: #fff4dc;        /* the cabinet */
  --paper2: #ffeedb;       /* strips inside it */
  --sky: #c9dcfb;
  --shadow: #a8b6e0;
  --pink: #ff8fc0;
  --hot: #ff4f95;
  --yellow: #ffcf5c;
  --blue: #9ecbff;
  --mint: #a8ecba;
  --lcd: #9ce8b0;
  --lcdbg: #1a1026;
  --dim: #8b7aa1;
  --plum: #7c2a52;
  --pix: 'Pixelify', ui-monospace, monospace;
  --silk: 'Silkscreen', ui-monospace, monospace;
  --vt: 'VT323', ui-monospace, monospace;
  --mono: var(--silk);
  --cw: {CELL_W}px;
  --ch: {CELL_H}px;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--sky) url('art/tile-sky.png'); color: var(--ink);
  font: 19px/1.5 var(--vt);
  display: flex; flex-direction: column; align-items: center;
  min-height: 100vh; padding: 22px 14px 40px; overflow-x: hidden;
}}
/* The player's canvas lives in a shadow root, so a plain `canvas` rule here never
   reaches it and it scaled with the browser's default smoothing — that is the
   thin ring that showed up around every closed eye at 125% zoom, a bilinear
   resample of the lid's hard alpha edge. image-rendering inherits, so setting it
   on the host is what actually gets in. */
canvas, popkorn-player {{ image-rendering: pixelated; }}
button {{ font: inherit; color: inherit; cursor: pointer; }}
a {{ color: var(--hot); }}
@keyframes marq {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}
@keyframes twinkle {{ 0%, 100% {{ opacity: .15; }} 50% {{ opacity: 1; }} }}
@keyframes sparkfade {{
  from {{ opacity: 1; transform: translateY(0) scale(1); }}
  to {{ opacity: 0; transform: translateY(-16px) scale(.4); }}
}}

/* ---- the shell -------------------------------------------------------- */
.star {{ position: fixed; width: 3px; height: 3px; background: #fff; z-index: 0;
        box-shadow: 0 -3px 0 currentColor, 0 3px 0 currentColor,
                    -3px 0 0 currentColor, 3px 0 0 currentColor;
        color: #fff; animation: twinkle 2.8s infinite; pointer-events: none; }}
.marquee {{
  border: 3px solid var(--ink); background: var(--yellow); overflow: hidden;
  margin-bottom: 14px; box-shadow: 5px 5px 0 var(--shadow); position: relative; z-index: 1;
}}
.marquee div {{ display: inline-block; white-space: nowrap; padding: 8px 0;
               font: 400 10px/1 var(--silk); letter-spacing: .1em;
               animation: marq 26s linear infinite; }}

/* the cabinet is exactly as wide as the two canvases, so every panel lines up */
.cab {{
  width: calc(var(--sw, 640px) + var(--bw, 240px) + 8px); max-width: 100%;
  border: 4px solid var(--ink); background: var(--paper);
  box-shadow: 10px 10px 0 var(--shadow); position: relative; z-index: 1;
}}
.marquee {{ width: calc(var(--sw, 640px) + var(--bw, 240px) + 8px); max-width: 100%; }}

.chrome {{ display: flex; align-items: center; gap: 11px; padding: 8px 13px;
          background: var(--pink); border-bottom: 4px solid var(--ink); }}
.chrome .dots {{ display: flex; gap: 5px; }}
.chrome .dots i {{ width: 11px; height: 11px; border: 2px solid var(--ink); display: block; }}
.chrome img {{ width: 26px; height: 26px; image-rendering: pixelated; }}
.chrome b {{ font: 700 21px/1 var(--pix); letter-spacing: .04em;
            text-shadow: 2px 2px 0 rgba(255,255,255,.5); white-space: nowrap; }}
.chrome .tag {{ flex: 1; min-width: 0; overflow: hidden; white-space: nowrap;
               font: 400 8px/1 var(--silk); color: var(--plum); }}
.lcd {{ background: var(--lcdbg); color: var(--lcd); border: 3px solid var(--ink);
       padding: 1px 9px 0; font: 21px/1.3 var(--vt); letter-spacing: .06em; }}

.top {{
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  background: var(--paper2); border-bottom: 4px solid var(--ink); padding: 7px 13px;
  font: 400 9px/1 var(--silk); letter-spacing: .1em; text-transform: uppercase;
}}
.top .sp {{ margin-left: auto; }}
.pips {{ display: flex; gap: 4px; }}
.pips b {{ display: flex; gap: 2px; margin-right: 8px; }}
.pips b:last-child {{ margin-right: 0; }}
.pips i {{ display: block; font: 13px/1 var(--vt); color: #d9cdea; font-style: normal; }}
.pips i::before {{ content: '♥'; }}
.pips i.done {{ color: var(--hot); }}
.pips i.now {{ color: var(--yellow); }}
#svc-now {{ background: var(--yellow); border: 2px solid var(--ink); padding: 4px 8px 3px;
           font-weight: 700; letter-spacing: .12em; }}
#svc-now::before {{ content: '☆ '; }}
#who-n {{ color: var(--dim); }}
.tipbox {{ background: #fff; border: 3px solid var(--ink); padding: 1px 8px 0;
          font: 19px/1.2 var(--vt); }}

/* ---- the counter ------------------------------------------------------ */
.stagerow {{ display: flex; background: var(--lcdbg); border-bottom: 4px solid var(--ink);
            position: relative; }}
.scene {{ position: relative; flex: none; }}
.scene popkorn-player {{ display: block; width: var(--sw); height: calc(var(--sw) * 0.5625); }}
/* the CRT layer sits over the canvas: it must never eat a click, because
   poking her is a click straight through to the popkorn machine */
.scene::after {{
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(rgba(255,255,255,.10) 0 1px, transparent 1px 3px);
}}
.livetag {{ position: absolute; left: 8px; top: 8px; z-index: 2; pointer-events: none;
           background: var(--pink); border: 2px solid var(--ink); padding: 3px 7px 2px;
           font: 400 8px/1 var(--silk); letter-spacing: .1em; text-transform: uppercase; }}
.side {{ flex: none; border-left: 4px solid var(--ink); background: #2a1b3d;
        position: relative; display: flex; flex-direction: column; }}
.side popkorn-player {{ display: block; width: var(--bw); height: calc(var(--bw) * 1.5); }}
.side .empty {{ position: absolute; inset: 0; display: grid; place-items: center; z-index: 2;
                font: 21px/1 var(--vt); color: #6f5a8c; pointer-events: none; }}
.side .cap {{ position: absolute; left: 0; right: 0; top: 6px; text-align: center; z-index: 2;
             font: 400 8px/1 var(--silk); letter-spacing: .18em; color: #b9a7d6;
             text-transform: uppercase; pointer-events: none; }}

/* ---- what she says ---------------------------------------------------- */
.say {{ padding: 14px 15px 16px; display: flex; gap: 14px; align-items: flex-start;
       border-bottom: 4px solid var(--ink); min-height: 148px; }}
.say .col {{ flex: 1; min-width: 0; }}
.who {{ display: inline-block; background: var(--hot); color: #fff; border: 3px solid var(--ink);
       padding: 3px 9px 2px; font: 400 9px/1 var(--silk); letter-spacing: .14em;
       text-transform: uppercase; }}
.line {{ margin: 10px 0 0; font-size: 25px; line-height: 1.32; min-height: 2.6em; }}
.aside {{ margin: 2px 0 0; color: var(--plum); font-style: italic; font-size: 20px;
         min-height: 1.4em; }}
.ticket {{
  flex: none; width: 214px; background: #fff; border: 3px solid var(--ink);
  box-shadow: 4px 4px 0 var(--shadow); padding: 9px 11px 12px;
  font: 20px/1.25 var(--vt); text-transform: uppercase;
}}
.ticket::before {{ content: '·· ticket ··'; display: block; text-align: center;
                  font: 400 8px/1 var(--silk); letter-spacing: .16em; color: var(--dim);
                  border-bottom: 2px dashed #cbb9dd; padding-bottom: 7px; margin-bottom: 7px; }}
.ticket:empty {{ visibility: hidden; }}
.verdict {{ margin-top: 9px; font: 400 10px/1.4 var(--silk); letter-spacing: .14em;
           text-transform: uppercase; }}
.verdict.perfect {{ color: #2e8b4f; }}
.verdict.okay {{ color: #b8791b; }}
.verdict.wrong {{ color: var(--hot); }}

/* ---- the rack --------------------------------------------------------- */
.rack {{ display: grid; grid-template-columns: repeat(13, 1fr); gap: 5px; padding: 12px;
        border-bottom: 4px solid var(--ink); }}
.ing {{
  width: 100%; height: 62px; padding: 0; border: 3px solid var(--ink); background: #fff;
  background-image: var(--atlas);
  background-repeat: no-repeat;
  background-size: calc(var(--cw) * 13 * 0.52) calc(var(--ch) * 0.52);
  background-position: calc(var(--n) * var(--cw) * -0.52) 4px;
  image-rendering: pixelated; position: relative;
}}
.ing b {{ position: absolute; left: -1px; top: -1px; background: var(--yellow);
         border: 2px solid var(--ink); padding: 0 2px; font: 400 7px/1.5 var(--silk); }}
.ing span {{ position: absolute; left: 0; right: 0; bottom: 0; overflow: hidden;
            font: 400 6px/1.8 var(--silk); text-transform: uppercase; white-space: nowrap;
            background: var(--paper2); border-top: 2px solid var(--ink); color: var(--ink); }}
.ing:hover {{ background-color: var(--mint); }}
.ing:active {{ transform: translate(1px, 1px); }}
.ing:disabled {{ opacity: .4; cursor: not-allowed; }}
.ing:focus-visible {{ outline: 3px solid var(--hot); outline-offset: 2px; }}
.acts {{ grid-column: 1 / -1; display: flex; gap: 10px; justify-content: flex-end;
        align-items: center; margin-top: 4px; }}
.acts .rule {{ margin-right: auto; font: 400 8px/1.6 var(--silk); color: var(--dim);
              letter-spacing: .1em; text-transform: uppercase; }}

.btn {{
  border: 3px solid var(--ink); background: #fff; padding: 9px 15px 8px;
  font: 400 11px/1 var(--silk); letter-spacing: .12em; text-transform: uppercase;
  box-shadow: 4px 4px 0 var(--shadow);
}}
.btn:hover {{ background: var(--mint); }}
.btn:active {{ transform: translate(2px, 2px); box-shadow: 2px 2px 0 var(--shadow); }}
.btn.go {{ background: var(--hot); color: #fff; box-shadow: 5px 5px 0 var(--ink); }}
.btn.go:hover {{ background: var(--pink); }}
/* keep a disabled button looking like the button it is: dropping .go's pink
   here left white letters on a white box, which read as an empty panel */
.btn:disabled {{ opacity: .45; cursor: not-allowed; }}
.btn:disabled:hover {{ background: #fff; }}
.btn.go:disabled:hover {{ background: var(--hot); }}
.btn.mini {{ padding: 5px 8px 4px; font-size: 9px; box-shadow: 3px 3px 0 var(--shadow); }}
.hint {{ font: 400 8px/2.2 var(--silk); color: var(--dim); letter-spacing: .1em;
        padding: 9px 13px; border-bottom: 4px solid var(--ink); text-transform: uppercase;
        display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
.hint kbd {{ background: #fff; border: 2px solid var(--ink); color: var(--ink);
            padding: 2px 5px 1px; font: inherit; }}
.hint .pokehint {{ margin-left: auto; color: var(--plum); }}

/* ---- screens ---------------------------------------------------------- */
.end {{ text-align: center; padding: 44px 24px; }}
.end h2 {{ font: 700 clamp(30px, 6vw, 54px)/1 var(--pix); margin: 0 0 14px; color: var(--hot);
          text-shadow: 4px 4px 0 var(--yellow), 7px 7px 0 var(--ink); letter-spacing: .02em; }}
.end p {{ max-width: 40ch; margin: 0 auto 10px; font-size: 22px; }}
.end .sub {{ color: var(--plum); font-size: 19px; }}
#title h2 {{ line-height: 1.05; }}
#title h2 .two {{ color: var(--yellow); text-shadow: 4px 4px 0 var(--hot), 7px 7px 0 var(--ink); }}
#svc-hours {{ display: inline-block; background: var(--lcdbg); color: var(--lcd);
             border: 3px solid var(--ink); padding: 2px 12px 0; font-size: 21px;
             letter-spacing: .12em; }}
.burg {{ width: 70px; image-rendering: pixelated; margin-bottom: 6px; }}

.gallery {{ padding: 15px; border-bottom: 4px solid var(--ink); background: var(--paper2); }}
.gal-top {{ display: flex; align-items: center; gap: 13px; flex-wrap: wrap;
           font: 400 9px/1.6 var(--silk); letter-spacing: .12em; text-transform: uppercase;
           color: var(--dim); margin-bottom: 12px; }}
.gal-top b {{ color: var(--ink); font-size: 12px; letter-spacing: .18em; }}
.gal-top .btn {{ margin-left: auto; }}
.gal-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }}
.card {{ border: 3px solid var(--ink); background: #fff; padding: 5px; text-align: center;
        box-shadow: 3px 3px 0 var(--shadow); }}
.card img {{ width: 100%; display: block; image-rendering: auto; }}
.card .nm {{ font: 400 8px/2 var(--silk); letter-spacing: .1em; text-transform: uppercase;
            color: var(--dim); }}
.card.got {{ border-color: var(--hot); cursor: pointer; }}
.card.got .nm {{ color: var(--hot); }}
.card .lock {{ aspect-ratio: 1; display: grid; place-items: center; color: #c9bcd8;
              font: 700 30px/1 var(--pix); background: var(--paper2); }}
.lightbox {{ position: fixed; inset: 0; background: rgba(29,17,40,.9); display: grid;
            place-items: center; z-index: 40; padding: 20px; }}
.lightbox img {{ image-rendering: auto; max-width: min(512px, 90vw); width: 512px;
                border: 4px solid var(--yellow); }}
.lightbox p {{ text-align: center; max-width: 42ch; margin: 14px auto 0; color: var(--paper);
              font-size: 21px; }}
.hidden {{ display: none !important; }}

/* ---- under the cabinet ------------------------------------------------ */
.rainbow {{ height: 7px; width: calc(var(--sw, 640px) + var(--bw, 240px) + 8px); max-width: 100%;
           margin: 16px 0 14px; border: 2px solid var(--ink); position: relative; z-index: 1;
           background: linear-gradient(90deg, var(--hot) 0 20%, var(--yellow) 0 40%,
                       var(--mint) 0 60%, var(--blue) 0 80%, #c9a7ff 0 100%); }}
.foot {{ text-align: center; position: relative; z-index: 1; }}
.badges {{ display: flex; gap: 9px; justify-content: center; flex-wrap: wrap; }}
.badge {{ width: 88px; height: 31px; border: 2px solid var(--ink); display: grid;
         place-items: center; font: 400 6px/1.5 var(--silk); letter-spacing: .06em;
         text-transform: uppercase; text-align: center; text-decoration: none; }}
.b1 {{ background: var(--lcdbg); color: var(--lcd); }}
.b2 {{ background: var(--yellow); color: var(--ink); }}
.b3 {{ background: var(--ink); color: var(--pink); }}
.b4 {{ background: var(--blue); color: var(--ink); }}
.hits {{ margin-top: 12px; font: 400 8px/1 var(--silk); letter-spacing: .1em;
        text-transform: uppercase; color: var(--plum); }}
.hits u {{ text-decoration: none; display: inline-flex; gap: 2px; margin: 0 6px;
          vertical-align: -3px; }}
.hits u i {{ background: var(--lcdbg); color: var(--lcd); border: 2px solid var(--ink);
            font: 15px/1.2 var(--vt); font-style: normal; padding: 0 4px; }}
.foot .book {{ display: block; margin-top: 12px; font: 21px/1 var(--vt); }}
.foot .made {{ margin-top: 12px; font: 400 9px/1.9 var(--silk); letter-spacing: .1em;
              text-transform: uppercase; color: var(--plum); }}
.foot .made a {{ color: var(--hot); text-decoration: none; border-bottom: 2px solid var(--hot); }}
.foot .made a:hover {{ color: var(--ink); border-color: var(--ink); }}
.foot .fine {{ margin-top: 7px; font: 400 6px/1.8 var(--silk); color: var(--dim);
              letter-spacing: .08em; text-transform: uppercase; }}

@media (max-width: 880px) {{
  .stagerow {{ flex-direction: column; }}
  .side {{ border-left: 0; border-top: 4px solid var(--ink); align-items: center; }}
  .say {{ flex-direction: column; }}
  .ticket {{ width: 100%; }}
  .rack {{ grid-template-columns: repeat(7, 1fr); }}
}}
</style>

<i class="star" style="left:5%;top:110px"></i>
<i class="star" style="left:12%;top:420px;color:#ffe9a8;animation-delay:.6s"></i>
<i class="star" style="right:6%;top:180px;animation-delay:.3s"></i>
<i class="star" style="right:10%;top:560px;color:#ffd1e8;animation-delay:1s"></i>
<i class="star" style="left:3%;bottom:120px;animation-delay:1.4s"></i>

<div class="marquee"><div>
  <span>{MARQUEE}</span><span>{MARQUEE}</span>
</div></div>

<div class="cab">
  <div class="chrome">
    <span class="dots"><i style="background:var(--yellow)"></i><i style="background:var(--mint)"></i><i style="background:var(--blue)"></i></span>
    <img src="favicon.png" alt="">
    <b>BORGIR NIGHT</b>
    <span class="tag">&#9733; the burger place that is a webpage &#9733;</span>
    <span class="lcd" id="clock">21:00</span>
  </div>

  <div class="top">
    <span class="pips" id="pips"></span>
    <span id="svc-now">Breakfast</span>
    <span id="who-n">customer 1 / 9</span>
    <span class="sp"></span>
    <span>tips <span class="tipbox" id="tips">0</span></span>
    <button class="btn mini" id="awards-btn">the wall <span id="awards-n">0</span>/9</button>
    <button class="btn mini" id="mute">sound: on</button>
  </div>

  <div class="stagerow hidden" id="stagerow">
    <div class="scene" id="scene"><span class="livetag">&#9834; live from the counter</span></div>
    <div class="side">
      <span class="cap">&#8212; your borgir &#8212;</span>
      <span class="empty" id="side-empty">stack it here &#8595;</span>
      <popkorn-player id="burger" loop fit="contain"></popkorn-player>
    </div>
  </div>

  <div class="say hidden">
    <div class="col">
      <span class="who" id="who">&#8212;</span>
      <p class="line" id="line"></p>
      <p class="aside" id="aside"></p>
      <div class="verdict" id="verdict"></div>
    </div>
    <div class="ticket" id="ticket"></div>
  </div>

  <div class="rack hidden" id="rack">
    {rack}
    <div class="acts">
      <span class="rule">a burger is: bottom bun &#183; the things &#183; top bun</span>
      <button class="btn" id="undo">undo</button>
      <button class="btn go" id="serve">serve! &#9829;</button>
    </div>
  </div>
  <div class="hint hidden">
    keys <kbd>1</kbd>&#8211;<kbd>=</kbd> stack &#183; <kbd>backspace</kbd> undoes &#183;
    <kbd>enter</kbd> serves<span class="pokehint">click her &#183; she likes it</span></div>

  <div class="end" id="title">
    <img class="burg" src="favicon.png" alt="">
    <h2>Borgir<br><span class="two">Night</span></h2>
    <p>You have the grill all weekend: Friday, Saturday and Sunday night, three of
    them each night, nine in all. Every one of them wants something slightly different.</p>
    <p class="sub">Read the ticket. Stack it bottom bun, things, top bun. Serve it.</p>
    <p><button class="btn go" id="open">open up</button></p>
    <p class="sub" style="font:400 8px/1.8 var(--silk);letter-spacing:.12em;text-transform:uppercase">
      free to play &#183; works at 2am &#183; bring your own spatula</p>
  </div>

  <div class="end hidden" id="service">
    <p class="sub" style="font:400 9px/1 var(--silk);letter-spacing:.24em;text-transform:uppercase">&#8212; now serving &#8212;</p>
    <h2 id="svc-title"></h2>
    <p><span id="svc-hours"></span></p>
    <p id="svc-blurb"></p>
    <p><button class="btn go" id="svc-go">start service</button></p>
  </div>

  <div class="gallery hidden" id="gallery">
    <div class="gal-top">
      <b>&#9733; The wall &#9733;</b>
      <span id="gal-note">Get an order exactly right and she gets her picture up here.</span>
      <button class="btn mini" id="gal-close">close</button>
    </div>
    <div class="gal-grid" id="gal-grid"></div>
  </div>

  <div class="end hidden" id="end">
    <h2 id="end-title"></h2>
    <p id="end-blurb"></p>
    <p class="sub" id="end-score"></p>
    <p><button class="btn go" id="again">open again tomorrow</button></p>
  </div>
</div>

<div class="rainbow"></div>
<div class="foot">
  <div class="badges">
    <span class="badge b1">Borgir Night<br>open 24 hrs</span>
    <span class="badge b2">made with<br>grease + love</span>
    <span class="badge b3">best viewed<br>640 &#215; 480</span>
    <span class="badge b4">kaki webring<br>&#8592; prev &#183; next &#8594;</span>
  </div>
  <p class="hits">you are visitor <u><i>0</i><i>0</i><i>4</i><i>2</i><i>1</i><i>7</i></u> &#183; burgers served</p>
  <a class="book" href="#" id="book">&#9733; sign the guestbook (it is the wall) &#9733;</a>
  <p class="made">made by <a href="https://github.com/dknos">@dknos</a> &#183;
    Kakis from <a href="https://www.oekakiconnect.net/">KemonoKaki</a></p>
  <p class="fine">&#169; 2026 Kaki's Diner &#183; this page is under construction forever &#183; no rights reserved probably</p>
</div>

{''.join(f'<script type="text/popkorn" id="{n}">{chr(10)}{t}{chr(10)}</script>{chr(10)}' for n, t in scenes)}
<script>
{bundle}
</script>
<script>
const DATA = {DATA};
</script>
<script>
(function () {{
  const $ = (id) => document.getElementById(id);
  const src = (id) => document.getElementById(id).textContent;
  const [CELL_W] = DATA.cell;
  const BASE_Y = 268, STEP = 26, PARK = 400, SLOTS = 8;
  const byId = Object.fromEntries(DATA.ingredients.map((x, i) => [x.id, {{ ...x, n: i }}]));

  /* ---- a little sound, synthesised, no files ---------------------------- */
  let audio = null, muted = false;
  function blip(freq, dur, type = 'square', vol = 0.05) {{
    if (muted) return;
    try {{
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      const o = audio.createOscillator(), g = audio.createGain();
      o.type = type; o.frequency.value = freq;
      g.gain.setValueAtTime(vol, audio.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + dur);
      o.connect(g); g.connect(audio.destination);
      o.start(); o.stop(audio.currentTime + dur);
    }} catch (e) {{ /* no audio, no problem */ }}
  }}
  const sfx = {{
    put: () => blip(320 + Math.random() * 60, 0.06),
    off: () => blip(180, 0.06),
    chomp: () => blip(90 + Math.random() * 40, 0.09, 'sawtooth', 0.07),
    good: () => {{ blip(660, 0.09); setTimeout(() => blip(880, 0.14), 90); }},
    meh: () => blip(300, 0.16, 'triangle'),
    bad: () => blip(150, 0.26, 'sawtooth', 0.06),
  }};

  /* ---- stage sizing: whole device pixels for the pixel art -------------- */
  function sizes() {{
    const dpr = window.devicePixelRatio || 1;
    const fit = (target, base) => {{
      const k = Math.max(1, Math.floor((target * dpr) / base));
      return Math.min((base * k) / dpr, target);
    }};
    const row = Math.min(1024, window.innerWidth - 44);
    const wide = window.innerWidth > 880;
    const sw = wide ? fit(row - 244, 640) : fit(row, 640);
    document.documentElement.style.setProperty('--sw', sw + 'px');
    document.documentElement.style.setProperty('--bw', (wide ? fit(240, 240) : fit(row, 240)) + 'px');
  }}
  sizes();
  addEventListener('resize', sizes);

  /* Nail smoothing shut at the source.

     The player sets canvas.width every time it lays out, and assigning width
     resets the whole 2D context including imageSmoothingEnabled. Setting the
     flag from our own rAF loses that race: the buffer is resized and drawn in
     one task, so by the time we set it again the frame is already blurred. At
     125% zoom that shows up as a thin ring around every closed eye, which is a
     bilinear resample of the lid's hard alpha edge.

     Overriding the accessor means the flag can never be true on any canvas on
     this page, whoever sets it and whenever. */
  (function noSmoothing() {{
    const p = CanvasRenderingContext2D.prototype;
    const d = Object.getOwnPropertyDescriptor(p, 'imageSmoothingEnabled');
    if (!d || !d.set) return;
    Object.defineProperty(p, 'imageSmoothingEnabled', {{
      configurable: true,
      get() {{ return false; }},
      set() {{ d.set.call(this, false); }},
    }});
    for (const k of ['mozImageSmoothingEnabled', 'webkitImageSmoothingEnabled']) {{
      if (k in p) Object.defineProperty(p, k, {{ configurable: true,
        get() {{ return false; }}, set() {{}} }});
    }}
  }})();

  /* Every frame, on every canvas that exists right now.
     This used to collect once into a list — except the collecting was never
     called, so the flag was never set on anything and the whole game drew with
     smoothing on. At 100% zoom the scene is 1:1 and nothing shows it. At 125%
     it resamples, and every layer with an alpha edge gets a soft halo: a thin
     ring appears around each closed eye where the lid meets the face.
     A player is also mounted fresh for every customer, so a list built once
     would go stale anyway. Two elements a frame is nothing. */
  const contexts = [];
  (function crisp() {{
    contexts.length = 0;
    document.querySelectorAll('popkorn-player').forEach((el) => {{
      const c = el.shadowRoot && el.shadowRoot.querySelector('canvas');
      if (c) contexts.push(c.getContext('2d'));
    }});
    for (let i = 0; i < contexts.length; i++) contexts[i].imageSmoothingEnabled = false;
    requestAnimationFrame(crisp);
  }})();

  /* ---- the burger ------------------------------------------------------- */
  const burger = $('burger');
  burger.source = src('scene-burger');
  let stack = [];
  function drawStack() {{
    for (let i = 0; i < SLOTS; i++) {{
      const it = stack[i];
      burger.setVariable('--s' + (i + 1), it ? byId[it].n : 0);
      burger.setVariable('--y' + (i + 1), it ? BASE_Y - i * STEP : PARK);
    }}
    $('side-empty').classList.toggle('hidden', stack.length > 0);
    $('serve').disabled = stack.length === 0 || busy;
    $('undo').disabled = stack.length === 0 || busy;
    document.querySelectorAll('.ing').forEach((b) => {{ b.disabled = busy || stack.length >= SLOTS; }});
  }}

  /* ---- the night -------------------------------------------------------- */
  let round = 0, tips = 0, busy = false, rule = null, player = null;
  let pokeTimer = null, asideTimer = null;
  const pips = $('pips');
  DATA.services.forEach((sv) => {{
    const g = document.createElement('b');
    DATA.customers.filter((c) => c.service === sv.key)
      .forEach(() => g.appendChild(document.createElement('i')));
    pips.appendChild(g);
  }});
  const allPips = () => [...pips.querySelectorAll('i')];
  const svcOf = (key) => DATA.services.find((s) => s.key === key);

  function mountCustomer(c) {{
    $('scene').innerHTML = '';
    player = document.createElement('popkorn-player');
    player.setAttribute('loop', '');
    player.setAttribute('fit', 'contain');
    $('scene').appendChild(player);
    player.source = src('scene-' + c.key);
    player.setVariable('--tod', svcOf(c.service).tod);
    /* poke her: the scene owns the hop and the squint, the page owns the line */
    player.addEventListener('popkorn:statechange', (ev) => {{
      if (ev.detail.to !== 'poked' || !c.poke) return;
      blip(440 + Math.random() * 80, 0.05, 'triangle', 0.04);
      if (busy) return;
      const held = $('line').textContent;
      $('line').textContent = c.poke;
      clearTimeout(pokeTimer);
      pokeTimer = setTimeout(() => {{ if (!busy) $('line').textContent = held; }}, 1500);
    }});
  }}

  function say(text) {{ $('line').textContent = text; }}

  /* ---- the wall of pictures --------------------------------------------- */
  const AW = 'borgir-awards';
  const CAST = new Set(DATA.customers.map((c) => c.key));
  // Someone who played before Cirno left still has her key saved, and counting it
  // would put 10/9 on the end screen.
  let awards = new Set(JSON.parse(localStorage.getItem(AW) || '[]').filter((k) => CAST.has(k)));
  function paintAwards() {{
    $('awards-n').textContent = awards.size;
    const grid = $('gal-grid');
    grid.innerHTML = '';
    DATA.customers.forEach((c) => {{
      const got = awards.has(c.key);
      const card = document.createElement('div');
      card.className = 'card' + (got ? ' got' : '');
      card.innerHTML = got
        ? `<img src="art/awards/${{c.key}}_t.png" alt="${{c.name}} eating her burger">`
          + `<div class="nm">${{c.name}}</div>`
        : `<div class="lock">?</div><div class="nm">${{c.name}}</div>`;
      if (got) card.addEventListener('click', () => lightbox(c));
      grid.appendChild(card);
    }});
    $('gal-note').textContent = awards.size === DATA.customers.length
      ? 'All nine. Every one of them got exactly what she asked for.'
      : 'Get an order exactly right and she gets her picture up here.';
  }}
  function lightbox(c) {{
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.innerHTML = `<div><img src="art/awards/${{c.key}}.png" alt="${{c.name}} eating her burger">`
      + `<p>${{c.lines.perfect}}</p></div>`;
    box.addEventListener('click', () => box.remove());
    document.body.appendChild(box);
  }}
  $('awards-btn').addEventListener('click', () => {{
    $('gallery').classList.toggle('hidden');
    paintAwards();
  }});
  $('gal-close').addEventListener('click', () => $('gallery').classList.add('hidden'));
  $('book').addEventListener('click', (e) => {{ e.preventDefault(); $('awards-btn').click(); }});
  paintAwards();

  function showService(key) {{
    const sv = svcOf(key);
    ['#stagerow', '.rack', '.say', '.hint'].forEach(
      (q) => document.querySelector(q).classList.add('hidden'));
    $('svc-title').textContent = sv.name;
    $('svc-hours').textContent = sv.hours;
    $('svc-blurb').textContent = sv.blurb;
    $('svc-now').textContent = sv.name;
    $('service').classList.remove('hidden');
    blip(400, 0.09); setTimeout(() => blip(560, 0.13), 100);
  }}
  $('svc-go').addEventListener('click', () => {{
    $('service').classList.add('hidden');
    ['#stagerow', '.rack', '.say', '.hint'].forEach(
      (q) => document.querySelector(q).classList.remove('hidden'));
    startRound();
  }});

  function startRound() {{
    const c = DATA.customers[round];
    rule = c.rule;
    stack = [];
    busy = false;
    $('verdict').textContent = '';
    $('verdict').className = 'verdict';
    $('who').textContent = c.name;
    $('clock').textContent = c.clock;
    $('who-n').textContent = 'customer ' + (round + 1) + ' / ' + DATA.customers.length;
    allPips().forEach((el, i) => {{
      el.className = i < round ? 'done' : (i === round ? 'now' : '');
    }});
    $('svc-now').textContent = svcOf(c.service).name;
    mountCustomer(c);
    say(c.order);
    $('aside').textContent = '';
    clearTimeout(asideTimer);
    if (c.aside) asideTimer = setTimeout(() => {{
      if (!busy) $('aside').textContent = c.aside;
    }}, 1900);
    $('ticket').textContent = c.follow ? '' : c.ticket;
    drawStack();
    if (c.follow) {{
      setTimeout(() => {{
        // she is already eating by now if you were quick — don't talk over the verdict
        if (busy || round !== DATA.customers.indexOf(c)) return;
        say(c.follow);
        $('ticket').textContent = c.ticket;
      }}, 2600);
    }}
  }}

  function maybeChangeMind() {{
    const c = DATA.customers[round];
    if (!c.change || c.changed || stack.length < 3) return;
    c.changed = true;
    rule = c.rule2;
    say(c.change);
    $('ticket').textContent = c.ticket2;
    blip(520, 0.08, 'triangle');
  }}

  function judge() {{
    const fills = stack.filter((x) => x !== 'bun_b' && x !== 'bun_t');
    const wellBuilt = stack.length >= 3 && stack[0] === 'bun_b'
      && stack[stack.length - 1] === 'bun_t'
      && !stack.slice(1, -1).some((x) => x === 'bun_b' || x === 'bun_t');
    const has = (x) => stack.includes(x);
    const missing = (rule.require || []).some((x) => !has(x));
    const banned = (rule.forbid || []).some((x) => has(x));
    const short = rule.min_fill ? fills.length < rule.min_fill : false;
    const over = rule.max_fill ? fills.length > rule.max_fill : false;
    if (missing || banned || over) return 'wrong';
    if (short || !wellBuilt) return 'okay';
    return 'perfect';
  }}

  function serve() {{
    if (busy || !stack.length) return;
    busy = true;
    drawStack();
    const c = DATA.customers[round];
    // Camper is the only one who wants the blue cheese. Serve it to anybody else
    // and you get her line back, in their voice.
    const moldy = c.key !== 'never' && stack.includes('mold');
    const verdict = moldy ? 'wrong' : judge();
    player.fire('eat');
    say('...');
    $('aside').textContent = '';
    clearTimeout(pokeTimer);
    clearTimeout(asideTimer);
    $('ticket').textContent = '';
    // she eats it a layer at a time
    (function bite() {{
      if (stack.length) {{
        stack.pop();
        drawStack();
        sfx.chomp();
        setTimeout(bite, 190);
        return;
      }}
      const pay = verdict === 'perfect' ? 3 : verdict === 'okay' ? 1 : 0;
      tips += pay;
      $('tips').textContent = tips;
      player.fire(verdict === 'perfect' ? 'happy' : verdict === 'okay' ? 'meh' : 'sad');
      (verdict === 'perfect' ? sfx.good : verdict === 'okay' ? sfx.meh : sfx.bad)();
      say(moldy ? DATA.mold_line : c.lines[verdict]);
      $('verdict').textContent = verdict === 'perfect' ? 'exactly right  +3'
        : verdict === 'okay' ? 'close enough  +1'
        : moldy ? 'she is not going to eat that' : 'not what she asked for';
      $('verdict').className = 'verdict ' + verdict;
      allPips()[round].className = 'done';
      if (verdict === 'perfect' && !awards.has(c.key)) {{
        awards.add(c.key);
        localStorage.setItem(AW, JSON.stringify([...awards]));
        paintAwards();
        $('verdict').textContent += '  ·  picture on the wall';
      }}
      setTimeout(() => {{
        round += 1;
        if (round >= DATA.customers.length) finish();
        else if (DATA.customers[round].service !== DATA.customers[round - 1].service)
          showService(DATA.customers[round].service);
        else startRound();
      }}, 3400);
    }})();
  }}

  function finish() {{
    $('stagerow').classList.add('hidden');
    document.querySelector('.rack').classList.add('hidden');
    document.querySelector('.say').classList.add('hidden');
    document.querySelector('.hint').classList.add('hidden');
    const rank = DATA.ranks.find((r) => tips >= r.at) || DATA.ranks[DATA.ranks.length - 1];
    const best = Math.max(tips, Number(localStorage.getItem('borgir-best') || 0));
    localStorage.setItem('borgir-best', String(best));
    $('end-title').textContent = rank.title;
    $('end-blurb').textContent = rank.blurb;
    $('end-score').textContent = tips + ' tips this weekend · best ' + best
      + ' · ' + awards.size + '/' + DATA.customers.length + ' on the wall';
    $('gallery').classList.remove('hidden');
    paintAwards();
    $('clock').textContent = '22:45';
    $('end').classList.remove('hidden');
  }}

  /* ---- input ------------------------------------------------------------ */
  $('rack').addEventListener('click', (e) => {{
    const b = e.target.closest('.ing');
    if (!b || busy || stack.length >= SLOTS) return;
    stack.push(b.dataset.ing);
    sfx.put();
    drawStack();
    maybeChangeMind();
  }});
  $('undo').addEventListener('click', () => {{
    if (busy || !stack.length) return;
    stack.pop(); sfx.off(); drawStack();
  }});
  $('serve').addEventListener('click', serve);
  $('mute').addEventListener('click', () => {{
    muted = !muted;
    $('mute').textContent = muted ? 'sound off' : 'sound on';
  }});
  function openUp() {{
    round = 0; tips = 0;
    DATA.customers.forEach((c) => {{ delete c.changed; }});
    $('tips').textContent = '0';
    ['#title', '#end', '#gallery', '#service'].forEach(
      (s) => document.querySelector(s).classList.add('hidden'));
    ['#stagerow', '.rack', '.say', '.hint'].forEach(
      (s) => document.querySelector(s).classList.remove('hidden'));
    blip(520, 0.08); setTimeout(() => blip(700, 0.12), 90);
    showService(DATA.customers[0].service);
  }}
  $('open').addEventListener('click', openUp);
  $('again').addEventListener('click', openUp);
  /* Sparkles behind the cursor. Throttled to 20 a second, removed the moment
     their animation ends, and off entirely for anyone who asked for less motion. */
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    const TRAIL = ['#fff', '#ffcf5c', '#ff9ec7'];
    let lastSpark = 0;
    addEventListener('mousemove', (e) => {{
      const now = performance.now();
      if (now - lastSpark < 50) return;
      lastSpark = now;
      const c = TRAIL[(Math.random() * TRAIL.length) | 0];
      const s = document.createElement('i');
      s.style.cssText = 'position:fixed;z-index:99;pointer-events:none;width:3px;height:3px'
        + ';background:' + c + ';box-shadow:0 -3px 0 ' + c + ',0 3px 0 ' + c
        + ',-3px 0 0 ' + c + ',3px 0 0 ' + c
        + ';left:' + (e.clientX + 6) + 'px;top:' + (e.clientY + 8) + 'px'
        + ';animation:sparkfade .7s ease-out forwards';
      s.addEventListener('animationend', () => s.remove());
      document.body.appendChild(s);
    }});
  }}

  const KEYS = '1234567890-=';
  addEventListener('keydown', (e) => {{
    if (e.key === 'Enter') {{ serve(); return; }}
    if (e.key === 'Backspace') {{ e.preventDefault(); $('undo').click(); return; }}
    const i = KEYS.indexOf(e.key);
    if (i >= 0 && DATA.ingredients[i]) {{
      const b = document.querySelector('.ing[data-ing="' + DATA.ingredients[i].id + '"]');
      if (b) b.click();
    }}
  }});

  document.documentElement.style.setProperty('--atlas', "url('art/ingredients.png')");
  const best = Number(localStorage.getItem('borgir-best') || 0);
  if (best) $('title').querySelector('p:nth-of-type(2)').textContent +=
    '  ·  best so far: ' + best + ' tips';
}})();
</script>
</html>
"""

IDS = sorted(set(re.findall(r"\$\('([\w-]+)'\)", HTML)))
SELECTORS = sorted(set(re.findall(r"querySelector(?:All)?\('([.#][\w-]+)'\)", HTML)))


def check():
    """Every hook the page's own script reaches for has to exist in the markup.

    Two of them are class selectors used inside forEach, so losing one in a
    restyle throws on null at the first service card rather than at load — which
    is exactly the kind of thing a screenshot does not catch.
    """
    body = HTML.split('<script>')[0]
    missing = [i for i in IDS if f'id="{i}"' not in body]
    for sel in SELECTORS:
        if sel[0] == '.' and f'class="{sel[1:]}' not in body and f' {sel[1:]}"' not in body:
            missing.append(sel)
    if missing:
        raise SystemExit('markup lost: ' + ', '.join(missing))
    print(f'checked {len(IDS)} ids + {len(SELECTORS)} selectors')


if __name__ == '__main__':
    check()
    out = os.path.join(HERE, 'index.html')
    open(out, 'w').write(HTML)
    print(f'{len(HTML):,} bytes -> {out}')
