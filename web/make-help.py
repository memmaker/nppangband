#!/usr/bin/env python3
"""Writes the in-page game guide (dist/help.html) for the NPPAngband web build,
or with --docs a standalone page (docs/web/nppangband-docs.html) in the shape
of the Docs collection's pages.

On the Mac the game content comes from the desktop key guides in
~/Desktop/Games/Roguelikes/Docs (build-docs.py + guides.py, entry
'nppangband.html'), so both guides stay in sync; without that folder (cloud)
the same content comes from the constants below.  The complete key list is
parsed from lib/help/cmdlist.txt either way.

  python3 web/make-help.py > web/dist/help.html
  python3 web/make-help.py --docs > docs/web/nppangband-docs.html"""
import html, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
esc = html.escape
UPSTREAM = 'b1d1d85'


def kbd(k):
    return ' '.join(f'<kbd>{esc(p)}</kbd>' for p in k.split(' / '))


TAGLINE = ('NPPAngband 0.5.1 (2011) by Jeff Greene and Diego González: an Angband 3.1 variant '
           'with new terrain (lava, water, trees, ice), monster traps, quests from the Adventurer\'s '
           'Guild, themed levels, and a wider range of classes.')

ESSENTIALS = [
    ('Moving', [('1-9 / arrows', 'Walk (numpad or digits; 5 = stay)'), ('Shift + direction', 'Run'),
                ('H', 'Auto-explore'), ('<', 'Go up (walks to a known staircase)'),
                ('>', 'Go down (walks to a known staircase)'), ('R', 'Rest (& = as needed)')]),
    ('Items', [('i', 'Inventory (cursor, Enter = item menu)'), ('e', 'Equipment'), ('g', 'Pick up'),
               ('w', 'Wear / wield'), ('t', 'Take off'), ('d', 'Drop'), ('q', 'Quaff a potion'),
               ('r', 'Read a scroll'), ('E', 'Eat'), ('F', 'Fuel your light')]),
    ('Fighting', [('Move into a monster', 'Attack it'), ('f', 'Fire a missile'),
                  ('h', 'Fire at the nearest target'), ('v', 'Throw'), ('m / p', 'Cast / pray'),
                  ('a / u / z', 'Aim a wand / use a staff / zap a rod')]),
    ('Information', [('Enter', 'Menu of all commands'), ('l', 'Look around'), ('C', 'Character sheet'),
                     ('Ctrl+P', 'Previous messages'), ('Ctrl+Q', 'Your current quest'),
                     ('~', 'Knowledge menus'), ('?', 'In-game help')]),
    ('Game', [('Ctrl+S', 'Save'), ('Ctrl+X', 'Save and quit'), ('=', 'Options'), ('_', 'Enter a store')]),
]

KEY_HINTS = [
    ('?', 'In-game help: every command, with explanations'),
    ('H', 'Auto-explore: walk to the nearest unexplored spot (original keyset)'),
    ('Enter', 'Menu of all commands'),
    ('<', 'Go up (walks to the nearest known staircase)'),
    ('>', 'Go down (walks to the nearest known staircase)'),
    ('Ctrl+S', 'Save'),
]

ABOUT = '''<p><strong>NPPAngband</strong> ("No Pet Peeves Angband") started as a small set of changes to
Angband 3.0 and grew into a variant of its own. Version 0.5.1 is built on Angband 3.1.2 and keeps the
familiar game: descend through 100 levels of dungeon below the town, find better gear, and defeat
Sauron and Morgoth at the bottom.</p>
<ul>
<li><strong>Terrain that matters:</strong> lava, deep water, ice, mud, sand, forests and burning oil,
with some monsters native to them.</li>
<li><strong>Quests</strong> from the Adventurer's Guild in town: kill a unique, clear a pit or nest,
recover an item from a vault, survive a themed level.</li>
<li><strong>Monster traps</strong> (<kbd>O</kbd>) and <strong>stealing</strong> from monsters (<kbd>P</kbd>,
rogues).</li>
<li>Classes Warrior, Mage, Priest, Rogue, Ranger, Paladin, Druid and Brigand; a Book Shop (<kbd>0</kbd>);
item squelching to hide junk.</li>
</ul>'''

