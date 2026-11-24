"""Story characters and stat blocks as fighters for willow's play-fight, each one a fighter
play-fight takes as it is. The fight itself, and its check, are play-fight's own tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "box"))
import dw_story as sf
import willow_pin

LANTERN = json.loads(
    (
        Path(__file__).resolve().parents[1] / "box" / "worlds" / "lantern-fair.json"
    ).read_text()
)


def test_a_character_gets_the_defaults_from_the_stories_own_stats():
    party = {f["name"]: f for f in sf.party_from_world(LANTERN)}
    assert set(party) == {"Tamsin", "Oro"}  # Old Vell has no seat
    t, o = party["Tamsin"], party["Oro"]  # Tamsin Grit 2 Heart 1; Oro Wit 2
    assert (
        t["hp"],
        t["ac"],
        t["init_mod"],
        t["attack_bonus"],
        t["damage"],
        t["attacks"],
    ) == (
        14,
        13,
        0,
        4,
        "1d6+2",
        1,
    )
    assert (o["hp"], o["ac"], o["init_mod"], o["attack_bonus"], o["damage"]) == (
        12,
        13,
        2,
        2,
        "1d6",
    )
    assert t["side"] == o["side"] == "party"


def test_a_story_that_says_its_hero_has_30_hit_points_gets_30():
    c = {
        "name": "Mira",
        "seat": True,
        "stats": {"Grit": 1},
        "fight": {"hp": 30, "attacks": 2},
    }
    f = sf.from_character(c, ["Grit", "Wit", "Heart"])
    assert (f["hp"], f["attacks"], f["ac"]) == (30, 2, 12)


def test_a_fight_key_that_is_not_one_is_refused_not_ignored():
    with pytest.raises(ValueError):
        sf.from_character({"name": "Mira", "fight": {"hit_points": 30}}, ["Grit"])


def test_a_character_with_no_stats_fights_with_the_floor():
    f = sf.from_character({"name": "Pip"}, [])
    assert (f["hp"], f["ac"], f["init_mod"], f["attack_bonus"], f["damage"]) == (
        8,
        11,
        0,
        2,
        "1d6",
    )


def test_a_stat_block_becomes_a_fighter_with_its_first_attack_and_multiattack():
    f = sf.from_statblock("aether_construct", "Construct")
    assert (f['name'], f['side'], f['hp'], f['ac'], f['init_mod'], f['attack_bonus'], f['damage'], f['attacks']) == ("Construct", "foes", 32, 16, 1, 4, "1d8+2", 2)  # fmt: skip
    with pytest.raises(KeyError):
        sf.from_statblock("dragon")


def test_the_fighters_made_here_are_ones_play_fight_takes():
    spec = importlib.util.spec_from_file_location("play_fight", willow_pin.root() / "adapters" / "deps" / "play-fight" / "play_fight.py")  # fmt: skip
    pf = importlib.util.module_from_spec(spec)
    sys.modules["play_fight"] = pf
    spec.loader.exec_module(pf)
    cast = [*sf.party_from_world(LANTERN), sf.from_statblock("scorched_belt_raider", "Raider")]  # fmt: skip
    assert [f.name for f in pf.fighters_from(cast)] == ["Tamsin", "Oro", "Raider"]
