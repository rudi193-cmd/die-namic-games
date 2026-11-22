"""session.xfight_summary and the recap line for the story's own fights, read from
rows built by hand (no dndwright, no tower): who is still standing is whoever has
more than 0 hit points, the rounds are the latest blow's, and the outcome is the
end row's winner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "box"))
import session

FIGHTERS = [
    {"name": "A", "side": "party", "hp": 10},
    {"name": "B", "side": "party", "hp": 8},
    {"name": "G", "side": "foes", "hp": 7},
]


def open_row(n: int = 1) -> dict:
    return {"n": n, "kind": "xfight-open", "fighters": FIGHTERS}


def blow(fight: int, target: str, hp_after: int, rnd: int = 1) -> dict:
    row = {
        "kind": "blow",
        "round": rnd,
        "who": "x",
        "target": target,
        "hp_after": hp_after,
    }
    return {"n": 0, "kind": "xfight-row", "fight": fight, "row": row}


def end(fight: int, winner: str, rnd: int = 9) -> dict:
    return {"n": 0, "kind": "xfight-row", "fight": fight, "row": {"kind": "end", "round": rnd, "winner": winner}}  # fmt: skip


def test_a_fighter_at_one_hit_point_stands_and_one_at_zero_does_not():
    rows = [
        open_row(),
        blow(1, "A", 1),
        blow(1, "B", 0),
        blow(1, "G", 0),
        end(1, "foes"),
    ]
    got = session.xfight_summary(rows, 1)
    assert got["party_survivors"] == ["A"]
    assert got["foe_survivors"] == []


def test_a_fighter_never_hit_still_stands_at_the_hit_points_they_began_with():
    got = session.xfight_summary([open_row(), blow(1, "G", 0), end(1, "party")], 1)
    assert got["party_survivors"] == ["A", "B"]
    assert got["foe_survivors"] == []


def test_a_foe_left_standing_is_named_on_its_own_side():
    got = session.xfight_summary([open_row(), blow(1, "A", 0), blow(1, "B", 0), blow(1, "G", 3), end(1, "foes")], 1)  # fmt: skip
    assert (got["party_survivors"], got["foe_survivors"]) == ([], ["G"])


def test_the_rounds_are_the_latest_blows_not_the_last_written_nor_the_end_rows():
    rows = [
        open_row(),
        blow(1, "G", 5, rnd=3),
        blow(1, "G", 4, rnd=1),
        end(1, "party", rnd=9),
    ]
    assert session.xfight_summary(rows, 1)["rounds"] == 3


def test_a_fight_with_no_blows_has_no_rounds():
    assert session.xfight_summary([open_row(), end(1, "stalemate")], 1)["rounds"] == 0


def test_the_outcome_is_the_end_rows_winner_and_a_missing_one_is_a_stalemate():
    for winner, outcome in (
        ("party", "party"),
        ("foes", "foe"),
        ("stalemate", "stalemate"),
    ):
        assert (
            session.xfight_summary([open_row(), end(1, winner)], 1)["outcome"]
            == outcome
        )
    assert (
        session.xfight_summary([open_row(), blow(1, "G", 2)], 1)["outcome"]
        == "stalemate"
    )


def test_another_fights_rows_are_not_this_ones():
    rows = [open_row(1), open_row(5), blow(5, "A", 0, rnd=7), end(5, "foes"), blow(1, "G", 0, rnd=2), end(1, "party")]  # fmt: skip
    got = session.xfight_summary(rows, 1)
    assert (got["outcome"], got["rounds"], got["party_survivors"]) == (
        "party",
        2,
        ["A", "B"],
    )


def test_the_recap_says_how_each_of_the_storys_own_fights_ended():
    for winner, said in (("party", "the party won"), ("foes", "the party fell"), ("stalemate", "neither side fell")):  # fmt: skip
        rows = [open_row(0), blow(0, "G", 0, rnd=2), end(0, winner)]
        lines = session.fights(rows, None)
        assert lines == [f"  the story's own fight: {said} in 2 rounds; standing: A, B   (row 0)"], lines  # fmt: skip


def test_a_fight_with_no_end_row_is_not_in_the_recap_and_one_outside_the_session_is_not_either():
    assert session.fights([open_row(0), blow(0, "G", 3)], None) == []
    done = [open_row(0), blow(0, "G", 0), end(0, "party")]
    assert session.fights(done, {"from": 5, "to": 9}) == []
    assert len(session.fights(done, {"from": 0, "to": 0})) == 1
