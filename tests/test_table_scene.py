"""A week of tables (box/table_scene.py) and the screens built from it
(ui/screen.py): a box for every seat, one identity a person carries to every
table, a page crossing only as a sealed package, a player's box that can't
answer from the binder, and a person's page that holds their own seats and
nothing else, never a key."""

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
def week(tmp_path_factory) -> Path:
    to = tmp_path_factory.mktemp("week") / "w"
    got = run(SCENE, "run", "--to", to)
    assert got.returncode == 0, got.stdout + got.stderr
    return to


def table(week: Path, tid: str) -> dict:
    return json.loads((week / tid / "table.json").read_text())


def rows(box: Path) -> list[dict]:
    return [json.loads(ln) for ln in (box / "record.jsonl").read_text().splitlines()]


def person_page(week: Path, tmp: Path, who: str) -> str:
    page = tmp / f"{who}.html"
    got = run(SCREEN, "build", "--night", week, "--person", who, "--to", page)
    assert got.returncode == 0, got.stderr
    return page.read_text()


def test_one_person_a_gm_at_one_table_and_a_player_at_another(week):
    people = json.loads((week / "people.json").read_text())
    seats = {p: {(s["table"], s["seat"]) for s in v} for p, v in people.items()}
    assert seats == {
        "rook": {("thursday", "gm"), ("sunday", "rook")},
        "ash": {("thursday", "ash"), ("sunday", "gm")},
        "wren": {("thursday", "wren"), ("sunday", "wren")},
    }


def test_every_seat_is_its_own_box_and_each_chain_holds(week):
    for tid, sealed in (("thursday", 2), ("sunday", 1)):
        t = table(week, tid)
        assert t["gm"]["chain"].startswith("the chain holds") and f"{sealed} sealed" in t["gm"]["chain"]  # fmt: skip
        for s in t["seats"]:
            assert s["chain"].startswith("the chain holds") and "0 sealed" in s["chain"]
            assert not (week / tid / s["seat"] / "pile" / "monsters").exists()


def test_one_identity_is_carried_to_every_table(week):
    thu = json.loads((week / "thursday" / "rook-to-wren.pkg").read_text())
    sun = json.loads((week / "sunday" / "ash-to-wren.pkg").read_text())
    assert thu["for"] == sun["for"]  # the same Wren at both tables
    assert thu["from"] != sun["from"]  # sent by two different GMs


def test_a_page_crosses_only_sealed_and_lands_good(week):
    for tid, rule in (("thursday", "A draw is offered"), ("sunday", "Dice are rolled")):
        t = table(week, tid)
        (sent,) = t["gm"]["on_table"]
        assert sent["subject"].startswith("proposal:")
        assert {x["received"] for x in sent["sent"]} == {"good"}
        for s in t["seats"]:
            (got,) = s["received"]  # read from the package that held
            assert got["what"].startswith(rule) and got["verdict"] == "good"
            assert got["cites"] and all(c.startswith("house-rules.md:") for c in got["cites"])  # fmt: skip


def test_the_wall_a_players_box_cant_answer_from_the_binder(week):
    for tid in ("thursday", "sunday"):
        t = table(week, tid)
        assert t["gm"]["wall"]["exit"] == 0 and t["gm"]["wall"]["served"][0].startswith("monsters/")  # fmt: skip
        for s in t["seats"]:
            assert s["wall"] == {
                "exit": 42,
                "served": [],
            }  # Rook too, at the table he plays


def test_the_dice_box_shows_a_roll_on_the_record(week):
    for tid in ("thursday", "sunday"):
        d = table(week, tid)["gm"]["dice"]
        roll = next(r for r in rows(week / tid / "gm" / "table" / "record") if r["n"] == d["rows"][0])  # fmt: skip
        assert roll["kind"] == "roll" and roll["faces"][0] == d["faces"]
        assert d["total"] == sum(d["faces"]) + roll["add"] + d["bonus"]


def test_an_offer_waits_on_the_gms_call_and_nothing_answers_it(week):
    t = table(week, "thursday")
    (offer,) = t["gm"]["offers"]
    assert [s["offered"] for s in t["seats"]] == [[offer], []]
    rs = rows(week / "thursday" / "gm" / "table" / "record")
    assert any(r.get("subject") == offer["subject"] and r["kind"] == "proposal" for r in rs)  # fmt: skip
    assert not any(r.get("subject") == offer["subject"] and r["kind"] in ("seal", "decline") for r in rs)  # fmt: skip


