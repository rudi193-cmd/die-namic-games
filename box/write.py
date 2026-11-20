"""write.py: write a story by answering a few questions, then play it. Python 3.9+.

    python box/write.py

The writing path open.md lays out, in a plain terminal: what it's about (or
an idea to start from), four small boxes (what it's called, where, who, what
the heroes are good at), then the moments one at a time, in plain words.
Play's "Write your own" comes here too.

It writes the one story file every door writes: the markdown author.py
reads (the shape story-timeline exports), into the box's stories/, and the
world author.py makes of it, checked by game-master, into worlds/. Nobody
types an id: they are made from the names. A story is played as soon as it
has a title, a place, one character someone plays, and one moment.

The ideas offered when stuck are dealt from the box's own words by ideas.py.
No model is asked: suggestions from a model are off unless the writer asks,
and this doesn't ask.

A moment's outcome left blank is written as "(GM: you say what happens.)",
so the story plays and the GM says it aloud. Keeping what the GM says on the
record is still to build (open.md, the GM's moments).

Nothing is written until the story is done; leaving before then writes
nothing. A story is never written over one already in the box.

Exit codes, the kernel's: 0 written (and played, if asked); 42 left before
the end; 2 refused.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import author
import play  # the way in: its box, its questions, its night

kernel = play.kernel
STRENGTHS = ["Brave", "Clever", "Kind"]
BLANK = "(GM: you say what happens.)"
OUTCOMES = (("strong", "If it goes great"), ("weak", "If it sort of works"), ("miss", "If it goes wrong"))  # fmt: skip


class Left(Exception):
    """The writer left before the story was done."""


def said(prompt: str, default: str = "") -> str:
    """What the writer typed, cleaned for the story file; DEFAULT on Enter."""
    got = play.ask(prompt)
    if got is None:
        raise Left
    got = re.sub(r"\s+", " ", got.replace("|", "/")).strip().lstrip("-*#").strip()
    return got or default


def must(prompt: str, why: str) -> str:
    while True:
        got = said(prompt)
        if got:
            return got
        print(f"  {why}")


def choose(prompt: str, options: list[str]) -> int:
    """The number of the option picked, from 1; the first on Enter."""
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        got = said(prompt, "1")
        if got.isdigit() and 1 <= int(got) <= len(options):
            return int(got) - 1
        print(f"  Type a number from 1 to {len(options)}.")


def slug(name: str, taken: set) -> str:
    """An id made from a name: lower case, dashes for spaces; never a taken one."""
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "it"
    out, n = base, 2
    while out in taken:
        out, n = f"{base}-{n}", n + 1
    taken.add(out)
    return out


def ideas(table: Path) -> list[str]:
    """Three ideas dealt from the box's own words, by ideas.py."""
    got = play.run(HERE / "ideas.py", "--table", table)
    seeds = got.stdout.split("## Seeds")[-1].split("\n## ")[0].splitlines()
    out = []
    for line in seeds:
        line = line.strip()
        if line.startswith("- ") and line[2:] not in out:
            out.append(line[2:])
    return out[:3]


def ask_story(table: Path) -> dict:
    """The writer's answers, as a story: title, place, cast, strengths, moments."""
    print("✏️  Let's write a story.\n")
    about = said("What's it about? (a sentence is plenty, or press Enter) ")
    if not about:
        dealt = ideas(table)
        if dealt:
            print("Stuck? Try one of these, or write your own:")
            pick = choose("Which one? (or press Enter for the first) ", dealt + ["My own idea"])  # fmt: skip
            about = dealt[pick] if pick < len(dealt) else must("What's it about? ", "A sentence is enough.")  # fmt: skip
    title = must("\nWhat's it called? ", "A story needs a name.")
    place = must("Where does it happen? ", "Somewhere for it to happen: a garden, a ship, a kitchen.")  # fmt: skip
    cast = []
    print("\nWho's in it? (a name, then a few words: Mira, a kid who likes bugs)")
    while True:
        who = said("  Someone: " if cast else "  The first one: ")
        if not who:
            if any(c["seat"] for c in cast):
                break
            print("  Someone at the table needs to play someone.")
            continue
        name, _, role = (p.strip() for p in who.partition(","))
        if name.lower() in (c["name"].lower() for c in cast):
            print(f"  There's already a {name} in it; give this one another name.")
            continue
        seat = play.yes(f"  Does someone at the table play {name}? (y/n) ")
        if seat is None:
            raise Left
        cast.append({"name": name, "role": role, "seat": seat})
        print("  (press Enter when that's everyone)")
    given = said(f"\nWhat are your heroes good at? (press Enter for {', '.join(STRENGTHS)}) ")  # fmt: skip
    strengths = [s.strip().title() for s in given.split(",") if s.strip()] or STRENGTHS
    story = {"about": about, "title": title, "place": place, "cast": cast, "strengths": strengths, "moments": []}  # fmt: skip
    while True:
        kinds = ["Someone tries something", "A question for the GM"] + (["That's the story"] if story["moments"] else [])  # fmt: skip
        print("\nWhat happens next?" if story["moments"] else "\nWhat happens first?")
        kind = choose("Which? ", kinds)
        if kind == 2:
            return story
        story["moments"].append(ask_try(story) if kind == 0 else ask_question(story))


