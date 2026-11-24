"""fight.py: a 5e fight from aetheris5e, blow by blow on the box's record. Python 3.9+.

    python box/fight.py list
    python box/fight.py --table DIR fight ENCOUNTER [--now TS]
    python box/fight.py --table DIR check
    python box/fight.py --table DIR board [--fight ROW] [--round N]

The fight is willow's play-fight5e add-on, through the pin: aetheris5e's
rules (initiative, attacks against AC, crits, resistances, recharging
specials, stun and blind), its six stat blocks and its four encounters
(`list`), every die dropped in willow's dice-tower and brought out, every
blow a row (`encounter-open`, `encounter-blow`, `encounter-end`). `check`
plays every fight on the record again on the tower's own faces; `board`
draws one. This hands it the table's record, and `tower/encounters` at the
table for its dice, and says what it says.

A fight is the machine's: it rolls and remembers. It proposes nothing,
seals nothing and never reads the key; what a fight means for the story is
the GM's to say. play-fight5e needs the MIT `dice` library: its card says
the install.

Exit codes, the kernel's: 0 done; 2 refused.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin


def run(*argv: str) -> int:
    done = subprocess.run([sys.executable, str(willow_pin.script("play-fight5e")), *argv], capture_output=True, text=True, check=False)  # fmt: skip
    sys.stdout.write(done.stdout)
    sys.stderr.write(done.stderr)
    return done.returncode


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a in ("--table", "--now", "--fight", "--round"):
            opts[a] = next(it, "")
        else:
            args.append(a)
    if args == ["list"]:
        return run("list")
    table = Path(opts.get("--table", ""))
    box = table / "record"
    if not opts.get("--table") or not (box / "record.jsonl").is_file() or args[:1] not in (["fight"], ["check"], ["board"]) or len(args) != (2 if args[0] == "fight" else 1):  # fmt: skip
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    if args == ["check"]:
        return run("--box", str(box), "check")
    if args == ["board"]:
        more = [x for k in ("--fight", "--round") if opts.get(k) for x in (k, opts[k])]
        return run("--box", str(box), "board", *more)
    dice = table / "tower" / "encounters"
    dice.mkdir(parents=True, mode=0o700, exist_ok=True)
    now = ["--now", opts["--now"]] if opts.get("--now") else []
    return run("--box", str(box), "fight", args[1], "--to", str(dice), *now)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
