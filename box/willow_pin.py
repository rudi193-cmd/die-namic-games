"""willow_pin.py: where the box finds willow, held to the pin. Python 3.9+.

    python box/willow_pin.py check [--willow DIR]
    python box/willow_pin.py repin [--willow DIR] [--add NAME ...] [--drop NAME ...]

The box plays with willow's kernel and add-ons where they live, in willow;
willow.pin.json pins them: willow's commit, and each file the box
runs at that commit by its SHA-256. `root()` finds a willow checkout and
gives its folder only if every pinned file is there with its pinned bytes.

Where it looks, in order: WILLOW_ROOT, if set; then a checkout beside
die-namic-games named Willow or willow, the way its CI checks out a sibling
repository. A checkout missing a file, or holding one that differs,
is refused by name: the box never runs on a willow it wasn't pinned to.

`check` says whether a checkout (DIR, else the one `root()` would look at
first) is the pinned willow. `repin` is the one way to move the pin, done on
purpose: it pins the checkout's commit. What is pinned is kernel.py and, for
each add-on the pin names, every file willow's git holds in its folder but
its tests, so an add-on's new file comes in by itself. `--add` pins another
add-on, `--drop` lets one go. It refuses a checkout whose pinned files have
changes not committed (the pin always names bytes a commit holds), and an
add-on the commit doesn't have; then it says what moved.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = HERE.parent / "willow.pin.json"
REPO = HERE.parent  # die-namic-games, holding box/


class Unpinned(RuntimeError):
    """No willow checkout holds the pinned files; the message says what."""


def pin() -> dict:
    return json.loads(PIN.read_text(encoding="utf-8"))


def candidates() -> list[Path]:
    found = [Path(os.environ["WILLOW_ROOT"])] if os.environ.get("WILLOW_ROOT") else []
    return found + [REPO.parent / "Willow", REPO.parent / "willow"]


def drift(root: Path, pinned: dict) -> list[str]:
    """The pinned files a checkout is missing, or holds with other bytes."""
    out = []
    for rel, want in pinned["files"].items():
        f = root / rel
        if not f.is_file():
            out.append(f"{rel} is missing")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != want:
            out.append(f"{rel} differs")
    return out


def root() -> Path:
    """The willow checkout the box runs on, or Unpinned saying why not."""
    pinned, tried = pin(), []
    for c in candidates():
        if not (c / "kernel.py").is_file():
            tried.append(f"{c}: no willow there")
            continue
        off = drift(c, pinned)
        if not off:
            return c
        tried.append(
            f"{c}: {len(off)} file(s) off the pin at {pinned['commit'][:12]}, first {off[0]}"
        )
    raise Unpinned(
        f"no willow checkout matches the pin (willow {pinned['commit'][:12]}); "
        "set WILLOW_ROOT, or check willow out beside die-namic-games. "
        + "; ".join(tried)
    )


def script(name: str) -> Path:
    """An add-on's script in the pinned willow, by the add-on's name: where it
    lives (adapters/stdlib or adapters/deps), its dashes as underscores. Only
    a pinned add-on: one willow.pin.json doesn't name is refused."""
    if name not in pin()["add_ons"]:
        raise Unpinned(f"{name} isn't an add-on willow.pin.json pins")
    base = root() / "adapters"
    for kind in ("stdlib", "deps"):
        f = base / kind / name / (name.replace("-", "_") + ".py")
        if f.is_file():
            return f
    raise Unpinned(f"{name} is pinned but not in the willow at {base.parent}")


def addon(name: str, module: str = ""):
    """A pinned add-on's script loaded as a module, once: what the box reads
    with it (a page, a sheet) is the add-on's own code, never a copy here.
    MODULE names another file of the add-on's (play-fight5e's statblocks),
    loaded with the add-on's folder first on the path, as its script is."""
    import importlib.util
    import sys

    main = script(name)
    key = "willow_" + name.replace("-", "_") + ("_" + module if module else "")
    if key not in sys.modules:
        if module:
            sys.path.insert(0, str(main.parent))
        spec = importlib.util.spec_from_file_location(key, main.with_name(module + ".py") if module else main)  # fmt: skip
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod  # a dataclass looks itself up by its module
        spec.loader.exec_module(mod)
    return sys.modules[key]


# ── moving the pin, on purpose ───────────────────────────────────────────────
KERNEL = "kernel.py"
KINDS = ("stdlib", "deps")


def git(where: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, check=False)  # fmt: skip


def pinned(name: str) -> bool:
    """A test, or what pytest reads beside them, is never pinned."""
    return not name.startswith("test_") and name != "conftest.py"


