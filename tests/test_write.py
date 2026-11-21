"""box/write.py: a story written by answering questions, as a person would.

The test types the writer's answers. What is held here: the story file is
the one author.py reads (every door writes the same file), nobody types an
id, a blank outcome is the GM's on the night, leaving early writes nothing,
and nothing already in the box is written over."""

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


FILLED = [
    *EGG[:13],
    "It cracks a little.",
    *EGG[14:],
]  # no blank: the GM is never asked


def run(script: str, home: Path, typed: list[str], *argv) -> subprocess.CompletedProcess:  # fmt: skip
    """SCRIPT, TYPED a line a question in order, Enter at every roll."""
    return person.typed_run([BOX / script, *argv], {"DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": NOW}, typed)  # fmt: skip


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
    got = run("play.py", home, ["w", *FILLED, "y", "y", "", "y"])
    assert got.returncode == 0, got.stderr
    assert "🌱 The Garden Egg is written: 2 moments." in got.stdout
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert "- mira: Mira | a kid who likes bugs | seated\n" in story
    assert "- the-groundskeeper: The Groundskeeper | who sees everything\n" in story  # the GM's to play  # fmt: skip
    assert "stats: Brave, Clever, Kind\n" in story and "setting: A kid who finds a dragon egg in the school garden.\n" in story  # fmt: skip
    assert "- weak: It cracks a little.\n" in story and "offers:" not in story  # nothing blank  # fmt: skip
    assert "proposed by: the-groundskeeper\nfact: The egg is a real dragon's." in story  # fmt: skip
    made = json.loads((table(home) / "worlds" / "the-garden-egg.json").read_text())
    again = subprocess.run([sys.executable, BOX / "author.py", table(home) / "stories" / "the-garden-egg.md"], capture_output=True, text=True, check=False)  # fmt: skip
    assert (
        again.returncode == 0 and json.loads(again.stdout) == made
    )  # one file, every door
    assert (
        "She picks up the egg.\n  Enter: roll · o: someone brings something in · s: sheets · x: set it aside\n> 🎲 Mira tries Kind: rolled "
        in got.stdout
    )
    assert "✋ Your call, GM. Is the egg a real dragon?\n   The Groundskeeper says:\n   The egg is a real dragon's." in got.stdout  # fmt: skip
    assert got.stdout.rstrip().endswith("Good night.")


def test_not_now_keeps_it_in_the_stories_for_later(home):
    got = run("write.py", home, [*EGG, "n"])
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert (
        "- weak: (GM: you say what happens.)\n" in story
    )  # left blank: the GM's on the night
    assert "offers: gm-word\n" in story
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


NEXT = [
    "",
    "",
    "",  # its name, the same place, what it's about
    "Pip, a baby dragon",
    "n",
    "",  # someone new, then that's everyone
    "1",
    "Mira feeds the hatchling.",
    "3",
    "Pip purrs like a kettle.",
    "",
    "Pip sneezes fire.",
    "2",  # only if yes
    "1",
    "Mira hides the egg.",
    "2",
    "He walks right past.",
    "He stops.",
    "",
    "1",  # always
    "3",  # that's the story
]
FULL_NEXT = [
    *NEXT[:10],
    "Pip hiccups.",
    *NEXT[11:18],
    "He sees her.",
    *NEXT[19:],
]  # no blank


def night_then_next(home: Path, answer: str, then: list[str]) -> subprocess.CompletedProcess:  # fmt: skip
    """The egg written and played, the GM's ANSWER to its call, the night
    ended, and what happens next written by THEN."""
    return run("play.py", home, ["w", *FILLED, "y", answer, "", "y", "y", *then])


