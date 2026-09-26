#!/usr/bin/env python3
"""Write the web build's sound.cfg (NPPAngband event names) from the Dubtrain
pack (web/dubtrain: Angband 4.2's mp3 copy + sound.prf) and copy the used
files.  NPP's events (angband_sound_name[] in src/variable.c) are the 3.x
names; Angband 4.2's sound.prf uses the same names in upper case.
Usage: sounds.py <sound.cfg to write> <sound dir>"""
import os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, 'dubtrain')
# NPP event -> 4.2 events, where the names differ or 4.2 has none; 'walk' stays silent.
MAP = {'walk': '', 'identify_bad': 'IDENT_BAD', 'identify_ego': 'IDENT_EGO', 'identify_art': 'IDENT_ART',
       'breathe_elements': 'BR_ELEMENTS', 'breathe_confusion': 'BR_CHAOS', 'breathe_disenchant': 'BR_DISEN',
       'summon_monster': 'SUM_MONSTER', 'summon_angel': 'SUM_AINU', 'summon_undead': 'SUM_UNDEAD',
       'summon_animal': 'SUM_ANIMAL', 'summon_spider': 'SUM_SPIDER', 'summon_hound': 'SUM_HOUND',
       'summon_hydra': 'SUM_HYDRA', 'summon_demon': 'SUM_DEMON', 'summon_dragon': 'SUM_DRAGON',
       'summon_gr_undead': 'SUM_HI_UNDEAD', 'summon_gr_dragon': 'SUM_HI_DRAGON',
       'summon_gr_demon': 'SUM_HI_DEMON', 'summon_ringwraith': 'SUM_WRAITH', 'summon_unique': 'SUM_UNIQUE',
       'pseudo_id': 'NOTICE', 'mon_create_trap': 'CREATE_TRAP', 'mon_shriek': 'SHRIEK',
       'mon_cast_fear': 'CAST_FEAR', 'cast_spell': 'SPELL', 'pray_prayer': 'PRAYER',
       'losing_nativity': 'NOTICE', 'losing_flying': 'NOTICE', 'hide_unhide': 'RUNE'}
for b in ('frost', 'elec', 'acid', 'gas', 'fire', 'chaos', 'shards', 'sound', 'light', 'dark', 'nether',
          'nexus', 'time', 'inertia', 'gravity', 'plasma', 'force'):
    MAP['breathe_' + b] = 'BR_' + b.upper()
src = open(os.path.join(HERE, '../src/variable.c'), encoding='latin-1').read()
src = src.split('angband_sound_name[MSG_MAX] =')[1].split('};')[0]
EVENTS = re.findall(r'"(\w*)"', src)
pack = {}
for line in open(os.path.join(PACK, 'sound.prf'), encoding='latin-1'):
    m = re.match(r'sound:(\w+):(.*)', line.strip())
    if m:
        pack[m[1]] = [f + '.mp3' for f in m[2].split() if os.path.exists(os.path.join(PACK, f + '.mp3'))]
cfg_path, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
lines = ['# NPPAngband web build: Dubtrain Angband Sound Pack v3.1.0 (web/sounds.py)', '[Sound]']
silent = []
for e in EVENTS:
    if not e: continue
    names = MAP.get(e, e.upper()).split()
    files = sorted({f for d in names for f in pack.get(d, [])})
    if not files: silent.append(e)
    for f in files:
        shutil.copy(os.path.join(PACK, f), out)
    lines.append(f'{e} = {" ".join(files)}')
open(cfg_path, 'w').write('\n'.join(lines) + '\n')
print(f'{len(EVENTS) - 1} events, {len(os.listdir(out))} files, silent: {" ".join(silent)}')
