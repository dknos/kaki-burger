"""Take what you drew in paint.html and wire it into the game.

Looks in your Downloads for anything paint.html exported — files named
`<key>__<state>.png` — works out what changed against what the scene draws right
now, and keeps only that rectangle.

    python3 apply_paint.py                 # every export it finds
    python3 apply_paint.py never__sad.png  # one
    python3 apply_paint.py --keep          # don't delete the export afterwards

`idle` is her own art, so it is written straight back to char_solo.png and shows
in every state. The other four become paint_<state>.png, drawn on top of the
generated lids and mouth only while that reaction is on screen. Nothing is
overwritten silently: the file it replaces is copied to .bak first.
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS = '/mnt/c/Users/rneeb/Downloads'
IDX = os.path.join(HERE, 'assets', 'index.json')
STATES = ('idle', 'half', 'meh', 'shut', 'sad')


def compose(key, state, index):
    """The frame paint.html showed you, rebuilt here."""
    m = index[key]
    body = 'char_dry.png' if key == 'kitty' else 'char_solo.png'
    frame = Image.open(os.path.join(HERE, 'assets', key, body)).convert('RGBA')
    if state != 'idle':
        for e in m['eyes']:
            f = e['states'].get(state)
            if f:
                frame.alpha_composite(
                    Image.open(os.path.join(HERE, 'assets', key, f)).convert('RGBA'),
                    (e['x'], e['y']))
        mo = m.get('mouth')
        if mo and state in mo['states']:
            frame.alpha_composite(
                Image.open(os.path.join(HERE, 'assets', key, mo['states'][state])).convert('RGBA'),
                (mo['x'], mo['y']))
    over = os.path.join(HERE, 'assets', key, f'paint_{state}.png')
    if os.path.exists(over):
        frame.alpha_composite(Image.open(over).convert('RGBA'))
    return frame


def backup(path):
    if os.path.exists(path):
        shutil.copy(path, path + '.bak')


def apply(fname, index, keep=False):
    stem = os.path.splitext(os.path.basename(fname))[0]
    if '__' not in stem:
        print(f'{fname}: not an export (expected <key>__<state>.png)')
        return False
    key, state = stem.split('__', 1)
    if key not in index or state not in STATES:
        print(f'{fname}: unknown character or state ({key} / {state})')
        return False

    src = fname if os.path.isabs(fname) else os.path.join(DOWNLOADS, os.path.basename(fname))
    drawn = Image.open(src).convert('RGBA')
    now = compose(key, state, index)
    if drawn.size != now.size:
        print(f'{key} {state}: size is {drawn.size}, expected {now.size} — skipped')
        return False

    d, n = np.array(drawn), np.array(now)
    diff = np.any(d != n, axis=2)
    if not diff.any():
        print(f'{key:9s} {state:5s} nothing changed')
        return False
    ys, xs = np.where(diff)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())

    if state == 'idle':
        body = 'char_dry.png' if key == 'kitty' else 'char_solo.png'
        dst = os.path.join(HERE, 'assets', key, body)
        backup(dst)
        drawn.save(dst, optimize=True)
        print(f'{key:9s} idle  {int(diff.sum()):5d} px -> {body} (shows in every state)')
    else:
        patch = drawn.crop((x0, y0, x1 + 1, y1 + 1))
        # only the pixels that actually changed: leave the rest of the rectangle
        # transparent so the generated lids still show through around the edit
        pm = np.array(patch)
        pm[..., 3] = np.where(diff[y0:y1 + 1, x0:x1 + 1], pm[..., 3], 0)
        name = f'paint_{state}.png'
        dst = os.path.join(HERE, 'assets', key, name)
        backup(dst)
        Image.fromarray(pm).save(dst, optimize=True)
        index[key].setdefault('paint', {})[state] = {
            'file': name, 'x': x0, 'y': y0, 'w': x1 - x0 + 1, 'h': y1 - y0 + 1}
        print(f'{key:9s} {state:5s} {int(diff.sum()):5d} px -> {name} at ({x0},{y0})')

    if not keep:
        os.remove(src)
    return True


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--keep']
    keep = '--keep' in sys.argv
    index = json.load(open(IDX))
    files = args or sorted(f for f in os.listdir(DOWNLOADS)
                           if f.endswith('.png') and '__' in f
                           and f.split('__')[0] in index)
    if not files:
        print('nothing to apply. Draw something in paint.html and hit export.')
        raise SystemExit(0)
    if any(apply(f, index, keep) for f in list(files)):
        json.dump(index, open(IDX, 'w'), indent=1)
        print('\nrebuild with:  python3 gen_scenes.py && python3 build.py '
              '&& python3 build_lab.py && python3 build_paint.py')