def test_a_night_whose_calls_were_answered_offers_what_happens_next(home):
    got = night_then_next(home, "y", [*FULL_NEXT, "y", "", "y"])
    assert got.returncode == 0, got.stderr
    assert "🌱 Your story grew. Write what happens next? (y/n)" in got.stdout
    assert "Last time, your table made true:\n  • The egg is a real dragon's." in got.stdout  # fmt: skip
    assert "Everyone from last time is here: Mira, The Groundskeeper." in got.stdout
    story = (
        table(home) / "stories" / "the-garden-egg-what-happens-next.md"
    ).read_text()
    assert "# The Garden Egg: What Happens Next\n" in story
    assert "- mira: Mira | a kid who likes bugs | seated\n" in story  # the same ids, carried  # fmt: skip
    assert "- pip: Pip | a baby dragon\n" in story
    assert "- the-school-garden: The school garden\n" in story
    assert "when: sealed the-garden-egg::start::m2 is sealed\n" in story
    assert story.count("when:") == 1
    nxt = got.stdout.split("is written: 2 moments.\nPlay it now?")[-1]
    assert (
        "Mira feeds the hatchling.\n  Enter: roll · o: someone brings something in · s: sheets · x: set it aside\n> 🎲 Mira tries Kind"
        in nxt
    )  # the table said yes
    assert (
        "Mira hides the egg.\n  Enter: roll · o: someone brings something in · s: sheets · x: set it aside\n> 🎲 Mira tries Clever"
        in nxt
    )


def test_a_moment_that_waits_on_a_yes_isnt_played_after_a_no(home):
    got = night_then_next(home, "n", [*FULL_NEXT, "y", "", "y"])
    assert "And said no to:\n  • The egg is a real dragon's." in got.stdout
    nxt = got.stdout.split("is written: 2 moments.\nPlay it now?")[-1]
    assert (
        "Mira feeds the hatchling." not in nxt
        and "Mira hides the egg.\n  Enter: roll · o: someone brings something in · s: sheets · x: set it aside\n> 🎲"
        in nxt
    )


def test_every_moment_waiting_on_last_time_is_asked_for_one_that_doesnt(home):
    waits = list(NEXT)
    waits[19] = "3"  # the second moment: only if no
    got = night_then_next(home, "y", [*waits, "1", "Mira waves.", "1", "Hi.", "Hm.", "Oh.", "1", "3", "n"])  # fmt: skip
    assert "Every moment waits on last time; add one that happens whatever was decided." in got.stdout  # fmt: skip
    assert got.returncode == 0, got.stderr


def test_write_offers_what_happens_next_in_a_story_that_has_answered_calls(home):
    night_then_next(home, "y", [])  # left at the offer's first question
    got = run("write.py", home, ["2", *NEXT, "n"])
    assert "What would you like to write?\n  1. A new story\n  2. What happens next in The Garden Egg\n" in got.stdout  # fmt: skip
    assert got.returncode == 0 and (table(home) / "worlds" / "the-garden-egg-what-happens-next.json").is_file()  # fmt: skip


def test_a_night_with_no_answered_call_ends_without_the_offer(home):
    got = run("play.py", home, ["w", *EGG[:9], "1", "She picks up the egg.", "3", "a", "b", "c", "3", "y", "", "y"])  # fmt: skip
    assert got.returncode == 0, got.stderr
    assert "Your story grew" not in got.stdout and got.stdout.rstrip().endswith("Good night.")  # fmt: skip


BLANKS = [
    *EGG[:9],
    "1",
    "She picks up the egg.",
    "3",
    "",
    "",
    "",
    "3",
]  # every outcome the GM's


