# adapter: adr

Captured answers become an Architecture Decision Record. The taxonomy is fixed, so STRUCTURE is light - the spine is the ADR's standard fields, and the interview drills into each.

## Profile

- **artifact**: an ADR markdown file
- **synthesis_target**: the ADR markdown template below
- **intermediate**: `out/<slug>.adr.md` - the ADR draft itself, reviewed before it lands
- **section_taxonomy** (fixed): Context, Decision, Alternatives considered, Consequences (and optionally Status)
- **unit_mapping**: each field is one interview section; the captured answers fill that field directly

## Question emphasis

The whole point of an ADR is the reasoning behind a choice, so lean hard on:

- Alternatives: "what else did you seriously consider and why did you not pick it" - this is the most-skipped, most-valuable field.
- The deciding trade-off: "what was the one thing that tipped it" - the heart of the Decision.
- Consequences and regrets: "what does this cost us / what did you give up / what would make you revisit this."
- Context: "what forced the decision now, what would a reader six months from now not know."

## Synthesis rendering notes

Fixed template:

```
# ADR <n>: <decision in one line>

## Status
<proposed / accepted / superseded>

## Context
<the forces, from the Context answers, in the expert's voice>

## Decision
<what was decided and the deciding trade-off, from the Decision answers>

## Alternatives considered
<each alternative + why it lost, from the Alternatives answers>

## Consequences
<what this buys, what it costs, what to watch, from the Consequences answers>
```

Keep it tight - an ADR is a record, not an essay. Preserve the actual reasoning; do not launder a blunt "we picked X because Y was a maintenance nightmare" into something vaguer.
