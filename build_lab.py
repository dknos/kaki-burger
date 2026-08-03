"""Build lab.html — look at every animation and every sliced artifact without playing.

Mount any customer, fire any state, page the burger to any stack, and see the raw
patches the scene is made of at 4x with their coordinates and the cast.json knobs
that produced them.
"""
import json
import os

from orders import CUSTOMERS, INGREDIENTS, SERVICES

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, 'assets', 'index.json')))
STUDIO_CFG = os.path.join('/mnt/c/Users/rneeb/Downloads/kaki-studio', 'cast.json')
KNOBS = json.load(open(STUDIO_CFG)) if os.path.exists(STUDIO_CFG) else {}

_svc = {v['key']: i for i, v in enumerate(SERVICES)}
ORDER = [c['key'] for c in sorted(CUSTOMERS, key=lambda c: (_svc[c['service']], c['clock']))]


def scene(name):
    return open(os.path.join(HERE, 'scenes', name)).read()


scenes = [('scene-burger', scene('burger.css'))]
for k in ORDER:
    scenes.append((f'scene-{k}', scene(f'cust-{k}.css')))
bundle = open(os.path.join(HERE, 'vendor', 'popkorn.bundle.js')).read()
for n, t in scenes:
    assert '</script' not in t, n

LAB = {
    'cast': [{
        'key': k,
        'name': IDX[k]['name'],
        'service': next(c['service'] for c in CUSTOMERS if c['key'] == k),
        'eyes': IDX[k]['eyes'],
        'char': IDX[k]['char'],
        'knobs': {kk: vv for kk, vv in KNOBS.get(k, {}).items()
                  if kk not in ('name', 'origin')},
        'files': [f for f in ['source.png', 'char.png', 'char_solo.png', 'char_dry.png',
                              'bg_plate_pad.png', 'tears.png']
                  if os.path.exists(os.path.join(HERE, 'assets', k, f))],
    } for k in ORDER],
    'ingredients': [{'id': i, 'label': l} for i, l in INGREDIENTS],
}

HTML = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Borgir Lab</title>
<style>
:root {{
  --bg: #14111c; --panel: #1e1928; --line: #3b3050; --lamp: #ffb454;
  --cream: #ffeccf; --pink: #ff8fc0; --green: #a6d47f; --dim: #9a89b0;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--cream);
       font: 13px/1.6 var(--mono); padding: 16px; }}
canvas, img {{ image-rendering: pixelated; display: block; }}
h1 {{ font: 700 13px/1 var(--mono); letter-spacing: .34em; text-transform: uppercase;
     color: var(--lamp); margin: 0 0 14px; }}
.row {{ display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-start; }}
.panel {{ border: 2px solid var(--line); background: var(--panel); padding: 10px; }}
.panel h2 {{ font: 500 10px/1 var(--mono); letter-spacing: .24em; text-transform: uppercase;
            color: var(--dim); margin: 0 0 8px; }}
button {{ font: 500 11px/1 var(--mono); letter-spacing: .1em; text-transform: uppercase;
         color: var(--cream); background: #251e33; border: 2px solid var(--line);
         padding: 7px 9px; cursor: pointer; }}