def folder_of(tracked: list[str], name: str) -> str:
    """Where an add-on lives in the commit's tree, or "" when it has none."""
    for kind in KINDS:
        top = "adapters/%s/%s" % (kind, name)  # noqa: UP031
        if any(f.startswith(top + "/") for f in tracked):
            return top
    return ""


def pinned_of(tracked: list[str], name: str) -> list[str]:
    """An add-on's files as the pin holds them: each one git holds in its
    folder, its tests left out."""
    top = folder_of(tracked, name)
    if not top:
        return []
    return [f for f in tracked if f.startswith(top + "/") and pinned(f.rsplit("/", 1)[-1])]  # fmt: skip


def in_order(old: list[str], new: list[str]) -> list[str]:
    """NEW in the pin's own order: what it held stays where it was, and a new
    file goes after the last one of its folder, or at the end."""
    keep = [f for f in old if f in new]
    for f in (f for f in new if f not in old):
        folder = f.rsplit("/", 1)[0] + "/"
        at = max((i for i, g in enumerate(keep) if g.startswith(folder)), default=len(keep) - 1)  # fmt: skip
        keep.insert(at + 1, f)
    return keep


def repin(where: Path, add: list[str] = (), drop: list[str] = (), at: Path | None = None) -> tuple[int, str]:  # fmt: skip
    """(exit, what was said): the pin moved to WHERE's commit, or why not."""
    at = at or PIN
    head = git(where, "rev-parse", "HEAD")
    if head.returncode != 0:
        return 2, f"refused: {where} isn't a willow git checkout"
    commit = head.stdout.strip()
    tracked = git(where, "ls-tree", "-r", "--name-only", commit).stdout.split()
    if KERNEL not in tracked:
        return 2, f"refused: no {KERNEL} in willow {commit[:12]}"
    old = json.loads(at.read_text(encoding="utf-8"))
    gone = [n for n in drop if n not in old["add_ons"]]
    if gone:
        return 2, f"refused: {gone[0]} isn't an add-on the pin names"
    names = [n for n in old["add_ons"] if n not in drop]
    for n in add:
        if n not in names:
            later = next((i for i, m in enumerate(names) if m > n), len(names))
            names.insert(later, n)
    files, folders = [KERNEL], [KERNEL]
    for n in names:
        got = pinned_of(tracked, n)
        if not got:
            return 2, f"refused: willow {commit[:12]} has no add-on {n}"
        files += got
        folders.append(folder_of(tracked, n))
    # what isn't committed in a pinned folder, new files too, its tests aside
    status = git(
        where, "status", "--porcelain", "--untracked-files=all", "--", *folders
    )
    dirty = [x for x in status.stdout.splitlines() if pinned(x[3:].rsplit("/", 1)[-1])]
    if dirty:
        return 2, "refused: changes not committed in pinned files:\n" + "\n".join(dirty)
    new = {}
    for rel in in_order(list(old["files"]), files):
        blob = subprocess.run(["git", "-C", str(where), "show", commit + ":" + rel], capture_output=True, check=False)  # fmt: skip
        new[rel] = hashlib.sha256(blob.stdout).hexdigest()
    doc = {**old, "commit": commit, "add_ons": names, "files": new}
    at.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    was = old["files"]
    moved = sorted(
        [f"changed: {r}" for r in new if r in was and was[r] != new[r]]
        + [f"added: {r}" for r in new if r not in was]
        + [f"gone: {r}" for r in was if r not in new]
    )
    said = f"pinned willow {commit[:12]}, {len(names)} add-ons, {len(new)} files"
    if commit == old["commit"] and not moved:
        said += "; nothing moved"
    return 0, "\n".join([said, *moved])


def first_willow() -> Path:
    """The checkout `root()` looks at first: WILLOW_ROOT, else the sibling."""
    return next((c for c in candidates() if (c / KERNEL).is_file()), candidates()[0])


def main(argv: list[str]) -> int:
    verb, it = (argv[0] if argv else ""), iter(argv[1:])
    where, add, drop, bad = None, [], [], verb not in ("check", "repin")
    for a in it:
        got = next(it, "")
        if a == "--willow" and got and where is None:
            where = Path(got)
        elif a in ("--add", "--drop") and got and verb == "repin":
            (add if a == "--add" else drop).append(got)
        else:
            bad = True
    if bad:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    where = where or first_willow()
    if verb == "repin":
        code, said = repin(where, add, drop)
        print(said, file=sys.stderr if code else sys.stdout)
        return code
    off = drift(where, pin()) if (where / KERNEL).is_file() else ["no willow there"]
    if off:
        print(f"{where} isn't the pinned willow ({pin()['commit'][:12]}):", *off, sep="\n  ")  # fmt: skip
        return 1
    print(f"{where} is the pinned willow, {pin()['commit'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
