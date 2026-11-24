"""The story's own fight on the play path: a story that names its foes gets f, the heroes
fight one of them with willow's play-fight on dice dropped in the tower, every blow is a
row, the GM's call on how it stands is asked as for any fight, and `open_table.py check`
has play-fight read the fight back from the record alone."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from test_table_turn import BOX, rows, table_turn

pytest.importorskip(
    "dndwright"
)  # the story's own fights are play-fight's, on dndwright


@pytest.fixture(scope="module")
def laid(tmp_path_factory) -> Path:
    home = tmp_path_factory.mktemp("home")
    code, _, _ = table_turn(home, [])
    assert code == 42
    return home


@pytest.fixture
def home(laid, tmp_path) -> Path:
    return shutil.copytree(laid, tmp_path / "home")


def with_foes(home: Path, foes: list[str], offers: list[str] | None = None) -> int:
    """The lantern fair, copied as a story that names its foes; its number in the menu."""
    worlds = home / "table" / "worlds"
    fair = json.loads((worlds / "lantern-fair.json").read_text())
    fair.update(id="lantern-fair-foes", title="Zed's Lantern Fair", foes=foes)
    if offers is not None:
        fair["offers"] = offers
    (worlds / "zz-lantern-fair-foes.json").write_text(json.dumps(fair))
    return len(list(worlds.glob("*.json")))  # sorted last of all


def go(home: Path, foe: int, extra=()):
    n = with_foes(home, ["scorched_belt_raider", "tide_touched_scout"])
    steps = [("Which story?", str(n)), (">", "f"), ("Which?", str(foe)), *extra]
    return table_turn(home, steps)


def test_a_story_that_names_foes_offers_f_and_one_that_doesnt_does_not(home):
    _code, out, _ = table_turn(home, [("Which story?", ""), (">", "f")])
    assert "f: a fight" not in out  # the lantern fair as it is: no f
    n = with_foes(home, ["scorched_belt_raider"])
    _code, out, _left = table_turn(home, [("Which story?", str(n)), (">", "z")])
    assert "· f: a fight" in out


def listed(home: Path) -> int:
    got = subprocess.run([sys.executable, str(BOX / "fight.py"), "list"], capture_output=True, text=True, check=False)  # fmt: skip
    return (
        len([ln for ln in got.stdout.splitlines() if ln.strip()])
        if got.returncode == 0
        else 0
    )


def test_the_heroes_fight_a_foe_and_every_blow_is_a_row_that_checks_from_the_record(
    home,
):
    first = (
        listed(home) + 1
    )  # after aetheris5e's encounters, when its dice are reachable
    _code, out, left = go(home, first)
    assert not left, out
    assert "against a Scorched Belt Raider" in out and "Tamsin, Oro against" in out.replace("⚔️  ", "")  # fmt: skip
    assert "Still standing:" in out
    assert "(What the fight means for the story is yours to say, GM.)" in out
    recs = rows(home)
    kinds = {r["kind"] for r in recs}
    assert {"fight-begin", "fight-row", "tower-drop", "tower-out"} <= kinds
    assert (
        not {"fight-open", "fight-blow", "fight-end"} & kinds
    )  # fight.py's are not touched
    done = subprocess.run([sys.executable, str(BOX / "open_table.py"), "check", "--table", str(home / "table")], capture_output=True, text=True, check=False)  # fmt: skip
    assert "## the story's own fights" in done.stdout, done.stdout + done.stderr
    assert "1 fight on the record, every one holds" in done.stdout
    assert (
        "the story's own fights:" not in done.stderr
    )  # check's own exit is the stack's


def test_the_story_that_turns_on_a_fight_asks_the_gm_how_it_stands(home):
    n = with_foes(home, ["scorched_belt_raider"], offers=["fight"])
    first = listed(home) + 1
    steps = [
        ("Which story?", str(n)),
        (">", "f"),
        ("Which?", str(first)),
        ("(y/n)", "n"),
    ]
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "Does it stand that the party won the fight?" in out


def test_the_recap_reads_the_story_s_own_fight_alongside_the_others(home):
    first = listed(home) + 1
    go(home, first)
    sys.path.insert(0, str(BOX))
    import session

    recs = rows(home)
    lines = session.fights(recs, None)
    assert len(lines) == 1 and lines[0].startswith("  the story's own fight: ")
    assert " rounds; standing: " in lines[0]


def test_a_foe_the_story_names_that_isnt_a_stat_block_is_left_out_not_guessed(home):
    n = with_foes(home, ["a_dragon"])
    _code, out, _left = table_turn(home, [("Which story?", str(n)), (">", "z")])
    assert "f: a fight" not in out


@pytest.mark.parametrize("foes", [[], None])
def test_no_foes_no_fight(home, foes):
    n = with_foes(home, foes or [])
    _code, out, _left = table_turn(home, [("Which story?", str(n)), (">", "z")])
    assert "f: a fight" not in out
