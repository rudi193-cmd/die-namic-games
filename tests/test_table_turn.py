"""The table's turn before each roll, in box/play.py: Enter rolls, o is
someone bringing something into the story (game-master's own offer), f a
fight (in a story fights belong to).

Played by a person at the keyboard who reads each question (tests/person.py),
since what comes before which roll is the dice's to say. What is held: the GM
is asked before anything is handed in, an offer is the character's, sealed
or declined once, and what it unlocks plays; a fight is kept on the record
and checks; walking away leaves nothing half done."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import person
import pytest

BOX = Path(__file__).resolve().parents[1] / "box"
NOW = "2026-11-20T19:00:00Z"
VELL = "Old Vell from the lantern fair comes down the stair."
HINT = "  Enter: roll · o: someone brings something in · x: set it aside\n> "


def table_turn(home: Path, steps: list, every: dict | None = None, now: str = NOW):
    env = {"DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": now}
    answer = person.answering(steps, every)
    code, out = person.at_table([BOX / "play.py"], env, answer)
    return code, out, answer.left


@pytest.fixture(scope="module")
def laid(tmp_path_factory) -> Path:
    home = tmp_path_factory.mktemp("home")
    code, _, _ = table_turn(home, [])
    assert code == 42
    return home


@pytest.fixture
def home(laid, tmp_path) -> Path:
    return shutil.copytree(laid, tmp_path / "home")


def rows(home: Path) -> list[dict]:
    return [json.loads(line) for line in (home / "table" / "record" / "record.jsonl").read_text().splitlines()]  # fmt: skip


def answered(home: Path, subject: str) -> list[str]:
    return [r["kind"] for r in rows(home) if r.get("subject") == subject and r["kind"] in ("seal", "decline", "table-heard")]  # fmt: skip


CELLAR = ("Which story?", "4")  # The Clockwork Cellar, with nothing played


def test_each_roll_waits_for_enter_and_a_word_that_isnt_one_is_asked_again(home):
    _code, out, left = table_turn(home, [("Which story?", ""), (">", "z")])
    assert (
        out.count(HINT) >= 2 and "f: a fight" not in out
    )  # the lantern fair has no fights
    assert "  Press Enter to roll, o or x.\n" in out and not left
    first = out.split(HINT)[0]
    assert "🎲" not in first  # nothing rolled before the first Enter


def test_someone_brings_something_in_and_the_gm_says_yes(home):
    steps = [CELLAR, (">", "o"), ("Who?", "1"), ("bring in?", VELL), ("Which?", "2"), ("(y/n)", "y")]  # fmt: skip
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert f"✋ Your call, GM. Pell brings this in:\n   {VELL}\n   Is that true in your world? (y/n)    It's true now." in out  # fmt: skip
    offer = [r for r in rows(home) if r["kind"] == "table-offer"]
    assert len(offer) == 1 and offer[0]["by"] == "pell" and "as" not in offer[0]
    assert answered(home, offer[0]["subject"]) == ["seal", "table-heard"]
    canon = subprocess.run([sys.executable, BOX / "session.py", "--table", home / "table", "canon"], capture_output=True, text=True, check=False).stdout  # fmt: skip
    assert f"{VELL}  [offered by pell]" in canon


def test_no_is_declined_and_the_story_goes_on(home):
    steps = [CELLAR, (">", "o"), ("Who?", "2"), ("bring in?", VELL), ("Which?", "2"), ("(y/n)", "n")]  # fmt: skip
    _code, out, _left = table_turn(home, steps)
    assert "Juno brings this in:" in out and "It didn't happen." in out
    offer = next(r for r in rows(home) if r["kind"] == "table-offer")
    assert offer["by"] == "juno" and answered(home, offer["subject"]) == ["decline", "table-heard"]  # fmt: skip
    assert out.split("It didn't happen.")[1].startswith(
        "\n" + HINT
    )  # back to the same roll


def test_a_guest_is_offered_as_one_and_what_waits_on_a_guest_plays(home):
    steps = [CELLAR, (">", "o"), ("Who?", "1"), ("bring in?", VELL), ("Which?", "1"), ("(y/n)", "y")]  # fmt: skip
    _code, out, _left = table_turn(home, steps, {">": "", "Is that true in your world? (y/n)": "y"})  # fmt: skip
    offer = next(r for r in rows(home) if r["kind"] == "table-offer")
    assert offer["as"] == "guest"
    assert (
        "the guest the table brought" in out
    )  # the cellar's moment that waits on a sealed guest


def test_leaving_at_the_gms_call_hands_nothing_in(home):
    steps = [CELLAR, (">", "o"), ("Who?", "1"), ("bring in?", VELL), ("Which?", "2")]
    code, out, _ = table_turn(home, steps)
    assert code == 42 and "The story is waiting." in out
    assert not [r for r in rows(home) if r["kind"] == "table-offer"]


def test_enter_instead_of_something_goes_back_to_the_roll(home):
    _code, out, left = table_turn(home, [CELLAR, (">", "o"), ("Who?", "1"), ("bring in?", "")])  # fmt: skip
    assert not left and not [r for r in rows(home) if r["kind"] == "table-offer"]
    assert "(or press Enter) " + HINT in out


def test_what_is_brought_in_gets_the_heads_up_too(home):
    first = [CELLAR, (">", "o"), ("Who?", "1"), ("bring in?", VELL), ("Which?", "2"), ("(y/n)", "y")]  # fmt: skip
    table_turn(home, first, {">": "", "Is that true in your world? (y/n)": "y", "That's our night?": "y", "remember": ""})  # fmt: skip
    again = [("Which story?", "1"), (">", "o"), ("Who?", "2"), ("bring in?", "Old Vell never came down the stair."), ("Which?", "2"), ("Which?", "2")]  # fmt: skip
    _code, out, left = table_turn(home, again, now="2026-11-27T19:00:00Z")
    assert not left, out
    assert f"💡 Before you decide:\n   on 2026-11-20 your table made this true:\n   {VELL}" in out  # fmt: skip
    assert "It didn't happen. The old one stands." in out
    offer = [r for r in rows(home) if r["kind"] == "table-offer"][-1]
    assert answered(home, offer["subject"]) == ["decline", "table-heard"]


def test_a_fight_in_the_story_it_belongs_to_is_kept_and_checks(home):
    steps = [
        ("Which story?", "1"),
        (">", "f"),
        ("Which?", "3"),
    ]  # Aetheris; the raiders
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "o: someone brings something in · f: a fight · x: set it aside\n> " in out
    assert "⚔️  the party ambushed by 4 Scorched Belt Raiders" in out
    end = next(r for r in rows(home) if r["kind"] == "fight-end")["result"]
    said = {"party": "The party won", "foe": "The party fell"}[end["outcome"]]
    assert f"⚔️  {said} in {end['rounds']} rounds. Still standing: " in out
    assert "(What the fight means for the story is yours to say, GM.)\n  Enter: roll" in out  # fmt: skip
    held = subprocess.run([sys.executable, BOX / "fight.py", "--table", home / "table", "check"], capture_output=True, text=True, check=False)  # fmt: skip
    assert held.returncode == 0 and held.stdout.startswith("1 fight on the record")


def test_no_fight_where_it_doesnt_belong(home):
    _code, out, _left = table_turn(home, [("Which story?", ""), (">", "f")])
    assert "Press Enter to roll, o or x." in out and "fight-open" not in json.dumps(rows(home))  # fmt: skip


LAMP = (
    "The lantern catches first time",
    "It catches, but a pane cracks",
    "The hook gives",
)


def test_x_at_a_roll_sets_the_part_aside_and_the_gm_says_what_happens(home):
    steps = [
        ("Which story?", ""),
        (">", "x"),
        ("happens instead?", "The lantern was lit already."),
    ]
    _code, out, left = table_turn(home, steps)
    assert "Set aside. Nobody needs to say why." in out and "   (Set aside.)\n" in out
    assert "✋ GM, what happens instead? (say it aloud, then press Enter)" in out
    assert "   Said aloud.\n" in out and not any(t in out for t in LAMP)
    assert not left
    xs = [r for r in rows(home) if r["kind"] == "table-x"]
    assert len(xs) == 1 and xs[0]["who"] == "table" and xs[0]["at"] == 0
    assert not {"why", "reason", "for", "because", "name", "character", "by"} & set(xs[0])  # fmt: skip


def test_a_part_set_aside_in_a_story_that_keeps_no_gm_word_is_said_aloud_and_the_night_goes_on(home):  # fmt: skip
    (home / "table" / "pile" / "our-lines.md").write_text("## Lines\n- hook\n")
    steps = [("Which story?", ""), (">", ""), ("happens instead?", "It was lit already."), (">", "")]  # fmt: skip
    _code, out, left = table_turn(home, steps)
    assert "Something went wrong" not in out and "   Said aloud.\n" in out
    assert "Oro keeps the crowd from noticing." in out and not left  # played on
    assert not [r for r in rows(home) if r["kind"] == "table-offer"]  # nothing kept
