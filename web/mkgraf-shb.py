#!/usr/bin/env python3
"""Write lib/pref/graf-shb.prf: Shockbolt tiles (Angband 4.2's 64x64 set,
~/Games/tactical-angband on the Mac) for NPPAngband 0.5.1's
monster.txt / object.txt / terrain.txt / flavor.txt and the S: slots.

Ported from the Zangband template (rvip/templates/zangband/web/mkgraf-shb.py).
Monsters and objects are matched by name against Shockbolt's 4.2 pref; an
entry without a tile of its own gets its family's tile (monsters: same symbol,
same colour if possible; objects: same tval) and is marked "(stand-in)".
Features (by name keywords), flavours (L:, by kind and colour) and the S:
slots are mapped here by hand.  Run from the repo root: python3 web/mkgraf-shb.py"""
import os, re, unicodedata
SHB = os.path.expanduser('~/Games/tactical-angband/lib/tiles/shockbolt')
GD = os.path.expanduser('~/Games/tactical-angband/lib/gamedata')
ED = 'lib/edit'
COLS = 'dwsorgbuDWvyRGBU'
CNAME = ['Dark', 'White', 'Slate', 'Orange', 'Red', 'Green', 'Blue', 'Umber', 'Light Dark',
         'Light Slate', 'Violet', 'Yellow', 'Light Red', 'Light Green', 'Light Blue', 'Light Umber']

def rd(p): return open(p, encoding='latin-1').read()
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', ' ', s.replace('&', '').replace('~', '').lower()).strip()

# --- Shockbolt's 4.2 pref ---
mon, obj, feat, trap, gf = {}, {}, {}, {}, {}
for l in open(f'{SHB}/graf-shb-dark.prf', encoding='utf-8').read().splitlines():
    p = l.split(':')
    if p[0] == 'monster': mon[norm(p[1])] = (p[2], p[3])
    elif p[0] == 'object': obj.setdefault(p[1], {})[norm(p[2])] = (p[3], p[4])
    elif p[0] == 'feat': feat[(p[1], p[2])] = (p[3], p[4])
    elif p[0] == 'trap': trap[(p[1], p[2])] = (p[3], p[4])
    elif p[0] == 'GF': gf[(p[1].split(' |')[0], p[2])] = (p[3], p[4])
flav = {int(m[1]): (m[2], m[3]) for m in re.finditer(r'^flavor:(\d+):(0x\w+):(0x\w+)', rd(f'{SHB}/flvr-shb.prf'), re.M)}

# 4.2 monster glyph/colour -> family tiles
base = dict(re.findall(r'^name:(.*)\nglyph:(.)', rd(f'{GD}/monster_base.txt'), re.M))
fam = {}
for blk in open(f'{GD}/monster.txt', encoding='utf-8').read().split('\nname:')[1:]:
    name = blk.split('\n')[0]
    g = re.search(r'^glyph:(.)', blk, re.M)
    b = re.search(r'^base:(.*)', blk, re.M)
    c = re.search(r'^color:(.)', blk, re.M)
    g = g[1] if g else base.get(b[1]) if b else None
    if g and norm(name) in mon: fam.setdefault(g, []).append((c[1] if c else 'w', mon[norm(name)]))

# 4.2 flavours: kind -> colour letter -> first tile
fl42 = {}
kind = None
for l in rd(f'{GD}/flavor.txt').splitlines():
    p = l.split(':')
    if p[0] == 'kind': kind = p[1]
    elif p[0] in ('flavor', 'fixed') and int(p[1]) in flav:
        col = p[3] if p[0] == 'fixed' else p[2]
        if col in CNAME: fl42.setdefault(kind, {}).setdefault(COLS[CNAME.index(col)], flav[int(p[1])])

def entries(f):
    """(idx, name, glyph, colour, tval, sval) of every N: block"""
    out = []
    for blk in re.split(r'^N:', rd(f'{ED}/{f}'), flags=re.M)[1:]:
        m = re.match(r'(\d+):([^\n]*)', blk)
        g = re.search(r'^G:(.):(.)', blk, re.M)
        i = re.search(r'^I:(\d+):(\d+)', blk, re.M)
        out.append((int(m[1]), m[2], g[1] if g else '?', g[2] if g else 'w',
                    int(i[1]) if i else 0, int(i[2]) if i else 0))
    return out

