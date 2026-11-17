"""ci/known.py: willow's report rows held to ci/known.json, a new row and a
stale entry each failing, a line number never part of the match."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
import known  # noqa: E402

G = "a password typed with its label"


def report(*wheres):
    return {"groups": [{"name": G, "rows": [{"where": w, "what": "value not shown"} for w in wheres]}]}


def entry(where, count=1):
    return {"group": G, "where": where, "what": "value not shown", "count": count, "why": "-"}


def test_a_place_is_matched_without_its_line():
    assert known.place("a/b.py:12") == "a/b.py"
    assert known.place("PyPI") == "PyPI" and known.place("x:y") == "x:y"
    assert known.keys(report("a.py:3", "a.py:90")) == Counter({(G, "a.py", "value not shown"): 2})


def test_every_row_known_is_nothing_to_settle_wherever_its_line_moved():
    assert known.held("secrets-audit", known.keys(report("a.py:3")), [entry("a.py")]) == []
    assert known.held("secrets-audit", known.keys(report("a.py:40")), [entry("a.py")]) == []


def test_a_row_nothing_accepts_is_new_and_a_second_in_a_known_file_too():
    got = known.held("secrets-audit", known.keys(report("a.py:3", "b.py:1")), [entry("a.py")])
    assert got == ["secrets-audit: new, 1 row(s): [a password typed with its label] b.py  value not shown"]
    got = known.held("secrets-audit", known.keys(report("a.py:3", "a.py:9")), [entry("a.py")])
    assert len(got) == 1 and got[0].startswith("secrets-audit: new, 1 row(s)")


def test_an_entry_no_row_matches_is_stale():
    got = known.held("secrets-audit", Counter(), [entry("a.py", count=2)])
    assert len(got) == 1 and "stale, known.json accepts 2 but 0 found" in got[0]


def test_advisories_is_refused_without_a_database_and_an_unknown_check_too(capsys):
    assert known.main(["advisories"]) == 2
    assert known.main(["--db"]) == 2
    assert known.main(["spelling"]) == 2
    assert "advisories needs --db" in capsys.readouterr().err
