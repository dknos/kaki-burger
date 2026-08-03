"""Rebuild og.png, the picture that shows up when the link is shared.

Rendered from the game rather than assembled by hand, so the character stands
exactly where she stands at the counter. The old card was put together
separately and had her floating with the floor visible under her feet.

    python3 make_og.py

Takes the diner stage at its native 640x360, drops the top of the frame to reach
1.9:1, and doubles it with nearest-neighbour. No fractional scaling anywhere, so
it stays as crisp as the game.
"""
import os
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NODE = '''
const { chromium } = require('/home/nemoclaw/.nemoclaw/playwright/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({
    executablePath: '/home/nemoclaw/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',
    args: ['--no-sandbox', '--mute-audio'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 1 });
  await p.addInitScript(() => localStorage.clear());
  await p.goto('file://HERE/index.html');
  await p.waitForTimeout(1500);
  await p.click('#open'); await p.waitForTimeout(900);
  await p.click('#svc-go'); await p.waitForTimeout(1800);
  for (const i of ['bun_b', 'patty', 'shroom', 'bun_t']) {
    await p.click(`.ing[data-ing="${i}"]`); await p.waitForTimeout(120);
  }
  await p.waitForTimeout(500);
  await p.locator('#scene').screenshot({ path: 'HERE/.og-stage.png' });
  await b.close();
})();
'''

if __name__ == '__main__':
    js = os.path.join(HERE, '.og.js')
    open(js, 'w').write(NODE.replace('HERE', HERE))
    subprocess.run(['node', js], check=True)
    stage = Image.open(os.path.join(HERE, '.og-stage.png')).convert('RGB')
    w, h = stage.size                       # 640 x 360
    keep = int(round(w / 1.9048))           # 336: the 1.9:1 slice, measured off the floor
    card = stage.crop((0, h - keep, w, h)).resize((w * 2, keep * 2), Image.NEAREST)
    card.save(os.path.join(HERE, 'og-weekend.png'), optimize=True)
    os.remove(js)
    os.remove(os.path.join(HERE, '.og-stage.png'))
    print(f'{card.size[0]}x{card.size[1]} -> og.png')
