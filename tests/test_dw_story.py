"""Story characters and stat blocks as Fighters, and a fight on the record that is read from the record."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "box"))
import dw_fight as fs
import dw_record as rf
import dw_story as sf
import dw_tower as tf
from test_dw_tower import make

LANTERN = json.loads(
    (
        Path(__file__).resolve().parents[1] / "box" / "worlds" / "lantern-fair.json"
    ).read_text()
)


def test_a_character_gets_the_defaults_from_the_stories_own_stats():
    party = {f.name: f for f in sf.party_from_world(LANTERN)}
    assert set(party) == {"Tamsin", "Oro"}  # Old Vell has no seat
    t, o = party["Tamsin"], party["Oro"]  # Tamsin Grit 2 Heart 1; Oro Wit 2
    assert (t.hp, t.ac, t.init_mod, t.attack_bonus, t.damage, t.attacks) == (
        14,
        13,
        0,
        4,
        "1d6+2",
        1,
    )
    assert (o.hp, o.ac, o.init_mod, o.attack_bonus, o.damage) == (12, 13, 2, 2, "1d6")
    assert t.side == o.side == "party"


def test_a_story_that_says_its_hero_has_30_hit_points_gets_30():
    c = {
        "name": "Mira",
        "seat": True,
        "stats": {"Grit": 1},
        "fight": {"hp": 30, "attacks": 2},
    }
    f = sf.from_character(c, ["Grit", "Wit", "Heart"])
    assert (f.hp, f.attacks, f.ac) == (30, 2, 12)


def test_a_fight_key_that_is_not_one_is_refused_not_ignored():
    with pytest.raises(ValueError):
        sf.from_character({"name": "Mira", "fight": {"hit_points": 30}}, ["Grit"])


def test_a_character_with_no_stats_fights_with_the_floor():
    f = sf.from_character({"name": "Pip"}, [])
    assert (f.hp, f.ac, f.init_mod, f.attack_bonus, f.damage) == (8, 11, 0, 2, "1d6")


def test_a_stat_block_becomes_a_fighter_with_its_first_attack_and_multiattack():
    f = sf.from_statblock("aether_construct", "Construct")
    assert (f.name, f.side, f.hp, f.ac, f.init_mod, f.attack_bonus, f.damage, f.attacks) == ("Construct", "foes", 32, 16, 1, 4, "1d8+2", 2)  # fmt: skip
    with pytest.raises(KeyError):
        sf.from_statblock("dragon")


def test_two_blows_a_turn_go_to_the_next_one_standing_and_stop_when_none_is():
    cast = [
        fs.Fighter(
            "A",
            "party",
            hp=20,
            ac=10,
            init_mod=0,
            attack_bonus=5,
            damage="1d6",
            attacks=2,
        ),
        fs.Fighter("B", "foes", hp=1, ac=10, init_mod=0, attack_bonus=0, damage="1d4"),
        fs.Fighter("C", "foes", hp=1, ac=10, init_mod=0, attack_bonus=0, damage="1d4"),
    ]
    # init 20 for A, 1 and 1 for the foes; A: d20 15 hits B (damage 3), d20 15 hits C (damage 3): both down
    rows = fs.fight(cast, [20, 1, 1, 15, 3, 15, 3])
    blows = [r for r in rows if r["kind"] == "blow"]
    assert [(b["who"], b["target"]) for b in blows] == [("A", "B"), ("A", "C")]
    assert rows[-1] == {"kind": "end", "round": 2, "winner": "party"}


def story_fight(tmp_path):
    box = make(tmp_path)
    party = sf.party_from_world(LANTERN)
    foe = sf.from_statblock("scorched_belt_raider", "Raider")
    return box, [*party, foe], rf.record(box, [*party, foe], tmp_path / "dice")


def test_a_fight_on_the_record_checks_from_the_record_alone(tmp_path):
    box, _, rows = story_fight(tmp_path)
    assert rows[-1]["kind"] == "end"
    assert rf.check_record(box) is None
    rec, _ = tf.kernel.read(box / "record.jsonl")
    assert (
        next(r["kind"] for r in rec if r["kind"].startswith("xfight")) == "xfight-open"
    )
    assert not [
        r for r in rec if r["kind"].startswith("fight-")
    ]  # fight.py's kinds are not touched


def test_the_record_names_the_engine_and_the_fighters_whole(tmp_path):
    box, cast, _ = story_fight(tmp_path)
    rec, _ = tf.kernel.read(box / "record.jsonl")
    opened = next(r for r in rec if r["kind"] == rf.OPEN)
    assert opened["engine"] == rf.ENGINE
    assert [f["name"] for f in opened["fighters"]] == [f.name for f in cast]


def test_an_edit_in_the_file_breaks_the_chain(tmp_path):
    box, _, _ = story_fight(tmp_path)
    path = box / "record.jsonl"
    lines = path.read_text().splitlines()
    k = next(
        i for i, ln in enumerate(lines) if '"xfight-row"' in ln and '"hp_after"' in ln
    )
    row = json.loads(lines[k])
    row["row"]["hp_after"] += 5
    broken = lines[:k] + [json.dumps(row)] + lines[k + 1 :]
    path.write_text("\n".join(broken) + "\n")
    assert "chain breaks" in rf.check_record(box)


def test_a_die_left_in_the_tower_is_named_by_the_record_check(tmp_path):
    box, _, _ = story_fight(tmp_path)
    tf.tower.drop(box, "1d20", tmp_path / "spare.json", "a spare", tf.now())
    assert "still in the tower" in rf.check_record(box)


def test_rows_written_honestly_to_the_chain_but_with_a_blow_changed_are_found(tmp_path):
    box, cast, rows = story_fight(tmp_path)
    opened = tf.kernel.append(box, tf.now(), rf.OPEN, who=rf.WHO, engine=rf.ENGINE, fighters=[f.__dict__ for f in cast])  # fmt: skip
    for r in rows:
        r = dict(r)
        if r["kind"] == "blow" and r["hit"]:
            r["damage"] += 1  # a blow that did more than the dice said
        tf.kernel.append(box, tf.now(), rf.ROW, who=rf.WHO, fight=opened["n"], row=r)
    assert rf.check_record(box) is not None  # no tower dice stand behind them
