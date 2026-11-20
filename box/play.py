"""play.py: the way in. Pick a story, play it, make the calls, end the night. Python 3.9+.

    python box/play.py

No setup and no questions first: it opens on the stories. The first time,
it lays a box by itself (box/open_table.py's own `open`) in the folder
DIE_NAMIC_HOME names, or ~/.die-namic: the table in `table/`, the game
master's key beside it in `gm.key`, never inside it. After that it opens on
"Previously on..." when the table has made anything true, then the stories,
the ones played first.

Playing is the box's own: every move goes through session.py's steps to
game-master, and every roll through dice, as `session.py` plays it. What is
new is only what the person sees, in the words open.md gives: a roll is
"rolled 12. Great!", a decision is "Your call, GM", and the end of the night
is "That's our night".

**Your call is the person's.** When the story puts a question to the GM,
this asks it and waits. The answer typed is the GM's own, and only then does
this run the kernel's `seal` (yes) or `decline` (no), with the key the
kernel was given when the box was laid: the same as browse's button. There
is no flag that answers for the GM, and nothing here answers on its own.
Closing it while a call waits leaves the call waiting; running it again
asks again.

The end of the night asks for anything to remember. A line written goes into
the binder, in the GM's own words, under sessions/ by the date, where the
recap reads the GM's notes. Then "That's our night?": a yes hands in the
session seal and seals it, and the record is checked.

"Write your own" goes to box/write.py.

Not here yet (open.md has them): the cup for the dice, a blank moment handed to the GM, the heads-up before a call that
clashes with an earlier one, fights, offers.

Exit codes, the kernel's: 0 done; 42 left with a call or the night waiting;
2 refused.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin

try:
    ROOT = willow_pin.root()
except willow_pin.Unpinned as e:
    print(
        "Die-Namic plays with willow, and needs a copy of it beside this folder.\n"
        f"({e})",
        file=sys.stderr,
    )
    raise SystemExit(2) from None
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "adapters" / "stdlib" / "game-master"))
import game_master as gm
import kernel
import session

KERNEL = ROOT / "kernel.py"
SEAL_END = ROOT / "adapters" / "stdlib" / "session-seal" / "session_seal.py"
FIRST = "lantern-fair"  # the story offered when none has been played
SAID = {"strong": "Great!", "weak": "It sort of works.", "miss": "It goes wrong."}


def home() -> Path:
    return Path(os.environ.get("DIE_NAMIC_HOME") or Path.home() / ".die-namic")


def run(*argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, check=False)  # fmt: skip


def ask(prompt: str) -> str | None:
    """What the person typed, or None when there is no one to type."""
    try:
        return input(prompt).strip()
    except EOFError:
        print()
        return None


def yes(prompt: str) -> bool | None:
    """The person's yes or no, asked until it is one; None if they've gone."""
    while True:
        got = ask(prompt)
        if got is None:
            return None
        if got.lower() in ("y", "yes"):
            return True
        if got.lower() in ("n", "no"):
            return False
        print("  Type y for yes, or n for no.")


def lay(where: Path) -> Path:
    """The table, laid the first time by open_table.py's own open."""
    table = where / "table"
    if not (table / "record" / "kernel.json").exists():
        where.mkdir(parents=True, exist_ok=True)
        got = run(HERE / "open_table.py", "open", "--table", table, "--key", where / "gm.key")  # fmt: skip
        if got.returncode == kernel.REFUSED:
            raise RuntimeError((got.stderr or got.stdout).strip())
    return table


def stories(table: Path, rows: list[dict]) -> list[tuple[dict, Path, str]]:
    """(world, its file, the day last played or "") for every story in the
    box: played ones first, the latest first, then the rest by title."""
    last = {}
    for g in gm.games(rows):
        if g["beats"]:
            last[g["open"].get("world")] = g["beats"][-1]["ts"][:10]
    out = []
    for f in sorted((table / "worlds").glob("*.json")):
        try:
            w = gm.load_world(f)
        except gm.WorldError:
            continue
        out.append((w, f, last.get(w["id"], "")))
    played = sorted((s for s in out if s[2]), key=lambda s: (s[2], s[0]["title"]), reverse=True)  # fmt: skip
    return played + sorted((s for s in out if not s[2]), key=lambda s: s[0]["title"])


def first_line(text: str) -> str:
    return text.split(". ")[0].rstrip(".") + "."


