#!/bin/sh
# Native AddressSanitizer build (curses frontend) for the random-key runs.
# Builds into $ASAN (default /tmp/npp-asan), with its own copy of lib/ and
# its own HOME, so nothing in the repo is written.  Driver: web/asan-keys.py.
set -e
cd "$(dirname "$0")/.."
ASAN=${ASAN:-/tmp/npp-asan}
mkdir -p "$ASAN/obj" "$ASAN/home" "$ASAN/run/lib"
# user dir inside the run folder: path_parse("~") uses getpwuid(), not $HOME
echo '#define PRIVATE_USER_PATH "./lib/user"' > "$ASAN/cfg.h"
SRCS=$(sed -n '/^ZFILES/,/^$/p;/^ANGFILES/,/^$/p' src/Makefile.src \
	| grep -o '[a-z0-9_-]*\.o' | grep -v '^main\|^snd-\|^cairo' | sed 's/\.o$/.c/;s|^|src/|' | sort -u)
for f in $SRCS src/main.c src/main-gcu.c; do
	o="$ASAN/obj/$(basename "$f" .c).o"
	[ "$o" -nt "$f" ] || echo "$f"
done | xargs -P "$(getconf _NPROCESSORS_ONLN)" -I{} sh -c 'gcc -c -g -O1 -fno-omit-frame-pointer -fsanitize=address -fcommon -std=gnu99 -w -DUSE_GCU -include '"$ASAN"'/cfg.h -Isrc {} -o '"$ASAN"'/obj/$(basename {} .c).o'
gcc -fsanitize=address -o "$ASAN/run/nppangband" "$ASAN"/obj/*.o -lncurses
rm -rf "$ASAN/run/lib" && mkdir -p "$ASAN/run/lib"
for d in edit file help pref xtra; do cp -R lib/$d "$ASAN/run/lib/"; done
mkdir -p "$ASAN/run/lib/save" "$ASAN/run/lib/user/NPPAngband" "$ASAN/run/lib/apex" "$ASAN/run/lib/bone" "$ASAN/run/lib/info"
echo "built $ASAN/run/nppangband"
