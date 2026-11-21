# What the survey of the eight says, and what it connects to

> **Corrected 2026-11-21:** "what none of them has" below is true of these eight
> only. Layforge, a ninth, has safety tools, a human veto and knowledge scoping
> (see open.md, "Round 2"). jurnalis-engine's 5.1 label is also wrong: it is
> mostly 2024 rules.

Read from `survey.md` (this folder) on 2026-11-21: eight chunks, 27 questions,
top 8 each, 133 of 216 cells hit. **The matrix over-counts.** A hit means a
passage held the rule's words, and some are accidents (A1's "enforce" hit a
ruff config in dndwright and a character's cooking in narrativeengine-p; A3's
"confirm" hit a Go prompt and a Rust grapple check). Only the passages read
below were checked by eye. A miss is "not in the top 8", not "absent".

## The shared shape: code decides, the model tells

- **dnd_ai_dm**: "The game engine is deterministic and owns all rules. A
  pluggable narrator writes the prose" (`AGENTS.md:5`); all randomness goes
  through an injected `random.Random` or `Dice` (`AGENTS.md:37`).
- **narrativeengine-p**: the model is handed `DICE OUTCOMES` or `RESOLVED
  ROLL` tags: "The engine already rolled; you narrate. Never reroll, change
  tier" (`Example_Setup/Ruleset/4.4_Fable5_PVP_mode.md:193`).
- **taleweaver**: a second pass narrates rule violations the code found
  (`backend/api/routes/adventures/turn_pass_flow.py:55`), and its release
  notes claim "zero dropped or hallucinated mechanics" (`v0.7.0-beta.md:130`).
- **Connection:** four independent projects land on Die-Namic's rule underneath,
  the code owns the rule and the model only proposes or tells. None goes the
  last step: nobody can check afterwards that the roll the model was told is
  the roll the code made. That is the record and the seal.

## Dice: the seam we need exists in four, the tower in none

- Injectable: dnd_ai_dm (injected `Dice`), dndwright (`DiceEngine(rng=...)`,
  "inject any `random.Random`", `CHANGELOG.md:537`), OpenCombatEngine
  (`IDiceRoller`, settable `Seed`). jurnalis-engine is seeded from a `u64`
  but no way to hand it faces was found.
- Reproducible: dndwright says "ideal for tests, replay, and audit trails";
  jurnalis: "replay any session exactly by replaying the seed and input
  sequence" (`README.md:19`); dnd_ai_dm saves don't keep RNG state, so replay
  needs the seed (`docs/guides/save-and-load.md:44`).
- **Typed faces from physical dice (B3): no hit in any.** Every rival rolls
  its own. ink & bone's README says systems can be rolled manually with
  buttons (`README.md:849`, found under A1): a lead, not checked.
- **Connection:** an engine whose roller can be replaced (dndwright, dnd_ai_dm,
  OpenCombatEngine) could be fed the tower's faces, or faces typed from a
  table's own dice, and every blow still land on the record. A seed-only
  engine (jurnalis) can't, unless its seed *is* the tower's output, which gives
  up the "no one reads it first" property. Pick by this.

## Fights: who has what

- dndwright, jurnalis, OpenCombatEngine and srd_5e answer death saves,
  conditions and reactions; dnd_ai_dm and taleweaver don't in the top 8.
  (dndwright and jurnalis are the two with a check-by-code shape;
  OpenCombatEngine adds an event stream, ADR 005.)
- State round-trips as JSON in all but srd_5e (D1). An event log or history
  (D2): dnd_ai_dm, inkandbone, narrativeengine-p, OpenCombatEngine, taleweaver;
  not dndwright, jurnalis, srd_5e: for those, the *record* would be the log.
- **Connection:** a pure engine (dndwright, jurnalis) is a function from state and
  input to new state, which is what the record wants: each blow a row, the
  engine re-run by `check` to confirm. An event-emitting one (OpenCombatEngine)
  would need its events turned into rows.

## What none of them has

- **A person's yes** (A3): nothing like a seal. Closest is taleweaver asking
  the player to confirm a blueprint in a review dialog (`core/prompts.py:513`),
  which is a UI step, not a record.
- **Lines and veils** (E1): none. Die-Namic's `safety.py` has no counterpart
  here.
- **Hiding what a character could not know:** narrativeengine-p's
  `mobile/docs/WITNESS_INTEGRITY.md:25`: "The LLM cannot hallucinate or act on
  verbatim scene details that the current scene's NPCs could not possibly know
  because that text is completely omitted from the context." This is the same
  problem as the `kids` leak in open.md (a child's question answered from
  `gm-only/`), solved by leaving text out of the context. Read it next.
- **Undo** (D5): hits are accidents except taleweaver's inventory change-set
  (`player_inventory.py:43`) and narrativeengine-p's cancel-without-revert;
  nothing like "kept, no longer standing".

## The law

- Licence files: MIT for dnd_ai_dm, dndwright, inkandbone, narrativeengine-p,
  taleweaver; Apache-2.0 for srd_5e; OpenCombatEngine has MIT plus an
  `LICENSE-OGL` and a `LEGAL.md`; **jurnalis-engine has none** (its README says
  all rights reserved). taleweaver adds CC-BY-NC for assets.
- SRD: dndwright cites SRD 5.2.1 CC-BY-4.0; jurnalis implements 5.1 ("one long
  rest per 24 hours", `src/state/mod.rs:49`); OpenCombatEngine and srd_5e hit
  F1. Dying engines to rank by version: not yet done.

## Next questions the survey can't answer

1. Does any engine's roller take faces as input, in code? (read dndwright's
   `dice/engine.py` and dnd_ai_dm's `Dice`).
2. Is dndwright's combat a pure function of state? (`combat/initiative.py`).
3. Read WITNESS_INTEGRITY.md whole.
4. Ask the pot for hashes and commit-reveal: not in the 27 questions.
