# survey of 1 chunks, 27 questions, top 8

A hit: a served passage holds the question's rule (survey-questions.tsv). Evidence to read, not proof. A miss: not in the top 8, which is not the same as absent. Nothing here is sealed.

## facts (counted by code)

| chunk | licence file | most files | build files | test files |
|---|---|---|---|---|
| layforge | LICENSE: MIT License Copyright (c) 2026 James Duane Plotts | .go 208, .md 38, .json 2, LICENSE 1 | - | 115 |

## matrix (● hit, · miss, ! box failed)

| | layforge |
|---|---|
| **A1** rules checked after the model speaks, violations fed back | ● |
| **A2** deterministic code decides, the model only narrates | ● |
| **A3** a person must confirm or can veto before something stands | ● |
| **A4** hallucination or invented facts named as a problem | ● |
| **B1** dice from a seeded random generator | ● |
| **B2** dice handed in from outside, injectable or forced for tests | ● |
| **B3** a player can type the faces from physical dice | · |
| **B4** advantage and disadvantage | ● |
| **B5** unpredictable or cryptographic randomness for live play | · |
| **C1** initiative order in a fight | ● |
| **C2** attack roll against armor class | · |
| **C3** damage types, resistance and vulnerability | ● |
| **C4** death saving throws | ● |
| **C5** conditions such as stunned, prone, poisoned | ● |
| **C6** reactions or opportunity attacks | ● |
| **D1** state saved and loaded as JSON | ● |
| **D2** an event log or history of what happened | ● |
| **D3** a run can be replayed or reproduced | ● |
| **D4** memory of the campaign between sessions | ● |
| **D5** undo, rollback or taking back a step | ● |
| **E1** content safety, lines and veils, age or family play | ● |
| **E2** local, self-hosted, offline, no telemetry | ● |
| **E3** which model APIs or keys it needs | ● |
| **F1** which SRD version the rules follow | · |
| **F2** licence terms that restrict use | · |
| **F3** what is not built yet | ● |
| **G1** how to install and run it | · |

## by question

### A1: rules checked after the model speaks, violations fed back (asked: "rule violations enforce")

- **layforge** ● `CLAUDE.md, line 10` — ution, PvP, character validation, content policy) must be enforced in code at the tool-call layer, before the effect executes — never left to the model deciding correctly. If you're adding a tool the DM can call and it has a

### A2: deterministic code decides, the model only narrates (asked: "deterministic engine narrates")

- **layforge** ● `README.md, line 307` — "deterministic bookkeeping, not something the DM has to remember," now actually wired up rather than sitting unreachable in the engine. The DM can also illustrate a scene — `generate_scene_image` calls a pluggable image-gen provid

### A3: a person must confirm or can veto before something stands (asked: "player confirm approve")

- **layforge** ● `master/README.md, line 1786` — tion range, HP... reasonable... anything but overpowered" → approved). Listed characters and overrode that verdict through the real admin HTTP API, and confirmed the connected player received the live push. In an actual browser: p

### A4: hallucination or invented facts named as a problem (asked: "hallucinate")

