"""ideas.py: story ideas between sessions, made from what's in the box. Python 3.9+.

    python box/ideas.py --table DIR [--seed TEXT] [--count N]

For the GM's eyes, between sessions. Nothing here is canon and nothing is
handed in. The ideas are willow's story-ideas add-on, through the pin: this
hands it the table's record, its worlds and its binder (the pile), as
open_table.py lays them, and says what it says. Its card has the four parts
(seeds, set up and never played, still open, something you wrote and forgot).

Exit codes, the kernel's: 0 done; 2 refused.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a in ("--table", "--seed", "--count"):
            opts[a] = next(it, "")
        else:
            args.append(a)
    if not opts.get("--table") or args:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    table = Path(opts["--table"])
    if not (table / "record" / "kernel.json").exists():
        print(f"refused: {table} isn't a box laid by open_table.py", file=sys.stderr)
        return 2
    more = [x for k in ("--seed", "--count") if k in opts for x in (k, opts[k])]
    done = subprocess.run([sys.executable, str(willow_pin.script("story-ideas")), "--box", str(table / "record"), "--worlds", str(table / "worlds"), "--pile", str(table / "pile"), *more], capture_output=True, text=True, check=False)  # fmt: skip
    sys.stdout.write(done.stdout)
    sys.stderr.write(done.stderr)
    return done.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
