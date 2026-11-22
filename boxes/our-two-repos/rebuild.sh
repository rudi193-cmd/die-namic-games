#!/bin/bash
# Lay a box over our two repositories and run its stack. Usage: rebuild.sh SCRATCH
#
# The pile is willow at the commit willow.pin.json names, and die-namic-games
# at the commit below, each as git archive writes it, keeping only what reads
# as words (.md .py), and without boxes/ (so a box never reads its own page).
# Willow is found as the box finds it (WILLOW_ROOT, or beside).
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into
# either repository.
set -u
DN=3de61d2   # die-namic-games: the commit that added the fight-engines note
[ $# -eq 1 ] || { echo "usage: rebuild.sh SCRATCH (a folder outside the repositories)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
WAT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' "$R/willow.pin.json") || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*|"$W"/*) echo "refused: SCRATCH is inside a repository"; exit 2;; esac
git -C "$R" cat-file -e "$DN^{commit}" 2>/dev/null || { echo "refused: die-namic-games checkout lacks $DN"; exit 2; }
git -C "$W" cat-file -e "$WAT^{commit}" 2>/dev/null || { echo "refused: willow checkout lacks $WAT"; exit 2; }
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile/willow" "$S/pile/die-namic-games"
git -C "$W" archive "$WAT" | tar -x -C "$S/pile/willow" --wildcards '*.md' '*.py' || exit 2
git -C "$R" archive "$DN" | tar -x -C "$S/pile/die-namic-games" --wildcards '*.md' '*.py' --exclude='boxes' || exit 2
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile: willow at ${WAT:0:7}, die-namic-games at $DN; $(find "$S/pile" -type f | wc -l) files"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "page: $S/page.md  each step: $S/run/"
exit $code
