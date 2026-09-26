#!/bin/sh
# Upload web/dist to https://ruzzoli.de/roguelikes/nppangband/ (only from pushed commits)
# Build first: . /path/to/emsdk/emsdk_env.sh && sh web/build.sh
cd "$(dirname "$0")" && git fetch -q && [ -z "$(git status --porcelain)" ] && [ "$(git rev-parse @)" = "$(git rev-parse @{u})" ] || { echo "commit + push first"; exit 1; }
set -e
[ -f dist/nppangband-core.wasm ] || { echo "no web/dist: run web/build.sh first"; exit 1; }
ssh ruzzoli.de 'sudo mkdir -p /var/www/ruzzoli.de/roguelikes/nppangband && sudo chown -R felix:www-data /var/www/ruzzoli.de/roguelikes/nppangband'
rsync -rtz --delete dist/ ruzzoli.de:/var/www/ruzzoli.de/roguelikes/nppangband/
