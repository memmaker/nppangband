#!/bin/sh
# Toolchain used for the NPPAngband web port (cloud session, Linux x86_64).
# Every command that was run to set it up, in order.

# Emscripten (worked first time, ~2 min): emcc 6.0.10 (d6c521a7)
git clone --depth 1 https://github.com/emscripten-core/emsdk /home/user/emsdk
(cd /home/user/emsdk && ./emsdk install latest && ./emsdk activate latest)
. /home/user/emsdk/emsdk_env.sh          # before web/build.sh in every new shell

# Resumed session (stage 2+): emsdk re-cloned and `install latest` again
# (same commands as above, ~2 min). Binaryen from apt as well (wasm-opt 108,
# never `npm i -g binaryen`); emcc uses emsdk's own wasm-opt.
apt-get install -y binaryen

# Python helpers: Pillow (tile coverage, tile sheet), pyte (ASan pty driver)
pip install pillow pyte

# Native ASan build (curses frontend, random-key driver): gcc + libncurses
#   see web/asan.sh
# Browser tests: Playwright + the pre-installed Chromium (/opt/pw-browsers)
#   (cd web/test && npm install) ; see web/test/*.mjs
