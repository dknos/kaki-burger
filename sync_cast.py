"""Pull the sliced cast out of kaki-studio into assets/ and rebuild index.json.

assets/index.json and char_solo.png used to be assembled by hand, which meant a
re-slice in the studio and the art the game actually loads could drift apart.
This is the one command that makes them agree.

    python3 sync_cast.py            # everyone
    python3 sync_cast.py cirno      # one

Anything the game owns and the studio doesn't — Kitty's tears and her dry body,
Mermaid's hand-fixed cutout — is carried over from the existing index rather
than regenerated. Run fix_mermaid.py if her cutout needs rebuilding.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = '/mnt/c/Users/rneeb/Downloads/kaki-studio'
IDX = os.path.join(HERE, 'assets', 'index.json')
CARRY = ('tears', 'paint')               # game-only entries the studio never writes
LIDS = tuple(f'eye{s}_{st}.png' for s in 'LR' for st in ('half', 'meh', 'shut', 'sad'))
MOUTHS = ('mouth_meh.png', 'mouth_sad.png')
FILES = ('char.png',) + LIDS + MOUTHS


def sync(key, index):
    src = os.path.join(STUDIO, 'cast', key)
    dst = os.path.join(HERE, 'assets', key)
    os.makedirs(dst, exist_ok=True)
    man = json.load(open(os.path.join(src, 'manifest.json')))
    old = index.get(key, {})
    for f in FILES:
        p = os.path.join(src, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(dst, f))
    for f in LIDS:
        if not man['eyes'] and os.path.exists(os.path.join(dst, f)):
            os.remove(os.path.join(dst, f))      # she stopped blinking; drop the lids
    for k in CARRY:
        if k in old:
            man[k] = old[k]
    # Only build a cutout that isn't there yet. Mermaid's is hand-fixed
    # (fix_mermaid.py) and the rest were tuned by eye before make_solo.py existed;
    # regenerating them keeps a few hundred more pixels each and puts specks back
    # on faces that are already clean. Delete one to have it rebuilt.
    if not os.path.exists(os.path.join(dst, 'char_solo.png')):
        subprocess.run(['python3', os.path.join(HERE, 'make_solo.py'), key], check=True)
    index[key] = man
    print(f'{key:9s} eyes={len(man["eyes"])} carried={[k for k in CARRY if k in man]}')


if __name__ == '__main__':
    index = json.load(open(IDX))
    for k in (sys.argv[1:] or list(index)):
        sync(k, index)
    json.dump(index, open(IDX, 'w'), indent=1)
    print(f'-> {IDX}')
