# aetheris5e — a D&D 5e lens over the Aetheris world

A companion harness that runs [`the-table`](../)'s `worlds/aetheris.json`
under **real 5e dice** (d20 + modifier vs DC, advantage/disadvantage, degrees of
success, the setting's aether-wild zone rule) instead of the-table's native 2d6
`StorySession` engine.

**The world is shared; only the resolution math differs.** Scenes, beats, the
cast, and — above all — Maunder's personhood *decision beat* all come from the
one authored world file. This directory never touches the-table's own engine,
registry, or tests; it imports only the-table's host shim (`the_table/host.py`),
which writes every roll as a `verdict` row in the one-script record, the one
chain (willows-grove `docs/design/one-script/flatten-2026-10-19.md` F-6). The
one-script must be beside the-table (`../willow-bot/one-script`, or
`ONESCRIPT_HOME`); with none, `gm5e` and `sealed_run` say why
and exit 2.

The one covenant is identical to the-table's and to `ai-game-master`'s:

> **The machine proposes, rolls, and remembers. It never seals. A person at
> the head of the table seals canon, with their own key.**

## What's here

| File | What it does |
|------|--------------|
| `dice5e.py` | The dice seam. Dice-notation **authority** is the MIT-licensed [`dice`](https://pypi.org/project/dice/) library (borntyping/python-dice) — the reuse-vs-build wall from `ai-game-master/docs/DECISION.md`. Two speedups sit on top without owning the grammar: a **cache** (each expression compiles once) and a **fast path** (simple `NdM±K` / advantage forms compute directly with the injected RNG, ~3000× faster than re-parsing pyparsing every call). The library still validates every expression and remains the fallback; a test asserts the fast path never diverges from it. Injects the engine's own `random.Random`, so seeded fights stay reproducible and the global `random` is never touched. |
| `monte_carlo.py` | Runs the whole adventure at volume (default 500 seeded rounds) for three level-3 pregens side by side, and reports where the average rolls out — per-beat success rates, successes-per-run distribution, the "night held together" verdict, and the one beat no policy can resolve. |
| `gm5e.py` | A live 5e roller CLI (checks, saves, attacks, damage) that appends every roll to the one-script record the moment it happens. `propose` puts a fact before the human as a proposal; `seal` refuses (a seal is the human's, made with their key through the one-script). |
| `sealed_run.py` | One live playthrough to Maunder's question, then the decision: the machine's seal attempt **refused**, the beat **proposed** for the human's seal (`onescript seal proposal:<hash> --proof ...`), the chain **verified**, and a tampered copy **rejected**. Until flatten F3 the seal itself is the one-script's, not this script's. |
| `combat.py`, `statblocks.py` | Moved into willow's `play-fight5e` add-on (the engine, the six stat blocks, the pregens and the four encounters), with their tests. |

## Run it

```sh
pip install -r requirements.txt     # the MIT `dice` library (the only dep)

python3 monte_carlo.py 500          # the skill-check baseline
python3 gm5e.py open "Aetheris"     # provision a live campaign box
python3 gm5e.py check Aether 5 13 --adv "attune to the broadcast"
python3 sealed_run.py                     # a full playthrough + proposal + tamper test

python3 play_fight5e.py list              # in willow's adapters/deps/play-fight5e: the four encounters
python3 play_fight5e.py sim enforcers --runs 500   # where a fight rolls out, at volume
```

### Combat, on the record

The combat engine, the six stat blocks, the three pregens and the four
encounters moved into willow as the `play-fight5e` add-on (2026-11-23), where
Die-Namic's `box/fight.py` plays them through its pin, on dice dropped in
willow's dice-tower. Its rules are the ones written here before; only where
the dice come from changed. `dice5e.py` stays here for `gm5e`,
`monte_carlo` and `sealed_run`.

## Data stays home

Record boxes hold played rolls, proposals, and their keys files — that is **data**,
not blueprint. Every box is written under `_boxes/` and is `.gitignore`d, the
same wall `ai-game-master` draws between the repo (how to build the vault)
and the box (the campaign that stays home). Nothing in this directory commits a
played campaign.

## Why two engines over one world

the-table's `StorySession` is a PbtA-style 2d6 spine; this is a d20 5e spine.
Pointing both at the same `worlds/aetheris.json` is the point: the *world* — its
scenes, its cast, and the human-only seal that decides what a mind **is** —
outlives whichever dice you bring to the table.
