"""A night at the table (box/table_scene.py) and the GM's screen built from it
(ui/screen.py): a box for every seat, a page crossing only as a sealed package,
a player's box that can't answer from the binder, and a page that holds what
table.json holds and never a key."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCENE = REPO / "box" / "table_scene.py"
SCREEN = REPO / "ui" / "screen.py"


def run(*argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, check=False)  # fmt: skip


@pytest.fixture(scope="module")
def night(tmp_path_factory) -> Path:
    to = tmp_path_factory.mktemp("night") / "n"
    got = run(SCENE, "run", "--to", to)
    assert got.returncode == 0, got.stdout + got.stderr
    return to


def test_every_seat_is_its_own_box_and_each_chain_holds(night):
    t = json.loads((night / "table.json").read_text())
    assert [s["seat"] for s in t["seats"]] == ["ash", "wren"]
    assert (
        t["gm"]["chain"].startswith("the chain holds")
        and "2 sealed" in t["gm"]["chain"]
    )
    for s in t["seats"]:
        assert s["chain"].startswith("the chain holds") and "0 sealed" in s["chain"]
        assert not (night / s["seat"] / "pile" / "monsters").exists()


def test_a_page_crosses_only_sealed_and_lands_good(night):
    t = json.loads((night / "table.json").read_text())
    (sent,) = t["gm"]["on_table"]
    assert sent["subject"].startswith("proposal:")
    assert {x["to"]: x["received"] for x in sent["sent"]} == {
        "ash": "good",
        "wren": "good",
    }
    assert all(r["verdict"] == "good" for s in t["seats"] for r in s["received"])


def test_the_wall_a_player_cant_answer_from_the_binder(night):
    t = json.loads((night / "table.json").read_text())
    assert t["gm"]["wall"]["exit"] == 0 and t["gm"]["wall"]["served"][0].startswith("monsters/")  # fmt: skip
    for s in t["seats"]:
        assert s["wall"] == {"exit": 42, "served": []}


def test_the_dice_box_shows_a_roll_on_the_record(night):
    d = json.loads((night / "table.json").read_text())["gm"]["dice"]
    rows = [json.loads(ln) for ln in (night / "gm" / "table" / "record" / "record.jsonl").read_text().splitlines()]  # fmt: skip
    roll = next(r for r in rows if r["n"] == d["rows"][0])
    assert roll["kind"] == "roll" and roll["faces"][0] == d["faces"]
    assert d["total"] == sum(d["faces"]) + roll["add"] + d["bonus"]


def test_the_screen_holds_the_table_and_no_key(night, tmp_path):
    page = tmp_path / "screen.html"
    got = run(SCREEN, "build", "--table", night / "table.json", "--to", page)
    assert got.returncode == 0, got.stderr
    html = page.read_text()
    assert "The Lantern Fair" in html and "Clockwork hound" in html
    assert "http://" not in html and "https://" not in html  # nothing fetched
    for f in night.rglob("*"):
        if f.name in ("key", "id") and f.is_file():
            secrets = re.findall(r"[0-9a-f]{32,}", f.read_text())
            assert secrets and not any(x in html for x in secrets), f


def test_a_script_end_in_the_table_cant_close_the_page(tmp_path):
    table = {"made": "", "demo_keys": True, "world": {"title": "</script><b>x", "setting": "", "scenes": [], "places": {}}, "gm": {}, "seats": []}  # fmt: skip
    (tmp_path / "t.json").write_text(json.dumps(table))
    assert run(SCREEN, "build", "--table", tmp_path / "t.json", "--to", tmp_path / "p.html").returncode == 0  # fmt: skip
    assert "</script><b>" not in (tmp_path / "p.html").read_text()


def test_a_night_is_laid_fresh_and_never_inside_the_repository(tmp_path):
    (tmp_path / "there").mkdir()
    assert run(SCENE, "run", "--to", tmp_path / "there").returncode == 2
    assert run(SCENE, "run", "--to", REPO / "night-here").returncode == 2
    assert not (REPO / "night-here").exists()
