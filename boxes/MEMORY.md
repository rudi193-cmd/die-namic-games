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
| [our-two-repos/](our-two-repos/) | what willow and die-namic-games already hold about a fight engine, the dice, the card promises, the deps rules; the research behind open.md's fight-engines note | willow at its pin `370f74a`, die-namic-games at `3de61d2` (.md and .py, no `boxes/`); 1,984 files | `bash boxes/our-two-repos/rebuild.sh SCRATCH`; about 1 min | 8 of 8 answered, none flagged |

Each folder: `stack.md` (the wants), `words.txt` (how readers ask), `rebuild.sh`,
`results/` (last `page.md` and step log, the machine's paths written
`<scratch>`). The words list takes one word, `=`, then words with commas
between; a word can't map to itself, even through a cycle (`gm = game master,
dm` and `dm = ...` was refused).

## Stacks, and which to ask first

- **gm-projects/stack.md** (10 wants): honesty (1–3), memory (4–5), dice and
  fights (6–8), what we may take (9–10). Ask 1, 2, 6, 7 first.
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

## Not done, and why

- **Tavern (t11z)**: `t11z/tavern` is refused to the session, both through
  `add_repo` and an anonymous clone. Its site says Apache-2.0, FastAPI, SRD
  5.2.1, rules in code; unconfirmed. Lay it in `gm-projects` once readable
  (add `tavern:COMMIT` to `PROJECTS` in `rebuild.sh`).
- **The three SRD fight engines of open.md** (OpenCombatEngine C#,
  srd_5e Elixir, jurnalis Rust): not cloned, so no box over them. A box over
  their READMEs and rules is the next one to lay, with a stack asking how each
  rolls dice and whether it is deterministic.
- **dndkit** (a PyPI package a search surfaced): unread; the one pure-Python
  SRD library lead. Check first.
- Nothing was run through willow's forge add-on, and no stack was sealed.
