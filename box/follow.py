"""follow.py: a person's page, following packages as they land. Python 3.9+.

    python box/follow.py --night DIR --person NAME [--to FILE.html] [--every SECONDS] [--once]

Runs on one person's device through the night. DIR is what table_scene.py
laid; the person's drop folder is DIR/drop/NAME: a synced folder, or one
they save a package into from an email, a chat or a stick (the maintainer:
both, each person's choice). Nothing here goes online; how a package
travels is the table's.

Every SECONDS (default 5), each new package in the drop folder is:

1. placed: the seat it is for is this person's at the table whose GM sent
   it (the package's sender is that GM's identity); one from no GM at their
   tables is set aside, unplaced, and said;
2. received into that seat's own box with willow's `share receive` and the
   person's one identity: a `received` row on that seat's chain whatever it
   found, `good`, `not-for-you` or `broken`;
3. kept in DIR/drop/NAME/kept, never deleted, so it is never received twice.

What held goes on the seat's "from the GM", its words read from the package
that held, marked just arrived; what didn't is shown as arrived and not
held, with why. Then the person's page is built again (ui/screen.py) into
FILE.html (default DIR/NAME.html), with FILE.html.stamp.js beside it: the
open page loads that small file every few seconds, which a page opened from
a file can do with no server, and reloads itself when the stamp changes.
The page is built again too when a table.json it is built from changes (the
GM sent something more).

It never seals, declines or reads a seal key; it reads the person's
identity only to receive, as share does. `--once` looks once and stops.
Exit 0; 2 refused.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin

sys.path.insert(0, str(HERE.parent / "ui"))
import screen

ROOT = willow_pin.root()
SHARE = ROOT / "adapters" / "stdlib" / "share" / "share.py"
KERNEL = ROOT / "kernel.py"


def now_after(box: Path) -> str:
    """Now, or a minute after the box's last row if that is later: a row is
    never written before the one above it."""
    t = datetime.now(timezone.utc).replace(microsecond=0)
    last = json.loads((box / "record.jsonl").read_text().splitlines()[-1])["ts"]
    t = max(
        t,
        datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        + timedelta(minutes=1),
    )
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


class Follower:
    def __init__(self, night: Path, person: str, to: Path, every: int):
        self.night, self.person, self.to, self.every = night, person, to, every
        self.drop = night / "drop" / person
        self.kept = self.drop / "kept"
        self.built = ""

    def seats(self) -> list[dict]:
        people = json.loads((self.night / "people.json").read_text(encoding="utf-8"))
        return people[self.person]

    def tables(self) -> dict:
        return {
            s["table"]: self.night / s["table"] / "table.json" for s in self.seats()
        }

    def place(self, sender: str) -> str | None:
        """The table, among those this person plays at, whose GM sent it."""
        for s in self.seats():
            if s["seat"] == "gm":
                continue
            doc = json.loads((self.night / s["table"] / "table.json").read_text(encoding="utf-8"))  # fmt: skip
            gm = (self.night / "people" / doc["gm_person"] / "pub").read_text().strip()
            if gm == sender:
                return s["table"]
        return None

    def take(self, pkg: Path) -> str:
        """Receive one package into the seat it is for; say what happened."""
        try:
            doc = json.loads(pkg.read_text(encoding="utf-8"))
            sender = doc["from"]
        except (ValueError, KeyError, TypeError):
            return f"{pkg.name}: not a package, set aside"
        tid = self.place(sender)
        if tid is None:
            return f"{pkg.name}: from no GM at your tables, set aside"
        box = self.night / tid / self.person / "box"
        got = subprocess.run(
            [sys.executable, str(SHARE), "receive", "--box", str(box), "--id",
             str(self.night / "people" / self.person / "id"), "--package", str(pkg),
             "--now", now_after(box)],
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        first = got.stdout.strip().splitlines()[0] if got.stdout.strip() else ""
        if got.returncode == 2 or not first:
            return f"{pkg.name}: refused by share ({(got.stderr or got.stdout).strip()[:120]})"  # fmt: skip
        if first.startswith(
            "already received"
        ):  # the same package again: one row, said once
            return f"{pkg.name}: {first}, at {tid}"
        verdict = first.split()[-1]
        why = [ln.strip() for ln in got.stdout.splitlines()[1:] if ln.startswith("  ") and verdict != "good"]  # fmt: skip
        tj = self.night / tid / "table.json"
        table = json.loads(tj.read_text(encoding="utf-8"))
        seat = next(s for s in table["seats"] if s["seat"] == self.person)
        when = now_after(box)
        if verdict == "good":
            seat["received"] += [
                {"what": a["data"], "claim": a["claim"], "from": table["gm_person"],
                 "cites": sorted(set(a.get("places", {}).values())), "verdict": verdict,
                 "arrived": when, "just": True}
                for a in doc["answers"]
            ]  # fmt: skip
        else:
            seat.setdefault("refused", []).append(
                {
                    "package": pkg.name,
                    "verdict": verdict,
                    "why": why[:2],
                    "arrived": when,
                    "just": True,
                }
            )
        seat["chain"] = subprocess.run([sys.executable, str(KERNEL), "verify", "--box", str(box)],
                                       capture_output=True, text=True, check=False).stdout.strip()  # fmt: skip
        tj.write_text(json.dumps(table, indent=1), encoding="utf-8")
        return f"{pkg.name}: {verdict}, at {tid}"

    def quiet(self) -> None:
        """A new round arrived: what was just arrived before is not any more."""
        for tj in self.tables().values():
            doc = json.loads(tj.read_text(encoding="utf-8"))
            for s in doc["seats"]:
                if s["seat"] == self.person:
                    for r in s["received"] + s.get("refused", []):
                        r.pop("just", None)
            tj.write_text(json.dumps(doc, indent=1), encoding="utf-8")

    def look(self) -> list[str]:
        new = sorted(p for p in self.drop.glob("*.pkg") if p.is_file())
        said = []
        if new:
            self.quiet()
            self.kept.mkdir(exist_ok=True)
        for pkg in new:
            said.append(self.take(pkg))
            shutil.move(str(pkg), str(self.kept / pkg.name))
        return said

    def build(self) -> bool:
        """Build the page again if a table it shows changed; True if it did."""
        stamp = hashlib.sha256(
            b"".join(p.read_bytes() for p in self.tables().values())
        ).hexdigest()[:16]
        if stamp == self.built and self.to.exists():
            return False
        screen.build_person(self.night, self.person, self.to, follow={"every": self.every, "stamp": stamp})  # fmt: skip
        Path(str(self.to) + ".stamp.js").write_text(f'window.__stamp = "{stamp}";\n')
        self.built = stamp
        return True

    def once(self) -> None:
        for line in self.look():
            print(line, flush=True)
        if self.build():
            print(f"page built: {self.to}", flush=True)


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a in ("--night", "--person", "--to", "--every"):
            opts[a] = next(it, "")
        else:
            args.append(a)
    if (
        not opts.get("--night")
        or not opts.get("--person")
        or args not in ([], ["--once"])
    ):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    night = Path(opts["--night"]).resolve()
    person = opts["--person"]
    if not (night / "people.json").is_file():
        print(f"refused: no people.json in {night}; run box/table_scene.py first", file=sys.stderr)  # fmt: skip
        return 2
    if person not in json.loads((night / "people.json").read_text()):
        print(f"refused: no {person!r} at these tables", file=sys.stderr)
        return 2
    try:
        every = max(1, int(opts.get("--every") or 5))
    except ValueError:
        print("refused: --every is a number of seconds", file=sys.stderr)
        return 2
    to = Path(opts.get("--to") or night / f"{person}.html")
    f = Follower(night, person, to, every)
    (night / "drop" / person).mkdir(parents=True, exist_ok=True)
    f.once()
    if args == ["--once"]:
        return 0
    print(f"following {f.drop}, every {every} s (Ctrl-C stops)", flush=True)
    try:
        while True:
            time.sleep(every)
            f.once()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
