"""fight.py: a 5e fight from aetheris5e, blow by blow on the box's record. Python 3.9+.

    python box/fight.py list
    python box/fight.py --table DIR fight ENCOUNTER [--now TS]
    python box/fight.py --table DIR check
    python box/fight.py --table DIR board [--fight ROW] [--round N]

the-table's aetheris5e has the fight: initiative, attacks against AC,
crits, resistances, recharging specials, the six stat blocks and the four
encounters (`list`). Its engine takes the place it writes as a sink, so
this hands it the box's own record: every blow is a kernel row, the way
play-dice5e writes a roll, and nothing else is needed to keep a fight.

The dice are seeded the way play-dice5e seeds a roll: by the hash of the
row before the fight opens. So nobody picks the seed, and `check` plays
every fight on the record again from its seed and refuses one whose blows
aren't what that seed gives (a hit edited, a blow dropped), as well as a
record whose chain doesn't hold.

A fight is the machine's: it rolls and remembers. It proposes nothing,
seals nothing and never reads the key; what a fight means for the story is
the GM's to say.

aetheris5e's dice come from the one-script (willow-bot's), with the MIT
`dice` library its requirements name: set ONESCRIPT_HOME, or check
willow-bot out beside die-namic-games.

`board` draws a fight from its rows (box/board.py): each fighter's hit
points as a bar, who's down, stunned or blinded, the round, and whose turn
is next; the last fight on the record unless --fight names its open row,
as it ended unless --round says which round to stop at.

Exit codes, the kernel's: 0 done; 2 refused.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AETHERIS = HERE.parent / "the-table" / "aetheris5e"
sys.path.insert(0, str(HERE))
import willow_pin

sys.path.insert(0, str(willow_pin.root()))
import kernel

OPEN, BLOW, END = "fight-open", "fight-blow", "fight-end"
WHO = "fight"


def engine():
    """aetheris5e's combat and stat blocks, imported where they live."""
    sys.path.insert(0, str(AETHERIS))
    import combat
    import statblocks

    return combat, statblocks


class Kept:
    """The engine's sink, kept in a list: what a fight wrote, in order."""

    def __init__(self):
        self.blows: list[tuple[str, dict]] = []

    def snapshot(self, state, note=""):
        self.blows.append((note, json.loads(json.dumps(state))))


def play(encounter: str, seed: str) -> tuple[list[tuple[str, dict]], dict]:
    """(every blow as (note, state), the result) of ENCOUNTER from SEED."""
    combat, statblocks = engine()
    if encounter not in statblocks.ENCOUNTERS:
        raise KeyError(f"no encounter {encounter!r}: {', '.join(statblocks.ENCOUNTERS)}")  # fmt: skip
    kept = Kept()
    rng = random.Random(int(seed, 16) if seed != kernel.GENESIS else 0)
    res = combat.Combat(statblocks.build_encounter(encounter), rng, sink=kept).run()
    return kept.blows, json.loads(json.dumps(res))


def fight(box: Path, encounter: str, ts: str) -> int:
    rows, breaks = kernel.read(box / "record.jsonl")
    if breaks:
        return refused("the record doesn't verify: " + "; ".join(breaks))
    seed = rows[-1]["hash"] if rows else kernel.GENESIS
    try:
        blows, res = play(encounter, seed)
    except KeyError as e:
        return refused(str(e.args[0]))
    _, statblocks = engine()
    opened = kernel.append(box, ts, OPEN, who=WHO, encounter=encounter, seed=seed,
                           desc=statblocks.ENCOUNTERS[encounter]["desc"])  # fmt: skip
    print(f"{statblocks.ENCOUNTERS[encounter]['desc']}   (row {opened['n']})")
    for note, state in blows:
        kernel.append(box, ts, BLOW, who=WHO, fight=opened["n"], note=note, state=state)  # fmt: skip
        print(f"  {note}")
    end = kernel.append(box, ts, END, who=WHO, fight=opened["n"], result=res)
    standing = ", ".join(res["party_survivors"] + res["foe_survivors"]) or "no one"
    print(f"{res['outcome'].upper()} in {res['rounds']} rounds; standing: {standing}   (rows {opened['n']}-{end['n']})")  # fmt: skip
    return kernel.ALIVE


def check(box: Path) -> int:
    rows, breaks = kernel.read(box / "record.jsonl")
    if breaks:
        return refused("the record doesn't verify: " + "; ".join(breaks))
    held = 0
    for r in rows:
        if r["kind"] != OPEN:
            continue
        before = rows[r["n"] - 1]["hash"] if r["n"] else kernel.GENESIS
        if r.get("seed") != before:
            return refused(f"row {r['n']}: its seed isn't the hash of the row before it")  # fmt: skip
        try:
            blows, res = play(r["encounter"], r["seed"])
        except KeyError as e:
            return refused(f"row {r['n']}: {e.args[0]}")
        mine = [(b["note"], b["state"]) for b in rows if b["kind"] == BLOW and b.get("fight") == r["n"]]  # fmt: skip
        ends = [e["result"] for e in rows if e["kind"] == END and e.get("fight") == r["n"]]  # fmt: skip
        for i, (got, again) in enumerate(zip(mine, blows)):
            if got != again:
                return refused(f"fight at row {r['n']}, blow {i + 1}: {got[0]!r} isn't what its seed gives ({again[0]!r})")  # fmt: skip
        if len(mine) != len(blows) or ends != [res]:
            return refused(f"fight at row {r['n']}: {len(mine)} blows and {len(ends)} ending on the record; its seed gives {len(blows)} and one")  # fmt: skip
        held += 1
    print(f"{held} fight{'s' if held != 1 else ''} on the record; every blow holds.")
    return kernel.ALIVE


def board_of(box: Path, fight_at: str, upto: str) -> int:
    import board

    rows, breaks = kernel.read(box / "record.jsonl")
    if breaks:
        return refused("the record doesn't verify: " + "; ".join(breaks))
    opened = [r["n"] for r in rows if r["kind"] == OPEN]
    if not opened:
        return refused("no fight on the record")
    if (fight_at and not fight_at.isdigit()) or (upto and not upto.isdigit()):
        return refused("--fight and --round are numbers")
    at = int(fight_at) if fight_at else opened[-1]
    if at not in opened:
        return refused(f"row {at} doesn't open a fight; fights open at rows {', '.join(map(str, opened))}")  # fmt: skip
    print(board.draw(board.state(rows, at, int(upto) if upto else None)))
    return kernel.ALIVE


def refused(why: str) -> int:
    print(f"refused: {why}", file=sys.stderr)
    return kernel.REFUSED


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a in ("--table", "--now", "--fight", "--round"):
            opts[a] = next(it, "")
        else:
            args.append(a)
    if args == ["list"]:
        _, statblocks = engine()
        for name, e in statblocks.ENCOUNTERS.items():
            print(f"  {name:<10} {e['desc']}")
        return kernel.ALIVE
    box = Path(opts.get("--table", "")) / "record"
    if not opts.get("--table") or not (box / "record.jsonl").is_file() or args[:1] not in (["fight"], ["check"], ["board"]) or len(args) != (2 if args[0] == "fight" else 1):  # fmt: skip
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return kernel.REFUSED
    if args == ["check"]:
        return check(box)
    if args == ["board"]:
        return board_of(box, opts.get("--fight", ""), opts.get("--round", ""))
    return fight(box, args[1], opts.get("--now") or kernel.now())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
