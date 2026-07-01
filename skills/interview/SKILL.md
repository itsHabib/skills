---
name: interview
description: Turn an expert's unwritten knowledge into a finished artifact (slide deck, design doc, ADR, post-mortem, onboarding guide, Gamma outline) by driving an interview-to-artifact loop. Curate a spine, fan out agents to generate deep story-eliciting questions in the expert's voice, assemble one fillable resumable interview doc, let the human fill answers over time, then synthesize the captured answers into the target artifact in their voice. Parameterized by an artifact adapter. Use when the operator says "interview me about X", "build me an interview for X", "turn my brain dump into a deck/doc/guide", "draw this out of my head", "I want to make a talk/deck/guide about X but staring at a blank page", "elicit my thinking on X", or invokes /interview. The deck adapter hands off to the pptx skill; the doc adapter to markdown/docx. Reach for this whenever the bottleneck is getting knowledge OUT of a person, not the final format.
argument-hint: "<slug> [adapter:deck|doc|adr|postmortem|onboarding|gamma] [phase:structure|interview|capture|synthesis]"
user_invocable: true
---

# /interview - the interview-to-artifact loop

Get deep knowledge out of an expert's head and into a finished artifact. The format is the easy part; the hard part is that staring at a blank deck produces nothing, but a good question pulls out a story, and a stack of captured stories is most of the artifact.

This skill drives a five-phase loop, parameterized by an artifact `adapter`:

```
INPUT      goal + expert + optional brain-dump
STRUCTURE  collaboratively curate the spine            -> outline.md
INTERVIEW  fan out questions + critic, assemble doc    -> interview.md   (a Workflow)
CAPTURE    human fills answers over time, resumable    -> interview.md   (in place)
SYNTHESIS  captured answers -> target artifact         -> out/...        (adapter)
```

Design ground truth and rationale: `docs/features/interview-to-artifact/spec.md`. The pattern was extracted from the intern-talk build (`docs/intern-talks/`).

## The model

Internalize this before running:

- **The markdown is the state.** Progress lives in a checklist, per-section status in a `_Status:_` line, the adapter and slug in the outline header. There is no sidecar JSON. The doc is human-readable, resumable, and outlives the tooling.
- **One voice source.** `profile.md` (who the expert is + how they talk) is read by BOTH the question generator and the synthesizer. Write it once.
- **Filled answers are the asset.** Never overwrite a captured answer as a side effect. Never hallucinate content into an empty slot. Synthesis builds from what was actually said.
- **Adapters are data, not code.** The loop is identical for every artifact; only the section vocabulary and the final synthesis hand-off change. Those live in `adapters/<name>.md`.
- **Synthesis composes, it does not reimplement.** The deck adapter hands a reviewed slide-spec to `anthropic-skills:pptx`. The doc adapter writes markdown or hands to `anthropic-skills:docx`. This skill never learns to render a binary itself.

## When to use

Triggers:
- "interview me about X" / "build me an interview for X" / "draw X out of my head"
- "turn my brain dump into a deck / doc / onboarding guide / ADR / post-mortem"
- "I want to make a talk about X but I'm staring at a blank page"
- "elicit my thinking on X" / "ghostwrite a deck from my head"
- Explicit `/interview`

Anti-triggers:
- The content already exists and just needs formatting into slides - go straight to `anthropic-skills:pptx`.
- A technical design for code work - that is `/tdd` (it has its own template + dossier seeding).
- A one-paragraph answer - just write it.

## Arguments

`/interview <slug> [adapter:<name>] [phase:<name>]`

- `<slug>` (required): kebab-case name for this interview project. Becomes `docs/interviews/<slug>/`.
- `adapter:<name>` (optional): `deck` (default), `doc`, `adr`, `postmortem`, `onboarding`, `gamma`. Selects the section taxonomy, question emphasis, and synthesis target. Read `adapters/<name>.md`.
- `phase:<name>` (optional): jump straight to `structure`, `interview`, `capture`, or `synthesis`. Default: infer from what already exists in the workspace (no outline.md -> structure; outline but no interview.md -> interview; interview with empty slots -> capture; enough filled -> offer synthesis).

