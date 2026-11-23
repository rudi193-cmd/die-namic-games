# a player's seat

Run over a player's own box at the table: their character as the GM handed
it, their notes, and what the GM sent them. The box holds nothing of the
GM's binder, so nothing here can answer from it (open.md:579, the `kids`
leak, answered by construction). Each step has the want it answers above
it. `table_scene.py` runs it for every player's seat.

    python adapters/stdlib/stack/stack.py --box DIR --stack seat-stack.md --to RUN

## what came to me

Want 1: "What has the GM sent me?" Every package on my chain: who sent it,
when, and whether it held.
- share -- log --box {box}

## my notes

Want 2: "What did I write down?" Every passage of my own notes, in order.
- all-passages -- --box {box} notes

## does my record hold

Want 3: "Is my side of the table whole?" My record, read from its first row.
- box-health -- --box {box}
