# Boxes

Two willow boxes and the stacks that ask them, made on 2026-11-20 as willow's
own [demo/kept](https://github.com/willow-memory/Willow/tree/main/demo/kept)
is made: a fresh kernel box whose pile is one repository's content pinned
by commit, a words list, a stack of wants each with the add-on step that
answers it, and the last run's page. A box is data and stays out of git, as
ai-game-master keeps a played campaign home; what is kept here is how to lay
it again, and what it said.

The family's own stack is beside the box's other pages, at
[../box/family-night.md](../box/family-night.md), run with
`python box/open_table.py family --table DIR`.

| Box | Its pile | Rebuild |
|---|---|---|
| [safe-app-store/](safe-app-store/) | the SAFE App Store at `ac07125`, without `apps/nasa-archive` (293 MB and 2,394 of its 4,362 files, a corpus the rest of the store isn't read by): 1,967 files | `bash boxes/safe-app-store/rebuild.sh SCRATCH`, with the store beside die-namic-games or at `SAFE_APP_STORE`; about 45 s |
| [session-2026-11-20/](session-2026-11-20/) | what the session of 2026-11-20 made, at `db37b51`, the last commit before this folder: open.md, README.md, box/README.md, every commit's own message as `tonight.md`, and the journey played end to end on a fresh box (`journey.txt`) | `bash boxes/session-2026-11-20/rebuild.sh SCRATCH`; about a second |

Each folder holds `stack.md` (the wants, as proposals: cut any, add your
own), `words.txt` (how its readers ask, put into the words its pages use),
`rebuild.sh`, and `results/`: the last run's `page.md` and its step log,
the machine's paths written `<scratch>`. Willow is found as the box finds
it (`WILLOW_ROOT`, or beside), held to [../willow.pin.json](../willow.pin.json).
The key each rebuild makes is a scratch key outside the box; nothing is ever
sealed with it.

## What they said

**The store** answers what it is from its own law (`CLAUDE.md:15`: "a store
is a provision-house… not a shop"; `stores/README.md:4`), the promotion bar
and why the maker can't promote their own build, when the house first said
it already knew (2026-08-04), and where Die-Namic is first named (the
lineage, 2026-01-15). `box-health` is the step flagged: 66 images and
binaries the kernel doesn't read, which a repository has. A `todo` want was
tried and cut: in this store "need to" is mostly prose (utety-chat's
lectures), 404 lines of it, and a want that answers with noise teaches
people to stop reading the page.

**The session** answers each thing it decided with the passage that decided
it: the dice and the cup, why the heads-up isn't conflict_scan (open.md's
correction, and the commit that made it), the four choices of "mine stands
now", the rule underneath, the first three for a family table. Two answers
are partly off and are left as found, not tuned until they look right: "what
has to change in willow" also brings back a line of the journey, and the
dice want's first passage is the Decided list, with the table of the two
kinds of dice second.
