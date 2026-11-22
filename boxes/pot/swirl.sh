#!/bin/bash
# Swirl the pot: lay a fresh box over everything poured so far and run the
# pot's own stack. Usage: swirl.sh POT [--ask "a question"] [--stack FILE]
#
# The pile (POT/pile) is what is kept between swirls; the box is made fresh
# each time (POT/box) under a scratch key in POT, nothing ever sealed. The
# page lands in POT/swirl/page.md. --ask adds one one-off want, as
# all-passages, to the stack for this swirl; --stack swaps in another stack.
# Willow, as the box finds it, held to willow.pin.json. An empty pot swirls
# too, and says so.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
[ $# -ge 1 ] || { echo 'usage: swirl.sh POT [--ask "question"] [--stack FILE]'; exit 2; }
POT=$1; shift; ASK=""; STACK="$HERE/stack.md"
while [ $# -gt 0 ]; do case "$1" in --ask) ASK=$2; shift 2;; --stack) STACK=$2; shift 2;; *) echo "refused: $1"; exit 2;; esac; done
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
mkdir -p "$POT/pile" "$POT/swirl" && POT=$(cd "$POT" && pwd) || exit 2
case "$POT/" in "$R"/*|"$W"/*) echo "refused: POT is inside a repository"; exit 2;; esac
[ -f "$POT/words.txt" ] || cp "$HERE/words.txt" "$POT/words.txt"; chmod 600 "$POT/words.txt"
n=$(find "$POT/pile" -type f ! -name _chunk.md | wc -l)
if [ "$n" -eq 0 ]; then echo "the pot is empty: pour something in first (pour.sh POT NAME SOURCE)"; exit 3; fi
rm -rf "$POT/box" "$POT/run" "$POT/scratch.key" && mkdir -p "$POT/run"
python3 "$W/kernel.py" init --box "$POT/box" --pile "$POT/pile" --key "$POT/scratch.key" --words "$POT/words.txt" >/dev/null || exit 2
S="$STACK"
if [ -n "$ASK" ]; then
  S="$POT/swirl/stack-with-ask.md"; cp "$STACK" "$S"
  q=${ASK//\"/}
  printf '\n## asked just now\n\nWant: "%s"\n- all-passages -- --box {box} --top 8 "%s"\n' "$q" "$q" >> "$S"
fi
start=$(date +%s)
python3 "$W/adapters/stdlib/stack/stack.py" --box "$POT/box" --stack "$S" --to "$POT/run" > "$POT/swirl/page.md" 2> "$POT/swirl/page.err"
code=$?
python3 "$W/kernel.py" verify --box "$POT/box"
echo "pot: $(ls "$POT/pile" | tr '\n' ' ')($n files)"
echo "stack: exit $code, $(( $(date +%s) - start )) s; $(tail -1 "$POT/run/00-stack.txt")"
echo "page: $POT/swirl/page.md"
exit $code
