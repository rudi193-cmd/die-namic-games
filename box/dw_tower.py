"""dw_tower.py: faces for dw_fight from willow's dice-tower. Python 3.9+.

Each die the engine asks for is dropped in the tower (only its SHA-256 goes on
the record, with what it is for), then brought out: the secret goes on the
record and the face is what the secret gives, checked by the tower's own
`check`. So a face is never chosen by whoever runs the fight, and the record
can be held to it afterwards: `tower_match` compares the faces a fight's rows
say were thrown with the tower's `tower-out` rows, in order.

Limit, said plainly: here a die is dropped and brought out in the same breath,
when the engine asks for it. The tower's own property (nobody foresaw it, no
row written between drop and out can steer it) holds, but the *window* between
the drop and the out is an instant, not a moment posed to the table. A play
path would drop a round's d20s when the round is posed, and the damage dice
when a hit is known. And whoever holds the die files can look inside early
(the tower's README: that is the game master's screen, not a seal).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dw_fight as fs
import willow_pin

WILLOW = Path(willow_pin.root())
sys.path.insert(0, str(WILLOW))
_spec = importlib.util.spec_from_file_location("dice-tower", WILLOW / "adapters" / "stdlib" / "dice-tower" / "dice_tower.py")  # fmt: skip
tower = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tower)
kernel = tower.kernel


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TowerFaces:
    """A source for dw_fight.fight: draw(sides) drops a die and brings it out."""

    def __init__(self, box: Path, die_dir: Path, ts: str | None = None):
        self.box, self.die_dir, self.ts = Path(box), Path(die_dir), ts
        self.die_dir.mkdir(parents=True, exist_ok=True)
        self.why = ""
        self.n = len(
            list(self.die_dir.glob("die-*.json"))
        )  # a later fight goes on from the dice already here

    def say(self, why: str) -> None:
        self.why = why

    def draw(self, sides: int) -> int:
        self.n += 1
        die = self.die_dir / f"die-{self.n:04d}.json"
        with contextlib.redirect_stdout(io.StringIO()):
            if (
                tower.drop(self.box, f"1d{sides}", die, self.why, self.ts or now())
                != kernel.ALIVE
            ):
                raise RuntimeError(f"the tower would not take a d{sides}")
            rows, breaks = kernel.read(self.box / "record.jsonl")
            if (
                breaks
                or tower.out(self.box, rows, die, self.ts or now()) != kernel.ALIVE
            ):
                raise RuntimeError(f"the tower would not bring a d{sides} out")
        rows, _ = kernel.read(self.box / "record.jsonl")
        return int(rows[-1]["faces"][0][0])


def tower_match(box: Path, fight_rows: list[dict]) -> str | None:
    """None if the faces the fight's rows say were thrown are the faces the tower
    brought out, in order, and every die out holds to its drop with none left inside;
    else why not."""
    rows, breaks = kernel.read(Path(box) / "record.jsonl")
    if breaks:
        return "the record does not verify"
    _held, inside, why = tower.check(rows)
    if why:
        return why
    if inside:
        return f"{len(inside)} die still in the tower"
    out_faces = [int(r["faces"][0][0]) for r in rows if r["kind"] == tower.OUT]
    said = fs.faces_of(fight_rows)
    if out_faces != said:
        i = next((k for k, (a, b) in enumerate(zip(out_faces, said)) if a != b), min(len(out_faces), len(said)))  # fmt: skip
        return f"the rows and the tower part at face {i}: the tower brought out {out_faces[i:i+1]}, the rows say {said[i:i+1]}"  # fmt: skip
    return None
