"""Retune one character's closed eyes without playing the game.

    python3 tune_eyes.py never                       # preview as-is
    python3 tune_eyes.py never --lid 0.66 --thick 9  # try other numbers
    python3 tune_eyes.py never --dark 80 --apply     # write them and sync

Writes tune_preview.png: open, half and shut side by side at 4x. Open it, decide,
run again with --apply. The knobs it accepts are the same ones cast.json holds,
so whatever you settle on can go straight in there.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

STUDIO = '/mnt/c/Users/rneeb/Downloads/kaki-studio'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, STUDIO)
import cast_slice as cs  # noqa: E402


def render(key, cfg, lid_shut, lid_half, thick_div, depth_frac):
    a = np.array(Image.open(f'{STUDIO}/cast/{key}/source.png').convert('RGB')).astype(int)
    bg = (cs.flood_background_walk(a, cfg['walk_tol']) if cfg.get('walk_tol')
          else cs.flood_background(a, [tuple(c) for c in cs.border_palette(a)],
                                   cfg.get('seed_bottom', False)))
    eyes = cs.eyes_from_boxes(a, cfg)
    bridge = cs.bridge_colour(a, cfg['eye_boxes'])
    ref = np.array(cfg.get('skin') or bridge)
    luma = a @ np.array([0.299, 0.587, 0.114])
    face = ((np.abs(a - ref).sum(axis=2) < cfg.get('face_tol', 150)) & ~bg
            & (luma < ref @ np.array([0.299, 0.587, 0.114]) + 18))

    if cfg.get('trim'):
        for e in eyes:
            e['blob'] = cs.trim_spikes(e['blob'], cfg['trim'])
            ys, xs = np.where(e['blob'])
            e['bbox'] = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))

    base = Image.open(f'{STUDIO}/cast/{key}/source.png').convert('RGBA')
    outs = {}
    for state in ('half', 'shut'):
        frame = base.copy()
        for e in eyes:
            x0, x1, y0, y1 = e['bbox']
            if state == 'half':
                # squashed into the bottom of the socket, not cut off at the top
                p = cs.eye_squash(a, e['blob'], x0, x1, y0, y1,
                                  keep=lid_half, face=face)
            else:
                lash = cs.darkest(a, e['blob'])
                p = cs.eye_patch(a, e['blob'], x0, x1, y0, y1, tuple(lash), lid_shut, True,
                                 face=face, thick_div=thick_div, depth_frac=depth_frac)
            frame.alpha_composite(p, (x0, y0))
            outs.setdefault(state, []).append((p, x0, y0))
        outs[state + '_frame'] = frame
    return base, outs, eyes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('key')
    ap.add_argument('--lid', type=float, default=0.60, help='where the shut lid sits, 0..1')
    ap.add_argument('--lid-half', type=float, default=0.58,
                    help='half-lidded: how much of the eye is left showing, 0..1')
    ap.add_argument('--thick', type=int, default=11, help='lash weight divisor; smaller = heavier')
    ap.add_argument('--depth', type=float, default=0.16, help='how much the lash arcs')
    ap.add_argument('--dark', type=int, help='rim luma ceiling')
    ap.add_argument('--dark-min', type=int, help='rim luma floor')
    ap.add_argument('--close', type=int, help='rim closing radius')
    ap.add_argument('--trim', type=int, help='knock arms thinner than this off the blob')
    ap.add_argument('--apply', action='store_true', help='write the patches and sync the game')
    args = ap.parse_args()

    cfg = dict(json.load(open(f'{STUDIO}/cast.json'))[args.key])
    for k, v in (('dark', args.dark), ('dark_min', args.dark_min), ('close', args.close),
                 ('trim', args.trim)):
        if v is not None:
            cfg[k] = v

    base, outs, eyes = render(args.key, cfg, args.lid, args.lid_half, args.thick, args.depth)
    e0, e1 = (eyes + eyes)[:2]
    box = (max(0, e0['bbox'][0] - 14), max(0, min(e0['bbox'][2], e1['bbox'][2]) - 16),
           min(300, e1['bbox'][1] + 14), min(300, max(e0['bbox'][3], e1['bbox'][3]) + 16))
    crops = [base.crop(box), outs['half_frame'].crop(box), outs['shut_frame'].crop(box)]
    w, h, S = crops[0].width, crops[0].height, 4
    sheet = Image.new('RGB', (w * S, h * S * 3 + 12), (24, 20, 30))
    for i, c in enumerate(crops):
        sheet.paste(c.convert('RGB').resize((w * S, h * S), Image.NEAREST), (0, i * (h * S + 6)))
    sheet.save(os.path.join(HERE, 'tune_preview.png'))
    print(f'{args.key}: shut lid={args.lid} · half keeps {args.lid_half} of the eye · '
          f'lash 1/{args.thick} deep {args.depth} -> tune_preview.png (open, half, shut)')

    if not args.apply:
        print('happy with it? run again with --apply')
        return
    for state in ('half', 'shut'):
        for i, (patch, x0, y0) in enumerate(outs[state]):
            name = f'eye{"LR"[i]}_{state}.png'
            patch.save(f'{STUDIO}/cast/{args.key}/{name}', optimize=True)
            shutil.copy(f'{STUDIO}/cast/{args.key}/{name}',
                        f'{HERE}/assets/{args.key}/{name}')
    print(f'applied to {args.key} and synced into assets/. '
          f'Put any --dark/--close values into kaki-studio/cast.json to keep them.')


if __name__ == '__main__':
    main()
