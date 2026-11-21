#!/bin/bash
# Throw a chunk into the pot. Usage: pour.sh POT NAME SOURCE [SUBDIR] [COMMIT]
#
# SOURCE is a git checkout (laid as git archive writes it at COMMIT, default
# HEAD, optionally only SUBDIR) or a plain folder or file. Only what reads as
# words is kept (.md .py .go .ts .cs .rs .ex .exs .toml .json .txt .rst,
# LICENSE files), without node_modules, bin, obj or lockfiles. It lands in
# POT/pile/NAME with _chunk.md saying where it came from, so every passage can
# be traced. Pouring a NAME again replaces that chunk. Nothing is sealed.
set -u
[ $# -ge 3 ] || { echo "usage: pour.sh POT NAME SOURCE [SUBDIR] [COMMIT]"; exit 2; }
POT=$1; NAME=$2; SRC=$3; SUB=${4:-.}; AT=${5:-HEAD}
case "$NAME" in */*|.*|"") echo "refused: NAME must be one plain word"; exit 2;; esac
mkdir -p "$POT/pile" && POT=$(cd "$POT" && pwd) || exit 2
D="$POT/pile/$NAME"; rm -rf "$D"; mkdir -p "$D"
KEEP=(--wildcards '*.md' '*.py' '*.go' '*.ts' '*.cs' '*.rs' '*.ex' '*.exs' '*.toml' '*.json' '*.txt' '*.rst' 'LICENSE*')
if [ -d "$SRC/.git" ]; then
  git -C "$SRC" cat-file -e "$AT^{commit}" 2>/dev/null || { echo "refused: $SRC has no $AT"; rmdir "$D"; exit 2; }
  FULL=$(git -C "$SRC" rev-parse "$AT")
  if [ "$SUB" = "." ]; then git -C "$SRC" archive "$FULL"; else git -C "$SRC" archive "$FULL" "$SUB"; fi | tar -x -C "$D" "${KEEP[@]}" 2>/dev/null
  [ "$SUB" = "." ] || { [ -d "$D/$SUB" ] && cp -a "$D/$SUB"/. "$D"/ && rm -rf "${D:?}/${SUB%%/*}"; }
  FROM="git $(git -C "$SRC" remote get-url origin 2>/dev/null || echo "$SRC") at $FULL, folder $SUB"
elif [ -d "$SRC" ]; then
  (cd "$SRC" && tar -c . ) | tar -x -C "$D" "${KEEP[@]}" 2>/dev/null; FROM="folder $SRC"
elif [ -f "$SRC" ]; then
  cp "$SRC" "$D/"; FROM="file $SRC"
else echo "refused: $SRC is not a folder, file or checkout"; rmdir "$D"; exit 2; fi
find "$D" \( -name node_modules -o -name bin -o -name obj -o -name '*lock*' \) -prune -exec rm -rf {} + 2>/dev/null
printf '# chunk: %s\n\nPoured %s from %s.\n' "$NAME" "$(date -u +%F)" "$FROM" > "$D/_chunk.md"
echo "poured $NAME: $(find "$D" -type f | wc -l) files ($FROM)"
