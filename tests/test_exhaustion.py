"""exhaustion.py read on its own: both SRD editions, kept apart, and what
each does to a roll, a speed and a hit point maximum."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "box"))
import exhaustion as ex


def test_5_2_takes_two_off_every_d20_and_five_feet_a_level():
    assert [ex.d20_modifier(n) for n in range(7)] == [0, -2, -4, -6, -8, -10, -12]
    assert [ex.speed_change(n, 30) for n in range(7)] == [30, 25, 20, 15, 10, 5, 0]
    assert ex.speed_change(6, 20) == 0  # never below 0


def test_5_1_gives_disadvantage_by_level_and_no_number():
    assert [ex.roll_mode("check", n, "5.1") for n in range(4)] == ["normal", "disadvantage", "disadvantage", "disadvantage"]  # fmt: skip
    assert [ex.roll_mode("attack", n, "5.1") for n in range(4)] == ["normal", "normal", "normal", "disadvantage"]  # fmt: skip
    assert (
        ex.roll_mode("save", 3, "5.1")
        == ex.roll_mode("attack", 3, "5.1")
        == "disadvantage"
    )
    assert ex.d20_modifier(4, "5.1") == 0


def test_5_1_speed_is_halved_from_two_and_zero_from_five():
    assert [ex.speed_change(n, 30, "5.1") for n in range(7)] == [
        30,
        30,
        15,
        15,
        15,
        0,
        0,
    ]
    assert ex.speed_change(2, 25, "5.1") == 12  # rounded down


def test_5_1_halves_the_hit_point_maximum_from_four_and_5_2_does_not():
    assert [ex.hp_max(n, 21, "5.1") for n in range(7)] == [21, 21, 21, 21, 10, 10, 10]
    assert ex.hp_max(4, 1, "5.1") == 1  # at least 1
    assert ex.hp_max(6, 21) == 21  # 5.2, the default


def test_the_default_is_5_2_so_no_disadvantage_unless_5_1_is_asked_for():
    assert ex.DEFAULT == "5.2"
    assert ex.roll_mode("check", 5) == "normal"
    assert ex.roll_mode("check", 5, "5.2") == "normal"
    assert ex.roll_mode("check", 5, "5.1") == "disadvantage"


def test_level_six_is_death_in_both_editions_and_only_then():
    assert [ex.dead(n) for n in range(7)] == [False] * 6 + [True]


def test_said_in_the_tables_words_for_each_edition():
    assert ex.said(0) == "not worn out"
    assert ex.said(2) == "worn out (2): every d20 roll -4, speed -10 feet"
    assert (
        ex.said(2, "5.1")
        == "worn out (2): disadvantage on ability checks, speed halved"
    )
    assert ex.said(6, "5.1") == ex.said(6) == "worn out to death"


@pytest.mark.parametrize("bad", [-1, 7, 2.0, "2", True, None])
def test_a_level_that_is_not_0_to_6_is_refused(bad):
    with pytest.raises(ValueError):
        ex.d20_modifier(bad)


def test_an_unknown_edition_or_kind_is_refused_not_guessed():
    with pytest.raises(ValueError):
        ex.d20_modifier(1, "5.5")
    with pytest.raises(ValueError):
        ex.roll_mode("skill", 1)


def test_a_long_rest_eases_one_level_and_never_below_zero():
    assert [ex.after_long_rest(n) for n in range(7)] == [0, 0, 1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        ex.after_long_rest(7)
