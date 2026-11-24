"""dw_record.py: a spike fight on the kernel's record, and a check that reads it from there. Python 3.9+.

Rows, written beside box/fight.py's (its kinds are `fight-open`, `fight-blow`,
`fight-end`, which this never writes and `fight.py check` never reads):

  xfight-open   the engine and its commit, and the fighters, whole: everything
                a replay needs that the rows don't say
  (tower rows)  tower-drop and tower-out, written by willow's dice-tower as the
                engine asks for each die
  xfight-row    one per row of dw_fight's fight (init, blow, down, end), the
                row itself under `row`, numbered under `fight` to the open row

`check_record` reads only the record: the kernel's chain must hold; the tower
must hold every die to its drop, none inside; the faces the tower brought out
between the open row and the first fight row must be the faces the fight rows
say were thrown, in order; and the fight, played again on those faces with
the fighters the open row names, must come out as the rows say.

The rows are the machine's: it rolls and remembers. It proposes nothing and
seals nothing. Limit: a fight's tower rows are read as the outs between its
open row and its first fight row, so nothing else may use the tower there.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import dw_fight as fs
import dw_tower as tf

kernel = tf.kernel
OPEN, ROW = "xfight-open", "xfight-row"
WHO = "fight-spike"
ENGINE = "dndwright 6f0fb9e"


def record(
    box: Path, fighters: list[fs.Fighter], die_dir: Path, ts: str | None = None
) -> list[dict]:
    """Play a fight on the tower, write it to the record; the fight's rows."""
    opened = kernel.append(box, ts or tf.now(), OPEN, who=WHO, engine=ENGINE, fighters=[asdict(f) for f in fighters])  # fmt: skip
    rows = fs.fight(fighters, tf.TowerFaces(box, die_dir, ts))
    for r in rows:
        kernel.append(box, ts or tf.now(), ROW, who=WHO, fight=opened["n"], row=r)
    return rows


def fights(rows: list[dict]) -> list[tuple[dict, list[dict]]]:
    """Every open row on the record with its fight rows, in order."""
    return [(o, [r for r in rows if r["kind"] == ROW and r.get("fight") == o["n"]]) for o in rows if o["kind"] == OPEN]  # fmt: skip


def check_record(box: Path) -> str | None:
    """None if every fight on the record holds; else the first thing that doesn't."""
    rows, breaks = kernel.read(Path(box) / "record.jsonl")
    if breaks:
        return f"the record's chain breaks: {breaks[0]}"
    _held, inside, why = tf.tower.check(rows)
    if why:
        return why
    if inside:
        return f"{len(inside)} die still in the tower"
    for opened, got in fights(rows):
        if not got:
            return f"fight at row {opened['n']} has no rows"
        written = [r["row"] for r in got]
        first = got[0]["n"]
        thrown = [int(r["faces"][0][0]) for r in rows if r["kind"] == tf.tower.OUT and opened["n"] < r["n"] < first]  # fmt: skip
        if thrown != fs.faces_of(written):
            return f"fight at row {opened['n']}: the rows' faces are not the tower's: tower {thrown}, rows {fs.faces_of(written)}"  # fmt: skip
        fighters = [fs.Fighter(**f) for f in opened["fighters"]]
        bad = fs.check(fighters, written)
        if bad:
            return f"fight at row {opened['n']}: {bad}"
    return None
