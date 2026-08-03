"""Build paint.html — edit any frame by hand, in her own colours, and send it back.

Every expression in this game is generated, and generating them keeps getting
things almost right. This is the escape hatch: pick a character and a state, draw
on the actual frame with the actual palette, export a PNG, and
`apply_paint.py` turns whatever you changed into the patch the scene loads.

    python3 build_paint.py        # writes paint.html
    # ...draw, hit export, it lands in Downloads...
    python3 apply_paint.py        # picks up every exported file and wires it in

Everything is inlined as a data URI on purpose. Reading pixels out of a canvas is
blocked when the image came from a file:// URL, so a paint tool that loaded its
art normally would open, look fine, and refuse to export.
"""
import base64
import json
import os

from orders import CUSTOMERS, SERVICES

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, 'assets', 'index.json')))

_svc = {v['key']: i for i, v in enumerate(SERVICES)}
ORDER = [c['key'] for c in sorted(CUSTOMERS, key=lambda c: (_svc[c['service']], c['clock']))]
STATES = ('idle', 'half', 'meh', 'shut', 'sad')


def uri(key, name):
    p = os.path.join(HERE, 'assets', key, name)
    if not os.path.exists(p):
        return None
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def layers(key):
    """What is composited for each state, in draw order."""
    m = IDX[key]
    out = {}
    for st in STATES:
        L = []
        if st != 'idle':
            for e in m['eyes']:
                f = e['states'].get(st)
                if f:
                    L.append({'x': e['x'], 'y': e['y'], 'src': uri(key, f)})
            mo = m.get('mouth')
            if mo and st in mo['states']:
                L.append({'x': mo['x'], 'y': mo['y'], 'src': uri(key, mo['states'][st])})
        over = uri(key, f'paint_{st}.png')
        if over:
            L.append({'x': 0, 'y': 0, 'src': over, 'painted': True})
        out[st] = L
    return out


DATA = {
    'cast': [{
        'key': k,
        'name': IDX[k]['name'],
        'w': IDX[k]['char']['w'],
        'h': IDX[k]['char']['h'],
        'base': uri(k, 'char_dry.png' if k == 'kitty' else 'char_solo.png'),
        'states': layers(k),
    } for k in ORDER],
    'states': list(STATES),
}

HTML = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Borgir Paint</title>
<style>
:root {
  --bg: #14111c; --panel: #1e1928; --line: #3b3050; --lamp: #ffb454;
  --cream: #ffeccf; --pink: #ff8fc0; --dim: #9a89b0;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--cream);
       font: 13px/1.6 var(--mono); padding: 16px; }
canvas { image-rendering: pixelated; display: block; }
h1 { font: 700 13px/1 var(--mono); letter-spacing: .34em; text-transform: uppercase;
     color: var(--lamp); margin: 0 0 4px; }
.sub { color: var(--dim); margin: 0 0 14px; }
.row { display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-start; }
.panel { border: 2px solid var(--line); background: var(--panel); padding: 10px; }
.panel h2 { font: 500 10px/1 var(--mono); letter-spacing: .24em; text-transform: uppercase;
            color: var(--dim); margin: 0 0 8px; }
button { font: 500 11px/1 var(--mono); letter-spacing: .1em; text-transform: uppercase;
         color: var(--cream); background: #251e33; border: 2px solid var(--line);
         padding: 7px 9px; cursor: pointer; }
