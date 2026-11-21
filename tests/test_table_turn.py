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
sys.path.insert(0, str(BOX))
import willow_pin

NOW = "2026-11-20T19:00:00Z"
VELL = "Old Vell from the lantern fair comes down the stair."
HINT = "  Enter: roll, or type the two dice you threw (like 4 6)\n  h: how · o: someone brings something in · s: sheets · u: undo a yes · x: set it aside\n> "


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
    assert (
        "  Press Enter to roll, type your two dice (like 4 6), or h, o, s, u or x.\n"
        in out
        and not left
    )
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
    assert (
        "o: someone brings something in · f: a fight · s: sheets · u: undo a yes · x: set it aside\n> "
        in out
    )
    assert "⚔️  the party ambushed by 4 Scorched Belt Raiders" in out
    end = next(r for r in rows(home) if r["kind"] == "fight-end")["result"]
    said = {"party": "The party won", "foe": "The party fell"}[end["outcome"]]
    assert f"⚔️  {said} in {end['rounds']} rounds. Still standing: " in out
    assert "(What the fight means for the story is yours to say, GM.)\n  Enter: roll" in out  # fmt: skip
    assert (
        "\n  The party\n    Sena Koll " in out and "\n  Their side\n" in out
    )  # the board, after
    assert out.index("  Their side") < out.index(f"⚔️  {said} in")
    held = subprocess.run([sys.executable, BOX / "fight.py", "--table", home / "table", "check"], capture_output=True, text=True, check=False)  # fmt: skip
    assert held.returncode == 0 and held.stdout.startswith("1 fight on the record")


def test_no_fight_where_it_doesnt_belong(home):
    _code, out, _left = table_turn(home, [("Which story?", ""), (">", "f")])
    assert "Press Enter to roll, type your two dice (like 4 6), or h, o, s, u or x." in out and "fight-open" not in json.dumps(rows(home))  # fmt: skip


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


def test_s_at_a_roll_shows_each_seated_characters_sheet_and_what_they_brought_in(home):
    steps = [("Which story?", ""), (">", "o"), ("Who?", "1"), ("bring in?", "Tamsin has a ladder"), ("(y/n)", "y"), (">", "s"), ("Write on a sheet?", ""), (">", "")]  # fmt: skip
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "   📜 Tamsin, lamp-lighter\n      Good at: Grit +2, Heart +1\n      · Tamsin has a ladder\n" in out  # fmt: skip
    assert "   📜 Oro, juggler\n      Good at: Wit +2\n" in out
    assert (
        "Old Vell" not in out.split("📜 Tamsin")[1].split("> ")[0]
    )  # not seated: no sheet


LADDER = [("Which story?", ""), (">", "o"), ("Who?", "1"), ("bring in?", "Tamsin has a ladder"), ("(y/n)", "y")]  # fmt: skip


def test_u_takes_back_a_yes_pressed_by_mistake_and_erases_nothing(home):
    steps = [
        *LADDER,
        (">", "u"),
        ("Take back", "y"),
        (">", "s"),
        ("Write on a sheet?", ""),
        (">", ""),
    ]
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert '   Take back "Tamsin has a ladder"? It stays on the record as a slip, and no longer stands. (y/n) ' in out  # fmt: skip
    assert "   Taken back. It no longer stands.\n" in out
    assert "· Tamsin has a ladder" not in out.split("Taken back.")[1]  # off the sheet
    offer = next(r for r in rows(home) if r["kind"] == "table-offer" and r["fact"] == "Tamsin has a ladder")  # fmt: skip
    kinds = [r["kind"] for r in rows(home) if r.get("subject") == offer["subject"] and r["kind"] in ("seal", "decline")]  # fmt: skip
    assert kinds == ["seal"]  # the yes is never undone; it is stood over
    back = [r for r in rows(home) if r["kind"] == "table-replaces" and r["old"] == offer["subject"]]  # fmt: skip
    assert (
        len(back) == 1 and back[0]["fact"] == "nothing: that yes was pressed by mistake"
    )
    canon = subprocess.run([sys.executable, BOX / "session.py", "--table", home / "table", "recap"], capture_output=True, text=True, check=False).stdout  # fmt: skip
    assert (
        "Tamsin has a ladder" not in canon.split("## For the GM's eyes")[0]
    )  # not read aloud


