"""willow_pin.py: where the box finds willow, held to the pin. Python 3.9+.

    python box/willow_pin.py check [--willow DIR]
    python box/willow_pin.py repin [--willow DIR] [--at COMMIT] [--add NAME ...] [--drop NAME ...]
    python box/willow_pin.py follow [COMMIT]
    python box/willow_pin.py prune [--days N]

The box plays with willow's kernel and add-ons by their own code, in willow;
willow.pin.json pins them: willow's commit, and each file the box
runs at that commit by its SHA-256. `root()` gives the willow the box runs
on, and only one whose every pinned file is there with its pinned bytes.

Where it looks, in order: WILLOW_ROOT, if set; then a checkout beside
die-namic-games named Willow or willow, the way its CI checks out a sibling
repository. The first that is a git checkout with the pinned commit gives a
copy of that commit, made from its git once and kept in willow's git folder,
named by the commit (so every checkout of that git shares them, and Model
Context Provider's too), so the box is on
its pin whatever branch the checkout is on. One that isn't git is used where
it is; then a missing file, or one that differs, is refused by name: the box
never runs on a willow it wasn't pinned to.

`check` says whether a checkout (DIR, else the one `root()` would look at
first) is the pinned willow. `repin` is the one way to move the pin, done on
purpose: it pins the checkout's commit, or with --at any commit its git has
(a branch, a tag, origin/main), read from git, never the files checked
out. What is pinned is kernel.py and, for
each add-on the pin names, every file willow's git holds in its folder but
its tests, so an add-on's new file comes in by itself. `--add` pins another
add-on, `--drop` lets one go. It refuses a checkout whose pinned files have
changes not committed (the pin always names bytes a commit holds), and an
add-on the commit doesn't have; then it says what moved.

`follow` is the whole move in one: it fetches, repins at COMMIT (origin/main
when none is named), makes its copy, and runs the tests on it. Only if they
pass does it commit willow.pin.json, on the branch you're on; if they fail,
the pin is put back as it was and nothing is committed. It never pushes.

`prune` lets go of the copies nothing has run for N days (14 when none is
named), never the one this pin names: a copy in use is marked so at most
once a day, and one let go is made again from git the next time it is
wanted.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
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


def copies(src: Path) -> Path | None:
    """Where the pinned copies of SRC's commits are kept, one folder per
    commit: in its git's own folder, where every checkout of that git finds
    them; None when SRC isn't a git checkout."""
    dot = src / ".git"
    try:
        if dot.is_file():  # a worktree: its git folder, then the one they share
            wt = Path(dot.read_text().split("gitdir:", 1)[1].strip())
            wt = wt if wt.is_absolute() else (src / wt)
            common = (
                (wt / "commondir").read_text().strip()
                if (wt / "commondir").is_file()
                else "."
            )
            dot = (wt / common).resolve()
    except (OSError, IndexError):
        return None
    return dot / "willow-pinned" if (dot / "objects").is_dir() else None


#: written last into a copy, so a copy cut short is never taken for one
DONE = ".willow-pinned"


def pinned_copy(src: Path, commit: str) -> Path | None:
    """Willow at COMMIT, made from SRC's git once and kept; None when SRC
    isn't a git checkout or its git doesn't have the commit."""
    home = copies(src)
    if home is None:
        return None
    at = home / commit
    if (at / DONE).is_file():
        used(at)
        return at
    if git(src, "rev-parse", "--verify", "--quiet", commit + "^{commit}").returncode:
        return None
    at.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=commit[:12] + ".", dir=at.parent))
    try:
        tar = work / "tree.tar"
        if git(src, "archive", "--format=tar", "-o", str(tar), commit).returncode:
            return None
        with tarfile.open(tar) as t:
            # git's own archive of willow; "data" where this Python has it
            safe = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
            t.extractall(work / "tree", **safe)
        (work / "tree" / DONE).write_text(commit + "\n")
        try:
            (work / "tree").rename(at)
        except OSError:  # another made it first: theirs is the same commit
            if not (at / DONE).is_file():
                raise
        return at
    finally:
        shutil.rmtree(work, ignore_errors=True)


#: how long a copy's mark of being used is left before it is renewed
DAY = 24 * 3600


def used(at: Path) -> None:
    """Mark a copy as run today, at most once a day: what prune goes by."""
    import time

    mark = at / DONE
    try:
        if time.time() - mark.stat().st_mtime > DAY:
            os.utime(mark)
    except OSError:  # a copy the person can't write to is still run
        pass


def prune(src: Path, keep: str, days: int = 14) -> list[str]:
    """The copies let go: each in SRC's git that isn't KEEP and that no one
    has run for DAYS days, removed, as their commits."""
    import time

    home = copies(src)
    if home is None or not home.is_dir():
        return []
    gone = []
    for at in sorted(home.iterdir()):
        mark = at / DONE
        if at.name == keep or not mark.is_file():
            continue  # this pin's, or one still being made
        if time.time() - mark.stat().st_mtime > days * DAY:
            shutil.rmtree(at, ignore_errors=True)
            gone.append(at.name)
    return gone