def ask_try(story: dict) -> dict:
    played = [c for c in story["cast"] if c["seat"]]
    who = 0
    if len(played) > 1:
        print("Who tries it?")
        who = choose("Who? ", [c["name"] for c in played])
    what = must(f"What does {played[who]['name']} try? ", "Say what they try: she picks up the egg.")  # fmt: skip
    print("Using?")
    using = choose("Which? ", story["strengths"])
    print("(leave one blank and the GM makes it up on the night)")
    outcomes = {k: said(f"{label}: ", BLANK) for k, label in OUTCOMES}
    return {"kind": "action", "by": played[who]["name"], "prompt": what, "suggests": story["strengths"][using], "outcomes": outcomes}  # fmt: skip


def ask_question(story: dict) -> dict:
    question = must("What's the question? ", "Ask it the way the GM would: is the egg a real dragon?")  # fmt: skip
    fact = must("If the GM says yes, what's true? ", "Say it as a fact: the egg is a real dragon's.")  # fmt: skip
    gm = [c for c in story["cast"] if not c["seat"]] or story["cast"]
    return {"kind": "decision", "prompt": question, "fact": fact, "by": gm[0]["name"]}


def sentence(text: str) -> str:
    """TEXT as a sentence: a capital first, a stop last."""
    text = text[:1].upper() + text[1:]
    return text if text.endswith((".", "!", "?")) else text + "."


def markdown(story: dict, sid: str) -> str:
    """The story file, in the shape author.py reads."""
    ids: set = set()
    who = {c["name"]: slug(c["name"], ids) for c in story["cast"]}
    pid = slug(story["place"], ids)
    lines = ["<!-- written with box/write.py -->", f"# {story['title']}", "", f"id: {sid}",
             f"setting: {sentence(story['about'] or 'in ' + story['place'])}",
             f"stats: {', '.join(story['strengths'])}", "base stat: 1", "", "## Characters", ""]  # fmt: skip
    for c in story["cast"]:
        lines.append(f"- {who[c['name']]}: {c['name']} | {c['role']}" + (" | seated" if c["seat"] else ""))  # fmt: skip
    lines += ["", "## Places", "", f"- {pid}: {sentence(story['place'])[:-1]}", ""]
    lines += [f"## Scene start: {sentence(story['place'])[:-1]} @ {pid}", ""]
    for i, m in enumerate(story["moments"], 1):
        lines += [f"### {m['prompt']}", "", f"id: m{i}", f"kind: {m['kind']}"]
        if m["kind"] == "action":
            lines += [f"by: {who[m['by']]}", f"suggests: {m['suggests']}", ""]
            lines += [f"- {k}: {m['outcomes'][k]}" for k, _ in OUTCOMES]
        else:
            lines += [f"proposed by: {who[m['by']]}", f"fact: {m['fact']}"]
        lines.append("")
    return "\n".join(lines)


def write(table: Path) -> tuple[dict, Path]:
    """A story asked for, written into the box, and its world made: (world, file)."""
    story = ask_story(table)
    taken = {p.stem for p in (table / "worlds").glob("*.json")} | {p.stem for p in (table / "stories").glob("*.md")}  # fmt: skip
    sid = slug(story["title"], set(taken))
    text = markdown(story, sid)
    try:
        world = author.gm.validate(author.read(text))
    except (author.StoryError, author.gm.WorldError) as e:
        raise RuntimeError(f"the story didn't come out right: {e}") from None
    (table / "stories").mkdir(exist_ok=True)
    (table / "stories" / f"{sid}.md").write_text(text, encoding="utf-8")
    made = table / "worlds" / f"{sid}.json"
    made.write_text(json.dumps(world, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")  # fmt: skip
    print(f"\n🌱 {world['title']} is written: {len(story['moments'])} moment{'s' if len(story['moments']) != 1 else ''}.")  # fmt: skip
    return world, made


def compose(table: Path, now: str) -> int:
    """Write a story, then play it if the writer wants to."""
    try:
        world, made = write(table)
    except Left:
        print("Nothing was written. Run this again to start a story.")
        return kernel.ESCALATE
    go = play.yes("Play it now? (y/n) ")
    if not go:
        print("It's in your stories, ready when you are.")
        return kernel.ALIVE
    return play.night(table, world, made, now)


def main(argv: list[str]) -> int:
    if argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return kernel.REFUSED
    now = os.environ.get("DIE_NAMIC_NOW") or kernel.now()
    try:
        return compose(play.lay(play.home()), now)
    except RuntimeError as e:
        print(f"\nSomething went wrong: {e}", file=sys.stderr)
        return kernel.REFUSED


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
