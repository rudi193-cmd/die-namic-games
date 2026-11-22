# willow and die-namic-games, asked about a swappable fight engine

A stack over our two repositories (willow at its pin, die-namic-games at
the commit that added the SRD 5.1 fight-engines note to open.md). The
question behind it: could OpenCombatEngine, srd_5e or jurnalis' engine, or
a Python port of their rules, stand under the kernel's record and seal?
Each want is written above its step: proposals, there to cut. Nothing here
is sealed. `rebuild.sh` lays the box and runs it.

## what already covers a fight

Want 1: "What does the house already hold about a fight?"
- all-passages -- --box {box} --top 8 "fight initiative attack armor class hit points"

Want 2: "Where do the dice come from, and can anything steer them?"
- all-passages -- --box {box} --top 8 "dice tower roll steer"

Want 3: "How does a blow get onto the record, and what does the seal cover?"
- all-passages -- --box {box} --top 6 "blow record seal fight"

## what an outside engine would have to be

Want 4: "What must an add-on that needs something installed carry?"
- all-passages -- --box {box} --top 6 "deps requirements pinned licence network"

Want 5: "What does a card promise, and what holds an add-on to it?"
- all-passages -- --box {box} --top 6 "card promises writes network guard"

Want 6: "May the kernel ever name an add-on?"
- all-passages -- --box {box} --top 4 "kernel never names an add-on"

## where this came up

Want 7: "When did aetheris5e first come into the picture?"
- first-mention -- --box {box} "aetheris5e"

Want 8: "What is still open about fights in open.md?"
- all-passages -- --box {box} --top 6 "fight open characters party"
