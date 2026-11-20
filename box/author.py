"""author.py: a story written as markdown, made into a world game-master plays. Python 3.9+.

    python box/author.py STORY.md [--to WORLD.json]

For writing between sessions: a new story, or the next chapter of one, in
plain headings and `key: value` lines, the way the binder is written. It is
the shape story-timeline's `export-story` writes a timeline out in, so a
story can be written in story-timeline, the writer's workbench, and played
here; a comment line, as the export's first, is skipped. It
prints the world as JSON, or writes it to WORLD.json (never over a file
that is there), and every world it makes is game-master's own, checked by
game-master's `validate`. A line it can't read is refused with its number.

The shape, in order:

    # Title
    id: wasp-nest
    setting: One line of where and when.
    stats: Grit, Wit, Heart
    base stat: 1
    offers: guest                       (the kinds of offer it turns on; optional)

    ## Characters
    - pell: Pell | miller's apprentice | seated | Grit 2, Heart 1
    - cogwen: Cogwen | the keeper        (no "seated": the GM's to play)

    ## Places
    - ceiling: The cellar ceiling

    ## Scene up: Up into the ceiling @ ceiling
    Opening lines, one a line.

    ### The prompt, as the GM says it.
    id: climb
    kind: action                        (or: decision)
    by: juno                            (whose beat it is; optional)
    suggests: Wit                       (an action's approach)
    when: up::climb is weak, miss       (or: offered guest is sealed;
                                         or: sealed clockwork-cellar::room::free is sealed,
                                         a ruling in an earlier chapter)
    - strong: what happens
    - weak: what happens
    - miss: what happens
    proposed by: vell                   (a decision's)
    fact: what the ruling would make true

A refusal names the line in the story, wherever it was found: a key that
isn't a story's, or a name game-master can't find (a stat, a seated
character, a place, an earlier beat), with the nearest name it might have
meant; a line that isn't a story's at all says what it looks meant to
be (an id with capitals, a scene without its place). Keys and section
headings may be written in any case, and a list item with `*` or `-`.

Exit codes, the kernel's: 0 made; 2 refused.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import willow_pin

ROOT = willow_pin.root()  # willow, where its pieces live, held to willow.pin.json
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "adapters" / "stdlib" / "game-master"))
import game_master as gm
import kernel

KEY = re.compile(r"^([a-z][a-z ]*):\s*(.*)$", re.IGNORECASE)
CHARACTER = re.compile(r"^[-*] ([a-z0-9-]+):\s*(.+)$")
OUTCOME = re.compile(r"^[-*] (strong|weak|miss):\s*(.+)$")
BEAT_PATH = {"proposed by": "proposes.proposed_by", "fact": "proposes.fact"}
WHERE = re.compile(r"^((?:world|characters|places|scenes)(?:\[\d+\]|\.[a-z_]+)*)")
SCENE = re.compile(r"^## Scene ([a-z0-9-]+):\s*(.+?)\s*@\s*([a-z0-9-]+)$")
BEAT_WHEN = re.compile(r"^([a-z0-9-]+::[a-z0-9-]+) is (.+)$")
OFFER_WHEN = re.compile(r"^offered ([a-z0-9-]+) is (.+)$")
SEALED_WHEN = re.compile(r"^sealed ([a-z0-9-]+::[a-z0-9-]+::[a-z0-9-]+) is (.+)$")


class StoryError(ValueError):
    """A story that can't be read; the message names the line."""


