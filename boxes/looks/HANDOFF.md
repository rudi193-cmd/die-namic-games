# Handoff: the looks box, and the GM's and players' screens (2026-11-22)

For the next session, which builds the screens. Read this, then
[my-table.md](my-table.md) (the maintainer's own words, the source of
every decision), [mock.md](mock.md) (the screens in ASCII) and the `looks`
entries in [../MEMORY.md](../MEMORY.md) (what each want found, with file and
line).

Branch: `ccr-c3a67a77-ubjzyq` in die-namic-games, pushed. No pull request.
Nothing was changed in willow. Nothing was sealed; no key was read.

## What was made

`boxes/looks/`, a box and a stack for Die-Namic's redesign, built one want
at a time with the maintainer.

| File | What it is |
|---|---|
| [rebuild.sh](rebuild.sh) | lays the box, its index, and runs the stack (about 15 s; the index rebuilds only when the pile changed) |
| [ask.sh](ask.sh) | asks the box any question from its index, about a second: `bash boxes/looks/ask.sh SCRATCH "your words" ...` |
| [stack.md](stack.md) | 10 wants, each a batch-ask scan of [questions/](questions/)`wantN.tsv` (46 questions) |
| [words.txt](words.txt) | how the maintainer asks, put into the words the pages use (`beastiary`, `binder`, `screen`, `tray`, ...) |
| [my-table.md](my-table.md) | the maintainer's table and every decision, in their words |
| [mock.md](mock.md) | the GM's screen, a lookup called to the centre, a fight, a kid's creature put in, a player's screen; what isn't built; what's open |
| [results/](results/) | the last run's page; [results/demos/](results/demos/) willow's two page demos, run and screenshotted, with how to make them again |

The pile (1,551 files, about 69,600 passages): the four AI game masters of
`gm-projects` at the same pins (page files only); Die-Namic's own design
pages, `box/` code, pages and worlds, `ui/` sources, the-table's README and
`boxes/MEMORY.md`; my-table.md and mock.md; willow's `share` whole and the
blackout, annex and johnson demos with annex_os.py and kiosk.py; willow's
`demo/craft-assembly` and four of its image apps' docs (photocraft,
drawcraft, artcraft, designcraft) at the demo's pins; and GM screen art
from `../screen-art` (empty so far).

## Setting up in a fresh session

    # willow at die-namic's pin (main is 2 files off it; see "Known" below)
    git -C ../Willow fetch origin 370f74a3fce0
    git -C ../Willow worktree add --detach ../willow-at-pin 370f74a3fce0
    export WILLOW_ROOT=$PWD/../willow-at-pin

    # the four game masters, beside die-namic-games
    git clone --filter=blob:none https://github.com/Sagesheep/NarrativeEngine-P ../narrativeengine-p
    git clone --filter=blob:none https://github.com/DTG404/inkandbone ../inkandbone
    git clone --filter=blob:none https://github.com/msadeqsirjani/dnd_ai_dm ../dnd_ai_dm
    git clone --filter=blob:none https://github.com/jschm42/taleweaver ../taleweaver

    # the image apps, at ../craft/NAME
    for n in photocraft drawcraft artcraft designcraft; do
      git clone --filter=blob:none --no-checkout https://github.com/storytold/$n ../craft/$n; done

    # tesseract, for the screen art's words (willow's ocr add-on)
    apt-get install -y tesseract-ocr

    bash boxes/looks/rebuild.sh /tmp/looks       # SCRATCH outside the repo
    bash boxes/looks/ask.sh /tmp/looks "your words"

A missing checkout is left out of the pile and said, never a failure.

## The design, as decided

**One page, a screen per seat.** The GM's page is the maintainer's real
table; a player's page is "their own screen", the same three panels from
their seat. "A gm can be a player sometimes too, at different tables": one
person's device holds their tables, `[ my tables ▾ ]` switches, and the
page is the screen of the seat they hold there.

| | Left | Centre | Right |
|---|---|---|---|
| **GM** | quick reference: the lookup, the bestiary, upcoming loot, planned battles | the binder's planned story, the dice box (centre of the view), active combat | the players |
| **Player** | my quick reference: the lookup (what's mine and what was sent to me), what I'm good at, previously on, our lines | the table: what the GM put on it, the dice, my hand (only I see it) | me: my character, my drawing, what I carry, my notes |

- **The binder** sits behind the GM's screen. Pages come out of it to the
  screen (the GM's alone) or the table (everyone's).
- **The lookup** lives in the left panel and comes into the centre when
  called. Anything on the left is called to the centre the same way.
- **The GM shares from their device to the others'** with willow's
  `share`: sealed answers packed for each player's key, checked on receipt,
  a `sent` row on the GM's chain and a `received` on the player's. It never
  goes online; how a package travels is the table's (a shared folder, a
  message).
