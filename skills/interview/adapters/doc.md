# adapter: doc

Captured answers become a prose document (markdown, optionally `.docx`). For essays, narrative explainers, internal write-ups - anything where the artifact is paragraphs, not slides.

## Profile

- **artifact**: a markdown document (or `.docx`)
- **synthesis_target**: `inline-markdown` by default; `anthropic-skills:docx` when the operator wants a formatted Word doc
- **intermediate**: `out/<slug>.draft.md` - the prose draft, reviewed before any docx conversion
- **section_taxonomy**: document sections (intro, the body sections, conclusion). The spine is an argument or a narrative arc, not a slide order.
- **unit_mapping**: one captured sub-topic -> one prose section or subsection; stories become illustrative paragraphs inside the argument

## Question emphasis

Tilt toward the why, the rationale, and the trade-offs. A doc has room for nuance a slide does not, so:

- "Why" and "what changed your mind" questions - the doc can carry the full reasoning.
- Contrast and failure questions - they become the "what not to do" sections.
- Less pressure for one-line punchlines; an answer can sprawl and still be usable.

## Synthesis rendering notes

- Write in the expert's voice and candor from `profile.md`; this is a write-up, not a transcript, so connect the captured answers into a flowing argument.
- Quote or closely paraphrase the expert's actual phrasing for the load-bearing claims; do not sand them into corporate prose.
- Preserve the spine's arc - each section advances the argument the outline laid out.
- Flag thin sections with `TODO: needs <what>` rather than padding.
- For `.docx`, hand the approved `out/<slug>.draft.md` to `anthropic-skills:docx`.