def listed(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def character(cid: str, text: str, at: int) -> dict:
    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 2:
        raise StoryError(
            f"line {at}: a character is `- id: Name | role [| seated] [| Stat N, ...]`"
        )
    c = {"id": cid, "name": parts[0], "role": parts[1], "seat": False, "stats": {}}
    for p in parts[2:]:
        if p == "seated":
            c["seat"] = True
        elif p:
            for s in listed(p):
                m = re.fullmatch(r"(\S+)\s+(-?\d+)", s)
                if not m:
                    raise StoryError(
                        f"line {at}: {s!r} isn't a stat and a number, as Grit 2"
                    )
                c["stats"][m.group(1)] = int(m.group(2))
    return c


def when_of(text: str, at: int) -> dict:
    if m := SEALED_WHEN.match(text):
        return {"sealed": m.group(1), "is": listed(m.group(2))}
    if m := OFFER_WHEN.match(text):
        return {"offered": m.group(1), "is": listed(m.group(2))}
    if m := BEAT_WHEN.match(text):
        return {"beat": m.group(1), "is": listed(m.group(2))}
    raise StoryError(
        f"line {at}: when is `scene::beat is strong, weak`, `offered KIND is sealed`"
        " or `sealed story::scene::beat is sealed`"
    )


def why_not(line: str, section: str) -> str:
    """What a line that isn't part of a story was most likely meant to be."""
    ids = "an id is lower case, with dashes for spaces, as old-vell"
    if line.lower().startswith("## scene"):
        return f": a scene is `## Scene id: Title @ place`, and {ids}"
    if OUTCOME.match(line):
        return ": an outcome comes under a beat (### The prompt)"
    if re.match(r"^[-*] [^:]+:", line) and section in ("characters", "places"):
        return f": {ids}"
    if line.startswith("## "):
        return ": a section is ## Characters, ## Places or ## Scene id: Title @ place"
    return ""


def read(text: str, lines: dict | None = None) -> dict:
    """The world a story's markdown writes, or StoryError naming the line.

    LINES, if given, is filled with where each part was written: a path as
    game-master's validate names it (scenes[0].beats[1].by) to its line."""
    world = {"characters": [], "places": [], "scenes": []}
    section, scene, beat = "head", None, None
    lines = {} if lines is None else lines
    bw = ""
    for at, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or (line.startswith("<!--") and line.endswith("-->")):
            continue
        if line.startswith("# ") and section == "head" and "title" not in world:
            world["title"] = line[2:].strip()
        elif line.lower() in ("## characters", "## places"):
            section, scene, beat = line[3:].lower(), None, None
        elif m := SCENE.match(line):
            scene = {"id": m.group(1), "title": m.group(2), "place": m.group(3), "opening": [], "beats": []}  # fmt: skip
            world["scenes"].append(scene)
            section, beat = "scene", None
            lines[f"scenes[{len(world['scenes']) - 1}]"] = at
        elif line.startswith("### "):
            if scene is None:
                raise StoryError(
                    f"line {at}: a beat comes inside a scene (## Scene id: Title @ place)"
                )
            beat = {"prompt": line[4:].strip()}
            scene["beats"].append(beat)
            bw = f"scenes[{len(world['scenes']) - 1}].beats[{len(scene['beats']) - 1}]"
            lines[bw] = at
        elif section in ("characters", "places") and (m := CHARACTER.match(line)):
            if section == "characters":
                world["characters"].append(character(m.group(1), m.group(2), at))
            else:
                world["places"].append({"id": m.group(1), "name": m.group(2).strip()})
            lines[f"{section}[{len(world[section]) - 1}]"] = at
        elif beat is not None and (m := OUTCOME.match(line)):
            beat.setdefault("outcomes", {})[m.group(1)] = m.group(2)
            lines[f"{bw}.outcomes.{m.group(1)}"] = at
        elif (m := KEY.match(line)) and (section == "head" or beat is not None):
            key, value = m.group(1).lower(), m.group(2).strip()
            if beat is None:
                head = {"id": "id", "setting": "setting", "stats": "stats", "base stat": "base_stat", "offers": "offers"}  # fmt: skip
                if key not in head:
                    raise StoryError(
                        f"line {at}: {key!r} isn't a story's: {', '.join(head)}"
                    )
                lines[f"world.{head[key]}"] = at
                if key == "base stat" and not re.fullmatch(r"-?\d+", value):
                    raise StoryError(f"line {at}: base stat is a number, as 1, not {value!r}")  # fmt: skip
                world[head[key]] = listed(value) if key in ("stats", "offers") else int(value) if key == "base stat" else value  # fmt: skip
            else:
                fields = {
                    "id": "id",
                    "kind": "kind",
                    "by": "by",
                    "suggests": "suggests",
                }
                lines[f"{bw}.{BEAT_PATH.get(key, key)}"] = at
                if key in fields:
                    beat[fields[key]] = value
                elif key == "when":
                    beat["when"] = when_of(value, at)
                elif key in ("proposed by", "fact"):
                    beat.setdefault("proposes", {})["proposed_by" if key == "proposed by" else "fact"] = value  # fmt: skip
                else:
                    raise StoryError(f"line {at}: {key!r} isn't a beat's: id, kind, by, suggests, when, proposed by, fact")  # fmt: skip
        elif scene is not None and beat is None and not OUTCOME.match(line):
            scene["opening"].append(line)
        else:
            raise StoryError(f"line {at}: {line[:60]!r} isn't part of a story here{why_not(line, section)}")  # fmt: skip
    world.setdefault("base_stat", 1)
    return world


def line_of(why: str, lines: dict) -> int | None:
    """The story line a validate message's path was written on: the path
    itself, or the nearest part of it that was written (a beat, a scene)."""
    m = WHERE.match(why)
    path = m.group(1) if m else ""
    while path:
        if path in lines:
            return lines[path]
        up = re.sub(r"(\.[a-z_]+|\[\d+\])$", "", path)
        path = "" if up == path else up
    return None


def candidates(why: str, world: dict) -> list[str]:
    """The names a refused name was meant to be one of, by what was refused."""
    if " is not a stat" in why or "not one of the stats" in why:
        return list(world.get("stats", []))
    if " is not a seated character" in why:
        return [c["id"] for c in world["characters"] if c.get("seat")]
    if " is not one of the places" in why:
        return [p["id"] for p in world["places"]]
    if " is not an earlier beat" in why:
        at = re.match(r"scenes\[(\d+)\]\.beats\[(\d+)\]", why)
        i, j = (int(at.group(1)), int(at.group(2))) if at else (0, 0)
        return [
            f"{sc['id']}::{b.get('id')}"
            for n, sc in enumerate(world["scenes"][: i + 1])
            for b in (sc["beats"][:j] if n == i else sc["beats"])
        ]
    if " is not one of world.offers" in why:
        return list(world.get("offers", []))
    if ".kind " in why:
        return ["action", "decision"]
    return []


def nearest(why: str, world: dict) -> str | None:
    """The name nearest the one refused, if one is near: 'pel' to 'pell'."""
    m = re.search(r"'([^']*)'", why)
    names = candidates(why, world)
    if not m or not names:
        return None
    said = m.group(1)
    if "::" in said:  # scene::beat: the scene's part shared, so each part on its own
        parts = said.split("::")
        near = [n for n in names if all(close(a, [b]) for a, b in zip(parts, n.split("::")))]  # fmt: skip
        return near[0] if near else None
    got = close(said, names)
    return got if got != said else None


def close(said: str, names: list[str]) -> str | None:
    """The name SAID was nearest meant to be: the same but for case, or near."""
    same = [n for n in names if n.lower() == said.lower()]
    near = same or difflib.get_close_matches(said, names, n=1, cutoff=0.6)
    return near[0] if near else None


def make(path: Path) -> dict:
    lines: dict = {}
    world = read(path.read_text(encoding="utf-8"), lines)
    try:
        return gm.validate(world)
    except gm.WorldError as e:
        why = str(e)
        at = line_of(why, lines)
        near = nearest(why, world)
        where = f"line {at}: " if at else ""
        hint = f"; did you mean {near!r}?" if near else ""
        raise StoryError(f"{path.name}: {where}{why}{hint}") from None


def main(argv: list[str]) -> int:
    opts, args, it = {}, [], iter(argv)
    for a in it:
        if a == "--to":
            opts[a] = next(it, "")
        else:
            args.append(a)
    if len(args) != 1 or ("--to" in opts and not opts["--to"]):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return kernel.REFUSED
    try:
        world = make(Path(args[0]))
    except (OSError, StoryError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return kernel.REFUSED
    text = json.dumps(world, indent=1, ensure_ascii=False) + "\n"
    if "--to" not in opts:
        print(text, end="")
        return kernel.ALIVE
    to = Path(opts["--to"])
    if to.exists():
        print(f"refused: {to} is there; a world is never written over", file=sys.stderr)
        return kernel.REFUSED
    to.write_text(text, encoding="utf-8")
    scenes = world["scenes"]
    print(f"wrote {to}: {world['title']}, {len(scenes)} scenes, {sum(len(s['beats']) for s in scenes)} beats")  # fmt: skip
    return kernel.ALIVE


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
