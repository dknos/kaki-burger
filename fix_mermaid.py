"""Rebuild Mermaid's cutout. She is the one portrait the generic slicer can't do.

Two things make her different from the other seven:

  * her artwork sits inside a drawn picture frame, and that frame walls her
    backdrop off from the image border, so the border flood never reaches it;
  * that backdrop is vertical stripes in three colours she also wears, so a
    colour flood seeded inside the frame walks straight into her hair and eats
    holes out of it.

So: sample the stripe palette off a row that is all backdrop, drop every pixel
wearing one of those colours, then fill back anything that turns out to be
enclosed by her. Backdrop stripes reach the edge of the frame and stay dropped;
the white shell in her hair and the pale of her face are surrounded by her own
hair, so they come back. Clip the drawn frame off geometrically at the end.
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, 'assets', 'mermaid')

TOP_ROW = 22                       # a row that is entirely backdrop
SAMPLE = (28, 272)                 # x range of a row that is entirely backdrop
INNER = (20, 292, 18, 280)         # the drawn frame lives outside this
# The shell in her hair sits right against the frame, so the original border
# flood took half of it for background before this script ever runs. Put it back
# from the source, by its own colours, inside its own box.
SHELL_BOX = (56, 148, 18, 94)
SHELL_COLS = [(248, 246, 245), (190, 164, 146), (221, 208, 200), (211, 189, 173)]


def main():
    src = np.array(Image.open(os.path.join(D, 'source.png')).convert('RGB')).astype(int)
    char = np.array(Image.open(os.path.join(D, 'char.png')).convert('RGBA'))
    H, W = src.shape[:2]

    pal = {tuple(int(v) for v in src[TOP_ROW, x]) for x in range(*SAMPLE)}
    stripe = np.zeros((H, W), bool)
    for c in pal:
        stripe |= np.all(src == np.array(c), axis=2)

    inner = np.zeros((H, W), bool)
    inner[INNER[0]:INNER[1], INNER[2]:INNER[3]] = True

    her = (char[:300, :, 3] > 0) & inner & ~stripe

    shell = np.zeros((H, W), bool)
    for c in SHELL_COLS:
        shell |= np.all(src == np.array(c), axis=2)
    box = np.zeros((H, W), bool)
    box[SHELL_BOX[0]:SHELL_BOX[1], SHELL_BOX[2]:SHELL_BOX[3]] = True
    her |= (shell & box)

    her = ndimage.binary_fill_holes(her)          # her face comes back
    lab, n = ndimage.label(her)
    sizes = ndimage.sum(her, lab, range(1, n + 1))
    her = ndimage.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)

    out = char.copy()
    out[:300, :, 3] = np.where(her, 255, 0)
    out[300:, 3] = 0
    Image.fromarray(out).save(os.path.join(D, 'char_solo.png'), optimize=True)
    ys, xs = np.where(her)
    print(f'mermaid: {len(pal)} stripe colours, {her.mean():.1%} kept, '
          f'x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}, {n} pieces considered')


if __name__ == '__main__':
    main()