def test_u_with_nothing_made_true_tonight_says_so(home):
    _code, out, left = table_turn(home, [("Which story?", ""), (">", "u"), (">", "")])
    assert "   Nothing has been made true tonight to take back.\n" in out and not left
    assert not [r for r in rows(home) if r["kind"] == "table-replaces"]


def test_no_at_take_back_leaves_it_standing(home):
    steps = [
        *LADDER,
        (">", "u"),
        ("Take back", "n"),
        (">", "s"),
        ("Write on a sheet?", ""),
        (">", ""),
    ]
    _code, out, left = table_turn(home, steps)
    assert not left and "· Tamsin has a ladder" in out.split("Take back")[1]
    assert not [r for r in rows(home) if r["kind"] == "table-replaces"]


def sheet_lines(*lines: str) -> list:
    return [
        (">", "s"),
        *[("Write on a sheet?", x) for x in lines],
        ("Write on a sheet?", ""),
    ]


def test_what_a_character_finds_and_uses_and_how_they_are_hurt_is_on_their_sheet(home):
    steps = [("Which story?", ""), *sheet_lines("Tamsin finds a rope", "Oro is hurt by a club", "Tamsin picks up two lanterns", "Mira finds a key", "Tamsin uses the ropes"), (">", "s"), ("Write on a sheet?", ""), (">", "")]  # fmt: skip
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert out.count("   On Tamsin's sheet.\n") == 3 and "   On Oro's sheet.\n" in out
    assert "   Start with a name (Tamsin, Oro), then finds, uses, is hurt or is healed.\n" in out  # Mira isn't seated  # fmt: skip
    last = out.split("📜 Tamsin")[-1]
    assert "      Carrying: two lanterns\n" in last and "rope" not in last.split("📜 Oro")[0]  # used up  # fmt: skip
    assert "   📜 Oro, juggler\n      Good at: Wit +2\n      Hurt: by a club\n" in out
    kept = [r for r in rows(home) if r["kind"] == "table-carry"]
    assert [(r["char"], r["change"], r["what"]) for r in kept] == [("Tamsin", "carry", "a rope"), ("Oro", "hurt", "by a club"), ("Tamsin", "carry", "two lanterns"), ("Tamsin", "spend", "the ropes")]  # fmt: skip


def test_what_carries_over_is_said_on_the_opening_screen_until_healed(home):
    table_turn(
        home, [("Which story?", ""), *sheet_lines("Oro is hurt", "Tamsin finds a rope")]
    )
    _code, out, _left = table_turn(home, [])
    assert "Carried over (read this out loud too):\n  - Oro is still hurt\n  - Tamsin carries a rope\n" in out  # fmt: skip
    healed = [("Which story?", "1"), ("(y/n)", "y"), *sheet_lines("Oro is healed")]
    table_turn(home, healed)  # picked up: the call it waited on, then the next roll
    _code, out, _left = table_turn(home, [])
    assert "  - Tamsin carries a rope\n" in out and "Oro is still hurt" not in out


def test_h_lets_the_player_choose_how_with_each_ways_chances(home):
    steps = [("Which story?", ""), (">", "h"), ("How?", "3"), (">", "")]
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "   How does Tamsin meet it?\n   1. Grit +2 (strong 42%, weak 42%, miss 17%) — the story's\n" in out  # fmt: skip
    assert "   3. Heart +1 (strong 28%, weak 44%, miss 28%)\n" in out
    assert "   Tamsin meets it with Heart.\n" in out and "🎲 Tamsin tries Heart: rolled " in out  # fmt: skip
    beat = next(r for r in rows(home) if r["kind"] == "table-beat")
    assert (beat["stat"], beat["bonus"]) == ("Heart", 1)
    held = subprocess.run([sys.executable, willow_pin.root() / "adapters" / "stdlib" / "game-master" / "game_master.py", "--box", home / "table" / "record", "check", "--world", home / "table" / "worlds" / "lantern-fair.json"], capture_output=True, text=True, check=False)  # fmt: skip
    assert held.returncode == 0, (
        held.stdout + held.stderr
    )  # the story's own check takes any of its stats


