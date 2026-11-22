# four open AI game masters, asked what Die-Namic would want to know

A stack over four open-source AI game-master projects, each at one commit:
NarrativeEngine-P, ink & bone, dnd_ai_dm and TaleWeaver (all MIT per their
LICENSE files; TaleWeaver also ships a CC-BY-NC-4.0 file, for its assets).
Each want is written above its step, as in `box/gm-stack.md`: proposals, in
the words these projects use, there to cut. Nothing here is sealed.
`rebuild.sh` lays the box and runs it.

## what keeps the model honest

Want 1: "How does each one stop the model inventing rules or results?"
- all-passages -- --box {box} --top 8 "rules engine enforce validate llm hallucinate"

Want 2: "Where is the line between what the model says and what the code decides?"
- all-passages -- --box {box} --top 6 "deterministic code decides model narrates"

Want 3: "Does a person have to say yes before something becomes true?"
- all-passages -- --box {box} --top 6 "approve confirm override player decides"

## what carries from night to night

Want 4: "How is a campaign remembered between sessions?"
- all-passages -- --box {box} --top 8 "persistent memory campaign summary session"

Want 5: "How are characters and non-player characters kept?"
- all-passages -- --box {box} --top 5 "npc character sheet state saved"

## the dice and the fights

Want 6: "Where do the dice come from, and can anyone steer them?"
- all-passages -- --box {box} --top 8 "dice roll random seed d20"

Want 7: "How is a fight run: initiative, attacks, armor class, hit points?"
- all-passages -- --box {box} --top 8 "combat initiative attack armor class hit points"

Want 8: "Which of them say they follow the SRD, and which version?"
- all-passages -- --box {box} --top 6 "srd 5.1 5.2 open game license"

## what we may take

Want 9: "What licence does each carry, and does anything restrict use?"
- all-passages -- --box {box} --top 8 "license MIT non-commercial attribution"

Want 10: "What do they ask a family or a child to know or agree to?"
- all-passages -- --box {box} --top 5 "children safety privacy"
