# Memory: which box to ask, and which stack

Read this first. It says what boxes and stacks exist in `boxes/`, what each
is for, how to lay it, and what it has already said, so you know which to
ask and don't lay one twice. A box is data and stays out of git; a stack is
a list of wants, each a proposal (cut any), never sealed here. Add a line
for every box or stack you make. Rule of the house: one want at a time on a
person's yes, and no agent ever seals or reads the key; these were built
broadly at the maintainer's word of 2026-11-21 ("as many boxes and stacks
as you want, write them down here").

## The boxes

| Box | Ask it when you want to know… | Pile | Lay it | Last run |
|---|---|---|---|---|
| [gm-projects/](gm-projects/) | how other open AI game masters keep a model honest, remember a campaign, roll dice, run a fight, and what they let us take | NarrativeEngine-P `6514be9`, ink & bone `653e527`, dnd_ai_dm `ea046d3`, TaleWeaver `7c12722`: only .md .py .go .ts .toml .txt and LICENSE files; 2,908 files | `bash boxes/gm-projects/rebuild.sh SCRATCH` (checkouts under `..`, or `GM_PROJECTS`); about 3 min | 10 of 10 answered, none flagged |
| [srd-engines/](srd-engines/) | whether an outside SRD rules engine could stand under the record and seal: can the dice be handed in, is it deterministic, how is a fight's state kept, what each asks of us | OpenCombatEngine `16b45b0` (C#, MIT), jurnalis-project/engine `dbf40d4` (Rust), srd_5e `b0a2164` (Elixir, from the agentic-realms monorepo's packages/srd_5e, Apache-2.0), dndwright `6f0fb9e` (Python, MIT); 685 files | `bash boxes/srd-engines/rebuild.sh SCRATCH` (checkouts at `../OWNER/NAME`, or `ENGINES_DIR`); about 30 s | 9 of 9 answered, none flagged |
| [pot/](pot/) | anything: an empty box you throw chunks into with `pour.sh`, swirled with `swirl.sh` and its general stack; chunks are yours, not pinned | whatever you pour, kept in a folder outside the repo (`POT`) | `bash boxes/pot/pour.sh POT NAME SOURCE`, then `bash boxes/pot/swirl.sh POT` (`--ask "..."` for a one-off want); seconds | tried once: 134 files, 7 of 8 steps clean; also `survey.py POT`, one box per chunk and 27 questions, first run over the eight in [pot/results-eight/](pot/results-eight/) (read `connections.md` first) |
| [our-two-repos/](our-two-repos/) | what willow and die-namic-games already hold about a fight engine, the dice, the card promises, the deps rules; the research behind open.md's fight-engines note | willow at its pin `370f74a`, die-namic-games at `3de61d2` (.md and .py, no `boxes/`); 1,984 files | `bash boxes/our-two-repos/rebuild.sh SCRATCH`; about 1 min | 8 of 8 answered, none flagged |