button:hover { border-color: var(--lamp); color: var(--lamp); }
button.on { background: var(--lamp); color: #221704; border-color: var(--lamp); }
.pickers { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px; }
#wrap { border: 2px solid var(--line);
        background: repeating-conic-gradient(#2a2338 0 25%, #201a2c 0 50%) 0 0/16px 16px;
        position: relative; cursor: crosshair; }
#grid { position: absolute; inset: 0; pointer-events: none; opacity: 0; }
.swatches { display: grid; grid-template-columns: repeat(6, 30px); gap: 4px; }
.sw { width: 30px; height: 30px; border: 2px solid var(--line); cursor: pointer; padding: 0; }
.sw.on { border-color: var(--lamp); }
.kv { color: var(--dim); } .kv b { color: var(--lamp); font-weight: 500; }
.tools { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 8px; }
label { color: var(--dim); display: flex; align-items: center; gap: 6px; }
input[type=range] { width: 120px; }
.note { color: var(--dim); max-width: 300px; font-size: 11px; line-height: 1.7; }
.note b { color: var(--cream); font-weight: 500; }
</style>

<h1>Borgir Paint</h1>
<p class="sub">Draw on the frame. Export. Then run <b style="color:var(--cream)">python3 apply_paint.py</b>.</p>

<div class="pickers" id="cast"></div>
<div class="pickers" id="states"></div>

<div class="row">
  <div class="panel">
    <h2>Frame</h2>
    <div id="wrap"><canvas id="cv"></canvas><canvas id="grid"></canvas></div>
    <div class="kv" style="margin-top:8px">
      <span id="pos">—</span> · <span id="who">—</span> ·
      zoom <b id="zn">4</b>x · <span id="dirty">clean</span>
    </div>
  </div>

  <div class="panel">
    <h2>Tools</h2>
    <div class="tools">
      <button data-tool="pen" class="on">pen</button>
      <button data-tool="pick">pick</button>
      <button data-tool="fill">fill</button>
      <button data-tool="erase">erase</button>
    </div>
    <div class="tools">
      <button id="undo">undo</button>
      <button id="revert">revert</button>
      <button id="gridbtn">grid</button>
    </div>
    <label style="margin-bottom:6px">brush <input type="range" id="brush" min="1" max="6" value="1">
      <b id="bn">1</b></label>
    <label>zoom <input type="range" id="zoom" min="2" max="10" value="4"></label>

    <h2 style="margin-top:14px">Her colours</h2>
    <div class="swatches" id="pal"></div>
    <div class="kv" style="margin-top:8px">ink <b id="ink">—</b></div>

    <h2 style="margin-top:14px">Send it back</h2>
    <button id="export" style="width:100%">export png</button>
    <p class="note" style="margin:8px 0 0">
      Saves <b>&lt;key&gt;__&lt;state&gt;.png</b> to your Downloads. Tell me it's there,
      or run <b>apply_paint.py</b> yourself: it diffs what you drew against what the
      scene draws now and writes only the changed rectangle.
      <br><br>
      <b>idle</b> edits the character herself, so it changes every state.
      The other four only show for that reaction.
    </p>
  </div>
</div>

<script>
/* smoothing can never be true here either: the preview is pixel art */
(function () {
  const p = CanvasRenderingContext2D.prototype;
  const d = Object.getOwnPropertyDescriptor(p, 'imageSmoothingEnabled');
  if (!d || !d.set) return;
  Object.defineProperty(p, 'imageSmoothingEnabled', {
    configurable: true, get() { return false; }, set() { d.set.call(this, false); },
  });
})();
</script>
<script>
const DATA = __DATA__;
const $ = (id) => document.getElementById(id);
const cv = $('cv'), ctx = cv.getContext('2d', { willReadFrequently: true });
const grid = $('grid'), gtx = grid.getContext('2d');
let cur = DATA.cast[0], state = 'idle', zoom = 4, tool = 'pen', brush = 1;
let ink = [255, 143, 192, 255], history = [], baseData = null, dirty = false;

function px(im, x, y) {
  const i = (y * im.width + x) * 4;
  return [im.data[i], im.data[i + 1], im.data[i + 2], im.data[i + 3]];
}
function same(a, b) { return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3]; }
const hex = (c) => '#' + c.slice(0, 3).map((v) => v.toString(16).padStart(2, '0')).join('');

