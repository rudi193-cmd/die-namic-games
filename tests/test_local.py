"""ci/local.py, the fast CI moves for the person working: which tests a change can reach (placed
wide, never narrow), what stands on the last full pass, and which test files the mutants jobs
never run."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
import local


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "t")
    files = {
        "box/session.py": "def s(): pass\n",
        "box/play.py": "import session\n",
        "box/lonely.py": "x = 1\n",
        "tests/test_session.py": "import session\n",
        "tests/test_play.py": "BOX = 'play.py'\n",
        "tests/test_other.py": "def test_nothing(): pass\n",
        "box/worlds/w.json": "{}\n",
        "open.md": "prose\n",
        "ci/mutants.json": json.dumps(
            {"tests": ["tests/test_session.py", "tests/test_play.py"]}
        ),
    }
    for p, text in files.items():
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def planned(repo: Path, *paths: str):
    return local.plan(repo, list(paths))[0]


def test_a_changed_test_file_is_itself(repo):
    assert planned(repo, "tests/test_other.py") == ["tests/test_other.py"]


def test_a_module_is_the_tests_that_name_it_and_those_of_whatever_imports_it(repo):
    assert planned(repo, "box/session.py") == [
        "tests/test_play.py",
        "tests/test_session.py",
    ]


def test_a_module_nothing_imports_is_only_the_tests_that_name_it(repo):
    assert planned(repo, "box/play.py") == ["tests/test_play.py"]


def test_a_module_no_test_names_runs_everything_rather_than_nothing(repo):
    tests, why = local.plan(repo, ["box/lonely.py"])
    assert tests is None and "running everything" in " ".join(why)


def test_what_it_cannot_place_runs_everything(repo):
    for path in (
        "box/worlds/w.json",
        ".github/workflows/ci.yml",
        "willow.pin.json",
        "box/unknown.py",
    ):
        assert planned(repo, path) is None, path


def test_prose_nothing_reads_runs_nothing_and_says_so(repo):
    tests, why = local.plan(repo, ["open.md", "boxes/a/page.md"])
    assert tests == [] and all("nothing reads it" in w for w in why)


def test_one_unplaced_path_among_placed_ones_widens_to_everything(repo):
    assert planned(repo, "box/play.py", "box/worlds/w.json") is None


def test_the_changes_are_what_differs_from_the_base_and_new_files(repo):
    (repo / "box/play.py").write_text("import session\n# edited\n")
    (repo / "tests/test_new.py").write_text("def test_x(): pass\n")
    got = local.changed(repo, "main")
    assert (
        "box/play.py" in got
        and "tests/test_new.py" in got
        and "box/session.py" not in got
    )


def test_the_test_files_the_mutants_jobs_never_run_are_named(repo):
    assert local.unlisted(repo) == ["tests/test_other.py"]


def run_with(repo: Path, monkeypatch, argv: list[str], code: int = 0):
    ran = []
    monkeypatch.setattr(
        local, "pytest", lambda r, files: ran.append(list(files)) or code
    )
    status = local.main(["--repo", str(repo), "run", "--base", "main", *argv])
    return status, ran


def test_a_full_pass_is_kept_and_the_same_bytes_then_stand_without_a_run(
    repo, monkeypatch, capsys
):
    (repo / "box/worlds/w.json").write_text('{"a": 1}\n')  # unplaced: everything
    status, ran = run_with(repo, monkeypatch, [])
    assert (status, ran) == (0, [[]]) and "kept" in capsys.readouterr().out
    status, ran = run_with(repo, monkeypatch, [])
    assert (status, ran) == (0, []) and "stands" in capsys.readouterr().out
    status, ran = run_with(repo, monkeypatch, ["--force"])
    assert ran == [[]]


def test_a_change_to_a_file_a_test_reads_moves_the_key_so_nothing_stands(
    repo, monkeypatch
):
    (repo / "box/worlds/w.json").write_text('{"a": 1}\n')
    run_with(repo, monkeypatch, [])
    (repo / "box/worlds/w.json").write_text('{"a": 2}\n')
    _status, ran = run_with(repo, monkeypatch, [])
    assert ran == [[]]


def test_a_partial_run_that_passes_keeps_nothing(repo, monkeypatch):
    (repo / "tests/test_other.py").write_text("def test_nothing(): assert True\n")
    run_with(repo, monkeypatch, [])
    _status, ran = run_with(repo, monkeypatch, [])
    assert ran == [["tests/test_other.py"]]  # not kept, so it ran again


def test_a_failing_run_exits_one_and_keeps_nothing(repo, monkeypatch):
    (repo / "box/worlds/w.json").write_text('{"a": 1}\n')
    status, _ = run_with(repo, monkeypatch, [], code=1)
    assert status == 1
    _status, ran = run_with(repo, monkeypatch, [])
    assert ran == [[]]


def test_a_change_only_in_prose_runs_nothing(repo, monkeypatch, capsys):
    (repo / "open.md").write_text("more prose\n")
    status, ran = run_with(repo, monkeypatch, [])
    assert (status, ran) == (0, []) and "read by no test" in capsys.readouterr().out


def test_needs_names_what_this_machine_may_lack():
    names = [t for t, _here, _cost in local.needs(ROOT)]
    assert names == ["willow at the pin", "ONESCRIPT_HOME (willow-bot's one-script)", "dndwright", "ruff", "tesseract"]  # fmt: skip
