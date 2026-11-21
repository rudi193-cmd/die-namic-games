"""The spike's claims, each held to a run: every face is supplied, none is
guessed, every blow is a row, and a replay of the rows finds an edit."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fight_spike as fs

TAMSIN = fs.Fighter(
    "Tamsin", "party", hp=12, ac=14, init_mod=2, attack_bonus=4, damage="1d6+2"
)
ORO = fs.Fighter(
    "Oro", "party", hp=9, ac=12, init_mod=0, attack_bonus=3, damage="1d6+1"
)
GOBLIN = fs.Fighter(
    "Goblin", "foes", hp=7, ac=13, init_mod=2, attack_bonus=4, damage="1d6+2"
)
CAST = [TAMSIN, ORO, GOBLIN]
# init: Tamsin 14, Oro 9, goblin 9; Tamsin hits 15 (19) for 4 (+2 = 6), goblin 7 -> 1;
# goblin (init 11) misses 5; Oro misses 3; round 2: Tamsin hits 12 (16) for 5 (+2), goblin down.
FACES = [14, 9, 9, 15, 4, 5, 3, 12, 5]


def test_a_fight_on_story_characters_runs_on_faces_that_were_handed_in():
    rows = fs.fight(CAST, FACES)
    assert [r["kind"] for r in rows if r["kind"] != "blow"] == ["init", "init", "init", "down", "end"]  # fmt: skip
    first = next(r for r in rows if r["kind"] == "blow")
    assert (first["who"], first["d20"], first["total"], first["hit"], first["damage"], first["hp_after"]) == ("Tamsin", 15, 19, True, 6, 1)  # fmt: skip
    assert rows[-1] == {"kind": "end", "round": 2, "winner": "party"}
    assert fs.faces_of(rows) == FACES  # every face went somewhere, in order


def test_the_engine_has_no_dice_of_its_own_to_fall_back_on():
    with pytest.raises(fs.OutOfFaces):
        fs.fight(CAST, FACES[:5])


def test_a_face_that_is_not_on_the_die_is_refused():
    with pytest.raises(ValueError):
        fs.fight(CAST, [21, *FACES[1:]])
    with pytest.raises(ValueError):
        fs.fight(CAST, [0, *FACES[1:]])


def test_the_same_faces_give_the_same_fight_and_other_faces_do_not():
    assert fs.fight(CAST, FACES) == fs.fight(CAST, FACES)
    other = [
        14,
        9,
        9,
        2,
        5,
        3,
        3,
        12,
        5,
        *([3] * 60),
    ]  # faces valid on every die, so it runs to the end
    assert fs.fight(CAST, other) != fs.fight(CAST, FACES)


def test_a_replay_of_the_rows_accepts_what_was_played():
    assert fs.check(CAST, fs.fight(CAST, FACES)) is None


def test_a_replay_finds_an_edited_hit_point_or_a_hit_made_a_miss():
    rows = fs.fight(CAST, FACES)
    edited = [dict(r) for r in rows]
    edited[3]["hp_after"] = 5  # first blow: the goblin kept more hit points than it did
    assert "row 3 differs" in fs.check(CAST, edited)
    swapped = [dict(r) for r in rows]
    swapped[3]["d20"] = (
        2  # a die edited after the fact: the total and the hit no longer follow
    )
    assert fs.check(CAST, swapped) is not None


def test_a_natural_20_is_a_hit_and_doubles_the_damage_dice():
    f = [14, 9, 9, 20, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    rows = fs.fight(CAST, f)
    blow = next(r for r in rows if r["kind"] == "blow")
    assert blow["crit"] is True and blow["hit"] is True
    assert len(blow["dice"]) == 2  # dndwright rolls the dice twice on a crit
