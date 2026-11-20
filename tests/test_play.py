"""box/play.py: the way in, played as a person would, by typing.

The test stands in for the person at the keyboard, as test_game_box stands
in for them with the kernel's seal: what it types is the GM's answer. What is
held here is that nothing is answered that wasn't typed, each call is
answered once, and the night ends only on the GM's yes. The table is laid in
a scratch folder, by play.py itself, with its own key."""

from __future__ import annotations

import collections
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

sys.path.insert(0, str(willow_pin.root()))
import kernel

NIGHT = "2026-11-20T19:00:00Z"


def play(home: Path, typed: str, now: str = NIGHT, *argv) -> subprocess.CompletedProcess:  # fmt: skip
    """play.py, TYPED a line a question in order (Enter at every roll, as a
    person throws the dice), walked away from when TYPED runs out."""
    env = {"DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": now}
    lines = typed.split("\n")[:-1] if typed.endswith("\n") else ([typed] if typed else [])  # fmt: skip
    return person.typed_run([BOX / "play.py", *argv], env, lines)


@pytest.fixture(scope="module")
def laid(tmp_path_factory) -> Path:
    """A table play.py laid itself, the first time, with nothing played."""
    home = tmp_path_factory.mktemp("home")
    got = play(home, "")
    assert got.returncode == 42 and (home / "table" / "record" / "kernel.json").exists(), got.stderr  # fmt: skip
    return home


@pytest.fixture
def home(laid, tmp_path) -> Path:
    return shutil.copytree(laid, tmp_path / "home")


def rows(home: Path) -> list[dict]:
    got, breaks = kernel.read(home / "table" / "record" / "record.jsonl")
    assert not breaks
    return got


def answers(home: Path) -> collections.Counter:
    return collections.Counter((r["kind"], r["subject"]) for r in rows(home) if r["kind"] in ("seal", "decline"))  # fmt: skip


def test_the_first_time_it_lays_the_box_by_itself_and_the_key_outside_it(laid):
    assert (laid / "gm.key").is_file()
    assert not any(p.name == "gm.key" for p in (laid / "table").rglob("*"))


def test_with_nothing_played_it_opens_on_a_story_to_try(home):
    got = play(home, "")
    assert got.stdout.startswith("Die-Namic\n\nLet's start a story.\n")
    assert "Try this one: The Lantern Fair. A night market in a made-up river town." in got.stdout  # fmt: skip
    assert "Previously on" not in got.stdout and "  w. Write your own" in got.stdout


def test_enter_plays_the_story_offered_and_walking_away_leaves_the_call_waiting(home):  # fmt: skip
    got = play(home, "\n")
    assert got.returncode == 42
    assert "The Lantern Fair\n" in got.stdout and "🎲 " in got.stdout
    assert "✋ Your call, GM." in got.stdout and "The call is waiting." in got.stdout
    assert not answers(home)  # nothing answered that wasn't typed


def test_a_whole_night_each_call_answered_once_and_ended_on_the_gms_yes(home):
    got = play(home, "\ny\ny\nBrann wants to bring a friend\ny\n")
    assert got.returncode == 0, got.stderr
    asked = [r["subject"] for r in rows(home) if r["kind"] == "table-ask"]
    ends = [r["subject"] for r in rows(home) if r["kind"] == "session"]
    assert len(asked) == 2 and len(ends) == 1
    assert answers(home) == collections.Counter({("seal", s): 1 for s in asked + ends})  # fmt: skip
    assert got.stdout.count("It's true now.") == 2
    assert "🌙 End of the night\nTonight, your table made true:\n  • " in got.stdout
    assert "Saved and checked: nothing can be changed after the fact.\n" in got.stdout
    assert "🌱 Your story grew. Write what happens next? (y/n)" in got.stdout
    assert got.stdout.rstrip().endswith("Good night.")  # not now: no one typed yes
    page = home / "table" / "pile" / "sessions" / "2026-11-20.md"
    assert page.read_text() == "# 2026-11-20\n\nBrann wants to bring a friend\n"
    assert subprocess.run([sys.executable, willow_pin.root() / "kernel.py", "verify", "--box", home / "table" / "record"], capture_output=True, check=False).returncode == 0  # fmt: skip


def test_no_is_a_decline_and_a_word_that_isnt_yes_or_no_is_asked_again(home):
    got = play(home, "\nmaybe\nn\n")
    assert "Type y for yes, or n for no." in got.stdout and "It didn't happen." in got.stdout  # fmt: skip
    assert [k for k, _ in answers(home)] == ["decline"]


def test_coming_back_asks_the_waiting_call_once_and_plays_on(home):
    play(home, "\n")  # away at the first call
    got = play(home, "1\ny\n", "2026-11-20T20:00:00Z")
    assert "Pick up where you left off" in got.stdout and "(last played 2026-11-20)" in got.stdout  # fmt: skip
    assert got.stdout.count("✋ Your call, GM.") == 2  # the waiting one, then the next
    assert list(answers(home).values()) == [1]


def test_not_yet_leaves_the_night_open_and_coming_back_ends_it_not_replays_it(home):  # fmt: skip
    got = play(home, "\ny\ny\n\nn\n")
    assert got.returncode == 42 and "The night stays open." in got.stdout
    assert not [r for r in rows(home) if r["kind"] == "session"]
    beats = sum(r["kind"] == "table-beat" for r in rows(home))
    again = play(home, "1\n\ny\n", "2026-11-20T21:00:00Z")
    assert "played to its end, and the night not ended yet." in again.stdout, again.stdout  # fmt: skip
    assert again.returncode == 0 and sum(r["kind"] == "table-beat" for r in rows(home)) == beats  # fmt: skip


def test_next_time_it_opens_on_previously_and_the_gms_own_note(home):
    play(home, "\ny\ny\nBrann wants to bring a friend\ny\n")
    got = play(home, "", "2026-11-27T19:00:00Z")
    aloud, rest = got.stdout.split("Just for you, GM (your notes from 2026-11-20):\n")
    assert "Previously on...\n\n(read this out loud)\n\nLast time:\n  - " in aloud
    assert rest.startswith("  Brann wants to bring a friend\n")
    assert "Pick up where you left off" in rest


def test_write_your_own_opens_the_writer(home):
    got = play(home, "w\n")
    assert "✏️  Let's write a story." in got.stdout and "Nothing was written." in got.stdout  # fmt: skip
    assert got.returncode == 42 and not answers(home)


def test_a_number_that_isnt_a_story_is_asked_again(home):
    got = play(home, "9\n")
    assert "Type a number from 1 to 5." in got.stdout


def test_it_takes_no_arguments(home):
    got = play(home, "", NIGHT, "--yes")
    assert got.returncode == 2 and got.stderr.strip() == "python box/play.py"
    assert not answers(home)  # there is no flag that answers for the GM


def test_a_record_that_doesnt_check_out_is_refused(home):
    path = home / "table" / "record" / "record.jsonl"
    lines = path.read_text().splitlines()
    first = json.loads(lines[0]) | {"ts": "1999-01-01T00:00:00Z"}
    path.write_text("\n".join([json.dumps(first), *lines[1:]]) + "\n")
    got = play(home, "\n")
    assert got.returncode == 2 and "Something went wrong: the record doesn't check out" in got.stderr  # fmt: skip
