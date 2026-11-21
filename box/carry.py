"""carry.py: what the characters carry, use up, and come through, from night to night. Python 3.9+.

The GM writes it on a sheet in plain words, one change a line, the way the
table says it:

    Tamsin finds a rope        Oro uses the rope
    Oro picks up a lantern     Tamsin gives away the lantern
    Oro is hurt by a club      Oro is healed

The name is a seated character's, first; the word after it says what
changed; the rest is the thing, or how. Each change is a `table-carry` row,
and a sheet is every row about that character read in order, so it carries
over between nights and between the parts of a story: nothing is taken off
the record, a thing used is a later row (willow's lending holds a loan the
same way: every line stays, a return is listed under it, never in place of
it), and a wound lasts until a line says they're healed (as livestock keeps
an animal's treatments). A thing is matched by its words, plural or not, so
"uses the ropes" spends "a rope".
"""

from __future__ import annotations

import re

import safety

KIND = "table-carry"
GAIN = ("finds", "found", "gets", "got", "picks up", "picked up", "takes", "took", "gains", "is given", "buys", "bought", "carries")  # fmt: skip
LOSE = ("uses up", "used up", "uses", "used", "loses", "lost", "spends", "spent", "drops", "dropped", "gives away", "gave away", "breaks", "broke")  # fmt: skip
HURT = ("is hurt", "gets hurt", "got hurt", "is wounded", "is poisoned", "is cursed")
HEAL = ("is healed", "heals", "healed", "is better", "is fine", "rests")
THE = re.compile(r"^(?:a|an|the|some|her|his|their|its|one)(?:\s+|$)", re.IGNORECASE)


def read(line: str, names: list[str]) -> dict | None:
    """{char, change (carry, spend, hurt, heal), what} from the GM's line, or
    None when it doesn't start with a seated name and a word this knows."""
    s = line.strip().rstrip(".!")
    for name in sorted(names, key=len, reverse=True):
        if s.lower().startswith(name.lower() + " "):
            rest = s[len(name) :].strip()
            for change, verbs in (("hurt", HURT), ("heal", HEAL), ("spend", LOSE), ("carry", GAIN)):  # fmt: skip
                for v in sorted(verbs, key=len, reverse=True):
                    if rest.lower() == v or rest.lower().startswith(v + " "):
                        what = rest[
                            len(v) :
                        ].strip()  # as written; matched without its article
                        if change in ("carry", "spend") and not THE.sub("", what):
                            return None
                        return {"char": name, "change": change, "what": what}
    return None


def same_thing(a: str, b: str) -> bool:
    """Two names for a thing, the same but for an article or a plural."""
    wa, wb = safety.words(THE.sub("", a)), safety.words(THE.sub("", b))
    return len(wa) == len(wb) and all(safety.same(x, y) for x, y in zip(wa, wb))


def sheet(rows: list[dict], name: str) -> tuple[list[str], list[str]]:
    """(what NAME carries now, how they're hurt now), from every row in order."""
    carrying: list[str] = []
    hurt: list[str] = []
    for r in rows:
        if r["kind"] != KIND or r.get("char", "").lower() != name.lower():
            continue
        if r["change"] == "carry":
            carrying.append(r["what"])
        elif r["change"] == "spend":
            hit = next((c for c in carrying if same_thing(c, r["what"])), None)
            if hit is not None:
                carrying.remove(hit)
        elif r["change"] == "hurt":
            hurt.append(r["what"])
        elif r["change"] == "heal":
            hurt = []
    return carrying, hurt


def said(name: str, carrying: list[str], hurt: list[str]) -> str:
    """One line a table reads aloud, or "" when there's nothing to say."""
    bits = []
    if carrying:
        bits.append("carries " + ", ".join(carrying))
    if hurt:
        how = "; ".join(h for h in hurt if h)
        bits.append("is still hurt" + (f" ({how})" if how else ""))
    return f"{name} " + " and ".join(bits) if bits else ""
