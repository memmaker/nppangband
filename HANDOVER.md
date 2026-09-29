# NPPAngband 0.5.1: handover

RVIP stages 1–9 done (2026-09-26; stages 1–6 in a cloud session, fixed and
published on the Mac). Live: https://ruzzoli.de/roguelikes/nppangband/, repo
https://github.com/memmaker/nppangband (`main`, remote `memmaker`), shrine
https://ruzzoli.de/roguelikes/shrine/nppangband.html. Procedure:
`~/Games/rvip-tools/RVIP.md`. (The cloud run's history, bundle and shots were
in memmaker/nppangband-cloud, deleted 2026-09-27; this repo is that history
filtered.)

## Source
- NPPAngband ("No Pet Peeves Angband") 0.5.1, tag `v0.5.1` = `b1d1d85`, remote
  `upstream` = github.com/nppangband/NPPAngband. Jeff Greene, Diego González;
  first release 0.1.0 2003 on Angband 3.0.3, 0.5.1 (2011) on Angband 3.1.2v2
  code. **Case A**, but 3.1-era (`game-cmd.c`, `ui-menu.c`, `cmd-obj.c`,
  `obj-ui.c`): closer to Quickband than Zangband.

## Build, test, deploy
- `sh web/build.sh` → `web/dist` (toolchain notes in `web/toolchain.sh`;
  Homebrew emcc on the Mac). emcc over `ZFILES` + `ANGFILES` of
  `src/Makefile.src` + `main.c main-web.c`, Asyncify, IDBFS; preload
  `lib/{edit,file,help,pref}` + web `sound.cfg` as `/nppangband/lib`. Pages
  load the shared `../rvip-wm.js` / `../rvip-app.js`.
- `web/deploy.sh` → `ruzzoli.de/roguelikes/nppangband/` (pushed commits only).
- ASan: `sh web/asan.sh` (native `-DUSE_GCU`, build in `/tmp/npp-asan`, user
  dir forced to `./lib/user` because `path_parse("~")` uses `getpwuid()`) +
  `python3 web/asan-keys.py SEED NEW RESTORED [extra keys]` (pty + pyte).
  No ASan run yet for stages 2–3 code.
- Playwright tests `web/test/stage{1..6}.mjs` (headless Chromium, serve
  `web/dist`). Written before the page loaded `../rvip-*.js`; they need the
  parent folder served to work now.
- `.github/workflows/release.yml` builds Linux/macOS/Windows releases.
- Birth: splash key, `a` `a` `a` `a` (point-based), Enter, name, key → town.
  Cheats: `^W` wizard, `^A` debug (mark the savefile).

## Port map (`USE_WEB`)
- `src/main-web.c` (Zangband's adapted), registered as `"web"` in
  `modules[]` (as `"x11"` it loaded `font-x11.prf` = blank walls);
  `lib/pref/pref.prf` loads `pref-x11.prf` for `$SYS web` too. 8 terms: Map,
  Inventory, Messages, Visible (`PW_MONLIST`), Recall, Equipment, Character
  (`PW_PLAYER_0`), Objects (`PW_ITEMLIST`); flags set by
  `web_new_character()` after `player_birth()` (`init_angband()` zeroes them
  after `init_web()`). Sub-windows follow `p_ptr->redraw` PR_* flags, not
  `p_ptr->window`: `web_apply_layout()` sets PR flags. No z-term resize
  hooks. Prompt box = `#t-main .wm-topl` (one cell row over row 0).
- `options[OPT_auto_more/OPT_center_player]` on in `init_web()`. Sound: 3.1
  `sound_hook` → `js_sound()`.
- Other edits: `config.h` no `PRIVATE_USER_PATH`; `z-file.c`
  `safe_setuid_drop/grab()` empty; `save.c` `web_sync_files()`.
- Explore (`H`, original keyset; also in NPP's command menu via
  `cmd_action[]` in `cmd0.c`): end of `src/cmd2.c` (`auto_explore` 0/1/2/3),
  hooks in `dungeon.c` `process_player()` / `dungeon()`, `disturb()`
  (`cave.c`). Own `explore_seen[][]` (NPP forgets torch-lit floors). Paints
  each step (40 ms). `<`/`>` off the stairs explore until a staircase is
  known, then walk there only.
- Enter menu: NPP's own `do_cmd_menu()` (`cmd0.c`), `'\r'`/`'\n'` added to
  `cmd_hidden[]`. Item menus: `inven_screen()` (`cmd3.c`) +
  `item_action_menu()` (`cmd-obj.c`, `item_actions[]`) with
  `do_item_preselect`.
- Tiles: **Shockbolt** 64x64 (`web/tiles.webp`, 13 MB; own 16x16 78.3%,
  32x32 63.6%, neither has `F:` lines). `lib/pref/graf-shb.prf` from
  `python3 web/mkgraf-shb.py` (reads `~/Games/tactical-angband`); coverage
  `python3 web/tile-coverage.py` (99.9%, 204 stand-ins). `GRAPHICS_SHOCKBOLT
  5`, bigtile (pad cell `255/0xFF`); loaded by `lib/pref/graf.prf`.
- Game end: `hook_quit` → `js_sync()` + `js_quit()`; dead save starts a new
  birth. Run-end beacon: `web_run_end()` from `files.c` `close_game()` before
  `death_screen()`. Killer art: roguelikes-index `killers/make.py`
  `nppangband()`.
- Sound: Dubtrain v3.1.0 mp3s vendored in `web/dubtrain/` (CC-BY 4.0);
  `web/sounds.py` writes the web `sound.cfg` (152 events). Music
  `web/music/new_town.ogg`.
- Help: `web/make-help.py` prefers the Docs entry
  (`~/Desktop/Games/Roguelikes/Docs`, `nppangband.html`); `NPP_NO_DOCS=1`
  for the self-contained version; `--docs` writes
  `docs/web/nppangband-docs.html`. Shrine manual: `web/mkmanual.py`.
- Layout file `/nppangband/lib/user/web-layout.json`.

## Open problems
- Not yet on the RVIP text-window model (part 2 "Presentation rules (W0)"
  rule 6): still the canvas sub-terms + prompt box.
- Map canvas keeps the 80x24 minimum and is CSS-scaled down in small Map
  windows (tiny tiles).
- Item list does not reopen after an action; Destroy (`k`), throw and fire
  are not in the item menu.
- Tiles: 204 stand-ins; sidebar equippy chars blank in tile mode; no
  light/dark floor shading; generic cloud/rune tiles.
- Sub-windows stay blank while a prompt is open during a resize; the Enter
  submenu box is a few columns too wide; torch-lit corridor floors are
  forgotten (NPP's behaviour); a monster blocking the only path stops
  explore without moving; no explore key in the roguelike keyset; no mouse.
- Win beacon not reachable in a test.
