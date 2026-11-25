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
    old, new = willow_pin.pin(), json.loads(at.read_text())
    head = willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()
    counts = f"{len(old['add_ons'])} add-ons, {len(old['files'])} files"
    assert (
        code == 0 and said == f"pinned willow {head[:12]}, {counts}"
    )  # moved, no file
    assert new["files"] == old["files"] and new["add_ons"] == old["add_ons"]
    assert list(new) == list(old) and new["commit"] == head != old["commit"]
    assert at.read_text() == json.dumps(new, indent=2, ensure_ascii=False) + "\n"
    code, said = willow_pin.repin(w, at=at)  # again: the same commit, the same bytes
    assert code == 0 and said == f"pinned willow {head[:12]}, {counts}; nothing moved"


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
    head = willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()
    before = at.read_text()
    cases = [
        (tmp_path / "nowhere", {}, "isn't a willow git checkout"),
        (w, {"add": ["no-such"]}, f"refused: willow {head[:12]} has no add-on no-such"),
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
    willow_pin.git(w, "rm", "-qf", "kernel.py")
    gone = commit(w)
    assert willow_pin.repin(w, at=at) == (
        2,
        f"refused: no kernel.py in willow {gone[:12]}",
    )
    assert at.read_text() == before


def test_a_file_in_a_folder_the_pin_never_held_goes_at_the_end():
    old = ["kernel.py", "adapters/stdlib/a/a.py", "adapters/stdlib/b/b.py"]
    new = ["adapters/stdlib/c/c.py", *old]
    assert willow_pin.in_order(old, new) == [*old, "adapters/stdlib/c/c.py"]


def test_with_no_willow_anywhere_the_first_place_looked_is_named(monkeypatch, tmp_path):
    places = [tmp_path / "first", tmp_path / "second"]
    monkeypatch.setattr(willow_pin, "candidates", lambda: places)
    assert willow_pin.first_willow() == places[0]
    (places[1] / "kernel.py").parent.mkdir()
    (places[1] / "kernel.py").write_text("")
    assert willow_pin.first_willow() == places[1]


def test_the_command_line_repins_with_add_and_drop(tmp_path, monkeypatch, capsys):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    new = w.joinpath("adapters", "stdlib", "new-one")
    new.mkdir()
    new.joinpath("new_one.py").write_text("x = 1\n")
    commit(w)
    monkeypatch.setattr(willow_pin, "PIN", at)
    argv = ["repin", "--willow", str(w), "--add", "new-one", "--drop", "play-dice"]
    assert willow_pin.main(argv) == 0
    pinned = json.loads(at.read_text())
    assert "new-one" in pinned["add_ons"] and "play-dice" not in pinned["add_ons"]
    assert "added: adapters/stdlib/new-one/new_one.py" in capsys.readouterr().out


def test_the_command_line(tmp_path, monkeypatch):
    script = [sys.executable, str(HERE / "willow_pin.py")]
    for bad in ([], ["move"], ["check", "--add", "x"], ["repin", "--willow"], ["repin", "--add"],
                ["repin", "--at"], ["check", "--at", "x"], ["follow", "a", "b"], ["follow", "--x"], ["prune", "x"], ["prune", "--days"]):  # fmt: skip
        got = subprocess.run(script + bad, capture_output=True, text=True, check=False)
        assert got.returncode == 2 and "willow_pin.py repin" in got.stderr, bad
    got = subprocess.run(script + ["check", "--willow", str(REAL)], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode == 0
    assert (
        got.stdout
        == f"{REAL} is the pinned willow, {willow_pin.pin()['commit'][:12]}\n"
    )
    got = subprocess.run(script + ["check", "--willow", str(tmp_path)], capture_output=True, text=True, check=False)  # fmt: skip
    short = willow_pin.pin()["commit"][:12]
    assert got.returncode == 1
    assert (
        got.stdout
        == f"{tmp_path} isn't the pinned willow ({short}):\n  no willow there\n"
    )


# ── the copy of the pinned commit, and follow ──────────────────────────────
def test_the_box_runs_the_pinned_commit_whatever_the_checkout_is_on(alone, monkeypatch):  # fmt: skip
    w = git_willow(alone / "w")
    pinned = willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()
    at = a_pin(alone)
    monkeypatch.setattr(willow_pin, "PIN", at)
    assert willow_pin.repin(w, at=at)[0] == 0
    (w / "kernel.py").write_text("# a newer kernel\n")
    commit(w)  # the checkout moves on; the pin stays
    (w / "adapters/stdlib/play-dice/play_dice.py").write_text("# mid-change\n")
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    got = willow_pin.root()
    assert got == w / ".git/willow-pinned" / pinned and (got / willow_pin.DONE).is_file()  # fmt: skip
    assert not willow_pin.drift(got, willow_pin.pin())
    other = alone / "other-worktree"
    assert willow_pin.git(w, "worktree", "add", "-q", "--detach", str(other)).returncode == 0  # fmt: skip
    monkeypatch.setenv("WILLOW_ROOT", str(other))
    assert willow_pin.root() == got  # every checkout of that git shares it


def test_a_commit_its_git_lacks_makes_no_copy(tmp_path):
    w = git_willow(tmp_path / "w")
    assert willow_pin.pinned_copy(w, "0" * 40) is None
    assert willow_pin.pinned_copy(tmp_path, "0" * 40) is None  # not git at all


def test_repin_at_a_commit_reads_git_not_the_checkout(tmp_path):
    at, w = a_pin(tmp_path), git_willow(tmp_path / "w")
    first = willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()
    (w / "kernel.py").write_text("# a newer kernel\n")
    commit(w)
    (w / "kernel.py").write_text("# changed, not committed\n")
    code, said = willow_pin.repin(w, at=at, rev=first)
    assert code == 0, said
    pinned = json.loads(at.read_text())
    assert pinned["commit"] == first and pinned["files"] == willow_pin.pin()["files"]
    code, said = willow_pin.repin(w, at=at, rev="no-such-branch")
    assert (code, said) == (2, f"refused: willow's git at {w} has no commit no-such-branch")  # fmt: skip


@pytest.mark.parametrize("passes", [True, False])
def test_follow_commits_the_pin_only_when_the_check_passes(alone, monkeypatch, passes):
    w = git_willow(alone / "w")
    repo = alone / "repo"
    repo.mkdir()
    at = a_pin(repo)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "p"], ["config", "user.name", "t"], ["config", "user.email", "t@t"]):  # fmt: skip
        assert willow_pin.git(repo, *args).returncode == 0
    (w / "kernel.py").write_text("# a newer kernel\n")
    new = commit(w)
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    monkeypatch.setattr(willow_pin, "CHECK", [sys.executable, "-c", f"raise SystemExit({int(not passes)})"])  # fmt: skip
    before, was = willow_pin.git(repo, "rev-parse", "HEAD").stdout, at.read_bytes()
    code, said = willow_pin.follow("HEAD", at=at)
    after = willow_pin.git(repo, "rev-parse", "HEAD").stdout
    if passes:
        assert code == 0 and said.endswith("the check passed; committed, not pushed"), (
            said
        )
        assert json.loads(at.read_text())["commit"] == new and after != before
        assert willow_pin.git(repo, "status", "--porcelain").stdout == ""
        assert willow_pin.follow("HEAD", at=at) == (0, f"the pin is on willow {new[:12]} already: nothing moved")  # fmt: skip
    else:
        assert (
            code == 1 and "the check didn't pass, so the pin is back as it was" in said
        )
        assert at.read_bytes() == was and after == before


