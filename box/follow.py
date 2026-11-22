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

import base64
import hashlib
import json
import re
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
GM = ROOT / "adapters" / "stdlib" / "game-master" / "game_master.py"
PICTURES = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def verify(box: Path) -> str:
    return subprocess.run([sys.executable, str(KERNEL), "verify", "--box", str(box)],
                          capture_output=True, text=True, check=False).stdout.strip()  # fmt: skip


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

    def place(self, sender: str, note: str) -> tuple[str, str] | str:
        """Where a package goes: (table, "player") at a table this person plays
        at whose GM sent it; (table, player) at a table they run, sent by one
        of its players. One person is one identity at every table, so the key
        alone can't tell two tables apart when two people sit at each other's:
        the sender names the table in the note ("..., at sunday"), which is
        inside the signature. Otherwise, a string saying why it was set aside."""
        named = re.search(r", at ([a-z0-9-]+)$", note or "")
        key = lambda p: (self.night / "people" / p / "pub").read_text().strip()
        fits = []
        for s in self.seats():
            if named and s["table"] != named.group(1):
                continue
            doc = json.loads((self.night / s["table"] / "table.json").read_text(encoding="utf-8"))  # fmt: skip
            if s["seat"] != "gm" and key(doc["gm_person"]) == sender:
                fits.append((s["table"], "player"))
            if s["seat"] == "gm":
                fits += [(s["table"], x["seat"]) for x in doc["seats"] if key(x["seat"]) == sender]  # fmt: skip
        if len(fits) == 1:
            return fits[0]
        if not fits:
            where = f"at {named.group(1)}" if named else "at your tables"
            return f"from no one {where} who could send it, set aside"
        return "it names no table and could be for more than one, set aside"

    def take(self, pkg: Path) -> str:
        """Receive one package into the seat it is for; say what happened."""
        try:
            doc = json.loads(pkg.read_text(encoding="utf-8"))
            sender = doc["from"]
        except (ValueError, KeyError, TypeError):
            return f"{pkg.name}: not a package, set aside"
        placed = self.place(sender, doc.get("note", ""))
        if isinstance(placed, str):
            return f"{pkg.name}: {placed}"
        tid, by = placed
        running = by != "player"
        box = (
            self.night / tid / ("gm/table/record" if running else f"{self.person}/box")
        )
        got = subprocess.run(
            [sys.executable, str(SHARE), "receive", "--box", str(box), "--id",
             str(self.night / "people" / self.person / "id"), "--package", str(pkg),
             "--now", now_after(box)],
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        first = got.stdout.strip().splitlines()[0] if got.stdout.strip() else ""
        if got.returncode == 2 or not first:
            return f"{pkg.name}: refused by share ({(got.stderr or got.stdout).strip()[:120]})"  # fmt: skip
        if first.startswith("already received"):  # the same package again: said once
            return f"{pkg.name}: {first}, at {tid}"
        verdict = first.split()[-1]
        why = [ln.strip() for ln in got.stdout.splitlines()[1:] if ln.startswith("  ") and verdict != "good"]  # fmt: skip
        tj = self.night / tid / "table.json"
        table = json.loads(tj.read_text(encoding="utf-8"))
        when = now_after(box)
        refused = {"package": pkg.name, "verdict": verdict, "why": why[:2], "arrived": when, "just": True}  # fmt: skip
        if running:
            said = self.from_player(table, tid, by, doc, pkg, when) if verdict == "good" else []  # fmt: skip
            if verdict != "good":
                table["gm"].setdefault("refused", []).append(refused | {"from": by})
            table["gm"]["chain"] = verify(box)
            tj.write_text(json.dumps(table, indent=1), encoding="utf-8")
            return f"{pkg.name}: {verdict}, from {by} at {tid}" + "".join(f"; {x}" for x in said)  # fmt: skip
        seat = next(s for s in table["seats"] if s["seat"] == self.person)
        if verdict == "good":
            seat["received"] += [
                {"what": a["data"], "claim": a["claim"], "from": table["gm_person"],
                 "cites": sorted(set(a.get("places", {}).values())), "verdict": verdict,
                 "arrived": when, "just": True}
                for a in doc["answers"]
            ]  # fmt: skip
        else:
            seat.setdefault("refused", []).append(refused)
        seat["chain"] = verify(box)
        tj.write_text(json.dumps(table, indent=1), encoding="utf-8")
        return f"{pkg.name}: {verdict}, at {tid}"

    def from_player(self, table: dict, tid: str, by: str, doc: dict, pkg: Path, when: str) -> list[str]:  # fmt: skip
        """What a player sent the GM, put where the GM's screen shows it. An
        offer or a creature is handed in through game-master's `offer`, as the
        player's character: it waits on the GM's call. A note is only shown."""
        seat = next(s for s in table["seats"] if s["seat"] == by)
        gm, said = table["gm"], []
        world = (
            self.night / tid / "gm" / "table" / "worlds" / f"{table['world_id']}.json"
        )
        for a in doc["answers"]:
            kind = a["claim"].split(":", 1)[0]
            lines = a["data"].splitlines()
            says = lines[0].split(": ", 1)[-1]
            base = {"from": by, "plays": seat["plays"], "says": says, "arrived": when, "just": True}  # fmt: skip
            if kind == "note":
                gm.setdefault("notes", []).append(base)
                said.append(f"a note from {by}")
                continue
            if kind not in ("offer", "creature"):
                said.append(f"{kind!r} isn't something a player sends; left on the record only")  # fmt: skip
                continue
            fact = says if kind == "offer" else f"A creature for the bestiary: {says}"
            got = subprocess.run(
                [sys.executable, str(GM), "--box", str(self.night / tid / "gm" / "table" / "record"),
                 "offer", seat["plays_id"], fact, "--world", str(world),
                 "--now", now_after(self.night / tid / "gm" / "table" / "record")],
                capture_output=True, text=True, check=False,
            )  # fmt: skip
            m = re.search(r"(proposal:[0-9a-f]{64})", got.stdout)
            item = base | {"subject": m.group(1) if m else "", "state": "waiting on your call" if m else "not handed in"}  # fmt: skip
            if kind == "offer":
                gm.setdefault("offers", []).append(
                    {"by": seat["plays_id"], "seat": by, "fact": says, "subject": item["subject"],
                     "state": item["state"], "travelled": True, "arrived": when, "just": True}
                )  # fmt: skip
            else:
                item["picture"], item["picture_said"] = self.picture(lines, pkg, tid)
                gm.setdefault("creatures", []).append(item)
            said.append(f"{kind} from {by} as {seat['plays']}, {item['state']}")
        return said

    def picture(self, lines: list[str], pkg: Path, tid: str) -> tuple[str, str]:
        """The picture beside a creature's package, kept only if it is the one
        the player sealed (its SHA-256 is in the sealed words)."""
        want = next((ln.split()[-1] for ln in lines if ln.startswith("Picture: sha256 ")), None)  # fmt: skip
        beside = [p for p in pkg.parent.glob(pkg.stem + ".*") if p.suffix.lower() in PICTURES]  # fmt: skip
        if want is None:
            return "", "no picture"
        if not beside:
            return "", "the picture didn't come with it"
        pic = beside[0]
        data = pic.read_bytes()
        self.kept.mkdir(exist_ok=True)
        shutil.move(str(pic), str(self.kept / pic.name))
        if hashlib.sha256(data).hexdigest() != want:
            return (
                "",
                "the picture beside it isn't the one sealed: left out, kept as it came",
            )
        keep = self.night / tid / "gm" / "pictures"
        keep.mkdir(exist_ok=True)
        (keep / (want[:16] + pic.suffix.lower())).write_bytes(data)
        if len(data) > 1_500_000:
            return (
                "",
                f"kept at {keep / (want[:16] + pic.suffix.lower())}, too big to show here",
            )
        mime = {".jpg": "jpeg", ".jpeg": "jpeg"}.get(
            pic.suffix.lower(), pic.suffix.lower()[1:]
        )
        return f"data:image/{mime};base64," + base64.b64encode(
            data
        ).decode(), "the one sealed"

    def quiet(self) -> None:
        """A new round arrived: what was just arrived before is not any more."""
        for tj in self.tables().values():
            doc = json.loads(tj.read_text(encoding="utf-8"))
            for s in doc["seats"]:
                if s["seat"] == self.person:
                    for r in s["received"] + s.get("refused", []):
                        r.pop("just", None)
            if doc["gm_person"] == self.person:
                for part in ("offers", "notes", "creatures", "refused"):
                    for r in doc["gm"].get(part, []):
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
