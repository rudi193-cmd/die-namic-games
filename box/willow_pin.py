"""willow_pin.py: where the box finds willow, held to the pin. Python 3.9+.

The box plays with willow's kernel and add-ons where they live, in willow;
willow.pin.json pins them: willow's commit, and each file the box
runs at that commit by its SHA-256. `root()` finds a willow checkout and
gives its folder only if every pinned file is there with its pinned bytes.

Where it looks, in order: WILLOW_ROOT, if set; then a checkout beside
die-namic-games named Willow or willow, the way its CI checks out a sibling
repository. A checkout missing a file, or holding one that differs,
is refused by name: the box never runs on a willow it wasn't pinned to.
"""

from __future__ import annotations

import hashlib
import json
import os
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
