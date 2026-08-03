"""Camper's eyebrows, drawn rather than sliced.

Her portrait has no brows under the fringe, and without them she reads blank next
to the rest of the cast. There is nothing in the art to detect, so this draws
them: one tapered arc per eye, in a navy dark enough to hold against her hair.

It writes an export in the same shape paint.html produces, so it goes in through
the same door as a hand edit:

    python3 draw_brows.py && python3 apply_paint.py && python3 gen_scenes.py

Numbers are in her 300px source space. Her eyes are at x88-152 (top 138) and
x197-250 (top 130), so each brow sits a few pixels above its own eye and tilts
up towards the nose.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS = '/mnt/c/Users/rneeb/Downloads'
INK = (36, 52, 104, 255)          # navy: black went flat against her slate hair


def brow(px, inner_x, outer_x, inner_y, outer_y, th_in=13.0, th_mid=14.0, bump=6.0):
    """Inner end to outer tip.

    Blunt and thick where it meets the nose, arcing up over the middle, tapering
    to a point on the way out. The first pass drew an even 6px stroke and it read
    as a pencil line rather than a brow — the taper is the whole shape.
    """
    n = abs(outer_x - inner_x)
    step = 1 if outer_x > inner_x else -1
    for i in range(n + 1):
        u = i / n
        x = inner_x + step * i
        y = inner_y + (outer_y - inner_y) * u - bump * 4 * u * (1 - u)
        th = (th_in + (th_mid - th_in) * (u / 0.30) if u < 0.30
              else th_mid * (1.0 - ((u - 0.30) / 0.70) ** 1.35))
        top = int(round(y - max(1.0, th) / 2))
        for d in range(max(1, int(round(th)))):
            px[top + d, x] = INK


if __name__ == '__main__':
    a = np.array(Image.open(os.path.join(HERE, 'assets', 'never', 'char_solo.png')
                            ).convert('RGBA'))
    brow(a, 152, 86, 126, 137)      # her left: inner at the nose, tip out past the eye
    brow(a, 197, 254, 116, 128)     # her right
    out = os.path.join(DOWNLOADS, 'never__idle.png')
    Image.fromarray(a).save(out)
    print(f'-> {out}\nnow run: python3 apply_paint.py')