out, n = [], {'exact': 0, 'stand-in': 0, 'hand': 0}
def put(kind, idx, name, t, how):
    n[how] += 1
    out.append(f'# {name}' + (' (stand-in)' if how == 'stand-in' else ''))
    out.append(f'{kind}:{idx}:{t[0]}/{t[1]}')

# --- Monsters ---
GLYPH = {'Q': 'G', 'N': 'p', 'x': 'X', 'l': 'l', 'I': 'I', 'z': 'z', 'A': 'A', 'U': 'U', 'Y': 'Y',
         'y': 'y', 'm': 'm', '$': '$', '!': '$', '?': '$', '=': '$', '|': '$', '(': '$', '/': '$',
         '~': '$', '*': '*', '.': 'l', '#': 'l', '+': 'l', ',': ',', 'n': 'n', 'j': 'j'}
ALIAS = {'Novice warrior': 'Soldier', 'Novice rogue': 'Cutpurse', 'Novice priest': 'Acolyte',
         'Novice mage': 'Apprentice', 'Novice paladin': 'Warrior', 'Novice ranger': 'Archer',
         'Novice archer': 'Archer', 'Smeagol': 'Sméagol', 'Grip, Farmer Maggot\'s Dog': 'Grip, Farmer Maggot\'s dog',
         'Fang, Farmer Maggot\'s Dog': 'Fang, Farmer Maggot\'s dog'}
out.append('##### Monsters #####')
for idx, name, g, c, _, _ in entries('monster.txt'):
    if idx == 0: continue
    t = mon.get(norm(ALIAS.get(name, name)))
    if t: put('R', idx, name, t, 'exact'); continue
    f = fam.get(g) or fam.get(GLYPH.get(g, g)) or fam['p']
    t = next((tt for cc, tt in f if cc == c), f[0][1])
    put('R', idx, name, t, 'stand-in')

# The player: warrior tile; per class/race from xtra-shb (no $GENDER in NPP prefs)
out.append('R:0:0x83/0x87')
skip = False
for l in rd(f'{SHB}/xtra-shb.prf').splitlines():
    if l.startswith('?:'):
        skip = 'GENDER' in l
        if not skip: out.append(l)
    elif l.startswith('monster:<player>') and not skip:
        p = l.split(':'); out.append(f'R:0:{p[2]}/{p[3].split()[0]}')
out.append('?:1')

# --- Objects ---
TV = {1: 'skeleton', 2: 'bottle', 3: 'junk', 5: 'spike', 7: 'chest',
      16: 'shot', 17: 'arrow', 18: 'bolt', 19: 'bow', 20: 'digger', 21: 'hafted', 22: 'polearm',
      23: 'sword', 30: 'boots', 31: 'gloves', 32: 'helm', 33: 'crown', 34: 'shield', 35: 'cloak',
      36: 'soft armour', 37: 'hard armour', 38: 'dragon armour', 39: 'light', 40: 'amulet',
      41: 'shield', 45: 'ring', 55: 'staff', 65: 'wand', 66: 'rod', 70: 'scroll', 75: 'potion',
      77: 'flask', 80: 'food', 90: 'magic book', 91: 'prayer book', 92: 'nature book', 100: 'gold'}
OBJ_HAND = {'skeleton': ('0x97', '0x8E'), 'bottle': ('0x88', '0x80'), 'junk': ('0x87', '0xB6'),
            'spike': ('0x86', '0xB5'), 'staff': ('0x8A', '0x80'), 'wand': ('0x88', '0x80'),
            'rod': ('0x88', '0x80'), 'potion': ('0x88', '0x80')}
FLV = {40: 'amulet', 45: 'ring', 55: 'staff', 65: 'wand', 66: 'rod', 70: 'scroll', 75: 'potion', 80: 'mushroom'}

