"""memo.py: the key a CI verdict stands on. Python 3.9+, stdlib only.

    python ci/memo.py key [--repo DIR] [--gate NAME] [--extra K=V ...]
    python ci/memo.py reach [--repo DIR]
    python ci/memo.py why PATH [--repo DIR]

A CI job's verdict is a function of the bytes it can reach. This names those
bytes, hashes each file's path and SHA-256 together into one key, and prints
it. The workflow keys a cache on it: a pull request whose key is one `main`
already passed on stands on main's verdict and skips the job, the way willow's
ci-memo does for willow's own gates (adapters/stdlib/ci-memo, whose gates are
willow's and whose records are ci.py's, so it can't be run on this repo; the
move is the same, kept small: a key is bytes, never a guess, and the reach is
drawn wide, never narrow).

The reach is every tracked file but the few nothing reads: EXCLUDED, each one
checked (a path in a string, not in a comment or a docstring, would put it back:
tests/test_memo.py holds that). Everything else is reached, README.md and
`.github/` included, so a change there runs the job: over-run, never
under-run. What the tree can't hold is named by `--extra` (the Python, the
runner, the commit of an unpinned checkout), so the key moves with it.

A gate's name is in its key, and the key's own version: change how keys are
made and change VERSION, so no old verdict stands. It decides nothing: it
prints a key.

Exit codes: 0 done; 2 refused.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

VERSION = "memo/1"

# Files and folders no test and no code reads (tests/test_memo.py's guard holds
# that no string in the code names one). Prose about the repo, and what this
# session's research left: changing one cannot change a verdict.
EXCLUDED = (
    "boxes/",
    "open.md",
    "open-gaps-from-the-boxes.md",
    "ci/README.md",
)


def excluded(path: str) -> bool:
    return any(path == e or (e.endswith("/") and path.startswith(e)) for e in EXCLUDED)


def tracked(repo: Path) -> list[str]:
    got = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=False)  # fmt: skip
    if got.returncode != 0:
        raise SystemExit(f"refused: {repo} is not a git checkout ({got.stderr.decode().strip()})")  # fmt: skip
    return sorted(p for p in got.stdout.decode().split("\0") if p)


def reach(repo: Path) -> list[str]:
    return [p for p in tracked(repo) if not excluded(p)]


def key(repo: Path, gate: str = "", extras: tuple[str, ...] = ()) -> str:
    h = hashlib.sha256()
    h.update(f"{VERSION}\0gate={gate}\0".encode())
    for e in sorted(extras):
        h.update(f"extra={e}\0".encode())
    for p in reach(repo):
        f = repo / p
        digest = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else "none"  # a symlink to nowhere, a deleted file  # fmt: skip
        h.update(f"{p}\0{digest}\n".encode())
    return h.hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="memo.py", description="the key a CI verdict stands on")  # fmt: skip
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("key", "reach", "why"):
        p = sub.add_parser(name)
        p.add_argument("--repo", default=".")
        if name == "key":
            p.add_argument("--gate", default="")
            p.add_argument("--extra", action="append", default=[])
        if name == "why":
            p.add_argument("path")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    if a.cmd == "key":
        print(key(repo, a.gate, tuple(a.extra)))
    elif a.cmd == "reach":
        print("\n".join(reach(repo)))
    else:
        p = a.path
        if p not in tracked(repo):
            print(f"{p}: not tracked here, so not in any key")
        elif excluded(p):
            print(f"{p}: left out of every key (nothing reads it)")
        else:
            print(f"{p}: in every key")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
