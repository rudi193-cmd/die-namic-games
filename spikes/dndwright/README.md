# Spike: an outside rules engine under the record

A fight on a story's characters, run by [dndwright](https://github.com/sligara7/dndwright)
(MIT, `6f0fb9e`), on dice somebody else supplies, with every blow a row and a
replay that finds an edit. Built 2026-11-21 to answer `open.md`, "Round 5". It
is a spike: **nothing in `box/` imports it**, and it is outside `tests/` so the
suite doesn't need dndwright; it is run by name.

    pip install git+https://github.com/sligara7/dndwright.git@6f0fb9e   # needs pydantic>=2.5, pyyaml>=6.0
    python3 -m pytest spikes/dndwright -q                                # 7 tests

## What it shows (each held by a test)

- **Dice come from outside.** dndwright rolls through a `random.Random` it is
  given; `SaidRandom` hands it faces from a list (`Faces`), in the order it
  asks. Out of faces it raises `OutOfFaces`: it has no generator of its own to
  guess with. A face not on the die (a 21 on a d20) is refused.
- **A fight on the story's characters.** `Fighter` is a name, a side, hit
  points, armor class, an initiative modifier, an attack bonus and a damage
  expression: plain numbers, as aetheris5e's stat blocks are.
- **Every blow is a row** (`init`, `blow`, `down`, `end`), and the faces of a
  fight are recoverable from its rows (`faces_of`).
- **`check` replays the rows' own faces** and finds an edited hit point, or a
  die changed after the fact.
- A natural 20 hits and doubles the damage dice (dndwright's rule).

## What it does not do

- **No tower yet.** The faces are typed or listed. The next step is to fill
  `Faces` from willow's `dice-tower` (one drop per roll, `1d20` then the
  damage dice, each out before the next is asked), so nobody reads a face
  first. Not built.
- **Not on the record.** The rows are plain dicts, not kernel rows; no seal.
- **Fixed choices.** A fighter hits the first one standing on the other side;
  in play that is a person's call. No advantage, no conditions, no death saves
  (a fighter drops at 0 hit points, as in aetheris5e), no reactions, no map.
- **Our sheets** (a bonus on each of a story's stats) are not mapped; a
  `Fighter`'s numbers are given by hand. dndwright's sheet graph is not used.
- **Edition:** attack and damage rules here are plain d20-versus-AC, the same
  in 5.1 and 5.2.1; dndwright's 2024 specifics (Weapon Mastery and the rest)
  are untouched.
- **The wider suite:** `python3 -m pytest tests` shows 23 failures in the
  fight tests with or without this folder; `box/fight.py` needs
  `ONESCRIPT_HOME` (willow-bot's one-script), which this session doesn't have.
