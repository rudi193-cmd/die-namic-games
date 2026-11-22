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
| [safe-app-store/](safe-app-store/) | the SAFE App Store at `ac07125`, without `apps/nasa-archive` (293 MB and 2,394 of its 4,362 files, a corpus the rest of the store isn't read by): 1,967 files; and beside it [UTETY](https://github.com/hornbook-knowledge/utety) at `56662d1`, the engine utety-chat runs on, and [terpsi-music](https://github.com/rudi193-cmd/terpsi-music) at `c1285af`, the youth music program's design, each with its pull requests and branches as pages (`history.py`; 19 and 15, 25 and 4): 2,368 files | `bash boxes/safe-app-store/rebuild.sh SCRATCH`, with the store beside die-namic-games or at `SAFE_APP_STORE`, UTETY at `../hornbook-knowledge/utety` or `UTETY`, terpsi-music at `../terpsi-music` or `TERPSI` (each left out, and said, without it); about 5 minutes |
| [looks/](looks/) | the four game masters of [gm-projects/](gm-projects/) at the same pins, their page files only (.tsx .vue .css .scss .html .md), Die-Namic's own `ui/` sources at HEAD, and book designs from `BOOKS` (default `../book-designs`, never in git): each picture with a `.md` note, read by willow's ocr when tesseract is installed | `bash boxes/looks/rebuild.sh SCRATCH`, with the projects beside die-namic-games or at `GM_PROJECTS`; about 10 seconds, then `bash boxes/looks/ask.sh SCRATCH "your words"` for any question, about a second |
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

**UTETY, beside the store**, answers what the store's own pages only cite:
its ground rules (`README.md:12`, the work and never the learner), where a
child's data stays (`utety/core/store.py`), mastery (`utety/core/mastery.py`,
the pattern the almanac, the forge and oakenscrolls borrow), and who says yes:
a session refuses to open without a guardian's grant (`loop.py:99`, PR #14,
B7), while the age gate is still to build (`docs/build-plan.md:153`). Its
history said two things its tree couldn't. The 2026-07-14 audit batch on
`claude/full-audit-kqozzy` (store transactions, the real-socket web tests, two
audits, the early-stage gaps) never reached main: main went on from PR #6
without it. And the handoff's open "nothing enforces consent yet" was closed
by PR #14 eleven days later. The store's `apps/oakenscrolls-office/NOTICE:4`
calls UTETY MIT; it is Apache-2.0. Asked about consent in its own words
("b7 consent gate authoritative model"), the box serves the pull request; in
ours, the store's other consent pages crowd it out.

**terpsi-music, beside the store**, is where two of the store's rules came
from: the decision boot's "absence surfaces as `unknown`, never as a result"
(its `CLAUDE.md` §13) and homestead's `L1`–`L5` rungs (its
`docs/SENSITIVITY.md`). It answers its own first question (`README.md:10`: how
little can the server be permitted to know, such that its full compromise is
survivable) and where §18 is. Its history: three branches never merged. One
landed reworked as `1d3eb7c`, and one's craft fix as `d89d6a1` without its
conformance record. `claude/highway-labor-sentence-xeksoj` holds five fixes to
guards that could not fail (a check bounded so zero passed it, FAIL branches
nothing could reach, a guard that mirrored §6 by hand), none of them on main.
And §18 still heads its blockers "one closed, three open", and the README
"four items block a first commit", though all four are struck closed.

**The session** answers each thing it decided with the passage that decided
it: the dice and the cup, why the heads-up isn't conflict_scan (open.md's
correction, and the commit that made it), the four choices of "mine stands
now", the rule underneath, the first three for a family table. Two answers
are partly off and are left as found, not tuned until they look right: "what
has to change in willow" also brings back a line of the journey, and the
dice want's first passage is the Decided list, with the table of the two
kinds of dice second.
