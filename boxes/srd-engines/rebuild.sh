#!/bin/bash
# Lay a box over four open SRD rules engines and run its stack. Usage: rebuild.sh SCRATCH
#
# The pile is each engine at one commit (git archive from a checkout under
# ENGINES, or beside die-namic-games as ../OWNER/NAME), keeping what reads as
# words: .md .cs .rs .py .ex .exs .toml .json .txt and LICENSE files. The
# Elixir srd_5e lives in a monorepo (autodidaddict/agentic-realms): only its
# packages/srd_5e folder and the repository's LICENSE are laid, as srd_5e/.
# jurnalis-project/engine carries no LICENSE file at that commit; the box says
# what its README says and no more. Willow, as the box finds it, held to
# willow.pin.json.
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into any
# repository.
set -u
# folder-in-pile : checkout (OWNER/NAME) : commit : subfolder to lay ("." for all)
ENGINES="opencombatengine:jamesplotts/opencombatengine:16b45b08888ee92402c01a263967a6e48d0b07d7:.
jurnalis-engine:jurnalis-project/engine:dbf40d4184bbea6b788d67549e841796bb603335:.
srd_5e:autodidaddict/agentic-realms:b0a21642bfd20824dc23b110a4b1e70d264e43cf:packages/srd_5e
dndwright:sligara7/dndwright:6f0fb9e8a6cb6e25f45dd5b6262050b7d64ad1e1:."
[ $# -eq 1 ] || { echo "usage: rebuild.sh SCRATCH (a folder outside the repositories)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
BASE=${ENGINES_DIR:-$R/..}
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*) echo "refused: SCRATCH is inside the repository"; exit 2;; esac
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile"
laid=""
for e in $ENGINES; do
  IFS=: read -r name repo at sub <<< "$e"
  co="$BASE/$repo"
  if [ -d "$co/.git" ] && git -C "$co" cat-file -e "$at^{commit}" 2>/dev/null; then
    mkdir -p "$S/pile/$name"
    if [ "$sub" = "." ]; then spec=""; else spec="$sub LICENSE"; fi
    git -C "$co" archive "$at" $spec | tar -x -C "$S/pile/$name" \
      --wildcards '*.md' '*.cs' '*.rs' '*.py' '*.ex' '*.exs' '*.toml' '*.json' '*.txt' 'LICENSE*' 2>/dev/null
    [ "$sub" = "." ] || { [ -d "$S/pile/$name/$sub" ] && mv "$S/pile/$name/$sub"/* "$S/pile/$name"/ && rm -rf "$S/pile/$name/packages"; }
    find "$S/pile/$name" \( -name node_modules -o -name bin -o -name obj -o -name '*lock*' \) -prune -exec rm -rf {} + 2>/dev/null
    laid="$laid $name@${at:0:7}"
  else
    laid="$laid ($name left out: no checkout holding ${at:0:7} at $co)"
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
