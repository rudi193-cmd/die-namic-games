# survey of 8 chunks, 27 questions, top 8

A hit: a served passage holds the question's rule (survey-questions.tsv). Evidence to read, not proof. A miss: not in the top 8, which is not the same as absent. Nothing here is sealed.

## facts (counted by code)

| chunk | licence file | most files | build files | test files |
|---|---|---|---|---|
| dnd_ai_dm | LICENSE: MIT License Copyright (c) 2024 MOHAMMADSADEGH SIRJANI | .py 48, .md 11, .txt 2, LICENSE 1, .toml 1 | pyproject.toml, requirements.txt | 8 |
| dndwright | LICENSE: MIT License Copyright (c) 2026 Anthony Sligar | .py 83, .json 10, .md 5, LICENSE 1, .toml 1 | pyproject.toml | 40 |
| inkandbone | LICENSE: MIT License Copyright (c) 2026 DTG404 | .go 186, .ts 42, .md 39, .json 6, LICENSE 1 | package.json | 103 |
| jurnalis-engine | no LICENSE file in the pile | .rs 38, .md 2, .toml 1 | Cargo.toml | 0 |
| narrativeengine-p | LICENSE: MIT License Copyright (c) 2026 Sagesheep | .ts 1270, .md 176, .json 73, .txt 4, LICENSE 1 | package.json | 482 |
| opencombatengine | LICENSE: Copyright (c) 2025 James Duane Plotts Permission is hereby granted, fr; LICENSE-OGL: # OPEN GAME LICENSE Version 1.0a The official OGL 1.0a PDF is availabl | .cs 343, .md 97, .txt 6, LICENSE-OGL 1, LICENSE 1 | - | 114 |
| srd_5e | LICENSE: Apache License Version 2.0, January 2004 | .exs 48, .ex 48, .md 3, LICENSE 1 | mix.exs | 37 |
| taleweaver | LICENSE: MIT License Copyright (c) 2026 Jean Schmitz; LICENSE-CC-BY-NC-4.0: Creative Commons Attribution-NonCommercial 4.0 International Creative | .py 880, .ts 188, .md 51, .json 10, .txt 6 | package.json, pyproject.toml | 256 |

## matrix (● hit, · miss, ! box failed)

| | dnd_ai_dm | dndwright | inkandbone | jurnalis-engine | narrativeengine-p | opencombatengine | srd_5e | taleweaver |
|---|---|---|---|---|---|---|---|---|
| **A1** rules checked after the model speaks, violations fed back | · | ● | ● | ● | ● | ● | ● | ● |
| **A2** deterministic code decides, the model only narrates | ● | ● | · | ● | ● | · | · | ● |
| **A3** a person must confirm or can veto before something stands | · | · | ● | ● | ● | · | · | ● |
| **A4** hallucination or invented facts named as a problem | · | · | ● | · | ● | · | · | ● |
| **B1** dice from a seeded random generator | ● | ● | ● | ● | ● | ● | · | ● |
| **B2** dice handed in from outside, injectable or forced for tests | ● | ● | ● | · | ● | ● | · | · |
| **B3** a player can type the faces from physical dice | · | · | · | · | · | · | · | · |
| **B4** advantage and disadvantage | ● | ● | ● | ● | ● | ● | ● | ● |
| **B5** unpredictable or cryptographic randomness for live play | · | ● | ● | · | · | · | · | ● |
| **C1** initiative order in a fight | ● | ● | ● | ● | ● | ● | ● | ● |
| **C2** attack roll against armor class | ● | ● | ● | ● | ● | ● | ● | ● |
| **C3** damage types, resistance and vulnerability | · | ● | · | ● | ● | ● | ● | · |
| **C4** death saving throws | · | ● | ● | ● | · | ● | ● | · |
| **C5** conditions such as stunned, prone, poisoned | · | ● | ● | ● | ● | ● | ● | · |
| **C6** reactions or opportunity attacks | · | ● | · | ● | ● | ● | ● | · |
| **D1** state saved and loaded as JSON | ● | ● | ● | ● | ● | ● | · | ● |
| **D2** an event log or history of what happened | ● | · | ● | · | ● | ● | · | ● |
| **D3** a run can be replayed or reproduced | ● | ● | ● | ● | ● | ● | · | ● |
| **D4** memory of the campaign between sessions | · | · | ● | · | ● | ● | · | ● |
| **D5** undo, rollback or taking back a step | · | ● | ● | ● | ● | · | · | ● |
| **E1** content safety, lines and veils, age or family play | · | · | · | · | ● | · | · | ● |
| **E2** local, self-hosted, offline, no telemetry | · | · | ● | · | ● | · | · | ● |
| **E3** which model APIs or keys it needs | ● | ● | ● | · | ● | · | · | ● |
| **F1** which SRD version the rules follow | · | ● | · | ● | ● | ● | ● | · |
| **F2** licence terms that restrict use | · | · | · | · | · | ● | · | ● |
| **F3** what is not built yet | · | · | · | · | ● | · | · | ● |
| **G1** how to install and run it | ● | ● | ● | · | ● | ● | ● | ● |

## by question

