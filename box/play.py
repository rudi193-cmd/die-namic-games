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

"Write your own" goes to box/write.py; and when a night's calls were
answered, its end offers "Write what happens next", which goes there too.

A moment written blank ("(GM: you say what happens.)", by write.py) is the
GM's moment: the roll is said, then "GM, what happens?". What the GM types
and says yes to is the rule of the table: handed in through game-master's
own offer, of the kind `gm-word` the story declares, at the moment of the
character whose turn it was, and sealed on that yes. Enter keeps nothing
(said aloud only). Leaving at that moment, it is asked first next time.

Before the GM decides a call, or keeps their own word, box/clash.py looks
for what the table already holds true about the same thing; if there is
any, the heads-up comes first: mine stands now, keep the old one, both are
true, and for the GM's own word, let me reword it.

**The table's turn, before each roll.** Every roll waits: the moment is
said, then "Enter: roll · o: someone brings something in" (and "· f: a
fight" in a story fights belong to, Aetheris, whose encounters are
aetheris5e's). o is game-master's own offer, as the character of whoever
brings it in, of a kind the story turns on if it names any: the GM is asked
first (with the heads-up when it meets what the table holds true), and only
then is it handed in and answered, so leaving midway leaves nothing behind.
f is a fight played by fight.py onto the record, blow by blow; what it means
for the story is the GM's to say.

**Safety, without a setup question.** x at any roll sets the next part
aside: no reason asked, the dice still roll, and the GM says what happens
instead; only that it was set aside is kept (a `table-x` row, no one named).
A family's lines and veils are a page they write once, pile/our-lines.md
(box/safety.py): a part that touches a line is never read, and the GM says
what happens instead; one that touches a veil happens off-screen. No page,
nothing changes.

Not here yet (open.md has it): the cup for the dice.

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
import clash
import game_master as gm
import kernel
import safety
import session

KERNEL = ROOT / "kernel.py"
SEAL_END = ROOT / "adapters" / "stdlib" / "session-seal" / "session_seal.py"
FIRST = "lantern-fair"  # the story offered when none has been played
SAID = {"strong": "Great!", "weak": "It sort of works.", "miss": "It goes wrong."}
BLANK = (
    "(GM: you say what happens.)"  # an outcome left for the GM, as write.py writes it
)
GM_WORD = "gm-word"  # the kind of offer a blank moment's line is kept as


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


CHOICES = {"mine": "Mine stands now", "old": "Keep the old one", "both": "Both are true", "reword": "Let me reword it"}  # fmt: skip


def heads_up(met: list[dict], reword: bool) -> str | None:
    """Before the GM decides: what the table already holds true about the
    same thing, and their choice ("mine", "old", "both", "reword"); None if
    they've gone."""
    print("💡 Before you decide:")
    for t in met:
        print(f"   on {t['day']} your table made this true:\n   {t['fact']}")
    keys = ["mine", "old", "both"] + (["reword"] if reword else [])
    for i, k in enumerate(keys, 1):
        print(f"   {i}. {CHOICES[k]}")
    while True:
        got = ask("   Which? ")
        if got is None:
            return None
        if got.isdigit() and 1 <= int(got) <= len(keys):
            return keys[int(got) - 1]
        print(f"   Type a number from 1 to {len(keys)}.")


def standing_by(box: Path, ts: str, choice: str, met: list[dict], subject: str, fact: str) -> None:  # fmt: skip
    """What the GM's choice keeps, once the new word is sealed."""
    for old in met:
        if choice == "mine":
            clash.replace(box, ts, old, subject, fact)
        elif choice == "both":
            clash.keep_both(box, ts, old, subject, fact)


def your_call(box: Path, world: dict, game: dict, now: str) -> bool | None:
    """The question the story puts to the GM, asked; the GM's answer made
    the record's by the kernel. When the table already holds something true
    about the same thing, the heads-up comes first. None if the person left
    it waiting."""
    a = game["asks"][-1]
    who = names(world).get(a.get("proposed_by"), a.get("proposed_by"))
    print(f"\n✋ Your call, GM. {prompt(world, a)}\n   {who} says:")
    print(f"   {a['fact']}")
    met = clash.meets(box, a["fact"], a["subject"])
    if met:
        choice = heads_up(met, reword=False)
        if choice is None:
            return None
        done = run(KERNEL, "decline" if choice == "old" else "seal", "--box", box, "--now", now, a["subject"])  # fmt: skip
        if done.returncode != kernel.ALIVE:
            raise RuntimeError((done.stderr or done.stdout).strip())
        standing_by(box, now, choice, met, a["subject"], a["fact"])
        print({"mine": "   It's true now, and the old one is replaced.", "old": "   It didn't happen. The old one stands.",
               "both": "   It's true now, beside the old one."}[choice])  # fmt: skip
        return choice != "old"
    answer = yes("   Is that true in your world? (y/n) ")
    if answer is None:
        return None
    done = run(
        KERNEL,
        "seal" if answer else "decline",
        "--box",
        box,
        "--now",
        now,
        a["subject"],
    )
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
    if (
        not err and waiting_blank(game) and not ended(rows, game)
    ):  # left at the GM's moment: asked first
        beat = game["beats"][-1]
        print(f"\n{world['title']}\n\n{prompt(world, beat)}\n{said_roll(world, rows, beat)}")  # fmt: skip
        if gm_says(box, world, world_file, beat, now) is None:
            print("\nThe GM's moment is waiting. Run this again to pick up.")
            return kernel.ESCALATE
        rows, game, err = gm.current(box, world)
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
                print(opening(table, "\n".join(sc["opening"])))
        asked = [a for a in game["asks"] if (a["scene"], a["beat"]) == (sc["id"], b["id"])]  # fmt: skip
        if b["kind"] == "action":
            if before_roll(table, world, world_file, b, now, game) is None:
                print("\nThe story is waiting. Run this again to pick up.")
                return kernel.ESCALATE
            done = session.step(box, world_file, now, "act", b["suggests"])
        elif not asked:
            done = session.step(box, world_file, now, "ask")
            if done.returncode == kernel.REFUSED:
                raise RuntimeError(done.stderr.strip())
            rows, game, _ = gm.current(box, world)
            if your_call(box, world, game, now) is None:
                print("\nThe call is waiting. Run this again to answer it.")
                return kernel.ESCALATE
            continue
        elif gm.ruling(box, rows, asked[-1]["subject"])[0] not in (
            "sealed",
            "declined",
        ):
            rows, game, _ = gm.current(box, world)
            if your_call(box, world, {**game, "asks": asked}, now) is None:
                print("\nThe call is waiting. Run this again to answer it.")
                return kernel.ESCALATE
            continue
        else:
            done = session.step(box, world_file, now, "settle")
        if done.returncode == kernel.REFUSED:
            raise RuntimeError(done.stderr.strip())
        rows, game, _ = gm.current(box, world)
        for i, beat in enumerate(game["beats"][shown:], shown):
            if beat["beat_kind"] != "action":
                continue
            print(said_roll(world, rows, beat))
            aside = set_aside(table, rows, game, i, f"{b.get('prompt', '')}\n{beat['text']}")  # fmt: skip
            if aside:
                print(aside)
            if beat["text"] != BLANK and not aside:
                print(beat["text"])
            elif gm_says(box, world, world_file, beat, now) is None:
                print("\nThe GM's moment is waiting. Run this again to pick up.")
                return kernel.ESCALATE
        shown = len(game["beats"])
    return end(table, world, game, now)


def ended(rows: list[dict], game: dict) -> bool:
    """Whether a session seal closes the night this game was played in."""
    last = game["beats"][-1]["n"] if game["beats"] else game["open"]["n"]
    return any(r["kind"] == "session" and r["to"] >= last for r in rows)


def waiting_blank(game: dict) -> bool:
    """Whether the last moment played was left blank for the GM, and the GM
    has said nothing for it yet (the person left at that moment)."""
    beat = game["beats"][-1] if game["beats"] else None
    if not beat or beat["beat_kind"] != "action" or beat["text"] != BLANK:
        return False
    return not any(o["n"] > beat["n"] and o.get("as") == GM_WORD for o in game["offers"])  # fmt: skip


def gm_says(box: Path, world: dict, world_file: Path, beat: dict, now: str) -> bool | None:  # fmt: skip
    """A moment left blank: the GM says what happens. What they type and say
    yes to is the rule of the table, kept as an offer of the GM's word, made
    at the moment of the character whose turn it was, and sealed on that yes.
    Enter keeps nothing (said aloud only); None if the person left. In a
    story with no GM's word to keep (it names no gm-word offer: a part set
    aside in a story written before), it's said aloud, and nothing kept."""
    if GM_WORD not in world.get("offers", []):
        said = ask("✋ GM, what happens instead? (say it aloud, then press Enter) ")
        if said is None:
            return None
        print("   Said aloud.")
        return False
    while True:
        line = ask(
            "✋ GM, what happens? (say it, and type it to keep it; or press Enter) "
        )
        if line is None:
            return None
        if not line:
            print("   Said aloud, not kept.")
            return False
        met = clash.meets(box, line)
        if met:
            choice = heads_up(met, reword=True)
            if choice is None:
                return None
            if choice == "reword":
                continue
            if choice == "old":
                print("   Not kept. The old one stands.")
                return False
            break
        keep_it = yes("   Is that the rule of the table now? (y/n) ")
        if keep_it is None:
            return None
        if keep_it:
            choice = ""
            break
    who = beat.get("character")
    done = session.step(box, world_file, now, "offer", who, line, "--as", GM_WORD)
    if done.returncode == kernel.REFUSED:
        raise RuntimeError(done.stderr.strip())
    _, game, _ = gm.current(box, world)
    subject = game["offers"][-1]["subject"]
    sealed = run(KERNEL, "seal", "--box", box, "--now", now, subject)
    if sealed.returncode != kernel.ALIVE:
        raise RuntimeError((sealed.stderr or sealed.stdout).strip())
    heard = session.step(box, world_file, now, "settle")
    if heard.returncode == kernel.REFUSED:
        raise RuntimeError(heard.stderr.strip())
    standing_by(box, now, choice, met, subject, line)
    print({"mine": "   It's the rule of the table now, and the old one is replaced.",
           "both": "   It's the rule of the table now, beside the old one."}.get(choice, "   It's the rule of the table now."))  # fmt: skip
    return True


def aside(table: Path, now: str, game: dict) -> None:
    """The X-card: the next part set aside, kept as only that it was. The row
    names no one and gives no reason: `game` is the story's open row, `at`
    the moment it is for (how many it had played)."""
    kernel.append(table / "record", now, safety.X, who="table", game=game["open"]["n"], at=len(game["beats"]))  # fmt: skip


def set_aside(table: Path, rows: list[dict], game: dict, i: int, text: str) -> str:
    """What to say instead of moment I's text, or "" to read it: set aside by
    an x, or touching one of the table's lines (never read) or veils (off-screen)."""
    if any(r["kind"] == safety.X and (r.get("game"), r.get("at")) == (game["open"]["n"], i) for r in rows):  # fmt: skip
        return "   (Set aside.)"
    lines, veils = safety.read(table)
    if safety.touches(lines, text):
        return "   (Set aside: one of your lines.)"
    if safety.touches(veils, text):
        return "   🌫 That happens off-screen."
    return ""


def opening(table: Path, text: str) -> str:
    """A scene's opening, or "(The GM sets the scene.)" when it touches a line."""
    lines, veils = safety.read(table)
    if safety.touches(lines, text):
        return "(The GM sets the scene.)"
    if safety.touches(veils, text):
        return "(Something happens off-screen, and the scene begins.)"
    return text


FIGHTS = {"aetheris-the-waking-tide"}  # the stories aetheris5e's encounters belong to


def before_roll(table: Path, world: dict, world_file: Path, b: dict, now: str, game: dict) -> bool | None:  # fmt: skip
    """The moment said, and the table's turn before the roll: Enter rolls, o
    is someone bringing something in, f a fight (in a story fights belong
    to). True to roll; None if the person left."""
    lines, veils = safety.read(table)
    line, veil = safety.touches(lines, b["prompt"]), safety.touches(veils, b["prompt"])
    if line:
        aside(table, now, game)
        print(f"\n🛑 The next part touches one of your lines ({line}). It's set aside:\n   the dice still roll, and the GM says what happens instead.")  # fmt: skip
    else:
        print(f"\n{b['prompt']}")
        if veil:
            print(f"   🌫 ({veil}: it happens off-screen.)")
    fights = world["id"] in FIGHTS
    hint = (
        "  Enter: roll · o: someone brings something in"
        + (" · f: a fight" if fights else "")
        + " · x: set it aside"
    )
    while True:
        print(hint)
        got = ask("> ")
        if got is None:
            return None
        if got == "":
            return True
        if got.lower() == "o":
            if bring_in(table / "record", world, world_file, now) is None:
                return None
        elif got.lower() == "f" and fights:
            if fight(table, now) is None:
                return None
        elif got.lower() == "x":
            if not line:
                aside(table, now, game)
            print("   Set aside. Nobody needs to say why. The dice still roll, and the GM says what happens instead.")  # fmt: skip
            return True
        else:
            print("  Press Enter to roll" + (", o, f or x." if fights else ", o or x."))


def pick_one(prompt_: str, options: list[str]) -> int | None:
    """The number of the option picked, from 0; the first on Enter; None if gone."""
    for i, o in enumerate(options, 1):
        print(f"   {i}. {o}")
    while True:
        got = ask(prompt_)
        if got is None:
            return None
        if got == "":
            return 0
        if got.isdigit() and 1 <= int(got) <= len(options):
            return int(got) - 1
        print(f"   Type a number from 1 to {len(options)}.")


def bring_in(box: Path, world: dict, world_file: Path, now: str) -> bool | None:
    """Someone at the table brings something into the story, as their
    character: game-master's own offer. The GM is asked first (with the
    heads-up when it meets what the table holds true), and only then is it
    handed in and answered, so leaving midway leaves nothing half done.
    True or False for the GM's answer, "" if no one brought anything,
    None if the person left."""
    seats = gm.seated(world)
    k = 0
    if len(seats) > 1:
        print("   Who brings it in?")
        k = pick_one("   Who? ", [c["name"] for c in seats])
        if k is None:
            return None
    who = seats[k]
    fact = ask(f"   What does {who['name']} bring in? (or press Enter) ")
    if not fact:
        return None if fact is None else ""
    kinds = [x for x in world.get("offers", []) if x != GM_WORD]
    kind = ""
    if kinds:
        print("   What is it?")
        j = pick_one("   Which? ", kinds + ["Something else"])
        if j is None:
            return None
        kind = kinds[j] if j < len(kinds) else ""
    print(f"\n✋ Your call, GM. {who['name']} brings this in:\n   {fact}")
    met = clash.meets(box, fact)
    if met:
        choice = heads_up(met, reword=False)
        if choice is None:
            return None
        answer = choice != "old"
    else:
        choice = ""
        answer = yes("   Is that true in your world? (y/n) ")
        if answer is None:
            return None
    done = session.step(box, world_file, now, "offer", who["id"], fact, *(["--as", kind] if kind else []))  # fmt: skip
    if done.returncode == kernel.REFUSED:
        raise RuntimeError(done.stderr.strip())
    _, game, _ = gm.current(box, world)
    subject = game["offers"][-1]["subject"]
    answered = run(
        KERNEL, "seal" if answer else "decline", "--box", box, "--now", now, subject
    )
    if answered.returncode != kernel.ALIVE:
        raise RuntimeError((answered.stderr or answered.stdout).strip())
    heard = session.step(box, world_file, now, "settle")
    if heard.returncode == kernel.REFUSED:
        raise RuntimeError(heard.stderr.strip())
    if answer:
        standing_by(box, now, choice, met, subject, fact)
    print({"mine": "   It's true now, and the old one is replaced.", "both": "   It's true now, beside the old one.",
           "old": "   It didn't happen. The old one stands."}.get(choice, "   It's true now." if answer else "   It didn't happen."))  # fmt: skip
    return answer


def fight(table: Path, now: str) -> bool | None:
    """A fight from aetheris5e, played by fight.py onto the record, blow by
    blow. True once fought, False if it couldn't be, None if the person left."""
    listed = run(HERE / "fight.py", "list")
    names = [line.split()[0] for line in listed.stdout.splitlines() if line.strip()]
    descs = [line.strip().split(None, 1)[1] for line in listed.stdout.splitlines() if line.strip()]  # fmt: skip
    if listed.returncode != kernel.ALIVE or not names:
        print("   A fight can't start here: aetheris5e's dice aren't reachable.")
        return False
    print("   Which fight?")
    k = pick_one("   Which? ", descs)
    if k is None:
        return None
    done = run(HERE / "fight.py", "--table", table, "fight", names[k], "--now", now)
    if done.returncode != kernel.ALIVE:
        print(f"   The fight couldn't start: {(done.stderr or done.stdout).strip()}")
        return False
    blows = done.stdout.rstrip().splitlines()
    print("\n⚔️  " + "\n".join(blows[:-1]))
    rows, _ = kernel.read(table / "record" / "record.jsonl")
    res = next(r for r in reversed(rows) if r["kind"] == "fight-end")["result"]
    said = {"party": "The party won", "foe": "The party fell", "stalemate": "Neither side fell"}.get(res["outcome"], "It ended")  # fmt: skip
    standing = ", ".join(res["party_survivors"] + res["foe_survivors"]) or "no one"
    print(f"⚔️  {said} in {res['rounds']} rounds. Still standing: {standing}.")
    print("   (What the fight means for the story is yours to say, GM.)")
    return True


def made_true(box: Path, rows: list[dict], game: dict) -> list[dict]:
    """The calls, what was brought in, and the GM's words this game, each
    answered, in row order."""
    out = game["asks"] + game["offers"]
    return sorted((a for a in out if gm.ruling(box, rows, a["subject"])[0] in ("sealed", "declined")), key=lambda a: a["n"])  # fmt: skip


def end(table: Path, world: dict, game: dict, now: str) -> int:
    """The end of the night: what was made true, a note, and the GM's yes."""
    box = table / "record"
    rows, _ = kernel.read(box / "record.jsonl")
    true = [a["fact"] for a in made_true(box, rows, game) if gm.ruling(box, rows, a["subject"])[0] == "sealed"]  # fmt: skip
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
        done = run(KERNEL, "seal", "--box", box, "--now", now, subject)
        if done.returncode != kernel.ALIVE:
            raise RuntimeError((done.stderr or done.stdout).strip())
    held = run(KERNEL, "verify", "--box", box)
    if held.returncode != kernel.ALIVE:
        raise RuntimeError((held.stderr or held.stdout).strip())
    print("Saved and checked: nothing can be changed after the fact.")
    answered = [a for a in game["asks"] if gm.ruling(box, rows, a["subject"])[0] in ("sealed", "declined")]  # fmt: skip
    if answered and yes("\n🌱 Your story grew. Write what happens next? (y/n) "):
        import write

        print()
        return write.compose(table, now, after=world)
    print("Good night.")
    return kernel.ALIVE


def keep(table: Path, note: str, now: str) -> None:
    """The GM's note, in their words, in the binder's notes for the day."""
    day = now[:10]
    page = table / "pile" / "sessions" / f"{day}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    head = "" if page.exists() else f"# {day}\n\n"
    with page.open("a", encoding="utf-8") as f:
        f.write(f"{head}{note}\n")


def previously(table: Path) -> None:
    """What the table made true, to read aloud; and the GM's own latest notes."""
    got = run(HERE / "session.py", "--table", table, "recap")
    aloud = got.stdout.split("## For the GM's eyes")[0]
    if "Nothing yet" not in aloud and aloud.strip():
        print(aloud.replace("# Previously on...", "Previously on...").replace("## Read aloud: what the table made true", "(read this out loud)").rstrip())  # fmt: skip
        print()
    gm_eyes = got.stdout.split("## For the GM's eyes")[-1]
    if "\nReplaced:\n" in gm_eyes:
        print("Just for you, GM, what your table replaced:")
        print(gm_eyes.split("\nReplaced:\n")[1].split("\nSaid no to:")[0].rstrip())
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
