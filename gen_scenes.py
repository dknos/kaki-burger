"""Scenes for BORGIR NIGHT.

Two kinds:

  cust-<key>   the diner, with one customer at the counter. A machine swaps her
               expression when the host fires happy / meh / sad / eat / reset.
  burger       eight stacked slots that all page the same ingredient atlas. The
               host writes --sN (which cell) and --yN (where it sits), so one
               static scene can draw any burger you can build.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = json.load(open(os.path.join(HERE, 'art', 'atlas.json')))
CAST = json.load(open(os.path.join(HERE, 'assets', 'index.json')))
SCENES = os.path.join(HERE, 'scenes')

STAGE_W, STAGE_H = 640, 360
ANCHOR_X = 452                    # she stands right of centre, counter stays visible
FOOT = 4                          # how far her feet run past the bottom of the frame
SLOTS = 8
# Extra pixels down, per character. Measuring the alpha box lands everyone's feet
# on the same line, but a portrait cropped tight at the chest still reads as a
# head floating at the ceiling. Mermaid's art fills her frame edge to edge, so she
# sits highest of the nine; this puts her head level with the rest.
DROP = {'mermaid': 20}
CELL_W, CELL_H = ART['cell_w'], ART['cell_h']
BURGER_W, BURGER_H = 240, 360
STACK_X = (BURGER_W - CELL_W) // 2
BASE_Y = 268                       # the plate
STEP = 26                          # how much each layer lifts the one above


def place(key):
    """Where this character stands, measured from her own sprite.

    Every portrait fills its 300x300 frame differently, so a fixed offset leaves
    some of them hovering with a visible cut edge and pushes others off the side.
    Reading the alpha box instead lands every one of them on the same spot with
    her feet just past the bottom of the frame.
    """
    import numpy as np
    from PIL import Image
    body = 'char_dry.png' if key == 'kitty' else 'char_solo.png'
    a = np.array(Image.open(os.path.join(HERE, 'assets', key, body)).convert('RGBA'))
    ys, xs = np.where(a[..., 3] > 0)
    cx = (int(xs.min()) + int(xs.max())) / 2
    return (int(round(ANCHOR_X - cx)),
            int(STAGE_H + FOOT + DROP.get(key, 0) - int(ys.max()) - 1),
            int(xs.min()), int(xs.max()), int(ys.min()))


def kf(name, stops):
    return '@keyframes %s {\n%s\n}\n' % (
        name, '\n'.join(f'  {p} {{ {d} }}' for p, d in stops))


BOB = kf('bob', [
    ('0%', 'transform: translate(0px, 0px);'),
    ('25%', 'transform: translate(0px, -1px);'),
    ('50%', 'transform: translate(0px, -2px);'),
    ('75%', 'transform: translate(0px, -1px);'),
    ('100%', 'transform: translate(0px, 0px);'),
])
CHEW = kf('chew', [
    ('0%', 'transform: translate(0px, 0px);'),
    ('50%', 'transform: translate(0px, 2px);'),
    ('100%', 'transform: translate(0px, 0px);'),
])
BLINK = kf('blinkShut', [
    ('0%', 'opacity: 0;'), ('75.9%', 'opacity: 1;'), ('77.1%', 'opacity: 0;'),
    ('100%', 'opacity: 0;'),
])
HOP = kf('hop', [
    ('0%', 'transform: translate(0px, 0px);'),
    ('22%', 'transform: translate(0px, -5px);'),
    ('48%', 'transform: translate(0px, 0px);'),
    ('62%', 'transform: translate(0px, -2px);'),
    ('100%', 'transform: translate(0px, 0px);'),
])
# Daylight on the room only. The character used to share this curve and it
# wrecked her: at breakfast, brightness 1.55 clipped Kaki's near-white skin and
# hair to flat white and the hue-rotate turned her purple hood spots white and
# her green hood yellow. Hue-rotating a character sprite is wrong at any
# strength, so she gets her own curve below — a little light, nothing else.
SUN = kf('sun', [
    ('0%', 'filter: brightness(1.34) saturate(0.88) hue-rotate(-10deg);'),
    ('50%', 'filter: brightness(1.16) saturate(0.95) hue-rotate(-4deg);'),
    ('100%', 'filter: brightness(1.0) saturate(1.0) hue-rotate(0deg);'),
])
DAY = kf('day', [
    ('0%', 'filter: brightness(1.10);'),
    ('50%', 'filter: brightness(1.05);'),
    ('100%', 'filter: brightness(1.0);'),
])
FLOAT = kf('float', [
    ('0%', 'transform: translate(0px, 0px);'),
    ('20%', 'transform: translate(0px, -1px);'),
    ('40%', 'transform: translate(0px, -3px);'),
    ('60%', 'transform: translate(0px, -3px);'),
    ('80%', 'transform: translate(0px, -1px);'),
    ('100%', 'transform: translate(0px, 0px);'),
])
TWINKLE = kf('twink', [
    ('0%', 'opacity: 0;'), ('42%', 'opacity: 0;'), ('50%', 'opacity: 1;'),
    ('62%', 'opacity: 1;'), ('70%', 'opacity: 0;'), ('100%', 'opacity: 0;'),
])
POP = kf('pop', [
    ('0%', 'transform: translate(0px, 0px); opacity: 0;'),
    ('30%', 'transform: translate(0px, -14px); opacity: 1;'),
    ('100%', 'transform: translate(0px, -34px); opacity: 0;'),
])


def lid(key, side, e, state, states, extra='', at=(0, 0), name=None):
    CUST_X, CUST_Y = at
    rules = ''.join(f'    &:state({s}) {{\n      opacity: 1;\n    }}\n' for s in states)
    return f"""  > #eye-{name or f'{side}-{state}'} {{
    type: image;
    content: url('assets/{key}/{e['states'][state]}');
    x: {CUST_X + e['x']}px;
    y: {CUST_Y + e['y']}px;
    width: {e['w']}px;
    height: {e['h']}px;
    opacity: 0;
    transition: opacity 140ms ease-out;
{extra}{rules}  }}
"""


def customer(key):
    m = CAST[key]
    CUST_X, CUST_Y, bx0, bx1, by0 = place(key)
    body = 'char_dry.png' if key == 'kitty' else 'char_solo.png'
    lids = ''
    if m['eyes']:
        left, right = m['eyes']
        # shut = pleased or asleep, half = chewing or unimpressed
        for side, e in (('l', left), ('r', right)):
            # Two nodes on the same shut artwork on purpose: an animated channel
            # outranks both the base value and the state, so a patch that blinks
            # can never also be held open by a state. One blinks, one is held.
            lids += lid(key, side, e, 'shut', [], name=f'blink-{side}',
                        extra='    animation: blinkShut 5.4s step-end infinite;\n',
                        at=(CUST_X, CUST_Y))
            lids += lid(key, side, e, 'shut', ['happy', 'poked'], at=(CUST_X, CUST_Y))
            lids += lid(key, side, e, 'sad', ['sad'], at=(CUST_X, CUST_Y))
            lids += lid(key, side, e, 'half', ['eating'], at=(CUST_X, CUST_Y))
            lids += lid(key, side, e, 'meh', ['meh'], at=(CUST_X, CUST_Y))
    # A smile under a shut eye reads as pleased whatever the lids are doing, so
    # unimpressed and miserable get their own mouth. Chewing and pleased keep the
    # one she was drawn with.
    mouth = ''
    mo = m.get('mouth')
    if mo:
        for kind in ('meh', 'sad'):
            mouth += f"""  > #mouth-{kind} {{
    type: image;
    content: url('assets/{key}/{mo['states'][kind]}');
    x: {CUST_X + mo['x']}px;
    y: {CUST_Y + mo['y']}px;
    width: {mo['w']}px;
    height: {mo['h']}px;
    opacity: 0;
    transition: opacity 140ms ease-out;
    &:state({kind}) {{
      opacity: 1;
    }}
  }}
