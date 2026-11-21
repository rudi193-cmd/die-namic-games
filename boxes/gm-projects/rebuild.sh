#!/bin/bash
# Lay a box over four open-source AI game-master projects and run its stack.
# Usage: rebuild.sh SCRATCH
#
# The pile is each project at one commit (git archive from a checkout beside
# die-namic-games: ../NAME, or GM_PROJECTS/NAME), keeping only what reads as
# words: .md .py .go .ts .toml .txt, without lockfiles, node_modules or
# vendored folders. Tavern (t11z) is left out: its repository was not readable
# from the session that made this (see ../MEMORY.md). Willow, as the box finds
# it (WILLOW_ROOT, or beside), held to willow.pin.json.
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into any
# repository.
set -u
# folder  commit
PROJECTS="narrativeengine-p:6514be9fd60165462513fb7dee5b613135c21625
inkandbone:653e527
dnd_ai_dm:ea046d3
taleweaver:7c12722"
[ $# -eq 1 ] || { echo "usage: rebuild.sh SCRATCH (a folder outside the repositories)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
BASE=${GM_PROJECTS:-$R/..}
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*) echo "refused: SCRATCH is inside the repository"; exit 2;; esac
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile"
laid=""
for pc in $PROJECTS; do
  name=${pc%%:*}; at=${pc#*:}
  co=$(ls -d "$BASE/$name" "$BASE"/*/"$name" 2>/dev/null | head -1)
  if [ -n "$co" ] && git -C "$co" cat-file -e "$at^{commit}" 2>/dev/null; then
    mkdir -p "$S/pile/$name"
    git -C "$co" archive "$at" | tar -x -C "$S/pile/$name" \
      --wildcards '*.md' '*.py' '*.go' '*.ts' '*.toml' '*.txt' 'LICENSE*' 2>/dev/null
    find "$S/pile/$name" \( -name node_modules -o -name vendor -o -name '*lock*' \) -prune -exec rm -rf {} + 2>/dev/null
    laid="$laid $name@${at:0:7}"
  else
    laid="$laid ($name left out: no checkout holding ${at:0:7})"
  fi
done
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile:$laid; $(find "$S/pile" -type f | wc -l) files"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "page: $S/page.md  each step: $S/run/"
exit $code