def pick(table: Path, rows: list[dict]) -> tuple[dict, Path] | None:
    """The story the person picks, or the one offered when nothing's played."""
    found = stories(table, rows)
    played = [s for s in found if s[2]]
    if played:
        print("Pick up where you left off, or pick another:\n")
    else:
        offer = next((s for s in found if s[0]["id"] == FIRST), found[0])
        print("Let's start a story.\n")
        print(f"  Try this one: {offer[0]['title']}. {first_line(offer[0]['setting'])}")
        print("  (press Enter to play it, or pick another)\n")
    for i, (w, _, day) in enumerate(found, 1):
        when = f"  (last played {day})" if day else ""
        print(f"  {i}. {w['title']}{when}")
    print("  w. Write your own")
    while True:
        got = ask("\nWhich story? ")
        if got is None:
            return None
        if got == "" and not played:
            return offer[0], offer[1]
        if got.lower() == "w":
            return "write"
        if got.isdigit() and 1 <= int(got) <= len(found):
            w, f, _ = found[int(got) - 1]
            return w, f
        print(f"  Type a number from 1 to {len(found)}.")


def names(world: dict) -> dict:
    return {c["id"]: c["name"] for c in world["characters"]}


def prompt(world: dict, row: dict) -> str:
    """The moment's own words, as the story has them, for a beat or an ask."""
    return next((b["prompt"] for sc, b in gm.flat(world) if (sc["id"], b["id"]) == (row.get("scene"), row.get("beat"))), "")  # fmt: skip


def said_roll(world: dict, rows: list[dict], beat: dict) -> str:
    """A roll, the way it's said at the table."""
    roll = rows[beat["roll_row"]] if beat.get("roll_row") is not None else {}
    faces = " + ".join(str(x) for f in roll.get("faces", []) for x in f)
    plus = f", +{beat['bonus']} {beat['stat']}" if beat.get("bonus") else ""
    who = names(world).get(beat.get("character"), beat.get("character"))
    return f"🎲 {who} tries {beat['stat']}: rolled {faces}{plus} = {beat['total']}. {SAID[beat['band']]}"  # fmt: skip


def your_call(box: Path, world: dict, game: dict) -> bool | None:
    """The question the story puts to the GM, asked; the GM's answer made
    the record's by the kernel. None if the person left it waiting."""
    a = game["asks"][-1]
    who = names(world).get(a.get("proposed_by"), a.get("proposed_by"))
    print(f"\n✋ Your call, GM. {prompt(world, a)}\n   {who} says:")
    print(f"   {a['fact']}")
    answer = yes("   Is that true in your world? (y/n) ")
    if answer is None:
        return None
    done = run(KERNEL, "seal" if answer else "decline", "--box", box, a["subject"])
    if done.returncode != kernel.ALIVE:
        raise RuntimeError((done.stderr or done.stdout).strip())
    print("   It's true now." if answer else "   It didn't happen.")
    return answer


def night(table: Path, world: dict, world_file: Path, now: str) -> int:
    """One story played as far as it goes, the GM asked each call."""
    box = table / "record"
    rows, game, err = gm.current(box, world)
    if err and "open first" not in err:
        raise RuntimeError(err)
    if not err and gm.finished(game, world) and not ended(rows, game):
        print(f"\n{world['title']}: played to its end, and the night not ended yet.")
        return end(table, world, game, now)
    if err or gm.finished(game, world):
        done = session.step(box, world_file, now, "open")
        if done.returncode == kernel.REFUSED:
            raise RuntimeError(done.stderr.strip())
        rows, game, _ = gm.current(box, world)
    print(f"\n{world['title']}\n{world['setting']}")
    shown = len(game["beats"])
    scene = None
    while True:
        rows, game, _ = gm.current(box, world)  # the record as it is now, every step
        if gm.finished(game, world):
            break
        sc, b, _ = gm.now_in(world, game)
        if sc["id"] != scene:
            scene = sc["id"]
            print(f"\n-- {sc['title']} --")
            if sc["opening"] and not any(x["scene"] == sc["id"] for x in game["beats"]):
                print("\n".join(sc["opening"]))
        asked = [a for a in game["asks"] if (a["scene"], a["beat"]) == (sc["id"], b["id"])]  # fmt: skip
        if b["kind"] == "action":
            done = session.step(box, world_file, now, "act", b["suggests"])
        elif not asked:
            done = session.step(box, world_file, now, "ask")
            if done.returncode == kernel.REFUSED:
                raise RuntimeError(done.stderr.strip())
            rows, game, _ = gm.current(box, world)
            if your_call(box, world, game) is None:
                print("\nThe call is waiting. Run this again to answer it.")
                return kernel.ESCALATE
            continue
        elif gm.ruling(box, rows, asked[-1]["subject"])[0] not in (
            "sealed",
            "declined",
        ):
            rows, game, _ = gm.current(box, world)
            if your_call(box, world, {**game, "asks": asked}) is None:
                print("\nThe call is waiting. Run this again to answer it.")
                return kernel.ESCALATE
            continue
        else:
            done = session.step(box, world_file, now, "settle")
        if done.returncode == kernel.REFUSED:
            raise RuntimeError(done.stderr.strip())
        rows, game, _ = gm.current(box, world)
        for beat in game["beats"][shown:]:
            if beat["beat_kind"] == "action":
                print(f"\n{prompt(world, beat)}\n{said_roll(world, rows, beat)}\n{beat['text']}")  # fmt: skip
        shown = len(game["beats"])
    return end(table, world, game, now)