"""

    # Hand-drawn overrides from paint.html, on top of everything generated.
    painted = ''
    for state, p in (m.get('paint') or {}).items():
        painted += f"""  > #paint-{state} {{
    type: image;
    content: url('assets/{key}/{p['file']}');
    x: {CUST_X + p['x']}px;
    y: {CUST_Y + p['y']}px;
    width: {p['w']}px;
    height: {p['h']}px;
    opacity: 0;
    transition: opacity 140ms ease-out;
    &:state({state}) {{
      opacity: 1;
    }}
  }}
"""

    # She has a halo and a pair of wings, so she does not bob like the rest of
    # them — she hovers, and something catches the light over her head.
    idle_anim = ('float 5.4s step-end infinite' if key == 'vesper'
                 else 'bob 3.6s step-end infinite')
    twinkle = ''
    if key == 'vesper':
        twinkle = f"""  > #twinkle {{
    type: text;
    content: "\u2726";
    x: {CUST_X + 150}px;
    y: {CUST_Y + 30}px;
    fill: #ffeccf;
    font-size: 20px;
    opacity: 0;
    animation: twink 5.4s linear infinite;
  }}
"""

    tears = ''
    if key == 'kitty':
        t = m['tears']
        tears = f"""  > #tears {{
    type: image;
    content: url('assets/kitty/{t['file']}');
    x: {CUST_X + t['x']}px;
    y: {CUST_Y + t['y']}px;
    width: {t['w']}px;
    height: {t['h']}px;
    &:state(happy) {{
      animation: fall 1.5s ease-in;
    }}
  }}
