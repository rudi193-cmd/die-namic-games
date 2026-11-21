"""safety.py: what never happens at our table, and what happens off-screen. Python 3.9+.

A family writes it once, in their own words, as a page in the table's pile:

    pile/our-lines.md

    ## Lines
    - spiders
    - a pet getting hurt

    ## Veils
    - kissing

A line never happens in the story: a moment that touches one isn't read,
and the GM says what happens instead. A veil can happen, off-screen: the
moment isn't played out, and the GM says it in passing. No page, nothing
changes. A line or veil touches a text when every word of it that carries
meaning is there (spiders, spider; a pet getting hurt: pet, hurt), so a
line is never missed for a plural, and a word alone in a longer line
doesn't trip it.

The X-card is the other half: at any roll, x sets the next part aside, no
reason asked. Only that it happened is kept (play.py's `table-x` row):
never who, never why.
"""

from __future__ import annotations

import re
from pathlib import Path

PAGE = "our-lines.md"
X = "table-x"
QUIET = frozenset({"a", "an", "the", "of", "to", "and", "or", "in", "on", "at", "for", "with", "by", "any", "no", "not", "being", "getting", "get", "gets", "is", "are", "be"})  # fmt: skip


def read(table: Path) -> tuple[list[str], list[str]]:
    """The table's (lines, veils), each as written; both empty with no page."""
    page = table / "pile" / PAGE
    if not page.is_file():
        return [], []
    got: dict[str, list[str]] = {"line": [], "veil": []}
    under = None
    for raw in page.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if s.startswith("#"):
            head = words(s)  # "Lines", "Our lines", "## Veils"
            under = "line" if {"line", "lines"} & set(head) else "veil" if {"veil", "veils"} & set(head) else None  # fmt: skip
        elif under and s[:1] in ("-", "*") and s[1:].strip():
            got[under].append(s[1:].strip())
    return got["line"], got["veil"]


def words(text: str) -> list[str]:
    return [w.removesuffix("'s") for w in re.findall(r"[a-z0-9']+", text.lower())]


def same(w: str, t: str) -> bool:
    """One word and another, the same but for a plural."""
    return t == w or t in (w + "s", w + "es") or w in (t + "s", t + "es")


def touches(entries: list[str], text: str) -> str | None:
    """The first entry every meaning word of which is in TEXT, or None."""
    ts = words(text)
    for e in entries:
        need = [w for w in words(e) if w not in QUIET] or words(e)
        if need and all(any(same(w, t) for t in ts) for w in need):
            return e
    return None
