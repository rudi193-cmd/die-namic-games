# The story's own fights (dndwright, on the tower, on the record)

In a story that names its foes, `f` at a roll offers a fight of the story's
own: its seated characters against one of aetheris5e's foes, run by
[dndwright](https://github.com/sligara7/dndwright) (MIT, `6f0fb9e`) on dice
dropped in willow's dice-tower, every blow a row on the record. It sits beside
the box's other fights (aetheris5e's, `fight.py`) and never touches them.

## Turn it on

    pip install git+https://github.com/sligara7/dndwright.git@6f0fb9e   # pydantic>=2.5, pyyaml>=6.0

and a story names its foes (keys of aetheris5e's stat blocks):

    "foes": ["scorched_belt_raider", "tide_touched_scout"]

Without dndwright, or in a story with no `"foes"` (or one with no seated
character, or aetheris5e's own), `f` is as it was. A foe key that isn't a stat
block is left out, not guessed. In a story that turns on a fight (`offers`
names `fight`), the end goes to the GM as a call, like any fight.

## What happens

- **Dice.** dndwright rolls through a `random.Random` it is handed
  (`dw_fight.SaidRandom`); each die it asks for is dropped in the tower (only
  its SHA-256 on the record, with what it is for: "Tamsin attacks Raider") and
  brought out at once (`dw_tower.TowerFaces`). Out of faces it raises; it has no
  generator of its own. A face off the die is refused.
- **Rows.** `xfight-open` (the engine and its commit, the fighters whole), the
  tower's own `tower-drop` and `tower-out` rows, then one `xfight-row` per row
  of the fight (`init`, `blow`, `down`, `end`). `fight.py`'s kinds (`fight-open`,
  `fight-blow`, `fight-end`) are not written and these are not read by it.
- **Check.** `open_table.py check` reads them from the record alone
  (`dw_record.check_record`): the chain holds, every tower die holds to its
  drop with none inside, the faces the tower brought out are the faces the
  rows say, and the fight played again on those faces comes out as written. An
  edit in the file breaks the chain; rows written honestly to the chain with a
  blow changed, and no tower dice behind them, are refused. If the rows are
  there and dndwright isn't installed, `check` fails and says so.
- **Recap.** `session.fights` lists them with the others ("the story's own
  fight: the party won in 6 rounds; standing: ..."), for the GM's eyes.
- **Nothing sealed.** The machine rolls and remembers; what a fight means for
  the story is the GM's to say.

## The characters

`dw_story.py` makes a Fighter from a story character by defaults of its own
(**made up, a design decision, not an SRD rule**): by the story's stats in
order (body, mind, heart), hit points 8 + 2 per point of bonus, armor class 11
+ the best bonus, initiative the second stat, attack 2 + the first stat, damage
1d6 plus it; one blow a turn. A character's own `"fight": {"hp", "ac",
"init_mod", "attack_bonus", "damage", "attacks"}` wins; an unknown key is
refused. A stat block becomes a Fighter by its numbers and first attack, with
multiattack as blows a turn.

## Not done

- A person chooses the target (a fighter hits the first one standing).
- Conditions, death saves (a fighter drops at 0), reactions, advantage, a map.
  Hurt characters (box/carry.py) start at full hit points.
- The drop and the out are an instant apart: nobody chose the face, but "nobody
  read it first" is only as good as the keeping of the die files (the tower's
  own README: that is the game master's screen, not a seal).
- A stat block's specials, saves and resistances.
- The `board` (box/board.py) draws `fight.py`'s fights only.
- The 23 tests that need `ONESCRIPT_HOME` (willow-bot's one-script) for
  aetheris5e's dice were not run green in the session that wrote this; the rest
  (30 for this) pass.

Code: [dw_fight.py](dw_fight.py), [dw_tower.py](dw_tower.py),
[dw_story.py](dw_story.py), [dw_record.py](dw_record.py); tests
[test_dw_*.py](../tests/); the reasoning in [../open.md](../open.md),
"Rounds 4 to 9".