If the workspace already exists, infer the phase from its state and continue rather than starting over.

## Steps

### 0. Pre-flight (INPUT)

Resolve `(slug, adapter, workspace_root, phase)`.

- Workspace root defaults to `docs/interviews/<slug>/`. Create it.
- Read `adapters/<adapter>.md` from this skill dir - it drives the taxonomy and synthesis target for every later step.
- If `profile.md` does not exist, draft it now (Step 1a) and confirm with the expert before generating any questions.

### 1a. The expert profile (voice source)

Write `docs/interviews/<slug>/profile.md` with two blocks:

- **Who the expert is**: role, background, current world, the through-line of how they work. This grounds questions in their real life so answers are stories, not definitions.
- **Voice and candor rules**: how they talk, phrases they use, tone to match, what to avoid.

Bootstrap from the operator's memory corpus when the expert IS the operator: pull from `user_role`, `user_cam_learning_goal`, and the `feedback_*` style entries (direct, hates fluff, never em dashes, blunt framing welcome). For any other expert, ask a short batch of profile questions first. Confirm the draft with the expert; the profile tunes everything downstream.

### 1b. Curate the spine (STRUCTURE)

Collaboratively build `docs/interviews/<slug>/outline.md`. The driver proposes a spine from `(goal, brain-dump, adapter default taxonomy)`; the expert refines until agreed. The outline contains:

