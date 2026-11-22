# The GM's page, first mock (2026-11-22)

An ASCII mock of the GM's side, drawn from my-table.md: the maintainer's
three-panel screen, the binder behind it, the dice box centre, pages sent
to the table with `share`. Real from the repository: The Lantern Fair's
first scene, Tamsin's and Oro's stats (box/worlds/lantern-fair.json), the
clockwork hound's stat line (box/README.md:69). Placeholders: the river
wisp, the cellar door battle, Vell's lamp as loot, Oro's scraped hand.

## The screen

```
┌─ Die·Namic ─ The Lantern Fair ─ night 2 ──────────────────────────────────────┐
│ ┌─ LEFT: quick ref ─────┐ ┌─ CENTRE ────────────────────────┐ ┌─ RIGHT ────────┐│
│ │ ⌕ ask anything… ____  │ │ BINDER  scene 1 of 2 · stalls   │ │ PLAYERS        ││
│ │                       │ │ ─────────────────────────────── │ │                ││
│ │ BESTIARY              │ │ Dusk at the stalls              │ │ Tamsin         ││
│ │  ▸ clockwork hound    │ │ The first lanterns go up along  │ │ lamp-lighter   ││
│ │  ▸ river wisp         │ │ the river. A stall is missing   │ │ Grit+2 Wit+1   ││
│ │                       │ │ its light.                      │ │ Heart+1        ││
│ │ PLANNED BATTLES       │ │                                 │ │ carries: hook, ││
│ │  ▸ the cellar door    │ │ ▶ Tamsin climbs to the dark     │ │  matches       ││
│ │    2× hound           │ │   stall's hook.  [Grit +2]      │ │ ────────────── ││
│ │                       │ │                                 │ │ Oro            ││
│ │ UPCOMING LOOT         │ │         ╔═══════════╗           │ │ juggler        ││
│ │  ▸ Vell's lamp        │ │         ║  ⚂   ⚄    ║ DICE BOX  │ │ Grit+1 Wit+2   ││
│ │    (scene 2)          │ │         ║  2d6 + 2  ║           │ │ Heart+1        ││
│ │                       │ │         ╚═══════════╝           │ │ hurt: scraped  ││
│ │                       │ │      [ Roll ]  [ Roll hidden ]  │ │  hand          ││
│ │                       │ │                                 │ │                ││
│ │                       │ │ ✋ Your call, GM:                │ │ [ sheets to    ││
│ │                       │ │ Old Vell's lamp is in the nest. │ │   the table ]  ││
│ │                       │ │ [ Yes, it's true ] [ No ]       │ │                ││
│ └───────────────────────┘ └─────────────────────────────────┘ └────────────────┘│
│  ON THE TABLE: scene card · Tamsin's sheet          [ ⇪ share a page ]        │
└───────────────────────────────────────────────────────────────────────────────┘
```

## A lookup, called to the centre

The lookup lives in the left panel and comes into the centre when called
(the maintainer's decision); the story steps aside.

```
┌─ LEFT: quick ref ─────┐ ┌─ CENTRE ────────────────────────┐ ┌─ RIGHT ────────┐
│ ⌕ hound stats ↵       │ │ ◂ back to scene 1               │ │ PLAYERS        │
│                       │ │ ─────────────────────────────── │ │ Tamsin …       │
│ where to look:        │ │ CLOCKWORK HOUND                 │ │ Oro …          │
│  ▸ monsters/          │ │ Grit 3, Wit 1, Heart 0,         │ │                │
│    clockwork-hound    │ │ Weird 2. Hits 6.                │ │                │
│  ▸ house rules §     │ │                                 │ │                │
│    Draws              │ │   monsters/clockwork-hound.md:5 │ │                │
│                       │ │                                 │ │                │
│                       │ │ [ to the screen ] [ to table ⇪ ]│ │                │
└───────────────────────┘ └─────────────────────────────────┘ └────────────────┘
```

## A fight in the centre

The centre becomes the board; the dice box stays in the middle.

```
┌─ CENTRE: the cellar door ─ round 2 ─────────┐
│ TURN ▸ Tamsin   Oro   hound A   hound B     │
│ Tamsin   ██████░░  6/8                      │
│ Oro      ████████  8/8                      │
│ hound A  ██░░░░░░  2/6   staggered          │
│ hound B  ░░░░░░░░  down                     │
│              ╔═══════════╗                  │
│              ║  ⚀   ⚅    ║  2d6 + 2         │
│              ╚═══════════╝                  │
└─────────────────────────────────────────────┘
```

## A kid's creature, put in

Typing is the main way in; the picture is just a picture (the
maintainer's decisions).

```
kid types:  "Biscuit — my dragon — Grit 3, Wit 1"   ← the creature
kid adds:   a photo of the drawing                   ← just a picture
(optional, on the GM's machine: crop it in photocraft, trace it in drawcraft)
your call, GM: [ Yes, it's true ] → bestiary card with Biscuit's picture
```

## What the mock shows that isn't built

- **Upcoming loot:** nothing keeps loot not yet found (carry.py keeps what
  is carried).
- **A live board:** box/board.py draws a fight from its rows, today at its end.
- **Roll hidden:** willow's `dice-tower` is built; the play path doesn't
  reach it yet.
- **The picture:** the pile reads words only; the page keeps and shows it.

## Open

- **The tidy-up.** Does a kid's drawing go in as they made it, or through
  the image suite first (crop and straighten, background removed, the
  sketch traced)? Left open by the maintainer, 2026-11-22.
