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
    assert {r["ts"] for r in kept} == {NOW[1]}  # the time given, not the clock's
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


def end_night(table: Path, now: str = "2026-11-20T23:00:00Z") -> None:
    """The night ended: a session seal handed in over it (never sealed here)."""
    seal = (
        willow_pin.root() / "adapters" / "stdlib" / "session-seal" / "session_seal.py"
    )
    assert py(seal, "--box", table / "record", "--now", now).returncode == 42


def gm_eyes(table: Path) -> tuple[str, str]:
    got = py(BOX / "session.py", "--table", table, "recap")
    assert got.returncode in (0, 42), got.stderr
    return tuple(got.stdout.split("## For the GM's eyes"))


def test_the_recap_tells_the_gm_how_last_nights_fights_ended_never_aloud(table):
    assert fight(table, "fight", "raiders").returncode == 0
    end = rows(table)[-1]["result"]
    end_night(table)
    aloud, gm = gm_eyes(table)
    said = {"party": "the party won", "foe": "the party fell"}[end["outcome"]]
    line = f"  the party ambushed by 4 Scorched Belt Raiders: {said} in {end['rounds']} rounds; standing: "
    assert f"Fights last time:\n{line}" in gm
    assert "Raider" not in aloud and "Fights" not in aloud  # a fight isn't canon


def test_a_fight_before_any_night_ended_is_so_far_and_older_ones_drop_off(table):
    fight(table, "fight", "warden")
    assert (
        "Fights so far:\n  the full party vs a Mind-Forge Warden" in gm_eyes(table)[1]
    )
    end_night(table)
    roll = py(BOX.parent / "games" / "play.py", "play-dice5e", "--table", table, "roll", "1d20")  # fmt: skip
    assert roll.returncode == 0, roll.stderr
    end_night(table, "2026-11-27T23:00:00Z")  # a second night: a roll, no fight
    assert "Fights" not in gm_eyes(table)[1]


def test_the_tables_check_plays_its_fights_again(table):
    assert "## the fights" not in py(BOX / "open_table.py", "check", "--table", table).stdout  # fmt: skip
    fight(table, "fight", "bruiser")
    ok = py(BOX / "open_table.py", "check", "--table", table)
    assert "## the fights\n1 fight on the record; every blow holds." in ok.stdout, (
        ok.stderr
    )
    assert ok.returncode != 2

    def edit(old):
        hit = next(
            r for r in old if r["kind"] == "fight-blow" and " hits " in r["note"]
        )
        hit["note"] = hit["note"].replace(" hits ", " misses ", 1)
        return old

    forge(table, edit)
    bad = py(BOX / "open_table.py", "check", "--table", table)
    assert (
        bad.returncode == 2
        and "refused: the fights: refused: fight at row" in bad.stderr
    ), bad.stderr


def test_a_fights_dice_are_its_seed_read_as_hex(table):
    """The rule a fight is replayed by, by hand or by check: random.Random of
    the seed read as a hexadecimal number, the engine and stat blocks as
    aetheris5e has them."""
    import random

    import fight as f

    combat, statblocks = f.engine()
    seed = "00ff" * 16
    blows, res = f.play("raiders", seed)
    kept = f.Kept()
    again = combat.Combat(statblocks.build_encounter("raiders"), random.Random(int(seed, 16)), sink=kept).run()  # fmt: skip
    assert blows == kept.blows and res == json.loads(json.dumps(again))
