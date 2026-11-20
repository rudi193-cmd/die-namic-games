#!/bin/bash
# Lay a box over the session of 2026-11-20 and run its stack. Usage: rebuild.sh SCRATCH [COMMIT]
#
# The pile is what that session made, as it was at one commit, the last
# before this folder existed (unless you name another), so the stack never
# finds its own questions: open.md, README.md and box/README.md as git kept
# them; tonight.md, every commit's own message from the session, dated; and
# journey.txt, the whole journey played end to end on a fresh box.
# Willow, as the box finds it (WILLOW_ROOT, or beside), held to willow.pin.json.
#
# A fresh box each time. The key is a scratch key init makes, in SCRATCH,
# outside the box; nothing is ever sealed with it. Writes nothing into the
# repository.
set -u
PINNED=db37b51c43aa3896e9b6dc0ee0bb419427cd066e
FIRST=c0d9c91  # the commit the session started from
[ $# -eq 1 ] || [ $# -eq 2 ] || { echo "usage: rebuild.sh SCRATCH [COMMIT] (SCRATCH a folder outside the repository)"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$1" && S=$(cd "$1" && pwd) || exit 2
case "$S/" in "$R"/*) echo "refused: SCRATCH is inside the repository"; exit 2;; esac
AT=${2:-$PINNED}
git -C "$R" cat-file -e "$AT^{commit}" 2>/dev/null || { echo "refused: this checkout does not hold commit $AT; fetch it first"; exit 2; }
rm -rf "$S/box" "$S/run" "$S/pile" "$S/scratch.key" && mkdir -p "$S/run" "$S/pile/box"
for f in open.md README.md box/README.md; do git -C "$R" show "$AT:$f" > "$S/pile/$f" || exit 2; done
git -C "$R" log --reverse --format='## %ad %s%n%n%b' --date=short "$FIRST..$AT" > "$S/pile/tonight.md" || exit 2
cp "$HERE/journey.txt" "$S/pile/journey.txt"
cp "$HERE/words.txt" "$S/words.txt" && chmod 600 "$S/words.txt"
python3 "$W/kernel.py" init --box "$S/box" --pile "$S/pile" --key "$S/scratch.key" --words "$S/words.txt" >/dev/null || exit 2
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$S/box" --stack "$HERE/stack.md" --to "$S/run" > "$S/page.md" 2> "$S/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$S/box"
echo "pile: the session to ${AT:0:7}, $(git -C "$R" rev-list --count "$FIRST..$AT") commits, $(find "$S/pile" -type f | wc -l) files"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$S/run/00-stack.txt")"
echo "page: $S/page.md  each step: $S/run/"
exit $code
