# how game pages look, asked what Die-Namic's redesign would want to know

A stack over the screens of four open AI game masters (NarrativeEngine-P,
ink & bone, dnd_ai_dm, TaleWeaver, at the same commits as ../gm-projects),
Die-Namic's own page sources, and GM screen art brought in for inspiration
(each picture with a note). Each want is written above its step: proposals,
one at a time, there to cut. Nothing here is sealed. `rebuild.sh` lays the
box and runs it.

Each want's questions are in `questions/wantN.tsv` (a name, a tab, the
question), asked of the box's index through willow's batch-ask: the kernel's
own answers, in about a second. A question of your own, any time:
`bash boxes/looks/ask.sh SCRATCH "your words"`.

## how a page is dressed

Want 1: "How does each one dress its pages: colours, fonts, themes?"
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want1.tsv

## the GM's side of the table

Want 2: "Where does each put the GM's things: the screen, the binder's
pages pulled out for reference, the dice?" (the maintainer's own side,
ours/my-table.md: a three-panel screen, a three-ring binder behind it,
pages taken out to the screen or the table, the dice box centre)
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want2.tsv

## from the GM's device to the table's

Want 3: "How does each send what the GM shows from their device to the
others'?" (the maintainer: "the GM would share from their device to others")
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want3.tsv

## what only one seat sees

Want 4: "Blind deal happens all the time in card games: where do our games
already deal something only one seat sees?" (the maintainer's connection,
2026-11-22: the GM's screen roll, the cup and a dealt hand)
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want4.tsv

## the screen's three panels

Want 5: "What does the box already hold for each of my screen's three
panels?" (the maintainer's screen: left, quick reference: the bestiary,
upcoming loot, planned battles; centre, the binder's planned story and
active combat; right, the players)
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want5.tsv

## a quick lookup

Want 6: "What do we already have for a quick lookup of everything that
might turn up: the rules, the books, asked on demand?" (the maintainer,
2026-11-22)
- batch-ask -- scan --index {box}/../index --words {box}/../words.txt --top 8 --questions {box}/../questions/want6.tsv