# Flavours (NPP flavor.txt: N:idx:tval[:sval], G:char:colour) -> L: lines
flv_tile = {}
out.append('##### Flavours #####')
for blk in re.split(r'^N:', rd(f'{ED}/flavor.txt'), flags=re.M)[1:]:
    m = re.match(r'(\d+):(\d+)', blk)
    g = re.search(r'^G:(.):(.)', blk, re.M)
    d = re.search(r'^D:(.*)', blk, re.M)
    idx, tv = int(m[1]), int(m[2])
    kind = FLV.get(tv)
    if not kind: continue
    tiles = fl42.get(kind) or {}
    c = g[2] if g else 'w'
    t = tiles.get(c) or next(iter(tiles.values()), None) or OBJ_HAND.get(TV.get(tv), ('0x88', '0x80'))
    flv_tile[tv] = flv_tile.get(tv) or t
    out.append(f'# {d[1] if d else idx}')
    out.append(f'L:{idx}:{t[0]}/{t[1]}')

out.append('##### Objects #####')
for idx, name, g, c, tv, sv in entries('object.txt'):
    if idx == 0: continue
    tn = TV.get(tv)
    o = obj.get(tn, {})
    t = o.get(norm(name))
    if t and tv not in FLV: put('K', idx, name, t, 'exact'); continue
    if 90 <= tv <= 92 and tn in obj:          # books: the n-th book of the 4.2 realm
        bl = list(obj[tn].values()); put('K', idx, name, bl[min(sv, len(bl) - 1)], 'hand'); continue
    if tv in FLV and tv != 80:                # drawn from the flavour (L: above)
        put('K', idx, name, flv_tile.get(tv) or OBJ_HAND.get(tn, ('0x88', '0x80')), 'hand'); continue
    if t: put('K', idx, name, t, 'exact'); continue
    if tv == 80 and 'mushroom' in name.lower():
        put('K', idx, name, flv_tile.get(80) or next(iter(o.values())), 'hand'); continue
    if tn in OBJ_HAND: put('K', idx, name, OBJ_HAND[tn], 'hand'); continue
    t = next(iter(o.values()), obj['none']['unknown item'])
    put('K', idx, name, t, 'stand-in')

