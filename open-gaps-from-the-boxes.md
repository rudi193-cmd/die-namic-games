# What the boxes already hold on open.md's gaps

[open.md](open.md) ends its play path with eighteen things "a real table does
that isn't in yet". On 2026-11-19 each was put, as a question, to three piles
on the maintainer's machine, and this page is what they served: where
something that answers a gap already exists, where something is near, and
where three piles hold nothing. A gap with nothing found is said as that; it
is a result, not a hole in the asking to paper over.

It adds no design. It is a list of places to look before building.

## What was asked, and of what

- **This repository**, at `9109dc8` on the branch that wrote open.md: its
  docs, the comments and docstrings of its code, every commit's message.
- **The willow repositories**: Willow, Nestor and five more of the
  maintainer's, the same three kinds of text, as last gathered on
  2026-11-11.
- **The game master's pile**: the tables, worlds, sheets and rules kept
  beside the-table before it moved here.

Each gap was asked in a sentence of its own words through willow's
`fair-merge`, which ranks each pile by itself and takes turns, so the
largest cannot crowd the others out. Eight were asked a second time in
other words. The kernel serves a passage only when it holds half a
question's content words, so "nothing" means no passage did, not that the
idea is nowhere.

**Two things the asking ran into.** Both older indexes refused to answer
("made with another kernel.py; index again") and were indexed again first.
And a whole sentence finds little: "lines and veils, X-card" served nothing
anywhere, and most of what is below came from shorter second questions
(`attendance`, `lineage`, `advantage`).

## At the roll

**1. Players rolling their own dice.** Nothing built, in any pile. What is
there is the leave to build it: Willow's constitution, VI.8 as narrowed on
2026-11-09 (commit `b590dea5`), says "what the person enters on purpose to
be recorded is theirs to keep". A roll typed in and kept as said is that.
The nearest door here is the blank moment in `box/play.py`, which already
keeps what the GM types and says yes to.

**2. The player choosing how.** Near. open.md already notes game-master's
`act` takes any stat. The piles add `the-table/the_table/menu.py` (commit
`815fd55c`): code turns `legal_moves(seat)` into a menu, "the one way a
model picks a move". The same menu, shown to a person, is the choice.

**3. Helping, and paying for a reroll.** The rule is written down and not
played. `game-lab/rules/COMPENDIUM.md` holds advantage and disadvantage
(two d20s, the higher or the lower). Outside this repository, Nestor's
`audits/2026-08-19-capability-probe/lives/resolution.py` implements
advantage and inspiration for its simulated lives. For a reroll paid for:
nothing; the game master's pile holds no passage with the word.

**4. The cup and the screen roll.** Not built anywhere. This repository's
commit `6bf7126d` states the hole (a roll seeded by a public row can be
foreseen). Willow pull request 382, opened the same day, builds the half
that hides the order: one close choice in five is shown with nothing
recommended. Its prediction is kept with the pick, not committed before
it, so the cup itself is still to build.

## The characters

**5. What happens to them carries over.** Near, for things; nothing, for
wounds. Willow's `lending` finds "what you lent, to whom and when, and which
are still out", and holds that a thing lent in parts is out until every
part is back; `debts` lists who owes whom and nets nothing. Both read plain
lines in notes, so a thing carried or spent, written as a line in a night's
note in the binder, is already theirs to find. No pile holds anything that
keeps a wound.

**6. Who is at the table.** A rule to keep, before anything is built.
`the-table/docs/homestead-table-vision.md` says the Table "does not record
who was present or how a person behaved — no attendance log, no per-person
profile". Willow has an `attendance` add-on, and by that line it is not the
answer here: a guest is a character. One exists already:
`ai-game-master/docs/poc_vander_room.py` walks a guest character into the
valley and the GM says yes.

**7. A sheet the player can see.** The sheet exists; nothing shows it.
`the-table/the_table/story_session.py` keeps a character sheet per seat and
sets the engine's stats from it before every roll. Willow's `print` has
`--large`, "big, high-contrast type", which would put one on paper.

**8. Growing.** Nothing, asked three ways (advancement, levels, getting
better). The only passage is the rule itself, in
`game-lab/rules/COMPENDIUM.md`: levels 1 to 20 and a proficiency bonus that
rises.

## The story

**9. The GM making up a scene.** Near. `box/write.py` (commit `1c9bfdd6`)
"writes the one story file every door writes". A scene made up mid-night
would be more of that file; nothing appends to it during play.

**10. Fights that change the story.** Near. `box/README.md` records that a
beat "can now say `when`: it is played only if an earlier beat came out
one of its ways". A fight's ending is kept on the record and is not yet one of
the ways a beat can wait on.

**11. Time pressing.** Nothing. Willow's `coming-up` reads dates in notes;
no pile holds a count the table watches fall during play.

**12. A replaced truth no longer unlocking.** Built, in Nestor.
`nestor/memory.py`: on a replacement "the old row keeps its text, verifier,
signature and reason, gains `superseded_by` pointing at its successor, and
falls out of the live unique index", and `memory_lineage` walks the chain.
`docs/decision-memory.md` there names the lineage as what a new proposal
should be shown. That is the shape of the fix open.md says belongs in
willow: "only if" reads the live seal, not the first.

## The people

**13. Safety.** Nothing, in any pile: no lines and veils, no way to stop a
scene. open.md puts this first for a family table, and it starts from
nothing.

**14. Undoing a slip.** Nothing for a yes pressed by mistake, asked two
ways. The nearest is 12's: a replacement that keeps what it replaced and
why. Nothing takes a seal back, and by willow's law nothing should erase
one.

**15. Sharing the GM's chair.** Not built. open.md's own later section
lists `grant` and `witness` as ideas. Nestor's
`docs/seal-staleness-and-quorum.md` works through more than one verifier on
a chain, and says plainly that no chain with more than one has been
measured.

## What the table sees

**16. The shared view.** Nothing for a map or a handout; no pile holds the
word. Willow's `print --large` is the one piece. `the-table`'s bureau
README notes what its own check cannot see, the page's rendering, which
any shared view will inherit.

**17. A board in a fight.** The facts are kept; nothing draws them.
`the-table/aetheris5e` rolls initiative, attacks, saves and damage and
remembers "every swing in a tamper-evident chain", so who is hurt and whose
turn it is are on the record already.

**18. Last night's fight on the opening screen.** The words exist. Commit
`8edcbc23`: "session.py's recap now tells the GM how each fight kept on the
last night ended". The opening screen of `box/play.py` does not show that
part of the recap. This is the smallest of the eighteen.

## In short

| | Gaps |
|---|---|
| Built somewhere, to be reached from the play path | 12 |
| Near: a piece exists and the join is missing | 2, 5 (things), 7, 9, 10, 17, 18 |
| A rule or a rule's text only | 1, 3, 6, 8 |
| Nothing found | 4, 11, 13, 14, 15, 16, and 5 for wounds |

Of open.md's three "first, for a family table": real dice (1) has the law's
leave and a door to copy, what carries over (5) is half there, and safety
(13) has nothing at all.