def notes(week: Path) -> dict:
    """Every player's notes, by (table, person)."""
    return {(tid, s["seat"]): s["notes"] for tid in ("thursday", "sunday") for s in table(week, tid)["seats"]}  # fmt: skip


@pytest.mark.parametrize("who", ["rook", "ash", "wren"])
def test_a_persons_page_holds_their_own_seats_and_nothing_else(week, tmp_path, who):
    html = person_page(week, tmp_path, who)
    people = json.loads((week / "people.json").read_text())[who]
    runs = any(s["seat"] == "gm" for s in people)
    for s in people:
        assert table(week, s["table"])["world"]["title"] in html
    # a player's own notes: on their page, and on no one else's, the GM's included
    for (tid, p), ns in notes(week).items():
        for n in ns:
            assert (n in html) == (p == who), (tid, p, n)
    # the binder only in the data of someone who runs a table (the page's
    # markup holds both screens' empty panels; what fills them is the data)
    data = html.split('<script id="table" type="application/json">', 1)[1].split("</script>", 1)[0]  # fmt: skip
    for gm_only in ("Cogwen", "springs", '"bestiary"', '"your_call"'):
        assert (gm_only in data) == runs, gm_only
    assert "http://" not in html and "https://" not in html
    for f in week.rglob("*"):  # no key, no identity's secret half
        if f.name in ("key", "id") and f.is_file():
            secrets = re.findall(r"[0-9a-f]{32,}", f.read_text())
            assert secrets and not any(x in html for x in secrets), f


def test_one_seat_at_one_table_still_builds(week, tmp_path):
    for seat in ("gm", "ash"):
        page = tmp_path / f"{seat}.html"
        got = run(SCREEN, "build", "--table", week / "thursday" / "table.json", "--to", page, "--seat", seat)  # fmt: skip
        assert got.returncode == 0, got.stderr
        assert "The Lantern Fair" in page.read_text()


def test_a_script_end_in_the_table_cant_close_the_page(tmp_path):
    doc = {"made": "", "demo_keys": True, "day": "", "world": {"title": "</script><b>x", "setting": "", "scenes": [], "places": {}}, "gm": {}, "table": {}, "seats": []}  # fmt: skip
    (tmp_path / "t.json").write_text(json.dumps(doc))
    assert run(SCREEN, "build", "--table", tmp_path / "t.json", "--to", tmp_path / "p.html").returncode == 0  # fmt: skip
    assert "</script><b>" not in (tmp_path / "p.html").read_text()


def test_a_seat_or_person_not_there_is_refused(week, tmp_path):
    no_seat = run(SCREEN, "build", "--table", week / "thursday" / "table.json", "--to", tmp_path / "x.html", "--seat", "nobody")  # fmt: skip
    no_one = run(SCREEN, "build", "--night", week, "--person", "nobody", "--to", tmp_path / "y.html")  # fmt: skip
    assert no_seat.returncode == 2 and no_one.returncode == 2
    assert not (tmp_path / "x.html").exists() and not (tmp_path / "y.html").exists()


def test_a_week_is_laid_fresh_and_never_inside_the_repository(tmp_path):
    (tmp_path / "there").mkdir()
    assert run(SCENE, "run", "--to", tmp_path / "there").returncode == 2
    assert run(SCENE, "run", "--to", REPO / "week-here").returncode == 2
    assert not (REPO / "week-here").exists()


# the night goes on: packages landing in a drop folder, box/follow.py

FOLLOW = REPO / "box" / "follow.py"


@pytest.fixture
def night(tmp_path) -> Path:
    to = tmp_path / "w"
    got = run(SCENE, "run", "--to", to)
    assert got.returncode == 0, got.stdout + got.stderr
    return to


def follow(night: Path, who: str) -> str:
    got = run(FOLLOW, "--night", night, "--person", who, "--once")
    assert got.returncode == 0, got.stderr
    return got.stdout


def seat(night: Path, tid: str, who: str) -> dict:
    return next(s for s in table(night, tid)["seats"] if s["seat"] == who)


