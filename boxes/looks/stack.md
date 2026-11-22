# how game pages look, asked what Die-Namic's redesign would want to know

A stack over the screens of four open AI game masters (NarrativeEngine-P,
ink & bone, dnd_ai_dm, TaleWeaver, at the same commits as ../gm-projects),
Die-Namic's own page sources, and book designs brought in for inspiration
(each picture with a note). Each want is written above its step: proposals,
one at a time, there to cut. Nothing here is sealed. `rebuild.sh` lays the
box and runs it.

## how a page is dressed

Want 1: "How does each one dress its pages: colours, fonts, themes?"
- all-passages -- --box {box} --top 10 "theme colour palette font"

## the GM's side of the table

Want 2: "Where does each put the GM's things: the screen, the binder's
pages pulled out for reference, the dice?" (the maintainer's own side,
ours/my-table.md: a three-panel screen, a three-ring binder behind it,
pages taken out to the screen or the table, the dice box centre)
- all-passages -- --box {box} --top 8 "sidebar handout reference dice"
- all-passages -- --box {box} --top 6 "only the gm sees the buttons"
- all-passages -- --box {box} --top 6 "gm screen roll hidden"
- all-passages -- --box {box} --top 6 "shared view table sees"

## from the GM's device to the table's

Want 3: "How does each send what the GM shows from their device to the
others'?" (the maintainer: "the GM would share from their device to others")
- all-passages -- --box {box} --top 6 "share sealed canon other box"
- all-passages -- --box {box} --top 8 "websocket players window sync"

## what only one seat sees

Want 4: "Blind deal happens all the time in card games: where do our games
already deal something only one seat sees?" (the maintainer's connection,
2026-11-22: the GM's screen roll, the cup and a dealt hand)
- all-passages -- --box {box} --top 6 "deal hand only one seat"
- all-passages -- --box {box} --top 6 "hand hidden other seats"
- all-passages -- --box {box} --top 6 "cups lifted dice hidden"
