"""The pin: the box runs on willow where its pieces live, and only on a willow
whose files are the pinned bytes."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "box"  # the box these tests test
sys.path.insert(0, str(HERE))
import willow_pin

REAL = willow_pin.root()  # found once, before any test hides it


def test_the_willow_beside_the_store_is_the_pinned_one():
    root = willow_pin.root()
    assert (root / "kernel.py").is_file() and not willow_pin.drift(
        root, willow_pin.pin()
    )


def test_every_add_on_the_box_plays_with_is_pinned():
    pinned = willow_pin.pin()
    folders = {p.split("/")[2] for p in pinned["files"] if p.startswith("adapters/")}
    assert set(pinned["add_ons"]) <= folders
    assert "kernel.py" in pinned["files"]


@pytest.fixture
def alone(tmp_path, monkeypatch):
    """A repo with no willow beside it: only WILLOW_ROOT is looked at."""
    monkeypatch.setattr(willow_pin, "REPO", tmp_path / "repo")
    return tmp_path


def copy_of_willow(to: Path) -> Path:
    real = REAL
    for rel in willow_pin.pin()["files"]:
        (to / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(real / rel, to / rel)
    return to


def test_a_willow_with_a_changed_file_is_refused_by_name(alone, monkeypatch):
    w = copy_of_willow(alone / "w")
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    assert willow_pin.root() == w
    with open(w / "adapters" / "stdlib" / "play-dice" / "play_dice.py", "a") as f:
        f.write("# changed\n")
    with pytest.raises(
        willow_pin.Unpinned, match="adapters/stdlib/play-dice/play_dice.py differs"
    ):
        willow_pin.root()


def test_a_willow_missing_a_file_or_none_at_all_is_refused(alone, monkeypatch):
    w = copy_of_willow(alone / "w")
    (w / "adapters" / "stdlib" / "play-odds" / "play_odds.py").unlink()
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    with pytest.raises(willow_pin.Unpinned, match="play_odds.py is missing"):
        willow_pin.root()
    monkeypatch.delenv("WILLOW_ROOT")
    with pytest.raises(willow_pin.Unpinned, match="no willow there"):
        willow_pin.root()


def test_a_refusal_names_the_pinned_commit_by_its_first_twelve(alone, monkeypatch):
    commit = willow_pin.pin()["commit"]
    w = copy_of_willow(alone / "w")
    (w / "kernel.py").write_text("# not the pinned kernel\n")
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    with pytest.raises(willow_pin.Unpinned) as got:
        willow_pin.root()
    said = str(got.value)
    assert (
        f"(willow {commit[:12]});" in said and f"off the pin at {commit[:12]}," in said
    )


# ── repin: the one way to move the pin ──────────────────────────────────────
def git_willow(to: Path) -> Path:
    """A copy of the pinned willow, made a git repository of its own."""
    w = copy_of_willow(to)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "w"]):  # fmt: skip
        assert willow_pin.git(w, *args).returncode == 0
    return w


def commit(w: Path) -> str:
    willow_pin.git(w, "add", "-A")
    willow_pin.git(
        w, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "more"
    )
    return willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()


def a_pin(tmp: Path) -> Path:
    at = tmp / "willow.pin.json"
    shutil.copy(willow_pin.PIN, at)
    return at


def test_repin_at_the_pinned_bytes_changes_nothing_but_the_commit(tmp_path):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    code, said = willow_pin.repin(w, at=at)
    assert code == 0 and said.startswith("pinned willow ") and "\n" not in said
    old, new = willow_pin.pin(), json.loads(at.read_text())
    assert new["files"] == old["files"] and new["add_ons"] == old["add_ons"]
    assert list(new) == list(old) and new["commit"] != old["commit"]


def test_a_new_file_in_a_pinned_add_on_comes_in_and_its_tests_do_not(tmp_path):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    dice = w.joinpath("adapters", "stdlib", "play-dice")
    dice.joinpath("faces.txt").write_text("1 2 3 4 5 6\n")
    dice.joinpath("test_more.py").write_text("")
    dice.joinpath("play_dice.py").write_text("# moved on\n")
    head = commit(w)
    code, said = willow_pin.repin(w, at=at)
    assert code == 0, said
    assert "added: adapters/stdlib/play-dice/faces.txt" in said
    assert "changed: adapters/stdlib/play-dice/play_dice.py" in said
    pinned = json.loads(at.read_text())
    assert pinned["commit"] == head and "adapters/stdlib/play-dice/test_more.py" not in pinned["files"]  # fmt: skip
    names = list(pinned["files"])
    at_new = names.index("adapters/stdlib/play-dice/faces.txt")
    assert names[at_new - 1].startswith("adapters/stdlib/play-dice/")  # beside its own


def test_add_and_drop_name_an_add_on_and_say_what_moved(tmp_path):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    new = w.joinpath("adapters", "stdlib", "new-one")
    new.mkdir()
    new.joinpath("new_one.py").write_text("x = 1\n")
    new.joinpath("README.md").write_text("# new-one\n")
    commit(w)
    code, said = willow_pin.repin(w, add=["new-one"], drop=["play-dice"], at=at)
    assert code == 0, said
    pinned = json.loads(at.read_text())
    assert "new-one" in pinned["add_ons"] and "play-dice" not in pinned["add_ons"]
    i = pinned["add_ons"].index("new-one")
    assert (
        pinned["add_ons"][i + 1] > "new-one" > pinned["add_ons"][i - 1]
    )  # in its place
    assert "added: adapters/stdlib/new-one/new_one.py" in said
    assert "gone: adapters/stdlib/play-dice/play_dice.py" in said


def test_repin_refuses_and_leaves_the_pin_as_it_was(tmp_path):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    before = at.read_text()
    cases = [
        (tmp_path / "nowhere", {}, "isn't a willow git checkout"),
        (w, {"add": ["no-such"]}, "has no add-on no-such"),
        (w, {"drop": ["no-such"]}, "no-such isn't an add-on the pin names"),
    ]
    (tmp_path / "nowhere").mkdir()
    for where, more, why in cases:
        code, said = willow_pin.repin(where, at=at, **more)
        assert code == 2 and why in said, said
    dice = w.joinpath("adapters", "stdlib", "play-dice")
    dice.joinpath("test_later.py").write_text("")  # a test: never pinned
    other = tmp_path / "other"
    other.mkdir()
    assert willow_pin.repin(w, at=a_pin(other))[0] == 0
    dice.joinpath("new.py").write_text("")  # in a pinned folder, not committed
    code, said = willow_pin.repin(w, at=at)
    assert code == 2 and "adapters/stdlib/play-dice/new.py" in said, said
    dice.joinpath("new.py").unlink()
    w.joinpath("kernel.py").write_text("# changed, not committed\n")
    code, said = willow_pin.repin(w, at=at)
    assert code == 2 and "changes not committed in pinned files" in said and "kernel.py" in said  # fmt: skip
    assert at.read_text() == before


def test_the_command_line(tmp_path, monkeypatch):
    script = [sys.executable, str(HERE / "willow_pin.py")]
    for bad in ([], ["move"], ["check", "--add", "x"], ["repin", "--willow"], ["repin", "--add"]):  # fmt: skip
        got = subprocess.run(script + bad, capture_output=True, text=True, check=False)
        assert got.returncode == 2 and "willow_pin.py repin" in got.stderr, bad
    got = subprocess.run(script + ["check", "--willow", str(REAL)], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode == 0 and "is the pinned willow" in got.stdout
    got = subprocess.run(script + ["check", "--willow", str(tmp_path)], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode == 1 and "no willow there" in got.stdout