def ended(rows: list[dict], game: dict) -> bool:
    """Whether a session seal closes the night this game was played in."""
    last = game["beats"][-1]["n"] if game["beats"] else game["open"]["n"]
    return any(r["kind"] == "session" and r["to"] >= last for r in rows)


def end(table: Path, world: dict, game: dict, now: str) -> int:
    """The end of the night: what was made true, a note, and the GM's yes."""
    box = table / "record"
    rows, _ = kernel.read(box / "record.jsonl")
    true = [a["fact"] for a in game["asks"] if gm.ruling(box, rows, a["subject"])[0] == "sealed"]  # fmt: skip
    print("\n🌙 End of the night")
    if true:
        print("Tonight, your table made true:")
        print("\n".join(f"  • {f}" for f in true))
    else:
        print("Tonight, your table played it through.")
    note = ask("Anything to remember for next time? (or press Enter) ")
    if note:
        keep(table, note, now)
    ended = yes("That's our night? (y/n) ")
    if not ended:
        print("The night stays open. Run this again when you're ready to end it.")
        return kernel.ESCALATE
    run(SEAL_END, "--box", box, "--now", now)
    rows, _ = kernel.read(box / "record.jsonl")
    ends = [r for r in rows if r["kind"] == "session"]
    subject = ends[-1]["subject"] if ends else None
    if subject and gm.ruling(box, rows, subject)[0] != "sealed":
        done = run(KERNEL, "seal", "--box", box, subject)
        if done.returncode != kernel.ALIVE:
            raise RuntimeError((done.stderr or done.stdout).strip())
    held = run(KERNEL, "verify", "--box", box)
    if held.returncode != kernel.ALIVE:
        raise RuntimeError((held.stderr or held.stdout).strip())
    print("Saved and checked: nothing can be changed after the fact. Good night.")
    return kernel.ALIVE


def keep(table: Path, note: str, now: str) -> None:
    """The GM's note, in their words, in the binder's notes for the day."""
    day = now[:10]
    page = table / "pile" / "sessions" / f"{day}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    head = "" if page.exists() else f"# {day}\n\n"
    with page.open("a", encoding="utf-8") as f:
        f.write(f"{head}{note}\n")
    run(KERNEL, "scan", "--box", table / "record")


def previously(table: Path) -> None:
    """What the table made true, to read aloud; and the GM's own latest notes."""
    got = run(HERE / "session.py", "--table", table, "recap")
    aloud = got.stdout.split("## For the GM's eyes")[0]
    if "Nothing yet" not in aloud and aloud.strip():
        print(aloud.replace("# Previously on...", "Previously on...").replace("## Read aloud: what the table made true", "(read this out loud)").rstrip())  # fmt: skip
        print()
    day, lines = session.last_notes(table / "pile")
    if lines and day == latest_night(table):
        print(f"Just for you, GM (your notes from {day}):")
        print("\n".join(f"  {t}" for _, _, t in lines))
        print()


def latest_night(table: Path) -> str:
    """The day the last night was ended, or ""."""
    rows, _ = kernel.read(table / "record" / "record.jsonl")
    ends = [r for r in rows if r["kind"] == "session"]
    return ends[-1]["ts"][:10] if ends else ""


def main(argv: list[str]) -> int:
    if argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return kernel.REFUSED
    now = os.environ.get("DIE_NAMIC_NOW") or kernel.now()
    try:
        table = lay(home())
        rows, breaks = kernel.read(table / "record" / "record.jsonl")
        if breaks:
            raise RuntimeError("the record doesn't check out: " + "; ".join(breaks))
        print("Die-Namic\n")
        previously(table)
        picked = pick(table, rows)
        if picked is None:
            return kernel.ESCALATE
        if picked == "write":
            import write

            return write.compose(table, now)
        return night(table, picked[0], picked[1], now)
    except RuntimeError as e:
        print(f"\nSomething went wrong: {e}", file=sys.stderr)
        return kernel.REFUSED


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
