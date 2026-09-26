#!/usr/bin/env python3
"""Coverage of a tile set over every monster (monster.txt), object
(object.txt) and feature (terrain.txt) entry of NPPAngband 0.5.1.  An entry
counts when the pref maps it to a non-empty tile inside the sheet.

  python3 web/tile-coverage.py            Shockbolt (graf-shb.prf, 64x64)
  python3 web/tile-coverage.py dvg        own 32x32 set (graf-dvg.prf, David Gervais)
  python3 web/tile-coverage.py new        own 16x16 set (graf-new.prf, Adam Bolt)"""
import re, sys, os
from PIL import Image
L = 'lib'
arg = sys.argv[1:] and sys.argv[1]
if arg == 'dvg':
    prefs, sheet, S = ['graf-dvg.prf'], f'{L}/xtra/graf/32x32.png', 32
elif arg == 'new':
    prefs, sheet, S = ['graf-new.prf'], f'{L}/xtra/graf/16x16.png', 16
else:
    prefs, sheet, S = ['graf-shb.prf'], 'rvip/templates/tactical-angband/lib/shockbolt/64x64.png', 64
    if not os.path.exists(sheet):
        sheet = 'web/tiles.webp'
img = Image.open(sheet).convert('RGBA')
W, H = img.size
def tile_ok(a, c):
    x, y = (c & 0x7F) * S, (a & 0x7F) * S
    if not (a & 0x80 and c & 0x80) or x + S > W or y + S > H:
        return False
    return img.crop((x, y, x + S, y + S)).getbbox() is not None
maps, stand = {}, set()
prev = ''
for pref in prefs:
    for line in open(f'{L}/pref/{pref}', encoding='latin-1'):
        m = re.match(r'([RKF]):(\d+):(0x[0-9A-Fa-f]+|\d+)[:/](0x[0-9A-Fa-f]+|\d+)', line)
        if m:
            maps[(m[1], int(m[2]))] = tile_ok(int(m[3], 0), int(m[4], 0))
            if prev.endswith('(stand-in)'): stand.add((m[1], int(m[2])))
        prev = line.rstrip()
tot = hit = 0
for kind, f in (('R', 'monster'), ('K', 'object'), ('F', 'terrain')):
    ids = [int(x) for x in re.findall(r'^N:(\d+):', open(f'{L}/edit/{f}.txt', encoding='latin-1').read(), re.M)]
    ok = [i for i in ids if maps.get((kind, i))]
    miss = [i for i in ids if not maps.get((kind, i))]
    si = sum((kind, i) in stand for i in ok)
    print(f'{f}: {len(ok)}/{len(ids)} ({si} family stand-ins)  missing: {miss[:20]}{" ..." if len(miss) > 20 else ""}')
    tot += len(ids); hit += len(ok)
print(f'total: {hit}/{tot} = {100 * hit / tot:.1f}%, family stand-ins: {len(stand)}')
