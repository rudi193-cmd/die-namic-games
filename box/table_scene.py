"""table_scene.py: a night at the table, a box for every seat. Python 3.9+.

    python box/table_scene.py run --to DIR [--now TS]

The boxes and stacks behind the GM's and the players' screens
(boxes/looks/mock.md), laid as willow's annex demo lays its compartments:
each seat is its own box (a pile, a record, a key and an identity of its
own), so access to one is never access to another, and what crosses goes
only as a sealed package, a `sent` row on one chain and a `received` on the
other (willow's `share`).

**Demo keys, by the maintainer's choice (2026-11-22).** Nobody's own key is
made or read. Every seat here is fictional, its key made by the scene in
DIR and thrown away with it, as annex's are; the seals this plays through
stand in for the GM's yes, so the screens can show a page crossing. A real
table's box is laid at home, with the GM's key (open.md:492), and nothing
in it is sealed but by them.

DIR, which must not exist yet and must be outside this repository, gets:

- DIR/gm: the GM's seat, laid by open_table.py (the binder as its pile, the
  house rules and the story waiting on the seal), and its prep sheet run.
- DIR/<seat>: each player's seat, over a pile of its own: their character
  as the GM handed it (me.md) and their notes (notes.md). Never the binder.

Then, in order:

1. The GM looks up the clockwork hound in the binder and seals the answer:
   a page clipped into the screen, the GM's alone, sent to no one.
2. The GM seals the house rule on draws and sends it to the table: one
   package for each player's key.
3. Each player receives it: a `received` row on their chain, `good`.
4. The story's first beat is played: Tamsin's Grit, 2d6 rolled on the GM's
   record by game-master (seeded by the record's tip; nobody picks the
   faces), the dice box's roll.
   Then Ash brings something in as Tamsin (game-master's `offer`): it waits
   on the GM's call, and nothing here answers it.
5. The wall: a player's box, asked about the hound, has nothing on record
   (exit 42); the GM's box, asked the same, serves the binder's page.
6. Each player's seat runs seat-stack.md; every chain verifies.

It writes DIR/table.json, what the screens are built from (never a box, a
key or a pile), and a transcript to standard output. Exit 0 when the night
plays as told, 1 when a step went otherwise, 2 refused.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin

ROOT = willow_pin.root()
KERNEL = ROOT / "kernel.py"
SHARE = ROOT / "adapters" / "stdlib" / "share" / "share.py"
STACK = ROOT / "adapters" / "stdlib" / "stack" / "stack.py"
GM = ROOT / "adapters" / "stdlib" / "game-master" / "game_master.py"
OPEN_TABLE = HERE / "open_table.py"
SEAT_STACK = HERE / "seat-stack.md"
BINDER = HERE / "binder"
WORLD = HERE / "worlds" / "lantern-fair.json"

#: the players: placeholders, named for no one and for no name the binder
#: uses (its notes have a Juno and a Pell); each plays a seated character
SEATS = [
    {"seat": "ash", "name": "Ash", "plays": "tamsin",
     "carries": ["a lamp hook", "matches"],
     "notes": ["Ask Old Vell about the river.", "The stall at the end had no light."]},
    {"seat": "wren", "name": "Wren", "plays": "oro",
     "carries": ["three juggling balls"],
     "notes": ["Oro owes the pie stall a coin."]},
]  # fmt: skip
#: the GM's lookup, a page for the screen alone
HOUND = ("clockwork hound stats", "monsters/clockwork-hound.md",
         ("Clockwork hound: Grit 3, Wit 0, Heart 0, Weird 1. Hits 6; brass, so a blade "
          "does half. Bite 2d6 + Grit. A bucket of water stops it for a round."),
         "the binder's page on the hound")  # fmt: skip
#: the house rule sent to the table
TO_TABLE = "Draws"
#: what a player brings in on the night, as their character: (seat, character, fact)
OFFER = ("ash", "tamsin", "Tamsin keeps a spare lantern under the stall.")


class Night:
    def __init__(self, to: Path, now: datetime):
        self.to, self.now = to, now
        self.wrong: list[str] = []
        self.pub: dict[str, str] = {}
        self.got: dict[str, list] = {s["seat"]: [] for s in SEATS}
        self.world = json.loads(WORLD.read_text(encoding="utf-8"))
        self.out: dict = {
            "made": "",
            "demo_keys": True,
            "world": {},
            "gm": {},
            "seats": [],
        }

    def ts(self) -> str:
        self.now += timedelta(minutes=1)
        return self.now.strftime("%Y-%m-%dT%H:%M:%SZ")

    def run(self, *argv, want=(0,)) -> subprocess.CompletedProcess:
        got = subprocess.run([sys.executable, *map(str, argv)], capture_output=True,
                             text=True, stdin=subprocess.DEVNULL, check=False)  # fmt: skip
        if got.returncode not in want:
            self.wrong.append(f"{Path(str(argv[0])).name} {argv[1]}: exit "
                              f"{got.returncode} {(got.stderr or got.stdout).strip()[:200]}")  # fmt: skip
        return got

    def box(self, seat: str) -> Path:
        return (
            self.to / "gm" / "table" / "record"
            if seat == "gm"
            else self.to / seat / "box"
        )

    def ident(self, seat: str) -> Path:
        return self.to / seat / "id"

    # the seats

    def lay_gm(self) -> dict:
        (self.to / "gm").mkdir(parents=True)
        got = self.run(OPEN_TABLE, "open", "--table", self.to / "gm" / "table",
                       "--key", self.to / "gm" / "key", "--now", self.ts(), want=(42,))  # fmt: skip
        waiting = {}
        for line in got.stdout.splitlines():
            m = re.match(r"waiting\s+(.+?): .* (proposal:[0-9a-f]{64})$", line)
            if m:
                waiting[m.group(1)] = m.group(2)
        self.pub["gm"] = self.run(SHARE, "id", "--to", self.ident("gm")).stdout.strip()
        print(f"gm         box laid by open_table, {len(waiting)} house rules waiting, "
              f"identity {self.pub['gm'][:12]}…")  # fmt: skip
        return waiting

    def lay_seat(self, s: dict) -> None:
        who = s["seat"]
        char = next(c for c in self.world["characters"] if c["id"] == s["plays"])
        pile = self.to / who / "pile"
        pile.mkdir(parents=True)
        (pile / "me.md").write_text(
            f"# {char['name']}\n\n{char['name']} is a {char['role']}.\n\n"
            + ", ".join(f"{k} {v}" for k, v in self.stats(char).items())
            + ".\n\nCarries: "
            + ", ".join(s["carries"])
            + ".\n",
            encoding="utf-8",
        )
        (pile / "notes.md").write_text(
            "# My notes\n\n" + "\n\n".join(s["notes"]) + "\n", encoding="utf-8"
        )
        self.run(KERNEL, "init", "--box", self.box(who), "--pile", pile,
                 "--key", self.to / who / "key", "--now", self.ts())  # fmt: skip
        self.pub[who] = self.run(SHARE, "id", "--to", self.ident(who)).stdout.strip()
        print(f"{who:10} box laid over its own pile ({char['name']}), "
              f"identity {self.pub[who][:12]}…")  # fmt: skip

    def stats(self, char: dict) -> dict:
        base = self.world.get("base_stat", 0)
        return {k: char.get("stats", {}).get(k, base) for k in self.world["stats"]}

    # the acts

    def seal_answer(self, question: str, source: str, data: str, claim: str) -> str:
        """The GM asks the binder, writes the answer from what was served, and
        seals it with the scene's stand-in key, as annex's scene does."""
        bite = json.loads(self.run(KERNEL, "bite", "--box", self.box("gm"), question,
                                   "--now", self.ts(), want=(0, 42)).stdout or "{}")  # fmt: skip
        cites = [s["id"] for s in bite.get("served", []) if s["where"].startswith(source + ":")]  # fmt: skip
        if not cites:
            self.wrong.append(f"gm: '{question}' served nothing from {source}")
            return ""
        sug = self.to / "gm" / "suggestion.jsonl"
        sug.write_text(json.dumps({"path": f"screen/{cites[0][:8]}.md", "data": data,
                                   "cites": cites[:1], "claim": claim}) + "\n")  # fmt: skip
        out = self.run(KERNEL, "propose", "--box", self.box("gm"), "--file", sug,
                       "--now", self.ts(), want=(42,)).stdout  # fmt: skip
        sug.unlink()
        subj = out.split()[1] if out.startswith("pass") else ""
        self.seal(subj)
        return subj

    def seal(self, subj: str) -> None:
        self.run(KERNEL, "seal", "--box", self.box("gm"), subj, "--now", self.ts())

    def send(self, subj: str, s: dict, note: str) -> Path:
        pkg = self.to / f"gm-to-{s['seat']}.pkg"
        self.run(SHARE, "send", "--box", self.box("gm"), "--id", self.ident("gm"),
                 "--answer", subj, "--for", self.pub[s["seat"]], "--to", pkg,
                 "--note", note, "--now", self.ts())  # fmt: skip
        return pkg

    def receive(self, s: dict, pkg: Path) -> str:
        got = self.run(SHARE, "receive", "--box", self.box(s["seat"]), "--id",
                       self.ident(s["seat"]), "--package", pkg, "--now", self.ts())  # fmt: skip
        verdict = "good" if re.search(r"\bgood\b", got.stdout) else "not good"
        if verdict == "good":  # what crossed, read from the package that held
            doc = json.loads(pkg.read_text(encoding="utf-8"))
            self.got[s["seat"]] += [
                {"what": a["data"], "claim": a["claim"], "from": "gm",
                 "cites": sorted(set(a.get("places", {}).values())), "verdict": verdict}
                for a in doc["answers"]
            ]  # fmt: skip
        if verdict != "good":
            self.wrong.append(
                f"{s['seat']} received {pkg.name}: {got.stdout.strip()[:200]}"
            )
        return verdict

    def asks(self, seat: str, question: str) -> dict:
        got = self.run(KERNEL, "bite", "--box", self.box(seat), question,
                       "--now", self.ts(), want=(0, 42))  # fmt: skip
        served = json.loads(got.stdout or "{}").get("served", [])
        return {"exit": got.returncode, "served": [s["where"] for s in served[:3]]}

    def verify(self, seat: str) -> str:
        return self.run(KERNEL, "verify", "--box", self.box(seat)).stdout.strip()

    # what the screens read

    def binder_pages(self, folder: str) -> list[dict]:
        out = []
        for p in sorted((BINDER / folder).glob("*.md")):
            lines = [ln for ln in p.read_text(encoding="utf-8").splitlines()]
            title = lines[0].lstrip("# ").strip() if lines else p.stem
            body = [ln.strip() for ln in lines[1:] if ln.strip()]
            out.append({"id": p.stem, "title": title, "lines": body,
                        "where": f"{folder}/{p.name}"})  # fmt: skip
        return out

    def house_rules(self) -> list[dict]:
        text = (BINDER / "house-rules.md").read_text(encoding="utf-8")
        parts = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
        return [{"title": p.splitlines()[0].strip(),
                 "text": " ".join(ln.strip() for ln in p.splitlines()[1:] if ln.strip())}
                for p in parts]  # fmt: skip

    def play(self) -> int:
        self.to.mkdir(parents=True)
        self.out["made"] = self.now.strftime("%Y-%m-%dT%H:%M:%SZ")
        print("## the seats")
        waiting = self.lay_gm()
        for s in SEATS:
            self.lay_seat(s)

        print("\n## the GM's screen and the table")
        hound = self.seal_answer(*HOUND)
        print(f"  gm seals the hound's page for the screen: {hound[:22]}…")
        rule = waiting.get(TO_TABLE, "")
        if not rule:
            self.wrong.append(f"open_table left no '{TO_TABLE}' rule waiting")
        self.seal(rule)
        print(f"  gm seals the house rule '{TO_TABLE}' and sends it to the table")
        sent = []
        for s in SEATS:
            pkg = self.send(rule, s, f"house rule: {TO_TABLE}")
            verdict = self.receive(s, pkg)
            print(f"  {s['seat']} receives {pkg.name}: {verdict}")
            sent.append({"to": s["seat"], "package": pkg.name, "received": verdict})

        print("\n## the story")
        world = self.to / "gm" / "table" / "worlds" / WORLD.name
        beat = self.world["scenes"][0]["beats"][0]
        acted = self.run(GM, "--box", self.box("gm"), "act", beat["suggests"],
                         "--world", world, "--now", self.ts()).stdout.strip()  # fmt: skip
        print("  " + acted.replace("\n", "\n  "))
        rows = [
            json.loads(ln)
            for ln in (self.box("gm") / "record.jsonl").read_text().splitlines()
        ]
        roll = next(r for r in rows[::-1] if r["kind"] == "roll")
        told = next(r for r in rows[::-1] if r["kind"] == "table-beat")
        status = self.run(
            GM, "--box", self.box("gm"), "status", "--world", world
        ).stdout
        dice = {"by": told["character"], "beat": told["beat"], "stat": told["stat"],
                "faces": roll["faces"][0], "bonus": told["bonus"],
                "total": roll["total"] + told["bonus"], "band": told["band"],
                "text": told["text"], "rows": [roll["n"], told["n"]]}  # fmt: skip
        odds = [
            ln.strip()
            for ln in status.splitlines()
            if re.match(r"\s*\*?\s*[A-Z][a-z]+\s+\+\d", ln)
        ]
        nxt = next((ln[5:] for ln in status.splitlines() if ln.startswith("beat ")), "")

        seat, who, fact = OFFER
        offered = self.run(GM, "--box", self.box("gm"), "offer", who, fact,
                           "--world", world, "--now", self.ts(), want=(42,)).stdout  # fmt: skip
        m = re.search(r"(proposal:[0-9a-f]{64})", offered)
        offer = {"by": who, "seat": seat, "fact": fact, "subject": m.group(1) if m else "",
                 "state": "waiting on the GM's call"}  # fmt: skip
        if not m:
            self.wrong.append(f"the offer was not handed in: {offered.strip()[:200]}")
        print(
            f"  {seat} brings something in as {who.title()}: {fact} (waits on the GM)"
        )

        print("\n## the wall")
        wall = {}
        for seat in ["gm"] + [s["seat"] for s in SEATS]:
            wall[seat] = self.asks(seat, "clockwork hound weakness")
            print(f"  {seat:8} asked about the hound: exit {wall[seat]['exit']}, "
                  f"served {wall[seat]['served'] or 'nothing on record'}")  # fmt: skip
            if (seat == "gm") != (wall[seat]["exit"] == 0):
                self.wrong.append(f"the wall: {seat} answered otherwise")

        print("\n## the stacks")
        prep = self.run(
            OPEN_TABLE, "prep", "--table", self.to / "gm" / "table", want=(0, 42)
        )
        prep_line = next(
            (ln for ln in prep.stdout.splitlines()[::-1] if "steps" in ln), ""
        )
        print(f"  gm       prep sheet: {prep_line}")
        seat_stacks = {}
        for s in SEATS:
            run = self.to / s["seat"] / "run"
            got = self.run(STACK, "--box", self.box(s["seat"]), "--stack", SEAT_STACK,
                           "--to", run, want=(0, 42))  # fmt: skip
            last = (run / "00-stack.txt").read_text().strip().splitlines()[-1] if (run / "00-stack.txt").exists() else got.stdout.strip()[-80:]  # fmt: skip
            seat_stacks[s["seat"]] = last
            print(f"  {s['seat']:8} seat stack: {last}")

        print("\n## the chains")
        chains = {
            seat: self.verify(seat) for seat in ["gm"] + [s["seat"] for s in SEATS]
        }
        for seat, line in chains.items():
            print(f"  {seat:8} {line}")

        rules = self.house_rules()
        for r in rules:
            r["state"] = ("sent to the table" if r["title"] == TO_TABLE
                          else "waiting on your seal" if r["title"] in waiting else "")  # fmt: skip
        chars = {c["id"]: c for c in self.world["characters"]}
        self.out["world"] = {
            "title": self.world["title"], "setting": self.world["setting"],
            "scenes": self.world["scenes"],
            "places": {p["id"]: p["name"] for p in self.world.get("places", [])},
        }  # fmt: skip
        self.out["gm"] = {
            "bestiary": self.binder_pages("monsters"),
            "people": self.binder_pages("people"),
            "previously": self.binder_pages("sessions")[::-1],
            "house_rules": rules,
            "on_screen": [{"what": HOUND[2], "cite": HOUND[1] + ":5", "subject": hound}],
            "on_table": [{"what": f"house rule: {TO_TABLE}", "subject": rule, "sent": sent}],
            "your_call": [k for k in waiting if k != TO_TABLE],
            "offers": [offer],
            "prep": prep_line, "chain": chains["gm"], "wall": wall["gm"],
            "dice": dice, "next": {"beat": nxt, "odds": odds}, "done": [told["beat"]],
        }  # fmt: skip
        scene = self.world["scenes"][0]
        self.out["table"] = {
            "_what": "what everyone at the table sees and hears: the scene read out, "
            "the dice landing in the box, whose turn it is; never the binder",
            "scene": {"title": scene["title"], "opening": scene["opening"],
                      "place": self.out["world"]["places"].get(scene["place"], "")},
            "played": [{"by": chars[told["character"]]["name"], "prompt": beat["prompt"],
                        "text": told["text"]}],
            "dice": {k: dice[k] for k in ("faces", "bonus", "total", "band", "stat")}
            | {"by": chars[told["character"]]["name"]},
            "next": re.sub(r"^\S+ \([a-z]+\), ", "", nxt),  # "Oro's turn: ..."
        }  # fmt: skip
        for s in SEATS:
            c = chars[s["plays"]]
            self.out["seats"].append({
                "seat": s["seat"], "name": s["name"], "plays": c["name"], "role": c["role"],
                "stats": self.stats(c), "carries": s["carries"], "notes": s["notes"],
                "received": self.got[s["seat"]],
                "offered": [offer] if offer["seat"] == s["seat"] else [],
                "wall": wall[s["seat"]], "stack": seat_stacks[s["seat"]],
                "chain": chains[s["seat"]],
            })  # fmt: skip
        (self.to / "table.json").write_text(
            json.dumps(self.out, indent=1), encoding="utf-8"
        )
        print(f"\nwrote {self.to / 'table.json'}")
        for w in self.wrong:
            print(f"WRONG: {w}")
        return 1 if self.wrong else 0


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[0] != "run" or argv[1] != "--to":
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    to = Path(argv[2]).resolve()
    now = datetime(2026, 11, 22, 19, 0, tzinfo=timezone.utc)
    if len(argv) == 5 and argv[3] == "--now":
        now = datetime.strptime(argv[4], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    if to.exists():
        print(f"refused: {to} is already there; a night is laid fresh", file=sys.stderr)
        return 2
    try:
        to.relative_to(HERE.parent)
        print(
            "refused: DIR is inside the repository; its keys would be", file=sys.stderr
        )
        return 2
    except ValueError:
        pass
    return Night(to, now).play()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
