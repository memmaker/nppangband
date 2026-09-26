# NPPAngband 0.5.1: handover

## Cloud experiment (read this first)

(Since stage 7 the `rvip/` bundle, `web/shots/` and `rvip/LESSONS.md` exist only
in the private cloud history: memmaker/nppangband-cloud, `~/Games/nppangband-cloud`.
This public repo is that history filtered with `git filter-repo`.)

This repo runs the RVIP import in a Claude Code **cloud** session. Everything
the procedure normally takes from sibling folders on the maintainer's Mac is
bundled under `rvip/`:

- `rvip/RVIP.md` — the procedure (snapshot; the canonical copy lives on the
  Mac). **Write lessons into `rvip/LESSONS.md`** (new file, one bullet per
  lesson naming the RVIP section it belongs to); never edit `rvip/RVIP.md`.
- `rvip/web/rvip-wm.js`, `rvip/web/rvip-sound.js` — shared page code every
  game loads (window manager, sound). Use, don't fork.
- `rvip/templates/zangband/` — the newest complete case-A (z-term) web port
  of a 2.x/3.0-era code base: `main-web.c` (z-term web frontend),
  `web/build.sh` (emcc + Asyncify + IDBFS), `web/zangband.js` +
  `web/index.html` (page with rvip-wm.js windows, tiles blit, sound),
  `web/mkgraf-shb.py` (Shockbolt pref generator; edit its `SHB`/`GD` paths
  to `rvip/templates/tactical-angband/lib/tiles/shockbolt` and
  `.../lib/gamedata`), `web/tile-coverage.py`, `web/sounds.py` (edit `PACK`
  to `rvip/templates/dubtrain`), `web/make-help.py`, `graf-shb.prf`
  (example output), `HANDOVER.md` (all nine stage sections: copy its
  solutions).
- `rvip/templates/tactical-angband/` — Shockbolt: `tiles.webp`, the prefs,
  4.2 `gamedata` for name matching, `lib/pref/`. Only needed if the game's
  own set falls below the coverage rule.
- `rvip/templates/dubtrain/` — the Dubtrain Angband Sound Pack for stage 6.

**The game.** NPPAngband 0.5.1 (tag `v0.5.1`, commit `b1d1d85`, upstream
github.com/nppangband/NPPAngband, remote `upstream`; full history; our
commits go on top on `main`). Angband 3.0.x-based variant by Jeff Greene
and Diego Gonzalez (see `AUTHORS`, `THANKS`, `readme.txt`, `NPPchanges.txt`,
`COPYING`: Angband licence / GPL as stated). Plain C, `src/main-*.c`, z-term.
Case **A**; read RVIP.md Part A (A0–A6b, A-Zangband, A-FrogComposband,
A-Hengband) and Part W. Build from `src/Makefile.inc`'s source list.

**Tiles:** the game ships `lib/xtra/graf/8x8.png`, `16x16.png` (Adam Bolt)
and `32x32.png` (David Gervais) with `lib/pref/graf-*.prf`. Count coverage
of the 32x32 set and the 16x16 set against every `N:` entry of
`lib/edit/monster.txt`, `object.txt`, `terrain.txt` (and flavours/traps if
they are drawable) with a script like `tile-coverage.py`; pick the largest
set with ≥95%; if none reaches it, Shockbolt from the bundle (the Zangband
way, family stand-ins, report the numbers). One set, never mix.

**Differences from a local run**
- No browser pane and no ruzzoli.de deploy key. Stages 1–6 are in scope.
  Tests: Playwright/Chromium (`/opt/pw-browsers` or `npx playwright install
  chromium`) driving `web/dist` served by `python3 -m http.server`:
  character creation, random keys, save/reload/restore, explore, stairs,
  menus, tiles (canvas pixels), screenshots into `web/shots/`. Write
  `web/deploy.sh` like the template's (target
  `ruzzoli.de/roguelikes/nppangband/`); never run it.
- Toolchain: Emscripten (`git clone https://github.com/emscripten-core/emsdk
  && ./emsdk install latest && ./emsdk activate latest`, ~2 min), gcc/clang
  for the native ASan build (`-DUSE_GCU` curses + pty + random keys,
  isolated `HOME`; `pyte` in a venv). Record every command in
  `web/toolchain.sh`. If Emscripten cannot be installed, write that file with
  what you tried and the errors, commit, push, stop.
