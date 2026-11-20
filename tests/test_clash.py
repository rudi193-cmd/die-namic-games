"""The heads-up: before the GM decides, what the table already holds true
about the same thing (box/clash.py, in box/play.py).

Played as a person would, by typing. Night one makes "The egg is a real
dragon's." true; the next part asks a call, or the GM's own word, about the
same thing. What is held: the heads-up comes before any answer, only the GM's
choice decides, "mine stands now" replaces the old truth under the GM's seal
and never erases it, and nothing about a different thing, or the same words
again, raises it."""

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
OLD = "The egg is a real dragon's."

EGG = [
    "a kid who finds a dragon egg", "The Garden Egg", "the school garden",
    "Mira, a kid who likes bugs", "y", "The Groundskeeper, who sees everything", "n", "", "",
    "1", "She picks up the egg.", "3", "It's warm.", "It cracks.", "He sees her.",
    "2", "Is the egg a real dragon?", OLD,
    "3",
]  # fmt: skip


def run(home: Path, typed: list[str], now: str = NOW) -> subprocess.CompletedProcess:
    return person.typed_run([BOX / "play.py"], {"DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": now}, typed)  # fmt: skip


def asking(fact: str) -> list[str]:
    """The next part: one call, always, that the GM is asked."""
    return ["", "", "", "", "2", "Is it, though?", fact, "1", "3"]


def saying() -> list[str]:
    """The next part: one moment, always, every outcome the GM's."""
    return ["", "", "", "", "1", "Mira shows the egg around.", "2", "", "", "", "1", "3"]  # fmt: skip


@pytest.fixture(scope="module")
def egg(tmp_path_factory) -> Path:
    """A table whose first night made OLD true, and ended."""
    home = tmp_path_factory.mktemp("home")
    got = run(home, ["w", *EGG, "y", "y", "", "y"])
    assert got.returncode == 0 and "It's true now." in got.stdout, got.stdout
    return home


@pytest.fixture
def home(egg, tmp_path) -> Path:
    return shutil.copytree(egg, tmp_path / "home")


def rows(home: Path) -> list[dict]:
    return [json.loads(line) for line in (home / "table" / "record" / "record.jsonl").read_text().splitlines()]  # fmt: skip


def next_part(home: Path, part: list[str], then: list[str]) -> subprocess.CompletedProcess:  # fmt: skip
    """What happens next, written from write.py and played; THEN answers it."""
    env = {"DIE_NAMIC_HOME": str(home), "DIE_NAMIC_NOW": "2026-11-27T19:00:00Z"}
    return person.typed_run([BOX / "write.py"], env, ["2", *part, "y", *then])


def canon(home: Path) -> str:
    return subprocess.run([sys.executable, BOX / "session.py", "--table", home / "table", "canon"], capture_output=True, text=True, check=False).stdout  # fmt: skip


def heads_up(out: str) -> str:
    return out.split("💡 Before you decide:\n")[1].split("   Which? ")[0]


NEW = "The egg was never a real dragon's; it's a painted stone."


def test_a_call_about_the_same_thing_gets_the_heads_up_before_any_answer(home):
    got = next_part(home, asking(NEW), [""])  # left at the heads-up
    shown = heads_up(got.stdout)
    assert shown == f"   on 2026-11-20 your table made this true:\n   {OLD}\n   1. Mine stands now\n   2. Keep the old one\n   3. Both are true\n"  # fmt: skip
    assert "Is that true in your world?" not in got.stdout.split("💡")[1]
    ask = [r for r in rows(home) if r["kind"] == "table-ask" and r["fact"] == NEW]
    assert ask and not [r for r in rows(home) if r.get("subject") == ask[0]["subject"] and r["kind"] in ("seal", "decline")]  # nothing answered  # fmt: skip


def test_mine_stands_now_replaces_the_old_under_the_gms_seal_and_erases_nothing(home):
    got = next_part(home, asking(NEW), ["1", "", "y"])
    assert "It's true now, and the old one is replaced." in got.stdout, got.stdout
    kept = [r for r in rows(home) if r["kind"] == "table-replaces"]
    assert len(kept) == 1 and kept[0]["fact"] == NEW
    assert [r["kind"] for r in rows(home) if r.get("subject") == kept[0]["subject"]] == ["proposal", "table-replaces", "seal"]  # fmt: skip
    old = next(r for r in rows(home) if r["kind"] == "table-ask" and r["fact"] == OLD)
    assert [r["kind"] for r in rows(home) if r.get("subject") == old["subject"] and r["kind"] in ("seal", "decline")] == ["seal"]  # never undone  # fmt: skip
    said = canon(home)
    assert f"what this table holds true:\n  {NEW}" in said and f"what it replaced:\n  was: {OLD}" in said  # fmt: skip
    later = run(home, [], "2026-12-04T19:00:00Z").stdout
    aloud = later.split("(read this out loud)")[1].split("Just for you")[0]
    assert NEW in aloud and OLD not in aloud
    assert f"Just for you, GM, what your table replaced:\n  - {OLD} (replaced on 2026-11-27 by: {NEW})" in later  # fmt: skip


def test_keep_the_old_one_declines_the_new_and_the_old_stands(home):
    got = next_part(home, asking(NEW), ["2", "", "y"])
    assert "It didn't happen. The old one stands." in got.stdout
    said = canon(home)
    assert f"what this table holds true:\n  {OLD}" in said and f"not: {NEW}" in said
    assert not [r for r in rows(home) if r["kind"] == "table-replaces"]


def test_both_are_true_keeps_both_and_the_pair_isnt_raised_again(home):
    got = next_part(home, asking(NEW), ["3", "", "y"])
    assert "It's true now, beside the old one." in got.stdout
    said = canon(home).split("what it said no to:")[0]
    assert OLD in said and NEW in said
    again = run(
        home, ["1", "y", "", "y"], "2026-12-04T19:00:00Z"
    )  # the next part, played again
    assert "Is it, though?" in again.stdout and "💡" not in again.stdout, again.stdout


def test_a_different_thing_and_the_same_words_again_raise_nothing(home):
    other = next_part(
        home, asking("The egg is warm."), ["y", "", "y"]
    )  # one word shared: no subject
    assert "💡" not in other.stdout and "Is that true in your world?" in other.stdout
    again = run(
        home, ["2", "y", "y", "", "y"], "2026-12-04T19:00:00Z"
    )  # the first story again
    assert "Is the egg a real dragon?" in again.stdout and "💡" not in again.stdout, (
        again.stdout
    )


def test_the_gms_own_word_gets_the_heads_up_and_can_be_reworded(home):
    got = next_part(home, saying(), [NEW, "4", "Mira sneezes.", "y", "", "y"])
    assert "4. Let me reword it" in got.stdout and got.stdout.count("✋ GM, what happens?") == 2  # fmt: skip
    assert "It's the rule of the table now." in got.stdout
    facts = [r["fact"] for r in rows(home) if r["kind"] == "table-offer"]
    assert facts == ["Mira sneezes."] and not [r for r in rows(home) if r["kind"] == "table-replaces"]  # fmt: skip


def test_the_gms_own_word_can_replace_or_be_let_go(home):
    went = next_part(home, saying(), [NEW, "2", "", "y"])
    assert "Not kept. The old one stands." in went.stdout
    assert not [r for r in rows(home) if r["kind"] == "table-offer"]
    stood = next_part(home, saying(), [NEW, "1", "", "y"])
    assert (
        "It's the rule of the table now, and the old one is replaced." in stood.stdout
    )
    assert f"what it replaced:\n  was: {OLD}" in canon(home)
