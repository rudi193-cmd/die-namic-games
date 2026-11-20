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
# UTETY goes in beside it, at pile/hornbook-utety: the pedagogy engine
# utety-chat runs on, which the store's own docs cite (utety/core/mastery.py,
# store.py) and which the store alone can't show. It's found at
# ../hornbook-knowledge/utety or UTETY, held to UTETY_PINNED; without it the
# box is laid without it, and says so.
# Its branches and pull requests go in too, at pile/hornbook-utety/history
# (utety_history.py: each PR's title, state and every commit's message; each
# branch merged or ahead, and an unmerged branch's changed files), when the
# checkout has them: git fetch --unshallow origin
# '+refs/heads/*:refs/remotes/origin/*' '+refs/pull/*/head:refs/remotes/pr/*'.
# Those are as fetched, not pinned: the page says so.
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into
# either repository.
set -u
PINNED=ac07125836eb33c50a540b6efa17701d875d4a64
UTETY_PINNED=56662d1fc4e2d6d8a0661afe61add4a387d4e366
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
UT=${UTETY:-$R/../hornbook-knowledge/utety}
if [ -d "$UT/.git" ] && git -C "$UT" cat-file -e "$UTETY_PINNED^{commit}" 2>/dev/null; then
  mkdir -p "$S/pile/hornbook-utety" && git -C "$UT" archive "$UTETY_PINNED" | tar -x -C "$S/pile/hornbook-utety" || exit 2
  ut="UTETY at ${UTETY_PINNED:0:7} in pile/hornbook-utety"
  if python3 "$HERE/utety_history.py" "$UT" "$UTETY_PINNED" "$S/pile/hornbook-utety/history" >/dev/null 2>&1; then
    ut="$ut, its $(grep -c '^## PR #' "$S/pile/hornbook-utety/history/prs.md") PRs and $(grep -c '^## ' "$S/pile/hornbook-utety/history/branches.md") branches as fetched"
  else
    ut="$ut, its branches and PRs left out (not fetched)"
  fi
else
  ut="UTETY left out (no checkout holding $UTETY_PINNED at $UT; set UTETY)"
fi
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile: the store at ${AT:0:7}, $(find "$S/pile" -type f | wc -l) files, apps/nasa-archive left out; $ut"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "page: $S/page.md  each step: $S/run/"
exit $code