- Commit after every stage (`RVIP: stage N <topic>`) and **push to `origin`**
  (github.com/memmaker/nppangband, private). Every commit message ends with
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never force-push.
- Never `fetch()` `.cfg`/`.prf` files from the page: stage them into the
  preload and read them with `Module.FS.readFile` (the template's
  `loadSoundCfg()`).
- The Docs page (stage 6) is not here: write `docs/web/nppangband-docs.html`
  in the shape of the template's `make-help.py` output and note it for the
  Mac side.

## RVIP progress

### Stage 1 (get + build): done 2026-09-26 (cloud)
- Base: NPPAngband 0.5.1, tag `v0.5.1` = `b1d1d85` (upstream
  nppangband/NPPAngband). **Case A**, but the code is **3.1-era Angband**
  (`game-cmd.c`, `ui-menu.c`, `ui-event.h`, `cmd-obj.c`, `obj-ui.c`,
  `Makefile.src` says 3.1.2v2): closer to Quickband than to Zangband.
- Toolchain: `web/toolchain.sh` — emsdk `latest` = **emcc 6.0.10** in
  `/home/user/emsdk` (first try, ~2 min); `pip install pillow pyte`;
  gcc + libncurses-dev for ASan; global Playwright 1.56.1 + `/opt/pw-browsers`.
