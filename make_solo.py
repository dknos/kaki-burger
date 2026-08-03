"""Cut one character free of her leftovers: char.png -> char_solo.png.

The background flood keeps whatever it could not reach — sparkles in the air,
a corner the walk never got into. Those read as floating grit once she is
standing in the diner. Keeping only the components that are actually part of
her (the biggest one, and anything within a few pixels of it) drops the grit
without touching her.

    python3 make_solo.py never
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = '/mnt/c/Users/rneeb/Downloads/kaki-studio'


def solo(key, near=6):
    src = os.path.join(STUDIO, 'cast', key, 'char.png')
    a = np.array(Image.open(src).convert('RGBA'))
    alpha = a[..., 3] > 8
    lab, n = ndimage.label(alpha)
    if n:
        sizes = ndimage.sum(alpha, lab, range(1, n + 1))
        main = int(np.argmax(sizes)) + 1
        body = lab == main
        # anything touching her within `near` px is hers: a bow, a loose braid
        reach = ndimage.binary_dilation(body, np.ones((3, 3), bool), iterations=near)
        keep = np.isin(lab, [i + 1 for i in range(n) if (reach & (lab == i + 1)).any()])
    else:
        keep = alpha
    a[..., 3] = np.where(keep, a[..., 3], 0)
    for d in (os.path.join(STUDIO, 'cast', key), os.path.join(HERE, 'assets', key)):
        Image.fromarray(a).save(os.path.join(d, 'char_solo.png'), optimize=True)
    print(f'{key}: {n} components -> kept {keep.mean():.3f} of frame')


if __name__ == '__main__':
    for k in sys.argv[1:]:
        solo(k)