- A header: slug, adapter, expert, date.
- The sections (the artifact's spine), from the adapter's default taxonomy adapted to this goal.
- Per-section notes plus an "Interview to capture:" hint line.
- A status legend: `[structure]` = shape agreed, `[raw]` = raw bullets not yet expanded, `[interview]` = still needs stories.
- Any throughline / spine note.

Do not leave STRUCTURE until the expert says the spine is right. Questions are only as good as the sections they come from. Use `templates/interview-header.md` as the shape reference and the prototype `docs/intern-talks/outline.md` as the gold standard.

### 2. Generate the interview (INTERVIEW)

Run the shipped fan-out Workflow. Read `workflows/interview-builder.js` from this skill dir and invoke it with `args` built from `profile.md` + `outline.md`:

```
Workflow({
  script: <contents of workflows/interview-builder.js>,
  args: {
    title, slug,
    profile,        // the §1a SHARED block
    rules,          // the question-design rules (adapter may tilt them; never em dashes)
    spine,          // the throughline note
    sections: [ { id, title, promise, subTopics: [ { name, note } ] }, ... ],
    crossCutting: [ { section: "Warm-up / who you are", focus }, { section: "Series-wide philosophy", focus }, { section: "Closing", focus } ]
  }
})
```

The workflow fans out one agent per section (4 to 7 deep questions per sub-topic, varied across war-story / hot-take / contrast / failure / tactical / transmission types), runs a breadth critic that adds the cross-cutting sections and per-section gap-fills, and returns assembled markdown. Write the returned `markdown` to `docs/interviews/<slug>/interview.md`.

This is a multi-agent Workflow - it needs the operator's opt-in. If the operator invoked `/interview` they have opted into this loop; proceed. If you are unsure, say what the workflow will do and ask.

**Incremental re-run (answer-safe merge).** When STRUCTURE adds sections after CAPTURE has begun, re-run the builder for the NEW sections only and merge into the existing `interview.md`:
- Never touch an existing section or a filled `_Answer:_` slot. The captured words are the asset.
- Append new sections; add their lines to the Progress checklist.
- A section that already exists is skipped with a warning, not regenerated. Editing existing questions is a manual, opt-in operation.

### 3. Capture answers (CAPTURE)

The human fills answers over many sittings. Support three modes, all writing to the same `interview.md`:

- **In-doc**: they edit `_Answer:_` slots directly and tick Progress lines. The driver just reports state.
- **Chat-transcribe**: they brain-dump in chat; you clean it (grammar, filler) and write it into the right slot. Read-modify-write with the current doc as the compare-and-swap guard. Never overwrite a non-empty slot without explicit confirmation. Keep their phrasing - clean, do not rewrite voice.
- **Live interview**: ask the open questions conversationally, one section at a time, and fill as you go.

Report progress by parsing the doc: "42 of 260 filled; warm-up and S1 complete; S6 untouched." The Progress checklist and `_Status:_` lines are the resume state.

**Build notes.** An answer can carry a `> Build note:` line saying where it lands in the artifact and why. These are first-class hints synthesis reads. Add one when a tangent clearly belongs on a specific slide or in a specific section.

### 4. Synthesize the artifact (SYNTHESIS)

When a section (or the whole) has enough captured, transform answers into the artifact via the adapter. Always two steps:

1. **Produce a reviewable intermediate** the human checks before any binary. For `deck`, run `workflows/deck-synthesis.js` (one agent per section drafts slides from that section's answers + build notes, then an editorial pass) and write a per-section `out/<section>.slidespec.md` (ordered slides: title + 3-5 bullets + speaker notes). The human edits the slide-spec - cheap to fix here, expensive in a `.pptx`.
2. **Hand the approved intermediate to the output skill** named by the adapter's `synthesis_target`: `deck` -> `anthropic-skills:pptx`; `gamma` -> emit a Gamma-import-ready outline (no pptx call); `doc` -> markdown or `anthropic-skills:docx`; `adr`/`postmortem`/`onboarding` -> the adapter's markdown template.

**Voice preservation is the contract.** Write in the expert's voice from `profile.md`. Build from what was actually said. Do not invent claims, smooth out candor, or swap a specific story for a generic principle. Empty answers are flagged as still-needed, never hallucinated into content.

### 5. Print the operator-facing summary

Tight, no process narration:

```
/interview <slug> (adapter: <name>) - <phase> done

Workspace: docs/interviews/<slug>/
Outline:   <N> sections [structure/raw/interview breakdown]
Interview: <M> questions, <K> filled (<sections complete>)
Synthesis: out/<section>.slidespec.md (review, then -> pptx)

Next: <the single most useful next action>
```

## Key reminders

- **Curate the spine first.** Generated questions are only as good as the sections. Do not skip STRUCTURE.
- **Protect filled answers.** Re-runs are append-only; transcription never clobbers a non-empty slot. This is the one inviolable rule.
- **One voice source.** `profile.md` tunes both questions and synthesis. Do not duplicate voice rules inline.
- **Review the slide-spec before the binary.** The intermediate is where editing is cheap.
- **Never em dashes.** In questions, in synthesis, in any file this skill writes.

## Anti-patterns

- **Do not auto-curate the spine.** STRUCTURE is human-in-the-loop. Propose, do not impose.
- **Do not regenerate the interview on a re-run.** New sections append; existing sections and answers are untouched.
- **Do not synthesize empty sections into invented content.** Flag the gap.
- **Do not reimplement the output format.** Hand off to the output skill. The adapter maps; the skill renders.
- **Do not make the loop generic mush.** The adapters are the only knob. The question-design rules, the answer-safety, the voice preservation are opinions, not config.

## Source material

- `docs/features/interview-to-artifact/spec.md` - the design and the decisions behind this skill.
- `docs/intern-talks/outline.md` and `interview.md` - the gold-standard worked example of every phase.
- `adapters/deck.md` - the first-class adapter; imitate its shape for new ones.
- `workflows/interview-builder.js` - the generalized fan-out, args-parameterized.
- `workflows/deck-synthesis.js` - the generalized deck synthesis fan-out.
- `~/.claude/skills/tdd/SKILL.md` - sibling skill; the house SKILL.md shape and the "skills compose, don't invent verbs" discipline.
- `anthropic-skills:pptx` - the deck synthesis hand-off target.

## Outcome

After `/interview` runs, the expert has: a curated `outline.md`, a fillable resumable `interview.md` of deep questions in their voice, a way to fill it over time without losing work, and a path from filled answers to a finished artifact in their voice. The loop is iterative - add sections any time and re-run; the captured answers carry forward.
