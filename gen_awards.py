"""Generate the award pictures: each Kaki eating her burger.

One Vertex image-to-image call per character, seeded from her own portrait so the
face survives. These are the reward for getting her order exactly right.

    python3 gen_awards.py           # all missing
    python3 gen_awards.py kaki      # one
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NANO = os.path.expanduser('~/review-doxx-video-claudec/scripts/nano_i2i.py')
OUT = os.path.join(HERE, 'art', 'awards')

KEEP = ('Keep this exact pixel-art character unchanged: same face, same hair, same outfit, '
        'same limited palette, same chunky pixel style with hard pixel edges. ')
SCENE = ('She is sitting in a warm late-night diner booth eating a big burger, holding it in both '
         'hands, mid-bite, delighted. Cosy lamp light, night window behind. ')
TAIL = 'Cute cosy 16-bit game art. No text, no words, no watermark, no border, no signature.'

BEATS = {
    'kaki': 'The burger has a mushroom in it, and she is very pleased about the mushroom.',
    'starcat': 'Her burger is absurdly tall, taller than her head, and she is thrilled about it.',
    'vesper': ('Her burger has exactly one thing in it and she is eating it with enormous '
               'dignity, halo and all.'),
    'rockstar': 'She eats it messily backstage, amp stacks behind her, unbothered.',
    'mermaid': 'Her burger is stacked with green leaves and pickles, and she looks fond of it.',
    'chii': 'She holds it very carefully with both hands and takes a small polite bite.',
    'brasil': 'Her burger has a fried egg in it and morning light comes through the window.',
    'kitty': 'She has stopped crying and is eating happily, eyes shut, paws around the burger.',
    'never': ('Her burger is stacked with a wedge of blue-veined mouldy cheese and she is eating '
              'it completely deadpan, as though nothing unusual is happening.'),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    keys = sys.argv[1:] or list(BEATS)
    for k in keys:
        dst = os.path.join(OUT, f'{k}.png')
        if os.path.exists(dst):
            print(f'{k:9s} already done')
            continue
        src = os.path.join(HERE, 'assets', k, 'source.png')
        prompt = KEEP + SCENE + BEATS[k] + ' ' + TAIL
        r = subprocess.run(['python3', NANO, src, dst, prompt],
                           capture_output=True, text=True, timeout=300)
        ok = os.path.exists(dst)
        tail = (r.stdout.strip().splitlines() or [r.stderr.strip()[:120]])[-1]
        print(f'{k:9s} {"ok" if ok else "FAILED"}  {tail}')