def test_a_package_landing_is_received_into_the_right_seat_and_shown(night):
    assert run(SCENE, "later", "--to", night, "--table", "thursday", "--rule", "Turns").returncode == 0  # fmt: skip
    assert (night / "drop" / "wren" / "thursday-turns.pkg").exists()
    said = follow(night, "wren")
    assert "thursday-turns.pkg: good, at thursday" in said
    got = seat(night, "thursday", "wren")["received"][-1]
    assert got["claim"].startswith("the rule Turns") and got["just"] is True
    assert seat(night, "sunday", "wren")["received"][-1]["claim"].startswith("the rule Dice")  # fmt: skip
    assert not (night / "drop" / "wren" / "thursday-turns.pkg").exists()
    assert (
        night / "drop" / "wren" / "kept" / "thursday-turns.pkg"
    ).exists()  # kept, never deleted
    rs = rows(night / "thursday" / "wren" / "box")
    assert [r["verdict"] for r in rs if r["kind"] == "received"] == ["good", "good"]
    html = (night / "wren.html").read_text()
    stamp = (night / "wren.html.stamp.js").read_text()
    assert "Play goes round the table in seat order" in html
    assert re.search(r'"stamp": "([0-9a-f]{16})"', html).group(1) in stamp
    # the GM's screen learns the rule went out: the table changed, the page is built again
    assert "Turns" in json.dumps(table(night, "thursday")["gm"]["on_table"])
    assert "page built" in follow(night, "rook")


def test_what_didnt_hold_is_on_the_record_and_shown_never_its_words(night):
    pk = json.loads((night / "thursday" / "rook-to-wren.pkg").read_text())
    pk["answers"][0]["data"] = "A draw is whatever the loudest player says."
    (night / "drop" / "wren" / "edited.pkg").write_text(json.dumps(pk))
    (night / "thursday" / "rook-to-wren.pkg").replace(night / "drop" / "ash" / "for-wren.pkg")  # not Ash's  # fmt: skip
    (night / "drop" / "ash" / "junk.pkg").write_text("not a package")
    assert "edited.pkg: broken, at thursday" in follow(night, "wren")
    said = follow(night, "ash")
    assert "for-wren.pkg: not-for-you, at thursday" in said and "junk.pkg: not a package" in said  # fmt: skip
    assert seat(night, "thursday", "wren")["refused"][0]["verdict"] == "broken"
    assert seat(night, "thursday", "ash")["refused"][0]["verdict"] == "not-for-you"
    assert "loudest player" not in (night / "wren.html").read_text()
    for who, verdict in (("wren", "broken"), ("ash", "not-for-you")):
        rs = rows(night / "thursday" / who / "box")
        assert [r["verdict"] for r in rs if r["kind"] == "received"] == [
            "good",
            verdict,
        ]
    assert (night / "drop" / "ash" / "kept" / "junk.pkg").exists()


def test_the_same_package_twice_is_said_once(night):
    run(SCENE, "later", "--to", night, "--table", "thursday", "--rule", "Turns")
    follow(night, "ash")
    (night / "drop" / "ash" / "kept" / "thursday-turns.pkg").replace(night / "drop" / "ash" / "again.pkg")  # fmt: skip
    assert "already received" in follow(night, "ash")
    assert [r["claim"][:14] for r in seat(night, "thursday", "ash")["received"]] == ["the rule Draws", "the rule Turns"]  # fmt: skip


def test_just_arrived_is_only_the_latest_round(night):
    run(SCENE, "later", "--to", night, "--table", "thursday", "--rule", "Turns")
    follow(night, "ash")
    run(SCENE, "later", "--to", night, "--table", "thursday", "--rule", "Arguments")
    follow(night, "ash")
    got = seat(night, "thursday", "ash")["received"]
    assert [r.get("just", False) for r in got] == [False, False, True]


def test_later_and_follow_refuse_what_isnt_there(night):
    assert run(SCENE, "later", "--to", night, "--table", "thursday", "--rule", "Draws").returncode == 2  # already sent  # fmt: skip
    assert run(SCENE, "later", "--to", night, "--table", "monday", "--rule", "Turns").returncode == 2  # fmt: skip
    assert run(FOLLOW, "--night", night, "--person", "nobody", "--once").returncode == 2
