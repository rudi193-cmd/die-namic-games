# Spike: an outside rules engine under the record

A fight on a story's characters, run by [dndwright](https://github.com/sligara7/dndwright)
(MIT, `6f0fb9e`), on dice somebody else supplies, with every blow a row and a
replay that finds an edit. Built 2026-11-21 to answer `open.md`, "Round 5". It
is a spike: **nothing in `box/` imports it**, and it is outside `tests/` so the
suite doesn't need dndwright; it is run by name.

    pip install git+https://github.com/sligara7/dndwright.git@6f0fb9e   # needs pydantic>=2.5, pyyaml>=6.0
    python3 -m pytest spikes/dndwright -q                                # 23 tests (7 listed faces, 5 tower, 11 story fighters and the record)

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
- **The fight is on the record, unsealed.** `record_fight.py` writes an
  `xfight-open` row (the engine and its commit, and the fighters, whole), the
  tower's own drop and out rows as the engine asks for dice, then one
  `xfight-row` per row of the fight. Its kinds are not `fight-open`,
  `fight-blow` or `fight-end`, so box/fight.py never reads them and this never
  writes theirs. `check_record` reads only the record: the chain holds, every
  tower die holds to its drop with none inside, the faces the tower brought
  out are the faces the rows say, and the fight played again on those faces
  comes out as written. Nothing is sealed, and no one decides what the fight
  means for the story: that is the GM's.
- **Story characters and stat blocks as Fighters** (`story_fighters.py`).
  A character's hit points, armor class, initiative and attack are made up
  from the bonuses on the story's own stats (by position: body, mind, heart);
  the defaults are the spike's, written at the top of the file, and a
  character's own `"fight": {...}` in the world file overrides them. An
  aetheris5e stat block becomes a Fighter by its numbers and its first attack,
  with multiattack as blows a turn.
- **Fixed choices.** A fighter hits the first one standing on the other side;
  in play that is a person's call. No advantage, no conditions, no death saves
  (a fighter drops at 0 hit points, as in aetheris5e), no reactions, no map.
- **dndwright's sheet graph is not used**, and the defaults that turn a bonus
  into hit points are made up here, not a rule from any SRD. A stat block's
  specials, saves and resistances are not carried.
- **Edition:** attack and damage rules here are plain d20-versus-AC, the same
  in 5.1 and 5.2.1; dndwright's 2024 specifics (Weapon Mastery and the rest)
  are untouched.
- **The wider suite:** `python3 -m pytest tests` shows 23 failures in the
  fight tests with or without this folder; `box/fight.py` needs
  `ONESCRIPT_HOME` (willow-bot's one-script), which this session doesn't have.
