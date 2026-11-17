"""die_namic.binder, Die-Namic's search seam: the core stands alone with any
ranker handed to it and imports nothing it isn't given; handed willow's
reading and ranker by the box, it asks the binder in the GM's own words, a
page named first, then what a word usually means, then the ranking."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import ClassVar

import pytest

GAME = Path(__file__).resolve().parents[1]
BOX = GAME / "box"
sys.path.insert(0, str(GAME))
from die_namic import Binder, Found  # noqa: E402


# ── the core alone: no willow, a ranker of the test's own ────────────────────
class Counting:
    """A ranker of the test's own: a passage scores the question's words it holds."""

    def __init__(self, pile):
        self.pile = pile

    def rank(self, question, top):
        ws = set(question.split())
        got = [(c, float(len(ws & set(c["text"].lower().split()))), []) for c in self.pile]
        return sorted([g for g in got if g[1]], key=lambda g: -g[1])[:top]


PILE = [
    {"path": "monsters/clockwork-hound.md", "line": 1, "text": "The hound bites. Hits 6."},
    {"path": "people/cogwen.md", "line": 1, "text": "Cogwen keeps the cellar and the hound."},
    {"path": "sessions/2026-11-07.md", "line": 3, "text": "Aldric asked for his goats back. The hound howled."},
]


def test_the_core_imports_nothing_it_is_not_handed():
    code = ("import sys; sys.path.insert(0, %r); import die_namic; "
            "print(sorted(m for m in ('kernel', 'pile_rank', 'willow_pin', 'socket', 'urllib', 'http', 'requests') if m in sys.modules))") % str(GAME)  # fmt: skip
    got = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
    assert got.returncode == 0 and got.stdout.strip() == "[]", got.stderr


def test_a_page_you_named_comes_first_then_what_your_word_means_then_the_rank():
    b = Binder(PILE, Counting, {"keeper": ["cogwen"]})
    got = b.ask("the keeper and the hound")
    assert [f.path for f in got] == ["monsters/clockwork-hound.md", "people/cogwen.md", "sessions/2026-11-07.md"]
    assert got[0].why == "you named its page"
    assert got[1].why == "what “keeper” usually means here"
    assert got[2].why.startswith("holds ") and "hound" in got[2].why
    assert got[0].where == "monsters/clockwork-hound.md:1" and isinstance(got[0], Found)


class Backwards(Counting):
    """A ranker that serves the pile last first, whatever the question: the
    order the tiers must overrule."""

    asked: ClassVar[list] = []

    def rank(self, question, top):
        Backwards.asked.append(top)
        got = [(c, 1.0, []) for c in reversed(self.pile) if set(question.split()) & set(c["text"].split())]
        return got[:top]


def test_the_tiers_overrule_the_ranking_named_then_meant_then_the_rest():
    pile = [
        {"path": "monsters/clockwork-hound.md", "line": 1, "text": "hound"},
        {"path": "people/cogwen.md", "line": 1, "text": "cogwen hound"},
        {"path": "sessions/one.md", "line": 1, "text": "hound"},
        {"path": "sessions/two.md", "line": 1, "text": "hound"},
    ]
    got = Binder(pile, Backwards, {"keeper": ["cogwen"]}).ask("keeper hound")
    assert [f.path for f in got] == [
        "monsters/clockwork-hound.md", "people/cogwen.md", "sessions/two.md", "sessions/one.md",
    ]  # fmt: skip


def test_a_three_letter_page_name_is_named_and_the_ranking_is_asked_for_twice_top():
    pile = [{"path": f"sessions/{i}.md", "line": 1, "text": "bob came by"} for i in range(9)]
    pile.append({"path": "people/bob.md", "line": 1, "text": "bob"})
    Backwards.asked.clear()
    got = Binder(pile, Backwards).ask("bob")
    assert got[0].path == "people/bob.md" and got[0].why == "you named its page"
    assert len(got) == 6 and Backwards.asked == [12]  # top is 6 unless asked, ranked from 2 x top
    assert len(Binder(pile, Backwards).ask("bob", top=3)) == 3 and Backwards.asked[-1] == 6


def test_a_passage_holding_many_of_your_words_names_the_first_four():
    pile = [{"path": "notes.md", "line": 1, "text": "ash birch cedar dogwood elm"}]
    got = Binder(pile, Counting).ask("ash birch cedar dogwood elm")
    assert got[0].why == "holds ash, birch, cedar, dogwood"


def test_a_page_name_with_a_dot_in_it_loses_only_its_extension():
    pile = [{"path": "notes.md", "line": 1, "text": "wasps nest here"},
            {"path": "monsters/v1.2-wasps.md", "line": 1, "text": "wasps sting"}]  # fmt: skip
    got = Binder(pile, Counting).ask("wasps")
    assert got[0].path == "monsters/v1.2-wasps.md" and got[0].why == "you named its page"


def test_words_said_together_are_also_one_word():
    pile = [{"path": "notes.md", "line": 1, "text": "the springwasps sting"}]
    got = Binder(pile, Counting).ask("spring wasps")  # held only as the two words run together
    assert [f.path for f in got] == ["notes.md"] and got[0].why == "holds springwasps"


def test_nothing_held_is_nothing_served_and_a_bare_question_asks_nothing():
    b = Binder(PILE, Counting)
    assert b.ask("pancakes") == [] and b.ask("  ?! ") == []


def test_a_passage_without_its_place_is_refused():
    with pytest.raises(ValueError, match="path, line and text"):
        Binder([{"text": "no place"}], Counting)


# ── handed willow by the box: the binder as the GM asks it ───────────────────
@pytest.fixture(scope="module")
def box_binder():
    sys.path.insert(0, str(BOX))
    import ask

    return ask, ask.binder(BOX / "binder", BOX / "gm-words.txt")


@pytest.mark.parametrize(
    "question, page, why",
    [
        ("what are the dog's stats", "monsters/clockwork-hound.md", "what “dog” usually means here"),
        ("who is the keeper", "people/cogwen.md", "what “keeper” usually means here"),
        ("what stops the wasps", "monsters/spring-wasps.md", "you named its page"),
        ("what does the prince want", "sessions/2026-11-07.md", "holds prince, aldric"),
    ],
)
def test_the_gms_questions_point_where_the_page_points(box_binder, question, page, why):
    _, b = box_binder
    first = b.ask(question)[0]
    assert (first.path, first.why) == (page, why)
    assert first.text in (BOX / "binder" / first.path).read_text()  # the binder's own words, never a summary


def test_within_a_tier_the_order_is_willows_ranking(box_binder):
    ask, b = box_binder
    import pile_rank

    question = "spring wasps sting weakness"
    raw = [(c["path"], c["line"]) for c, _, _ in pile_rank.Ranker(b.passages).rank(question, 12)]
    got = [(f.path, f.line) for f in b.ask(question, 12)]
    named = [g for g in got if g[0] == "monsters/spring-wasps.md"]
    rest = [g for g in got if g[0] != "monsters/spring-wasps.md"]
    assert got == named + rest
    assert named == [r for r in raw if r in named] and rest == [r for r in raw if r in rest]


def run(*argv):
    return subprocess.run([sys.executable, str(BOX / "ask.py"), *argv], capture_output=True, text=True)


def test_ask_says_where_to_look_or_that_nothing_holds_it_by_the_kernels_codes():
    got = run("what", "stops", "the", "wasps")
    assert got.returncode == 0 and got.stdout.startswith("monsters/spring-wasps.md:")
    assert run("pancakes").returncode == 42
    assert run().returncode == 2 and run("--top", "many", "hound").returncode == 2


def test_ask_with_no_question_prints_how_to_ask():
    got = run()
    assert got.returncode == 2 and "python box/ask.py [--table DIR] [--top N] QUESTION..." in got.stderr
