"""fight_spike on willow's dice-tower: every face a die dropped (a hash first)
and brought out, every blow a row, and the rows held to the tower afterwards."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fight_spike as fs
import tower_faces as tf

CAST = [
    fs.Fighter(
        "Tamsin", "party", hp=12, ac=14, init_mod=2, attack_bonus=4, damage="1d6+2"
    ),
    fs.Fighter("Oro", "party", hp=9, ac=12, init_mod=0, attack_bonus=3, damage="1d6+1"),
    fs.Fighter(
        "Goblin", "foes", hp=7, ac=13, init_mod=2, attack_bonus=4, damage="1d6+2"
    ),
]


def make(tmp_path: Path) -> Path:
    pile = tmp_path / "pile"
    pile.mkdir(parents=True)
    (pile / "notes.md").write_text("The gremlins hate fire.\n")
    box = tmp_path / "box"
    got = subprocess.run([sys.executable, str(tf.WILLOW / "kernel.py"), "init", "--box", str(box), "--pile", str(pile), "--key", str(tmp_path / "key"), "--now", "2026-11-22T10:00:00Z"], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode == 0, got.stderr
    return box


def play(tmp_path: Path):
    box = make(tmp_path)
    rows = fs.fight(CAST, tf.TowerFaces(box, tmp_path / "dice"))
    return box, rows


def test_a_fight_on_the_tower_ends_and_every_face_is_on_the_record(tmp_path):
    box, rows = play(tmp_path)
    assert rows[-1]["kind"] == "end"
    assert tf.tower_match(box, rows) is None
    rec, _ = tf.kernel.read(box / "record.jsonl")
    drops = [r for r in rec if r["kind"] == "tower-drop"]
    assert len(drops) == len(fs.faces_of(rows)) >= 5
    assert any(
        "Tamsin attacks" in d.get("for", "") for d in drops
    )  # what each die was for


def test_every_die_was_a_hash_on_the_record_before_it_was_out(tmp_path):
    box, _ = play(tmp_path)
    rec, _ = tf.kernel.read(box / "record.jsonl")
    for out in (r for r in rec if r["kind"] == "tower-out"):
        drop = rec[out["drop"]]
        assert drop["kind"] == "tower-drop" and drop["n"] < out["n"]
        assert (
            "secret" not in drop and "faces" not in drop
        )  # only the commitment until it is out


def test_the_rows_replay_on_their_own_faces(tmp_path):
    _, rows = play(tmp_path)
    assert fs.check(CAST, rows) is None


def test_a_face_changed_in_the_rows_no_longer_matches_the_tower(tmp_path):
    box, rows = play(tmp_path)
    edited = [dict(r) for r in rows]
    blow = next(r for r in edited if r["kind"] == "blow")
    blow["d20"] = 1 if blow["d20"] != 1 else 2
    assert "part at face" in tf.tower_match(box, edited)


def test_a_die_left_inside_the_tower_is_named(tmp_path):
    box, rows = play(tmp_path)
    tf.tower.drop(box, "1d20", tmp_path / "spare.json", "a spare", tf.now())
    assert "still in the tower" in tf.tower_match(box, rows)
