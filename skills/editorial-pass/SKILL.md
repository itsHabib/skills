---
name: editorial-pass
description: Multi-editor editorial pass over a draft (blog post, essay, README-as-prose) in YOUR voice — a mechanical AI-tell scan, six specialized editor lenses fanned out via the Workflow tool, an editor-in-chief consolidation with verbatim old/new fixes and a publish verdict, then must-fixes applied. Use when you say "editorial pass", "edit my draft", "run the panel on this", "de-AI this post", "does this sound like me", "voice pass", or invoke /editorial-pass <draft-path>. Grounded in a voice-profile doc you provide; pairs with /interview for sections that need raw material instead of editing.
argument-hint: "<draft-path> — the near-ready draft; the voice profile is set via $VOICE_PROFILE"
user_invocable: true
---

# /editorial-pass — the six-lens panel + editor-in-chief

Turn a near-ready draft into a publish-verdict draft that sounds like you, not
like a model. The pass has a **subtractive** half (kill the AI tells) and an
**additive** half (inject your actual markers) — a draft is not done when it's
merely clean.

## Inputs

- **DRAFT** (required): path to the draft. From `$ARGUMENTS` or ask.
- **VOICE PROFILE**: a doc that captures your voice — the kill-list, the
  additive rule, the diction tables, and the drafting checklist that every lens
  and every rewrite is held to. Point `$VOICE_PROFILE` at it (e.g.
  `~/writing/voice-profile.md`), or pass it explicitly. Read it FIRST, in full.
  If no profile exists yet, the mechanical scan and most lenses still run, but
  the additive half needs one — offer to draft a starter profile.
- **CAVEATS** (optional): facts the draft must keep honest (e.g. features
  described as in-progress that no edit may inflate into "shipped"). Ask if the
  draft discusses your own projects and no caveats were given.
- **TARGET READER**: ask if not stated; default = a smart reader who wants the
  piece to earn its length.

## Step 1 — Mechanical tell-scan (before any model reads anything)

Run deterministic checks over the draft and record the results; they feed the
voice lens and the editor-in-chief. Grep/count, don't eyeball:

1. **Em-dashes:** `—` anywhere → each is a finding.
2. **Fingerprint watchlist frequency:** count case-insensitive hits for
   `quiet|quietly`, `genuinely`, `actually`, `honest|honestly`, `simply`,
   `deliberate|deliberately` (plus any words added to profile kill-list #10).
   Any word >2 hits → finding listing every location; keep the single best.
3. **Negation-correction shapes:** regex for `\bnot [^.]{3,40}[.,;] (it|this|that|we|I)('s| is| are|'re)?\b` and `It('s| is)n't [^.]*\. It('s| is)\b` — approximations; the voice lens confirms.
4. **Repeated sentence openers:** flag any 2+ consecutive sentences sharing
   their first two words (anaphora candidates).
5. **Triad density:** count `X, Y, and Z` list constructions per section;
   >1 per section → finding.
6. **Sentence-length variance:** compute per-paragraph mean/stdev of sentence
   word-counts; paragraphs where every sentence lands 18–30 words → rhythm
   finding (human paragraphs run ragged).

## Step 2 — The panel (six lenses, background Workflow, two waves of three)

Fan out via the Workflow tool with a structured-output schema per editor
(findings: location + verbatim problem snippet + concrete in-voice fix +
severity). **Two waves of three** — a prior run got rate-limited firing all
six at once; add retry/backoff on rate-limit errors. Every editor gets: the
draft, the voice profile, the caveats, the target reader.

1. **Developmental** — theme, arc, does every section earn its place, hook ↔
   close connection. (4–7 observations.)
2. **Line** — clarity, rhythm, wordiness; quote each problem sentence, give a
   tighter rewrite; keep the casual confident register, do not formalize.
   (5–10 edits.)
3. **Copy** — grammar, typos, tense, name/capitalization consistency,
   code-vs-prose mismatches, internal contradictions. (Every concrete error.)
4. **Voice & AI-tells** — the core lens, two halves:
   (a) *subtractive*: confirm/extend every Step-1 mechanical finding, hunt
   every kill-list tell (1–12), clean rewrite for each;
   (b) *additive*: score the draft against the profile's positive markers —
   pet phrases, hedges, self-deprecating aside, rhetorical-question beat,
   concrete numbers, "I" vs "we" usage. Missing markers are findings with a
   suggested insertion point, not vibes.
5. **Credibility** — where a skeptical senior engineer calls BS; overclaiming;
   verify every CAVEAT item is not overstated; hedging calibrated (honest,
   not mush).
6. **Reader value** — the single strongest takeaway and whether it lands;
   what's missing (a number, a worked example, a how-to-start); shareability.
   (4–6 prioritized.)

## Step 3 — Elicitation-gap check (the /interview seam)

The best-sounding lines in any draft are lifted near-verbatim from you;
synthesized connective tissue is where the AI register creeps in. For each
section the panel flagged as voice-weak, ask: **is there raw material behind
it** (interview answers, notes, chat quotes, friction-log lines)? If not, do
NOT rewrite it into better synthesis — mark it an **elicitation gap** and
surface 2–4 specific story-eliciting questions you should answer (offer to run
`/interview` on them). Editing can't fix what was never yours to begin with.

## Step 4 — Editor-in-chief

One consolidation agent reads the draft + profile + all six reports + the
mechanical scan. It produces ONE de-duplicated, prioritized fix list:

- Per fix: **EXACT verbatim old snippet** (empty if pure addition) + new
  text + one-line reason + tag **must / should / optional**.
- Every new text: in-voice, clean of all 12 tells, respects the caveats.
- Conflicts between lenses: reconcile and make the call, one-line reason.
- **Publish verdict:** `ready-to-publish` / `minor-fixes` / `needs-work`,
  plus a one-paragraph theme assessment and the elicitation-gap list.

## Step 5 — Apply and report

1. Apply the **must** fixes to the draft directly.
2. Re-run the Step-1 mechanical scan on the result — a fix that introduces a
   new tell is a bug; fix it before reporting.
3. Report back: verdict, what changed (grouped, not a wall), should/optional
   fixes awaiting a yes, elicitation gaps with their questions, and the
   mechanical before/after counts (e.g. "quietly 5→1, triads 9→4,
   em-dashes 0→0").

## Rules

- The voice profile is the contract. When a lens's suggestion conflicts with
  it, the profile wins.
- Never inflate held-back/in-progress features into shipped ones — the
  credibility lens verifies this explicitly.
- Don't formalize. The failure mode of line editing is a smoother, more
  generic draft. When in doubt, rougher and more you.
- New tells you flag during review get appended to the profile's kill-list
  (with a date), so the list compounds.
