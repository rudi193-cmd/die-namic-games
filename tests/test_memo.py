"""ci/memo.py: a key is the bytes a verdict can reach, drawn wide: the same files give the same
key; a change to anything reached moves it; a change to what nothing reads doesn't; and no code
names what it leaves out."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
import memo


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    for p, text in {
        "box/play.py": "print('play')\n",
        "tests/test_play.py": "def test_x(): pass\n",
        "README.md": "readme\n",
        "open.md": "the design\n",
        "boxes/one/page.md": "a page\n",
        "boxes/MEMORY.md": "memory\n",
        "ci/README.md": "ci\n",
    }.items():
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    git(tmp_path, "add", ".")
    return tmp_path


def test_the_same_files_give_the_same_key_and_it_is_a_sha256(repo):
    k = memo.key(repo, "mutants:box/play.py")
    assert re.fullmatch(r"[0-9a-f]{64}", k) and k == memo.key(
        repo, "mutants:box/play.py"
    )


@pytest.mark.parametrize("path", ["box/play.py", "tests/test_play.py", "README.md"])
def test_a_change_to_anything_reached_moves_the_key(repo, path):
    before = memo.key(repo)
    (repo / path).write_text("changed\n")
    assert memo.key(repo) != before


@pytest.mark.parametrize(
    "path", ["open.md", "boxes/one/page.md", "boxes/MEMORY.md", "ci/README.md"]
)
def test_a_change_to_what_nothing_reads_leaves_the_key_alone(repo, path):
    before = memo.key(repo)
    (repo / path).write_text("changed\n")
    assert memo.key(repo) == before


def test_a_new_tracked_file_and_a_removed_one_move_the_key(repo):
    before = memo.key(repo)
    (repo / "box/new.py").write_text("x = 1\n")
    git(repo, "add", "box/new.py")
    added = memo.key(repo)
    assert added != before
    git(repo, "rm", "-q", "-f", "box/new.py")
    assert memo.key(repo) == before


def test_a_new_file_in_what_is_left_out_changes_nothing(repo):
    before = memo.key(repo)
    (repo / "boxes/two").mkdir()
    (repo / "boxes/two/page.md").write_text("more\n")
    git(repo, "add", ".")
    assert memo.key(repo) == before


def test_an_untracked_file_is_not_in_the_key(repo):
    before = memo.key(repo)
    (repo / "scratch.py").write_text("x = 1\n")
    assert memo.key(repo) == before


def test_the_gate_the_extras_and_the_version_are_in_the_key(repo, monkeypatch):
    base = memo.key(repo, "tests")
    assert memo.key(repo, "mutants:x") != base
    assert memo.key(repo, "tests", ("python=3.12",)) != base
    assert memo.key(repo, "tests", ("a=1", "b=2")) == memo.key(
        repo, "tests", ("b=2", "a=1")
    )  # their order isn't
    monkeypatch.setattr(memo, "VERSION", "memo/2")
    assert memo.key(repo, "tests") != base


def test_a_path_is_in_the_key_not_just_its_bytes(repo):
    before = memo.key(repo)
    git(repo, "mv", "box/play.py", "box/play2.py")
    assert memo.key(repo) != before


def test_reach_is_every_tracked_file_but_the_left_out(repo):
    assert memo.reach(repo) == ["README.md", "box/play.py", "tests/test_play.py"]


def test_a_folder_is_left_out_by_its_slash_and_a_file_that_only_starts_like_it_is_not(
    repo,
):
    assert (
        memo.excluded("boxes/a/b.md")
        and not memo.excluded("boxes.py")
        and not memo.excluded("xboxes/a")
    )
    assert (
        memo.excluded("open.md")
        and not memo.excluded("open.md.bak")
        and not memo.excluded("docs/open.md")
    )


def test_the_command_line_prints_the_key_and_says_why_a_path_is_or_isnt_in_it(repo):
    run = lambda *a: subprocess.run(
        [sys.executable, str(ROOT / "ci" / "memo.py"), *a, "--repo", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )
    got = run("key", "--gate", "tests", "--extra", "python=3.12")
    assert got.returncode == 0 and got.stdout.strip() == memo.key(
        repo, "tests", ("python=3.12",)
    )
    assert "left out of every key" in run("why", "open.md").stdout
    assert "in every key" in run("why", "box/play.py").stdout
    assert "not tracked" in run("why", "nope.py").stdout


def test_a_folder_that_is_not_a_checkout_is_refused(tmp_path):
    got = subprocess.run([sys.executable, str(ROOT / "ci" / "memo.py"), "key", "--repo", str(tmp_path)], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode != 0 and "not a git checkout" in (got.stderr + got.stdout)


def test_no_code_in_this_repo_names_a_file_the_keys_leave_out():
    """The guard that holds the reach: a path left out is one nothing reads. A string in the code
    (not a docstring) that IS such a path, or a path under boxes/, would put the claim in doubt."""
    named = []
    for p in memo.tracked(ROOT):
        if (
            not p.endswith(".py")
            or p in ("ci/memo.py", "tests/test_memo.py")
            or p.startswith("boxes/")
        ):
            continue
        try:
            tree = ast.parse((ROOT / p).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            continue
        docs = {id(n.body[0].value) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}  # fmt: skip
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs and re.fullmatch(r"(boxes/\S*|boxes|open\.md|open-gaps-from-the-boxes\.md|ci/README\.md)", n.value.strip()):  # fmt: skip
                named.append(f"{p}:{n.lineno} {n.value!r}")
    assert named == [], named