- Web frontend: `src/main-web.c` (Zangband template adapted to NPP's z-term):
  registered as `"x11"` in `modules[]` of `src/main.c` (plain
  `init_web(int, char **)`, no cast), `quit_aux = quit_hook` under
  `#ifndef USE_WEB`. 8 terms (`WEB_TERMS`, = `ANGBAND_TERM_MAX`): Map,
  Inventory, Messages, Visible (`PW_MONLIST`), Recall, Equipment, Character
  (`PW_PLAYER_0`), Objects (`PW_ITEMLIST`); flags set for new characters by
  `web_new_character()` (called in `dungeon.c` right after `player_birth()`;
  `init_angband()` zeroes `op_ptr->window_flag[]` after `init_web()` ran).
  Option defaults: `options[OPT_auto_more/OPT_center_player].normal = TRUE`
  in `init_web()`. Sound: 3.1 `sound_hook` → `js_sound(angband_sound_name[v])`
  (not `TERM_XTRA_SOUND`); `use_sound` is `op_ptr->opt[OPT_use_sound]`, forced on.
- Page: `web/index.html`, `web/nppangband.js` (from `zangband.js`: `/nppangband/lib`
  paths, IDBFS on `lib/save|user|apex|bone`, save `0.PLAYER` via `-uPLAYER`,
  8 windows), shared `rvip/web/rvip-wm.js` copied by the build, town music
  `web/music/new_town.ogg` (vendored from the template). Text only for now
  (`TILE_SRC = ''` in the JS). `pict()` knows NPP's bigtile: the pad cell is
  `255/0xFF` after the tile, `js_pict(..., use_bigtile)`.
- Build: `sh web/build.sh` (source `emsdk_env.sh` first) → `web/dist`:
  `ZFILES` + `ANGFILES` of `src/Makefile.src` + `main.c main-web.c`,
  `emcc -O2 -fcommon -std=gnu99 -DUSE_WEB -w`, `-sASYNCIFY
  -sASYNCIFY_STACK_SIZE=65536 -sSTACK_SIZE=1048576 -sALLOW_MEMORY_GROWTH
  -sINITIAL_MEMORY=64MB -sFORCE_FILESYSTEM -lidbfs.js -sENVIRONMENT=web`,
  preload `lib/{edit,file,help,pref}` as `/nppangband/lib`. ~25 s, no
  wasm-ld warnings; `-Wcast-function-type-strict` over all sources is clean
  after the option-menu wrappers.
- Port edits (`USE_WEB`): `config.h` no `PRIVATE_USER_PATH`; `z-file.c`
  `safe_setuid_drop/grab()` empty (setegid failed → quit at start);
  `save.c` `web_sync_files()` at the end of `save_player()`; `main.h`
  prototypes; `externs.h` `web_sync_files()`, `web_new_character()`.
- Quirks: globals `inkey_flag`, `character_generated`, `p_ptr->is_dead`,
  `p_ptr->depth`; z-term has `TERM_XTRA_CLEAR` and `bigcurs_hook` but **no
  resize hooks** (web_apply_layout() calls `do_cmd_redraw()` for the main
  term / `handle_stuff()` for sub-windows, as main-sdl.c does). Ctrl-X asks
  "Press Return (or Escape)" and shows the scores before `quit()`.
  Birth: splash key, then menus `a` (sex) `a` (race) `a` (class) `a`
  (point-based), Enter accepts points, name prompt (typing replaces
  PLAYER), any key on the sheet → town (night: only shop numbers visible).
- ASan: `sh web/asan.sh` (native `-DUSE_GCU`, objects and a copy of lib in
  `/tmp/npp-asan`, user dir forced to `./lib/user` because
  `path_parse("~")` uses `getpwuid()`, not `$HOME`) + `python3
  web/asan-keys.py SEED NEW RESTORED [extra keys]` (pty + pyte, birth by
  screen text, Ctrl-X save, restart on the save). 6 seeds × (2500–3000 new
  + 1500–2000 restored). Upstream bugs fixed in `port:` commit `4090971`:
  `init1.c` `%lu` into u32b; `calcs.c` stat index −3 during birth reset;
  `squelch.c` `seen_type[]` one short and `tv_to_type[]` with tval ≥ 100;
  `object1.c` discount string out of scope; `load.c` 8-byte header into
  `vvv[4]`; `cmd4.c` macro trigger burst overflow, option menu function
  casts (would trap in wasm), `<0x>` in the message window. Then clean.
- Browser test (Playwright, `node web/test/stage1.mjs SEED N`, headless
  Chromium against `python3 -m http.server` on `web/dist`): birth (Human
  Warrior "Tester") → town → 400/600/800 random keys (seeds 1–3, reached
  50 ft) → Ctrl-X → overlay → `0.PLAYER` in IDBFS → reload → character
  restored (`C` sheet) → no console errors. Screenshots `web/shots/s1-*.png`.
  Test IDBFS dbs (`/nppangband/lib/*`) deleted at the end of every test.
- **Tiles decision (stage 4): Shockbolt** (case A fallback).
  `python3 web/tile-coverage.py dvg|new`: own **32x32** (Gervais,
  `graf-dvg.prf`) **850/1337 = 63.6%** (monsters 628/687, objects 222/451,
  features 0/199); own **16x16** (Adam Bolt, `graf-new.prf`) **1047/1337 =
  78.3%** (monsters 600/687, objects 447/451, features 0/199). Neither pref
  has a single `F:` line: NPP 0.5.1 rewrote `terrain.txt` (199 features) and
  never updated the graphics prefs, so terrain would be ASCII in both sets.
- Open problems: in the dungeon after random keys only `@` and `<` showed
  (probably the torch was taken off; check walls in stage 2); the prompt box
  (RvipWM.prompt) sits over row 0 of the map; no mouse (clicks not queued).

### Stage 2 (explore + stairs): done 2026-09-26 (cloud, resumed session)
- **Explore key `H`** (was unused in the original keyset, `lib/help/cmdlist.txt`;
  roguelike `H` stays run west: no explore key there). Entry
  `{ "Explore the level", 'H', CMD_NULL, do_cmd_explore }` in `cmd_action[]`
  (`src/cmd0.c`), so it is also in NPP's own command menu.
- Code: end of `src/cmd2.c`: `auto_explore` (0 off, 1 explore, 2 walk to `<`,
  3 walk to `>`), `explore_step()`, `do_cmd_explore()`, `explore_to_stairs()`,
  `explore_reset()`, `explore_new_level()`; prototypes in `externs.h`;
  `do_cmd_open_aux()` no longer static.
- Hooks: `process_player()` (`dungeon.c`) treats `auto_explore` like running
  (key abort check, `else if (auto_explore) explore_step();` before
  `run_step`); `dungeon()` calls `explore_new_level()` after
  `p_ptr->leaving = FALSE`; `disturb()` (`cave.c`) calls `explore_reset()`;
  `do_cmd_go_up/down()` (`cmd2.c`) call `explore_to_stairs()` instead of
  "I see no ... staircase here". On the stair it `cmd_insert(CMD_GO_UP/DOWN)`.
- **Known grid**: `cave_info & CAVE_MARK` or the explorer's own
  `explore_seen[][]` (every `CAVE_SEEN` grid noted each step: NPP forgets
  torch-lit corridor floors). Passable: known, `cave_passable_bold`, not a
  shop, no visible player trap (`EF1_HIDDEN`), no damaging non-native terrain;
  known closed doors are opened with `do_cmd_open_aux()` (given up after 5
  tries: locked/stuck). Targets: known grid next to an unknown one, or a
  marked object not stood on. BFS from all targets, step to the neighbour
  with the smallest distance.
- Stops: `disturb()`, a new message (`messages_num()`), confusion/blind/
  hallucination, a visible monster in `projectable()` range (explore only;
  `NEVER_MOVE` monsters only within 2 grids), a step that did not move.
  `<`/`>` without a known staircase explore until one is seen, then walk.
- **Map fix**: the web module registered as `"x11"` loaded `font-x11.prf`,
  which draws walls/floors as X11-font glyphs 1–31/127 (blank on the page:
  the "only `@` and `<`" problem of stage 1). Now `{ "web", ... }` in
  `main.c`; `lib/pref/pref.prf` loads `pref-x11.prf` (keysym macros) for
  `$SYS web` too; fonts/graf come from `font-xxx.prf`/`graf-xxx.prf`.
- Help: `lib/help/cmdlist.txt` (H), `cmddesc.txt` ("Explore (H)", stairs walk).
- Test: `node web/test/stage2.mjs` (Playwright, headless): town `>` walks to
  the stairs and descends; 40× `H` on level 1 (monsters in view removed with
  debug `^A z`) until "Nothing left to explore."; `>` → 100 ft; `<` → 50 ft;
  no console errors. Shots `web/shots/s2-*.png`.
- Not done: ASan random-key run weighted to `H`/`<`/`>` (time budget of the
  cloud session; `web/asan.sh` + `web/asan-keys.py` are ready for it).
- Open problems: corridor floors lit only by the torch are not drawn after
  you leave them (NPP's own `view_torch_grids` behaviour, not the explorer);
  a monster blocking the only path makes explore stop without moving.

### Stage 3 (Enter menu + inventory): done 2026-09-26 (cloud)
- **Enter menu**: NPP's own 3.1 command menu `do_cmd_menu()` (`src/cmd0.c`,
  `cmds_all[]` groups → `cmd_menu()` sub-list, `menu_select()`), before on
  `^H` only; now also `'\r'` and `'\n'` in `cmd_hidden[]`. All 6 groups
  (Use magic/Pray, Action, Use item, Manage items, Information, Utility)
  incl. the new "Explore the level" (H). Cursor 2/8 + Enter, Escape closes.
- **Item menus**: `inven_screen()` in `src/cmd3.c` (`do_cmd_inven()`/
  `do_cmd_equip()` call it): cursor `>` left of the labels (column from
  `show_list_col`, set in `show_obj_list()` in `obj-ui.c`; item of a row by
  its label via `Term_what` + `label_to_inven/equip`), 2/8/arrows move,
  Enter/Space/5/6 or the item's letter open the action menu, `/` (or 4)
  switches lists, Escape/0 close, any other key is taken as a command
  (as before).
- **How item actions run (direct call + preselect)**: `item_action_menu()`
  at the end of `src/cmd-obj.c` lists the `item_actions[]` entries whose
  filter and places (`USE_INVEN/EQUIP/FLOOR`) accept the item
  (`item_action_okay()`), each with its command key (q r E u a z A b G m F
  w t d I { }). Choosing one sets `do_item_preselect` and calls `do_item()`,
  which skips `get_item()` for that item (aiming still asks a direction);
  commands then go through `cmd_insert()` as usual.
- Test: `node web/test/stage3.mjs`: Enter menu (all groups, Action list with
  Explore, run by cursor), `i` cursor, `a` → menu (Eat/Drop/Examine), `E`
  eats (rations −1), cursor+Enter opens the menu, `e` → body armour → `t`
  takes it off into the pack, `/` switches lists; no console errors.
  Shots `web/shots/s3-*.png`.
- Open problems: the list does not reopen after an action; Destroy (`k`),
  throw and fire are not in the item menu (not in `item_actions[]`); the
  page prompt box (RvipWM.prompt) still covers the start of row 0; no
  ASan run for stages 2–3 (time).

### Stage 4 (tiles): done 2026-09-26 (cloud)
- **Tile set: Shockbolt** 64x64 (Raymond Gaustadnes; Angband 4.2
  `lib/tiles/shockbolt`), `web/tiles.webp` = the bundle's
  `rvip/templates/tactical-angband/tiles.webp` (lossless, 13 MB, committed),
  the one set. Own sets: 16x16 **78.3%**, 32x32 **63.6%** (no `F:` lines);
  Shockbolt **1335/1337 = 99.9%** (monsters 687/687, objects 450/451,
  terrain 198/199; the misses are the index-0 "nothing" entries), 665 by
  name, 466 by hand, **204 family stand-ins** (153 monsters, 51 objects):
  `python3 web/tile-coverage.py` (`dvg` / `new` for the own sets).
- **Pref**: `lib/pref/graf-shb.prf`, generated by `python3 web/mkgraf-shb.py`
  (Zangband template's script ported to NPP's `monster.txt`/`object.txt`/
  `terrain.txt`/`flavor.txt`): monsters/objects by name, family stand-ins,
  terrain by name keywords (shops, traps, doors, walls, veins, stairs,
  water/lava/sand, trees, runes, clouds → GF tiles), flavours as `L:` lines
  (kind + colour → 4.2 flavour tiles), bolts `S:0x30..0x7F`, player `R:0`
  per class/race from `xtra-shb.prf`. Loaded by `lib/pref/graf.prf`
  `?:[AND [EQU $SYS web] [EQU $GRAF shb]]`.
- **C**: `GRAPHICS_SHOCKBOLT 5` (`defines.h`); `web_graphics()` in
  `src/main-web.c` sets it, `ANGBAND_GRAF = "shb"`, transparency and
  **bigtile** (square tiles: one grid = two cells, the pad cell `255/0xFF`);
  the page's Tiles button → `web_switch_graphics()` (reset_visuals +
  redraw) at the command prompt. No lighting shades: NPP's
  `special_lighting_*()` switches have no case for it (the lit tile always).
