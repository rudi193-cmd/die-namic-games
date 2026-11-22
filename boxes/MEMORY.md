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
| [looks/](looks/) | how game pages are dressed and laid out, for Die-Namic's redesign: the other GMs' screens, our own pages, and published GM screens brought in for the art on them | the four gm-projects at the same pins (.tsx .vue .css .scss .html .md only), Die-Namic's `ui/` sources at HEAD, and GM screen art from `SCREEN_ART` (default `../screen-art`, outside git: each picture with a `.md` note; pictures read by willow's ocr when tesseract is there); 1,217 files with no screen art yet, with `my-table.md`, the maintainer's own GM side in their words, and Die-Namic's design pages | `bash boxes/looks/rebuild.sh SCRATCH`, about 10 s (the index, kept in SCRATCH, rebuilds only when the pile changed: 8 s); then `bash boxes/looks/ask.sh SCRATCH "your words" ...`, about a second | 7 wants, 24 questions, none flagged |

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

- **looks/stack.md** (2 wants, built one at a time with the maintainer, 2026-11-22):
  how each dresses its pages (1); where each puts the GM's screen, pulled-out
  pages and dice, against the maintainer's own table (2); how each sends what the GM
  shows to the others' devices (3). The next wants wait on their yes.

## What they said (as found, not tuned)

- **looks, want 1** (colours, fonts, themes): ink & bone's "Worn Grimoire"
  redesign, a parchment palette with Cormorant Garamond and three columns
  (`docs/superpowers/specs/2026-04-03-ui-redesign-design.md:8`), and
  NarrativeEngine-P's beta skin, a light "parchment" and a dark "ink" palette
  (`src/styles/beta.css:44`, `:96`). Five of the ten passages are its glyph and command
  palettes, not colours: "palette" means three things there.
- **looks: ask the index, not the box.** The kernel reads the whole pile
  for every question: 10 to 30 s each over 1,191 files, 134 s for the stack.
  From 2026-11-22 rebuild.sh lays an index with willow's `index-cache` (8 s,
  then only when a file changed) and every want is a `batch-ask` scan of its
  `questions/wantN.tsv`: the kernel's own answers, in the same order, in
  about a second (the stack, 4 s). Ask your own with `ask.sh`. The pile holds
  this file, so the box also serves back what was written here about it:
  read past a `ours/boxes/MEMORY.md` hit to the page it cites.
- **looks: ask our own pages first.** Wants 2 and 3 were first answered
  from a pile without Die-Namic's design pages, and both answers were wrong
  where open.md already said otherwise (the maintainer caught it). From
  2026-11-22 the pile holds README.md, open.md, open-gaps-from-the-boxes.md,
  box/'s and the-table's pages and this file, and each want asks several
  questions, our words and theirs.
- **looks, want 2** (the GM's side): our own design already has it.
  open.md:113, "the table hears the story and the dice; only the GM sees the
  buttons"; the GM's screen roll is willow's `dice-tower` (drop with only a
  hash on the record, out into the tray, check; open-gaps-from-the-boxes.md:56),
  and a roll hidden from the one who made it is `blind-deal`, an idea
  (open.md:537). The shared view, item 16 (open.md:467: pictures, a map, a
  handout, the dice landing where everyone can see) has nothing yet but
  `print --large` (open-gaps:135); `box/paper.py` prints the sheets in big
  type. Of the others, every layout is a player's: ink & bone's sheet and
  dice left, story centre, notes right
  (`docs/superpowers/specs/2026-04-03-ui-redesign-design.md:27`), and its
  handouts, a note the GM reveals (`…group-b-interactivity-design.md:63`), are
  the nearest to a page laid on the table; its hidden roll shows `[GM]` and
  `?` (`DiceHistoryPanel.test.tsx:81`), hidden in the page only.
- **looks, want 3** (from the GM's device to the others'): open.md's order
  for a home box starts with it (open.md:551): "the kit, and `share`… one
  command sends what the table made true to the other box, one receives it.
  Works with what is built"; then `record-sync` (planned) and `kids`. willow's
  `share`, tested across its demos, packs sealed answers for each person's
  key and checks them on receipt; it never goes online, so how a package
  travels is the GM's. None of the four game masters sends to another
  person's device; ink & bone syncs one person's windows over a WebSocket.
- **looks, want 4** (what only one seat sees; the maintainer's connection:
  blind deal is every card game): our pages already join them. open.md:580,
  "the cup and the screen roll are the same mechanism" as a dealt hand
  (`blind-deal`: each seat's share sealed to it, only its hash on the record,
  opened at the call; planned in willow). the-table deals it in the view
  today, `observe(seat)`: a seat's own hand in full, the others' as counts
  (the-table/README.md:68, :206); a Liar's Dice call lifts every cup. What
  isn't yet: the record still holds every hand open (`show` laid all four
  liar's-dice hands open, open.md:580). The GM's screen roll alone is built,
  willow's `dice-tower`.
