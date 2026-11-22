"""local.py: the fast CI moves, for the person working. Python 3.9+, stdlib only.

    python ci/local.py needs                     what this machine can't run, before a change
    python ci/local.py plan [--base REF]         which tests a change can reach
    python ci/local.py run  [--base REF] [--all] [--force]
    python ci/local.py lists                     test files the mutants jobs never run

The full suite takes minutes and CI's mutants jobs many more, and most changes
reach a few tests. So:

  needs   says what is missing (willow beside this repo, willow-bot's one-script,
          dndwright, ruff, tesseract) and which tests that costs, in a second, so a
          missing tool isn't taken for a failure of yours.
  plan    reads what changed (since REF's merge-base, default origin/main, plus
          the working tree and new files) and says the tests that can reach it:
          a test file is itself; a module of box/, die_namic/, games/ or ci/ is
          the tests that name it, and those of every module that imports it. A
          change it can't place (a world file, a workflow, a pin, anything
          outside those) runs everything: wide, never narrow. Prose nothing reads
          (ci/memo.py's EXCLUDED) runs nothing.
  run     runs the planned tests (pytest, stopping at the first failure); a full
          run that passes is kept, keyed on ci/memo.py's key of every file a test
          can reach. The next `run` on the same bytes says it stands, and runs
          nothing: --force runs anyway. --all runs everything.
  lists   the test files mutants.json doesn't name that name a file it breaks.
          The mutants jobs run only the files it lists, so a break only such a
          file's tests would catch survives in CI: this is how that was found.

This decides nothing CI decides: CI still runs the full suite, and every mutants
job, on main's commit. A stand here is this machine's own last full pass.

Exit codes: 0 done and every test passed; 1 a test failed; 2 refused.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import memo

CODE_DIRS = ("box", "die_namic", "games", "ci")


def git(repo: Path, *args: str) -> str:
    got = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    return got.stdout if got.returncode == 0 else ""


def changed(repo: Path, base: str = "origin/main") -> list[str]:
    """Paths that differ from where this branch left BASE, as the working tree has them, and new files."""
    mb = (
        git(repo, "merge-base", "HEAD", base).strip()
        or git(repo, "merge-base", "HEAD", "main").strip()
    )
    out = set()
    if mb:
        out |= set(git(repo, "diff", "--name-only", mb).split("\n"))
    out |= set(git(repo, "diff", "--name-only", "HEAD").split("\n"))
    out |= set(git(repo, "ls-files", "-o", "--exclude-standard").split("\n"))
    return sorted(p for p in out if p)


def test_files(repo: Path) -> list[str]:
    return sorted(
        p.relative_to(repo).as_posix() for p in (repo / "tests").glob("test_*.py")
    )


def modules(repo: Path) -> dict[str, list[str]]:
    """stem -> the code files of that name, in the folders the tests reach by name."""
    out: dict[str, list[str]] = {}
    for d in CODE_DIRS:
        for p in sorted((repo / d).glob("*.py")) if (repo / d).is_dir() else []:
            out.setdefault(p.stem, []).append(p.relative_to(repo).as_posix())
    return out


def imports(repo: Path, path: str) -> set[str]:
    try:
        tree = ast.parse((repo / path).read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module.split(".")[0])
    return out


def names(text: str, stem: str) -> bool:
    """Does a test's source name this module: imported, or its file run, or quoted."""
    return bool(
        re.search(
            rf"\bimport {stem}\b|\bfrom {stem}\b|\b{stem}\.py\b|[\"']{stem}[\"']", text
        )
    )