Each folder: `stack.md` (the wants), `words.txt` (how readers ask), `rebuild.sh`,
`results/` (last `page.md` and step log, the machine's paths written
`<scratch>`). The words list takes one word, `=`, then words with commas
between; a word can't map to itself, even through a cycle (`gm = game master,
dm` and `dm = ...` was refused).

## Stacks, and which to ask first

- **gm-projects/stack.md** (10 wants): honesty (1–3), memory (4–5), dice and
  fights (6–8), what we may take (9–10). Ask 1, 2, 6, 7 first.
- **srd-engines/stack.md** (9 wants): can the dice come from outside (1–3), what a fight is to each (4–6), what we'd have to agree to (7–9). Ask 1, 2, 5 first.
- **our-two-repos/stack.md** (8 wants): what already covers a fight (1–3),
  what an outside engine would have to be (4–6), where it came up (7–8).

## What they said (as found, not tuned)

- **TaleWeaver** enforces rules after the model speaks: a "deterministic
  enforcement" pass, rule violations fed back into a second narration pass,
  and a test where the model falsely completes a quest
  (`docs/specs/llm_injection_spec.md`, `RELEASE_NOTES_v0.7.0-beta.md`).
- **NarrativeEngine-P** states the same split: "deterministic code decides
  *when*, LLM decides *how*" (`Example_Setup/Ruleset/Archive/Brainstorm.md`).
- **dnd_ai_dm** (Python, MIT, 65 files) injects every random choice through one
  seeded `random.Random`, so `--seed` reproduces a run
  (`docs/architecture.md:66`) and `Dice(...).d20` takes advantage. The
  smallest, and the likeliest to read and port to a stdlib add-on. Not
  checked: whether its rules match SRD 5.1.
- **TaleWeaver's dice** are seeded too (`tw.dice`, scripting_engine.md:859).
  None of the four, in these passages, has a tower or a cup: anyone holding
  the seed can foresee the roll. That is what willow's dice-tower adds.
- **Human approval**: want 3 came back thin (2 passages, API-key policy and
  prompt guidance, nothing like a seal). Read as: none of the four has a
  GM's yes the way the box does. Not proved: a thin answer is not an absence.
- **Licences**: all four LICENSE files are MIT; TaleWeaver also ships
  `LICENSE-CC-BY-NC-4.0` for its assets (`ASSETS.md`), so nothing under its
  asset folders is free to take. Want 9 only reached TaleWeaver's pages.
- **Left as found:** want 10 (a family or a child) returned a Chainsaw Man
  world file and a database plan: the projects don't say, and the words
  matched noise. Don't treat it as an answer.
- **our-two-repos**: the house holds `aetheris5e` fights, `dice-tower`, and
  game-master's `--said` real dice; the deps rules live in `adapters/deps`.
  Wants 4–6 came back noisy (CHANGELOG and ADDONS lines): ask the rules
  page directly, not the box.

- **srd-engines** (as found, from passages; nothing was built or run):
  - **dndwright** (Python, MIT, 110 files) is the one that fits our shape:
    each `DiceEngine` owns a private RNG, `DiceEngine(seed=42)` is
    reproducible, and its docs say to inject an unpredictable generator for
    live play (`src/dndwright/dice/engine.py`). Its bundled content cites
    SRD 5.2.1, CC-BY-4.0. Alpha. Not checked: how it takes faces "as said".
  - **OpenCombatEngine** (C#, MIT) has an `IDiceRoller` interface and a
    settable `Seed`; a code comment admits its attack roll uses `Random`
    (insecure). It has combat events (`docs/architecture/005-combat-events.md`)
    and JSON save and load of an encounter. The interface is the seam the
    dice tower would plug into.
  - **jurnalis-project/engine** (Rust) says it is stateless: state is JSON
    after every call and passed back (`README.md:19`), which suits the record.
    **Its README says there is no license file, all rights reserved**, though a badge
    says MIT: until it has one, don't copy from it. Ask the author.
  - **srd_5e** (Elixir, Apache-2.0, early): `Srd.Dice` is a placeholder in
    one version's docs, so its rules are content, not yet an engine.
  - Want 2 and 5 are the strongest answers; want 4 (a fight resolved) mostly
    reached class data, not the resolving code: ask the source for it.

- **The three next steps, done 2026-11-21** (full notes in
  [../open.md](../open.md), "Open records"):
  - WITNESS_INTEGRITY.md read: a structural filter (scenes no on-stage NPC
    witnessed never reach the model) and a behavioural one (facts split in the
    prompt, advice only). The structural one is the `kids` fix's shape.
  - dndwright run: `DiceEngine(rng=...)` takes a `random.Random`, so typed
    faces can drive it through a small subclass; `apply_damage` is pure; needs
    `pydantic` and `pyyaml` (a `deps` add-on).
  - Exhaustion written as `box/exhaustion.py` in both SRD editions: dndwright
    is 5.1, srd_5e is 5.2. Not wired into play (item 3 first).
- **Decided 2026-11-21: the box plays SRD 5.2.1**, 5.1 only where an engine forces it. Engine pick follows: srd_5e (5.2) and dndwright's 5.2.1 content fit; OpenCombatEngine is 5.1, so an idea to borrow, not a drop-in; jurnalis is mostly 2024 despite its 5.1 label. Still to check: what aetheris5e's fights follow.

- **Round 2 (2026-11-21), the box asked until the good questions ran out**
  (full notes in [../open.md](../open.md), "Round 2"): layforge
  (`jamesplotts/layforge`, MIT) poured as a ninth chunk; it has safety tools,
  an operator veto and knowledge scoping, so the "none of the eight" claims
  above hold for the eight only; jurnalis-engine is mostly 2024 rules despite
  its 5.1 label; OpenCombatEngine is the engine half of a host/engine split
  with a stateless gRPC contract; leads found for items 3, 4, 8, 9, 11, 16, 17.
  Ask with `ask.py`-style batches over `POT/survey/box-NAME` (about 25 s a
  question across eight chunks).

## Not done, and why

- **Tavern (t11z)**: `t11z/tavern` is refused to the session, both through
  `add_repo` and an anonymous clone. Its site says Apache-2.0, FastAPI, SRD
  5.2.1, rules in code; unconfirmed. Lay it in `gm-projects` once readable
  (add `tavern:COMMIT` to `PROJECTS` in `rebuild.sh`).
- **dndkit**: a search listed such a package, but a second search found no
  PyPI project of that name; dndwright (above) is the Python one that exists.
  Other Python leads, unread: `dnd-character` (EPL-2.0, fetches SRD data from
  an API, so it goes online), `dnd5epy` (an API client).
- **Ideas for the next boxes:** a box over the willow add-on cards alone
  (what promises each makes); one over Datasworn and the Ironsworn oracle
  tools; one over the Discord and chat GMs (samvoisin, MyGameMaster).
- Nothing was run through willow's forge add-on, and no stack was sealed.
