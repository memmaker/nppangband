**RVIP port** of NPPAngband 0.5.1 by Jeff Greene and Diego González, from
https://github.com/nppangband/NPPAngband tag `v0.5.1`
([commit `b1d1d85`](https://github.com/nppangband/NPPAngband/tree/b1d1d85a45d454af7d41c7ef307e6ccd9e04d10a),
the first commit here, untouched).
Play: https://ruzzoli.de/roguelikes/nppangband/
Our changes: https://github.com/memmaker/nppangband/compare/b1d1d85...main

NPPAngband ("No Pet Peeves Angband") began as a small set of changes to
Angband 3.0.3 (0.1.0, April 2003) and grew into a variant of its own:
Moria (1985) → Umoria (1989) → Angband 2.x → Angband 3.0.x → NPPAngband
(Jeff Greene; Diego González co-maintainer from 0.4.1). Version
0.5.1 (2011) is rebuilt on Angband 3.1.2v2 code. It keeps the dive to
Sauron and Morgoth on dungeon level 100 and adds terrain that matters (lava,
deep water, ice, mud, forests, burning oil, monsters native to them), quests
from the Adventurer's Guild, themed levels, monster traps, stealing, a Book
Shop and the Druid and Brigand classes. Upstream notes: `readme.txt`,
`NPPchanges.txt`, `AUTHORS`, `THANKS`, `lib/help/`.

What this port adds:
- **Web frontend** `src/main-web.c` (z-term hooks to canvases, Emscripten +
  Asyncify), saves in the browser's IndexedDB, autosave; page
  `web/index.html` + `web/nppangband.js` with the shared `rvip-wm.js`
  windows: Map, Inventory, Visible, Messages, Recall, Equipment, Character,
  Objects. The map view follows the window size, big tiles over two cells.
- **Explore** `H`, **`<` / `>`** walk to the nearest known staircase and take
  it (`src/cmd2.c`).
- **Enter menu**: NPP's own command menu, now on Enter (`src/cmd0.c`);
  **inventory cursor** with item menus (`src/cmd3.c`, `src/cmd-obj.c`);
  no `-more-` stops.
- **Tiles**: Shockbolt (Angband 4.2), mapped to NPP's monsters, objects and
  terrain by `web/mkgraf-shb.py` (`lib/pref/graf-shb.prf`, 99.9%); NPP's own
  sets have no terrain mappings for 0.5.1's rewritten terrain.
- **Sound**: the Dubtrain Angband Sound Pack (`web/dubtrain`), town music;
  both off by default.
- Upstream bug fixes found with AddressSanitizer and the wasm cast check in
  the `port:` commit.

Controls (original keyset): 1–9 / arrows move, Shift runs, `H` explore,
`<` `>` stairs, Enter command menu, `i` / `e` item menus, `g` pick up,
`E` `q` `r` eat / quaff / read, `m` `p` cast / pray, `f` `v` fire / throw,
`O` set a monster trap, `P` steal, `Ctrl+Q` current quest, `?` help,
Ctrl+S save, Ctrl+X save and quit. The Help button opens the game guide.

Build: `sh web/build.sh` → `web/dist` (Homebrew emscripten; see
`web/toolchain.sh`). Deploy: `sh web/deploy.sh`. Notes: `HANDOVER.md`.

Credits: NPPAngband by Jeff Greene and Diego González; Angband 3.1.2v2 by
Andrew Sidwell, 2.8.6–3.0.6 by Robert Ruehlmann, 2.7.0–2.8.5 by Ben
Harrison, 2.0–2.6.2 by Alex Cutler, Andy Astrand, Sean Marsh, Geoff Hill,
Charles Teague and Charles Swiger; VMS Moria by Robert Alan Koeneke and
Jimmey Wayne Todd Jr., Umoria by James E. Wilson. Tiles: Shockbolt ©
Raymond Gaustadnes (from Angband 4.2). Sound: Dubtrain Angband Sound Pack
v3.1.0 by Dubtrain, CC BY 4.0. Web port: memmaker.

Licence: GNU GPL version 2 or the Angband licence, at your choice, as stated
in `COPYING` (Angband licence: "may be copied and distributed for
educational, research, and not for profit purposes provided that this
copyright and statement are included in all such copies").
