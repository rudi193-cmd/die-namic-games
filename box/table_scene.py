"""table_scene.py: a week of tables, a box for every seat. Python 3.9+.

    python box/table_scene.py run   --to DIR [--now TS]
    python box/table_scene.py later --to DIR --table ID --rule NAME

The boxes and stacks behind the GM's and the players' screens
(boxes/looks/mock.md), laid as willow's annex demo lays its compartments:
each seat is its own box (a pile, a record and a key of its own), so access
to one is never access to another, and what crosses goes only as a sealed
package, a `sent` row on one chain and a `received` on the other (willow's
`share`).

**One person, many tables** (the maintainer: "a gm can be a player
sometimes too, at different tables"). A person has one identity, an Ed25519
key pair kept outside every box (share/README.md), and a box for each seat
they hold. Rook runs The Lantern Fair on Thursday, where Ash and Wren play;
Ash runs Ironworks on Sunday, where Wren and Rook play. Every GM's box holds
the one binder this repository keeps (box/binder). Every name is a placeholder.

**Demo keys, by the maintainer's choice (2026-11-22).** Nobody's own key is
made or read. Every seat here is fictional, its key made by the scene in
DIR and thrown away with it, as annex's are; the seals this plays through
stand in for a GM's yes, so the screens can show a page crossing. A real
table's box is laid at home, with the GM's key (open.md:492), and nothing
in it is sealed but by them.

DIR, which must not exist yet and must be outside this repository, gets
DIR/people/<person>/id, each person's identity, and for each table:

- DIR/<table>/gm: the GM's seat, laid by open_table.py (the binder as its
  pile, the house rules and the story waiting on the seal), its prep sheet run.
- DIR/<table>/<person>: each player's seat, over a pile of its own: their
  character as the GM handed it (me.md) and their notes (notes.md). Never
  the binder.

Then, at each table, in order:

1. The GM may look something up in the binder and seal the answer: a page
   clipped into the screen, the GM's alone, sent to no one (Thursday: the
   clockwork hound).
2. The GM seals a house rule and sends it to the table: one package for each
   player's identity. Each player receives it: a `received` row, `good`.
3. The story's first beat is played: 2d6 rolled on the GM's record by
   game-master (seeded by the record's tip; nobody picks the faces), the
   dice box's roll. A player may bring something in as their character
   (game-master's `offer`, Thursday: Ash as Tamsin): it waits on the GM's
   call, and nothing here answers it.
4. The wall: a player's box, asked about the binder, has nothing on record
   (exit 42); the GM's box, asked the same, serves the binder's page.
5. Each player's seat runs seat-stack.md; every chain verifies.

`later` is the night going on: the GM of table ID seals the house rule NAME
(still waiting on the seal) with the same stand-in key and sends it to each
player, the package written into that person's drop folder, DIR/drop/<person>
(a synced folder or one they save files into: the way it travels is the
table's). box/follow.py, on each person's device, receives what lands there.

It writes DIR/<table>/table.json, what a table's screens are built from,
and DIR/people.json, each person's seats (never a box, a key or a pile in
either), and a transcript to standard output. Exit 0 when the week plays as
told, 1 when a step went otherwise, 2 refused.
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
WORLDS = HERE / "worlds"

#: the people: placeholders, named for no one and for no name the binder or a
#: story uses (the binder's notes have a Juno and a Pell)
PEOPLE = ["rook", "ash", "wren"]
#: the tables, each with its GM, its players and what happens there
TABLES = [
    {"id": "thursday", "day": "Thursday", "world": "lantern-fair", "gm": "rook",
     "seats": [
         {"person": "ash", "plays": "tamsin", "carries": ["a lamp hook", "matches"],
          "notes": ["Ask Old Vell about the river.", "The stall at the end had no light."]},
         {"person": "wren", "plays": "oro", "carries": ["three juggling balls"],
          "notes": ["Oro owes the pie stall a coin."]},
     ],
     "lookup": ("clockwork hound stats", "monsters/clockwork-hound.md",
                ("Clockwork hound: Grit 3, Wit 0, Heart 0, Weird 1. Hits 6; brass, so a "
                 "blade does half. Bite 2d6 + Grit. A bucket of water stops it for a round."),
                "the binder's page on the hound"),
     "to_table": "Draws",
     "offer": ("ash", "tamsin", "Tamsin keeps a spare lantern under the stall.")},
    {"id": "sunday", "day": "Sunday", "world": "ironworks", "gm": "ash",
     "seats": [
         {"person": "wren", "plays": "sable", "carries": ["her grandfather's journal", "a torch"],
          "notes": ["The mold is behind the last furnace."]},
         {"person": "rook", "plays": "tel", "carries": ["the city's ledger", "a phone with 9% battery"],
          "notes": ["Sixty years missing from the pour records."]},
     ],
     "lookup": None, "to_table": "Dice", "offer": None},
]  # fmt: skip
#: what every player's box is asked, to show it can't reach the binder
WALL = "clockwork hound weakness"


class Week:
    def __init__(self, to: Path, now: datetime):
        self.to, self.now = to, now
        self.wrong: list[str] = []
        self.pub: dict[str, str] = {}
        self.people: dict[str, list] = {p: [] for p in PEOPLE}

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

    def ident(self, person: str) -> Path:
        return self.to / "people" / person / "id"

    def identities(self) -> None:
        for p in PEOPLE:
            (self.to / "people" / p).mkdir(parents=True)
            self.pub[p] = self.run(SHARE, "id", "--to", self.ident(p)).stdout.strip()
            (self.to / "people" / p / "pub").write_text(
                self.pub[p] + "\n"
            )  # public: given to people
            (self.to / "drop" / p).mkdir(parents=True)  # where packages for them land
            print(f"{p:6} one identity for every table, {self.pub[p][:12]}…")

    def play(self) -> int:
        self.to.mkdir(parents=True)
        made = self.now.strftime("%Y-%m-%dT%H:%M:%SZ")
        print("## the people")
        self.identities()
        for t in TABLES:
            doc = Table(self, t).play()
            doc["made"] = made
            (self.to / t["id"] / "table.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")  # fmt: skip
        (self.to / "people.json").write_text(json.dumps(self.people, indent=1), encoding="utf-8")  # fmt: skip
        print(f"\nwrote {self.to / 'people.json'} and each table's table.json")
        for w in self.wrong:
            print(f"WRONG: {w}")
        return 1 if self.wrong else 0


class Table:
    def __init__(self, week: Week, t: dict):
        self.w, self.t = week, t
        self.dir = week.to / t["id"]
        self.world = json.loads(
            (WORLDS / f"{t['world']}.json").read_text(encoding="utf-8")
        )
        self.chars = {c["id"]: c for c in self.world["characters"]}
        self.got: dict[str, list] = {s["person"]: [] for s in t["seats"]}

    def box(self, person: str) -> Path:
        if person == self.t["gm"]:
            return self.dir / "gm" / "table" / "record"
        return self.dir / person / "box"

    def stats(self, char: dict) -> dict:
        base = self.world.get("base_stat", 0)
        return {k: char.get("stats", {}).get(k, base) for k in self.world["stats"]}

    def name(self, cid: str) -> str:
        return self.chars[cid]["name"]

    # the seats

    def lay_gm(self) -> dict:
        (self.dir / "gm").mkdir(parents=True)
        got = self.w.run(OPEN_TABLE, "open", "--table", self.dir / "gm" / "table",
                         "--key", self.dir / "gm" / "key", "--world", self.t["world"],
                         "--now", self.w.ts(), want=(42,))  # fmt: skip
        waiting = {}
        for line in got.stdout.splitlines():
            m = re.match(r"waiting\s+(.+?): .* (proposal:[0-9a-f]{64})$", line)
            if m:
                waiting[m.group(1)] = m.group(2)
        print(
            f"  {self.t['gm']:6} GM: box laid by open_table, {len(waiting)} house rules waiting"
        )
        return waiting

    def lay_seat(self, s: dict) -> None:
        who, char = s["person"], self.chars[s["plays"]]
        pile = self.dir / who / "pile"
        pile.mkdir(parents=True)
        (pile / "me.md").write_text(
            f"# {char['name']}\n\n{char['name']}: {char['role']}.\n\n"
            + ", ".join(f"{k} {v}" for k, v in self.stats(char).items())
            + ".\n\nCarries: " + ", ".join(s["carries"]) + ".\n",
            encoding="utf-8",
        )  # fmt: skip
        (pile / "notes.md").write_text("# My notes\n\n" + "\n\n".join(s["notes"]) + "\n", encoding="utf-8")  # fmt: skip
        self.w.run(KERNEL, "init", "--box", self.box(who), "--pile", pile,
                   "--key", self.dir / who / "key", "--now", self.w.ts())  # fmt: skip
        print(f"  {who:6} plays {char['name']}: a box over their own pile")

    # the acts

    def seal_answer(self, question: str, source: str, data: str, claim: str) -> str:
        """The GM asks the binder, writes the answer from what was served, and
        seals it with the scene's stand-in key, as annex's scene does."""
        gm = self.t["gm"]
        bite = json.loads(self.w.run(KERNEL, "bite", "--box", self.box(gm), question,
                                     "--now", self.w.ts(), want=(0, 42)).stdout or "{}")  # fmt: skip
        cites = [s["id"] for s in bite.get("served", []) if s["where"].startswith(source + ":")]  # fmt: skip
        if not cites:
            self.w.wrong.append(f"{gm}: '{question}' served nothing from {source}")
            return ""
        sug = self.dir / "gm" / "suggestion.jsonl"
        sug.write_text(json.dumps({"path": f"screen/{cites[0][:8]}.md", "data": data,
                                   "cites": cites[:1], "claim": claim}) + "\n")  # fmt: skip
        out = self.w.run(KERNEL, "propose", "--box", self.box(gm), "--file", sug,
                         "--now", self.w.ts(), want=(42,)).stdout  # fmt: skip
        sug.unlink()
        subj = out.split()[1] if out.startswith("pass") else ""
        self.seal(subj)
        return subj

    def seal(self, subj: str) -> None:
        self.w.run(KERNEL, "seal", "--box", self.box(self.t["gm"]), subj, "--now", self.w.ts())  # fmt: skip

    def send(self, subj: str, to: str, note: str) -> Path:
        gm = self.t["gm"]
        pkg = self.dir / f"{gm}-to-{to}.pkg"
        self.w.run(SHARE, "send", "--box", self.box(gm), "--id", self.w.ident(gm),
                   "--answer", subj, "--for", self.w.pub[to], "--to", pkg,
                   "--note", note, "--now", self.w.ts())  # fmt: skip
        return pkg

    def receive(self, who: str, pkg: Path) -> str:
        got = self.w.run(SHARE, "receive", "--box", self.box(who), "--id", self.w.ident(who),
                         "--package", pkg, "--now", self.w.ts())  # fmt: skip
        verdict = "good" if re.search(r"\bgood\b", got.stdout) else "not good"
        if verdict != "good":
            self.w.wrong.append(
                f"{who} received {pkg.name}: {got.stdout.strip()[:200]}"
            )
            return verdict
        doc = json.loads(
            pkg.read_text(encoding="utf-8")
        )  # what crossed, from the package that held
        self.got[who] += [
            {"what": a["data"], "claim": a["claim"], "from": self.t["gm"],
             "cites": sorted(set(a.get("places", {}).values())), "verdict": verdict}
            for a in doc["answers"]
        ]  # fmt: skip
        return verdict

    def asks(self, who: str, question: str) -> dict:
        got = self.w.run(KERNEL, "bite", "--box", self.box(who), question,
                         "--now", self.w.ts(), want=(0, 42))  # fmt: skip
        served = json.loads(got.stdout or "{}").get("served", [])
        return {"exit": got.returncode, "served": [s["where"] for s in served[:3]]}

    def verify(self, who: str) -> str:
        return self.w.run(KERNEL, "verify", "--box", self.box(who)).stdout.strip()

    # what the screens read

    def binder_pages(self, folder: str) -> list[dict]:
        out = []
        for p in sorted((BINDER / folder).glob("*.md")):
            lines = p.read_text(encoding="utf-8").splitlines()
            title = lines[0].lstrip("# ").strip() if lines else p.stem
            body = [ln.strip() for ln in lines[1:] if ln.strip()]
            out.append({"id": p.stem, "title": title, "lines": body, "where": f"{folder}/{p.name}"})  # fmt: skip
        return out

    def house_rules(self) -> list[dict]:
        text = (BINDER / "house-rules.md").read_text(encoding="utf-8")
        parts = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
        return [{"title": p.splitlines()[0].strip(),
                 "text": " ".join(ln.strip() for ln in p.splitlines()[1:] if ln.strip())}
                for p in parts]  # fmt: skip

    def play(self) -> dict:
        t, gm = self.t, self.t["gm"]
        print(f"\n## {t['day']}: {self.world['title']}, run by {gm}")
        waiting = self.lay_gm()
        left = {k: v for k, v in waiting.items() if k != t["to_table"]}
        (self.dir / "gm" / "waiting.json").write_text(
            json.dumps(left, indent=1)
        )  # the GM's own
        for s in t["seats"]:
            self.lay_seat(s)

        on_screen = []
        if t["lookup"]:
            subj = self.seal_answer(*t["lookup"])
            on_screen.append({"what": t["lookup"][2], "cite": t["lookup"][1] + ":5", "subject": subj})  # fmt: skip
            print(f"  {gm} seals a page for the screen: {t['lookup'][1]}")
        rule = waiting.get(t["to_table"], "")
        if not rule:
            self.w.wrong.append(f"open_table left no '{t['to_table']}' rule waiting")
        self.seal(rule)
        sent = []
        for s in t["seats"]:
            pkg = self.send(rule, s["person"], f"house rule: {t['to_table']}")
            verdict = self.receive(s["person"], pkg)
            sent.append({"to": s["person"], "package": pkg.name, "received": verdict})
        print(f"  {gm} seals the house rule '{t['to_table']}' and sends it to the table: "
              + ", ".join(f"{x['to']} {x['received']}" for x in sent))  # fmt: skip

        world = self.dir / "gm" / "table" / "worlds" / f"{t['world']}.json"
        beat = self.world["scenes"][0]["beats"][0]
        acted = self.w.run(GM, "--box", self.box(gm), "act", beat["suggests"],
                           "--world", world, "--now", self.w.ts()).stdout.strip()  # fmt: skip
        print("  " + acted.splitlines()[0] if acted else "  (no roll)")
        rows = [json.loads(ln) for ln in (self.box(gm) / "record.jsonl").read_text().splitlines()]  # fmt: skip
        roll = next(r for r in rows[::-1] if r["kind"] == "roll")
        told = next(r for r in rows[::-1] if r["kind"] == "table-beat")
        status = self.w.run(
            GM, "--box", self.box(gm), "status", "--world", world
        ).stdout
        dice = {"by": told["character"], "beat": told["beat"], "stat": told["stat"],
                "faces": roll["faces"][0], "bonus": told["bonus"],
                "total": roll["total"] + told["bonus"], "band": told["band"],
                "text": told["text"], "rows": [roll["n"], told["n"]]}  # fmt: skip
        odds = [ln.strip() for ln in status.splitlines() if re.match(r"\s*\*?\s*[A-Z][a-z]+\s+\+\d", ln)]  # fmt: skip
        nxt = next((ln[5:] for ln in status.splitlines() if ln.startswith("beat ")), "")

        offers = []
        if t["offer"]:
            seat, who, fact = t["offer"]
            out = self.w.run(GM, "--box", self.box(gm), "offer", who, fact,
                             "--world", world, "--now", self.w.ts(), want=(42,)).stdout  # fmt: skip
            m = re.search(r"(proposal:[0-9a-f]{64})", out)
            if not m:
                self.w.wrong.append(f"the offer was not handed in: {out.strip()[:200]}")
            offers.append({"by": who, "seat": seat, "fact": fact, "subject": m.group(1) if m else "",
                           "state": "waiting on the GM's call"})  # fmt: skip
            print(
                f"  {seat} brings something in as {self.name(who)}: {fact} (waits on {gm})"
            )

        wall = {}
        for who in [gm] + [s["person"] for s in t["seats"]]:
            wall[who] = self.asks(who, WALL)
            if (who == gm) != (wall[who]["exit"] == 0):
                self.w.wrong.append(f"the wall at {t['id']}: {who} answered otherwise")
        print(
            "  the wall: " + ", ".join(f"{k} exit {v['exit']}" for k, v in wall.items())
        )

        prep = self.w.run(OPEN_TABLE, "prep", "--table", self.dir / "gm" / "table", want=(0, 42))  # fmt: skip
        prep_line = next(
            (ln for ln in prep.stdout.splitlines()[::-1] if "steps" in ln), ""
        )
        stacks = {}
        for s in t["seats"]:
            run = self.dir / s["person"] / "run"
            self.w.run(STACK, "--box", self.box(s["person"]), "--stack", SEAT_STACK, "--to", run, want=(0, 42))  # fmt: skip
            log = run / "00-stack.txt"
            stacks[s["person"]] = (
                log.read_text().strip().splitlines()[-1] if log.exists() else ""
            )
        chains = {
            who: self.verify(who) for who in [gm] + [s["person"] for s in t["seats"]]
        }
        print(f"  {gm} prep: {prep_line}; " + "; ".join(f"{k}: {v}" for k, v in chains.items()))  # fmt: skip

        rules = self.house_rules()
        for r in rules:
            r["state"] = ("sent to the table" if r["title"] == t["to_table"]
                          else "waiting on your seal" if r["title"] in waiting else "")  # fmt: skip
        scene = self.world["scenes"][0]
        places = {p["id"]: p["name"] for p in self.world.get("places", [])}
        self.w.people[gm].append({"table": t["id"], "day": t["day"], "title": self.world["title"], "seat": "gm"})  # fmt: skip
        seats = []
        for s in t["seats"]:
            c = self.chars[s["plays"]]
            seats.append({
                "seat": s["person"], "name": s["person"].title(), "plays": c["name"],
                "role": c["role"], "stats": self.stats(c), "carries": s["carries"],
                "notes": s["notes"], "received": self.got[s["person"]],
                "offered": [o for o in offers if o["seat"] == s["person"]],
                "wall": wall[s["person"]], "stack": stacks[s["person"]],
                "chain": chains[s["person"]],
            })  # fmt: skip
            self.w.people[s["person"]].append({"table": t["id"], "day": t["day"], "title": self.world["title"],
                                               "seat": s["person"], "plays": c["name"]})  # fmt: skip
        return {
            "table_id": t["id"], "day": t["day"], "gm_person": gm, "demo_keys": True,
            "world": {"title": self.world["title"], "setting": self.world["setting"],
                      "scenes": self.world["scenes"], "places": places},
            "gm": {
                "bestiary": self.binder_pages("monsters"), "people": self.binder_pages("people"),
                "previously": self.binder_pages("sessions")[::-1], "house_rules": rules,
                "on_screen": on_screen,
                "on_table": [{"what": f"house rule: {t['to_table']}", "subject": rule, "sent": sent}],
                "your_call": [k for k in waiting if k != t["to_table"]], "offers": offers,
                "prep": prep_line, "chain": chains[gm], "wall": wall[gm],
                "dice": dice, "next": {"beat": nxt, "odds": odds}, "done": [told["beat"]],
            },
            "table": {
                "_what": "what everyone at the table sees and hears: the scene read out, "
                "the dice landing in the box, whose turn it is; never the binder",
                "scene": {"title": scene["title"], "opening": scene["opening"],
                          "place": places.get(scene["place"], "")},
                "played": [{"by": self.name(told["character"]), "prompt": beat["prompt"], "text": told["text"]}],
                "dice": {k: dice[k] for k in ("faces", "bonus", "total", "band", "stat")}
                | {"by": self.name(told["character"])},
                "next": re.sub(r"^\S+ \([a-z]+\), ", "", nxt),  # "Oro's turn: ..."
            },
            "seats": seats,
        }  # fmt: skip


def after(box: Path) -> str:
    """A minute after the box's last row: the night goes on from where it is."""
    last = json.loads((box / "record.jsonl").read_text().splitlines()[-1])["ts"]
    t = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    t += timedelta(minutes=1)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def later(to: Path, tid: str, rule: str) -> int:
    """The GM of table tid seals a waiting house rule (the stand-in key) and
    sends it into each player's drop folder."""
    tj = to / tid / "table.json"
    if not tj.is_file():
        print(f"refused: no table {tid} in {to}", file=sys.stderr)
        return 2
    doc = json.loads(tj.read_text(encoding="utf-8"))
    waiting = json.loads((to / tid / "gm" / "waiting.json").read_text())
    if rule not in waiting:
        print(f"refused: '{rule}' isn't waiting on the seal at {tid} ({', '.join(waiting)})", file=sys.stderr)  # fmt: skip
        return 2
    gm, box, subj = (
        doc["gm_person"],
        to / tid / "gm" / "table" / "record",
        waiting.pop(rule),
    )
    wrong = []

    def go(*argv):
        got = subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, check=False)  # fmt: skip
        if got.returncode != 0:
            wrong.append(f"{Path(str(argv[0])).name} {argv[1]}: {(got.stderr or got.stdout).strip()[:200]}")  # fmt: skip
        return got

    go(KERNEL, "seal", "--box", box, subj, "--now", after(box))
    sent = []
    for s in doc["seats"]:
        pub = (to / "people" / s["seat"] / "pub").read_text().strip()
        pkg = to / "drop" / s["seat"] / f"{tid}-{rule.lower().replace(' ', '-')}.pkg"
        go(SHARE, "send", "--box", box, "--id", to / "people" / gm / "id", "--answer", subj,
           "--for", pub, "--to", pkg, "--note", f"house rule: {rule}", "--now", after(box))  # fmt: skip
        sent.append({"to": s["seat"], "package": pkg.name, "received": "sent"})
        print(f"{gm} sends '{rule}' to {s['seat']}: {pkg}")
    (to / tid / "gm" / "waiting.json").write_text(json.dumps(waiting, indent=1))
    doc["gm"]["on_table"].append(
        {"what": f"house rule: {rule}", "subject": subj, "sent": sent}
    )
    doc["gm"]["your_call"] = [r for r in doc["gm"]["your_call"] if r != rule]
    for r in doc["gm"]["house_rules"]:
        if r["title"] == rule:
            r["state"] = "sent to the table"
    doc["gm"]["chain"] = go(KERNEL, "verify", "--box", box).stdout.strip()
    tj.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    for w in wrong:
        print(f"WRONG: {w}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["later"]:
        opts = dict(zip(argv[1::2], argv[2::2]))
        if len(argv) != 7 or set(opts) != {"--to", "--table", "--rule"}:
            print(__doc__.split("\n\n")[1], file=sys.stderr)
            return 2
        return later(Path(opts["--to"]).resolve(), opts["--table"], opts["--rule"])
    if len(argv) < 3 or argv[0] != "run" or argv[1] != "--to":
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    to = Path(argv[2]).resolve()
    now = datetime(2026, 11, 22, 19, 0, tzinfo=timezone.utc)
    if len(argv) == 5 and argv[3] == "--now":
        now = datetime.strptime(argv[4], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)  # fmt: skip
    if to.exists():
        print(f"refused: {to} is already there; a week is laid fresh", file=sys.stderr)
        return 2
    try:
        to.relative_to(HERE.parent)
        print(
            "refused: DIR is inside the repository; its keys would be", file=sys.stderr
        )
        return 2
    except ValueError:
        pass
    return Week(to, now).play()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