def test_enter_at_how_keeps_the_storys_way(home):
    _code, out, _left = table_turn(home, [("Which story?", ""), (">", "h"), ("How?", ""), (">", "")])  # fmt: skip
    assert "   Tamsin meets it with Grit.\n" in out and "🎲 Tamsin tries Grit:" in out


def checks(home: Path) -> list[subprocess.CompletedProcess]:
    adds = willow_pin.root() / "adapters" / "stdlib"
    box = home / "table" / "record"
    out = []
    for a in ("game-master/game_master.py", "play-dice/play_dice.py", "dice-tower/dice_tower.py"):  # fmt: skip
        out.append(subprocess.run([sys.executable, adds / a, "--box", box, "check"], capture_output=True, text=True, check=False))  # fmt: skip
    return out


def test_the_dice_are_in_the_tower_before_anything_is_written_and_come_out_on_the_roll(home):  # fmt: skip
    steps = [*LADDER, (">", "")]  # the moment posed, something brought in, then Enter
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "Tamsin climbs to the dark stall's hook.\n🥤 The dice are in the tower. Nobody knows them yet, not even the GM.\n" in out  # fmt: skip
    kinds = [r["kind"] for r in rows(home)]
    drop, offer, out_ = kinds.index("tower-drop"), kinds.index("table-offer"), kinds.index("tower-out")  # fmt: skip
    assert (
        drop < offer < out_ and kinds[out_ + 1] == "table-beat"
    )  # dropped first, out on the roll
    beat = rows(home)[out_ + 1]
    assert (
        beat["roll_row"] == rows(home)[out_]["n"] and "roll" not in kinds
    )  # no seeded roll at all
    die = next((home / "table" / "tower").iterdir())
    assert die.stat().st_mode & 0o777 == 0o600 and not str(die).startswith(str(home / "table" / "record"))  # fmt: skip
    assert all(c.returncode == 0 for c in checks(home)), [
        c.stderr for c in checks(home)
    ]


def test_dice_thrown_at_the_table_are_typed_in_and_kept_as_said(home):
    steps = [("Which story?", ""), (">", "4 5"), (">", "6,6"), ("(y/n)", "y")]
    _code, out, left = table_turn(home, steps)
    assert not left, out
    assert "🎲 Tamsin tries Grit: rolled 4 + 5 (your dice), +2 Grit = 11. Great!\n" in out  # fmt: skip
    assert "🎲 Oro tries Wit: rolled 6 + 6 (your dice), +2 Wit = 14. Great!\n" in out
    said = [r for r in rows(home) if r["kind"] == "roll"]
    assert [(r["generator"], r["faces"]) for r in said] == [("said", [[4, 5]]), ("said", [[6, 6]])]  # fmt: skip
    beats = [r for r in rows(home) if r["kind"] == "table-beat" and r["beat_kind"] == "action"]  # fmt: skip
    assert [b["roll_row"] for b in beats[:2]] == [r["n"] for r in said]
    held = checks(home)
    assert all(c.returncode == 0 for c in held), [c.stderr for c in held]
    assert "2 of them said, kept as said." in held[1].stdout
    assert "still inside" not in held[2].stdout  # the tower's unused dice came out


def test_a_die_that_isnt_one_is_asked_again_and_enter_still_rolls(home):
    steps = [("Which story?", ""), (">", "7 2"), (">", "")]
    _code, out, left = table_turn(home, steps)
    assert not left and "  A die shows 1 to 6: type the two dice, like 4 6.\n" in out
    assert "(your dice)" not in out and any(r["kind"] == "tower-out" for r in rows(home))  # fmt: skip


def test_a_moment_asked_for_its_dice_again_finds_them_still_in_the_tower(home, capsys):  # fmt: skip
    import play

    game = {"open": {"n": 1}, "beats": []}
    first = play.in_tower(home / "table", game, NOW)
    again = play.in_tower(home / "table", game, NOW)  # a night picked up again
    assert first == again and capsys.readouterr().out.count("🥤") == 1
    drops = [r for r in rows(home) if r["kind"] == "tower-drop"]
    assert len(drops) == 1 and drops[0]["for"] == "moment 1"
    nxt = play.in_tower(home / "table", {**game, "beats": [{}]}, NOW)
    assert (
        nxt != first and len([r for r in rows(home) if r["kind"] == "tower-drop"]) == 2
    )