button:hover {{ border-color: var(--lamp); color: var(--lamp); }}
button.on {{ background: var(--lamp); color: #221704; border-color: var(--lamp); }}
.pickers {{ display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 12px; }}
.pickers .svc {{ color: var(--dim); align-self: center; letter-spacing: .2em;
                text-transform: uppercase; font-size: 10px; margin: 0 4px 0 8px; }}
#stage popkorn-player {{ width: calc(640px * var(--z, 1)); height: calc(360px * var(--z, 1)); }}
#burger popkorn-player {{ width: calc(240px * var(--z, 1)); height: calc(360px * var(--z, 1)); }}
.strip {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.tile {{ text-align: center; color: var(--dim); font-size: 10px; }}
.tile .box {{ border: 1px solid var(--line);
             background: repeating-conic-gradient(#2a2338 0 25%, #201a2c 0 50%) 0 0/12px 12px; }}
.tile img {{ max-width: 220px; }}
.tile b {{ display: block; color: var(--cream); font-weight: 500; margin-top: 3px; }}
pre {{ background: #100d18; border: 2px solid var(--line); padding: 10px; overflow: auto;
      max-height: 340px; color: #cfe0b6; font-size: 11px; margin: 0; }}
.kv {{ color: var(--dim); }} .kv b {{ color: var(--lamp); font-weight: 500; }}
.stackbar {{ display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }}
.stackbar .ing {{ width: 54px; height: 40px; padding: 0; background-image: url('art/ingredients.png');
                 background-repeat: no-repeat;
                 background-size: calc(var(--cw) * {len(INGREDIENTS)} * 0.4) calc(var(--ch) * 0.4);
                 background-position: calc(var(--n) * var(--cw) * -0.4) center; }}
</style>

<h1>Borgir Lab</h1>

<div class="pickers" id="cast"></div>

<div class="row">
  <div class="panel">
    <h2>Scene · <span id="who">—</span></h2>
    <div id="stage"></div>
    <div class="strip" style="margin-top:10px" id="states"></div>
    <div class="kv" style="margin-top:8px">machine: <b id="machine">—</b> ·
      click her to poke · zoom
      <span id="zooms"></span></div>
  </div>

  <div class="panel">
    <h2>Burger</h2>
    <div id="burger"><popkorn-player id="bp" loop fit="contain"></popkorn-player></div>
    <div class="stackbar" style="margin-top:10px" id="rack"></div>
    <div class="kv" style="margin-top:8px">stack: <b id="stackout">empty</b></div>
  </div>
</div>

<div class="row" style="margin-top:14px">
  <div class="panel" style="flex:1 1 520px">
    <h2>Sliced artifacts</h2>
    <div class="strip" id="files"></div>
  </div>
  <div class="panel" style="flex:1 1 420px">
    <h2>Eye patches · 4x</h2>
    <div class="strip" id="patches"></div>
    <div class="kv" style="margin-top:10px">cast.json knobs: <b id="knobs">—</b></div>
    <div class="kv">retune: <b>python3 tune_eyes.py &lt;key&gt; --lid 0.6 --thick 5</b></div>
  </div>
</div>

<div class="panel" style="margin-top:14px">
  <h2>Scene source</h2>
  <pre id="src">—</pre>
</div>

{''.join(f'<script type="text/popkorn" id="{n}">{chr(10)}{t}{chr(10)}</script>{chr(10)}' for n, t in scenes)}
<script>
/* The player resizes its canvas on layout, and assigning width resets the 2D
   context, so setting imageSmoothingEnabled from a rAF always loses the race.
   Override the accessor and it can never be true on this page. */
(function () {{
  const p = CanvasRenderingContext2D.prototype;
  const d = Object.getOwnPropertyDescriptor(p, 'imageSmoothingEnabled');
  if (!d || !d.set) return;
  Object.defineProperty(p, 'imageSmoothingEnabled', {{
    configurable: true, get() {{ return false; }}, set() {{ d.set.call(this, false); }},
  }});
}})();
</script>
<script>
{bundle}
</script>
<script>
const LAB = {json.dumps(LAB, ensure_ascii=False)};
</script>
<script>
(function () {{
  const $ = (id) => document.getElementById(id);
  const src = (id) => document.getElementById(id).textContent;
  document.documentElement.style.setProperty('--cw', '132px');
  document.documentElement.style.setProperty('--ch', '56px');

  let cur = LAB.cast[0], player = null, zoom = 1, stack = [];

  // --- crisp -----------------------------------------------------------------
  (function crisp() {{
    document.querySelectorAll('popkorn-player').forEach((el) => {{
      const c = el.shadowRoot && el.shadowRoot.querySelector('canvas');
      if (c) c.getContext('2d').imageSmoothingEnabled = false;
    }});
    requestAnimationFrame(crisp);
  }})();

  // --- who -------------------------------------------------------------------
  let lastSvc = null;
  LAB.cast.forEach((c) => {{
    if (c.service !== lastSvc) {{
      lastSvc = c.service;
      const tag = document.createElement('span');
      tag.className = 'svc';
      tag.textContent = c.service;
      $('cast').appendChild(tag);
    }}
    const b = document.createElement('button');
    b.textContent = c.name;
    b.onclick = () => mount(c);
    b.dataset.key = c.key;
    $('cast').appendChild(b);
  }});

  function mount(c) {{
    cur = c;
    [...$('cast').querySelectorAll('button')].forEach(
      (b) => b.classList.toggle('on', b.dataset.key === c.key));
    $('stage').innerHTML = '';
    player = document.createElement('popkorn-player');
    player.setAttribute('loop', '');
    player.setAttribute('fit', 'contain');
    $('stage').appendChild(player);
    const text = src('scene-' + c.key);
    player.source = text;
    player.addEventListener('popkorn:statechange',
      (e) => {{ $('machine').textContent = e.detail.machine + ' → ' + e.detail.to; }});
    $('who').textContent = c.name + '  (' + c.service + ')';
    $('machine').textContent = 'idle';
    $('src').textContent = text;
    paintFiles();
    paintPatches();
    $('knobs').textContent = Object.keys(c.knobs).length
      ? JSON.stringify(c.knobs) : 'none — all defaults';
  }}

  // --- states ----------------------------------------------------------------
  ['idle', 'eat', 'happy', 'meh', 'sad', 'reset'].forEach((ev) => {{
    const b = document.createElement('button');
    b.textContent = ev;
    b.onclick = () => {{ if (player) player.fire(ev === 'idle' ? 'reset' : ev); }};
    $('states').appendChild(b);
  }});
  [1, 2].forEach((z) => {{
    const b = document.createElement('button');
    b.textContent = z + 'x';
    b.onclick = () => {{
      zoom = z;
      document.documentElement.style.setProperty('--z', z);
      [...$('zooms').querySelectorAll('button')].forEach(
        (x) => x.classList.toggle('on', x.textContent === z + 'x'));
    }};
    if (z === 1) b.classList.add('on');
    $('zooms').appendChild(b);
  }});

  // --- the artifacts ---------------------------------------------------------
  function tile(srcPath, label, extra) {{
    const d = document.createElement('div');
    d.className = 'tile';
    d.innerHTML = `<div class="box"><img src="${{srcPath}}" alt=""></div><b>${{label}}</b>`
      + (extra ? `<span>${{extra}}</span>` : '');
    return d;
  }}
  function paintFiles() {{
    $('files').innerHTML = '';
    cur.files.forEach((f) => $('files').appendChild(
      tile(`assets/${{cur.key}}/${{f}}`, f)));
  }}
  function paintPatches() {{
    $('patches').innerHTML = '';
    if (!cur.eyes.length) {{
      $('patches').textContent = 'no blink — her eyes are already shut in the source';
      return;
    }}
    cur.eyes.forEach((e, i) => {{
      ['half', 'shut'].forEach((st) => {{
        const t = tile(`assets/${{cur.key}}/${{e.states[st]}}`,
                       (i ? 'right' : 'left') + ' ' + st,
                       `${{e.w}}x${{e.h}} @ ${{e.x}},${{e.y}}`);
        t.querySelector('img').style.width = (e.w * 4) + 'px';
        $('patches').appendChild(t);
      }});
    }});
  }}

  // --- burger ----------------------------------------------------------------
  const bp = $('bp');
  bp.source = src('scene-burger');
  const BASE_Y = 268, STEP = 26, PARK = 400, SLOTS = 8;
  function drawStack() {{
    for (let i = 0; i < SLOTS; i++) {{
      const it = stack[i];
      const n = it ? LAB.ingredients.findIndex((x) => x.id === it) : 0;
      bp.setVariable('--s' + (i + 1), n);
      bp.setVariable('--y' + (i + 1), it ? BASE_Y - i * STEP : PARK);
    }}
    $('stackout').textContent = stack.length ? stack.join(' · ') : 'empty';
  }}
  LAB.ingredients.forEach((ing, n) => {{
    const b = document.createElement('button');
    b.className = 'ing';
    b.style.setProperty('--n', n);
    b.title = ing.label;
    b.onclick = () => {{ if (stack.length < SLOTS) {{ stack.push(ing.id); drawStack(); }} }};
    $('rack').appendChild(b);
  }});
  const clr = document.createElement('button');
  clr.textContent = 'clear';
  clr.onclick = () => {{ stack = []; drawStack(); }};
  $('rack').appendChild(clr);

  mount(LAB.cast[0]);
  drawStack();
}})();
</script>
</html>
"""

if __name__ == '__main__':
    out = os.path.join(HERE, 'lab.html')
    open(out, 'w').write(HTML)
    print(f'{len(HTML):,} bytes -> {out}')
