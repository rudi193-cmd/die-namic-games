# The story's own fights (willow's play-fight, through the pin)

In a story that names its foes, `f` at a roll offers a fight of the story's
own: its seated characters against one of aetheris5e's foes. The fight is
willow's play-fight add-on (`adapters/deps/play-fight` in willow), pinned in
[willow.pin.json](../willow.pin.json) like every other piece of willow the box
plays with: [dndwright](https://github.com/sligara7/dndwright)'s rules (MIT),
on dice dropped in willow's dice-tower, every blow a row on the record. It
sits beside the box's other fights (aetheris5e's, `fight.py`) and never
touches them.

Die-Namic keeps one part of it, the part that is the table's to say: where
a fighter's numbers come from (`dw_story.py`, below).

## Turn it on

    pip install -r "$WILLOW_ROOT/adapters/deps/play-fight/requirements.txt"   # dndwright, Python 3.10+

and a story names its foes (keys of aetheris5e's stat blocks):

    "foes": ["scorched_belt_raider", "tide_touched_scout"]

Without dndwright, or in a story with no `"foes"` (or one with no seated
character, or aetheris5e's own), `f` is as it was. A foe key that isn't a stat
block is left out, not guessed. In a story that turns on a fight (`offers`
names `fight`), the end goes to the GM as a call, like any fight.

## What happens

- **The fighters** are written to `tower/fighters.json` at the table, and
  play-fight is run on them, with the night's record as its box and
  `tower/fights` for its dice. Its lines print as the blows land.
- **Rows.** play-fight's own: `fight-begin` (the fighters whole, and the
  dndwright that ran it), the tower's `tower-drop` and `tower-out`, then one
  `fight-row` per thing that happened, each naming the tower dice behind it.
  `fight.py`'s kinds (`fight-open`, `fight-blow`, `fight-end`) are not written
  and these are not read by it.
- **Check.** `open_table.py check` runs play-fight's `check`, which reads the
  record alone and plays each fight again on the tower's faces (its card says
  what it holds each row to).
- **Recap.** `session.fights` lists them with the others ("the story's own
  fight: the party won in 2 rounds; standing: ..."), for the GM's eyes.
- **Nothing sealed.** The machine rolls and remembers; what a fight means for
  the story is the GM's to say.

## The characters

`dw_story.py` makes a fighter from a story character by defaults of its own
(**made up, a design decision, not an SRD rule**): by the story's stats in
order (body, mind, heart), hit points 8 + 2 per point of bonus, armor class 11
+ the best bonus, initiative the second stat, attack 2 + the first stat, damage
1d6 plus it; one blow a turn. A character's own `"fight": {"hp", "ac",
"init_mod", "attack_bonus", "damage", "attacks"}` wins; an unknown key is
refused. A stat block becomes a fighter by its numbers and first attack, with
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

Code: [dw_story.py](dw_story.py), and `story_foes` and `story_fight` in
[play.py](play.py); tests [test_dw_story.py](../tests/test_dw_story.py) and
[test_dw_play.py](../tests/test_dw_play.py). The fight's own tests are
play-fight's, in willow. The reasoning in [../open.md](../open.md),
"Rounds 4 to 9" and "Round 10".
