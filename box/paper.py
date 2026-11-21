"""paper.py: the characters' sheets on one page, in big type, to hold. Python 3.9+.

    python box/open_table.py sheets --table DIR --to FILE.html [--story ID]

One self-contained HTML file: inline style, no script, nothing fetched, large
high-contrast type (light, dark, and plain black on white when printed), one
card a seated character, the same facts as `s` at a roll (play.py's
sheet_data). The story is the one last played, unless --story names another (by its id);
when none has been played, the first by title.

Willow's `print --large` makes a page of an answer with its sources, and
writes the question to the record; a character sheet is no answer, so this is
Die-Namic's own, and writes nothing to the record. FILE is never overwritten
and never inside the table's record/ folder.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import play

CSS = """
:root{--bg:#fff;--fg:#000;--card:#f2f2f2;--rule:#000}
@media (prefers-color-scheme:dark){:root{--bg:#000;--fg:#fff;--card:#1a1a1a;--rule:#fff}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:28px/1.4 system-ui,sans-serif}
h1{font-size:1.4em;margin:0 0 .5em}
section{background:var(--card);border:4px solid var(--rule);border-radius:12px;padding:16px 20px;margin:0 0 20px;break-inside:avoid}
h2{font-size:1.5em;margin:0}
.role{font-size:1em;margin:0 0 .4em}
p{margin:.2em 0}b{font-weight:800}
ul{margin:.2em 0;padding-left:1.2em}
@media print{:root{--bg:#fff;--fg:#000;--card:#fff;--rule:#000}body{padding:0}}
"""


def render(title: str, data: list[dict]) -> str:
    cards = []
    for c in data:
        part = [f"<h2>{escape(c['name'])}</h2>"]
        if c["role"]:
            part.append(f'<p class="role">{escape(c["role"])}</p>')
        part.append(f"<p><b>Good at:</b> {escape(c['good'])}</p>")
        if c["carrying"]:
            part.append(f"<p><b>Carrying:</b> {escape(', '.join(c['carrying']))}</p>")
        if c["hurt"] is not None:
            part.append("<p><b>Hurt</b>" + (f": {escape(c['hurt'])}" if c["hurt"] else "") + "</p>")  # fmt: skip
        if c["true"]:
            part.append("<ul>" + "".join(f"<li>{escape(f)}</li>" for f in c["true"]) + "</ul>")  # fmt: skip
        cards.append("<section>" + "".join(part) + "</section>")
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(title)}: the sheets</title><style>{CSS}</style></head><body>"
        f"<h1>{escape(title)}</h1>\n" + "\n".join(cards) + "\n</body></html>\n"
    )


def inside(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def write(table: Path, to: Path, story: str | None = None) -> str | None:
    """Write the page; None when done, else why it was refused."""
    if inside(to, table / "record"):
        return "the page can't go inside the table's record folder"
    if to.exists() or to.is_symlink():
        return f"{to} is already there, and is never overwritten"
    if not to.parent.is_dir():
        return f"{to.parent} isn't a folder"
    rows, _ = play.kernel.read(table / "record" / "record.jsonl")
    found = play.stories(table, rows)
    pick = next((s for s in found if s[0]["id"] == story), None) if story else (found[0] if found else None)  # fmt: skip
    if pick is None:
        return f"no story {story}" if story else "the table has no stories"
    try:
        with open(to, "x", encoding="utf-8") as f:
            f.write(render(pick[0]["title"], play.sheet_data(table, pick[0])))
    except FileExistsError:
        return f"{to} is already there, and is never overwritten"
    return None
