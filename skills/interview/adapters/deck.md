# adapter: deck

The first-class adapter. Captured answers become a slide deck via `anthropic-skills:pptx`, with a reviewable slide-spec as the intermediate.

## Profile

- **artifact**: slide deck (one `.pptx`, optionally one per top-level section)
- **synthesis_target**: `anthropic-skills:pptx`
- **intermediate**: `out/<section>.slidespec.md` - reviewed by the human before any binary is generated
- **section_taxonomy**: talks / sessions, each a group of slides. A multi-talk series is many sections; a single talk is one section with sub-topic groups. Sub-topics map to slide clusters.
- **unit_mapping**: one captured sub-topic with good answers -> one to three slides. One strong story -> its own slide. The warm-up section -> the opener slides. A throughline note -> a recurring spine slide.

## Question emphasis (tilts the shared rules)

Lean toward questions whose answers can each carry a slide on their own:

- War stories and concrete examples - a slide built on a real incident lands; a slide built on a definition does not.
- Hot-takes and contrarian framing - these become the memorable slides and the section openers.
- A single transmission question per sub-topic ("the one thing you would force every intern to internalize") - that answer is usually the section's punchline slide.

De-emphasize exhaustive tactical step-by-steps unless the deck is a how-to; they read as dense slides.

## Synthesis rendering notes

Slide-spec shape (per slide in `out/<section>.slidespec.md`):

```
### Slide N: <punchy title in the expert's voice>
- bullet (3 to 5, each a phrase not a paragraph)
- ...
Speaker notes: <the story / framing in the expert's voice, 2 to 4 sentences, drawn from the captured answer>
Source: <Qn> [+ build note if present]
```

Rules:

- Title in the expert's voice and candor. A blunt captured phrase makes a better title than a sanitized one.
- Bullets are phrases, not sentences. The story lives in the speaker notes, not on the slide.
- Speaker notes are built from the captured answer, in the expert's voice. Do not invent. If a slide needs a beat the answers do not cover, leave a `TODO: needs <what>` marker rather than fabricating.
- Honor `> Build note:` lines - they say which slide an answer belongs on and why. A build note overrides default placement.
- Respect the section's promise/throughline from the outline; open each section by stating its promise.
- One section synthesizes to one slidespec file. The human reviews and edits it. Only then hand the approved spec to `anthropic-skills:pptx`.

## Hand-off to pptx

After the slide-spec is approved, invoke `anthropic-skills:pptx` with the slide-spec as the content source. Map each `### Slide N` to a slide, bullets to the body, speaker notes to the slide's notes. Keep one `.pptx` per top-level section unless the expert wants a single combined deck.