- **layforge** ● `master/README.md, line 1333` — Privately` re-checks that same condition itself, so a stray/hallucinated call can't succeed just because the tool wasn't offered this turn (the same "gates over prompting" shape every DM tool in this package already follows). Deli

### B1: dice from a seeded random generator (asked: "seed random")

- **layforge** ● `README.md, line 92` — sidecar to retry, or see OpenCombatEngine's README for pre-seeding the cache.

### B2: dice handed in from outside, injectable or forced for tests (asked: "inject dice roller")

- **layforge** ● `README.md, line 300` — er on another's behalf, and a maturity-tier text constraint injected into DM narration, both via a per-campaign JSON config file (`-campaign-policies`); an unconfigured campaign gets the strictest PvP setting by default, not an op

### B3: a player can type the faces from physical dice (asked: "physical dice")

- **layforge** · nothing in the top 8 holds the rule; best-ranked: `master/web/README.md, line 267`

### B4: advantage and disadvantage (asked: "advantage disadvantage")

- **layforge** ● `docs/design.md, line 392` — content):** basic mechanics (ability scores, saving throws, advantage/disadvantage), generic creature statistics, spell *mechanics* (not descriptions), generic class features as mechanics, standard conditions, action economy.

### B5: unpredictable or cryptographic randomness for live play (asked: "cryptographic random secrets")

- **layforge** · nothing in the top 8 holds the rule; best-ranked: `master/README.md, line 2241`

### C1: initiative order in a fight (asked: "initiative order")

- **layforge** ● `README.md, line 279` — start real structured turn order (`start_combat`) — rolling initiative through the System Engine rather than trusting the model to order it — broadcast to everyone as `turn.state`, and now actually enforced on players too: once co

### C2: attack roll against armor class (asked: "armor class attack")

- **layforge** · nothing in the top 8 holds the rule; best-ranked: `master/README.md, line 692`

### C3: damage types, resistance and vulnerability (asked: "damage resistance vulnerability")

- **layforge** ● `docs/client-message-family-ideas.md, line 255` — DC | name, creature type, one-line nature | | 2 | DC + 3 | resistances / immunities / vulnerabilities, condition immunities | | 3 | DC + 5 | its attacks — what it does, damage types, roughly how hard it hits | | 4 | DC + 8 | the

### C4: death saving throws (asked: "death saving throws")

- **layforge** ● `README.md, line 286` — isn't skipped — they get a turn that automatically rolls a death saving throw instead (a real System Engine RPC, `StartTurn`, newly added so OpenCombatEngine's own SRD death-save logic — previously built but unreachable — is actu

### C5: conditions such as stunned, prone, poisoned (asked: "conditions stunned prone")

- **layforge** ● `master/README.md, line 745` — lt for real as part of this (only the resulting `Grappled`/`Prone` conditions existed; nothing ever applied them), composed entirely from primitives already tested elsewhere (opposed Athletics/Acrobatics checks, condition applicat

### C6: reactions or opportunity attacks (asked: "opportunity attack reaction")

- **layforge** ● `docs/client-message-family-ideas.md, line 37` — t Reorx and needs to pause: *"Cast Shield? Counterspell? an opportunity attack? Cutting Words?"* — a prompt that **interrupts** whatever's on screen, shows a visible countdown, and **auto-resolves to a default** if the player does

### D1: state saved and loaded as JSON (asked: "json save load")

- **layforge** ● `master/internal/admin/policy_provider.go, line 20` — ign doc // §3.3) — no in-memory cache, since SQLite already serializes concurrent // access and a settings change should be visible on the very next call, // not after some cache TTL. A campaign with no admin-saved row falls // ba

### D2: an event log or history of what happened (asked: "event log history")

- **layforge** ● `docs/client-message-family-ideas.md, line 213` — er the assembled text and write a single `client.display` event, so `log.history_request` replay shows the finished bubble, not a stutter. Same rule as not logging every `audio.chunk`, only the finalized transcript. - If the

### D3: a run can be replayed or reproduced (asked: "replay reproducible")

- **layforge** ● `registry/README.md, line 136` — .org`) on the same infrastructure — documented here so it's reproducible, not tribal knowledge:

### D4: memory of the campaign between sessions (asked: "campaign memory summary")

- **layforge** ● `master/internal/registry/heartbeat.go, line 155` — artbeat: failed to heartbeat", "error", err, "campaign_id", summary.CampaignID) return } // The registry no longer recognizes this listing (TTL expiry, or // the registry process itself restarted — its store is in-memory by

### D5: undo, rollback or taking back a step (asked: "undo revert")

- **layforge** ● `master/internal/campaignpack/write.go, line 74` — mong files, or the merged pack failing to parse), this call undoes // only what it itself did — restoring a file's prior content if it

### E1: content safety, lines and veils, age or family play (asked: "content safety children")

- **layforge** ● `master/internal/campaignpack/generate.go, line 93` — - lines and veils: OPTIONAL lists of standing safety limits, ONLY when the adventure's content genuinely calls for them (an adventure touching torture, execution of captives, or harm to children should pre-declare these; a strai

### E2: local, self-hosted, offline, no telemetry (asked: "self-hosted local offline")

- **layforge** ● `README.md, line 238` — hed default endpoint unless `-llm-url` overrides it (e.g. a self-hosted OpenAI-compatible gateway). `-llm-model` takes whatever model name/tag the chosen provider expects — an Ollama tag like `qwen3.8:27b`, or a vendor model id li

### E3: which model APIs or keys it needs (asked: "api key openai anthropic")

- **layforge** ● `README.md, line 31` — **An LLM** for the AI Dungeon Master's narration — an [Ollama](https://ollama.com) server is the zero-key default (`-llm-url`/`-llm-model`); Anthropic/OpenAI/OpenRouter/Z.ai also work with `-llm-provider` + `-llm-api-

### F1: which SRD version the rules follow (asked: "SRD system reference document")

- **layforge** · nothing in the top 8 holds the rule; best-ranked: `docs/design.md, line 11`

### F2: licence terms that restrict use (asked: "non-commercial license")

- **layforge** · no passage held the question's words

### F3: what is not built yet (asked: "not implemented roadmap")

- **layforge** ● `master/main.go, line 60` — by // protocol area, and docs/design.md §11 for the overall roadmap. package main

### G1: how to install and run it (asked: "install run")

- **layforge** · nothing in the top 8 holds the rule; best-ranked: `README.md, line 24`