def root() -> Path:
    """The willow the box runs on, or Unpinned saying why not."""
    pinned, tried = pin(), []
    for c in candidates():
        made = pinned_copy(c, pinned["commit"])
        if made and not drift(made, pinned):
            return made
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
        "set WILLOW_ROOT to a willow git checkout that has that commit (git fetch there), "
        "or check willow out beside die-namic-games. " + "; ".join(tried)
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


def repin(where: Path, add: list[str] = (), drop: list[str] = (), at: Path | None = None, rev: str = "") -> tuple[int, str]:  # fmt: skip
    """(exit, what was said): the pin moved to WHERE's commit, or REV, or why
    not."""
    at = at or PIN
    if git(where, "rev-parse", "--git-dir").returncode != 0:
        return 2, f"refused: {where} isn't a willow git checkout"
    head = git(where, "rev-parse", "--verify", "--quiet", (rev or "HEAD") + "^{commit}")
    if head.returncode != 0:
        return 2, f"refused: willow's git at {where} has no commit {rev}"
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
    if dirty and not rev:  # REV is read from git alone: the checkout is no matter
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


#: the check `follow` runs on the willow it pins: the tests
CHECK = [sys.executable, "-m", "pytest", "-q", "tests"]


def follow(rev: str = "", at: Path | None = None) -> tuple[int, str]:
    """(exit, what was said). Repin at REV (origin/main when none is named),
    run CHECK, and commit the pin only if it passes."""
    at = at or PIN
    src = first_willow()
    git(src, "fetch", "-q", "origin")  # offline, what git has is followed
    was = at.read_bytes()
    code, said = repin(src, at=at, rev=rev or "origin/main")
    if code:
        return code, said
    commit = json.loads(at.read_text(encoding="utf-8"))["commit"]
    if was == at.read_bytes():
        return 0, f"the pin is on willow {commit[:12]} already: nothing moved"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    ran = subprocess.run(CHECK, cwd=REPO, env={**env, "WILLOW_ROOT": str(src)},
                         capture_output=True, text=True, check=False)  # fmt: skip
    if ran.returncode != 0:
        at.write_bytes(was)
        why = (ran.stdout + ran.stderr).strip()[-2000:]
        return 1, f"{said}\nthe check didn't pass, so the pin is back as it was:\n{why}"
    msg = f"Pin willow {commit[:12]}\n\n" + "\n".join(said.splitlines()[1:])
    done = subprocess.run(
        ["git", "-C", str(REPO), "commit", "-q", "-m", msg.strip() + "\n", "--", str(at)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    if done.returncode != 0:
        return (
            1,
            f"{said}\nthe check passed, but the commit didn't: {done.stderr.strip()}",
        )
    return 0, f"{said}\nthe check passed; committed, not pushed"


def main(argv: list[str]) -> int:
    verb, it = (argv[0] if argv else ""), iter(argv[1:])
    if verb == "prune":
        days = argv[2] if argv[1:2] == ["--days"] and len(argv) == 3 else "14"
        if (
            argv[1:]
            and (argv[1:2] != ["--days"] or len(argv) != 3)
            or not days.isdigit()
        ):
            print(__doc__.split("\n\n")[1], file=sys.stderr)
            return 2
        gone = prune(first_willow(), pin()["commit"], int(days))
        print(
            f"let go of {len(gone)} cop{'y' if len(gone) == 1 else 'ies'}",
            *gone,
            sep="\n  ",
        )
        return 0
    if verb == "follow":
        if len(argv) > 2 or any(not a or a.startswith("-") for a in argv[1:]):
            print(__doc__.split("\n\n")[1], file=sys.stderr)
            return 2
        code, said = follow(argv[1] if argv[1:] else "")
        print(said, file=sys.stderr if code else sys.stdout)
        return code
    where, rev, add, drop, bad = None, "", [], [], verb not in ("check", "repin")
    for a in it:
        got = next(it, "")
        if a == "--willow" and got and where is None:
            where = Path(got)
        elif a == "--at" and got and not rev and verb == "repin":
            rev = got
        elif a in ("--add", "--drop") and got and verb == "repin":
            (add if a == "--add" else drop).append(got)
        else:
            bad = True
    if bad:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    if verb == "repin":
        code, said = repin(where or first_willow(), add, drop, rev=rev)
        print(said, file=sys.stderr if code else sys.stdout)
        return code
    if where is None:
        try:
            where = root()
        except Unpinned as why:
            print(why)
            return 1
    off = drift(where, pin()) if (where / KERNEL).is_file() else ["no willow there"]
    if off:
        print(f"{where} isn't the pinned willow ({pin()['commit'][:12]}):", *off, sep="\n  ")  # fmt: skip
        return 1
    print(f"{where} is the pinned willow, {pin()['commit'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
