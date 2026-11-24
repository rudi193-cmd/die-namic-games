"""box/fight.py: aetheris5e's fights, blow by blow on a box's record.

The fights are willow's play-fight5e add-on, through the pin (aetheris5e's
engine and stat blocks, on the tower's dice); what is tested here is that a
table keeps one through box/fight.py: every blow a kernel row, and a fight
edited after the fact refused even when its forger rehashes the chain. The
engine's own tests are play-fight5e's. The table is the test's, laid in a
scratch folder with its own key; nothing here seals."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("dice")  # play-fight5e's dice library
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
    kept = [r for r in rows(table)[before:] if r["kind"].startswith("encounter-")]
    opened, *blows, end = kept
    assert opened["kind"] == "encounter-open" and opened["encounter"] == "warden"
    assert {r["kind"] for r in rows(table)[before:]} == {"encounter-open", "encounter-blow", "encounter-end", "tower-drop", "tower-out"}  # fmt: skip
    assert blows and {b["kind"] for b in blows} == {"encounter-blow"}
    assert {b["fight"] for b in blows} == {end["fight"]} == {opened["n"]}
    assert blows[0]["note"].startswith("initiative: ")
    assert all(f"  {b['note']}" in got.stdout for b in blows)
    res = end["result"]
    assert f"{res['outcome'].upper()} in {res['rounds']} rounds" in got.stdout
    assert {r["who"] for r in kept} == {"play-fight5e"}
    assert {r["ts"] for r in kept} == {NOW[1]}  # the time given, not the clock's
    assert not [
        r for r in rows(table) if r["kind"] in ("seal", "decline")
    ]  # it seals nothing
    ok = fight(table, "check")
    assert (
        ok.returncode == 0
        and ok.stdout == "1 encounter on the record; every blow holds\n"
    )


def test_two_fights_on_one_record_both_hold(table):
    assert fight(table, "fight", "raiders").returncode == 0
    assert fight(table, "fight", "raiders").returncode == 0
    ok = fight(table, "check")
    assert ok.returncode == 0 and ok.stdout.startswith("2 encounters on the record")


def test_a_blow_edited_and_the_chain_rehashed_is_refused(table):
    fight(table, "fight", "warden")

    def edit(old):  # the dice are the tower's, so a fight may have no hit: swap one
        swap = {" hits ": " misses ", " misses ": " hits "}
        blow = next(
            r
            for r in old
            if r["kind"] == "encounter-blow" and any(w in r["note"] for w in swap)
        )
        was = next(w for w in swap if w in blow["note"])
        blow["note"] = blow["note"].replace(was, swap[was], 1)
        return old

    forge(table, edit)
    got = fight(table, "check")
    assert got.returncode == 2
    assert "isn't what its dice give" in got.stderr, got.stderr


@pytest.mark.parametrize("cut", ["encounter-blow", "encounter-end"])
def test_a_blow_or_the_ending_dropped_is_refused(table, cut):
    fight(table, "fight", "warden")

    def drop(old):
        last = max(i for i, r in enumerate(old) if r["kind"] == cut)
        return old[:last] + old[last + 1 :]

    forge(table, drop)
    got = fight(table, "check")
    assert got.returncode == 2 and "the encounter opened at row" in got.stderr, (
        got.stderr
    )


def test_a_row_edited_without_its_hash_is_the_chains_to_refuse(table):
    fight(table, "fight", "warden")
    path = table / "record" / "record.jsonl"
    text = path.read_text()  # the tower's dice: a fight may have no hit, or no miss
    was, now = (" hits ", " misses ") if " hits " in text else (" misses ", " hits ")
    assert was in text
    path.write_text(text.replace(was, now, 1))
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
    assert got.stderr.strip() == "python box/fight.py list\n    python box/fight.py --table DIR fight ENCOUNTER [--now TS]\n    python box/fight.py --table DIR check\n    python box/fight.py --table DIR board [--fight ROW] [--round N]"  # fmt: skip


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
    assert "## the fights\n1 encounter on the record; every blow holds" in ok.stdout, (
        ok.stderr
    )
    assert ok.returncode != 2

    def edit(old):  # the dice are the tower's, so a fight may have no hit: swap one
        swap = {" hits ": " misses ", " misses ": " hits "}
        blow = next(
            r
            for r in old
            if r["kind"] == "encounter-blow" and any(w in r["note"] for w in swap)
        )
        was = next(w for w in swap if w in blow["note"])
        blow["note"] = blow["note"].replace(was, swap[was], 1)
        return old

    forge(table, edit)
    bad = py(BOX / "open_table.py", "check", "--table", table)
    assert (
        bad.returncode == 2
        and "refused: the fights: play-fight5e: the encounter opened at row"
        in bad.stderr
    ), bad.stderr


def test_the_opening_screen_tells_the_gm_how_last_nights_fights_ended(table):
    assert fight(table, "fight", "raiders").returncode == 0
    end = rows(table)[-1]["result"]
    end_night(table)
    env = {**os.environ, "DIE_NAMIC_HOME": str(table.parent), "DIE_NAMIC_NOW": "2026-11-27T19:00:00Z"}  # fmt: skip
    got = subprocess.run([sys.executable, BOX / "play.py"], input="", capture_output=True, text=True, env=env, check=False)  # fmt: skip
    said = {"party": "the party won", "foe": "the party fell"}[end["outcome"]]
    assert f"Just for you, GM, how last time's fights ended:\n  the party ambushed by 4 Scorched Belt Raiders: {said} in {end['rounds']} rounds; standing: " in got.stdout  # fmt: skip
    head = got.stdout.split("Let's start a story.")[0]
    assert (
        "(row" not in head and "Just for you, GM, how last time's fights ended" in head
    )


def board(table: Path, *argv) -> subprocess.CompletedProcess:
    return py(BOX / "fight.py", "--table", table, "board", *argv)


def test_the_board_at_the_end_is_what_the_fights_end_says(table):
    assert fight(table, "fight", "raiders").returncode == 0
    end = rows(table)[-1]["result"]
    got = board(table)
    assert got.returncode == 0, got.stderr
    said = {"party": "the party won", "foe": "the party fell"}[end["outcome"]]
    assert got.stdout.startswith(f"⚔️  the party ambushed by 4 Scorched Belt Raiders, round {end['rounds']} of {end['rounds']}: {said}\n")  # fmt: skip
    standing = set(end["party_survivors"] + end["foe_survivors"])
    for name in ["Sena Koll", "Tide-touched Scout", "Warforged"] + [f"Scorched Belt Raider #{i}" for i in range(1, 5)]:  # fmt: skip
        mark = next(
            x for x in got.stdout.splitlines() if x.strip().startswith(name + " ")
        )
        assert ("✖ down" in mark) == (name not in standing), mark
    assert "▶" not in got.stdout  # it's over: no one's turn


def test_the_board_after_a_round_is_the_fight_as_it_stood_then(table):
    assert fight(table, "fight", "raiders").returncode == 0
    end = rows(table)[-1]["result"]
    got = board(table, "--round", "1")
    assert got.returncode == 0 and f", round 1 of {end['rounds']}\n" in got.stdout
    assert (": the party" not in got.stdout.splitlines()[0]) == (end["rounds"] > 1)
    assert ("▶" in got.stdout) == (end["rounds"] > 1)  # whose turn, mid-fight


def test_the_board_needs_no_dice_only_the_rows(table):
    assert fight(table, "fight", "raiders").returncode == 0
    env = {k: v for k, v in os.environ.items() if k != "ONESCRIPT_HOME"}
    got = subprocess.run([sys.executable, BOX / "fight.py", "--table", table, "board"], capture_output=True, text=True, env=env, check=False)  # fmt: skip
    assert got.returncode == 0 and "The party" in got.stdout


def test_a_board_it_cant_draw_is_refused(table):
    assert board(table).stderr == "play-fight5e: no encounter on the record\n"
    assert fight(table, "fight", "raiders").returncode == 0
    at = next(r["n"] for r in rows(table) if r["kind"] == "encounter-open")
    assert board(table, "--fight", "1").stderr == f"play-fight5e: row 1 doesn't open an encounter; encounters open at rows {at}\n"  # fmt: skip
    assert board(table, "--round", "x").returncode == 2
    assert board(table, "--fight", str(at)).returncode == 0
