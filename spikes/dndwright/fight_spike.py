"""fight_spike.py: a fight on a story's characters, run by dndwright, on dice somebody else supplies. Python 3.9+.

A SPIKE, outside the play path (nothing in box/ imports it; pytest's testpaths
is tests/, so it is run by name, see README.md). It answers one question from
open.md, "Round 5": can an outside rules engine run a fight on the story's
characters, with every face handed in (typed at a real table, or dropped from
the tower) and every blow a row a later check can replay?

dndwright needs pydantic and pyyaml; nothing else here does. dndwright rolls
through a `random.Random`-compatible object it is handed (`DiceEngine(rng=)`),
so the faces come from `Faces`, and the engine has no generator of its own to
fall back on: out of faces, it refuses.

Order of faces, fixed so a replay can read them back: initiative d20s in the
order the fighters are listed; then, in turn order, per blow one d20, and when
it hits, the damage dice. A fighter at 0 hit points is down (no death saves,
as in aetheris5e). Whom a fighter hits is the first one standing on the other
side: in play that is the GM's or the player's call, here it is fixed so the
spike has one answer.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from dndwright.combat.combat import CombatantState, apply_damage
from dndwright.combat.initiative import (
    InitiativeEntry,
    order_initiative,
    roll_initiative,
)
from dndwright.dice.engine import DiceEngine

MAX_ROUNDS = 20


class OutOfFaces(RuntimeError):
    """The engine asked for a die nobody supplied. It is never guessed."""


class Faces:
    """Faces handed in, in the order the engine asks for them."""

    def __init__(self, faces: list[int]):
        self._faces = list(faces)
        self.drawn: list[int] = []

    def draw(self, sides: int) -> int:
        if not self._faces:
            raise OutOfFaces(f"a d{sides} was asked for and no face is left")
        face = self._faces.pop(0)
        if not 1 <= face <= sides:
            raise ValueError(f"{face} is not on a d{sides}")
        self.drawn.append(face)
        return face

    @property
    def left(self) -> int:
        return len(self._faces)


class SaidRandom(random.Random):
    """The one generator dndwright is given: every die is a face from Faces."""

    def __init__(self, faces: Faces):
        super().__init__()
        self.faces = faces

    def randint(
        self, a: int, b: int
    ) -> int:  # dndwright rolls through randint(1, sides)
        if a != 1:
            raise ValueError("dice here run from 1")
        return self.faces.draw(b)


@dataclass(frozen=True)
class Fighter:
    name: str
    side: str  # "party" or "foes"
    hp: int
    ac: int
    init_mod: int
    attack_bonus: int
    damage: str  # e.g. "1d6+2"


def fight(fighters: list[Fighter], faces: list[int]) -> list[dict]:
    """The fight as rows: init, blow, down, end. Raises OutOfFaces if the faces run out."""
    src = Faces(faces)
    engine = DiceEngine(rng=SaidRandom(src))
    rows: list[dict] = []

    def row(**kw) -> None:
        rows.append(kw)

    inits = {}
    for f in fighters:
        r = roll_initiative(engine, f.init_mod)
        inits[f.name] = r.total
        row(kind="init", who=f.name, d20=r.roll, total=r.total)
    order = [
        e.name
        for e in order_initiative(
            InitiativeEntry(f.name, inits[f.name], dexterity_modifier=f.init_mod)
            for f in fighters
        )
    ]
    by = {f.name: f for f in fighters}
    state = {f.name: CombatantState(current_hp=f.hp, max_hp=f.hp) for f in fighters}

    def standing(side: str) -> list[str]:
        return [
            f.name for f in fighters if f.side == side and state[f.name].current_hp > 0
        ]

    for rnd in range(1, MAX_ROUNDS + 1):
        for name in order:
            me = by[name]
            if state[name].current_hp <= 0:
                continue
            other = "foes" if me.side == "party" else "party"
            foes = standing(other)
            if not foes:
                row(kind="end", round=rnd, winner=me.side)
                return rows
            target = foes[0]
            atk = engine.roll_attack(modifier=me.attack_bonus, target_ac=by[target].ac)
            blow = {
                "kind": "blow",
                "round": rnd,
                "who": name,
                "target": target,
                "d20": atk.roll.natural_roll,
                "total": atk.roll.total,
                "ac": by[target].ac,
                "hit": bool(atk.is_hit),
                "crit": atk.roll.is_critical,
            }
            if atk.is_hit:
                dmg = engine.roll_damage(me.damage, is_critical=atk.roll.is_critical)
                state[target], _ = apply_damage(state[target], dmg.roll.total)
                blow.update(damage=dmg.roll.total, dice=list(dmg.roll.individual_rolls))
            blow["hp_after"] = state[target].current_hp
            row(**blow)
            if state[target].current_hp <= 0:
                row(kind="down", who=target)
    row(kind="end", round=MAX_ROUNDS, winner="stalemate")
    return rows


def faces_of(rows: list[dict]) -> list[int]:
    """Every face the rows say was thrown, in the order the fight asked for them."""
    out: list[int] = []
    for r in rows:
        if r["kind"] == "init":
            out.append(r["d20"])
        elif r["kind"] == "blow":
            out.append(r["d20"])
            out.extend(r.get("dice", []))
    return out


def check(fighters: list[Fighter], rows: list[dict]) -> str | None:
    """Play the fight again on the rows' own faces; None if every row comes out as written,
    else what differed. An edited row (a hit, a total, a hit point) does not survive."""
    try:
        again = fight(fighters, faces_of(rows))
    except (OutOfFaces, ValueError) as e:
        return f"the rows' faces do not make a fight: {e}"
    for i, (a, b) in enumerate(zip(rows, again)):
        if a != b:
            return f"row {i} differs: wrote {a}, replay gives {b}"
    if len(rows) != len(again):
        return f"{len(rows)} rows written, {len(again)} on replay"
    return None
