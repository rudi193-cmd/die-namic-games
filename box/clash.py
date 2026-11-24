"""clash.py: what the table already holds true that a new word may meet. Python 3.9+.

The heads-up before the GM decides is willow's game-canon add-on, through
the pin: what the table holds true, whether a new word meets it (willow's
contradictions rule), and the rows for "mine stands now" and "both are
true". game-canon hands in a replacement and stops there; it never seals.

What stays here is the table's own step: the GM types the choice, and only
then does this run the kernel's own `seal` on the replacement game-canon
handed in, the way play.py seals a call. Nothing here chooses.

- **Mine stands now:** the new word is sealed, and the replacement is
  handed in and sealed on the same choice. The old one stays on the record,
  read as replaced from then on.
- **Both are true:** a row that the two don't clash. It changes no truth,
  so it is no seal.
- **Keep the old one:** the new word isn't kept (a call is declined).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin

ROOT = willow_pin.root()
sys.path.insert(0, str(ROOT))
import kernel

canon = willow_pin.addon("game-canon")
KERNEL = ROOT / "kernel.py"
REPLACES, BOTH, SLIP = canon.REPLACES, canon.BOTH, canon.SLIP
standing, replaced, both, meets, tonight, keep_both = (
    canon.standing,
    canon.replaced,
    canon.both,
    canon.meets,
    canon.tonight,
    canon.keep_both,
)


def seal(box: Path, subject: str, ts: str) -> None:
    done = subprocess.run([sys.executable, str(KERNEL), "seal", "--box", str(box), "--now", ts, subject], capture_output=True, text=True, check=False)  # fmt: skip
    if done.returncode != kernel.ALIVE:
        raise RuntimeError((done.stderr or done.stdout).strip())


def replace(box: Path, ts: str, old: dict, new_subject: str, new_fact: str) -> None:
    """The GM's "mine stands now": game-canon hands the replacement in; sealed here on the GM's choice."""
    seal(box, canon.replace(box, ts, old, new_subject, new_fact), ts)


def take_back(box: Path, ts: str, old: dict) -> None:
    """A yes pressed by mistake, taken back: game-canon's replacement whose new
    word is nothing, sealed as "mine stands now" is. Nothing takes a seal back."""
    seal(box, canon.take_back(box, ts, old), ts)