TIPS = '''<ul>
<li>Pick <strong>Warrior</strong> for a first game: no spells to learn, the most hit points.</li>
<li>Buy <strong>Flasks of oil</strong> in the General Store: they are a strong thrown weapon early
(<kbd>v</kbd>) and fuel for a lantern.</li>
<li>Carry <strong>Cure Light Wounds</strong> potions and a <strong>Word of Recall</strong> scroll; recall
takes you between town and your deepest level.</li>
<li><kbd>H</kbd> explores until something interesting happens; press it again after each stop.
<kbd>&gt;</kbd> anywhere walks to the nearest known down staircase and takes it.</li>
<li>Rest (<kbd>R</kbd> <kbd>&amp;</kbd>) before opening doors and after fights.</li>
<li>Look at a monster (<kbd>l</kbd>, then <kbd>r</kbd>) to read what you know about it.</li>
</ul>'''

GUIDE = [
    ('Your first character', '''<p>After the splash screen choose sex, race and class with the cursor keys and
<kbd>Enter</kbd> (or the letters), accept the point-based stats with <kbd>Enter</kbd> and type a name. You
start in town with some gold: visit the General Store (<kbd>1</kbd>) for food, torches and flasks of oil,
the Alchemist (<kbd>5</kbd>) for Cure Light Wounds potions. Walk onto a shop's number to enter it.</p>'''),
    ('The dungeon', '''<p>Take the down staircase <kbd>&gt;</kbd> in town. Each level is new every time you
enter it. The deeper you go, the better the items and the stronger the monsters: dive only as fast as
your character level allows (a common rule: dungeon level no deeper than your character level early on).</p>'''),
    ('Items and identification', '''<p>Unknown potions and scrolls are learned by use. Press <kbd>i</kbd>, move
the cursor with <kbd>2</kbd>/<kbd>8</kbd> and press <kbd>Enter</kbd> (or the item's letter) for a menu of
what you can do with it. Wearable items tell you more after you have worn them for a while.</p>'''),
    ('Quests', '''<p>The Adventurer's Guild (<kbd>9</kbd> in town) offers quests. <kbd>Ctrl+Q</kbd> shows the
current one. Rewards are gold, items or a boost from the guild.</p>'''),
]

SAVING = '''<ul>
<li><strong>Saving is automatic.</strong> Every save goes straight into this browser's storage (IndexedDB). The game saves every two minutes while it waits for your next command, and whenever you switch to another tab or window.</li>
<li><kbd>Ctrl+S</kbd> saves and keeps playing. <kbd>Ctrl+X</kbd> saves and quits; reload the page (or press <em>Play again</em>) to continue.</li>
<li>Each browser keeps <strong>one character</strong>. <em>New character</em> deletes it and starts over. When your character dies, the next game starts after the tombstone.</li>
<li><em>Export save</em> downloads your savefile; <em>Import save</em> loads one. Use them to keep a backup or to move a character to another browser or computer.</li>
<li>Your window layout, zoom levels, window titles and the Tiles/Sound/Music buttons are stored in the same browser storage and survive a new character.</li>
<li>Private/incognito windows and "clear site data" delete the stored game. Export first if the character matters.</li>
</ul>'''

