"""bring.py: a player sends something back to the GM. Python 3.9+.

    python box/bring.py hand --night DIR --person NAME --table ID --kind KIND "WORDS" [--picture FILE]
    python box/bring.py send --night DIR --person NAME --table ID --proposal proposal:<sha256>

Run on the player's own device, at a table they play at (DIR is what
box/table_scene.py laid). KIND is one of:

- offer:    something brought to the table as their character ("Tamsin
            keeps a spare lantern under the stall"); on the GM's record it
            waits on the GM's call, and only the GM's yes makes it canon;
- note:     a word for the GM's eyes ("I'll be late on Sunday"), shown on
            the GM's screen, never a call, never canon;
- creature: a creature or character, typed (the maintainer: "typing should
            be the main way. the picture is just a picture"), with a picture
            beside it if there is one; it waits on the GM's yes for the bestiary.

`hand` writes the words into the seat's own pile (brought/N-KIND.md), the
picture beside the pile (pictures/, never read as words), and hands them in
through the kernel: a proposal that cites the player's own page, waiting on
the player's own seal. That seal says only "this is what I brought, in my
words" (the maintainer, 2026-11-22). Then `send` packs the sealed answer for
the GM's identity with willow's `share` into the GM's drop folder,
DIR/drop/<gm>, the picture beside the package under the same name; the
sealed words carry the picture's SHA-256, so the GM's side keeps the
picture only if it is the one sealed. box/follow.py, on the GM's device,
receives it.

This never seals, declines or reads a seal key; `share send` refuses an
answer the player has not sealed. Exit 0 sent; 42 handed in, waiting on
the player's seal; 2 refused.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
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
KINDS = {"offer": "Offer", "note": "Note to the GM", "creature": "Creature, for the bestiary"}  # fmt: skip
PICTURES = (".png", ".jpg", ".jpeg", ".webp", ".gif")
STOP = {"a", "an", "the", "of", "to", "in", "on", "at", "is", "are", "was", "it", "its", "and", "or", "for", "with", "my", "i", "me"}  # fmt: skip


def fail(why: str) -> int:
    print(f"refused: {why}", file=sys.stderr)
    return 2


def after(box: Path) -> str:
    """Now, or a minute after the box's last row if that is later."""
    t = datetime.now(timezone.utc).replace(microsecond=0)
    last = json.loads((box / "record.jsonl").read_text().splitlines()[-1])["ts"]
    then = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return max(t, then + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(*argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, check=False)  # fmt: skip


class Seat:
    def __init__(self, night: Path, person: str, tid: str):
        self.night, self.person, self.tid = night, person, tid
        self.tj = night / tid / "table.json"
        self.doc = json.loads(self.tj.read_text(encoding="utf-8"))
        self.me = next((s for s in self.doc["seats"] if s["seat"] == person), None)
        self.dir = night / tid / person
        self.box = self.dir / "box"

    def save(self) -> None:
        self.tj.write_text(json.dumps(self.doc, indent=1), encoding="utf-8")


def hand(seat: Seat, kind: str, words: str, picture: Path | None) -> int:
    words = " ".join(words.split())
    if not words:
        return fail("say it in words: typing is the main way in")
    if picture is not None and (not picture.is_file() or picture.suffix.lower() not in PICTURES):  # fmt: skip
        return fail(f"no picture at {picture} (a .png, .jpg, .webp or .gif)")
    brought = seat.me.setdefault("brought", [])
    n = len(brought) + 1
    head = f"{KINDS[kind]}, as {seat.me['plays']}" if kind == "offer" else KINDS[kind]
    data = f"{head}: {words}"
    pic = None
    if picture is not None:
        digest = hashlib.sha256(picture.read_bytes()).hexdigest()
        pic = f"{n}-{kind}{picture.suffix.lower()}"
        (seat.dir / "pictures").mkdir(exist_ok=True)
        shutil.copy(
            picture, seat.dir / "pictures" / pic
        )  # beside the pile, never read as words
        data += f"\nPicture: sha256 {digest}"
    page = seat.dir / "pile" / "brought" / f"{n}-{kind}.md"
    page.parent.mkdir(exist_ok=True)
    page.write_text(f"# {KINDS[kind]}\n\n{data}\n", encoding="utf-8")
    # asked in a few of its own words, so the page is served, not echoed
    content = sorted({w for w in re.findall(r"[a-z0-9]+", words.lower()) if w not in STOP}, key=len)  # fmt: skip
    question = " ".join([kind, *content[-3:]])
    bite = json.loads(run(KERNEL, "bite", "--box", seat.box, question, "--now", after(seat.box)).stdout or "{}")  # fmt: skip
    cites = [s["id"] for s in bite.get("served", []) if s["where"].startswith(f"brought/{n}-{kind}.md:")]  # fmt: skip
    if not cites:
        return fail(f"your box didn't serve your own page for '{question}'")
    sug = seat.dir / "suggestion.jsonl"
    sug.write_text(json.dumps({"path": f"brought/{n}-{kind}-sealed.md", "data": data, "cites": cites[:1],
                               "claim": f"{kind}: in {seat.person}'s own words"}) + "\n")  # fmt: skip
    out = run(KERNEL, "propose", "--box", seat.box, "--file", sug, "--now", after(seat.box)).stdout  # fmt: skip
    sug.unlink()
    if not out.startswith("pass"):
        return fail(f"the kernel didn't take it: {out.strip()[:200]}")
    subj = out.split()[1]
    brought.append({"kind": kind, "says": words, "subject": subj, "picture": pic,
                    "state": "waiting on your own seal"})  # fmt: skip
    seat.save()
    print(f"handed in as {subj}: {data.splitlines()[0]}")
    print('it waits on your own seal ("this is what I brought, in my words"):')
    print(f"  python kernel.py seal --box {seat.box} {subj}")
    print(f"then: python box/bring.py send --night {seat.night} --person {seat.person} --table {seat.tid} --proposal {subj}")  # fmt: skip
    return 42


def send(seat: Seat, subj: str) -> int:
    item = next((b for b in seat.me.get("brought", []) if b["subject"] == subj), None)
    if item is None:
        return fail(f"{subj} isn't something you handed in at {seat.tid}")
    if item["state"].startswith("sent"):
        return fail(f"{subj} was sent already")
    gm = seat.doc["gm_person"]
    gm_key = (seat.night / "people" / gm / "pub").read_text().strip()
    n = seat.me["brought"].index(item) + 1
    pkg = seat.night / "drop" / gm / f"{seat.tid}-{seat.person}-{n}-{item['kind']}.pkg"
    if pkg.exists():
        return fail(f"{pkg} is there already")
    got = run(SHARE, "send", "--box", seat.box, "--id", seat.night / "people" / seat.person / "id",
              "--answer", subj, "--for", gm_key, "--to", pkg, "--note", f"{item['kind']} from {seat.person}, at {seat.tid}",
              "--now", after(seat.box))  # fmt: skip
    if got.returncode != 0:  # not sealed by the player, or anything else share refuses
        return fail((got.stderr or got.stdout).strip().removeprefix("refused: ")[:300])
    if item["picture"]:
        shutil.copy(seat.dir / "pictures" / item["picture"], pkg.with_suffix(Path(item["picture"]).suffix))  # fmt: skip
    item["state"] = f"sent to {gm}"
    seat.save()
    print(f"sent to {gm}: {pkg}")
    return 0


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a in ("--night", "--person", "--table", "--kind", "--picture", "--proposal"):
            opts[a] = next(it, "")
        else:
            args.append(a)
    need = {"--night", "--person", "--table"}
    if not args or args[0] not in ("hand", "send") or not need <= set(opts):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    night = Path(opts["--night"]).resolve()
    if not (night / opts["--table"] / "table.json").is_file():
        return fail(f"no table {opts['--table']} in {night}")
    seat = Seat(night, opts["--person"], opts["--table"])
    if seat.me is None:
        return fail(f"{opts['--person']} doesn't play at {opts['--table']} (a GM sends with table_scene.py later)")  # fmt: skip
    if args[0] == "hand":
        if opts.get("--kind") not in KINDS or len(args) != 2:
            return fail(f"hand takes --kind ({', '.join(KINDS)}) and the words")
        pic = Path(opts["--picture"]) if opts.get("--picture") else None
        return hand(seat, opts["--kind"], args[1], pic)
    if len(args) != 1 or not opts.get("--proposal", "").startswith("proposal:"):
        return fail("send takes --proposal proposal:<sha256>")
    return send(seat, opts["--proposal"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
