# Spike: an outside rules engine under the record

A fight on a story's characters, run by [dndwright](https://github.com/sligara7/dndwright)
(MIT, `6f0fb9e`), on dice somebody else supplies, with every blow a row and a
replay that finds an edit. Built 2026-11-21 to answer `open.md`, "Round 5". It
is a spike: **nothing in `box/` imports it**, and it is outside `tests/` so the
suite doesn't need dndwright; it is run by name.

    pip install git+https://github.com/sligara7/dndwright.git@6f0fb9e   # needs pydantic>=2.5, pyyaml>=6.0
    python3 -m pytest spikes/dndwright -q                                # 12 tests (7 on listed faces, 5 on the tower)

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
- **On the tower** (`test_tower_faces.py`): every face is a die dropped as a
  hash and then out; the fight's rows match the tower's outs; a face changed in
  the rows is found; a die left inside is named.

## What it does not do

- **The tower is wired, with a short window.** `tower_faces.py` fills the
  faces from willow's `dice-tower`: each die the engine asks for is dropped
  (only its SHA-256 on the record, with what it is for: "Tamsin attacks
  Goblin") and brought out at once. The tower's guarantee holds (nobody
  chose the face, and `tower_match` holds the fight's rows to the tower's
  `tower-out` rows, in order, with none left inside), but the drop and the
  out are an instant apart, not a moment posed to the table; and whoever holds
  the die files can look first (the tower's own README: that is the game
  master's screen, not a seal). A play path would drop a round's d20s when
  the round is posed, and the damage dice when a hit is known.
- **The fight is not on the record as rows.** The tower's drops and outs are
  kernel rows; the fight's own rows (`init`, `blow`, `down`, `end`) are plain
  dicts, not kernel rows, and nothing is sealed.
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
