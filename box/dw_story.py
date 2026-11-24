"""dw_story.py: a story's characters, and aetheris5e's stat blocks, as fighters for willow's play-fight. Python 3.9+.

A fighter is the object play-fight's fighters file holds (its card names the
fields): name, side, hp, ac, init_mod, attack_bonus, damage, attacks. This
file says where the numbers come from; play-fight, through the pin, fights.

A story character has a name and a bonus on some of the story's own stats
(the lantern fair: Grit, Wit, Heart), over a base. It has no hit points, armor
class or attack. These are the defaults this file MAKES UP, so a fight has
one answer; they are a design decision for the table, not a rule from any SRD:

  stats        the story's own list; by position: the first is the body
               (Grit, Brave), the second the mind (Wit, Clever), the third the
               heart (Heart, Kind). Any further stat is counted for hit points
               and armor only.
  hit points   8 + 2 for every point of bonus, all stats together
  armor class  11 + the best single bonus
  initiative   the bonus on the second stat
  attack       2 + the bonus on the first stat; damage 1d6 plus that bonus
  one blow a turn.

A character's own `"fight": {...}` in the world file wins over any of these
(keys: hp, ac, init_mod, attack_bonus, damage, attacks): a story that says
its hero has 30 hit points gets 30. Only seated characters fight for the
party, as the box seats them (`"seat": true`).

A stat block (aetheris5e's, in willow's play-fight5e) already is numbers: armor class,
hit points, initiative, and attacks with a bonus and a damage expression. Its
first attack is used, `multiattack` blows a turn; its specials, saves and
resistances are NOT carried (nothing here reads them).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import willow_pin

statblocks = willow_pin.addon("play-fight5e", "statblocks")  # aetheris5e's, in willow

FIGHT_KEYS = {"hp", "ac", "init_mod", "attack_bonus", "damage", "attacks"}


def _bonus(c: dict, stats: list[str], i: int) -> int:
    if i >= len(stats):
        return 0
    return int(c.get("stats", {}).get(stats[i], 0))


def from_character(c: dict, stats: list[str], side: str = "party") -> dict:
    """One story character as a fighter, by the defaults above; `c["fight"]` overrides them."""
    given = c.get("stats", {})
    body = _bonus(c, stats, 0)
    total = sum(int(v) for v in given.values())
    best = max([int(v) for v in given.values()] + [0])
    made = {
        "hp": 8 + 2 * total,
        "ac": 11 + best,
        "init_mod": _bonus(c, stats, 1),
        "attack_bonus": 2 + body,
        "damage": f"1d6+{body}" if body > 0 else "1d6",
        "attacks": 1,
    }
    own = c.get("fight", {})
    unknown = set(own) - FIGHT_KEYS
    if unknown:
        raise ValueError(
            f"{c.get('name')}: fight has no {sorted(unknown)}; it takes {sorted(FIGHT_KEYS)}"
        )
    made.update(own)
    return {"name": c["name"], "side": side, **made}


def party_from_world(world: dict) -> list[dict]:
    """The seated characters of a story, as the party."""
    stats = list(world.get("stats", []))
    return [from_character(c, stats) for c in world["characters"] if c.get("seat")]


def from_statblock(key: str, name: str | None = None) -> dict:
    """One of aetheris5e's foes (a key of statblocks.FOES) as a fighter."""
    if key not in statblocks.FOES:
        raise KeyError(f"no foe {key!r}; known: {sorted(statblocks.FOES)}")
    sb = statblocks.FOES[key]()
    if not sb["attacks"]:
        raise ValueError(f"{key} has no attack to fight with")
    a = sb["attacks"][0]
    return {
        "name": name or sb["name"],
        "side": "foes",
        "hp": sb["hp"],
        "ac": sb["ac"],
        "init_mod": sb["init"],
        "attack_bonus": a["atk"],
        "damage": a["dmg"],
        "attacks": sb.get("multiattack", 1),
    }


def world(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