### A1: rules checked after the model speaks, violations fed back (asked: "rule violations enforce")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `pyproject.toml, line 62` — [tool.ruff.lint] # State the enforced rule set EXPLICITLY rather than inheriting ruff's defaults. # Inheriting means the gate's meaning is a property of whichever ruff CI happened # to install, so a release that widens the default
- **inkandbone** ● `README.md, line 849` — the ruleset has dice roll rules defined. Some systems don't enforce automatic dice rolls. You can always roll manually using the dice buttons in the left sidebar.
- **jurnalis-engine** ● `src/state/mod.rs, line 49` — art of the most recent completed long rest, /// used to enforce the SRD 5.1 "one long rest per 24 hours" rule. /// `None` if the character has never taken a long rest. #[serde(default)] pub last_long_rest_minutes:
- **narrativeengine-p** ● `Example_Setup/World_compendium/Franchisee/Chainsaw Man/CSM_AI_optimized.md:369` — he is not. But he becomes their family. He cooks for them, enforces house rules, and quietly ca
- **opencombatengine** ● `docs/adr/0054-character-builder.md, line 38` — **Positive**: * **Robustness**: Character creation enforces rules and dependencies. * **Dynamic**: Stat updates propagate correctly. * **Negative**: * **Complexity**: Circular dependencies in constructor req
- **srd_5e** ● `lib/srd/rules/exhaustion.ex, line 6` — @enforce_keys [:level, :d20_penalty, :speed_penalty, :dead?] defstruct [:level, :d20_penalty, :speed_penalty, :dead?]
- **taleweaver** ● `backend/api/routes/adventures/turn_pass_flow.py, line 55` — Violations are appended to `rule_violations` so Pass 2 narrates the failure. Soft rules run first, against the sequence active when the message started; their outcomes are regular events, not violations. """ ac

### A2: deterministic code decides, the model only narrates (asked: "deterministic engine narrates")

- **dnd_ai_dm** ● `AGENTS.md, line 5` — nsole D&D 5e-inspired RPG. Python 3.10+. The game engine is deterministic and owns all rules. A pluggable narrator writes the prose: `OpenAINarrator` (OpenAI Chat Completions) or `OfflineNarrator` (templates). Dependencies: `opena
- **dndwright** ● `README.md, line 95` — A self-contained, typed dice engine (`dndwright.dice`) — deterministic by default:
- **inkandbone** · no passage held the question's words
- **jurnalis-engine** ● `README.md, line 8` — A stateless, deterministic text-based CRPG engine implementing SRD 5.1 (d20) mechanics. The engine is a standalone Rust library crate — it carries no server, no persistent state, and no runtime dependencies beyond `serde` and `ran
- **narrativeengine-p** ● `mobile/docs/COMBAT_PHASE3_CONTRACTS.md, line 205` — ls), (2) narrate the engine-computed outcome. Enemies are deterministic (Phase 2 engine) — no per-enemy calls.
- **opencombatengine** · nothing in the top 8 holds the rule; best-ranked: `RELEASE_NOTES.md, line 79`
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/api/routes/adventures/talent_use.py, line 3` — The engine part is deterministic: it checks the unlock state, the uses left and the cost, resolves the target in the current scene, pays the cost, counts the use and runs the talent's ``on_use_script`` (with a ``talent`` dict in s

### A3: a person must confirm or can veto before something stands (asked: "player confirm approve")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · no passage held the question's words
- **inkandbone** ● `internal/api/automation_jobs.go, line 933` — t but not trigger-happy: only remove when the story clearly confirms they are gone. Empty array if none.
- **jurnalis-engine** ● `src/combat/mod.rs, line 2648` — : &mut GameState, ) -> Option<GrappleEscapeResult> { // Confirm the player is actually grappled. if !conditions::has_condition(&state.character.conditions, ConditionType::Grappled) { return None; }
- **narrativeengine-p** ● `Example_Setup/Ability Compendium/simulation_room_cross_system_ability_compendium.json:5014` — nal content", "gmNotes": "Original provisional ability. Confirm NIMPH capabilities and balance before approving it for a character.", "promptEnabled": true,
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/core/prompts.py, line 513` — summarize the blueprint in character and ask the player to confirm it.\n" "Once the player confirms, the Loom opens a review dialog with the blueprint. The player can adjust it there " "and starts the weaving with its sta

### A4: hallucination or invented facts named as a problem (asked: "hallucinate")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · no passage held the question's words
- **inkandbone** ● `README.md, line 15` — aps, and rulebook text — so it remembers everything without hallucinating your game state.
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `mobile/docs/WITNESS_INTEGRITY.md, line 25` — * **Result:** The LLM cannot hallucinate or act on verbatim scene details that the current scene's NPCs could not possibly know because that text is completely omitted from the context.
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `RELEASE_NOTES_v0.7.0-beta.md, line 130` — ies) back over the LLM output, guaranteeing zero dropped or hallucinated mechanics. * **Adherence Modes**: * **Strict Adherence**: Forces the AI to strictly preserve chapter order and add only the minimum needed to connect your

### B1: dice from a seeded random generator (asked: "seed random")

- **dnd_ai_dm** ● `AGENTS.md, line 9` — -r requirements-dev.txt python main.py --offline --quick --seed 1 # play without network python -m pytest # run tests black . # format ```
- **dndwright** ● `README.md, line 124` — t, overkill tracked s, save = roll_death_save(s, DiceEngine(seed=1)) # nat 20 → 1 HP; 3 fails → dead s.is_stable, s.is_dead, s.hp_percentage ```
- **inkandbone** ● `internal/db/integrity_migration_test.go, line 475` — mustInsertID(t, seed, `INSERT INTO messages(session_id, role, content) VALUES (?, 'assistant', 'See /api/files/maps/old.svg and keep text.')`, sessionID) require.NoError(t, seed.Close())
- **jurnalis-engine** ● `src/combat/monsters.rs, line 1126` — // now that the window extends to HP 35. use rand::SeedableRng; use rand::rngs::StdRng; let mut found_dark_mage = false; for seed in 0..200u64 { let mut rng = StdRng::seed_from_u64(seed
- **narrativeengine-p** ● `src/services/npc-generation/profile.ts, line 167` — ts, 0); // NPC Signature Kit (v1) — durable loadout seeded from the render call. `undefined` // (empty kit) is fine and expected for plain characters. Bounded by sanitizeSignatureKit. newEntry.signatureKit
- **opencombatengine** ● `README.md, line 71` — r handling without exceptions - ✅ **Reproducible Testing**: Seed-based dice rolling for deterministic tests
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `docs/specs/audio_generation.md, line 211` — e_settings`), cache by `(provider, model, prompt, duration, seed)` hash so identical prompts across sessions reuse one file (`data/audio_cache/`). * **Licensing:** exported adventures carry an "AI-generated audio (Google Lyria /

### B2: dice handed in from outside, injectable or forced for tests (asked: "inject dice roller")

- **dnd_ai_dm** ● `AGENTS.md, line 37` — dataclasses and functions. - All randomness goes through an injected `random.Random` or `Dice`. Never call the `random` module's global functions. - The engine returns output as `list[str]`. Only `ui/` prints. Line prefixes contro
- **dndwright** ● `CHANGELOG.md, line 537` — `DiceEngine(seed=…)`); for unpredictable production rolls inject any `random.Random` (e.g. `DiceEngine(rng=secrets.SystemRandom())`) — no NumPy dependency. `DiceEngine` is also re-exported at the top level.
- **inkandbone** ● `docs/superpowers/specs/2026-04-07-vtm-v5-overhaul-design.md, line 270` — ntries each. Rolls fire automatically on Messy Critical and inject result into GM context.
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `Example_Setup/Ruleset/4.4_Fable5_PVP_mode.md, line 193` — Trigger: an injected `DICE OUTCOMES` or `RESOLVED ROLL` tag. The engine already rolled; you narrate. Never reroll, change tier, combine alternatives, or let prose soften or negate the result.
- **opencombatengine** ● `tests/OpenCombatEngine.Implementation.Tests/Features/MonsterAbilityTests.cs, line 114` — // Decision: Refactor RechargeableFeature to allow injecting roller for testability? // Or use an IServiceLocator? // Let's leave it for now and test what we can deterministically. } }
- **srd_5e** · no passage held the question's words
- **taleweaver** · no passage held the question's words

### B3: a player can type the faces from physical dice (asked: "physical dice")

- **dnd_ai_dm** · nothing in the top 8 holds the rule; best-ranked: `AGENTS.md, line 26`
- **dndwright** · nothing in the top 8 holds the rule; best-ranked: `src/dndwright/content/classes.json, line 706`
- **inkandbone** · nothing in the top 8 holds the rule; best-ranked: `docs/games/shadowrun.md, line 15`
- **jurnalis-engine** · nothing in the top 8 holds the rule; best-ranked: `src/combat/mod.rs, line 2066`
- **narrativeengine-p** · nothing in the top 8 holds the rule; best-ranked: `src/services/npc-generation/profile.ts, line 277`
- **opencombatengine** · nothing in the top 8 holds the rule; best-ranked: `CODE_OF_CONDUCT.md, line 30`
- **srd_5e** · nothing in the top 8 holds the rule; best-ranked: `CHANGELOG.md, line 29`
- **taleweaver** · nothing in the top 8 holds the rule; best-ranked: `backend/core/prompts.py, line 364`

### B4: advantage and disadvantage (asked: "advantage disadvantage")

- **dnd_ai_dm** ● `README.md, line 9` — ability modifiers, proficiency, armor class, skill checks, advantage and disadvantage, critical hits, levels 1–10. - **Turn-based combat:** initiative, attack, dodge, flee, potions and one class feature per class. - **Procedural
- **dndwright** ● `CHANGELOG.md, line 531` — 5e dice expressions (`1d20+5`, `4d6kh3`, `2d6r1`, `1d6!`, advantage/disadvantage) plus `roll_attack`/`roll_save`/`roll_check`/`roll_damage`/`roll_initiative`/`roll_stat_array`/ `roll_hit_dice`/`roll_death_save`. Returns a **
- **inkandbone** ● `docs/games/dnd5e.md, line 57` — roll d20 + ability modifier + proficiency (if trained). - **Advantage/Disadvantage:** Roll twice, take the higher or lower. The AI tells you when this applies. - **Short rests:** Recover some HP using Hit Dice. Tell the AI when yo
- **jurnalis-engine** ● `src/combat/mod.rs, line 5861` — weapon_name: "Longsword".to_string(), disadvantage: false, attacker_had_advantage: false, } }
- **narrativeengine-p** ● `Example_Setup/Ruleset/4.4_Fable5_PVP_mode.md, line 197` — . One label per category → it is final. If a category lists Disadvantage / Normal / Advantage variants, pick exactly one tier first: Normal by default; Advantage only if the player explicitly leveraged a known weakness or superior
- **opencombatengine** ● `docs/adr/0043-condition-effects.md, line 25` — to query the `IEffectManager` (via `StatType`s like `AttackAdvantage`, `IncomingAttackAdvantage`) to determine if advantage or disadvantage applies.
- **srd_5e** ● `lib/srd/dice.ex, line 41` — * `:advantage` - Rolls 2d20 and takes the max * `:disadvantage` - Rolls 2d20 and takes the min
- **taleweaver** ● `LICENSE-CC-BY-NC-4.0, line 35` — s not primarily intended for or directed towards commercial advantage or monetary compensation. For purposes of this Public License, the exchange of the Licensed Material for other material subject to Copyright and Similar Rights

### B5: unpredictable or cryptographic randomness for live play (asked: "cryptographic random secrets")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `README.md, line 106` — # unpredictable production rolls (no NumPy dependency): import secrets DiceEngine(rng=secrets.SystemRandom()) ```
- **inkandbone** ● `docs/superpowers/specs/2026-07-16-complete-project-remediation-design.md, line 51` — copied into a browser cookie. A successful login creates a cryptographically random, server-side session with:
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** · nothing in the top 8 holds the rule; best-ranked: `Example_Setup/World_compendium/Heroes Aftermath/design_pillars.md:148`
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `scripts/generate_keys.py, line 39` — er = argparse.ArgumentParser( description="Generate cryptographic keys for TaleWeaver (.env)", formatter_class=argparse.RawDescriptionHelpFormatter, ) group = parser.add_mutually_exclusive_group() group

### C1: initiative order in a fight (asked: "initiative order")

- **dnd_ai_dm** ● `core/combat_system.py, line 43` — nt for _, _, combatant in rolls] lines = ["Roll for initiative!"]
- **dndwright** ● `README.md, line 194` — amage, temp HP, healing, death saves. | | `dndwright.combat.initiative` | Pure initiative: roll, order (DEX tie-break), advance/rewind turns. |
- **inkandbone** ● `docs/superpowers/specs/2026-04-04-phase-a-design.md, line 147` — P milestones from AI narration (deferred to Phase E) - Roll-initiative button (combatants already have initiative set when combat starts via MCP tools; this feature only improves display and turn tracking) - Player-visible turn in
- **jurnalis-engine** ● `src/combat/mod.rs, line 7715` — ult) should handle it. let json = r#"{ "initiative_order": [], "current_turn": 0, "round": 1, "distances": {}, "player_movement_remaining": 30, "playe
- **narrativeengine-p** ● `Example_Setup/World_compendium/Community Creation/Warhammer 40k - 15-07-2026 Version - By operatorofarma/Vorthain_Reach_Lore.md:160` — thing except wasting them, and files insubordination under "initiative" when it works. He writes a personal letter for every trooper the regiment loses. All of them. **Voice:** Gravel and understatement; calls catastrophes "a bit
- **opencombatengine** ● `docs/adr/0058-combat-loop-refinement.md, line 19` — ate `StandardTurnManager.NextTurn()` to iterate through the initiative order until it finds a living creature or completes a full loop (preventing infinite loops if everyone is dead).
- **srd_5e** ● `lib/srd.ex, line 49` — # Order the combatants. The caller rolls each initiative and captures the roll. Initiative.order([ {"knight", Dice.Rolls.initiative(2)}, {"orc", Dice.Rolls.initiative(1)} ]) #=> [{"orc", %Srd.Dice.Roll{...}}, {"kni
- **taleweaver** ● `README.md, line 100` — cal Combat Dialog:** Full-screen combat view with per-round initiative (every combatant acts in rolled order, shown as clickable portraits above the arena), a stack of enemy cards to pick your target from (the selected target move

### C2: attack roll against armor class (asked: "armor class attack")

- **dnd_ai_dm** ● `README.md, line 9` — - **5e-style rules:** ability modifiers, proficiency, armor class, skill checks, advantage and disadvantage, critical hits, levels 1–10. - **Turn-based combat:** initiative, attack, dodge, flee, potions and one class feature per c
- **dndwright** ● `README.md, line 152` — ength sets the Strength score, a Ring of Protection adds to Armor Class, and Dwarven Resilience unions in poison resistance — compose() merges them and one snap-in recomputes the whole downstream subtree (strength modifier to athl
- **inkandbone** ● `docs/games/dnd5e.md, line 15` — **AC** is your Armor Class. Enemies need to roll this high to hit you.
- **jurnalis-engine** ● `src/character/feat.rs, line 176` — FeatDef { name: "Defense", description: "+1 AC while wearing armor.", category: FeatCategory::FightingStyle, effects: &[FeatEffect::Flavor], }, FeatDef { name: "Dueling",
- **narrativeengine-p** ● `src/services/combat/__tests__/combatController.test.ts, line 434` — , stats: [{ name: 'HP', value: '30' }, { name: 'Armor Class', value: '15' }, { name: 'Attack', value: '+6' }, { name: 'Damage', value: '2d6+1' }], weaknesses: ['fire'], resistances: [], };
- **opencombatengine** ● `docs/adr/0044-magic-item-passive-bonuses.md, line 11` — often provide passive bonuses to statistics, such as +1 to Armor Class (Ring of Protection), +1 to Saving Throws, or bonuses to Attack/Damage rolls. We needed a way to apply these bonuses automatically when an item is equipped or
- **srd_5e** ● `priv/data/feats.exs, line 125` — le}], features: [ %{name: "Defense", text: "+1 to Armor Class while wearing light, medium, or heavy armor."}
- **taleweaver** ● `docs/specs/entity_bundle_format.md, line 29` — s along: attributes in `stat_modifier_*` (absolute values), armor class as offset in `stat_modifier_armor_class` (AC = 10 + value), and `metadata_json.main_attack`, `special_actions` and scripts. Protagonist: profile, vitals, attr

### C3: damage types, resistance and vulnerability (asked: "damage resistance vulnerability")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `CHANGELOG.md, line 467` — ### Added - **Damage-type resistance / immunity / vulnerability** in `dndwright.combat`. `CombatantState` gains `resistances` / `immunities` / `vulnerabilities` (frozensets of damage types — plain, composable data), and `apply
- **inkandbone** · no passage held the question's words
- **jurnalis-engine** ● `src/combat/monsters.rs, line 646` — def.size, alignment: def.alignment, damage_resistances: def.damage_resistances.to_vec(), damage_immunities: def.damage_immunities.to_vec(),
- **narrativeengine-p** ● `Example_Setup/World_compendium/Community Creation/The World of John Wick - By ericsonguk/world_lore_the_continental V1.1(1).md:283` — Its vulnerability is loyalty itself. Enemies know Koji will risk institutional security for people he considers family. Younger members disagree over whether honor means obedience, resistance, or survival.
- **opencombatengine** ● `docs/architecture/011-damage-types.md, line 17` — mage Update**: Now accepts `DamageType` as a parameter. - **Resistance Logic**: `StandardHitPoints` (or `StandardCreature` via `ICombatStats`) checks for resistance/vulnerability before applying damage. - Resistance: Halves da
- **srd_5e** ● `CHANGELOG.md, line 72` — s faces (`Attack`, `Save`, `Check`); `Damage` with the 13 damage types and resistance/vulnerability/immunity; `Hitpoints` with temporary hit points, clamping, and downed/dead/recovered outcomes; `DeathSaves`; and `Initiative
- **taleweaver** · no passage held the question's words

### C4: death saving throws (asked: "death saving throws")

- **dnd_ai_dm** · nothing in the top 8 holds the rule; best-ranked: `content/heroes.py, line 27`
- **dndwright** ● `src/dndwright/combat/combat.py, line 186` — ozen=True) class DeathSaveResult: """The outcome of one death saving throw applied to the running tally."""
- **inkandbone** ● `docs/games/dnd5e.md, line 43` — -based. The AI tracks initiative order, HP, conditions, and death saves. When you drop to 0 HP, the AI starts death saving throws.
- **jurnalis-engine** ● `src/combat/mod.rs, line 6302` — // ---------- Death Saving Throws (issue #84) -------------------------- // // Per SRD 5e, a player character reduced to 0 HP does not immediately // die: they fall unconscious and roll Death Saving Throws at the s
- **narrativeengine-p** · nothing in the top 8 holds the rule; best-ranked: `Example_Setup/World_compendium/Franchisee/Chainsaw Man/CSM_AI_optimized.md:339`
- **opencombatengine** ● `docs/architecture/012-death-saves.md, line 15` — We implemented Death Saving Throw logic within the `StartTurn` method of `StandardCreature`.
- **srd_5e** ● `lib/srd/dice/rolls.ex, line 27` — @doc "A death saving throw: **1d20**, no modifier." @spec death_save() :: Dice.Roll.t() def death_save, do: Dice.d20(0)
- **taleweaver** · nothing in the top 8 holds the rule; best-ranked: `backend/engine/combat/area_attacks.py, line 3`

### C5: conditions such as stunned, prone, poisoned (asked: "conditions stunned prone")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `src/dndwright/content/creatures.json, line 5053` — es": [ "Necrotic", "Poison" ], "condition_immunities": [ "Charmed", "Exhaustion", "Frightened", "Grappled", "Incapacitated", "Paralyzed", "Petrifi
- **inkandbone** ● `internal/db/queries_combat_test.go, line 246` — // Advance to B (index 1): B's conditions decay _, _, err = d.AdvanceTurn(encID) require.NoError(t, err) combatants, err := d.ListCombatants(encID) require.NoError(t, err) // A (index 0) unchanged assert.Equal(t, `[{"name":
- **jurnalis-engine** ● `src/combat/mod.rs, line 1083` — // Defender-side conditions: Prone/Stunned/Paralyzed/Petrified/Restrained/ // Unconscious/Blinded grant advantage; Invisible imposes disadvantage. match conditions::get_defense_advantage(&player.conditions, target_cond
- **narrativeengine-p** ● `packages/engine/src/combat/__tests__/director.test.ts, line 159` — it('accepts an order for a stunned unit, which still loses the turn', () => { const s = arena([hero(at(8, 5)), officer('e', at(5, 5), { conditions: [{ id: 'stunned', turns: 1 }] })]); const r = applyOrders(s, [
- **opencombatengine** ● `docs/architecture/014-concrete-conditions.md, line 17` — - **Standard Conditions**: Implemented classes for `Blinded`, `Charmed`, `Deafened`, `Frightened`, `Grappled`, `Incapacitated`, `Invisible`, `Paralyzed`, `Petrified`, `Poisoned`, `Prone`, `Restrained`, `Stunned`, `Unconscious`. -
- **srd_5e** ● `priv/data/classes.exs, line 1047` — Touch", text: "Lay On Hands can also end blinded, charmed, deafened, frightened, paralyzed, or " <> "stunned, at 5 hit points from the pool per condition." }, %{ level: 16,
- **taleweaver** · no passage held the question's words

### C6: reactions or opportunity attacks (asked: "opportunity attack reaction")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `src/dndwright/content/creatures.json, line 10448` — : "For each head the hydra has beyond one, it gets an extra Reaction that can be used only for Opportunity Attacks." } ], "actions": [ { "name": "Multiattack", "text": "The hydra mak
- **inkandbone** · no passage held the question's words
- **jurnalis-engine** ● `src/character/feat.rs, line 154` — FeatDef { name: "Sentinel", description: "Opportunity attacks stop movement; reaction attack when adjacent ally is attacked.", category: FeatCategory::General, effects: &[FeatEffect::Flavor],
- **narrativeengine-p** ● `Example_Setup/Ability Compendium/original_magic_system_ability_compendium_template.json:306` — force, unfamiliar magical structure, or attacks outside the reaction window." ],
- **opencombatengine** ● `docs/adr/0054-core-event-system.md, line 11` — UI needs to know when a creature moves to animate it. - The Reaction System needs to know when a creature moves to trigger opportunity attacks. - Conditions need to know when a turn starts or ends. - Features might trigger on spec
- **srd_5e** ● `priv/data/classes.exs, line 667` — e up to half your speed without " <> "provoking opportunity attacks." }, %{ level: 6, name: "Ability Score Improvement",
- **taleweaver** · no passage held the question's words

### D1: state saved and loaded as JSON (asked: "json save load")

- **dnd_ai_dm** ● `README.md, line 12` — and gold rewards. - **Saving:** save, load and autosave as JSON files.
- **dndwright** ● `CHANGELOG.md, line 608` — erate_classes`/`species`/`creatures`): you pass a `complete_json(prompt, system) -> dict` callable wrapping your own LLM; prompts produce *original homebrew* (no official content), matching the bundled schema and component ont
- **inkandbone** ● `docs/superpowers/specs/2026-06-25-group-b-interactivity-design.md, line 326` — canned for the `[ZONES]...[/ZONES]` block. - Extracted zone JSON is parsed and each entry passed to `CreateMapZone`. If the block is absent, malformed, or contains invalid coords (outside 0–1), map creation succeeds without zones
- **jurnalis-engine** ● `src/character/mod.rs, line 719` — #[test] fn test_character_missing_subrace_deserializes_none() { // Legacy save predating the subrace field: should default to None. let c = create_character("Test".to_string(), Race::Human, Class::Fighter,
- **narrativeengine-p** ● `packages/engine/src/combat/__tests__/builtins.test.ts, line 203` — e).state; expect(step).toBe(19); expect(fnv(JSON.stringify(state))).toBe('d2070ee1'); let loaded = JSON.parse(JSON.stringify(state)) as CombatState;
- **opencombatengine** ● `docs/adr/0059-combat-serialization.md, line 33` — stays in classes, data stays in DTOs. - **Flexibility**: JSON format is human-readable and version-tolerant. - **Testability**: `CombatSerializationTests` verify the fidelity of the save/load process.
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `docs/comfyui/README.md, line 119` — alternative is Google Lyria with a Gemini key), upload the JSON file, enter the ComfyUI server URL, switch audio generation on and save. Use **Generate test clip** to render one clip and listen to it. The test runs in the b

### D2: an event log or history of what happened (asked: "event log history")

- **dnd_ai_dm** ● `docs/architecture.md, line 45` — ates quests from world facts and completes them on matching events. | | `core/narrator.py` | `Scene`, `Narration`, the `Narrator` protocol and `OfflineNarrator`. | | `core/openai_narrator.py` | `OpenAINarrator`: prompts, JSON pars
- **dndwright** · no passage held the question's words
- **inkandbone** ● `docs/superpowers/specs/2026-04-05-button-theme-inventory-currency-favicon-design.md, line 156` — ination (multi-denomination is a future concern) - Currency history / transaction log (chat history serves this role) - Shop/merchant UI (buy flow is GM-narrated; AI handles the deduction)
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `src/services/mods/events/__tests__/emitSites.test.ts, line 65` — it('reports pending: false for a history edit', () => { useAppStore.setState({ messages: [msg('u1', 'user')] }); const log: Logged[] = []; const off = listen(['message.edited'], log);
- **opencombatengine** ● `docs/architecture/011-damage-types.md, line 26` — - Damage calculations are now type-aware. - `DamageTakenEventArgs` includes the `DamageType` for event subscribers (UI, logs). - Future features like "Resistance to Non-Magical Attacks" can be built on this enum.
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/api/routes/adventures/turn_llm_pipeline.py, line 396` — log_structured_event( "gm.turn.pipeline.context", adventure_id=self.manager.adventure.id, game_id=self.manager.game_id, operation="chat_turn", phase="context",

### D3: a run can be replayed or reproduced (asked: "replay reproducible")

- **dnd_ai_dm** ● `docs/guides/save-and-load.md, line 44` — ve files do not store the random number generator state. To replay the same world and the same dice from the start, use a seed:
- **dndwright** ● `src/dndwright/dice/engine.py, line 7` — Each engine owns a private RNG. ``DiceEngine(seed=42)`` is reproducible (stdlib Mersenne Twister) — ideal for tests, replay, and audit trails. The RNG is *stateful*: each roll advances the stream, so a sequence of rolls from one
- **inkandbone** ● `docs/superpowers/plans/2026-07-16-phase-2-runtime-reliability-protocols.md, line 7` — refer authoritative state reconciliation over durable event replay.
- **jurnalis-engine** ● `README.md, line 19` — o use across threads, processes, or network boundaries. - **Deterministic RNG** — seeded from a `u64`. Replay any session exactly by replaying the seed and input sequence. - **Ironman mode** — optional flag that gates save/load se
- **narrativeengine-p** ● `Example_Setup/World_compendium/Three Kingdoms - War of the Mandate/three_kingdoms_starterPrompt.md:116` — low Turban curses. These are rare, named, costly, and never reproducible. No spellcasters, no mana, no schools. The default explanation for any "magic" event is coincidence plus reputation. Let the players decide what they believe
- **opencombatengine** ● `src/OpenCombatEngine.Core/Interfaces/Dice/IDiceRoller.cs, line 74` — /// Gets or sets the random number generator seed for reproducible results /// </summary> /// <remarks> /// Setting a specific seed enables reproducible dice rolls for testing or replay functionality.
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `scripts/bundle_skill.py, line 356` — rfile.TarInfo: """Drop local owner data so archives are reproducible. O(1).""" info.uid = info.gid = 0 info.uname = info.gname = "" return info

### D4: memory of the campaign between sessions (asked: "campaign memory summary")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · no passage held the question's words
- **inkandbone** ● `internal/api/routes_messages.go, line 115` — last 30 messages to bound input token cost. // The session summary in buildWorldContext covers long-term memory.
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `src/services/archive-memory/__tests__/synopsisBackfill.test.ts, line 225` — it('regression: non-string summary (null/undefined/object from old campaigns) does not crash, skips the chapter', async () => { // Old campaigns may have chapters with non-string `summary` from buggy // seals,
- **opencombatengine** ● `src/OpenCombatEngine.GrpcSidecar/SystemEngineGrpcService.cs, line 29` — /// <summary> /// Implements the System Engine gRPC contract (protocol/system_engine.proto) /// against OpenCombatEngine. Every method is stateless per-call: no creature /// state is held between calls, since Master owns campaign/
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/api/routes/adventures/gameplay_logic.py, line 2466` — task is to maintain a concise, chronological, and coherent summary of past events that have fallen outside the active memory window.\n\n" "CRITICAL INSTRUCTIONS:\n" "1. Output MUST be entirely in English,

### D5: undo, rollback or taking back a step (asked: "undo revert")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `src/dndwright/combat/initiative.py, line 115` — Does not undo any actions — only moves the marker. Wrapping backward past the start decrements the round (floored at 1). """ n = len(order) if n == 0 or not any(e.is_active for e in order): return TurnA
- **inkandbone** ● `docs/superpowers/specs/2026-04-05-button-theme-inventory-currency-favicon-design.md, line 140` — eb/src/InventoryPanel.tsx` | Add currency row, inline edit, undo toast |
- **jurnalis-engine** ● `src/combat/mod.rs, line 1641` — is // rolled with disadvantage. Multiattack follow-ups revert to normal.
- **narrativeengine-p** ● `e2e/checkpoint3-uninstall-path.spec.ts, line 317` — // written until the user confirms, so a cancel needs no revert"). await annoCheckbox.click(); const disableDialog = page.locator('div[role="alertdialog"]').first(); await expect(disableDialog).toBeVisib
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/engine/scripting/player_inventory.py, line 43` — ict[str, Any]) -> None: """Adds an inventory entry, undoing an earlier removal of the same item.""" target = ref_id(entry) removed = self._changeset.player_removed_item_ids undone = next((i for i in

### E1: content safety, lines and veils, age or family play (asked: "content safety children")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · nothing in the top 8 holds the rule; best-ranked: `src/dndwright/content/classes.json, line 1450`
- **inkandbone** · nothing in the top 8 holds the rule; best-ranked: `internal/ai/openrouter.go, line 192`
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `Example_Setup/World_compendium/Franchisee/Chainsaw Man/CSM_AI_optimized.md:968` — lls, the warmth does not change; the content does. "Be good children and kill him." **Status:** Deceased (Part 1) **Faction:** American Bureau (implicitly); herself **Goals:** Capture Chainsaw Man. Expand her network of children.
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `backend/engine/media/image_generation_support.py, line 26` — r", "failed", "expired", "task not found", "tasknotfound"} _MODERATION_MARKERS = ("content moderated", "safety filter", "moderated")

### E2: local, self-hosted, offline, no telemetry (asked: "self-hosted local offline")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · nothing in the top 8 holds the rule; best-ranked: `src/dndwright/rules/compose.py, line 52`
- **inkandbone** ● `docs/security.md, line 3` — ink & bone is local-first, not inherently offline. The database and uploaded assets stay on the host, while model inputs go wherever the selected AI provider runs.
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `mobile/src/services/npc/nameBank.ts, line 3` — Engine-shipped name bank (Plan 05, Component A). A static, offline list of * given names organised by culture header, generated from the campaign-agnostic * asset pipeline (scripts/buildNameBank.mjs). * * Dual purpose: * 1.
- **opencombatengine** · no passage held the question's words
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `README.md, line 478` — - **Local ComfyUI Generation**: Offline text-to-image (SD 1.5/SDXL) and text-to-audio background music generation via local ComfyUI servers. - **Custom OpenAI-Compatible Endpoints**: Granular per-pass support for hosted and self-h

### E3: which model APIs or keys it needs (asked: "api key openai anthropic")

- **dnd_ai_dm** ● `README.md, line 3` — ion, talk to its people, take quests and fight monsters. An OpenAI model narrates the story and voices the characters. The game engine handles every rule: dice, combat, skill checks, XP and loot. Without an API key, a built-in off
- **dndwright** ● `src/dndwright/content/generate.py, line 3` — n(prompt, system) -> dict`` callable that wraps *your* LLM (OpenAI, Anthropic, OpenRouter, a local model, …) and returns the parsed JSON object. The prompts steer toward **original homebrew** — novel names and mechanics, never off
- **inkandbone** ● `internal/ai/deepseek.go, line 19` — // DeepSeekClient calls the DeepSeek API directly via its OpenAI-compatible endpoint. // It implements Completer, Responder, and Streamer. type DeepSeekClient struct { apiKey string model string http *http.Client think boo
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** ● `src/utils/__tests__/thinkingReserve.test.ts, line 9` — const claudeProvider: EndpointConfig = { endpoint: 'https://api.anthropic.com', apiKey: 'test-key', modelName: 'claude-sonnet', apiFormat: 'claude', }; const geminiProvider: EndpointConfig = { endpoint: 'https:
- **opencombatengine** · nothing in the top 8 holds the rule; best-ranked: `docs/adr/0057-open5e-integration.md, line 17`
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `README.md, line 116` — Designed to harness the reasoning power of flagship models (Anthropic Opus 5.x, OpenAI 5.x, DeepSeek v4 Pro) via our LiteLLM adapter for flawless, complex world generation. You provide your own API key, meaning you have full contr

### F1: which SRD version the rules follow (asked: "SRD system reference document")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** ● `README.md, line 212` — rules tables encode game *mechanics* derived from the **D&D System Reference Document 5.2.1** (English, published May 1, 2025; © Wizards of the Coast, **CC-BY-4.0**) — source PDF: [`SRD_CC_v5.2.1.pdf`](https://media.dndbeyond.com/
- **inkandbone** · nothing in the top 8 holds the rule; best-ranked: `docs/superpowers/plans/2026-07-16-phase-2-runtime-reliability-protocols.md, line 343`
- **jurnalis-engine** ● `src/equipment/magic.rs, line 100` — /// SRD 5.1 core magic weapons. Only mechanically-modelled weapons are /// included; deferred variants (Flame Tongue, Vorpal Sword, Holy Avenger) /// are documented in docs/specs/magic-items.md. pub const SRD_MAGIC_WEAPONS: &[Magi
- **narrativeengine-p** ● `Example_Setup/Ability Compendium/Dungeons and Dragons 5e 2024/README.md:47` — This work includes material from the System Reference Document 5.2.1 ("SRD 5.2.1") by Wizards of the Coast LLC, available at https://www.dndbeyond.com/srd. The SRD 5.2.1 is licensed under the Creative Commons Attribution 4.0 Inter
- **opencombatengine** ● `LEGAL.md, line 5` — This project uses game mechanics and rules derived from the System Reference Document 5.1 (SRD 5.1) under the Open Gaming License version 1.0a (OGL 1.0a).
- **srd_5e** ● `README.md, line 24` — This work includes material from the System Reference Document 5.2 ("SRD 5.2") by Wizards of the Coast LLC, available at https://www.dndbeyond.com/srd, and material from the System Reference Document 5.1 ("SRD 5.1") by Wizards of
- **taleweaver** · nothing in the top 8 holds the rule; best-ranked: `AGENTS.md, line 40`

### F2: licence terms that restrict use (asked: "non-commercial license")

- **dnd_ai_dm** · no passage held the question's words
- **dndwright** · no passage held the question's words
- **inkandbone** · no passage held the question's words
- **jurnalis-engine** · no passage held the question's words
- **narrativeengine-p** · nothing in the top 8 holds the rule; best-ranked: `Example_Setup/World_compendium/Franchisee/My Hero Academia/MHA_AI_optimized.md:100`
- **opencombatengine** ● `LEGAL.md, line 115` — ansformative work that adds substantial new functionality - Non-commercial open-source software - Tool that enhances rather than replaces official products
- **srd_5e** · nothing in the top 8 holds the rule; best-ranked: `LICENSE, line 159`
- **taleweaver** ● `docs/local_stable_diffusion.md, line 109` — flux1-dev-bnb-nf4` | NF4 safetensors | ~5.5 GB | FLUX.1-dev Non-Commercial | https://huggingface.co/lllyasviel/flux1-dev-bnb-nf4 | | `flux1-schnell-gguf` | GGUF (Q4_0/Q5_0) | ~6-8 GB | Apache-2.0 | https://huggingface.co/city96/FL

### F3: what is not built yet (asked: "not implemented roadmap")

- **dnd_ai_dm** · nothing in the top 8 holds the rule; best-ranked: `docs/architecture.md, line 72`
- **dndwright** · nothing in the top 8 holds the rule; best-ranked: `CHANGELOG.md, line 382`
- **inkandbone** · nothing in the top 8 holds the rule; best-ranked: `docs/superpowers/plans/2026-07-16-phase-1-security-privacy-data-integrity.md, line 452`
- **jurnalis-engine** · nothing in the top 8 holds the rule; best-ranked: `README.md, line 8`
- **narrativeengine-p** ● `Example_Setup/Ruleset/Archive/NPC Agency Architecture — Implementation Plan.md:212` — ## Phase 2+: Conditional Roadmap (build only if Phase 1.5 data demands)
- **opencombatengine** · nothing in the top 8 holds the rule; best-ranked: `ROADMAP.md, line 16`
- **srd_5e** · no passage held the question's words
- **taleweaver** ● `docs/status-updates/backlog.md, line 3` — One topic per post. Queue, not roadmap: an item is drafted only once the feature it describes is actually in `main`, and it leaves this list when the discussion is published. Order is a suggestion, not a promise.

### G1: how to install and run it (asked: "install run")

- **dnd_ai_dm** ● `AGENTS.md, line 9` — ```bash python -m venv .venv && source .venv/bin/activate pip install -r requirements-dev.txt python main.py --offline --quick --seed 1 # play without network python -m pytest # run tests black .
- **dndwright** ● `RELEASING.md, line 20` — hen run from a bare source tree. So after bumping you must `pip install -e .` before running the tests, or the guard is silently skipped.
- **inkandbone** ● `docs/superpowers/plans/2026-07-16-phase-3-responsive-accessible-ui.md, line 359` — Run: `cd e2e && npm install --save-dev --save-exact @axe-core/playwright@4.12.1`
- **jurnalis-engine** · nothing in the top 8 holds the rule; best-ranked: `README.md, line 48`
- **narrativeengine-p** ● `README.md, line 38` — **Or manually:** ```bash npm install npm run build --prefix packages/engine npm run dev ```
- **opencombatengine** ● `CONTRIBUTING.md, line 54` — CombatEngine.git ``` 4. Build the project: ```bash dotnet build ``` 5. Run tests: ```bash dotnet test ```
- **srd_5e** ● `priv/data/subclasses.exs, line 364` — : "Fast Hands", text: "As a bonus action, make a Sleight of Hand check to pick a lock, disarm a trap, or " <> "pick a pocket, or use an object." }, %{ level: 3, name: "Seco
- **taleweaver** ● `README.md, line 320` — # 4. Install & build frontend cd frontend npm ci npm run build cd ..