- **Each seat is its own box.** A player's lookup asks their own box (what
  was sent to them, their notes) and can't reach the GM's binder by
  construction, as annex's compartments can't. This answers the `gm-only/`
  leak (open.md:579).
- **What only one seat sees** (a dealt hand, a cup, the GM's screen roll)
  is one mechanism: the maintainer's "blind deal happens all the time in
  card games"; open.md:580 says the same.
- **Pictures:** typing is the main way in; "the picture is just a
  picture". A kid types their creature or character and adds a photo of
  the drawing; the GM's yes puts it in the bestiary.
- **The pattern to build on:** willow's annex_os.py and blackout's kiosk.py,
  one self-contained page per person built from what the scene wrote,
  never reading a box, a key or a pile; choose who you are and see only
  your own. Dressed as the machine they pretend to be; ours is dressed in
  GM screen art.

## What each panel stands on (built)

- Bestiary: aetheris5e's stat blocks, named by a story's `"foes"`
  (box/dw-fights.md, `story_foes` in box/play.py).
- Planned battles: those foes in `box/worlds/*.json`.
- The planned story: `box/worlds/*.json`, scenes in order.
- Active combat: box/fight.py onto the record; box/board.py draws it.
- Players: the sheets (box/carry.py's rows, `s` at a roll), box/paper.py's
  big-type page.
- The lookup: box/ask.py (where to look, pile-rank), `kernel.py bite` (the
  answer), `rules.py ask` (sealed house rules word for word); for speed,
  index-cache and batch-ask (about 1 s) or pile-serve's pile-rank (0.13 s).
- The GM's screen roll: willow's `dice-tower`.
- Your call, GM: offers and seals, as box/play.py does in the terminal.
- x, p, lines and veils: box/safety.py and play.py.
- Sending to the table: willow's `share`.

## Not built (the gaps the screens show)

- Upcoming loot: nothing keeps loot not yet found.
- A live board: board.py draws a fight at its end.
- Roll hidden: dice-tower is built; the play path doesn't reach it.
- The picture kept and shown: the pile reads words only.
- The sheet a player sees: it exists; nothing shows it.
- A hand hidden on the record: `blind-deal` (planned in willow).
- One person's many tables in one page, and sharing the GM's chair
  (open.md item 15; `grant`, `witness` are ideas).
- Live pages: both willow page demos are built once from a finished
  scene; a table's must follow packages arriving during the night.
- The shared view (open.md item 16): pictures, a map, the dice landing
  where everyone sees.

## Open (the maintainer's to decide)

- **The tidy-up:** does a kid's drawing go in as made, or through the image
  suite first (photocraft crops and removes a background; drawcraft traces
  a sketch)? Left open.
- **Screen art:** none in `../screen-art` yet. Each picture wants a `.md`
  note beside it: name, publisher, year, which side (GM's or table's), where
  it came from, what to take.
- **How a package travels** at their table (a shared folder, or something
  else).
- **Which rulebooks** go in the binder (PDFs, through willow's `pdf`
  add-on).

## Known

- `ui/build.py` and every box fail against willow's main checkout: it is
  two files off `willow.pin.json` (first `adapters/stdlib/session-seal/README.md`).
  Everything here ran against a worktree at the pin. Fixing the pin is its
  own change.
- `boxes/MEMORY.md` is in the pile, so the box can quote back what was
  written about it: read past an `ours/boxes/MEMORY.md` hit to the page it
  cites.
- "palette" means three things in NarrativeEngine-P (colours, glyphs, a
  command palette).
- tesseract misreads children's handwriting often; typing comes first.

## How this was worked, and what went wrong

One want at a time, in the maintainer's words, asked of the box before
anything was proposed. Twice the answer was wrong because the box was not
asked enough: the pile lacked open.md (so `share` was called a gap, and
the GM's side "not designed"), and willow's checkout was searched over
GitHub instead of locally. Both were caught by the maintainer. Ask our own
pages first, ask several ways, and search the checkouts that are here.
