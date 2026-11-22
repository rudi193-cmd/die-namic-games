# four open SRD rules engines, asked what a record-and-seal box would need of them

A stack over OpenCombatEngine (C#), jurnalis-project/engine (Rust), srd_5e
(Elixir, from the agentic-realms monorepo) and dndwright (Python), each at
one commit. The question behind it, from open.md's note: could one stand
under the kernel's record and seal, with the dice coming from the tower?
Each want is written above its step: proposals, there to cut. Nothing here
is sealed. `rebuild.sh` lays the box and runs it.

## can the dice come from outside

Want 1: "Can the caller hand the engine its dice, or does it roll its own?"
- all-passages -- --box {box} --top 8 "inject random number generator dice roller interface"

Want 2: "Is it deterministic: the same inputs, the same blow?"
- all-passages -- --box {box} --top 8 "deterministic seeded reproducible same result"

Want 3: "Can the faces be given as said, a roll made at a real table?"
- all-passages -- --box {box} --top 5 "fixed dice forced roll test"

## what a fight is to each

Want 4: "How is initiative, an attack against armor class and damage resolved?"
- all-passages -- --box {box} --top 8 "initiative attack roll armor class damage"

Want 5: "What does a fight's state look like, and can it be written out and read back?"
- all-passages -- --box {box} --top 8 "state serialize save load replay event log"

Want 6: "Does anything write to a record each blow, an event or a log?"
- all-passages -- --box {box} --top 6 "event emitted combat log history"

## what we'd have to agree to

Want 7: "Which SRD does each follow, and under what licence?"
- all-passages -- --box {box} --top 8 "srd 5.1 5.2 creative commons license"

Want 8: "What does each need installed to run?"
- all-passages -- --box {box} --top 6 "dependencies install"

Want 9: "Where does the engine say it stops: what rules are not built?"
- all-passages -- --box {box} --top 6 "not implemented limitations roadmap missing"
