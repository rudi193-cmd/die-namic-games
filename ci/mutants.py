"""mutants.py: Die-Namic's code broken on purpose, to see its tests notice.

    python ci/mutants.py run [FILE ...] [--per N|all]
    python ci/mutants.py list FILE

willow's mutants add-on breaks an add-on's code in small ways, one at a time,
and runs its tests against each break. It is built for willow's own
adapters/stdlib, so this drives it for Die-Namic: the breaks are its own
(`points` finds where one can be made: a comparison flipped, an `and` made
`or`, a whole number made one larger), taken from the willow the pin names,
and made in place (`broken` below: only the broken expression is rewritten), and only the files and their tests are Die-Namic's,
named in ci/mutants.json. Every break runs against the whole suite, fastest
file first: which test covers which file is not guessed.

A break whose tests fail is killed. One they pass is a survivor: the tests
can't tell the code from a broken copy, and it fails here unless
mutants.json's `accepted` gives the reason it is harmless. An accepted id
that no longer survives is stale, and fails too; since a test that fails now
and then would make an accepted break look killed, one is run three times and
called stale only when every run kills it, naming the test that did.

The suite is run once unbroken first, and must pass: a break is only judged
against tests that pass without it. So, unlike the add-on (where a collection
error may be the add-on's own), pytest's exit 2 counts as a kill here: the
same tests collected cleanly on the unbroken code, so it is the break that
stopped them (a test module that calls the code at import, as
test_willow_pin.py does). Any other exit (no tests, a usage error) and a
timeout killed nothing, and are said, never counted as a kill.

Each break runs in a copy of the repo, never this checkout, with its tests
stopping at the first failure. Each file takes the breaks mutants.json gives
it: "all", or the first N by id (the add-on's sample, the same on every
machine); `--per` gives every file named the same. The ids are the add-on's: a hash of the file, the
kind of break, its code and which of the same it is, so an id stays put when
lines above it move.

Exit 0 every break killed or accepted; 1 otherwise; 2 a bad command line.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "ci" / "mutants.json"
sys.path.insert(0, str(REPO / "box"))
import willow_pin  # noqa: E402

WILLOW = willow_pin.root()
sys.path.insert(0, str(WILLOW))
import kernel  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "willow_mutants", WILLOW / "adapters" / "stdlib" / "mutants" / "mutants.py"
)
willow_mutants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(willow_mutants)

SKIP = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}


def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def mutants(rel: str) -> list[dict]:
    """Every break of one file, each with its id, sorted by id: the add-on's
    own walk and ids, over a Die-Namic file."""
    source = (REPO / rel).read_text(encoding="utf-8")
    tree = ast.parse(source)
    skip = willow_mutants.inert(tree)
    seen: dict[tuple, int] = {}
    out = []
    for i, (kind, node) in enumerate(willow_mutants.points(tree)):
        code = ast.get_source_segment(source, node) or ""
        nth = seen[(kind, code)] = seen.get((kind, code), -1) + 1
        if node in skip:
            continue
        mid = kernel.h256(f"{rel}\x1f{kind}\x1f{code}\x1f{nth}")[:12]
        out.append({"id": mid, "file": rel, "line": node.lineno,
                    "kind": kind, "code": code, "point": i})  # fmt: skip
    return sorted(out, key=lambda m: m["id"])


def broken(source: str, point: int) -> str:
    """The file's source with the break at `point` made, and every other byte
    as it was. willow's `broken` writes the whole file back through
    ast.unparse; on a CI runner's Python that rewrite alone changed how a
    file behaved (binder's every break was killed there by a test the break
    never touched), so here only the broken expression is unparsed, in
    parentheses, and spliced in where it stood."""
    tree = ast.parse(source)
    kind, node = willow_mutants.points(tree)[point]
    if kind == "compare":
        node.ops[0] = willow_mutants.SWAP[type(node.ops[0])]()
    elif kind == "and-or":
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
    else:
        node.value += 1
    lines = source.encode("utf-8").splitlines(keepends=True)
    start = sum(len(ln) for ln in lines[: node.lineno - 1]) + node.col_offset
    end = sum(len(ln) for ln in lines[: node.end_lineno - 1]) + node.end_col_offset
    raw = source.encode("utf-8")
    return (raw[:start] + f"({ast.unparse(node)})".encode() + raw[end:]).decode("utf-8")


def made(rel: str, mid: str) -> str:
    """The line a break changes, before and after, as this Python makes it:
    what to compare when a break is judged one way here and another there."""
    import difflib

    m = next(x for x in mutants(rel) if x["id"] == mid)
    source = (REPO / rel).read_text(encoding="utf-8")
    plain = source.splitlines()
    broke = broken(source, m["point"]).splitlines()
    changed = [ln.strip() for ln in difflib.unified_diff(plain, broke, lineterm="", n=0)
               if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]  # fmt: skip
    return f"{' -> '.join(changed)} (Python {sys.version.split()[0]})"


_stamp = [0]


def fresh(copy: Path, target: Path) -> None:
    """No code cached from an earlier break is run for this one. A cached .pyc
    holds when its source has the same size and the same whole-second mtime,
    and a break made in place is often the size of the last one (`3` made
    `(4)`, `2` made `(3)`). PYTHONDONTWRITEBYTECODE doesn't stop it: a test
    that runs `python -I` ignores the variable and writes the cache. So every
    __pycache__ in the copy goes, and the file gets an mtime of its own."""
    for cache in list(copy.rglob("__pycache__")):
        shutil.rmtree(cache, ignore_errors=True)
    _stamp[0] += 1
    when = int(time.time()) + _stamp[0]
    os.utime(target, (when, when))


def run(files: list[str], per: int | str | None, limit: int) -> int:
    cfg = config()
    accepted = cfg.get("accepted", {})
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "die-namic-games"
        shutil.copytree(REPO, copy, ignore=lambda _d, names: SKIP & set(names))
        # the copy has no willow-bot beside it, so the one-script the fights
        # roll with is named where the checkout's sibling has it
        bot = os.environ.get("ONESCRIPT_HOME") or str(REPO.parent / "willow-bot" / "one-script")  # fmt: skip
        env = {**os.environ, "WILLOW_ROOT": str(WILLOW), "ONESCRIPT_HOME": bot, "PYTHONDONTWRITEBYTECODE": "1"}  # fmt: skip
        tests = [str(copy / t) for t in cfg["tests"]]
        pytest = [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                  "--rootdir", str(copy), *tests]  # fmt: skip
        clean = subprocess.run(pytest, capture_output=True, text=True, cwd=copy, env=env, check=False)
        if clean.returncode != 0:
            print(f"refused: the suite fails on the unbroken code (exit {clean.returncode});"
                  " a break can't be judged against it")  # fmt: skip
            print(clean.stdout[-2000:])
            return 1
        for rel in files:
            take = cfg["targets"][rel] if per is None else per
            every = mutants(rel)
            chosen = every if take == "all" else every[:take]
            survived, couldnt, killed_by = [], [], {}
            started = time.monotonic()
            for m in chosen:
                target = copy / m["file"]
                original = target.read_text(encoding="utf-8")
                target.write_text(broken(original, m["point"]), encoding="utf-8")
                fresh(copy, target)
                try:
                    # An accepted break the tests kill is run twice more before it
                    # is called stale: a test that fails now and then on a CI
                    # runner would otherwise kill it once and turn the run red.
                    # It is stale only if every run kills it, and says what did.
                    tries = 3 if m["id"] in accepted else 1
                    for _ in range(tries):
                        got = subprocess.run(
                            pytest, capture_output=True, text=True, timeout=limit, cwd=copy,
                            env=env, check=False,
                        )  # fmt: skip
                        if got.returncode == 0:
                            break
                        killed_by.setdefault(m["id"], []).extend(
                            ln for ln in got.stdout.splitlines() if ln.startswith(("FAILED", "ERROR"))
                        )
                    if got.returncode == 0:
                        survived.append(m)
                    elif got.returncode not in (1, 2):
                        couldnt.append(f"{m['id']}: pytest exited {got.returncode}")
                except subprocess.TimeoutExpired:
                    couldnt.append(f"{m['id']}: its tests ran past {limit} s")
                finally:
                    target.write_text(original, encoding="utf-8")
                    fresh(copy, target)
            mine = {k for k in accepted if k in {m["id"] for m in mutants(rel)}}
            wrong = [m for m in survived if m["id"] not in accepted]
            stale = sorted(mine - {m["id"] for m in survived} & {m["id"] for m in chosen})
            killed = len(chosen) - len(survived) - len(couldnt)
            print(f"{rel}: {killed} of {len(chosen)} killed, "
                  f"{len(survived) - len(wrong)} accepted, "
                  f"{time.monotonic() - started:.0f} s")  # fmt: skip
            for m in wrong:
                print(f"  survived {m['id']}  {m['file']}:{m['line']}  {m['kind']}: {m['code']}")
            for why in couldnt:
                print(f"  couldn't run {why}")
            for mid in stale:
                print(f"  stale {mid}: accepted, but no longer surviving;"
                      " take it out of ci/mutants.json")  # fmt: skip
                for ln in killed_by.get(mid, []):
                    print(f"    killed by {ln}")
                print(f"    the break made: {made(rel, mid)}")
            bad += len(wrong) + len(stale) + len(couldnt)
    orphan = sorted(set(accepted) - {m["id"] for f in cfg["targets"] for m in mutants(f)})
    for mid in orphan:
        print(f"stale {mid}: accepted, but no file makes it any more; take it out")
    bad += len(orphan)
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    cfg = config()
    usage = "usage: mutants.py run [FILE ...] [--per N|all] | mutants.py list FILE"
    if not argv or argv[0] not in ("run", "list"):
        print(usage, file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    per = None
    if "--per" in rest:
        i = rest.index("--per")
        got = rest[i + 1] if i + 1 < len(rest) else ""
        if got != "all" and not got.isdigit():
            print("refused: --per needs a whole number or all", file=sys.stderr)
            return 2
        per = got if got == "all" else int(got)
        rest = rest[:i] + rest[i + 2 :]
    unknown = [f for f in rest if f not in cfg["targets"]]
    if unknown:
        print(f"refused: {', '.join(unknown)} not in ci/mutants.json's targets", file=sys.stderr)
        return 2
    if cmd == "list":
        if len(rest) != 1:
            print(usage, file=sys.stderr)
            return 2
        for m in mutants(rest[0]):
            print(f"{m['id']}  {m['file']}:{m['line']}  {m['kind']}: {m['code']}")
        return 0
    if subprocess.run([sys.executable, "-c", "import pytest"], capture_output=True, check=False).returncode:
        print("refused: pytest isn't installed", file=sys.stderr)
        return 2
    return run(rest or list(cfg["targets"]), per, cfg.get("limit", willow_mutants.LIMIT))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