"""
    fall = kf('fall', [
        ('0%', 'transform: translate(0px, 0px); opacity: 1;'),
        ('70%', 'opacity: 0.6;'),
        ('100%', 'transform: translate(0px, 44px); opacity: 0;'),
    ]) if key == 'kitty' else ''

    return f"""/* {m['name']} at the counter. The host fires the reaction; the scene owns what
 * that looks like. */

:root {{
  width: {STAGE_W}px;
  height: {STAGE_H}px;
  background: #0b0912;
  --tod: 1;
}}

@machine poke {{
  initial: calm;
  state calm  {{ to: poked on click(:root); }}
  state poked {{ to: calm on complete; }}
}}

/* Every mood reaches every other mood. Leaving happy/meh/sad with only a reset
   out of them means the lab needs a reset click between any two expressions,
   and the game can't go straight from one reaction to the next. */
@machine mood {{
  initial: idle;
  state idle   {{ to: eating on event(eat); to: happy on event(happy); to: meh on event(meh); to: sad on event(sad); }}
  state eating {{ to: happy on event(happy); to: meh on event(meh); to: sad on event(sad); to: idle on event(reset); }}
  state happy  {{ to: eating on event(eat); to: meh on event(meh); to: sad on event(sad); to: idle on event(reset); }}
  state meh    {{ to: eating on event(eat); to: happy on event(happy); to: sad on event(sad); to: idle on event(reset); }}
  state sad    {{ to: eating on event(eat); to: happy on event(happy); to: meh on event(meh); to: idle on event(reset); }}
}}

{BOB}{CHEW}{BLINK}{HOP}{SUN}{DAY}{FLOAT}{TWINKLE}{fall}{POP}
/* The art is a night diner; breakfast is the same room brightened and cooled.
   One keyframed filter, scrubbed by the service rather than played. */
#room {{
  type: group;
  animation: sun 1s linear;
  animation-timeline: var(--tod);

  > #diner {{
    type: image;
    content: url('art/diner.png');
    x: 0px;
    y: 0px;
    width: {STAGE_W}px;
    height: {STAGE_H}px;
  }}
}}

#light {{
  type: group;
  animation: day 1s linear;
  animation-timeline: var(--tod);

  > #cust {{
  type: group;
  animation: {idle_anim};
  cursor: pointer;
  &:state(eating) {{
    animation: chew 0.42s step-end infinite;
  }}
  &:state(poked) {{
    animation: hop 0.62s ease-out;
  }}

  > #body {{
    type: image;
    content: url('assets/{key}/{body}');
    x: {CUST_X}px;
    y: {CUST_Y}px;
    width: {m['char']['w']}px;
    height: {m['char']['h']}px;
  }}

{lids}{mouth}{painted}{twinkle}{tears}  }}
}}

#spark {{
  type: text;
  content: "♥";
  x: {min(CUST_X + bx1 + 6, STAGE_W - 30)}px;
  y: {CUST_Y + by0 + 44}px;
  fill: #ff9fd0;
  font-size: 34px;
  opacity: 0;
  &:state(happy) {{
    animation: pop 1.2s ease-out;
  }}
  &:state(poked) {{
    animation: pop 0.9s ease-out;
  }}
}}
"""


def burger():
    slots = ''
    for i in range(1, SLOTS + 1):
        slots += f"""#s{i} {{
  type: image;
  content: url('art/ingredients.png');
  x: {STACK_X}px;
  y: calc(var(--y{i}) * 1px);
  width: {CELL_W}px;
  height: {CELL_H}px;
  object-view-box: xywh(calc(var(--s{i}) * {CELL_W}px) 0px {CELL_W}px {CELL_H}px);
}}

"""
    vars_ = ''.join(f'  --s{i}: 0;\n  --y{i}: 400;\n' for i in range(1, SLOTS + 1))
    return f"""/* The burger. Eight slots, one atlas, two variables each: which cell to show
 * and where to sit. The scene is static; the stack is not.
 */

:root {{
  width: {BURGER_W}px;
  height: {BURGER_H}px;
  background: #17121d;
{vars_}}}

#plate {{
  type: rect;
  x: 16px;
  y: {BASE_Y + 52}px;
  width: {BURGER_W - 32}px;
  height: 10px;
  rx: 4px;
  fill: #3b3049;
}}

{slots}"""


if __name__ == '__main__':
    os.makedirs(SCENES, exist_ok=True)
    for key in CAST:
        open(os.path.join(SCENES, f'cust-{key}.css'), 'w').write(customer(key))
    open(os.path.join(SCENES, 'burger.css'), 'w').write(burger())
    for f in sorted(os.listdir(SCENES)):
        print(f'  {f:20s} {os.path.getsize(os.path.join(SCENES, f)):>6,} bytes')
    print(f'stack: base y={BASE_Y}, step={STEP}, slot x={STACK_X}, cell {CELL_W}x{CELL_H}')
