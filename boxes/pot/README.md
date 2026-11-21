# The pot

An empty box to throw chunks into, and a stack that swirls whatever is in
it. Unlike the other boxes here, nothing is pinned: the pot is whatever you
have poured, kept in a folder of your own (outside this repository), and
each swirl lays a fresh box over it.

    bash boxes/pot/pour.sh POT NAME SOURCE [SUBDIR] [COMMIT]   # throw a chunk in
    bash boxes/pot/swirl.sh POT                                # run the pot's stack
    bash boxes/pot/swirl.sh POT --ask "who says yes?"          # plus a one-off want
    bash boxes/pot/swirl.sh POT --stack my-stack.md            # or a stack of your own

- A chunk is a git checkout (at a commit, whole or one folder), a folder, or
  one file. It lands in `POT/pile/NAME`, only what reads as words, with a
  `_chunk.md` that says where it came from. Pour the same NAME again to
  replace it. Delete the folder to take it out.
- `POT/words.txt` is the pot's own words list, copied from here the first
  time; edit it as the chunks need (a word can't map to itself).
- The page lands in `POT/swirl/page.md`, the box in `POT/box` (fresh each
  time, a scratch key in `POT`, nothing ever sealed).
- An empty pot says so and stops (exit 3).
- Step 1 (`box-health`) flags a fresh box ("no out row yet"): expected, not
  a fault in the pot.

[stack.md](stack.md) is seven general wants: health, disagreements between
chunks (willow's `contradictions` reads only lines with a date or an amount,
so it often finds none), what each chunk is, its licence, how it installs,
where its dice come from, how it keeps state. Add wants of your own; each is
a proposal. To compare chunks you already know, pour the same ones the other
boxes use (see [MEMORY.md](MEMORY.md)).

Tried on 2026-11-21 with dndwright (whole), ink & bone's `docs/` and
open.md: 134 files, 7 seconds, 7 of 8 steps clean.
