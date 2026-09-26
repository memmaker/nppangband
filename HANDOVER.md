# NPPAngband 0.5.1: handover

## Cloud experiment (read this first)

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

### Next: stage 2 (explore + stairs)
- 3.1-era code: Quickband's `pathfind.c` `explore_step()` is the closest
  template (not bundled here; port from the Zangband stage-2 description).
  NPP has its own `src/pathfind.c` (mouse travel) and `cmd0.c` command
  tables (`cmd_init()`), `textui_process_command()` in `cmd0.c`,
  `process_player()` in `dungeon.c` ~l.1720, `disturb()` in `util.c`/`xtra2.c`.
