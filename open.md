# Opening Die-Namic

How Die-Namic should open for someone who has never seen any of it: a parent,
a teacher, a kid at the table, someone who has never typed a command. This is
the design, talked through on 2026-11-20.

**Built so far:** the play path, in a plain terminal: `python box/play.py`
opens on the stories with no setup, offers The Lantern Fair when nothing has
been played, plays it with rolls and "Your call, GM" in these words, ends the
night with a note and the GM's yes, and opens next time on "Previously on..."
and the GM's own note. And the writing path, in a plain terminal:
`python box/write.py`, or "Write your own" from play: what it's about (or an
idea dealt from the box's words), four small boxes, the moments in plain
words, written as the one story file author.py reads, then played. A blank
outcome is the GM's moment: the box rolls, asks "GM, what happens?", and
what the GM types and says yes to is kept as the rule of the table (an offer
of the GM's word, sealed on that yes), read aloud next time as canon. And "Write
what happens next", offered at the end of a night whose calls were
answered: the next part keeps its people and place, shows what the table
made true and said no to, and each moment can wait on a yes or a no from
last time. And the heads-up: before the GM decides a call, or keeps their
own word, what the table already holds true about the same thing is shown,
with mine stands now, keep the old one, both are true (and, for the GM's own
word, let me reword it). And the table's turn before each roll: every roll
waits for "Enter: roll", where o is someone bringing something into the
story as their character (the GM asked first, the heads-up too, and only then
handed in), and f, in a story fights belong to (Aetheris), a fight from
aetheris5e played onto the record.
Everything else on this page is still to build.

## Why

Willow's governance is done and it holds: the record, the seal, the key that
is only the person's, the machine that proposes and never decides. The next
proof is that all of it can work **without being seen**, so that anyone can
take a stack from willow and make it theirs.

Willow's demos already show many stacks doing many things over one kernel
and one law. Die-Namic should be the one that is **easiest to walk into**: a
game is something anyone can sit down to, at any age. If the most
approachable stack runs the full governance underneath, unchanged, no stack
has a reason to be hard to walk into.

**The test for every change:** can someone who has never seen this sit down
and play a night without help?

## The rule underneath

The governance stays exactly as strict. Only its words and its doors change.

- Nothing is true at the table until the game master says so.
- A player, a script or a model may suggest; only the GM's yes makes it so.
- Every roll is honest, every night can be checked, and nothing can be
  changed after the fact.
- Nothing about the people at the table is written down. The seats are the
  story's characters.

What the GM sees is table language. What the record keeps is the seal, signed
with the GM's key, as it is now.

## The words

| Under the hood | At the table |
|---|---|
| a proposal waiting on the seal | **your call** |
| seal | **yes, it's true** |
| decline | **no, it didn't happen** |
| sealed canon | **what your table made true** |
| session seal | **end of the night: that's our night** |
| `proposal:069360c5…` (a hash) | a button, or a short name |
| beat | a moment |
| action beat | someone tries something |
| decision beat | a question for the GM |
| strong / weak / miss | it goes great / it sort of works / it goes wrong |
| `when:` | only if… |
| seated | someone at the table plays them |
| stats | what your heroes are good at |

"Suggested" and "your call" keep the one thing that matters: the GM decides.
Words like "saved" or "accepted" would blur it, and are not used.

The kernel's own names (seal, proposal, row, the record) stay where they are:
in the kernel, the record, willow's law and the code. They are precise, and
the law rests on them.

## The first five minutes

No setup questions. Opening Die-Namic goes straight to a story.

**If the GM has stories** (their own, or ones played before):

> **Pick up where you left off**
> 🏮 The Lantern Fair: last played Thursday · *Previously on…*
> ⚙️ The Clockwork Cellar
> ✏️ Write a new one

**If there are none:**

> **Let's start a story.**
> 🏮 **Try this one:** *The Lantern Fair*, a night market and a missing light.
> Short and gentle, good for a first night. **[ Play it ]**
> *Or pick another:* ⚙️ The Clockwork Cellar · 🌊 Aetheris · 🐝 The Wasp Nest
> ✏️ **Write your own:** a few lines is enough to start

One tap and they are playing. Without asking:

- The box sets itself up the first time a story is opened: the record, the
  key (kept outside the box), the binder.
- The table is named for itself (the date, or the story); it can be renamed
  later.
- The house rules wait in a "for later" pile and never block a first game.

**Playing.** The table hears the story and the dice; only the GM sees the
buttons.

> 🎲 **Juno tries Wit**: rolled 12. **Great!**
> *She finds the nest, and every spring is woven into it like straw.*
>
> ✋ **Your call, GM:** *Old Vell's lamp is in the nest, and it's still lit.*
> Is that true in your world?
> **[ Yes, it's true ]**  **[ No, it didn't happen ]**

**Ending the night.**

> 🌙 **End of the night**
> Tonight, your table made true:
> • Old Vell's lamp is in the nest, still lit.
> • Cogwen is building a clockwork friend.
> Anything to remember for next time? → *Brann wants to bring a friend*
> **[ That's our night ✓ ]**
> *Saved and checked: nothing can be changed after the fact.*

That one button is the session seal. The note goes into the binder, so the
next night's recap finds it.

**Next time, the first thing they see:**

> **Previously on…** *(read this out loud)*: Old Vell's lamp is in the nest,
> still lit…
> **Just for you, GM:** Brann wants to bring a friend.

Kept out of the first five minutes on purpose: 5e stats, house rules, the
kernel, stories from files. All of it stays one step in, there when wanted.
Fights and offers are one keypress in: at each roll, "o" brings something
in and "f" starts a fight, in a story fights belong to; Enter just rolls.

## Writing a story

Writing a story is the same move as playing one: the helper suggests, the
writer decides. The writer is the GM of their own story.

**1. What's it about?** One line, or none.

> What's it about? → *"a kid who finds a dragon egg in the school garden"*
> *Stuck? Try one of these:* 🥚 something hatches · 🗝️ a door that wasn't
> there yesterday · 🎪 the fair comes to town

The ideas are dealt from the box's own words. **Model suggestions are off**
unless the writer asks for them.

**2. Four small boxes.**

> **What's it called?** → *The Garden Egg*
> **Where does it happen?** → *the school garden*
> **Who's in it?** → *Mira, a kid who likes bugs* · *[ + someone else ]*
> (each: ☐ someone at the table plays them · ☐ the GM plays them)
> **What are your heroes good at?** → *Brave, Clever, Kind* (filled in;
> change them if you like)

The ids are made from the names. Nobody types `old-vell`.

**3. What happens?** One moment at a time, two kinds:

> 🎲 **Someone tries something.** Who? → *Mira* · What? → *She picks up the
> egg.* · Using? → *Kind*
> **If it goes great:** *It's warm, and something inside taps back.*
> **If it sort of works:** *It's warm, and it cracks a little. Uh oh.*
> **If it goes wrong:** *The groundskeeper sees her.*
> *(Leave one blank and the GM makes it up on the night.)*

> ❓ **A question for the GM.** *Is the egg a real dragon?* → if yes:
> *"The egg is a real dragon's."*

**[ + another moment ]**  **[ + only if… ]**

**4. Play it.** The button lights up as soon as there is a title, a place,
one character someone plays, and one moment. Everything else has a default.
A story is never refused with a line number here; what's missing is said
where it is: *"This moment needs what happens if it goes wrong, or leave it
for the GM."*

**5. The story grows from play.**

> 🌱 **Your story grew.** Tonight your table made true: *the egg is a real
> dragon's.* **[ Write what happens next ]**

**Three doors, one story file:**

| Who | Door | What it is |
|---|---|---|
| a first-timer, a kid, a parent | the boxes and moments above | a form that writes the story format |
| someone who likes typing | a plain text file in the story format | `box/author.py` |
| a serious writer | story-timeline, the SAFE App Store's writer's workbench | its `export-story` feeds author.py; `import-canon` brings play back |

## The GM's moments

**A blank outcome is fine.** The box rolls, says how it went, and hands the
moment to the GM:

> 🎲 **Mira tries Kind**: rolled 8. **It sort of works.**
> ✋ **GM, what happens?** *(say it, or type a line)*

The roll still matters: it gives the GM something to build on. This is the
thesis from ai-game-master: the machine carries the dice and the memory, the
person does the part that was worth doing.

**What the GM types and says yes to is the rule of the table at that
moment.** It is canon, dated, on the record.

## When the GM's word meets an earlier one

The GM's word is the word, so two true things can meet: "Old Vell's lamp is
lost" on one night, "Old Vell never had a lamp" on another. Each was true
when it was said.

The heads-up comes **in the moment, before the GM decides**, so the decision
is an informed one:

> ✋ **GM, what happens?** → *"Old Vell never had a lamp. It was always
> Cogwen's."*
> 💡 **Before you decide:** on Nov 14 your table made this true:
> *"Old Vell's lost lamp is in the nest, and it's still lit."*
> **[ Mine stands now ]** · **[ Keep the old one ]** · **[ Both are true ]**
> · **[ Let me reword it ]**

- **Mine stands now:** the new word is the rule from tonight; the old one is
  kept, marked as replaced. Nothing is erased.
- **Keep the old one:** the new line is dropped, and play goes on.
- **Both are true:** they don't clash after all; the pair isn't raised
  again.
- **Let me reword it:** the GM makes it fit.

Only the GM sees it. The machine never picks a side. The recap reads aloud
only what stands now, and shows the GM what was replaced, and when.

It has to be right most of the time, or GMs will learn to click past it. So
it is not a new search: it is the house's own. **Corrected on 2026-11-20,
when it was built:** this page first named Jeles's `conflict_scan` for it.
That is a web search: it looks for two independent sources online that
refute a claim, and a table's story never leaves the box. The heads-up uses
willow's `contradictions` rule instead, read from the box's own record: two
lines are about the same thing when they share at least two of their own
words, and at least half of the shorter one's. It cannot tell agreeing from
disagreeing, and needn't: it only asks, and "both are true" is there for
the pair that agrees. The same words made true again (a story played
again), and a pair the GM already called both true, are never raised.

## The dice

Found on 2026-11-20: every roll today is seeded by the hash of the row before
it, and that hash is public the moment the row is written. Read from the
record alone, the next d20 was predicted as a 20, and rolled a 20. No roll
can be forged after the fact, but three doors are open:

- **Prediction:** anyone with the record knows the next roll before it is
  thrown.
- **Steering the GM's call:** yes and no write different rows, so they lead
  to different next rolls. A GM who looks ahead could decide by the dice,
  not by the story.
- **Shopping for a roll:** anyone who can add a harmless row first (an ask,
  an offer, a note) changes the next roll.

Thought through as a real table and a real writing session use dice, there
are two kinds.

**At the table** the die is thrown after the decision, in the open: before it
lands nobody knows it, the GM included, and everyone sees it land. A reroll
costs something (inspiration, a luck point) and is an event of its own. Table
dice are **unknown until thrown, thrown after the decision, seen by all, and
kept.**

**In a writing session** (the tables in the DMG, solo journaling, oracles)
dice are prompts: nobody is an opponent, rerolling is fine, and the same roll
again is a feature ("roll 37 on the tavern table"; a class working from the
same draw). Prompt dice are **surprising, free to reroll, and repeatable.**
Seeding as it is today suits them; `box/ideas.py` and `daily-word` already
work this way.

| | Table dice (stakes) | Prompt dice (writing, ideas) |
|---|---|---|
| could be gamed by | anyone with the record; the GM's call | no one: there is nothing to win |
| thrown | after the decision, unknown until then | whenever the writer likes |
| reroll | only as a visible, kept event | freely |
| repeatable | checkable after, never foreseeable | yes, by seed |
| how | **the cup**: committed when the moment is posed, revealed when thrown | seeded, as now |

**The cup.** When a moment is posed ("Mira tries to climb"), the box shakes
the die and sets the cup down: a commitment on the record, the hash of a
fresh secret. Nobody can see under it, the GM included. After the GM's call,
the cup is lifted: the roll is the record's tip and that secret, the secret
is shown, and the check holds it to the commitment made before the decision,
then plays the roll again as it does now. Nobody sees ahead, no call can be
steered by the dice, no row can shop for a roll, and every roll is still
checked after the fact.

At the table, in its own words:

> 🥤 **The die is in the cup.**
> ✋ **Your call, GM:** *Old Vell's lamp is in the nest, still lit?*
> **[ Yes, it's true ]**
> 🎲 **Lift the cup:** Juno rolled 12. **Great!**

**Later:** the GM's screen roll, a roll only the GM sees. (The GM's word
over the dice ("the dice said miss; I say she makes it") is built: a kept
call of its own, never a roll quietly changed.)

Table dice are willow's (`play-dice`, the seeding in `game-master`,
`play-dice5e`) and the one-script's, so the cup is a change in willow, not
here; `box/fight.py` seeds the same way and follows it. aetheris5e's
`gm5e.py` already chose fresh randomness for live rolls ("the ledger is the
honesty guarantee, not reproducibility"); the cup keeps that, and keeps the
check too.

## What it builds on

Most of this is already in the house. Before building any of it, look here
first.

| Need | Already there |
|---|---|
| the box, the record, the story, the rolls, the recap, the canon | `box/` (open_table, session, author, ideas, fight) and willow's game-master |
| approve with a click, signed with the GM's key, on their own machine | willow's `browse` |
| set up in one step | willow's `first-run` |
| a note for next time into the binder | willow's `capture` |
| ideas when stuck, from the box's own words | `box/ideas.py`, willow's `oracle-text` and `random-passage` |
| the newer word stands after the older, both kept | willow's `decisions` (`--replaces`) |
| two lines that disagree, neither side picked | willow's `contradictions` (dates and amounts), and newer willow's `kept-clash` |
| two lines about the same thing, read offline | willow's `contradictions` (`subject`, `same`), pinned; used by `box/clash.py` |
| a story written by a serious writer, and play brought back to it | story-timeline's `export-story` and `import-canon` |
| what was promised, owed, lent and still open | willow's `debts`, `lending`, `minutes`, `digest` |

## What is missing

- **A front door in the browser:** the game-shaped page with the buttons
  above, most likely `browse` with a Die-Namic front page. The plain-terminal
  version, in the same words, is built: `box/play.py`.
- **The writing form in the browser.** The terminal version is built:
  `box/write.py`.
- **The cup:** table dice committed when the moment is posed and revealed
  after the GM's call, in willow's dice, and in `box/fight.py` after them.

## What a real table does that isn't in yet

Gathered on 2026-11-20, after a whole journey was played end to end on a
fresh box (three nights: a story written and played, what happens next with
the heads-up, Aetheris with a fight) and held against how people actually
play. *(Underneath)* marks what willow or the box can already do, not yet
reached from the play path.

**At the roll**

1. **Players rolling their own dice.** At a real table a kid throws a real
   d6 and says the number. There is no way to type in a physical roll, and
   for the youngest players it matters most. Its honesty is the table
   watching, not a seed: a roll typed in is kept as said, and as such.
   **Built:** type the two dice at the roll ("4 6"); willow's play-dice
   `said` keeps them, marked "(your dice)", and game-master's check holds
   them as said.
2. **The player choosing how.** Aetheris says "Declare how you meet it",
   but the story fixes the stat. Letting the player say "I talk my way
   through" is how most tables play. *(Underneath: game-master's `act`
   takes any stat.)*
   **Built:** h at a roll, the menu the-table's `menu.py` makes of legal
   moves, shown to a person: each of the story's stats with the
   character's bonus and its exact chances, the story's way first.
3. **Helping, and paying for a reroll.** "I hold the ladder for her" as +1;
   a luck point spent to throw again, kept as its own event. *(Not here: game-master's check holds a beat's total to the roll
   plus the stat, so a +1 for help is a willow change first.)*
4. **The cup, the screen roll, and the GM's word over the dice:** in The
   dice, above. **The cup is built:** every moment's dice go into willow's
   dice-tower when the moment is posed and come out on the roll, so no
   call or row can steer them and nobody reads them first. Not yet: the
   GM's screen roll. **The GM's word over the dice is built:** g at the
   next roll prompt, over the roll just read, is kept as a `gm-word` call of
   its own (sealed on the GM's yes; said aloud only in a story with no
   gm-word), and the roll and its beat are never edited; over a fight, a
   call on how it stands, against the dice, is kept beside it (10).

**The characters**

5. **What happens to them carries over.** Sena falls in every fight and is
   whole the next moment; the writ lost to the black water is never lost.
   Wounds, things carried and spent strength have to last, between moments
   and between nights. *(Underneath, in part: willow's `debts`, `lending`,
   `log-kit`.)*
   **Built, for things and wounds:** after s, the GM writes on a sheet in
   plain words ("Tamsin finds a rope", "Oro uses the rope", "Oro is hurt
   by a club", "Oro is healed"), box/carry.py: each a row, nothing taken
   off the record, so it lasts between nights, and the opening screen
   reads what carried over aloud. Read as willow's `lending` reads a loan
   (every line stays; a return listed under it) and `livestock` an
   animal's treatments. Not yet: a wound that changes a roll, and spent
   strength. *(2026-11-21: the rule for one wound, exhaustion, is written as
   a pure module, `box/exhaustion.py`, in both SRD editions; it is not wired
   into a roll, because that is item 3's willow change first. See "Open
   records" at the bottom.)*
6. **Who is at the table.** One player or five; a friend for one night;
   someone leaving. The seats are fixed by the story, and every fight brings
   the same three.
7. **A sheet the player can see:** what their hero is good at, carries, and
   has been through. **Built:** s at any roll shows each seated
   character's sheet, what they're good at (the bonus a roll adds), what they
   carry and how they're hurt, kept apart from the rest (box/carry.py), and
   the last three things the table made true about them or they brought in,
   still standing. On paper: `open_table.py sheets --to FILE.html` writes
   them as one page in big, high-contrast type (box/paper.py). Willow's
   `print --large` is for an answer with its sources and writes to the
   record, so it doesn't fit a sheet.
8. **Growing:** getting better at things over the nights, and rewards.

**The story**

9. **The GM making up a scene.** Kids go where the story never planned. A
   story is its scenes in order; the GM can say one line (a blank moment),
   not open a new place or moment.
10. **Fights that change the story.** Won or lost, the next moment is the
    same. *(Nearest so far: a blank moment, and the GM's word.)* **Built:** a
    moment can be written "when: the fight is won" (or lost); after a fight
    the GM is asked whether it stands that the party won, and that call,
    sealed or declined as an offer of the kind `fight` (game-master's own
    `offered`), picks the moment that follows. write.py asks for it in plain
    words too: after the first moment, "Only if the heroes win a fight" or
    "lose a fight", written as the `when:` lines above.
11. **Time pressing:** the tide rising, the fair closing at midnight, a
    count the table can see.
12. **A replaced truth no longer unlocking.** Found in the journey: "Mira
    feeds the hatchling" (only if the egg is a real dragon's) played after
    the egg was made a painted stone. game-master's "only if" reads the
    first seal and knows nothing of the replacement; the fix is in willow.

**The people**

13. **Safety, first of all at a kids' table.** Agreeing beforehand what is
    off the table, and a way to stop a scene with no reason asked (lines
    and veils; the X-card). **Built, without a setup question:** x at any
    roll sets the part aside, the dice still roll and the GM says what
    happens instead, and the record keeps only that it was (no one named,
    no reason). Lines and veils are a page the family writes once,
    `pile/our-lines.md` (box/safety.py): a part that touches a line is never
    read; a veil's happens off-screen. **Also built:** p at a roll, a call or a
    GM's moment pauses the whole night (no reason asked; a `table-pause`
    row, no one named; run it again to pick up), and x works at a GM's call
    (nothing is decided, the call waits) and a GM's moment (nothing kept,
    the story goes on). Not yet: a call skipped for good, which needs
    game-master (willow) to settle a call without a yes or no.
14. **Undoing a slip.** A "y" pressed by mistake can only be turned back
    by a later "mine stands now". **Built, on that shape:** u at a roll
    takes back the last yes made tonight, on the GM's y: a replacement
    whose new word is nothing, sealed, so the yes stays on the record and
    no longer stands (as willow's `decisions` keeps a replaced row). Not
    yet: a "no" pressed by mistake (bring it in again with o), and a slip
    from an earlier night.
15. **Sharing the GM's chair:** a co-GM, or a kid running a night.

**What the table sees**

16. **The shared view:** pictures, a map, a handout, the dice landing where
    everyone can see. That is the browser door.
17. **A board in a fight:** who's hurt, who's stunned, whose turn. **Built:**
    box/board.py draws a fight from its rows alone, at its end (after
    every fight in play) or at any round (`fight.py board --round N`):
    each fighter's hit points as a bar, who's down, stunned or blinded,
    and whose turn is next. Not yet: a map of where they stand.
18. **Last night's fight on the opening screen.** Found in the journey: the
    recap says "Fights last time", but the screen the GM opens on doesn't.
    **Built:** the opening screen tells the GM how each of last night's
    fights ended, for their eyes only.

**First, for a family table:** 1 (real dice typed in), 13 (safety) and 5
(what carries over). They decide most whether a room of kids can play it,
and 5 is what makes a fight mean something.

## A home box, in two places, for many families

Talked through on 2026-11-20: the GM's own box at home, played from two
places (a parent away for the night, the kids at home), and made so that
lots of families in lots of places can take it up in their own ways. Read
off willow's cards (what is built, with its promises) and its ideas
(`adapters/planned.json`, the 228 waiting under willow issue #85, and the
one-script's IDEAS.md).

**The key stays the GM's.** A home box is laid on the GM's own machine, where
its key is made and stays. Laid anywhere else (a cloud session, a borrowed
machine) the key would be that machine's. So a home box comes as a kit the
GM runs at home: their stories, their binder, and one script that lays the
box with their key. Only characters go in; nothing about the people at the
table, and nothing of the family's in any repository.

Nothing below goes online on its own. What is shared travels the way a
family already moves things: email, a USB stick, a chat message, a synced
folder.

### Built: the cards that share today

| Card | For a home box |
|---|---|
| `share` | the night's sealed canon sent from one box to the other, signed, checkable by them; each hop a row on both records; never the folder, never the key |
| `many-boxes` | one page across both homes' boxes, every line cited to the box it came from |
| `diverge` | where two copies part, to the first row |
| `tip-pin` | where a record ends, written where the box can't reach |
| `backup`, `restore-drill`, `three-two-one` | copies that are checked, that restore, three of them, one away from home |
| `words-es`, `-fr`, `-de`, `-pt` and ten more; `accents`; `translate` (a local model, held until sealed) | families in other languages |
| `print --large`, `reading-level`, `nicknames` | sheets and recaps for kids and grandparents; a story a seven-year-old can read; "the dragon" finds the dragonborn |
| `braille` | recaps for a player who reads braille |
| `wake-gate` | asking out loud, nothing before the wake word kept |
| `browse`, `launcher` | the GM's yes with a click, on their own machine |
| `static-search`, `rss-out`, `calendar-out` | the story so far as a page with its own search, a feed, game night on the calendar |
| `stack-share`, `first-run`, `starter-words` | a family's stack written out for another family; a box in one step |
| `noised-count`, `secure-sum` | totals across families ("how many tables let Bill in?") with no one family's number knowable |

Left out on purpose: `snapshot` (it fetches the web) and `mcp` (an
assistant's reach into the box), unless a family chooses them.

### Ideas: the add-ons that make it a family's own

Each is a willow add-on to build (willow #85: a draft pull request that
names it, its card and its promises, its tests), then pinned here like any
other, so every family's stack can use it, not only this box.

| Idea | What it says | For a home box |
|---|---|---|
| `family-box` | one box for a household: each person's own seal, and every answer showing whose | the GM's seal and a co-GM's, in one box |
| `kids` | a box for a child: answers only from the folder chosen for them, and nothing they can approve | the kids ask "what are my character's stats?"; they never seal |
| `record-sync` | the record on two devices through any synced folder, the chain checked on each before it's trusted | two places, literally |
| `grant` | someone else allowed to ask part of the folder, passed on only narrower, never the seal key | the other home, or a friend's family, reading the canon |
| `witness` | a second person's seal beside yours, for answers that need two to agree | sharing the GM's chair; the big rulings both parents make |
| `blind-deal` | cards or dice only one seat can read, each share sealed to it, its hash on the record, opened when the hand ends | **the cup, and the GM's screen roll** (The dice, above) |
| `beacon` | draws seeded by a public randomness beacon (drand) | the cup's online twin, for a table that opts in: dice nobody, GM included, could see ahead |
| `play-fight5e` | tabletop combat from stat blocks on dice5e's rolls, every attack on the record | what box/fight.py and aetheris5e do, as an add-on: the kids' own stat blocks at any table |
| `lore` | a world's facts sealed one at a time, a story checked against its canon | the valley's canon; the heads-up's home in willow |
| `sheet-drift` | a character's numbers differing between two notes, side by side | the kids' sheets across nights and two homes |
| `table` | one way to sit at any game: whose seat, the moves it may make, one move | who is at the table; joining and leaving |
| `ink-story` | a branching ink story, every choice made for you from a seed on the record | stories bigger than scenes in order |
| `speak`, `dictate` | answers read aloud; asking out loud | kids who can't read or type yet; "previously on" read by the box |
| `kiosk` | a shared machine in a library or classroom: one box, ask only, nobody's key on it | a school club's table |
| `paper-key` | the key printed as words on paper, typed back to restore | the GM's key kept safe where a family can't lose it |
| `tatoeba` | a question in one language finding the same idea in another | families across languages |

### The order, for a home box

1. **The kit, and `share`:** a home box laid on the GM's machine with their
   stories and binder; after a night, one command sends what the table made
   true to the other box, one receives it. Works with what is built.
2. **`record-sync` and `kids`:** one record on two devices, checked on
   each; and the kids' own seat, that asks and never seals.
3. **`blind-deal` and `witness`:** the cup and the screen roll; and a second
   seal for the rulings two people make.

### What a stupid night at home showed

On 2026-11-20 a home kit was laid on a throwaway box and everything was
piled onto one evening: liar's dice, the daily word, tarot, a horoscope and
the quiz before dinner; a rules argument settled by sealing two games
mid-argument; a story night with a guest brought in, a fight asked for
where none belonged, a wrong key pressed, and the GM's own word clashing
with a truth made twenty minutes before; fights; checkers; the night's
canon sent to a second house with `share`; the next morning's recap. The
demo GM sealed; the box and its key were deleted after.

**What held, unchanged:** the heads-up inside one night, a truth replaced
and the recap reading only what stands, `share` between two houses (sent,
received, holds), rules sealed and asked word for word, every game played
again from the record, and the chain (102 rows, 7 sealed).

**What the night showed, and the shape each idea takes from it:**

| Idea | What happened | Its shape |
|---|---|---|
| `kids` | A child's question, "how does it end?", was answered from `gm-only/`, the campaign's secret act, word for word. The daily word and the quiz draw from the same pile. | **Buildable on what exists:** a second box over the binder's folders without `gm-only/` (`kernel.py init --from NAME=FOLDER ...`), with a key that seals nothing. Tried: nothing secret came back, and the rules still answered. The add-on lays that box for the family, and points the games that draw from a pile at it. **First, because it's the one that leaked.** |
| `blind-deal` | `show` laid all four liar's-dice hands open: everyone saw everyone's dice. | Each seat's dice sealed to that seat, only their hash on the record, opened at the call. The cup and the screen roll are the same mechanism. |
| `table` | Characters bid and called; the record says north and east. No game knows who is at the table. | One map from a story's characters to a game's seats, used by every game. |
| `record-sync` | The other house received the canon and it checks, but its own play screen doesn't show it: it came as rows, not "previously on". | What another house made true joins the recap, each line saying which house. |
| `sheet-drift` | Two characters with one name (a kid's own and a hero card's) and different numbers: the box serves one and never says there is another. | Two sheets of one name, side by side for the GM; neither picked. |
| `play-fight5e` | The kids' fights ran from a script beside the box, not from their binder pages. | A fight read from the binder's own pages (a character, a monster), every blow on the record. |
| `witness` | Not reached: the night had one GM. | Two seals where today there's one, for the rulings two people make. |

## Decided

- No setup questions: straight to picking a story; a suggested one, or write
  your own, when there are none.
- Writing: four small boxes, moments in plain words, heroes good at **Brave,
  Clever, Kind** by default.
- Model suggestions **off** unless the writer asks.
- A **blank outcome is fine:** the box rolls, the GM says what happens.
- What the GM types and says yes to **is the rule of the table** at that
  moment.
- An earlier word that clashes is raised **in the moment, before the GM
  decides**, with four choices; only the GM sees it, and the machine never
  picks.
- The governance stays exactly as strict underneath; it is worded as "your
  call" on the surface.
- **Two kinds of dice.** Table dice go in **the cup**: unknown until thrown,
  thrown after the GM's call, seen by all, kept. Prompt dice stay seeded:
  surprising, free to reroll, repeatable.
- **The box plays SRD 5.2.1** (decided 2026-11-21, the maintainer agreeing
  to the recommendation). New rules and content come from 5.2.1, CC-BY-4.0:
  any content taken carries the attribution Wizards of the Coast asks for
  ("This work includes material from the System Reference Document 5.2.1 ...
  licensed under CC-BY-4.0"; read the exact wording from the SRD itself).
  SRD 5.1 is used only where an engine forces it, named as such, never mixed
  in one stat block. Nothing already built declares an edition; aetheris5e
  names none, so what it plays is still to be checked against 5.2.1.
- The GM's screen roll comes **later**. The GM's word over the dice is
  built (g at the next roll).

## Note: other people's SRD 5.1 fight engines (research, not a plan)

Added from a web search on 2026-11-21, to read and decide on later. Nothing
below has been opened, run or checked: the licences and activity come from
search snippets only, so check each repo's LICENSE and history first.

The idea: the box's fights today are aetheris5e's (`f`, `box/fight.py`). Other
open projects implement the same SRD 5.1 d20 rules. The interest is
engineering: the kernel's record and seal could stand over any of them, each a
swappable rules engine whose every blow lands on the record, and none of them
the authority. Not as the kernel works today; that is the open part.

| Project | Language | Licence (per search) | Note |
|---|---|---|---|
| [OpenCombatEngine](https://github.com/jamesplotts/opencombatengine) | C# / .NET 8 | MIT | Interface-driven combat engine, SRD 5.1. Closest match. |
| [srd_5e](https://hex.pm/packages/srd_5e/0.2.0/files) | Elixir | Apache-2.0 | Newer releases model SRD 5.2 by default, with 5.1 rules as opt-ins. |
| [jurnalis-project/engine](https://awesome.ecosyste.ms/projects/github.com%2Fjurnalis-project%2Fengine) | Rust | not shown | Stateless, deterministic text CRPG engine, SRD 5.1 (d20). Licence unknown: read LICENSE before anything else. |

Left out on purpose: [libsrd5](https://github.com/kupka/libsrd5) (C#, AGPL).

Questions to settle before building anything:

- None is Python, and willow's stdlib add-ons need nothing beyond Python. A
  deps add-on would need a pinned install and a licence on its card; a run
  of a foreign binary would need a `network:`-style line of its own. Or the
  rules are read and rewritten in Python, with credit.
- A deterministic, stateless engine (the Rust one says it is) fits the record
  best: the same inputs give the same blow, so a seal can be checked again.
- The dice must still come out of the tower, not from the engine's own
  generator (see "The dice").
- How this sits beside aetheris5e's fights, and the open point that the
  fight is fought by its own party, not the story's characters.

## Open records: the survey of the eight, against what is open and built

*A living section: update it, don't rewrite it. First written 2026-11-21 from
[boxes/pot/results-eight/](boxes/pot/results-eight/) (eight open GM projects
and rules engines, 27 questions each; hits are evidence to read, not proof) and
[boxes/MEMORY.md](boxes/MEMORY.md), its twin.*

**Built here, and nothing like it in any of the eight** *(corrected 2026-11-21, see "Round 2" below: a ninth project, layforge, has safety tools and a human veto)*: typed real dice (1),
the tower and the cup (4), lines, veils, x and p (13), taking back a yes (14),
the GM's yes under a seal, carry-over as rows (5).

**Open, and what the eight add:**

| Open | What they add | State |
|---|---|---|
| 5 (rest): a wound that changes a roll | the rule is in two engines, in two editions that disagree (below) | rule written, `box/exhaustion.py`, 14 tests; **not wired**: blocked by 3 |
| 3 and 12 | nothing found; advantage/disadvantage hits everywhere, so help as advantage is one shape to try | open, willow first |
| 8 growing | class data by level in dndwright (`classes.json`), srd_5e, OpenCombatEngine (ADR 0054) | unread beyond the hit |
| 9 a scene made up | taleweaver, narrativeengine-p are built on it, with a person confirming (`core/prompts.py:513`) | unread |
| 4 (rest): screen roll | the tower hides a roll from everyone; a screen roll is the same, opened by the GM only | open |
| 16, 17 (map) | narrativeengine-p's world-map mod (MIT) | unread |
| 6, 11, 15 | not surveyed | open |

**Read in full on 2026-11-21 (the three next steps):**

1. **narrativeengine-p `mobile/docs/WITNESS_INTEGRITY.md`.** Two layers. A
   *structural* one: scenes are filtered at retrieval by `npcsWitnessed`, and
   a scene no on-stage NPC witnessed is never put in the model's context, so
   it cannot be leaked. A *behavioural* one: a register of diverged facts
   with `knownBy`, sent whole in one system message, so the split is advice
   the model is trusted to follow. Its own text says so ("advisory rather
   than structurally isolating"). **For the `kids` leak** (a child's question
   answered from `gm-only/`): the structural layer is the shape that held
   there too (a second box over the binder's folders without `gm-only/`); the
   behavioural one is the shape that would have leaked. Same conclusion,
   reached by them in prose and by us in an incident.
2. **dndwright's dice and combat (run, not just read).** `DiceEngine(rng=...)`
   takes any `random.Random`; a subclass whose `randint` hands out the faces a
   table said, in order, and refuses when it is out, made a 2d6 of 4 and 6 and
   an attack of 13 +5 = 18 against AC 16 a hit. So **typed dice can drive its
   rolls, with a small adapter.** Its `apply_damage` is a pure function of a
   frozen state (8 hp, 3 temp, 10 damage gives 1). It needs `pydantic>=2.5`
   and `pyyaml>=6.0`, so it would be a `deps` add-on, pinned, with a licence
   on its card, not a stdlib one. Not yet checked: that a fight can be run on
   the *story's* characters rather than aetheris5e's own party; the state is
   a plain value, which is hopeful.
3. **Exhaustion, written** (`box/exhaustion.py`, `tests/test_exhaustion.py`).
   The two engines disagree: **dndwright's catalog is the SRD 5.1 rule**
   (cumulative: disadvantage on ability checks, speed halved, disadvantage on
   attacks and saves, hit point maximum halved, speed 0, death) and
   **srd_5e's is 5.2** (-2 on every d20 per level, -5 feet, death at 6). The
   module keeps both, named, never mixed. *The box plays 5.2.1* (decided
   2026-11-21, see Decided), so 5.2 is the module's default.

**Decided 2026-11-21:** the box plays SRD 5.2.1 (see Decided). **Still open:**
whether aetheris5e's fights already match it; whether an outside engine is a
`deps` add-on or a port; and whether a wound's change to a roll waits on item 3
or is shown to the GM as advice meanwhile.

**Notes for later updates.** Tavern (t11z) was unreadable from the session;
jurnalis-engine has no licence file; the survey's hit rule over-counts, read
the passages. When a want here is built or closed, change its row and say
when.

### Round 2: asking the box until the good questions ran out (2026-11-21)

Fifteen more questions asked of each chunk's own box (the pot's
`survey/box-NAME`), then the leads read. Same caveat: a hit is a passage to
read. Updating the earlier claims:

**Corrections.**
- **Layforge** (`jamesplotts/layforge`, MIT, 249 files, now the ninth chunk of
  the pot), by the author of OpenCombatEngine, is the closest sibling found. A
  *Master* holds the authoritative state and the model's credentials; thin
  clients hold neither; "everything mechanically consequential (dice, rules
  resolution, PvP, character validation, content policy) is a gate enforced in
  code at the tool-call layer, not left to the model's discretion." Its
  design.md section 9 has **safety tools** (`safety.flag` from any player,
  interrupts the scene; pre-declared lines and veils in campaign front
  matter), **character import veto** (a human operator approves or rejects
  before a character enters play), **knowledge scoping** (`strict`: chat log
  entries keep the visibility they had live, so history can't leak what was
  private; the same problem as the `kids` leak) and a **`family_friendly`
  maturity tier**. So the earlier "none of the eight has lines, veils or a
  person's yes" is true of the eight and **false of this ninth**.
- **How it differs from ours:** its safety flag is "injected as a hard
  constraint into the DM's next generation", and its maturity tiers are
  "prompt-constraint text", which its own docs call "behavior-shaping rather
  than a hard filter": the behavioural layer. Ours (a part that touches a line
  is never read) is the structural one. Its approvals are an operator panel;
  none of its code found is a hash-chained record or a seal. No commit-reveal
  dice either (the only hash/seed hits are auth and settings).
- **Edition labels were wrong.** *jurnalis-engine* says SRD 5.1 but its code
  has Weapon Mastery "per 2024 SRD" (`class.rs:251`), exhaustion as "2024 SRD
  unified formula" (`conditions/mod.rs:491`), a Warhammer weight "per the
  2024 SRD" and origin feats; one comment still says 5.1. It is mostly 2024.
  *dndwright* carries a full `dnd_5e_2024` ruleset graph (`rules/
  dnd_5e_2024.py`) and Heroic Inspiration in its species, though its
  conditions catalog is 5.1 wording. *OpenCombatEngine* is 5.1 under the OGL
  (`LEGAL.md`). *srd_5e* is 5.2 and says the experience table is the same in
  both. *narrativeengine-p* ships a 5.2.1 ability compendium. *aetheris5e* names
  no edition: a d20-versus-AC fight with advantage, nat-20 crits and no death
  saves, which reads the same in both. **So for 5.2.1: dndwright, srd_5e and
  (mostly) jurnalis are the better fits; OpenCombatEngine is 5.1.**

**What the engines hand us (new).**
- **OpenCombatEngine is built as the rules half of a host/engine split.**
  `protocol/system_engine.proto` (a gRPC contract, 1,225 lines): `ResolveCheck`,
  `Attack`, `StartTurn`, `StreamEvents`, `ToJson`/`FromJson`; each call is
  stateless; the proto says the engine "answers *what would happen*, Master
  decides *is this allowed to happen*". An `Outcome` returns the dice it rolled
  (`DieRoll` sides, result, label). The request's `params` are "engine-defined",
  with "roll-spec overrides" mentioned; whether a caller can pass the faces
  in is **not found**: read `SystemEngineGrpcService.cs` `ResolveCheck`/`Attack`.
  That is the same seam as our tower and seal, written by someone else.
- **Rests:** jurnalis eases exhaustion by one on a long rest
  (`rest/mod.rs:309`), OpenCombatEngine has a resting ADR (`017`). The rule is now in
  `box/exhaustion.py` (`after_long_rest`).

**Leads for the still-open items.**

| Item | Lead |
|---|---|
| 3, help and a reroll | narrativeengine-p has a built-in Help ability in its combat actions (`BUILTIN_HELP_ID`, `packages/engine/src/combat/__tests__/tabletopActions.test.ts:406`: it costs the action); jurnalis has the Lucky feat (3 luck points, reroll an attack, check or save: `character/feat.rs:91`) |
| 4 (rest), a GM screen roll | ink & bone: a hidden roll shows `[GM]` and `?` to others (`e2e/tests/smoke.spec.ts:162`): hidden in the UI, with no proof it wasn't changed |
| 8, growing | ink & bone's XP design with the standard 5e thresholds (`docs/superpowers/specs/2026-04-06-xp-advancement-design.md`), OpenCombatEngine ADR 0050, jurnalis XP drives level |
| 9, a scene made up | ink & bone: `POST /api/sessions/{id}/improvise` returns a 2 to 3 sentence suggestion from the last five messages: it suggests, a person decides; dnd_ai_dm builds its world from one seeded generator |
| 11, time pressing | taleweaver: an in-game clock, minutes-per-tick, and `on_time_reached` deadline triggers (`RELEASE_NOTES_v0.7.0-beta.md:102`) |
| 16, 17, map | ink & bone: draggable tokens with positions kept per map, synced to every window over a WebSocket; OpenCombatEngine ADR 0028: a 3D integer grid, Chebyshev distance |
| 6, 15 | no seat or co-GM model found in any of the nine; layforge has many players and an operator |

**Asked, and nothing found in any chunk:** a commit-then-reveal or hashed roll;
an audit trail or tamper-evident log; a check that narration's numbers match
state. These look like the real gaps the box fills. Absence from a top-ten
list is not proof.

**Next.** Read layforge's tool-call gate code and its `store.go`; read
OpenCombatEngine's `ResolveCheck`/`Attack` for how dice enter; box layforge
alone with the survey questions (it is in the pot, not yet surveyed).

### Round 3: the three next steps, read (2026-11-21)

1. **Layforge's gate and its log.** The gate is code, not prompting. The PvP
   check (`master/internal/server/dm_tools.go:700`, again at 852 and 972)
   switches on the policy and **fails closed**: "PvPPolicyPveOnly, or an
   unrecognized/unspecified value" is denied, and a campaign with no
   configuration "gets the strictest PvP setting by default, not an open
   one" (`README.md:300`). Its README says a tool is re-checked inside the
   call, "so a stray/hallucinated call can't succeed just because the tool
   wasn't offered this turn", "gates over prompting" (`master/README.md:1333`).
   A human can override the model: the operator lists imported characters and
   overrides the model's verdict through the admin API (`master/README.md:1786`).
   Its **log** is an event store described as "a campaign's append-only event
   log", with a strictly increasing `Sequence`, a refused duplicate message id
   (`ErrDuplicateMessage`), paged reads; **no hash chain, no signature**.
   Lines and veils are even model-authored: its pack generator is told to
   pre-declare them "ONLY when the adventure's content genuinely calls for
   them" (`campaignpack/generate.go:93`), so a model proposes the family's
   limits where ours are the family's own page.
   *For us:* fail-closed on an unknown setting is worth copying in
   `safety.py`; an append-only log with sequence numbers is what our record
   already is, plus a chain and a seal.
2. **How dice enter OpenCombatEngine.** They don't, through its contract.
   `ResolveCheck` in the gRPC sidecar takes a `checkType`, an `ability` and a
   `skill`; the engine rolls (`creature.Checks.RollAbilityCheck`) and the
   sidecar copies the dice it rolled into the answer
   (`SystemEngineGrpcService.cs:256`). There is no field for a seed or for
   faces; the `params` doc's "roll-spec overrides" isn't read there. The seam
   is in the .NET library (`IDiceRoller`, settable `Seed`), so a sidecar with
   our roller registered **in-process** could take typed faces, but the
   wire contract can't. Compare dndwright, where `DiceEngine(rng=...)` is the
   public parameter. **For our purpose, dndwright is the easier engine to
   put under the record.**
3. **The survey over layforge alone** (`boxes/pot/results-layforge/`): 21 of
   27 cells hit, and the same over-count caveat applies (B1's hit is a
   sentence about pre-seeding a cache; B2's is about injecting a text
   constraint). The real ones are above, plus: typed dice (B3), unpredictable
   randomness (B5), and the SRD version (F1) all miss. **Layforge never says
   which SRD it plays; it leaves that to its engine**, which is the same shape
   as our decision: an edition belongs to the engine, so ours is chosen by
   the engine we pick.

**What this changes.** The nearest design to ours now has: an engine that
answers "what would happen", a host that decides "is it allowed", safety
tools, a human veto, scoped knowledge, an append-only log, fail-closed gates.
What it does not have, and the box does: a seal that is a person's and no
one else's; a chain that makes the log checkable; typed or committed dice; and
lines and veils read structurally rather than injected into a prompt. Those
four are the box's reasons to exist beside it, not instead of it. Worth asking
the maintainer whether to talk to its author, or to borrow its engine contract.

### Round 4: read in the source, and one run (2026-11-21)

**dndwright can fight the story's characters, with typed dice (run).**
Open point from the PR: "the fight is fought by aetheris5e's own party, not
the story's characters". dndwright's combat types carry no identity:
`InitiativeEntry` is "no IDs, just what ordering needs" (a name, a total, a
Dexterity modifier); `CombatantState` is "just the numbers, no identity or
persistence" (hp, max hp, temp hp, death-save tallies, resistances,
immunities, vulnerabilities); `weapon_attack` takes the attacker's modifiers
and a weapon name. And `roll_initiative(engine, modifier, manual_roll=...)`
already takes a rolled number as said. Run with three made-up story
characters (Tamsin, Oro, a goblin), faces typed in: initiative came out
Tamsin 16, goblin 11, Oro 9; Tamsin's shortsword attack (+4, `1d6 + 2`,
mastery Vex, the 2024 rule) with a typed 15 made 19, a hit; a typed 4 on the
damage die made 6. *Slip in my run:* it then took the 4 rather than the 6
off the goblin's 7 hit points, because I read the damage total from the wrong
field; the library's own `apply_damage` was correct for the number it was
given. So: the story's characters can be fought, and dice can be typed or
dropped from the tower by an adapter; **what is not checked is the fit to our
sheets** (our characters carry a bonus per stat, not a Strength modifier) and
a whole fight loop.

**Layforge's tool gate, read.** One switch (`callDMTool`, `dm_tools.go:478`)
names about 45 tools (`resolve_check`, `apply_effect`, attacks, grapple,
equip, loot, currency, `start_combat`, `advance_turn`, `create_npc`,
vendors, `travel_to`, `stash_*`); each handler enforces its own gate and
returns a reason code on refusal (`pvp_blocked`, `internal_error`), which is
the "log with caller, args, success or reason code" its design describes.
*For us:* a refusal with a named reason is what `safety.py`'s x and our
declines already do; copying the **reason codes** as a small fixed list would
make declines countable.

**Edition, closed for dndwright.** Its weapons carry 2024 Weapon Mastery
(Vex on the shortsword) and its species Heroic Inspiration, so the code is
2024; only its conditions catalog is 5.1 wording. Rule: use dndwright for
5.2.1 and read the conditions text against the SRD before trusting it.

**Still unread:** layforge's state machine for turns (`dmStartCombat`,
`dmAdvanceTurn`); aetheris5e's stat blocks against the 5.2.1 monster list;
dndwright's `rules/dnd_5e_2024.py` graph, to see whether a story character's
bonus-per-stat can be a graph input.
