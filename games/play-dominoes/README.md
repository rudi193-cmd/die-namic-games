# play-dominoes

All Fives dominoes on the record, shuffled by the record's tip: the first double a spinner, every multiple of five scored, to 250.

A willow add-on, and it stays in willow: Die-Namic plays it there, pinned by its files' hashes ([../../willow.pin.json](../../willow.pin.json)). Its card, with everything it does and refuses: [play-dominoes in willow](https://github.com/willow-memory/Willow/tree/406d56bb9689a85654b034843a1c5c47bbcf4277/adapters/stdlib/play-dominoes).

## Playing it

```
python games/play.py play-dominoes --table DIR new
python games/play.py play-dominoes --table DIR show --seat north
python games/play.py play-dominoes --table DIR play 6|3 up
python games/play.py play-dominoes --table DIR draw
python games/play.py play-dominoes --table DIR pass
python games/play.py play-dominoes --table DIR auto
python games/play.py play-dominoes --table DIR check
```

On a box laid by `box/open_table.py`, `--table DIR` plays on its record.

Two seats, north and south, nine tiles each. The first double played is the spinner, with four arms, left, right, up and down, played in any order; a tile's arm is said when it fits more than one. A seat that can play must; one that can't draws until it can. Every multiple of five on the open ends scores; the game is 250. `auto` plays the seat to move by a fixed rule, and `show --seat` shows one seat's tiles. Each deal, play, draw and pass is a row on the record, through the kernel.

## Where it came from

All Fives, from a game of dominoes played at Die-Namic's table on 2026-11-26, the table's player choosing its rules: only the first double spins, its arms in any order, a seat draws until it can play, and the 6|6 leads the first hand.