function load() {
  const c = cur;
  cv.width = c.w; cv.height = c.h;
  ctx.clearRect(0, 0, c.w, c.h);
  const imgs = [{ src: c.base, x: 0, y: 0 }, ...c.states[state]];
  let n = 0;
  imgs.forEach((L) => {
    const im = new Image();
    im.onload = () => {
      ctx.drawImage(im, L.x, L.y);
      if (++n === imgs.length) ready();
    };
    im.src = L.src;
  });
}
function ready() {
  baseData = ctx.getImageData(0, 0, cv.width, cv.height);
  history = []; dirty = false; $('dirty').textContent = 'clean';
  palette(); paint();
}
function palette() {
  const im = ctx.getImageData(0, 0, cv.width, cv.height), tally = new Map();
  for (let i = 0; i < im.data.length; i += 4) {
    if (im.data[i + 3] < 250) continue;
    const k = [im.data[i], im.data[i + 1], im.data[i + 2]].join(',');
    tally.set(k, (tally.get(k) || 0) + 1);
  }
  const top = [...tally].sort((a, b) => b[1] - a[1]).slice(0, 30);
  $('pal').innerHTML = '';
  top.forEach(([k]) => {
    const rgb = k.split(',').map(Number);
    const b = document.createElement('button');
    b.className = 'sw'; b.style.background = hex(rgb);
    b.title = hex(rgb);
    b.onclick = () => setInk([...rgb, 255], b);
    $('pal').appendChild(b);
  });
  if (top.length) setInk([...top[0][0].split(',').map(Number), 255], $('pal').firstChild);
}
function setInk(c, el) {
  ink = c; $('ink').textContent = hex(c);
  [...document.querySelectorAll('.sw')].forEach((s) => s.classList.remove('on'));
  if (el) el.classList.add('on');
}
function paint() {
  cv.style.width = cv.width * zoom + 'px'; cv.style.height = cv.height * zoom + 'px';
  grid.width = cv.width * zoom; grid.height = cv.height * zoom;
  grid.style.width = grid.width + 'px'; grid.style.height = grid.height + 'px';
  gtx.clearRect(0, 0, grid.width, grid.height);
  gtx.strokeStyle = 'rgba(255,180,84,.35)'; gtx.lineWidth = 1;
  if (zoom >= 4) {
    for (let x = 0; x <= cv.width; x++) {
      gtx.beginPath(); gtx.moveTo(x * zoom + .5, 0); gtx.lineTo(x * zoom + .5, grid.height); gtx.stroke();
    }
    for (let y = 0; y <= cv.height; y++) {
      gtx.beginPath(); gtx.moveTo(0, y * zoom + .5); gtx.lineTo(grid.width, y * zoom + .5); gtx.stroke();
    }
  }
  $('zn').textContent = zoom;
}
function push() {
  history.push(ctx.getImageData(0, 0, cv.width, cv.height));
  if (history.length > 60) history.shift();
  dirty = true; $('dirty').textContent = 'edited';
}
function dot(x, y) {
  const r = brush - 1;
  ctx.fillStyle = `rgba(${ink[0]},${ink[1]},${ink[2]},${ink[3] / 255})`;
  if (tool === 'erase') { ctx.clearRect(x - r, y - r, brush + r, brush + r); return; }
  ctx.fillRect(x - r, y - r, brush + r, brush + r);
}
function bucket(x, y) {
  const im = ctx.getImageData(0, 0, cv.width, cv.height);
  const want = px(im, x, y);
  if (same(want, ink)) return;
  const q = [[x, y]];
  while (q.length) {
    const [cx, cy] = q.pop();
    if (cx < 0 || cy < 0 || cx >= im.width || cy >= im.height) continue;
    if (!same(px(im, cx, cy), want)) continue;
    const i = (cy * im.width + cx) * 4;
    im.data[i] = ink[0]; im.data[i + 1] = ink[1]; im.data[i + 2] = ink[2]; im.data[i + 3] = ink[3];
    q.push([cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]);
  }
  ctx.putImageData(im, 0, 0);
}
function at(ev) {
  const r = cv.getBoundingClientRect();
  return [Math.floor((ev.clientX - r.left) / zoom), Math.floor((ev.clientY - r.top) / zoom)];
}
let down = false;
$('wrap').addEventListener('pointerdown', (ev) => {
  const [x, y] = at(ev);
  if (x < 0 || y < 0 || x >= cv.width || y >= cv.height) return;
  if (tool === 'pick') {
    setInk(px(ctx.getImageData(0, 0, cv.width, cv.height), x, y), null);
    return;
  }
  push();
  if (tool === 'fill') { bucket(x, y); return; }
  down = true; dot(x, y);
  $('wrap').setPointerCapture(ev.pointerId);
});
$('wrap').addEventListener('pointermove', (ev) => {
  const [x, y] = at(ev);
  $('pos').textContent = `${x}, ${y}`;
  if (down && x >= 0 && y >= 0 && x < cv.width && y < cv.height) dot(x, y);
});
addEventListener('pointerup', () => { down = false; });

$('undo').onclick = () => { const h = history.pop(); if (h) ctx.putImageData(h, 0, 0); };
$('revert').onclick = () => { if (baseData) { push(); ctx.putImageData(baseData, 0, 0); } };
$('gridbtn').onclick = (e) => {
  grid.style.opacity = grid.style.opacity === '1' ? '0' : '1';
  e.target.classList.toggle('on');
};
$('brush').oninput = (e) => { brush = +e.target.value; $('bn').textContent = brush; };
$('zoom').oninput = (e) => { zoom = +e.target.value; paint(); };
document.querySelectorAll('[data-tool]').forEach((b) => {
  b.onclick = () => {
    tool = b.dataset.tool;
    document.querySelectorAll('[data-tool]').forEach((o) => o.classList.toggle('on', o === b));
  };
});
$('export').onclick = () => {
  cv.toBlob((blob) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${cur.key}__${state}.png`;
    a.click();
  });
};

function chrome() {
  $('cast').innerHTML = ''; $('states').innerHTML = '';
  DATA.cast.forEach((c) => {
    const b = document.createElement('button');
    b.textContent = c.name; b.classList.toggle('on', c === cur);
    b.onclick = () => {
      if (dirty && !confirm('You have unexported edits. Drop them?')) return;
      cur = c; chrome(); load();
    };
    $('cast').appendChild(b);
  });
  DATA.states.forEach((s) => {
    const b = document.createElement('button');
    b.textContent = s === 'idle' ? 'idle (her art)' : s;
    b.classList.toggle('on', s === state);
    b.onclick = () => {
      if (dirty && !confirm('You have unexported edits. Drop them?')) return;
      state = s; chrome(); load();
    };
    $('states').appendChild(b);
  });
  $('who').textContent = `${cur.name} · ${state}`;
}
chrome(); load();
</script>
"""

if __name__ == '__main__':
    out = os.path.join(HERE, 'paint.html')
    html = HTML.replace('__DATA__', json.dumps(DATA))
    open(out, 'w', encoding='utf-8').write(html)
    print(f'{len(html):,} bytes -> {out}')
