"""Key the generated art onto one pixel grid and pack the ingredient atlas.

The generated sheets come back at 1024/1280 with a chunky block size. Everything
is reduced by the same integer factor so the diner and the ingredients share a
pixel grid, then the twelve ingredients are packed into a single horizontal
atlas the burger scene pages through with `object-view-box`.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, ART = os.path.join(HERE, 'raw'), os.path.join(HERE, 'art')
from orders import INGREDIENTS                                    # noqa: E402

CELL_W, CELL_H = 132, 56          # atlas cell, in game pixels
EXTRAS = {'mold': 'mold.png'}     # generated one at a time, not on the 4x3 sheet
SHRINK = 2                        # generated art -> game pixel grid


def block_size(im, max_k=8):
    """Largest k for which the image is a clean k-times upscale."""
    a = np.array(im.convert('RGB'))
    h, w, _ = a.shape
    for k in range(max_k, 1, -1):
        if h % k or w % k:
            continue
        b = a.reshape(h // k, k, w // k, k, 3)
        if np.all(b == b[:, :1, :, :1]):
            return k
    return 1


def keyed(im, tol=110):
    """Drop the flat magenta backdrop, keeping only what the border cannot reach.

    The generated sheet is anti-aliased against the magenta, so the exact-colour
    test leaves a one-pixel fringe of half-magenta around every ingredient. It is
    invisible at 130px and obvious the moment anything is drawn larger, so the
    alpha is eroded by a pixel after keying.
    """
    a = np.array(im.convert('RGB')).astype(int)
    # take the key from the image's own corner: the generator does not return the
    # exact magenta it was asked for, and a fixed #FF00FF misses by enough to
    # leave the whole backdrop behind
    key = a[0, 0]
    near = (np.abs(a - key).sum(axis=2) < tol)
    # anything magenta-ish that the border can reach is background
    lab, n = ndimage.label(near)
    bg = np.zeros(near.shape, bool)
    edge = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    for i in edge:
        if i:
            bg |= (lab == i)
    keep = ndimage.binary_erosion(~bg, np.ones((3, 3), bool))
    out = np.dstack([a, np.where(keep, 255, 0)]).astype(np.uint8)
    return Image.fromarray(out)


def trim(im):
    a = np.array(im)
    ys, xs = np.where(a[..., 3] > 0)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def to_cell(im):
    """Fit a trimmed ingredient into one atlas cell without distorting it."""
    w, h = im.size
    s = min((CELL_W - 8) / w, (CELL_H - 6) / h)
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    im = im.resize((nw, nh), Image.NEAREST)
    cell = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
    cell.paste(im, ((CELL_W - nw) // 2, (CELL_H - nh) // 2))
    return cell


if __name__ == '__main__':
    os.makedirs(ART, exist_ok=True)

    sheet = Image.open(os.path.join(RAW, 'ingredients.png')).convert('RGB')
    print('ingredient sheet', sheet.size, 'block size', block_size(sheet))
    sheet = sheet.resize((sheet.width // SHRINK, sheet.height // SHRINK), Image.NEAREST)
    W, H = sheet.size
    cw, ch = W // 4, H // 3

    atlas = Image.new('RGBA', (CELL_W * len(INGREDIENTS), CELL_H), (0, 0, 0, 0))
    # the sheet reads left-to-right, top-to-bottom in the order the prompt asked for
    order = ['bun_b', 'bun_t', 'patty', 'cheese', 'lettuce', 'tomato',
             'pickle', 'onion', 'bacon', 'egg', 'shroom', 'ice']
    index = {k: i for i, (k, _) in enumerate(INGREDIENTS)}
    for n, key in enumerate(order):
        cell = sheet.crop(((n % 4) * cw, (n // 4) * ch, (n % 4 + 1) * cw, (n // 4 + 1) * ch))
        piece = keyed(cell)
        if key == 'bun_t':
            # the sheet drew a whole little burger in this cell; keep the dome
            t = trim(piece)
            piece = t.crop((0, 0, t.width, int(t.height * 0.56)))
        piece = to_cell(trim(piece))
        atlas.paste(piece, (index[key] * CELL_W, 0))
        print(f'  {key:8s} cell {n} -> slot {index[key]}  {piece.size}')
    # ingredients that were generated on their own rather than on the sheet
    for key, fname in EXTRAS.items():
        piece = to_cell(trim(keyed(Image.open(os.path.join(RAW, fname)).convert('RGB'))))
        atlas.paste(piece, (index[key] * CELL_W, 0))
        print(f'  {key:8s} {fname} -> slot {index[key]}  {piece.size}')
    atlas.save(os.path.join(ART, 'ingredients.png'), optimize=True)

    diner = Image.open(os.path.join(RAW, 'diner.png')).convert('RGB')
    print('diner', diner.size, 'block size', block_size(diner))
    diner.resize((diner.width // SHRINK, diner.height // SHRINK), Image.NEAREST) \
         .save(os.path.join(ART, 'diner.png'), optimize=True)

    json.dump({'cell_w': CELL_W, 'cell_h': CELL_H,
               'slots': [k for k, _ in INGREDIENTS]},
              open(os.path.join(ART, 'atlas.json'), 'w'), indent=1)
    print('atlas', Image.open(os.path.join(ART, 'ingredients.png')).size)