# --- Features (terrain.txt), by name keywords; the lit variant ---
F = lambda code: feat[(code, 'lit')] if (code, 'lit') in feat else feat[(code, '*')]
T = lambda nm: trap[(nm, 'lit')]
G = lambda el: gf.get((el, 'static')) or gf[('*', 'static')]
FLOOR = F('FLOOR'); GRASS = ('0x97', '0x83'); WATER = ('0x98', '0xE0'); LAVA = ('0x98', '0xD7')
TREE = ('0x9F', '0x83'); PINE = ('0x9F', '0x87'); DEAD = ('0x9F', '0x81'); WILLOW = ('0x9F', '0x86')
SAND = ('0x82', '0xBD')
FEATKW = [
    ('nothing', F('NONE')), ('open floor', FLOOR), ('book shop', F('STORE_BOOK')), ('general store', F('STORE_GENERAL')),
    ('armoury', F('STORE_ARMOR')), ('weapon smith', F('STORE_WEAPON')), ('temple', ('0x99', '0x86')),
    ('alchemy', F('STORE_ALCHEMY')), ('magic shop', F('STORE_MAGIC')), ('black market', F('STORE_BLACK')),
    ('home', F('HOME')), ("adventurer's guild", ('0x96', '0x83')),
    ('glyph of warding', T('glyph of warding')), ('monster trap', T('decoy')),
    ('dagger pit', T('spiked pit')), ('poison spiked pit', T('poison pit')), ('spiked pit', T('spiked pit')),
    ('trap door', T('trap door')), ('pit', T('pit')), ('strange spot', T('teleport rune')),
    ('luminous spot', T('rune of summoning')), ('brown spot', T('acid trap')), ('burning spot', T('fire trap')),
    ('gray dart', T('slow dart')), ('red dart', T('strength loss dart')), ('violet dart', T('dexterity loss dart')),
    ('brown dart', T('constitution loss dart')), ('orange dart', T('slow dart')),
    ('light red gas', T('confusion gas trap')), ('light gray gas', T('sleep gas trap')),
    ('yellow gas', T('poison gas trap')),
    ('broken', F('BROKEN')), ('secret', F('GRANITE')), ('open ', F('OPEN')), ('door', F('CLOSED')),
    ('rubble', F('RUBBLE')), ('magma vein with', F('MAGMA_K')), ('quartz vein with', F('QUARTZ_K')),
    ('magma', F('MAGMA')), ('quartz', F('QUARTZ')), ('permanent', F('PERM')),
    ('up staircase', F('LESS')), ('up shaft', F('LESS')), ('down staircase', F('MORE')), ('down shaft', F('MORE')),
    ('wall of fire', LAVA), ('over lava', F('GRANITE')), ('over boiling', F('GRANITE')), ('over acid', F('GRANITE')),
    ('wall', F('GRANITE')), ('glacier', F('GRANITE')), ('oil shale', F('MAGMA')), ('burning coal', LAVA),
    ('coal', F('MAGMA')), ('silent watcher', F('PERM')), ('loose rock', F('RUBBLE')),
    ('lava', LAVA), ('fire', LAVA), ('burning', LAVA), ('boiling', LAVA), ('geyser', WATER),
    ('water', WATER), ('wave', WATER), ('acid', WATER), ('ice', FLOOR), ('oil', WATER),
    ('sand', SAND), ('mud', SAND), ('dune', SAND),
    ('thicket', WILLOW), ('burnt', FLOOR), ('bush', WILLOW), ('thorns', DEAD), ('brambles', DEAD),
    ('branch', PINE), ('tree', TREE), ('forest soil', GRASS), ('putrid flower', GRASS),
    ('rune', T('rune of necromancy')), ('inscription', T('teleport rune')),
    ('frost', G('COLD')), ('inertia', G('INERTIA')), ('smoke', G('DARK_WEAK')), ('fog', G('DARK_WEAK')),
    ('poison', G('POIS')), ('static', G('ELEC')), ('storm', G('ELEC')), ('steam', G('WATER')),
    ('gravity', G('GRAVITY')), ('sparks', G('ELEC')), ('flashing lite', G('LIGHT_WEAK')),
    ('darkness', G('DARK_WEAK')), ('nether', G('NETHER')), ('chaos', G('CHAOS')),
    ('disenchant', G('DISEN')), ('nexus', G('NEXUS')), ('time', G('TIME')), ('confusion', G('CONFUSION')),
    ('drain life', G('NETHER')), ('shard', G('SHARD')), ('meteor', G('METEOR')),
    ('floor', FLOOR), ('bridge', FLOOR), ('pebbles', FLOOR), ('earth', FLOOR), ('rock', FLOOR),
]
out.append('##### Features #####')
for idx, name, *_ in entries('terrain.txt'):
    nm = name.lower().replace('~', '')
    t = next((v for k, v in FEATKW if k in nm), None)
    if t: put('F', idx, name, t, 'hand')
    else: put('F', idx, name, FLOOR, 'stand-in')

# --- S: slots.  0x30..0x7F bolts (static | - / \ by text colour), 0x80.. flavours ---
GFC = ['DARK_WEAK', 'LIGHT_WEAK', 'SHARD', 'FIRE', 'FIRE', 'POIS', 'COLD', 'GRAVITY', 'DARK_WEAK',
       'SHARD', 'NEXUS', 'LIGHT_WEAK', 'METEOR', 'POIS', 'ELEC', 'SOUND']
out.append('##### Bolts #####')
for base, d in ((0x30, 'static'), (0x40, '90'), (0x50, '0'), (0x60, '45'), (0x70, '135')):
    for k in range(16):
        t = gf.get((GFC[k], d)) or gf[('*', d)]
        out.append(f'S:0x{base + k:02X}:{t[0]}/{t[1]}')

hdr = f"""# File: graf-shb.prf
#
# Shockbolt 64x64 tiles (Raymond Gaustadnes; Angband 4.2 lib/tiles/shockbolt)
# for NPPAngband 0.5.1.  Generated by web/mkgraf-shb.py -- do not edit.
# {n['exact']} entries by name, {n['hand']} mapped by hand, {n['stand-in']} family stand-ins.
"""
open('lib/pref/graf-shb.prf', 'w').write(hdr + '\n'.join(out) + '\n')
print(n)