- **JS only blits**: `web/nppangband.js` `TILE_SRC = 'tiles.webp'`,
  `TILE = 64`, `pict(..., big)` draws nearest-neighbour
  (`imageSmoothingEnabled = false`) at the cell size (2 cells wide).
  `web/build.sh` copies `tiles.webp` into `web/dist`.
- Test `node web/test/stage4.mjs`: town (shops, walls, townspeople, the
  warrior tile) 838 pict cells, canvas colour variety 552; dungeon level 1
  in tiles; Tiles off → text (no pict on `^R`), on again (1979 pict cells);
  no console errors. Shots `web/shots/s4-*.png`.
- Open problems: 204 stand-ins; the sidebar's equipment chars (`|~[`) are
  blank in tile mode; no light/dark shading of floors; clouds/runes use
  generic GF/rune tiles.

### Stage 5 (web page): done 2026-09-26 (cloud) — deploy NOT run
- **Windows** (`rvip/web/rvip-wm.js`, copied by the build; `web/index.html`
  `#t-<id>`, `TERMS` in `web/nppangband.js`, 8 terms = `WEB_TERMS` in
  `src/main-web.c`): 0 Map, 1 Inventory, 2 Messages, 3 Visible
  (`PW_MONLIST`), 4 Recall, 5 Equipment, 6 Character (`PW_PLAYER_0`),
  7 Objects (`PW_ITEMLIST`). Flags set for new characters by
  `web_new_character()` after `player_birth()` (stage 1). Default on: Map,
  Inventory, Visible, Messages; the rest via Windows ▾.
