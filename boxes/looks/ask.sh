#!/bin/bash
# Ask the looks box one or more questions, from its index, in about a second.
# Usage: ask.sh SCRATCH "your words" ["more words" ...]   (--top N first to change 8)
#
# SCRATCH is the folder rebuild.sh laid (it holds index/ and words.txt). The
# answers are the kernel's own (willow's batch-ask over index-cache's index),
# printed as each passage's file and line, then its first lines.
set -u
top=8
[ "${1:-}" = "--top" ] && { top=$2; shift 2; }
[ $# -ge 2 ] || { echo "usage: ask.sh [--top N] SCRATCH \"your words\" [...]"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$HERE/../.." && pwd)
S=$(cd "$1" && pwd) || exit 2; shift
[ -d "$S/index" ] || { echo "no index in $S: run rebuild.sh $S first"; exit 2; }
W=$(cd "$R" && python3 -c 'import sys; sys.path.insert(0, "box"); import willow_pin; print(willow_pin.root())') || exit 2
q=$(mktemp) && trap 'rm -f "$q"' EXIT
i=0; for a in "$@"; do i=$((i+1)); printf '%s\t%s\n' "$i" "$a" >> "$q"; done
python3 "$W/adapters/stdlib/batch-ask/scan.py" scan --index "$S/index" --words "$S/words.txt" --top "$top" --questions "$q" |
python3 -c '
import json, sys
qs = sys.argv[1:]
for line in sys.stdin:
    d = json.loads(line)
    served = d.get("served", [])
    print("== %s  (%s, %d)" % (qs[int(d["question"]) - 1], d["state"], len(served)))
    for s in served:
        text = " / ".join(l.strip() for l in s["text"].splitlines() if l.strip())
        print("  " + s["where"] + "\n      " + text[:220])
' "$@"
