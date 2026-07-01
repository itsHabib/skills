# adapter: gamma

A near-twin of `deck` that proves the adapter seam: same capture, different render. Output is a Gamma-import-ready markdown outline instead of a `.pptx`.

## Profile

- **artifact**: a Gamma presentation, produced by importing a markdown outline
- **synthesis_target**: `gamma-outline` (emit markdown; no pptx call). The human imports it into Gamma.
- **intermediate**: `out/<slug>.gamma.md` - the import outline itself is the reviewable artifact
- **section_taxonomy**: same as `deck` - talks/sessions, each a slide group
- **unit_mapping**: one sub-topic with good answers -> one card; one strong story -> its own card

## Question emphasis

Identical to `deck`: stories and hot-takes that each carry a card; one transmission question per sub-topic.

## Synthesis rendering notes

Gamma's import reads markdown structure as cards. Emit:

- `# Title` for the deck title.
- `---` between cards (Gamma splits on these).
- `## Card heading` in the expert's voice, then 3 to 5 bullet phrases.
- Keep speaker-note depth in a short paragraph under the bullets; Gamma pulls it into the card body.

Same voice and no-fabrication rules as `deck`. The difference is purely the render target: emit clean import markdown, do not call `anthropic-skills:pptx`. Tell the operator to import `out/<slug>.gamma.md` via Gamma's "paste in text / import" flow.