WEB = '''<ul>
<li><strong>Windows:</strong> the map fills the big window; Inventory and Visible (monsters in view) are on the right, Messages along the bottom. Recall, Equipment, Character and Objects can be turned on under <em>Windows</em>.</li>
<li><strong>Resize windows</strong> by dragging the gaps between them; the game redraws them at their new size.</li>
<li><strong>Zoom:</strong> <em>Zoom −</em> / <em>Zoom +</em> change the size of the map tiles.</li>
<li><strong>Keys:</strong> arrow keys, the numeric keypad or <kbd>1</kbd>–<kbd>9</kbd> move you; <kbd>Shift</kbd> + direction runs. There is no mouse support in this port.</li>
<li><strong>Tiles</strong> switches between the Shockbolt tiles and text. <strong>Sound</strong> and <strong>Music</strong> are off by default; Music plays a town tune on the surface.</li>
<li>Browsers keep a few shortcuts for themselves (<kbd>Ctrl+W</kbd>, <kbd>Ctrl+T</kbd>, <kbd>Ctrl+N</kbd>), so those never reach the game.</li>
<li>If the game ever crashes, a message appears at the top; reload the page to continue from your last save.</li>
</ul>'''

CREDITS = '''<ul>
<li><strong>NPPAngband</strong> 0.4.1 and later: Jeff Greene and Diego González (co-maintainers). See the game's <code>AUTHORS</code> and <code>THANKS</code>.</li>
<li><strong>Angband</strong> 3.1.2v2, maintained by Andrew Sidwell; earlier Robert Rühlmann (2.8.6–3.0.6), Ben Harrison (2.7.0–2.8.5), Alex Cutler, Andy Astrand, Sean Marsh, Geoff Hill, Charles Teague, Charles Swiger (2.0–2.6.2); based on VMS Moria by Robert Alan Koeneke and Jimmey Wayne Todd Jr.</li>
<li>Licence: GNU GPL version 2 or the Angband licence, as stated in <code>COPYING</code>.</li>
<li><strong>Tiles:</strong> Shockbolt 64x64 tile set © Raymond Gaustadnes (from Angband 4.2).</li>
<li><strong>Sounds:</strong> Dubtrain Angband Sound Pack v3.1.0 by Dubtrain (dubtrain.com/angband), Creative Commons Attribution 4.0.</li>
<li><strong>Music:</strong> town tune from the Quickband web port.</li>
</ul>'''


# Desktop Docs entry, when it exists, wins (same fields)
DOCS = os.path.expanduser('~/Desktop/Games/Roguelikes/Docs')
PAGE = 'nppangband.html'
if os.path.exists(os.path.join(DOCS, 'build-docs.py')) and not os.environ.get('NPP_NO_DOCS'):
    sys.path.insert(0, DOCS)
    spec = importlib.util.spec_from_file_location('build_docs', os.path.join(DOCS, 'build-docs.py'))
    docs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docs)
    from guides import GUIDES   # noqa: E402
    game = next((g for g in docs.GAMES if g['file'] == PAGE), None)
    if game and PAGE in GUIDES:
        info = dict(game['info'])
        TAGLINE, ESSENTIALS, TIPS, CREDITS = game['tagline'], game['essentials'], info['Tips'], info['Credits']
        ABOUT, GUIDE = GUIDES[PAGE][0][1], GUIDES[PAGE][1:]


def all_keys():
    """(key, description) of the original keyset, from lib/help/cmdlist.txt"""
    t = open(os.path.join(HERE, '../lib/help/cmdlist.txt'), encoding='latin-1').read()
    t = t.split('Command Summary -- Original keyset')[1].split('======')[0]
    out = []
    for line in t.splitlines():
        for m in re.finditer(r'(\^?\S)\s\s(.+?)(?=\s{3,}\^?\S\s\s|$)', line.strip()):
            k, d = m[1], m[2].strip()
            if d.startswith('(') or d in ('Unused', '{reserved}'): continue
            out.append(('Ctrl+' + k[1] if k.startswith('^') and len(k) == 2 else k, d))
    return out


def dl(items):
    return '<dl>' + ''.join(f'<dt>{kbd(k)}</dt><dd>{esc(d)}</dd>' for k, d in items) + '</dl>'


def section(anchor, title, body):
    return f'<h2 id="h-{anchor}">{esc(title)}</h2>{body}'


