"""box/fight.py: aetheris5e's fights, blow by blow on a box's record.

The fights are the-table's (aetheris5e's engine and stat blocks); what is
tested here is that a box keeps one: every blow a kernel row, the dice
seeded by the row before, and a fight edited after the fact refused even
when its forger rehashes the chain. The table is the test's, laid in a
scratch folder with its own key; nothing here seals."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BOX = Path(__file__).resolve().parents[1] / "box"
sys.path.insert(0, str(BOX))
import willow_pin

sys.path.insert(0, str(willow_pin.root()))
import kernel

NOW = ["--now", "2026-11-20T21:00:00Z"]


def py(*argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, check=False)  # fmt: skip


@pytest.fixture(scope="module")
def laid(tmp_path_factory) -> Path:
    tmp = tmp_path_factory.mktemp("fight")
    got = py(BOX / "open_table.py", "open", "--table", tmp / "table", "--key", tmp / "gm.key", *NOW)  # fmt: skip
    assert got.returncode == 42, got.stderr
    return tmp / "table"


@pytest.fixture
def table(laid, tmp_path) -> Path:
    shutil.copytree(laid, tmp_path / "table")
    return tmp_path / "table"


def fight(table: Path, *argv) -> subprocess.CompletedProcess:
    return py(BOX / "fight.py", "--table", table, *argv, *NOW)


def rows(table: Path) -> list[dict]:
    got, breaks = kernel.read(table / "record" / "record.jsonl")
    assert not breaks
    return got


def forge(table: Path, change) -> None:
    """The record rewritten by CHANGE, then every row's chain made again: a
    forger's copy, which the chain alone can't tell from the record."""
    path = table / "record" / "record.jsonl"
    old = [json.loads(line) for line in path.read_text().splitlines()]
    new, prev = [], kernel.GENESIS
    for r in change(old):
        r = {k: v for k, v in r.items() if k != "hash"} | {"n": len(new), "prev": prev}  # fmt: skip
        r["hash"] = kernel.h256(kernel.canon(r))
        new.append(r)
        prev = r["hash"]
    path.write_text("".join(kernel.canon(r) + "\n" for r in new))


def test_a_fight_is_kept_blow_by_blow_and_checks(table):
    before = len(rows(table))
    got = fight(table, "fight", "warden")
    assert got.returncode == 0, got.stderr
    kept = rows(table)[before:]
    opened, *blows, end = kept
    assert opened["kind"] == "fight-open" and opened["encounter"] == "warden"
    assert opened["seed"] == rows(table)[before - 1]["hash"]  # nobody picked it
    assert blows and {b["kind"] for b in blows} == {"fight-blow"}
    assert {b["fight"] for b in blows} == {end["fight"]} == {opened["n"]}
    assert blows[0]["note"].startswith("initiative: ")
    assert all(f"  {b['note']}" in got.stdout for b in blows)
    res = end["result"]
    assert f"{res['outcome'].upper()} in {res['rounds']} rounds" in got.stdout
    assert {r["who"] for r in kept} == {"fight"}
    assert not [
        r for r in rows(table) if r["kind"] in ("seal", "decline")
    ]  # it seals nothing
    ok = fight(table, "check")
    assert (
        ok.returncode == 0 and ok.stdout == "1 fight on the record; every blow holds.\n"
    )


def test_the_same_record_gives_the_same_fight_and_the_next_a_new_one(laid, tmp_path):
    a, b = (shutil.copytree(laid, tmp_path / n) for n in "ab")
    first, again = fight(a, "fight", "raiders"), fight(b, "fight", "raiders")
    assert first.returncode == again.returncode == 0
    assert first.stdout == again.stdout
    second = fight(a, "fight", "raiders")  # seeded by the first fight's end
    assert second.stdout.split("\n", 1)[1] != first.stdout.split("\n", 1)[1]
    ok = fight(a, "check")
    assert ok.returncode == 0 and ok.stdout.startswith("2 fights on the record")


def test_a_blow_edited_and_the_chain_rehashed_is_refused(table):
    fight(table, "fight", "warden")

    def edit(old):
        hit = next(
            r for r in old if r["kind"] == "fight-blow" and " hits " in r["note"]
        )
        hit["note"] = hit["note"].replace(" hits ", " misses ", 1)
        return old

    forge(table, edit)
    got = fight(table, "check")
    assert got.returncode == 2
    assert "blow " in got.stderr and "isn't what its seed gives" in got.stderr, (
        got.stderr
    )


@pytest.mark.parametrize("cut", ["fight-blow", "fight-end"])
def test_a_blow_or_the_ending_dropped_is_refused(table, cut):
    fight(table, "fight", "warden")

    def drop(old):
        last = max(i for i, r in enumerate(old) if r["kind"] == cut)
        return old[:last] + old[last + 1 :]

    forge(table, drop)
    got = fight(table, "check")
    assert got.returncode == 2 and "its seed gives" in got.stderr, got.stderr


def test_a_seed_that_isnt_the_row_before_is_refused(table):
    fight(table, "fight", "warden")

    def reseed(old):
        next(r for r in old if r["kind"] == "fight-open")["seed"] = "0" * 64
        return old

    forge(table, reseed)
    got = fight(table, "check")
    assert got.returncode == 2 and "its seed isn't the hash of the row before it" in got.stderr  # fmt: skip


def test_a_row_edited_without_its_hash_is_the_chains_to_refuse(table):
    fight(table, "fight", "warden")
    path = table / "record" / "record.jsonl"
    path.write_text(path.read_text().replace(" hits ", " misses ", 1))
    for argv in (["check"], ["fight", "warden"]):
        got = fight(table, *argv)
        assert got.returncode == 2 and "the record doesn't verify" in got.stderr


def test_an_encounter_that_isnt_one_is_refused_and_nothing_written(table):
    before = rows(table)
    got = fight(table, "fight", "dragon")
    assert got.returncode == 2 and "no encounter 'dragon': warden, enforcers, raiders, bruiser" in got.stderr  # fmt: skip
    assert rows(table) == before


def test_the_encounters_are_listed():
    got = py(BOX / "fight.py", "list")
    assert got.returncode == 0
    assert [line.split()[0] for line in got.stdout.splitlines()] == ["warden", "enforcers", "raiders", "bruiser"]  # fmt: skip


@pytest.mark.parametrize("argv", [[], ["fight", "warden"], ["--table", "{t}"], ["--table", "{t}", "fight"], ["--table", "{t}", "check", "x"], ["--table", "{t}", "roll"]])  # fmt: skip
def test_a_bad_command_line_prints_how_to_fight(table, argv):
    got = py(BOX / "fight.py", *[a.format(t=table) for a in argv])
    assert got.returncode == 2
    assert got.stderr.strip() == "python box/fight.py list\n    python box/fight.py --table DIR fight ENCOUNTER [--now TS]\n    python box/fight.py --table DIR check"  # fmt: skip


def test_a_table_with_no_record_prints_how_to_fight(tmp_path):
    got = py(BOX / "fight.py", "--table", tmp_path, "check")
    assert got.returncode == 2 and "python box/fight.py --table DIR check" in got.stderr
