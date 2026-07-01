# adapter: postmortem

Captured answers become a blameless post-mortem. The taxonomy is fixed; the interview reconstructs the incident and pulls out the contributing factors and actions.

## Profile

- **artifact**: a post-mortem markdown file
- **synthesis_target**: the post-mortem markdown template below
- **intermediate**: `out/<slug>.postmortem.md` - reviewed before it is shared
- **section_taxonomy** (fixed): Summary, Timeline, Impact, Root cause, Contributing factors, Action items, What went well
- **unit_mapping**: each field is one interview section; Timeline is reconstructed from a sequence-of-events question set

## Question emphasis

Blameless and sequence-driven. Lean on:

- Timeline: "walk me through it minute by minute - what did you see, what did you do, when did you know it was bad." Reconstruct the order of events.
- Contributing factors over single root cause: "what made this possible / what made it worse / what almost caught it but did not." Systems, not people.
- Detection and recovery: "how did you find out, how long to mitigate, what would have caught it sooner."
- Honest "what went well" - the parts of the response that worked are as instructive as the failure.

Never frame a question to assign blame. Factors and systems, not culprits.

## Synthesis rendering notes

Fixed template:

```
# Post-mortem: <incident> (<date>)

## Summary
<one paragraph: what happened, impact, resolution>

## Timeline
<ordered events with timestamps, from the Timeline answers>

## Impact
<who/what was affected and how much, from the Impact answers>

## Root cause
<the technical root, from the Root cause answers>

## Contributing factors
<the systemic factors that made it possible or worse>

## Action items
<concrete, owned, dated follow-ups, from the Action items answers>

## What went well
<the parts of the response that worked>
```

Blameless voice. Preserve the expert's candor about what broke, but keep it about systems. Flag missing facts (a timestamp, an owner) with `TODO: needs <what>` rather than guessing.