- **Prompt box** (RVIP W4, z-term): `#t-main .wm-topl` in `web/index.html`
  is one cell row high, full width, opaque, `white-space: pre`, font and
  height from `--cell-h`/`--cell-font` that `configureTerm(0)` sets per zoom:
  it now covers row 0 exactly instead of overlapping it.
- **Layout file** `/nppangband/lib/user/web-layout.json` (IDBFS; splits, wm
  tree, zoom, fonts, Tiles, audio) — from stage 1.
- **Game end**: `quit_aux = hook_quit` (`main-web.c`) → `js_sync()` +
  `js_quit(msg, p_ptr->is_dead)`. Death: tombstone menu + scores wait for
  keys in C, then the page syncs and reloads; the dead save starts a new
  birth. Ctrl-X: "Press Return", scores, then the overlay (reload restores;
  stage-1 test).
- **`web/deploy.sh`** (template's, guard line = only from pushed commits,
  refuses without `web/dist`), target `ruzzoli.de/roguelikes/nppangband/`.
  **Written, never run** (no deploy key in the cloud).
- Test `node web/test/stage5.mjs`: Inventory/Visible/Equipment/Character
  terms hold their content, 8 windows, `i` → prompt box 24 px = one cell,
  text "(Inventory) …"; `Q` → y → y → `@` → tombstone → keys → page reloads
  → new birth screen; no console errors. Shots `web/shots/s5-*.png`.