def body():
    parts = []
    toc = [('about', 'About the game'), ('keys', 'Keyboard controls'), ('saving', 'Saving your game'),
           ('tips', 'Tips'), ('guide', "New player's guide"), ('web', 'Playing in the browser'),
           ('credits', 'Credits')]
    parts.append('<p>' + esc(TAGLINE) + '</p><ul class="toc">' +
                 ''.join(f'<li><a href="#h-{a}">{esc(t)}</a></li>' for a, t in toc) + '</ul>')
    parts.append(section('about', 'About the game', ABOUT))
    ess = ''.join(f'<div class="box"><h3>{esc(cat)}</h3>{dl(items)}</div>' for cat, items in ESSENTIALS)
    keys = all_keys()
    full = ''.join(f'<div>{kbd(k)}<span>{esc(d)}</span></div>' for k, d in keys)
    parts.append(section('keys', 'Keyboard controls',
                         '<div class="box key"><h3>The keys to remember</h3>' + dl(KEY_HINTS) + '</div>'
                         '<h3>Essential keys</h3><div class="grid">' + ess + '</div>'
                         '<details><summary>Complete key list (' + str(len(keys)) + ' commands, original keyset)</summary>'
                         '<div class="all">' + full + '</div></details>'))
    parts.append(section('saving', 'Saving your game', SAVING))
    parts.append(section('tips', 'Tips', TIPS))
    parts.append(section('guide', "New player's guide", ''.join(f'<h3>{esc(t)}</h3>{b}' for t, b in GUIDE)))
    parts.append(section('web', 'Playing in the browser', WEB))
    parts.append(section('credits', 'Credits', CREDITS))
    parts.append('<h2 id="h-version">About this version</h2><ul>'
                 '<li>Based on <strong>NPPAngband 0.5.1</strong>.</li>'
                 f'<li>Original source: <a href="https://github.com/nppangband/NPPAngband/tree/{UPSTREAM}" target="_blank" rel="noopener">nppangband/NPPAngband, tag v0.5.1 (commit {UPSTREAM})</a></li>'
                 '<li>Our changes (port, auto-explore, command and item menus, tiles, web build): '
                 f'<a href="https://github.com/memmaker/nppangband/compare/{UPSTREAM}...main" target="_blank" rel="noopener">memmaker/nppangband</a></li></ul>')
    return '\n'.join(parts)


DOC = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NPPAngband keys</title>
<style>
:root { --bg: #0b0b0d; --panel: #16161a; --line: #2b2b33; --text: #d8d8de; --dim: #8a8a96; --accent: #d9b24c; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.55 system-ui, sans-serif; }
main { max-width: 980px; margin: 0 auto; padding: 24px 16px 60px; }
h1 { color: var(--accent); margin: 0 0 6px; }
h2 { font-size: 19px; margin: 28px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }
h3 { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--accent); margin: 18px 0 8px; }
a { color: var(--accent); }
kbd { display: inline-block; min-width: 1.2em; padding: 0 5px; font: 13px/1.6 ui-monospace, monospace; text-align: center;
  background: #22222a; border: 1px solid #3a3a46; border-bottom-width: 2px; border-radius: 4px; }
.toc { display: flex; flex-wrap: wrap; gap: 6px; padding: 0; list-style: none; }
.toc a { display: block; padding: 3px 10px; border: 1px solid var(--line); border-radius: 12px; text-decoration: none; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.box { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 4px 14px 10px; }
dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; margin: 0; }
dd { margin: 0; color: var(--text); }
.all { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 4px 16px; margin-top: 10px; }
.all span { margin-left: 8px; }
details summary { cursor: pointer; color: var(--accent); margin-top: 14px; }
</style></head>
<body><main><h1>NPPAngband</h1>
%s
</main></body></html>
'''

if __name__ == '__main__':
    print(DOC % body() if '--docs' in sys.argv else body())
