"""known.py: willow's report add-ons run on Die-Namic, held to what is known.

    python ci/known.py [--db OSV_DIR] [NAME ...]

Each NAME is a report add-on (all five when none is named), run from the
willow the pin names (box/willow_pin.py finds it) with `--from` this repo and
`--json`. Every row it reports must be one ci/known.json accepts, with the
reason it is no finding; a row nothing accepts is new, and fails. An entry
that accepts no row any more is stale, and fails too: take it out, so the
list never holds a reason for something that has gone.

A row is matched by its add-on, its group, its place without the line number
(a line moves when the file above it is edited) and what it says. An entry
accepts `count` such rows (1 when unsaid): a second secret in a file that held
one is a new row, not the known one again.

An add-on that couldn't look (`unreachable`) or refused fails: it said
nothing about the repo. advisories needs `--db`, a folder of OSV records
(osv.dev's PyPI export, unzipped): without one it only lists what is locked,
which is no check, so it is refused here rather than passed.

Exit 0 every row known and no entry stale; 1 otherwise; 2 a bad command line.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KNOWN = REPO / "ci" / "known.json"
sys.path.insert(0, str(REPO / "box"))
import willow_pin  # noqa: E402

CHECKS = {
    "unpinned": "unpinned/unpinned.py",
    "agents-md-check": "agents-md-check/agents_md_check.py",
    "secrets-audit": "secrets-audit/secrets_audit.py",
    "ref-check": "ref-check/ref_check.py",
    "advisories": "advisories/advisories.py",
}


def place(where: str) -> str:
    """A row's place without its line number: `a/b.py:12` is `a/b.py`."""
    head, _, tail = where.rpartition(":")
    return head if head and tail.isdigit() else where


def keys(report: dict) -> Counter:
    """Each row of a report, as the key an entry in known.json matches."""
    out: Counter = Counter()
    for group in report.get("groups", []):
        for row in group["rows"]:
            out[(group["name"], place(row["where"]), row["what"])] += 1
    return out


def held(name: str, found: Counter, known: list[dict]) -> list[str]:
    """What is wrong with one add-on's rows against its known entries."""
    want: Counter = Counter()
    for e in known:
        want[(e["group"], e["where"], e["what"])] += e.get("count", 1)
    out = []
    for key, n in sorted(found.items(), key=str):
        extra = n - want.get(key, 0)
        if extra > 0:
            group, where, what = key
            out.append(f"{name}: new, {extra} row(s): [{group}] {where}  {what}")
    for key, n in sorted(want.items(), key=str):
        if found.get(key, 0) < n:
            group, where, what = key
            out.append(
                f"{name}: stale, known.json accepts {n} but {found.get(key, 0)} found:"
                f" [{group}] {where}  {what}; take it out or lower its count"
            )
    return out


def report(willow: Path, name: str, db: str | None) -> dict:
    """The add-on's report on this repo, or an `unreachable` one saying why."""
    cmd = [sys.executable, str(willow / "adapters" / "stdlib" / CHECKS[name])]
    cmd += ["--from", str(REPO), "--json"]
    if name == "advisories":
        cmd += ["--db", db]
    got = subprocess.run(cmd, capture_output=True, text=True, check=False)
    try:
        return json.loads(got.stdout)
    except json.JSONDecodeError:
        why = (got.stderr or got.stdout).strip().splitlines()[-1:] or ["no output"]
        return {"addon": name, "state": "refused", "said": why[0], "groups": []}


def main(argv: list[str]) -> int:
    db = None
    if "--db" in argv:
        i = argv.index("--db")
        if i + 1 >= len(argv):
            print("refused: --db needs a folder", file=sys.stderr)
            return 2
        db = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    names = argv or list(CHECKS)
    unknown = [n for n in names if n not in CHECKS]
    if unknown:
        print(f"refused: no check {', '.join(unknown)}; the checks are {', '.join(CHECKS)}",
              file=sys.stderr)  # fmt: skip
        return 2
    if "advisories" in names and not (db and Path(db).is_dir()):
        print("refused: advisories needs --db, a folder of OSV records", file=sys.stderr)
        return 2
    willow = willow_pin.root()
    known = json.loads(KNOWN.read_text(encoding="utf-8"))
    bad = []
    for name in names:
        got = report(willow, name, db)
        print(f"{name}: {got['state']}, {got['said']}")
        if got["state"] not in ("populated", "empty"):
            bad.append(f"{name}: {got['state']}, so it said nothing of the repo")
            continue
        bad += held(name, keys(got), known.get(name, []))
    for line in bad:
        print(f"  {line}")
    print("known: every row known" if not bad else f"known: {len(bad)} to settle")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