- **looks, want 5** (the screen's three panels, in the maintainer's own
  layout). **Left, quick reference.** The bestiary is aetheris5e's stat
  blocks, which a story names as its `"foes"` (box/dw-fights.md:13;
  `story_foes`, box/play.py:876; `Fighter`, box/dw_fight.py:82); planned
  battles are those foes in the story's world file; loot is what box/carry.py
  keeps per character (a `table-carry` row each, things and wounds), with no
  pile of loot yet to come. **Centre.** The planned story is box/worlds/
  (scenes in order, the-table.js:4); active combat is box/fight.py onto the
  record and box/board.py's board, drawn from the rows ("who's hurt, who's
  down, whose turn", board.py:1), today only at a fight's end (open.md:467).
  **Right, the players.** The sheets: carry.py's rows, `s` at a roll
  (play.py:634), and box/paper.py's big-type page, one card a character
  (paper.py:5). Of the others: ink & bone's bestiary is an uploaded rulebook
  for its model (README.md:485); NarrativeEngine-P lays a combat strip,
  board and story side by side (combatScreen.test.tsx:158).
- **looks, want 6** (a quick lookup of whatever turns up: the rules, the
  books, on demand). The binder is already asked: a table's pile is "the
  GM's notes, monsters, people, session notes and house rules… what the GM
  asks" (box/open_table.py:13); `box/ask.py` points at where to look in it
  (willow's pile-rank; README.md:92), `kernel.py bite` answers from it
  (box/README.md:69), and sealed house rules come back word for word
  (`rules.py ask`, box/README.md:77). The rules in the repository are
  game-lab/rules/COMPENDIUM.md. Not yet: the books, a rulebook as a PDF,
  which willow's `pdf` add-on reads into the pile; and speed. Timed on this
  box's 57,000 passages: the kernel's rank kept running in `pile-serve`
  answers in 9.6 s, pile-rank there in 0.13 s, and batch-ask over an
  index-cache index, the kernel's own answers, in about a second.
  Decided by the maintainer: the lookup lives in the left panel and comes
  into the centre when called (my-table.md).
- **looks, want 7** (pictures the table makes: a creature's, a kid's own
  drawing). tesseract is on the table already: a table laid by
  open_table.py has `scans/` (box/open_table.py:114), and the end of the
  night's first want reads the GM's handwritten pages from it into
  `pile/scanned` with willow's `ocr` (box/gm-end.md:12; "OCR guesses: the
  binder cites the line tesseract read"). A drawing brought in by a player
  is an `offer`: something brought to the table as their character, handed
  to the GM, canon that night only on the GM's seal (box/README.md:235).
  `kids` (an idea) is the seat that asks and never seals (open.md:530). Not
  yet: a picture kept as a picture (the pile and the kernel read only its
  words), a drawing read during the night rather than at its end, and a
  page that shows it; ink & bone keeps a portrait per character, an 80px
  circle uploaded from the sheet (README.md:326).

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

- **Round 3 (2026-11-21):** layforge's gate is code that fails closed, its log
  is append-only with sequence numbers but no chain or signature; OpenCombatEngine
  rolls its own dice and its gRPC contract has no way to pass faces in (dndwright
  has); layforge never names an SRD, its engine decides. Notes in open.md,
  "Round 3"; survey in [pot/results-layforge/](pot/results-layforge/).

- **Round 4 (2026-11-21), read in the source:** dndwright's combat types carry
  no identity, so the story's characters can be fought (run: initiative with
  `manual_roll`, typed attack and damage); its weapons are 2024 (Weapon
  Mastery), so it is a 5.2.1 fit; layforge's gate is one switch of about 45
  tools with reason codes on refusal. Notes in open.md, "Round 4".

- **Round 5:** dndwright's sheet graph needs 5e ability scores, ours are
  bonuses on a story's own stats, so no fit for sheets; a fight only needs
  plain numbers (modifiers, AC, hit points), which aetheris5e's stat blocks
  already are. Decision waiting: a spike adapter, or leave aetheris5e as is.

- **Round 6, the spike:** `spikes/dndwright/` runs a fight on story characters
  with dndwright on supplied faces, every blow a row, replay finds an edit;
  7 tests. Next: faces from the tower. Wider suite: 23 fight-test failures
  here from a missing `ONESCRIPT_HOME`, not from the spike.

- **Round 7, the tower is wired into the spike:** `spikes/dndwright/tower_faces.py`;
  a fight's every face is a die dropped and brought out, the rows are held to the
  tower's outs; 12 spike tests. Window between drop and out is an instant.
  Next: fight rows on the kernel's record, stats to `Fighter` numbers.

- **Round 8 (2026-11-22), the two next steps done in the spike:** fight rows on
  the kernel's record (`xfight-*`, checked from the record alone, a real run
  was 26 tower dice and 21 rows) and story characters and stat blocks as
  Fighters (defaults made up, overridable per character); 23 tests. Still
  spike-only; nothing in box/ calls it.

- **Round 9 (2026-11-22), wired:** the spike moved to `box/dw_*.py` and is on the
  play path, off unless a story names `"foes"` and dndwright is installed; the
  record, recap and `open_table.py check` read it; 30 new tests; whole suite 23
  failed (the missing `ONESCRIPT_HOME`, as before) and 287 passed. See
  `box/dw-fights.md`.

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
