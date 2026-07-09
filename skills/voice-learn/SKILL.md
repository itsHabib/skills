---
name: voice-learn
description: Build and mine a corpus of AI-draft → operator-final pairs so the agent's writing converges on the operator's real voice. Two verbs — capture (freeze the AI version of a draft BEFORE the operator edits it) and learn (diff the operator's final against the frozen AI version, classify every edit as voice vs content, and fold recurring voice edits into voice-profile.md and tellscan.mjs as dated, evidence-backed rules). Use when the operator says "voice learn", "capture this draft", "here's my final version, learn from it", "diff my edits", "store this pair", "learn my voice", or invokes /voice-learn. Corpus lives under a writing dir you configure (e.g. ~/writing/corpus/); the voice profile stays the single contract.
---

# /voice-learn — revealed-preference voice tuning

The voice profile is *declared* preference: the operator describing his voice.
An edit diff is *revealed* preference: what his hands do when AI prose is in
front of him. This skill collects those diffs as a corpus and compounds them
into the two enforcement artifacts you maintain —
a `voice-profile.md` (the contract) and an optional `tellscan.mjs`
mechanical scanner alongside it. Nothing new sits between them; this skill only
feeds them.

## Corpus layout

```
<your-writing-dir>/corpus/
  README.md                 # what this is, how pairs get added
  LEDGER.md                 # sub-threshold rule candidates + evidence
  <slug>/
    ai.md                   # frozen last-AI-touch version (verbatim)
    final.md                # operator's published/final version (verbatim)
    meta.md                 # date, doc type, provenance, edit-density notes
```

## Verbs

### `/voice-learn capture <draft-path> [slug]`

Freeze the AI side BEFORE the operator starts editing. Copy the file
byte-for-byte to `corpus/<slug>/ai.md` (slug defaults to the draft filename),
write `meta.md` with date + provenance (how much human material the draft
already contains — a panel-edited draft with interview answers folded in will
have low edit density, and that's worth recording), and mark the pair
`status: pending-final`. Never reconstruct an AI version after the fact; if
the pre-edit version wasn't captured, the pair is lost — skip it rather than
approximate it.

**The freeze is permanent (operator-settled 2026-07-06).** Once the operator
starts editing, NEVER touch ai.md again — not to fold in later fixes, not to
"keep it in sync." Edits the operator directs the agent to make after the
freeze ("kill the colons", "add a shoutout here") are OPERATOR edits: his
judgment, the agent's hands. They belong in the final-vs-ai diff exactly like
his typed edits. Do not maintain side-files of "AI contributions", do not
re-freeze, do not subtract agent-executed changes from the diff.

### `/voice-learn <slug> <final-path>` (learn)

1. **Store the final verbatim** at `corpus/<slug>/final.md`. If it arrives as
   docx, convert (pandoc) and store both; if it's a Medium paste, ask for the
   markdown/plain-text export rather than scraping formatting artifacts.
2. **Diff.** `git diff --no-index --word-diff=plain ai.md final.md` for the
   word level, plus a sentence-level read for moves and splits the word diff
   obscures.
3. **Classify every edit** before learning anything. Four buckets:
   - **voice** — same meaning, different wording/rhythm/structure. Teaches.
   - **content** — he added or removed information. Does not teach voice;
     note it in meta.md (it may reveal an elicitation gap instead).
   - **fact** — correction of something wrong. Does not teach. Worth a
     separate line in the report so the error source gets fixed.
   - **format** — headers, links, platform artifacts. Ignore.
   Each voice edit gets recorded with verbatim old → new evidence. When the
   bucket is ambiguous, ask; a content edit mislearned as voice is how the
   model learns the wrong lesson ("he always adds a paragraph about X").
4. **Mine the voice edits** into candidate rules, by shape:
   - deletions → kill-list candidates (words/phrases/constructions he cuts)
   - substitutions → diction preferences (he says X where the model says Y)
   - structural → rhythm rules (splits long sentences, breaks paragraphs,
     reorders clauses, converts prose to bullets or back)
   - additions → additive-rule candidates (markers he injects that drafts
     keep missing)
5. **Threshold before promotion.** A candidate becomes a profile rule at
   **≥2 independent occurrences across different pairs**, or 1 occurrence the
   operator explicitly confirms. Below threshold it goes in `LEDGER.md` with
   its evidence and waits. One-off edits are usually mood, not voice.
6. **Apply promoted rules.**
   - Append to the matching voice-profile section with the same dating
     convention the kill-list already uses:
     `(flagged YYYY-MM-DD via /voice-learn, N occurrences across M pairs)`.
   - If the rule is mechanically countable (a word, a phrase, a regex-able
     construction), add the pattern to `tellscan.mjs` too and show the
     operator the code diff.
7. **Report.** Edit density (words changed / words total), the
   voice/content/fact split, rules promoted, candidates ledgered, candidates
   confirmed by this pair, and corpus size. If content edits cluster in one
   section, say so — that's an elicitation gap for `/interview`, not a voice
   problem.

### `/voice-learn status`

List the corpus: pairs complete, captures pending a final, ledger candidates
and their counts.

## Rules

- **The profile stays the single contract.** This skill appends evidence-backed
  rules to it; it never forks a second style document. The ledger holds only
  sub-threshold candidates.
- **Rules can be retired.** If later pairs show the operator consistently
  reverting a promoted rule, flag it for removal instead of letting the
  profile drift wrong. Note the retirement with a date, same as additions.
- **Never learn from content or fact edits.** Voice is how he says things,
  and only that.
- **The corpus is personal material.** It lives under your own writing dir, not
  in the public skills repo. The skill is public; the data is not.
- **Expect diminishing returns and say so.** The first handful of pairs carry
  most of the signal. When a learn pass promotes nothing and confirms
  little, report that as convergence, not failure.
