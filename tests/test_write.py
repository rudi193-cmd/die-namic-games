"""box/write.py: a story written by answering questions, as a person would.

The test types the writer's answers. What is held here: the story file is
the one author.py reads (every door writes the same file), nobody types an
id, a blank outcome is the GM's on the night, leaving early writes nothing,
and nothing already in the box is written over."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BOX = Path(__file__).resolve().parents[1] / "box"
NOW = "2026-11-20T19:00:00Z"

EGG = [
    "a kid who finds a dragon egg in the school garden",  # what it's about
    "The Garden Egg",
    "the school garden",
    "Mira, a kid who likes bugs", "y",
    "The Groundskeeper, who sees everything", "n",
    "",  # that's everyone
    "",  # Brave, Clever, Kind
    "1", "She picks up the egg.", "3",
    "It's warm, and something inside taps back.", "", "The groundskeeper sees her.",
    "2", "Is the egg a real dragon?", "The egg is a real dragon's.",
    "3",  # that's the story
]  # fmt: skip


def run(script: str, home: Path, typed: list[str], *argv) -> subprocess.CompletedProcess:  # fmt: skip
    env = {**os.environ, "DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": NOW}
    text = "".join(f"{t}\n" for t in typed)
    return subprocess.run([sys.executable, BOX / script, *argv], input=text, capture_output=True, text=True, env=env, check=False)  # fmt: skip


@pytest.fixture(scope="module")
def laid(tmp_path_factory) -> Path:
    home = tmp_path_factory.mktemp("home")
    assert run("play.py", home, []).returncode == 42
    return home


@pytest.fixture
def home(laid, tmp_path) -> Path:
    return shutil.copytree(laid, tmp_path / "home")


def table(home: Path) -> Path:
    return home / "table"


def test_a_story_written_from_play_is_the_file_author_reads_and_plays(home):
    got = run("play.py", home, ["w", *EGG, "y", "y", "", "y"])
    assert got.returncode == 0, got.stderr
    assert "🌱 The Garden Egg is written: 2 moments." in got.stdout
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert "- mira: Mira | a kid who likes bugs | seated\n" in story
    assert "- the-groundskeeper: The Groundskeeper | who sees everything\n" in story  # the GM's to play  # fmt: skip
    assert "stats: Brave, Clever, Kind\n" in story and "setting: A kid who finds a dragon egg in the school garden.\n" in story  # fmt: skip
    assert "- weak: (GM: you say what happens.)\n" in story  # left blank: the GM's on the night  # fmt: skip
    assert "proposed by: the-groundskeeper\nfact: The egg is a real dragon's." in story  # fmt: skip
    made = json.loads((table(home) / "worlds" / "the-garden-egg.json").read_text())
    again = subprocess.run([sys.executable, BOX / "author.py", table(home) / "stories" / "the-garden-egg.md"], capture_output=True, text=True, check=False)  # fmt: skip
    assert (
        again.returncode == 0 and json.loads(again.stdout) == made
    )  # one file, every door
    assert "She picks up the egg.\n🎲 Mira tries Kind: rolled " in got.stdout
    assert "✋ Your call, GM. Is the egg a real dragon?\n   The Groundskeeper says:\n   The egg is a real dragon's." in got.stdout  # fmt: skip
    assert got.stdout.rstrip().endswith("Good night.")


def test_not_now_keeps_it_in_the_stories_for_later(home):
    got = run("write.py", home, [*EGG, "n"])
    assert got.returncode == 0 and "It's in your stories, ready when you are." in got.stdout  # fmt: skip
    listed = run("play.py", home, [])
    assert "The Garden Egg" in listed.stdout


def test_leaving_before_the_end_writes_nothing(home):
    before = sorted(p.name for p in (table(home) / "worlds").iterdir())
    got = run("write.py", home, EGG[:6])
    assert got.returncode == 42 and "Nothing was written." in got.stdout
    assert sorted(p.name for p in (table(home) / "worlds").iterdir()) == before
    assert not (table(home) / "stories" / "the-garden-egg.md").exists()


def test_the_boxes_that_need_an_answer_ask_again(home):
    typed = [EGG[0], "", EGG[1], "", EGG[2], *EGG[3:], "n"]
    got = run("write.py", home, typed)
    assert "A story needs a name." in got.stdout and "Somewhere for it to happen" in got.stdout  # fmt: skip
    assert got.returncode == 0


def test_someone_at_the_table_has_to_play_someone(home):
    typed = [*EGG[:3], "The Groundskeeper", "n", "", "Mira", "y", "", *EGG[8:], "n"]
    got = run("write.py", home, typed)
    assert "Someone at the table needs to play someone." in got.stdout
    assert got.returncode == 0


def test_two_people_with_one_name_are_asked_apart(home):
    typed = [*EGG[:5], "mira, again", "Mira Two", "y", *EGG[5:10], "1", *EGG[10:], "n"]  # fmt: skip
    got = run("write.py", home, typed)
    assert "There's already a mira in it; give this one another name." in got.stdout
    assert "Who tries it?" in got.stdout  # two at the table: asked whose moment it is
    assert "- mira-two: Mira Two |" in (table(home) / "stories" / "the-garden-egg.md").read_text()  # fmt: skip


def test_their_own_strengths_and_nothing_typed_breaks_the_file(home):
    typed = list(EGG)
    typed[8] = "fast, quiet"
    typed[11] = "2"  # Quiet
    typed[3] = "Mira | the bold, a kid"
    typed[12] = "- strong: it hums"
    got = run("write.py", home, [*typed, "n"])
    assert got.returncode == 0, got.stderr
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert "stats: Fast, Quiet\n" in story and "suggests: Quiet\n" in story
    assert "- mira-the-bold: Mira / the bold | a kid | seated" in story
    assert "- strong: strong: it hums\n" in story


def test_the_same_title_twice_is_a_new_story_never_written_over(home):
    run("write.py", home, [*EGG, "n"])
    first = (table(home) / "stories" / "the-garden-egg.md").read_text()
    run("write.py", home, [*EGG, "n"])
    assert (table(home) / "stories" / "the-garden-egg.md").read_text() == first
    assert (table(home) / "worlds" / "the-garden-egg-2.json").is_file()


def test_stuck_deals_ideas_from_the_box_and_one_can_be_taken(home):
    got = run("write.py", home, ["", "1", *EGG[1:], "n"])
    assert "Stuck? Try one of these, or write your own:\n  1. " in got.stdout
    idea = got.stdout.split("Stuck? Try one of these, or write your own:\n  1. ")[1].split("\n")[0]  # fmt: skip
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert f"setting: {idea[:1].upper() + idea[1:]}" in story


def test_the_story_needs_a_moment_before_it_can_end(home):
    typed = [*EGG[:9], "3", *EGG[9:], "n"]
    got = run("write.py", home, typed)
    assert "Type a number from 1 to 2." in got.stdout and got.returncode == 0


def test_it_takes_no_arguments(home):
    got = run("write.py", home, [], "story.md")
    assert got.returncode == 2 and got.stderr.strip() == "python box/write.py"
