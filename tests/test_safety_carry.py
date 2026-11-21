"""safety.py's lines and veils, and carry.py's sheets, read on their own: the
words a line needs, the page as a family writes it, and a sheet read in
order from every row."""

from __future__ import annotations

import sys
from pathlib import Path

BOX = Path(__file__).resolve().parents[1] / "box"
sys.path.insert(0, str(BOX))
import board
import carry
import safety


def page(tmp_path: Path, text: str) -> Path:
    (tmp_path / "pile").mkdir()
    (tmp_path / "pile" / "our-lines.md").write_text(text)
    return tmp_path


def test_the_page_is_read_as_written_under_its_two_headings(tmp_path):
    t = page(tmp_path, "- before any heading\n# Our lines\n- spiders\n* a pet getting hurt\n-ghosts\n-x\n-\n- \n## Veils\n- kissing\n## Other\n- not a line\n")  # fmt: skip
    assert safety.read(t) == (["spiders", "a pet getting hurt", "ghosts", "x"], ["kissing"])  # a dash with no space too  # fmt: skip


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


def blows(*states) -> list[dict]:
    rs = [{"n": 0, "kind": "fight-open", "encounter": "bruiser", "desc": "a test"}]
    rs += [{"n": i + 1, "kind": "fight-blow", "fight": 0, "state": s} for i, s in enumerate(states)]  # fmt: skip
    return rs


ORDER = {"kind": "initiative", "order": ["Sena Koll", "Engine-Blooded Bruiser", "Tide-touched Scout", "Tide-Touched Scout", "Warforged"]}  # fmt: skip


def test_the_board_follows_every_kind_of_blow():
    rs = blows(ORDER, {"kind": "round", "n": 1},
               {"kind": "attack", "by": "Sena Koll", "vs": "Engine-Blooded Bruiser", "hit": True, "target_hp": 40},
               {"kind": "attack", "by": "Engine-Blooded Bruiser", "vs": "Sena Koll", "hit": False, "target_hp": 3},
               {"kind": "special", "by": "Tide-Touched Scout", "name": "Riptide"},
               {"kind": "save", "who": "Warforged", "vs": "Riptide", "saved": False, "dmg": 6, "hp": 25},
               {"kind": "save", "who": "Sena Koll", "vs": "Glare", "saved": False, "effect": "blind"},
               {"kind": "save", "who": "Tide-touched Scout", "vs": "Slam", "saved": False, "effect": "stun"},
               {"kind": "overheat", "who": "Engine-Blooded Bruiser", "dmg": 5, "hp": 35})  # fmt: skip
    s = board.state(rs, 0)
    f = {x["name"]: x for x in s["fighters"]}
    assert (
        f["Engine-Blooded Bruiser"]["hp"] == 35 and f["Sena Koll"]["hp"] == 20
    )  # a miss moves nothing
    assert f["Warforged"]["hp"] == 25 and f["Sena Koll"]["blinded"] and f["Tide-touched Scout"]["stunned"]  # fmt: skip
    assert (
        s["round"] == 1 and s["outcome"] is None and s["next"] == "Warforged"
    )  # after the scout's special
    text = board.draw(s)
    assert "Sena Koll" in text and "blinded" in text and "stunned" in text and "▶ Warforged" in text  # fmt: skip


def test_a_stun_ends_with_the_turn_it_loses_and_a_blinding_with_its_round():
    rs = blows(ORDER, {"kind": "round", "n": 1},
               {"kind": "save", "who": "Sena Koll", "vs": "Glare", "saved": False, "effect": "blind"},
               {"kind": "save", "who": "Warforged", "vs": "Slam", "saved": False, "effect": "stun"},
               {"kind": "round", "n": 2},
               {"kind": "stunned_skip", "who": "Warforged"})  # fmt: skip
    f = {x["name"]: x for x in board.state(rs, 0)["fighters"]}
    assert not f["Sena Koll"]["blinded"] and not f["Warforged"]["stunned"]
    g = {x["name"]: x for x in board.state(rs, 0, 1)["fighters"]}  # as round 1 ended
    assert g["Sena Koll"]["blinded"] and g["Warforged"]["stunned"]


def test_the_fallen_are_down_and_skipped_for_the_next_turn():
    rs = blows(ORDER, {"kind": "round", "n": 1},
               {"kind": "attack", "by": "Sena Koll", "vs": "Engine-Blooded Bruiser", "hit": True, "target_hp": 0},
               {"kind": "down", "who": "Engine-Blooded Bruiser"})  # fmt: skip
    s = board.state(rs, 0)
    assert s["next"] == "Tide-touched Scout"  # the Bruiser, next in order, is down
    assert "✖ down" in board.draw(s) and "Engine-Blooded Bruiser ✖" in board.draw(s)


def test_a_bar_is_never_empty_while_standing_and_full_at_full():
    assert board.bar(1, 75) == "█" + "░" * 9
    assert board.bar(0, 75) == "░" * 10 and board.bar(31, 31) == "█" * 10
    assert board.bar(10, 20) == "█" * 5 + "░" * 5