def a_repo_to_pin(alone: Path) -> tuple[Path, Path]:
    """A Die-Namic repo of its own with a pin committed, that names itself."""
    repo = alone / "repo"
    repo.mkdir()
    at = a_pin(repo)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t"], ["add", "-A"], ["commit", "-qm", "p"]):  # fmt: skip
        assert willow_pin.git(repo, *args).returncode == 0
    return repo, at


def test_follow_by_its_command_line_pins_the_commit_named(alone, monkeypatch, capsys):  # fmt: skip
    w = git_willow(alone / "w")
    repo, at = a_repo_to_pin(alone)
    (w / "kernel.py").write_text("# a newer kernel\n")
    named = commit(w)
    (w / "kernel.py").write_text("# newer still\n")
    commit(w)  # HEAD, and what follow would take with no commit named
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    monkeypatch.setattr(willow_pin, "PIN", at)
    monkeypatch.setattr(willow_pin, "CHECK", [sys.executable, "-c", "pass"])
    assert willow_pin.main(["follow", named]) == 0
    said = capsys.readouterr().out
    assert json.loads(at.read_text())["commit"] == named
    body = willow_pin.git(repo, "log", "-1", "--format=%B").stdout
    assert body.startswith(f"Pin willow {named[:12]}\n\n")
    assert said.splitlines()[1] in body  # what moved, from its first line


