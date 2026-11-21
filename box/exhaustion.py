"""exhaustion.py: what a level of exhaustion does to a roll. Python 3.9+.

A pure rule, no table and no record: a level in, an effect out. It is here
for open.md item 5's "a wound that changes a roll", and is NOT yet wired into
play: game-master's check holds a beat's total to the roll plus the stat
(open.md item 3), so a roll that a wound lowers is a willow change first.

The two SRD editions say different things about the same word, so both are
kept, named, never mixed:

  "5.1"  six cumulative levels: 1 disadvantage on ability checks, 2 speed
         halved, 3 disadvantage on attack rolls and saving throws, 4 hit point
         maximum halved, 5 speed 0, 6 death (SRD 5.1, CC-BY-4.0).
  "5.2"  every d20 test is reduced by 2 per level, Speed by 5 feet per level,
         level 6 is death (SRD 5.2, CC-BY-4.0).

Read from two open projects that each hold one: dndwright's conditions
catalog (5.1 wording) and srd_5e's `Srd.Rules.Exhaustion` (5.2). Written
afresh here, from the rules as they read, not copied from either.
"""

from __future__ import annotations

EDITIONS = ("5.1", "5.2")
MAX_LEVEL = 6


def _level(level: int) -> int:
    if (
        isinstance(level, bool)
        or not isinstance(level, int)
        or not 0 <= level <= MAX_LEVEL
    ):
        raise ValueError(f"exhaustion level is 0 to {MAX_LEVEL}, not {level!r}")
    return level


def _edition(edition: str) -> str:
    if edition not in EDITIONS:
        raise ValueError(f"edition is one of {EDITIONS}, not {edition!r}")
    return edition


def dead(level: int) -> bool:
    """Level 6 is death, in both editions."""
    return _level(level) >= MAX_LEVEL


def d20_modifier(level: int, edition: str = "5.2") -> int:
    """What every d20 test is changed by. 5.2: -2 a level. 5.1 has none: it
    gives disadvantage instead (see roll_mode)."""
    _level(level)
    return -2 * level if _edition(edition) == "5.2" else 0


def speed_change(level: int, speed: int, edition: str = "5.2") -> int:
    """A speed in feet, after exhaustion. 5.2: 5 feet off a level, never below
    0. 5.1: halved from level 2, 0 from level 5."""
    _level(level)
    if speed < 0:
        raise ValueError("speed is not below 0")
    if _edition(edition) == "5.2":
        return max(0, speed - 5 * level)
    if level >= 5:
        return 0
    return speed // 2 if level >= 2 else speed


def roll_mode(kind: str, level: int, edition: str = "5.1") -> str:
    """'disadvantage' or 'normal' for a kind of roll ('check', 'attack',
    'save'). Only 5.1 uses it: checks from level 1, attacks and saves from 3.
    In 5.2 it is always 'normal'; the penalty is d20_modifier."""
    _level(level)
    if kind not in ("check", "attack", "save"):
        raise ValueError("kind is 'check', 'attack' or 'save'")
    if _edition(edition) != "5.1":
        return "normal"
    if kind == "check":
        return "disadvantage" if level >= 1 else "normal"
    return "disadvantage" if level >= 3 else "normal"


def hp_max(level: int, maximum: int, edition: str = "5.1") -> int:
    """Hit point maximum: halved from level 4 in 5.1 (rounded down, at least 1);
    unchanged in 5.2."""
    _level(level)
    if maximum < 1:
        raise ValueError("a hit point maximum is at least 1")
    if _edition(edition) == "5.1" and level >= 4:
        return max(1, maximum // 2)
    return maximum


def said(level: int, edition: str = "5.2") -> str:
    """The effect in the table's words, as a GM would say it."""
    if _level(level) == 0:
        return "not worn out"
    if dead(level):
        return "worn out to death"
    if _edition(edition) == "5.2":
        return f"worn out ({level}): every d20 roll {d20_modifier(level)}, speed {-5 * level} feet"
    parts = []
    if level >= 1:
        parts.append("disadvantage on ability checks")
    if level >= 2:
        parts.append("speed halved")
    if level >= 3:
        parts.append("disadvantage on attacks and saves")
    if level >= 4:
        parts.append("hit point maximum halved")
    if level >= 5:
        parts.append("speed 0")
    return f"worn out ({level}): " + ", ".join(parts)
