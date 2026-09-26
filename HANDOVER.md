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

(nothing yet — start with stage 1)