def test_follow_says_so_when_the_check_passed_but_the_commit_didnt(alone, monkeypatch):  # fmt: skip
    w = git_willow(alone / "w")
    repo, at = a_repo_to_pin(alone)
    hook = repo / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    (w / "kernel.py").write_text("# a newer kernel\n")
    commit(w)
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    monkeypatch.setattr(willow_pin, "CHECK", [sys.executable, "-c", "pass"])
    code, said = willow_pin.follow("HEAD", at=at)
    assert code == 1 and "the check passed, but the commit didn't" in said, said


def test_check_with_no_willow_found_says_why_and_fails(alone, monkeypatch, capsys):  # fmt: skip
    monkeypatch.setenv("WILLOW_ROOT", str(alone / "nowhere"))
    assert willow_pin.main(["check"]) == 1
    assert capsys.readouterr().out.strip()  # why: no willow where it looked


def test_prune_by_its_command_line_takes_its_days(alone, monkeypatch, capsys):
    import os
    import time

    w = git_willow(alone / "w")
    monkeypatch.setenv("WILLOW_ROOT", str(w))
    assert willow_pin.prune(w, keep="") == []  # no copy made yet
    assert willow_pin.prune(alone, keep="") == []  # not git at all
    old = willow_pin.pinned_copy(w, willow_pin.git(w, "rev-parse", "HEAD").stdout.strip())  # fmt: skip
    days3 = time.time() - 3 * willow_pin.DAY
    os.utime(old / willow_pin.DONE, (days3, days3))
    assert willow_pin.main(["prune"]) == 0 and old.is_dir()  # 14 days by default
    assert willow_pin.main(["prune", "--days", "2"]) == 0 and not old.exists()
    assert capsys.readouterr().out.endswith(f"let go of 1 copy\n  {old.name}\n")


def test_prune_lets_go_of_old_copies_but_this_pins(tmp_path):
    import os
    import time

    w = git_willow(tmp_path / "w")
    first = willow_pin.git(w, "rev-parse", "HEAD").stdout.strip()
    (w / "kernel.py").write_text("# a newer kernel\n")
    second = commit(w)
    old, new = willow_pin.pinned_copy(w, first), willow_pin.pinned_copy(w, second)
    month = time.time() - 30 * willow_pin.DAY
    for at in (old, new):
        os.utime(at / willow_pin.DONE, (month, month))
    assert willow_pin.prune(w, keep=second) == [first]
    assert not old.exists() and new.is_dir()
    assert willow_pin.prune(w, keep="", days=60) == []  # not old enough
    assert willow_pin.pinned_copy(w, first) == old and old.is_dir()  # made again
    os.utime(old / willow_pin.DONE, (month, month))
    willow_pin.pinned_copy(w, first)  # run: marked as used today
    assert willow_pin.prune(w, keep=second) == []


def test_only_a_pinned_add_on_is_loaded_and_only_once():
    with pytest.raises(
        willow_pin.Unpinned, match="no-such isn't an add-on willow.pin.json pins"
    ):
        willow_pin.script("no-such")
    assert willow_pin.addon("story-ideas") is willow_pin.addon("story-ideas")
