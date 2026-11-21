# family night

The page for a family's own table, the one box/play.py keeps: before the
night, what was promised and what waits; after it, that every roll and
every story still holds, a copy kept, and where the record ends written
down. Every step is one the box's other pages already run. The wants are
written in a family GM's words, as proposals: cut any, add your own (a want
in your words, then the add-on that answers it), and it is your stack.

    python box/open_table.py family --table ~/.die-namic/table

**What never happens at our table.** Write it once, before the first night,
in your own words, as `pile/our-lines.md` in the table: a heading "Lines"
over what never happens in the story (spiders, say), and a heading "Veils"
over what can happen, off-screen (kissing), each on its own line after a
dash. play.py reads it at every part, and anyone can press x at a roll to
set a part aside, no reason asked.

Each run is kept in a folder of its own, DIR/family/NNN, so the steps that
write a file write it there. It reads, and keeps a copy; it seals nothing.

## before the night

Want 1: "What did we promise for next time?" Every line of the notes that
says next time, ranked: the friend someone was told could come, the thread
left hanging.
- all-passages -- --box {box} "next time"

Want 2: "Is anything waiting on me?" A call left unanswered, a night not
ended, a house rule still waiting: one page of what needs the GM.
- digest -- --box {box}

## after the night

Want 3: "Does every story still hold?" Every story on the record played
again from its first row, the way it was played.
- game-master -- --box {box} check

Want 4: "Does every roll still hold?" Every throw thrown again from its seed.
- play-dice -- --box {box} check

Want 5: "Is our box all right?" Files it can't read, readers out of date,
when its record was last checked.
- box-health -- --box {box}

Want 6: "Keep a copy, in case." The record and the notes, backed up and
checked, in this run's folder.
- backup -- --box {box} --to {run}

Want 7: "Write down where the record ends tonight." A pin of its last row,
so a copy kept anywhere can be checked against it.
- tip-pin -- pin --box {box} --to {run}/pin.json