- Open problems: live URL does not exist yet (Mac: deploy); layout
  persistence across reload not re-tested here (stage-1 code, unchanged);
  no mouse (clicks not queued, NPP's `DEFINED_XFF` mouse command unused).

### Stage 6 (docs + sound): done 2026-09-26 (cloud) — Docs collection entry is Mac work
- **Sound**: the bundle's `rvip/templates/dubtrain/` was missing, so the
  Dubtrain Angband Sound Pack v3.1.0 is vendored from upstream Angband
  (`lib/sounds/*.mp3` + `lib/customize/sound.prf`, commit 1d2ad35a2fc8,
  CC-BY 4.0) into `web/dubtrain/` (214 mp3, 3.3 MB, README with credit).
  `web/sounds.py <cfg> <dir>` writes the web `sound.cfg` for all 152
  `angband_sound_name[]` events (NPP's 3.x names = 4.2's in upper case; `MAP`
  for breathe_*/summon_*/identify_*/cast_spell/… → BR_*/SUM_*/IDENT_*/SPELL)
  and copies 211 files to `dist/sound`; only `walk` is silent. `build.sh`
  stages it into the preload (`/nppangband/lib/xtra/sound/sound.cfg`), the
  page reads it with `Module.FS.readFile` (`loadSoundCfg()`), never fetch.
  C/JS unchanged: `sound_hook` → `js_sound()` → `Module.qb.sound()`.
  Sound and Music off by default (buttons in the bar, kept in the layout).
- **Help**: `web/make-help.py` (template's shape, but self-contained: the
  Mac's `~/Desktop/Games/Roguelikes/Docs` is not here; game text inline,
  complete key list parsed from `lib/help/cmdlist.txt`, 154 commands) →
  `dist/help.html` in `build.sh`; `--docs` writes the standalone page
  **`docs/web/nppangband-docs.html`** (About / Keys / Saving / Tips / Guide /
  Browser / Credits / About this version with upstream + compare links).
  Credits: Jeff Greene, Diego González; Angband 3.1.2v2 (Andrew Sidwell) and
  earlier maintainers from `AUTHORS`; GPL-2 or Angband licence (`COPYING`);
  Shockbolt © Raymond Gaustadnes; Dubtrain CC-BY 4.0; town music from
  Quickband's port.
- Test `node web/test/stage6.mjs`: fresh load Sound/Music off; Help shows all
  sections + credits; no sound fetched while off; Sound on → eat →
  `plm_eat_bite.mp3` 200; no `.cfg`/`.prf` request; Music on in town →
  `music/new_town.ogg`; reload keeps both on; no console errors.
  Stage-1 test re-run (save/restore) after stage 6.
- **Mac side**: add the Docs collection entry (`build-docs.py` GAMES +
  `guides.py`) from `web/make-help.py`'s data / `docs/web/nppangband-docs.html`,
  then switch `make-help.py` back to importing the Docs (template version);
  deploy (`sh web/build.sh && sh web/deploy.sh`); browser check in the pane.
- Open problems: no ambient sounds (NPP has no ambient events in
  `angband_sound_name[]`); music only in town (depth 0); hit/kill sounds
  not tested separately (same path as eat).

### Stage 7 — publish (done 2026-09-26, Mac)
- **Mac check** (browser pane, own tab, `web/dist` on 127.0.0.1:8747 with
  `Cache-Control: no-store`): birth (Human Warrior), town, `>` walks to the
  entrance and descends, `H` explores, `<` walks back up to town, Enter menu
  + Action submenu, `i` list with cursor + item action box, Windows ▾
  (Equipment, Character, Recall on) → reload → same windows and character,
  resize 1440x900 → 1200x750 (prompt open) → 760x500, zoom ±, Tiles off/on,
  Help guide (Docs entry), Sound/Music off at first load, Sound on after a
  click (`sound/plm_eat_bite.mp3` on eating), town music plays, no
  `.cfg`/`.prf` request, Ctrl-X → Hall of Fame → "Play again" overlay →
  reload restores, no console errors. Live URL checked the same way (birth,
  stairs, explore, Help links, no console errors).
- **What the cloud got wrong** (fixed in "RVIP: stage 1-6 fixes (Mac)"):
  every sub-window went blank after a browser resize or window change until
  a key/Ctrl-R: `web_apply_layout()` set `p_ptr->window`, which NPP 0.5.1
  never reads (sub-windows follow `p_ptr->redraw` PR_* events); now it sets
  the PR flags. The map was fine (unlike Easyband's cloud build): 3.1's
  `SCREEN_HGT/WID` follow `Term->hgt/wid`, bigtile = square tiles over two
  8x16 cells, player centred, the map fills the window at the default zoom.
  Mac paths: `build.sh` takes `rvip-wm.js` from `~/Games/rvip-tools/web`,
  `mkgraf-shb.py`/`tile-coverage.py` read Shockbolt from
  `~/Games/tactical-angband/lib/tiles/shockbolt`, `asan.sh` without GNU
  `xargs -r`/`nproc`, `toolchain.sh` notes Homebrew emcc.
- **Stash** (local stage-2 attempt): kept the portable `asan.sh`, the local
  Shockbolt paths and the toolchain note; dropped the rest (the cloud's
  explore/stairs/menu and the `"web"` module name cover it).
- **Docs**: entry `nppangband.html` in `~/Desktop/Games/Roguelikes/Docs`
  (`build-docs.py` GAMES after Easyband + `parse_nppangband()` for
  `lib/help/cmdlist.txt`, `guides.py` GUIDES + SAVING), generated from
  `make-help.py`'s data; `make-help.py` now prefers the Docs entry
  (`NPP_NO_DOCS=1` for the self-contained version). Other Docs pages
  byte-identical (only `index.html` gained the card).
- **Repos**: public **memmaker/nppangband** (this folder, remote `memmaker`,
  branch `main`; `git filter-repo --path rvip --path web/shots --path
  LESSONS.md --invert-paths`, `git log --all -- rvip` empty). Upstream
  commit unchanged: `b1d1d85` (filter-repo keeps untouched commits' hashes;
  the empty "refresh procedure snapshot" commit was dropped). Private
  **memmaker/nppangband-cloud** (renamed, `~/Games/nppangband-cloud`,
  remote `origin`, holds the bundle, `web/shots/`, `rvip/LESSONS.md`).
  README with upstream tag/commit and the compare view.
- **Live**: https://ruzzoli.de/roguelikes/nppangband/ (`sh web/build.sh &&
  sh web/deploy.sh`), og block by hand (image `roguelikes/nppangband.png`).
  Index `94d24c1`: card before Quickband (60 Shockbolt monsters at 32 px,
  384x160), count 37, tree: the existing `NPPAngband` node under Angband 3.0
  (parent of Quickband) is now a gold link, "2011 · Jeff Greene, Diego
  González; 0.5.1 on Angband 3.1.2 code".
- Test IndexedDB `/nppangband/...` deleted on 127.0.0.1:8747 and ruzzoli.de.
- Open problems: the main term keeps Angband's 80x24 minimum, so a small Map
  window (e.g. 760x500 browser, or several extra windows on) shows the map
  CSS-scaled down (tiny tiles); sub-windows stay blank while a prompt is
  open during a resize (redrawn when it closes); the Enter submenu box is a
  few columns wider than its entries; NPP's first release year not checked
  (card/tree use 0.5.1's 2011; stage 8); the starting kit's torch is already
  wielded (no problem, just differs from Easyband).

### Next: stage 8 (shrine)
- Page `~/Games/roguelikes-index/shrine/nppangband.html` (+ `shrine/nppangband/`),
  Info button on the card, ✦ in the tree, `#bar h1` link in `web/index.html`.
- Material: manual/help = `lib/help/*.txt` (`general.hlp`, `tutorial.txt`,
  `birth.txt`, `raceclas.txt`, `quests.txt`, `dungeon.txt`, `town.txt`,
  `magic.txt`, `cmddesc.txt`, `cmdlist.txt`, ...), the in-game `?` menu;
  readme `readme.txt` (Angband 3.1.0's, NPP forum link); licence `COPYING`
  (GPL-2 or Angband licence, tile/sound notes); changelog `NPPchanges.txt`
  (1238 lines, 0.5.1 back to early versions); credits `AUTHORS`, `THANKS`,
  splash `lib/file/news.txt`. Upstream history: github.com/nppangband/NPPAngband
  (tags v0.5.1 … v7.1.0, local branch `master` = 7.1.0). Walkthrough: none
  known (look on RogueBasin / angband.oook.cz / the NPP forum).

### Stage 8 — shrine (done)
- Page https://ruzzoli.de/roguelikes/shrine/nppangband.html (roguelikes-index
  `2dc883a`, committed/deployed from a fresh clone: the main checkout has
  another session's untracked `shrine/faangband/`). Files in
  `shrine/nppangband/`: `manual.html` (all 29 `lib/help` files, generated by
  `web/mkmanual.py`, Easyband's script + a CR/NEL fix + unreached files),
  `changelog.txt` (`NPPchanges.txt`, cp1252 → UTF-8), `license.txt` (`COPYING`).
- Links: card Info button, tree ✦, game `#bar h1` link (was already there
  since stage 5), Quickband shrine lineage now links NPPAngband.
- Lineage checked: first release 0.1.0 on 24 April 2003 on Angband 3.0.3
  (RogueBasin "No Pet Peeves Angband"; 0.2.0 announcement Sep 2003 says 3.0.3);
  0.5.1 (tag 20 March 2011) moved to Angband 3.1.2v2. Card and tree now say
  2003; tree text "from Angband 3.0.3, 0.5.1 on 3.1.2 code".
- Name fixed: "Not Pure Plain Angband" (stage 5-7 invention, no source) →
  "No Pet Peeves Angband" (RogueBasin; the game's own files never expand NPP)
  in the card, `web/index.html` og/description, `make-help.py`, README,
  `docs/web/nppangband-docs.html`, and the Docs entry (`guides.py`,
  `nppangband.html` in `~/Desktop/Games/Roguelikes/Docs`, not a git repo).
- Missing: no walkthrough found (RogueBasin stub, no guide on the web);
  cheats exist (`^W` wizard, `^A` debug, cheat options; they mark the savefile).
- Open problems: angband.oook.cz and Google Groups answered 429 during the
  check (codename "Ghost on the Road" read from the Groups page title only).

### Next: stage 9 (graveyard + leaderboard)

### Stage 9 — graveyard + leaderboard (done)
- Hook: `web_run_end()` in `src/main-web.c` (decl in `externs.h` under
  `USE_WEB`), called from `src/files.c` `close_game()` at the top of the
  `is_dead` branch, before `death_screen()` (which zeroes a winner's depth).
  Commit `4f38cad`, deployed.
- Fields: `g=nppangband`, `ev` (win = `total_winner`; quit = died_from
  "Quitting"/"Interrupting"/"Abortion"; else death), `name` =
  `op_ptr->full_name`, `killer` = `died_from` with a/an/the stripped,
  `depth` = `p_ptr->depth`, `score` = `total_points()`, `turns` = `turn`
  (both as the high-score entry), `lvl` = `p_ptr->lev`. Nothing missing.
  Save & quit (Ctrl-X) sends nothing (not a finished run).
- Killer art: roguelikes-index `9e6eff7`, `killers/make.py` `nppangband()`
  (generic `angband()` helper, new `the=True` strips a leading "The "),
  670 PNGs from `web/tiles.webp` via `lib/pref/graf-shb.prf`, deployed.
- Live test (ruzzoli.de, fetch wrapper): `Q` `y` `@` →
  `ev=quit&name=PLAYER&depth=0&score=0&turns=20&lvl=1` 204; count `0588`,
  `^A` `y` `n` summons a Great Hell Wyrm (asleep), walk into it →
  `ev=death&killer=Great%20Hell%20Wyrm&…` 204, `great-hell-wyrm.png` live;
  outbox empty both times. Win path not reachable in a test (same
  `total_winner` check as Easyband). `/nppangband/...` IDB deleted on
  ruzzoli.de.
- Open problems: none.
