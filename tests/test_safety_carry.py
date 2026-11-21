"""safety.py's lines and veils, and carry.py's sheets, read on their own: the
words a line needs, the page as a family writes it, and a sheet read in
order from every row."""

from __future__ import annotations

import sys
from pathlib import Path

BOX = Path(__file__).resolve().parents[1] / "box"
sys.path.insert(0, str(BOX))
import carry
import safety


def page(tmp_path: Path, text: str) -> Path:
    (tmp_path / "pile").mkdir()
    (tmp_path / "pile" / "our-lines.md").write_text(text)
    return tmp_path


def test_the_page_is_read_as_written_under_its_two_headings(tmp_path):
    t = page(tmp_path, "- before any heading\n# Our lines\n- spiders\n* a pet getting hurt\n-\n- \n## Veils\n- kissing\n## Other\n- not a line\n")  # fmt: skip
    assert safety.read(t) == (["spiders", "a pet getting hurt"], ["kissing"])


def test_no_page_is_no_lines(tmp_path):
    assert safety.read(tmp_path) == ([], [])


def test_a_line_needs_its_meaning_words_not_its_little_ones():
    assert safety.touches(["a pet getting hurt"], "The pet is hurt badly.") == "a pet getting hurt"  # fmt: skip
    assert safety.touches(["a pet getting hurt"], "A cat getting fed.") is None
    assert safety.touches(["a pet getting hurt"], "The pet sleeps.") is None


def test_a_line_of_only_little_words_needs_them_all():
    assert safety.touches(["being"], "Being alone in the dark.") == "being"
    assert safety.touches(["being"], "Alone in the dark.") is None


def test_a_plural_or_a_possessive_is_the_same_word():
    assert safety.touches(["spiders"], "A spider drops from the beam.") == "spiders"
    assert safety.touches(["hook"], "Tamsin climbs to the stall's hooks.") == "hook"
    assert safety.touches(["box"], "Two boxes.") == "box"


NAMES = ["Tamsin", "Oro", "Old Vell"]


def test_a_sheet_line_is_a_name_a_change_and_a_thing():
    assert carry.read("Tamsin finds a rope.", NAMES) == {"char": "Tamsin", "change": "carry", "what": "a rope"}  # fmt: skip
    assert carry.read("Old Vell gives away the lantern", NAMES) == {"char": "Old Vell", "change": "spend", "what": "the lantern"}  # fmt: skip
    assert carry.read("Oro is hurt by a club", NAMES) == {"char": "Oro", "change": "hurt", "what": "by a club"}  # fmt: skip
    assert carry.read("Oro is healed", NAMES) == {"char": "Oro", "change": "heal", "what": ""}  # fmt: skip


def test_a_sheet_line_it_cant_read_is_none():
    for line in ("Mira finds a key", "Tamsin finds", "Tamsin finds the", "Tamsin sings", "Tamsinfinds a rope"):  # fmt: skip
        assert carry.read(line, NAMES) is None, line


def rows(*changes) -> list[dict]:
    return [{"kind": carry.KIND, "char": c, "change": ch, "what": w} for c, ch, w in changes]  # fmt: skip


def test_a_sheet_is_every_row_in_order_a_thing_used_by_its_words():
    got = rows(("Oro", "carry", "a rope"), ("Oro", "carry", "a lantern"), ("Tamsin", "carry", "a rope"), ("oro", "spend", "the ropes"), ("Oro", "spend", "a kite"))  # fmt: skip
    assert carry.sheet(got, "Oro") == (["a lantern"], [])
    assert carry.sheet(got, "Tamsin") == (["a rope"], [])


def test_a_wound_lasts_until_healed_and_heals_all_at_once():
    got = rows(("Oro", "hurt", "by a club"), ("Oro", "hurt", ""), ("Oro", "heal", ""), ("Oro", "hurt", "stung"))  # fmt: skip
    assert carry.sheet(got, "Oro") == ([], ["stung"])
    assert carry.sheet(got[:2], "Oro") == ([], ["by a club", ""])


def test_what_is_said_aloud():
    assert carry.said("Oro", ["a lantern", "a kite"], ["by a club", ""]) == "Oro carries a lantern, a kite and is still hurt (by a club)"  # fmt: skip
    assert carry.said("Oro", [], [""]) == "Oro is still hurt"
    assert carry.said("Oro", [], []) == ""
