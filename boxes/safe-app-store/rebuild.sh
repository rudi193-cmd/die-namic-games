#!/bin/bash
# Lay a box over the SAFE App Store and run its stack. Usage: rebuild.sh SCRATCH [COMMIT]
#
# The pile is the store at one commit (the one this was made at, unless you
# name another), written out by git archive into SCRATCH/pile, without
# apps/nasa-archive: 293 MB and over half the store's files, a corpus the
# rest of it doesn't need to be read by. The store is found beside
# die-namic-games (../safe-app-store) or at SAFE_APP_STORE; willow, as the
# box finds it (WILLOW_ROOT, or beside), held to willow.pin.json.
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into
# either repository.
set -u
PINNED=ac07125836eb33c50a540b6efa17701d875d4a64
[ $# -eq 1 ] || [ $# -eq 2 ] || { echo "usage: rebuild.sh SCRATCH [COMMIT] (SCRATCH a folder outside the repositories)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
STORE=${SAFE_APP_STORE:-$R/../safe-app-store}
[ -d "$STORE/.git" ] || { echo "refused: no safe-app-store checkout at $STORE (set SAFE_APP_STORE)"; exit 2; }
STORE=$(cd "$STORE" && pwd)
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*|"$STORE"/*) echo "refused: SCRATCH is inside a repository"; exit 2;; esac
AT=${2:-$PINNED}
git -C "$STORE" cat-file -e "$AT^{commit}" 2>/dev/null || { echo "refused: the store checkout does not hold commit $AT; fetch it first"; exit 2; }
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile"
git -C "$STORE" archive "$AT" | tar -x -C "$S/pile" --exclude="apps/nasa-archive" || exit 2
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile: the store at ${AT:0:7}, $(find "$S/pile" -type f | wc -l) files, apps/nasa-archive left out"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "page: $S/page.md  each step: $S/run/"
exit $code
