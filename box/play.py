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
f is a fight played by fight.py onto the record, blow by blow, then drawn
as a board (box/board.py: who's hurt, who's down, whose turn); what it
means for the story is the GM's to say. In a story that turns on a fight
(a moment written "when: the fight is won", or lost), f is there too, and
its end goes to the GM as a call: "Does it stand that the party won?" Their
yes or no is sealed or declined as an offer of the kind `fight`, so the
moment that follows is the one the call says; a call against the dice is
the GM's word over them, kept beside the fight, never the fight changed.
A story that names its `"foes"` (and has dndwright installed) offers f too, with its own
seated characters against one of those foes, run by dndwright on dice dropped in
the tower, every blow a row (box/dw-fights.md).
g, once a roll has been read, is the GM's word over it: "the dice said miss;
I say she makes it". The roll and its moment stay exactly as they went; what
the GM types is a kept call of its own (an offer of the kind `gm-word`, at
the character's moment, sealed on the GM's yes, with the heads-up first), in
a story that declares gm-word; in any other it is said aloud and nothing is
kept. It reads in the night's summary as made true, beside the roll.
h is how the character meets it: the story's stats, each with the
character's bonus and its exact chances (2d6 counted, as play-odds would),
the story's own first; game-master's act takes any of them. u undoes a yes pressed by mistake: the last thing made true tonight, taken
back on the GM's y. On the next night's opening screen it reads "taken back on
<day>, pressed by mistake", not as a replacement. Nothing takes a seal back; a replacement whose new word
is nothing stands over it (clash.py's take_back, the "mine stands now"
shape, as willow's decisions keep a replaced row), so the old yes stays on
the record and no longer stands. After the sheets, the GM can write on them, a line each ("Tamsin finds a
rope", "Oro is hurt", box/carry.py): what a character carries, uses up, and
comes through lasts between nights, and the opening screen reads what
carried over aloud. s shows each seated character's sheet: who they are, what they're good at
(the bonus a roll adds), and the last few things the table made true about
them, still standing (sheet_data, which box/paper.py also sets on a page for
holding, big and high-contrast). The opening screen tells the GM how last night's
fights ended (session.py's recap, for the GM's eyes, never read aloud).

**Safety, without a setup question.** x at any roll sets the next part
aside: no reason asked, the dice still roll, and the GM says what happens
instead; only that it was set aside is kept (a `table-x` row, no one named).
p at any of those prompts pauses the whole night: nothing asked, nothing
more played, "Paused. Nobody needs to say why.", exit 42, and running it
again picks the night up where it was; only that it happened is kept (a
`table-pause` row, no one named). x works at the GM's call and at the GM's
moment too: at a call nothing is decided (the machine never seals or
declines for the GM; game-master settles a call only on a yes or no), so
the call waits for later; at a moment nothing is kept and the story goes on.
A family's lines and veils are a page they write once, pile/our-lines.md
(box/safety.py): a part that touches a line is never read, and the GM says
what happens instead; one that touches a veil happens off-screen. No page,
nothing changes.

**The dice.** When a moment is posed its dice are dropped in willow's
dice-tower (in_tower): only their hash goes on the record, the secret to a
file in the table's tower/ folder, outside it, so no row written before the
roll (an offer, a call, a sheet) can change them, and nobody reads them
first, the GM included. Enter brings them out as the roll (game-master's
act --tower). Or the table throws real dice and types the two faces ("4 6"):
game-master's act --said keeps them as said, marked "(your dice)", and the
tower's unused dice come out so none is left inside.

Exit codes, the kernel's: 0 done; 42 left with a call or the night waiting;
2 refused.
"""

from __future__ import annotations

import json
import os
import re
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
import session

carry = willow_pin.addon("carry-sheet")  # what the characters carry and come through
safety = willow_pin.addon("lines-veils")  # what never happens at our table

KERNEL = ROOT / "kernel.py"


def addon(name: str, *argv: str) -> str:
    """A pinned add-on run by its command line, writing its own rows; what it
    printed. One that refuses stops the night with its reason, never quietly."""
    done = subprocess.run([sys.executable, str(willow_pin.script(name)), *argv], capture_output=True, text=True, check=False)  # fmt: skip
    if done.returncode != kernel.ALIVE:
        raise SystemExit(f"{name} refused: {done.stderr.strip()}")
    return done.stdout


TOWER = ROOT / "adapters" / "stdlib" / "dice-tower" / "dice_tower.py"
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


class Pause(Exception):
    """The table stopped the whole night (p): nothing asked, nothing more played."""


ASIDE = "aside"  # what a prompt returns when the table pressed x there


def safe_key(got: str, ctx: tuple | None, at: int | None = None, part: str = "") -> bool:  # fmt: skip
    """x or p typed alone where the table can set a part aside or stop the
    night: p records that a pause happened (no one named, no reason) and
    raises Pause; x records the part set aside and returns True. CTX is
    (table, now, game); None where the keys aren't offered."""
    key = got.strip().lower()
    if ctx is None or key not in ("x", "p"):
        return False
    table, now, game = ctx
    if key == "p":
        pause(table, now, game)
    aside(table, now, game, at, part)
    return True


def yes(prompt: str, ctx: tuple | None = None, part: str = "") -> bool | str | None:  # fmt: skip
    """The person's yes or no, asked until it is one; None if they've gone.
    With CTX, x sets the part aside (ASIDE) and p pauses the night."""
    while True:
        got = ask(prompt)
        if got is None:
            return None
        if safe_key(got, ctx, part=part):
            return ASIDE
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
    yours = " (your dice)" if roll.get("generator") == "said" else ""
    return f"🎲 {who} tries {beat['stat']}: rolled {faces}{yours}{plus} = {beat['total']}. {SAID[beat['band']]}"  # fmt: skip


CHOICES = {"mine": "Mine stands now", "old": "Keep the old one", "both": "Both are true", "reword": "Let me reword it"}  # fmt: skip


def heads_up(met: list[dict], reword: bool, ctx: tuple | None = None, part: str = "") -> str | None:  # fmt: skip
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
        if safe_key(got, ctx, part=part):
            return ASIDE
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


CALL_KEYS = "  x: set it aside · p: pause the night"
CALL_ASIDE = "   Set aside. Nobody needs to say why. Nothing is decided: the call waits until you want it."  # fmt: skip


def your_call(box: Path, world: dict, game: dict, now: str) -> bool | None:
    """The question the story puts to the GM, asked; the GM's answer made
    the record's by the kernel. When the table already holds something true
    about the same thing, the heads-up comes first. None if the person left
    it waiting."""
    a = game["asks"][-1]
    who = names(world).get(a.get("proposed_by"), a.get("proposed_by"))
    print(f"\n{CALL_KEYS}\n✋ Your call, GM. {prompt(world, a)}\n   {who} says:")
    print(f"   {a['fact']}")
    ctx = (box.parent, now, game)
    met = clash.meets(box, a["fact"], a["subject"])
    if met:
        choice = heads_up(met, reword=False, ctx=ctx, part="call")
        if choice == ASIDE:
            print(CALL_ASIDE)
            return None
        if choice is None:
            return None
        done = run(KERNEL, "decline" if choice == "old" else "seal", "--box", box, "--now", now, a["subject"])  # fmt: skip
        if done.returncode != kernel.ALIVE:
            raise RuntimeError((done.stderr or done.stdout).strip())
        standing_by(box, now, choice, met, a["subject"], a["fact"])
        print({"mine": "   It's true now, and the old one is replaced.", "old": "   It didn't happen. The old one stands.",
               "both": "   It's true now, beside the old one."}[choice])  # fmt: skip
        return choice != "old"
    answer = yes("   Is that true in your world? (y/n) ", ctx, "call")
    if answer == ASIDE:
        print(CALL_ASIDE)
        return None
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
            got = before_roll(table, world, world_file, b, now, game)
            if got is None:
                print("\nThe story is waiting. Run this again to pick up.")
                return kernel.ESCALATE
            how, faces, die = got
            if faces:  # the table threw its own: the tower's die comes out unused
                run(TOWER, "--box", box, "out", "--die", die, "--now", now)
                done = session.step(box, world_file, now, "act", how, "--said", faces)
            else:
                done = session.step(box, world_file, now, "act", how, "--tower", die)
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


MOMENT_KEYS = "  x: set it aside · p: pause the night"
MOMENT_ASIDE = "   Set aside. Nobody needs to say why. Nothing is kept; the story goes on."  # fmt: skip


def gm_says(box: Path, world: dict, world_file: Path, beat: dict, now: str, over: bool = False) -> bool | None:  # fmt: skip
    """A moment left blank: the GM says what happens. What they type and say
    yes to is the rule of the table, kept as an offer of the GM's word, made
    at the moment of the character whose turn it was, and sealed on that yes.
    Enter keeps nothing (said aloud only); None if the person left. In a
    story with no GM's word to keep (it names no gm-word offer: a part set
    aside in a story written before), it's said aloud, and nothing kept.
    With `over`, the moment was read and its roll stands as it went: this
    is the GM's word over it, a row of its own, never the roll changed."""
    _, game, _ = gm.current(box, world)
    ctx = (box.parent, now, game)
    at = len(game["beats"]) - 1  # the moment the GM is speaking for
    if GM_WORD not in world.get("offers", []):
        print(MOMENT_KEYS)
        said = ask("✋ GM, what happens instead? (say it aloud, then press Enter) ")
        if said is None:
            return None
        if safe_key(said, ctx, at, "moment"):
            print(MOMENT_ASIDE)
            return False
        print("   Said aloud.")
        return False
    while True:
        print(MOMENT_KEYS)
        line = ask(
            "✋ GM, what happens instead? (the roll stands as it went; say it, and type it to keep it; or press Enter) "
            if over
            else "✋ GM, what happens? (say it, and type it to keep it; or press Enter) "
        )
        if line is None:
            return None
        if safe_key(line, ctx, at, "moment"):
            print(MOMENT_ASIDE)
            return False
        if not line:
            print("   Said aloud, not kept.")
            return False
        met = clash.meets(box, line)
        if met:
            choice = heads_up(met, reword=True, ctx=ctx, part="moment")
            if choice == ASIDE:
                print(MOMENT_ASIDE)
                return False
            if choice is None:
                return None
            if choice == "reword":
                continue
            if choice == "old":
                print("   Not kept. The old one stands.")
                return False
            break
        keep_it = yes("   Is that the rule of the table now? (y/n) ", ctx, "moment")
        if keep_it == ASIDE:
            print(MOMENT_ASIDE)
            return False
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


def aside(table: Path, now: str, game: dict, at: int | None = None, part: str = "") -> None:  # fmt: skip
    """The X-card: the next part set aside, kept as only that it was. The row
    names no one and gives no reason: `game` is the story's open row, `at`
    the moment it is for (how many it had played). At a GM's call or moment
    (PART "call" or "moment") the row says which kind of part, nothing more."""
    at = len(game["beats"]) if at is None else at
    more = ["--part", part] if part else []
    addon("lines-veils", "--box", str(table / "record"), "x", "--game", str(game["open"]["n"]), "--at", str(at), *more, "--now", now)  # fmt: skip


def pause(table: Path, now: str, game: dict) -> None:
    """The pause: the whole night stopped, kept as only that it was (a
    `table-pause` row: no one named, no reason). Raises Pause."""
    addon("lines-veils", "--box", str(table / "record"), "pause", "--game", str(game["open"]["n"]), "--at", str(len(game["beats"])), "--now", now)  # fmt: skip
    raise Pause


def set_aside(table: Path, rows: list[dict], game: dict, i: int, text: str) -> str:
    """What to say instead of moment I's text, or "" to read it: set aside by
    an x, or touching one of the table's lines (never read) or veils (off-screen)."""
    if any(r["kind"] == safety.X and (r.get("game"), r.get("at")) == (game["open"]["n"], i) and "part" not in r for r in rows):  # fmt: skip
        return "   (Set aside.)"
    lines, veils = safety.read(table)
    if safety.touches(lines, text):
        return "   (Set aside: one of your lines.)"
    if safety.touches(veils, text):
        return "   🌫 That happens off-screen."
    return ""


def undo(box: Path, now: str) -> bool | None:
    """A yes pressed by mistake: the last thing made true tonight, taken back
    on the GM's word. It stays on the record as a slip and no longer stands.
    True if taken back, False if not (or nothing to take), None if gone."""
    rows, _ = kernel.read(box / "record.jsonl")
    made = clash.tonight(box, rows)
    if not made:
        print("   Nothing has been made true tonight to take back.")
        return False
    last = made[-1]
    sure = yes(f"   Take back \"{last['fact']}\"? It stays on the record as a slip, and no longer stands. (y/n) ")  # fmt: skip
    if not sure:
        return sure
    clash.take_back(box, now, last)
    print("   Taken back. It no longer stands.")
    return True


def write_on_sheet(box: Path, world: dict, now: str) -> bool | None:
    """The GM's changes to the sheets, a line each, until Enter: what a
    character finds or uses up, and when they're hurt or healed (carry.py),
    each kept on the record. True if any was kept, None if the person left."""
    names = [c["name"] for c in gm.seated(world)]
    kept = False
    while True:
        line = ask(f'   Write on a sheet? ("{names[0]} finds a rope", "{names[-1]} is hurt"; or press Enter) ')  # fmt: skip
        if line is None:
            return None
        if not line:
            return kept
        got = carry.read(line, names)
        if got is None:
            print(f"   Start with a name ({', '.join(names)}), then finds, uses, is hurt or is healed.")  # fmt: skip
            continue
        addon("carry-sheet", "--box", str(box), "write", "--names", ",".join(names), line, "--now", now)  # fmt: skip
        print(f"   On {got['char']}'s sheet.")
        kept = True


def sheet_data(table: Path, world: dict) -> list[dict]:
    """Each seated character's sheet as data, for the terminal and for paper
    (paper.py): name, role, what they're good at, what they carry, how they're
    hurt, and the last three things the table made true about them or that
    they brought in, still standing."""
    box = table / "record"
    rows, _ = kernel.read(box / "record.jsonl")
    out = session.gone(box, rows)
    said = [s for s in session.answers(box, rows, table / "worlds") if s[1] == "sealed" and s[0] not in out]  # fmt: skip
    data = []
    for c in gm.seated(world):
        good = ", ".join(f"{k} +{v}" for k, v in c.get("stats", {}).items()) or "nothing yet"  # fmt: skip
        carrying, hurt = carry.sheet(rows, c["name"])
        theirs = [fact for _, _, fact, _, by, _ in said if by == c["id"] or c["name"].lower() in fact.lower()]  # fmt: skip
        data.append(
            {
                "name": c["name"],
                "role": c.get("role") or "",
                "good": good,
                "carrying": list(carrying),
                "hurt": "; ".join(h for h in hurt if h) if hurt else None,
                "true": theirs[-3:],
            }
        )
    return data


def sheets(table: Path, world: dict) -> str:
    """Each seated character's sheet, for the table (sheet_data, as text)."""
    lines = []
    for c in sheet_data(table, world):
        lines.append(f"\n   📜 {c['name']}" + (f", {c['role']}" if c["role"] else "") + f"\n      Good at: {c['good']}")  # fmt: skip
        if c["carrying"]:
            lines.append("      Carrying: " + ", ".join(c["carrying"]))
        if c["hurt"] is not None:
            lines.append("      Hurt" + (f": {c['hurt']}" if c["hurt"] else ""))
        lines += [f"      · {f}" for f in c["true"]]
    return "\n".join(lines) + "\n"


def opening(table: Path, text: str) -> str:
    """A scene's opening, or "(The GM sets the scene.)" when it touches a line."""
    lines, veils = safety.read(table)
    if safety.touches(lines, text):
        return "(The GM sets the scene.)"
    if safety.touches(veils, text):
        return "(Something happens off-screen, and the scene begins.)"
    return text


PLAY_FIGHT = (
    ROOT / "adapters" / "deps" / "play-fight" / "play_fight.py"
)  # the story's own fights, through the pin
FIGHTS = {"aetheris-the-waking-tide"}  # the stories aetheris5e's encounters belong to


def before_roll(table: Path, world: dict, world_file: Path, b: dict, now: str, game: dict) -> tuple | None:  # fmt: skip
    """The moment said, the dice dropped in the tower, and the table's turn
    before the roll: Enter brings them out, two faces typed are the table's
    own dice, o is someone bringing something in, f a fight (in a story
    fights belong to), h how the character meets it. (the stat to roll with,
    the faces typed or "", the die in the tower); None if the person left."""
    lines, veils = safety.read(table)
    line, veil = safety.touches(lines, b["prompt"]), safety.touches(veils, b["prompt"])
    if line:
        aside(table, now, game)
        print(f"\n🛑 The next part touches one of your lines ({line}). It's set aside:\n   the dice still roll, and the GM says what happens instead.")  # fmt: skip
    else:
        print(f"\n{b['prompt']}")
        if veil:
            print(f"   🌫 ({veil}: it happens off-screen.)")
    die = in_tower(table, game, now)
    fights = world["id"] in FIGHTS or "fight" in world.get("offers", []) or bool(story_foes(world))  # fmt: skip
    how = b["suggests"]
    last = next((x for x in reversed(game["beats"]) if x["beat_kind"] == "action"), None)  # fmt: skip
    hint = (
        "  Enter: roll, or type the two dice you threw (like 4 6)\n"
        + "  h: how · o: someone brings something in"
        + (" · f: a fight" if fights else "")
        + " · s: sheets · u: undo a yes"
        + (" · g: the GM's word over the last roll" if last else "")
        + " · x: set it aside · p: pause the night"
    )
    while True:
        print(hint)
        got = ask("> ")
        if got is None:
            return None
        if got == "":
            return how, "", die
        threw = DICE.fullmatch(got)
        if threw:
            return how, f"{threw[1]},{threw[2]}", die
        if re.fullmatch(r"\s*\d+\s*[ ,]\s*\d+\s*", got):
            print("  A die shows 1 to 6: type the two dice, like 4 6.")
            continue
        if got.lower() == "h":
            picked = choose_how(world, game, b, how)
            if picked is None:
                return None
            how = picked
        elif got.lower() == "o":
            if bring_in(table / "record", world, world_file, now) is None:
                return None
        elif got.lower() == "f" and fights:
            if fight(table, now, world, world_file, game) is None:
                return None
        elif got.lower() == "s":
            print(sheets(table, world))
            if write_on_sheet(table / "record", world, now) is None:
                return None
        elif got.lower() == "u":
            if undo(table / "record", now) is None:
                return None
        elif got.lower() == "g" and last:
            if gm_says(table / "record", world, world_file, last, now, over=True) is None:  # fmt: skip
                return None
        elif got.lower() == "p":
            pause(table, now, game)
        elif got.lower() == "x":
            if not line:
                aside(table, now, game)
            print("   Set aside. Nobody needs to say why. The dice still roll, and the GM says what happens instead.")  # fmt: skip
            return how, "", die
        else:
            print(
                "  Press Enter to roll, type your two dice (like 4 6), or "
                + ("h, o, f, s, u" if fights else "h, o, s, u")
                + (", g, x or p." if last else ", x or p.")
            )


DICE = re.compile(
    r"\s*([1-6])\s*[ ,]\s*([1-6])\s*"
)  # two real d6, as the table read them


def in_tower(table: Path, game: dict, now: str) -> str:
    """The die for this moment, dropped in willow's dice-tower when the moment
    is posed: only its hash goes on the record, the secret to a file outside
    it (the table's tower/ folder), so no row written before the roll (an
    offer, a call, a note) can change it and nobody can read it first. A
    night picked up again finds the die it left in the tower."""
    folder = table / "tower"
    folder.mkdir(mode=0o700, exist_ok=True)
    die = folder / f"story-{game['open']['n']}-moment-{len(game['beats']) + 1}.die"
    if not die.exists():
        done = run(TOWER, "--box", table / "record", "drop", "--dice", "2d6", "--to", die, "--for", f"moment {len(game['beats']) + 1}")  # fmt: skip
        if done.returncode != kernel.ALIVE:
            raise RuntimeError((done.stderr or done.stdout).strip())
        print("🥤 The dice are in the tower. Nobody knows them yet, not even the GM.")
    return str(die)


def chances(bonus: int) -> str:
    """Two d6 plus BONUS, as how often each band comes up, counted exactly."""
    sums = [a + b + bonus for a in range(1, 7) for b in range(1, 7)]
    per = {k: sum(1 for s in sums if gm.band_of(s) == k) for k in ("strong", "weak", "miss")}  # fmt: skip
    return ", ".join(f"{k} {round(100 * n / 36)}%" for k, n in per.items())


def choose_how(world: dict, game: dict, b: dict, how: str) -> str | None:
    """The player says how their character meets it: each of the story's
    stats, with the character's bonus and its chances, the story's own way
    first (game-master's act takes any of them). None if the person left."""
    char = gm.now_in(world, game)[2]
    order = [b["suggests"]] + [s for s in world["stats"] if s != b["suggests"]]
    labels = [f"{s} {gm.stat_of(world, char, s):+d} ({chances(gm.stat_of(world, char, s))})" + (" — the story's" if s == b["suggests"] else "") for s in order]  # fmt: skip
    print(f"   How does {char['name']} meet it?")
    k = pick_one("   How? ", labels)
    if k is None:
        return None
    print(f"   {char['name']} meets it with {order[k]}.")
    return order[k]


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
    print(f"\n{CALL_KEYS}\n✋ Your call, GM. {who['name']} brings this in:\n   {fact}")
    ctx = (box.parent, now, gm.current(box, world)[1])
    met = clash.meets(box, fact)
    if met:
        choice = heads_up(met, reword=False, ctx=ctx, part="call")
        if choice is None:
            return None
        answer = choice != "old"
    else:
        choice = ""
        answer = yes("   Is that true in your world? (y/n) ", ctx, "call")
        if answer is None:
            return None
    if ASIDE in (choice, answer):
        print("   Set aside. Nobody needs to say why. Nothing is handed in or decided.")
        return ""
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


def story_foes(world: dict | None) -> list[tuple[str, str]]:
    """(label, stat block key) for the foes this story's own seated characters
    can fight with willow's play-fight (dw_story.py makes the fighters), or []
    when they can't: dndwright isn't installed, the story has no seated
    characters, or it is one aetheris5e's own party fights in. A story opts in
    by naming its foes in `"foes"` (keys of aetheris5e's stat blocks, e.g.
    "scorched_belt_raider"); one that doesn't has no such fight, as before."""
    if world is None or world["id"] in FIGHTS or not any(c.get("seat") for c in world.get("characters", [])):  # fmt: skip
        return []
    import importlib.util

    if importlib.util.find_spec("dndwright") is None:
        return []
    import dw_story

    out = []
    for k in world.get("foes", []):
        try:
            f = dw_story.from_statblock(k)
        except (KeyError, ValueError):
            continue
        out.append((f"The story's own: its heroes against a {f['name']} ({f['hp']} hit points, armor {f['ac']})", k))  # fmt: skip
    return out


def story_fight(table: Path, now: str, world: dict, world_file: Path | None, game: dict | None, key: str) -> bool | None:  # fmt: skip
    """The story's seated characters against one of aetheris5e's foes, fought
    by willow's play-fight, through the pin: dndwright's rules, on dice dropped
    in willow's tower one at a time, every blow a row on the record
    (`fight-begin`, `fight-row`). Not the box's other fights: fight.py never
    reads these, and `open_table.py check` has play-fight read them again from
    the record alone. True once fought; None if the person left."""
    import dw_story

    box = table / "record"
    foe = dw_story.from_statblock(key)
    party = dw_story.party_from_world(world)
    folder = table / "tower" / "fights"
    folder.mkdir(parents=True, mode=0o700, exist_ok=True)
    fighters = table / "tower" / "fighters.json"
    fighters.write_text(json.dumps([*party, foe], indent=1), encoding="utf-8")
    print(f"\n⚔️  {', '.join(f['name'] for f in party)} against a {foe['name']}")
    done = subprocess.run([sys.executable, str(PLAY_FIGHT), "--box", str(box), "fight", "--fighters", str(fighters), "--to", str(folder), "--now", now], capture_output=True, text=True, check=False)  # fmt: skip
    if done.returncode != kernel.ALIVE:
        print(f"   The fight didn't happen: {done.stderr.strip()}")
        return True
    for line in done.stdout.splitlines():
        if not line.startswith("("):
            print("   " + line)
    recs, _ = kernel.read(box / "record.jsonl")
    begun = max(r["n"] for r in recs if r["kind"] == session.FIGHT_BEGIN)
    summary = session.xfight_summary(recs, begun)
    won = {"party": "party", "foe": "foes"}.get(summary["outcome"], "stalemate")
    said = {"party": "The party won", "foes": "The party fell", "stalemate": "Neither side fell"}[won]  # fmt: skip
    standing = ", ".join(summary["party_survivors"] + summary["foe_survivors"]) or "no one"  # fmt: skip
    print(f"⚔️  {said} in {summary['rounds']} rounds. Still standing: {standing}.")
    if world is not None and "fight" in world.get("offers", []):
        return fight_stands(box, world, world_file, game, won == "party", now)
    print("   (What the fight means for the story is yours to say, GM.)")
    return True


def fight(table: Path, now: str, world: dict | None = None, world_file: Path | None = None, game: dict | None = None) -> bool | None:  # fmt: skip
    """A fight: one of aetheris5e's encounters, played by fight.py onto the
    record, blow by blow, then drawn as a board; or, in a story with seated
    characters, those characters against one of its foes, run by dndwright
    (story_fight). In a story that turns on a fight (one whose offers name
    `fight`: a moment written "when: the fight is won"), its end goes to the GM
    as a call (fight_stands). True once fought, False if it couldn't be, None
    if the person left."""
    listed = run(HERE / "fight.py", "list")
    names = [line.split()[0] for line in listed.stdout.splitlines() if line.strip()]
    descs = [line.strip().split(None, 1)[1] for line in listed.stdout.splitlines() if line.strip()]  # fmt: skip
    if listed.returncode != kernel.ALIVE:
        names, descs = [], []
    own = story_foes(world)
    if not names and not own:
        print("   A fight can't start here: aetheris5e's dice aren't reachable.")
        return False
    print("   Which fight?")
    k = pick_one("   Which? ", descs + [label for label, _ in own])
    if k is None:
        return None
    if k >= len(names):
        return story_fight(table, now, world, world_file, game, own[k - len(names)][1])
    done = run(HERE / "fight.py", "--table", table, "fight", names[k], "--now", now)
    if done.returncode != kernel.ALIVE:
        print(f"   The fight couldn't start: {(done.stderr or done.stdout).strip()}")
        return False
    blows = done.stdout.rstrip().splitlines()
    print("\n⚔️  " + "\n".join(blows[:-1]))
    shown = run(HERE / "fight.py", "--table", table, "board")
    if shown.returncode == kernel.ALIVE:
        print("\n" + shown.stdout.rstrip() + "\n")
    rows, _ = kernel.read(table / "record" / "record.jsonl")
    res = next(r for r in reversed(rows) if r["kind"] == "encounter-end")["result"]
    said = {"party": "The party won", "foe": "The party fell", "stalemate": "Neither side fell"}.get(res["outcome"], "It ended")  # fmt: skip
    standing = ", ".join(res["party_survivors"] + res["foe_survivors"]) or "no one"
    print(f"⚔️  {said} in {res['rounds']} rounds. Still standing: {standing}.")
    if world is not None and "fight" in world.get("offers", []):
        return fight_stands(table / "record", world, world_file, game, res["outcome"] == "party", now)  # fmt: skip
    print("   (What the fight means for the story is yours to say, GM.)")
    return True


def fight_stands(box: Path, world: dict, world_file: Path, game: dict, won: bool, now: str) -> bool | None:  # fmt: skip
    """The GM's call on how a fight stands for the story: "the party won",
    handed in as an offer of the kind `fight` and sealed on the GM's yes or
    declined on their no, so the moments written "when: the fight is won" (or
    lost) are the ones played. Answered against the dice, it's the GM's word
    over them: the fight stays on the record as it went, and the call beside
    it. True once answered, None if the person left."""
    who = gm.now_in(world, game)[2]["id"]
    print(f"\n✋ Your call, GM. The dice say the party {'won' if won else 'fell'}.")
    answer = yes("   Does it stand that the party won the fight? (y/n) ")
    if answer is None:
        return None
    done = session.step(box, world_file, now, "offer", who, "The party won the fight.", "--as", "fight")  # fmt: skip
    if done.returncode == kernel.REFUSED:
        raise RuntimeError(done.stderr.strip())
    _, game, _ = gm.current(box, world)
    subject = game["offers"][-1]["subject"]
    answered = run(KERNEL, "seal" if answer else "decline", "--box", box, "--now", now, subject)  # fmt: skip
    if answered.returncode != kernel.ALIVE:
        raise RuntimeError((answered.stderr or answered.stdout).strip())
    heard = session.step(box, world_file, now, "settle")
    if heard.returncode == kernel.REFUSED:
        raise RuntimeError(heard.stderr.strip())
    if answer != won:
        print("   Your word over the dice: the fight stays on the record as it went, and your call beside it.")  # fmt: skip
    print("   It stands: the party " + ("won." if answer else "lost."))
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
    rows, _ = kernel.read(table / "record" / "record.jsonl")
    names = dict.fromkeys(r["char"] for r in rows if r["kind"] == carry.KIND)
    over = [s for s in (carry.said(n, *carry.sheet(rows, n)) for n in names) if s]
    if over:
        print("Carried over (read this out loud too):")
        print("\n".join(f"  - {s}" for s in over))
        print()
    ends = [r for r in rows if r["kind"] == "session"]
    fought = session.fights(rows, ends[-1]) if ends else []
    if fought:
        print("Just for you, GM, how last time's fights ended:")
        print("\n".join(f.split("   (row")[0] for f in fought))
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
        try:
            return night(table, picked[0], picked[1], now)
        except Pause:
            print("\nPaused. Nobody needs to say why. Run this again when you're ready.")  # fmt: skip
            return kernel.ESCALATE
    except RuntimeError as e:
        print(f"\nSomething went wrong: {e}", file=sys.stderr)
        return kernel.REFUSED


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
