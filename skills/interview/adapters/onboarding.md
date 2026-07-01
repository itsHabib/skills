# adapter: onboarding

Captured answers become an onboarding guide - the "what I wish someone had told me" doc for the next person into a codebase, product area, or role.

## Profile

- **artifact**: an onboarding guide (markdown). Pairs naturally with the `ShareOnboardingGuide` flow if the guide is named `ONBOARDING.md`.
- **synthesis_target**: `inline-markdown` (write the guide directly)
- **intermediate**: `out/ONBOARDING.md` - reviewed before sharing
- **section_taxonomy**: What is this and why does it exist, Getting set up, Your first task, The non-obvious gotchas, Who to ask for what, How we work here
- **unit_mapping**: one section per taxonomy entry; gotchas become a checklist; "who to ask" becomes a small table

## Question emphasis

The gold here is the tacit knowledge a veteran has stopped noticing. Lean on:

- "What I wish someone had told me on day one" - the single best onboarding question.
- Gotchas: "what trips up every new person / what looks wrong but is intentional / what is the footgun nobody documents."
- The real first task: "what is the smallest real thing a new person should ship in week one, and what will they get stuck on."
- Hidden map: "who actually knows X, where is the thing that is not where you would expect, what doc is lying."

## Synthesis rendering notes

- Write to the new person, in the expert's voice. Warm but blunt - the gotchas section is where candor pays off.
- Turn gotchas into a scannable checklist; turn "who to ask" into a name/area table.
- Concrete over abstract: real paths, real commands, real names, drawn from the captured answers.
- Flag gaps with `TODO: needs <what>`; an honest gap beats a confident wrong instruction in an onboarding doc.
- If the guide is `ONBOARDING.md`, the operator can publish it with `ShareOnboardingGuide`.
