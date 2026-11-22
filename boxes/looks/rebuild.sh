#!/bin/bash
# Lay a box over how game pages look: the four open AI game masters'
# screens, Die-Namic's own pages, and book designs brought in for
# inspiration. Run its stack.
# Usage: rebuild.sh SCRATCH
#
# The pile, in three parts:
#   screens/NAME  each project at one commit (git archive from a checkout
#                 beside die-namic-games: ../NAME, or GM_PROJECTS/NAME),
#                 keeping what a page is made of and said about: .tsx .vue
#                 .css .scss .html .md, without node_modules or lockfiles.
#   ours/         Die-Namic's own page sources (ui/*.src.html, ui/tables/,
#                 ui/build.py) and its design pages (README.md, open.md,
#                 open-gaps-from-the-boxes.md, box/'s and the-table's
#                 READMEs and stacks, boxes/MEMORY.md) at this checkout's
#                 HEAD, and my-table.md: the
#                 maintainer's own GM side of the table, in their words.
#   books/        book designs, from a folder outside the repository (BOOKS,
#                 or ../book-designs): each picture with a note beside it
#                 (same name, .md) saying what it is and what to take from
#                 it. The notes are laid as written; the pictures are read by
#                 willow's ocr add-on into books-read/ when tesseract is
#                 installed, and left out, and said, when it isn't. No add-on
#                 reads colour or layout from a picture: the note carries it.
#
# The pictures are someone else's work: they stay in BOOKS and the scratch
# folder, never in git. A fresh box each time. The key is a scratch key init
# makes, in SCRATCH, outside the box; nothing is ever sealed with it.
# SCRATCH/index is kept between runs (index-cache rebuilds it only when the
# pile changed); everything else in SCRATCH is laid fresh.
set -u
# folder  commit (the same pins as ../gm-projects)
PROJECTS="narrativeengine-p:6514be9fd60165462513fb7dee5b613135c21625
inkandbone:653e527
dnd_ai_dm:ea046d3
taleweaver:7c12722"
[ $# -eq 1 ] || { echo "usage: rebuild.sh SCRATCH (a folder outside the repositories)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
BASE=${GM_PROJECTS:-$R/..}
BOOKS=${BOOKS:-$R/../book-designs}
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*) echo "refused: SCRATCH is inside the repository"; exit 2;; esac
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile/screens" "$S/pile/ours"
laid=""
for pc in $PROJECTS; do
  name=${pc%%:*}; at=${pc#*:}
  co=$(ls -d "$BASE/$name" "$BASE"/*/"$name" 2>/dev/null | head -1)
  if [ -n "$co" ] && git -C "$co" cat-file -e "$at^{commit}" 2>/dev/null; then
    mkdir -p "$S/pile/screens/$name"
    git -C "$co" archive "$at" | tar -x -C "$S/pile/screens/$name" \
      --wildcards '*.tsx' '*.vue' '*.css' '*.scss' '*.html' '*.md' 2>/dev/null
    find "$S/pile/screens/$name" \( -name node_modules -o -name vendor -o -name '*lock*' \) -prune -exec rm -rf {} + 2>/dev/null
    laid="$laid $name@${at:0:7}"
  else
    laid="$laid ($name left out: no checkout holding ${at:0:7})"
  fi
done
head=$(git -C "$R" rev-parse --short HEAD)
git -C "$R" archive HEAD ui/index.src.html ui/tables ui/build.py \
  README.md open.md open-gaps-from-the-boxes.md box/README.md box/family-night.md box/gm-stack.md box/gm-end.md \
  the-table/README.md boxes/MEMORY.md | tar -x -C "$S/pile/ours"
cp "$HERE/my-table.md" "$S/pile/ours/my-table.md"
laid="$laid ours@$head"
if [ -d "$BOOKS" ]; then
  mkdir -p "$S/pile/books"
  (cd "$BOOKS" && find . -type f \( -name '*.md' -o -name '*.txt' \) -exec cp --parents {} "$S/pile/books/" \;)
  pics=$(find "$BOOKS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.gif' -o -iname '*.tif' -o -iname '*.tiff' \) | wc -l)
  if [ "$pics" -gt 0 ] && command -v tesseract >/dev/null; then
    python3 "$W/adapters/deps/ocr/ocr.py" mirror --from "$BOOKS" --to "$S/pile/books-read" > "$S/run/ocr.txt" 2>&1
    laid="$laid books($pics pictures, read by ocr: $(tail -1 "$S/run/ocr.txt"))"
  else
    laid="$laid books($pics pictures, notes only: $( [ "$pics" -gt 0 ] && echo 'no tesseract' || echo 'none yet'))"
  fi
else
  laid="$laid (books left out: no folder at $BOOKS)"
fi
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
rm -rf "$S/questions" && cp -r "$HERE/questions" "$S/questions"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
# The index: willow's index-cache, kept in SCRATCH between runs and rebuilt
# only when a file in the pile changed; the stack asks it through batch-ask.
python3 "$W/adapters/stdlib/index-cache/index_cache.py" --from "$S/pile" --to "$S/index" > "$S/index.log" || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile:$laid; $(find "$S/pile" -type f | wc -l) files"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "index: $(cat "$S/index.log")"
echo "page: $S/page.md  each step: $S/run/"
echo "ask it: bash $HERE/ask.sh $S \"your words\""
exit $code