def test_a_blank_moment_asks_the_gm_and_keeps_their_word_as_the_rule(home):
    got = run("play.py", home, ["w", *BLANKS, "y", "The egg hums, and Mira hums back.", "y", "", "y"])  # fmt: skip
    assert got.returncode == 0, got.stderr
    story = (table(home) / "stories" / "the-garden-egg.md").read_text()
    assert "offers: gm-word\n" in story
    assert "🎲 Mira tries Kind: rolled " in got.stdout and "(GM: you say what happens.)" not in got.stdout  # fmt: skip
    assert "✋ GM, what happens?" in got.stdout and "It's the rule of the table now." in got.stdout  # fmt: skip
    assert "Tonight, your table made true:\n  • The egg hums, and Mira hums back." in got.stdout  # fmt: skip
    rows = [json.loads(line) for line in (table(home) / "record" / "record.jsonl").read_text().splitlines()]  # fmt: skip
    offer = [r for r in rows if r["kind"] == "table-offer"]
    assert len(offer) == 1 and offer[0]["as"] == "gm-word" and offer[0]["by"] == "mira"
    assert offer[0]["fact"] == "The egg hums, and Mira hums back."
    assert [r["kind"] for r in rows if r.get("subject") == offer[0]["subject"]] == ["proposal", "table-offer", "seal", "table-heard"]  # fmt: skip
    later = run("play.py", home, [])
    aloud = later.stdout.split("Pick up where")[0]
    assert "  - The egg hums, and Mira hums back.\n" in aloud and "brought by" not in aloud  # the GM's word, no one's offer  # fmt: skip


def test_enter_at_the_gms_moment_keeps_nothing_and_no_asks_again(home):
    got = run("play.py", home, ["w", *BLANKS, "y", "Something odd.", "n", "", "", "y"])
    assert "Said aloud, not kept." in got.stdout and got.stdout.count("✋ GM, what happens?") == 2  # fmt: skip
    assert "Tonight, your table played it through." in got.stdout
    rows = (table(home) / "record" / "record.jsonl").read_text()
    assert '"kind":"table-offer"' not in rows.replace(" ", "")


def test_leaving_at_the_gms_moment_asks_it_first_when_coming_back(home):
    got = run("play.py", home, ["w", *BLANKS, "y"])
    assert got.returncode == 42 and "The GM's moment is waiting." in got.stdout
    again = run("play.py", home, ["1", "The egg hums.", "y", "", "y"])
    assert (
        "She picks up the egg.\n🎲 Mira tries Kind" in again.stdout
    )  # picked up: rolled already
    assert "It's the rule of the table now." in again.stdout and again.returncode == 0, again.stdout  # fmt: skip
    gone = run("play.py", home, ["1"])  # the night is ended: nothing waits
    assert "✋ GM, what happens?" not in gone.stdout.split("Which story?")[-1].split("The Garden Egg")[0]  # fmt: skip


def test_stuck_offers_the_first_three_different_seeds_ideas_deals_and_only_those(home):
    """The ideas are ideas.py's own Seeds, as it deals them today: the first
    three that differ, in its order, and nothing from its other sections."""
    dealt = subprocess.run([sys.executable, BOX / "ideas.py", "--table", table(home)], capture_output=True, text=True, check=False).stdout  # fmt: skip
    seeds = [line.strip()[2:] for line in dealt.split("## Seeds")[1].split("\n## ")[0].splitlines() if line.strip().startswith("- ")]  # fmt: skip
    first = list(dict.fromkeys(seeds))[:3]
    assert len(first) == 3
    got = run("write.py", home, [""])
    offered = got.stdout.split("Stuck? Try one of these, or write your own:\n")[1].split("Which one?")[0]  # fmt: skip
    assert offered == "".join(f"  {i}. {s}\n" for i, s in enumerate(first, 1)) + "  4. My own idea\n"  # fmt: skip


def test_an_idea_dealt_twice_is_offered_once(monkeypatch, tmp_path):
    sys.path.insert(0, str(BOX))
    import write

    dealt = "# Ideas\n\n## Seeds (seed 'x')\n\n  - a door\n  - a door\n  - an egg\n  - a fair\n  - a ship\n\n## Set up, never played\n\n  - not this\n"  # fmt: skip
    monkeypatch.setattr(write.play, "run", lambda *a: subprocess.CompletedProcess(a, 0, dealt, ""))  # fmt: skip
    assert write.ideas(tmp_path) == ["a door", "an egg", "a fair"]