def uses(text: str, stem: str) -> bool:
    """Stricter than `names`, read from the syntax and not the strings: the test imports the module,
    or runs its file as a path join (BOX / "play.py"). A fixture that merely says so doesn't count."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(
            a.name.split(".")[0] == stem for a in n.names
        ):
            return True
        if (
            isinstance(n, ast.ImportFrom)
            and n.level == 0
            and (n.module or "").split(".")[0] == stem
        ):
            return True
        if (
            isinstance(n, ast.BinOp)
            and isinstance(n.op, ast.Div)
            and isinstance(n.right, ast.Constant)
            and n.right.value == f"{stem}.py"
        ):
            return True
    return False


def plan(repo: Path, paths: list[str]) -> tuple[list[str] | None, list[str]]:
    """(the tests that can reach PATHS, or None for everything; one line for each path saying why)."""
    tests = test_files(repo)
    mods = modules(repo)
    importers: dict[str, set[str]] = {}
    for stem, files in mods.items():
        for f in files:
            for imp in imports(repo, f):
                if imp in mods and imp != stem:
                    importers.setdefault(imp, set()).add(stem)
    texts = {t: (repo / t).read_text(encoding="utf-8", errors="replace") for t in tests}
    run: set[str] = set()
    why: list[str] = []
    for p in paths:
        top = p.split("/")[0]
        if memo.excluded(p):
            why.append(f"{p}: nothing reads it")
        elif p in tests:
            run.add(p)
            why.append(f"{p}: itself")
        elif (
            p.endswith(".py")
            and top in CODE_DIRS
            and (repo / p).parent == repo / top
            and (repo / p).stem in mods
        ):
            stem = Path(p).stem
            reach, todo = {stem}, [stem]
            while todo:
                for up in importers.get(todo.pop(), ()):
                    if up not in reach:
                        reach.add(up)
                        todo.append(up)
            hit = {t for t, text in texts.items() if any(names(text, s) for s in reach)}
            run |= hit
            why.append(
                f"{p}: {len(hit)} test file(s) name {stem}"
                + (
                    f" or what imports it ({', '.join(sorted(reach - {stem}))})"
                    if len(reach) > 1
                    else ""
                )
            )
            if not hit:
                why.append(f"{p}: no test names it, so running everything")
                return None, why
        else:
            why.append(f"{p}: couldn't place it, so running everything")
            return None, why
    return sorted(run), why


def needs(repo: Path) -> list[tuple[str, bool, str]]:
    """(thing, here, what it costs if it isn't)."""
    sys.path.insert(0, str(repo / "box"))
    try:
        import willow_pin

        willow = Path(willow_pin.root())
        got = (True, str(willow))
    except SystemExit as e:
        got = (False, str(e))
    except Exception as e:  # noqa: BLE001  (the pin refusing is a finding, not a crash)
        got = (False, str(e))
    onescript = os.environ.get("ONESCRIPT_HOME")
    return [
        (
            "willow at the pin",
            got[0],
            "every test that plays a game, which is nearly all: " + got[1]
            if not got[0]
            else got[1],
        ),
        (
            "ONESCRIPT_HOME (willow-bot's one-script)",
            bool(onescript and Path(onescript).is_dir()),
            "the fights: tests/test_fight.py and the tests that start one (test_table_turn, test_write)",
        ),
        (
            "dndwright",
            importlib.util.find_spec("dndwright") is not None,
            "the story's own fights: tests/test_dw_*.py (box/requirements-dndwright.txt)",
        ),
        (
            "ruff",
            importlib.util.find_spec("ruff") is not None
            or shutil.which("ruff") is not None,
            "the lint check",
        ),
        (
            "tesseract",
            shutil.which("tesseract") is not None,
            "the end-of-night test that reads a handwritten page",
        ),
    ]


def unlisted(repo: Path) -> list[str]:
    """Test files mutants.json doesn't list that name a file it breaks: the mutants jobs never run
    them, so a break only they would catch survives. Files that test code nothing breaks (ci/, the
    exhaustion rule, the dw_ modules) are not named: nothing is lost by their not being run there."""
    cfg = json.loads((repo / "ci" / "mutants.json").read_text())
    listed = set(cfg["tests"])
    stems = {Path(t).stem for t in cfg["targets"]}
    out = []
    for t in test_files(repo):
        if t in listed:
            continue
        text = (repo / t).read_text(encoding="utf-8", errors="replace")
        if any(uses(text, stem) for stem in stems):
            out.append(t)
    return out


def store(repo: Path) -> Path:
    got = git(repo, "rev-parse", "--git-dir").strip()
    d = Path(got) if os.path.isabs(got) else repo / got
    return d / "die-namic-verdicts"


def current_key(repo: Path) -> str:
    extras = [
        f"python={sys.version_info.major}.{sys.version_info.minor}",
        f"onescript={'yes' if os.environ.get('ONESCRIPT_HOME') else 'no'}",
        f"dndwright={'yes' if importlib.util.find_spec('dndwright') else 'no'}",
    ]
    return memo.key(repo, "tests:local", tuple(extras))


def pytest(repo: Path, files: list[str]) -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x", *files], cwd=repo, check=False
    ).returncode


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="local.py", description="the fast CI moves, for the person working"
    )
    ap.add_argument("--repo", default=str(HERE.parent))
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("needs", "plan", "run", "lists"):
        p = sub.add_parser(name)
        if name in ("plan", "run"):
            p.add_argument("--base", default="origin/main")
        if name == "run":
            p.add_argument("--all", action="store_true")
            p.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    if a.cmd == "needs":
        for thing, here, cost in needs(repo):
            print(
                f"  {'here   ' if here else 'MISSING'}  {thing}"
                + ("" if here else f": without it, {cost}")
            )
        return 0
    if a.cmd == "lists":
        miss = unlisted(repo)
        print(
            "every test file is one the mutants jobs run"
            if not miss
            else "the mutants jobs never run:\n" + "\n".join(f"  {t}" for t in miss)
        )
        return 0
    paths = changed(repo, a.base)
    tests, why = plan(repo, paths)
    if a.cmd == "plan":
        print(f"{len(paths)} path(s) changed")
        for w in why:
            print("  " + w)
        print(
            "\nrun everything"
            if tests is None
            else ("\nnothing to run" if not tests else "\n" + "\n".join(tests))
        )
        return 0
    everything = a.all or tests is None
    key = current_key(repo)
    held = store(repo) / key
    if not a.force and held.exists():
        print(
            f"stands: these bytes passed the full suite ({held.read_text().strip()}); --force runs anyway"
        )
        return 0
    if tests == [] and not a.all:
        print("nothing to run: what changed is read by no test")
        return 0
    files = [] if everything else tests
    print(
        "running everything"
        if everything
        else f"running {len(files)} test file(s) the change can reach"
    )
    code = pytest(repo, files)
    if code == 0 and everything:
        store(repo).mkdir(parents=True, exist_ok=True)
        held.write_text(
            f"a full pass at {time.strftime('%Y-%m-%d %H:%M:%S')}, {git(repo, 'rev-parse', '--short', 'HEAD').strip()}\n"
        )
        print("kept: the next run on these bytes stands")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
