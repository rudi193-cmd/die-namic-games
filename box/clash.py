"""clash.py: what the table already holds true that a new word may meet. Python 3.9+.

The heads-up open.md asks for, before the GM decides: a call, or the GM's own
word at a blank moment, that is about the same thing as something the table
already made true. "About the same thing" is willow's contradictions rule,
unchanged (`subject` and `same`): the two share at least two of their own
words, and at least half of the shorter one's. It cannot tell whether they
disagree; it never picks a side. It only asks, and the GM decides.

Read only from the box's own record: nothing leaves it. (Jeles's
conflict_scan, the house's refutation search, looks on the web for two
independent sources; a table's story never goes there.)

What the GM chooses is kept:

- **Mine stands now:** the new word is sealed, and a proposal that it
  replaces the old one is handed in and sealed on the same choice, so
  nothing stops being true without the GM's seal. The old one stays on the
  record; read as replaced from then on.
- **Both are true:** a row that the two don't clash, so the pair isn't
  raised again. It changes no truth, so it is no seal.
- **Keep the old one:** the new word isn't kept (a call is declined).

Every row here is written by the kernel's append, and every seal by the
kernel's own `seal`, on the GM's choice; nothing here chooses.
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
sys.path.insert(0, str(ROOT / "adapters" / "stdlib" / "game-master"))
sys.path.insert(0, str(ROOT / "adapters" / "stdlib" / "contradictions"))
import contradictions
import game_master as gm
import kernel

KERNEL = ROOT / "kernel.py"
REPLACES, BOTH = "table-replaces", "table-both"
WHO = "die-namic"


def stems(text: str) -> set:
    return {kernel.stem(w) for w in contradictions.subject(text)}


def standing(box: Path, rows: list[dict]) -> list[dict]:
    """Everything the table holds true now, in every story: each sealed call
    and each sealed offer, unless a sealed replacement says it was replaced.
    {subject, fact, n (the seal's row), day}."""
    out = []
    for g in gm.games(rows):
        for a in g["asks"] + g["offers"]:
            what, got = gm.ruling(box, rows, a["subject"])
            if what == "sealed":
                out.append({"subject": a["subject"], "fact": a["fact"], "n": got["n"], "day": got["ts"][:10]})  # fmt: skip
    gone = {old for old, _ in replaced(box, rows).items()}
    return sorted((t for t in out if t["subject"] not in gone), key=lambda t: t["n"])


def replaced(box: Path, rows: list[dict]) -> dict:
    """{the old subject: the replacing row} for every replacement the GM sealed."""
    out = {}
    for r in rows:
        if r["kind"] == REPLACES and gm.ruling(box, rows, r["subject"])[0] == "sealed":
            out[r["old"]] = r
    return out


def both(rows: list[dict]) -> set:
    """The pairs of words the GM said are both true, by their words: the same
    two said again (a story played again) aren't raised again."""
    return {frozenset(r["facts"]) for r in rows if r["kind"] == BOTH}


def meets(box: Path, fact: str, subject: str = "") -> list[dict]:
    """What the table holds true that FACT is about the same thing as, not
    itself, not the same words made true again (a story played again), and
    not a pair the GM already said are both true."""
    rows, _ = kernel.read(box / "record.jsonl")
    said, ok = {"stems": stems(fact)}, both(rows)
    return [t for t in standing(box, rows)
            if t["subject"] != subject and t["fact"] != fact and frozenset((t["fact"], fact)) not in ok
            and contradictions.same(said, {"stems": stems(t["fact"])})]  # fmt: skip


def seal(box: Path, subject: str) -> None:
    done = subprocess.run([sys.executable, str(KERNEL), "seal", "--box", str(box), subject], capture_output=True, text=True, check=False)  # fmt: skip
    if done.returncode != kernel.ALIVE:
        raise RuntimeError((done.stderr or done.stdout).strip())


def replace(box: Path, ts: str, old: dict, new_subject: str, new_fact: str) -> None:
    """The GM's "mine stands now": a replacement handed in and sealed."""
    prop = {"path": f"table/replaces/{old['subject'].split(':')[-1][:16]}.txt", "data": new_fact, "cites": [],
            "claim": f"From now on this stands in place of what the table made true on {old['day']}: {old['fact']}"}  # fmt: skip
    subject, why = gm.hand_in(box, ts, f"die-namic replaces {old['subject']}", prop)
    if why:
        raise RuntimeError(why)
    kernel.append(box, ts, REPLACES, who=WHO, old=old["subject"], new=new_subject, fact=new_fact, subject=subject)  # fmt: skip
    seal(box, subject)


def keep_both(box: Path, ts: str, old: dict, new_subject: str, new_fact: str) -> None:
    """The GM's "both are true": the pair isn't raised again."""
    kernel.append(box, ts, BOTH, who=WHO, pair=sorted((old["subject"], new_subject)), facts=sorted((old["fact"], new_fact)))  # fmt: skip
