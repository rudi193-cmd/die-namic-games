"""The sheets on paper (box/paper.py, run by open_table.py sheets): one page,
every seated character, text escaped, nothing written to the record, and a
file or a record folder never overwritten or written into."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import test_table_turn as tt

BOX = Path(__file__).resolve().parents[1] / "box"
OPEN = BOX / "open_table.py"


def sheets(table: Path, *args: str):
    done = subprocess.run([sys.executable, str(OPEN), "sheets", "--table", str(table), *args], capture_output=True, text=True, check=False)  # fmt: skip
    return done.returncode, done.stdout + done.stderr


def played(home: Path) -> Path:
    steps = [*tt.LADDER, (">", "s"), ("Write on a sheet?", "Tamsin finds a <b>rope</b>"), ("Write on a sheet?", "Oro is hurt by a club"), ("Write on a sheet?", ""), (">", "")]  # fmt: skip
    tt.table_turn(home, steps)
    return home / "table"


def test_the_page_holds_each_seated_character_and_is_escaped(tmp_path):
    table = played(tmp_path / "home")
    before = (table / "record" / "record.jsonl").read_bytes()
    to = tmp_path / "sheets.html"
    code, out = sheets(table, "--to", str(to))
    assert code == 0, out
    page = to.read_text()
    assert "Tamsin" in page and "Good at:</b> Grit +2, Heart +1" in page
    assert "Oro" in page and "Wit +2" in page and "Old Vell" not in page
    assert "<b>Carrying:</b> a &lt;b&gt;rope&lt;/b&gt;" in page and "<b>rope</b>" not in page  # fmt: skip
    assert "<b>Hurt</b>: by a club" in page
    assert "Tamsin has a ladder" in page  # a thing made true
    assert "@media print" in page and "prefers-color-scheme:dark" in page
    assert "<script" not in page and "http" not in page
    assert (table / "record" / "record.jsonl").read_bytes() == before  # nothing kept


def test_a_fact_with_markup_is_escaped(tmp_path):
    steps = [("Which story?", ""), (">", "o"), ("Who?", "1"), ("bring in?", "Tamsin has a <i>ladder</i>"), ("(y/n)", "y"), (">", "")]  # fmt: skip
    tt.table_turn(tmp_path / "home", steps)
    to = tmp_path / "p.html"
    assert sheets(tmp_path / "home" / "table", "--to", str(to))[0] == 0
    assert "Tamsin has a &lt;i&gt;ladder&lt;/i&gt;" in to.read_text()


def test_an_existing_file_or_a_path_in_the_record_is_refused(tmp_path):
    table = played(tmp_path / "home")
    there = tmp_path / "there.html"
    there.write_text("mine")
    code, out = sheets(table, "--to", str(there))
    assert code == 2 and "never overwritten" in out and there.read_text() == "mine"
    inside = table / "record" / "sheets.html"
    code, out = sheets(table, "--to", str(inside))
    assert code == 2 and "record folder" in out and not inside.exists()
    code, out = sheets(table, "--to", str(tmp_path / "x.html"), "--story", "nope")
    assert code == 2 and "no story nope" in out
    assert sheets(table)[0] == 2  # no --to
