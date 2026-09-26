#!/bin/sh
# Build NPPAngband for the browser (Emscripten + Asyncify).
# Output goes to web/dist; deploy with web/deploy.sh.
# Toolchain: see web/toolchain.sh (emsdk, emcc 6.0.10).
set -e
cd "$(dirname "$0")/.."
OUT=web/dist
rm -rf "$OUT" web/stage && mkdir -p "$OUT" web/stage/lib

# Game files (no X11 fonts, BMP tiles)
for d in edit file help pref; do cp -R lib/$d web/stage/lib/; done
mkdir -p web/stage/lib/info web/stage/lib/save web/stage/lib/user web/stage/lib/apex web/stage/lib/bone

# Sources: ANGFILES and ZFILES of src/Makefile.src (no main-*, snd-sdl, gtk), plus main.c main-web.c
SRCS=$(sed -n '/^ZFILES/,/^$/p;/^ANGFILES/,/^$/p' src/Makefile.src \
	| grep -o '[a-z0-9_-]*\.o' | grep -v '^main\|^snd-\|^cairo' | sed 's/\.o$/.c/;s|^|src/|' | sort -u)

emcc -O2 -fcommon -std=gnu99 -DUSE_WEB -Isrc -w \
	$SRCS src/main.c src/main-web.c \
	-o "$OUT/nppangband-core.js" \
	-sASYNCIFY -sASYNCIFY_STACK_SIZE=65536 -sSTACK_SIZE=1048576 \
	-sALLOW_MEMORY_GROWTH -sINITIAL_MEMORY=64MB \
	-sEXPORTED_FUNCTIONS=_main,_web_request_save \
	-sEXPORTED_RUNTIME_METHODS=FS,IDBFS,HEAPU8,addRunDependency,removeRunDependency \
	-sFORCE_FILESYSTEM -lidbfs.js -sENVIRONMENT=web \
	--preload-file web/stage/lib@/nppangband/lib

cp web/index.html rvip/web/rvip-wm.js web/nppangband.js "$OUT/"
echo '<p>The game guide is added in stage 6. Press <b>?</b> in the game for its own help.</p>' > "$OUT/help.html"
# Town music (depth 0), vendored from the Zangband template (Quickband's)
mkdir -p "$OUT/music" && cp web/music/new_town.ogg "$OUT/music/"
rm -rf web/stage
ls -la "$OUT"
