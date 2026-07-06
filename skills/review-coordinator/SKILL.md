---
name: review-coordinator
description: Consolidate the AI PR reviewers (Codex, Claude, Cursor Bugbot, GitHub Copilot) on a pull request into ONE verdict — a deduped, severity-ranked finding list plus a block/go merge gate — and post it as a single sticky comment layered on top of (never replacing) the bots' own comments. The "judge" over the finders: it consolidates, it never produces findings of its own. Use when you (or work-driver) want one pane + one merge decision instead of reading four separate bot comment streams. Triggers: "consolidate the reviews on PR <n>", "what's the verdict on PR <n>", "judge the bot findings", "/review-coordinator <n>". NOT a reviewer itself — pair it AFTER the bots have reviewed.
user_invocable: true
argument-hint: "<pr-number> [--repo <owner/repo>] [--cycle <n>] [--settle fast|full] [--format json|comment|both]"
---

# /review-coordinator — the judge over the four AI reviewers

Given a PR that the AI reviewers (Codex, Claude, Cursor Bugbot, GitHub Copilot) have commented on, produce **one consolidated verdict**: a deduped, severity-ranked finding list and a `block`/`go` merge gate. Emit it two ways — a **JSON verdict** (for a calling agent / a future required check) and a **sticky comment** (for the operator's glance), layered on top of the bots' comments.

This skill is a **pure judge**. It reads what the bots already said and organizes it. It **never produces findings of its own** and (in v1) **makes no judgment calls** about whether a finding is real — it only collects, normalizes, groups, ranks, and presents. That is deliberate: a judge that can't suppress is a judge you can trust. (Refuting false positives is v1.5's job — see § Not in v1.)

The pipeline below is the whole skill; each step explains its own rationale.

## When to use

- "consolidate / judge the reviews on PR `<n>`" · "what's the verdict on PR `<n>`" · "/review-coordinator `<n>`"
- Called by `/work-driver` at a review-cycle settle point (it owns the policy — re-ping, 3-cycle cap, merge; this skill owns the mechanism — the verdict).

**Anti-trigger:** don't use this *as* a reviewer. It runs **after** the bots, not instead of them. If no bot has reviewed yet, there's nothing to consolidate.

## Arguments

`/review-coordinator <pr-number> [--repo <owner/repo>] [--cycle <n>] [--settle fast|full] [--format json|comment|both]`

- `<pr-number>` — required.
- `--repo` — default: infer from the cwd's `origin` remote (`gh repo view --json nameWithOwner`).
- `--cycle` — review-cycle index (work-driver passes this; default 1). Feeds the merge-patience rule (Step 3).
- `--settle` — `fast` (default: fire on fast quorum or timeout) vs `full` (wait for all expected bots up to the long timeout). See Step 1.
- `--format` — `both` (default: JSON + sticky comment), `json` (programmatic only), or `comment` (operator glance only).

## The five-step pipeline

Work through these in order. Steps 2–4 are pure mechanical transforms — no judgment about finding validity.

### Step 0. Resolve + identify the expected bots

1. Resolve `<owner/repo>` (from `--repo` or `origin`) and the PR's current `head_sha`: `gh pr view <n> --json headRefOid,state,title`.
2. Determine which bots are **expected on this repo** — do NOT assume all four. The `expected` set is per-repo (a bot that isn't wired won't post, and that's not a failure). Known logins:
   - Codex → `chatgpt-codex-connector[bot]`
   - Copilot → `copilot-pull-request-reviewer[bot]` (formal review) / `Copilot` (inline comment author) — same bot
   - Cursor Bugbot → `cursor[bot]`
   - Claude → `claude[bot]`
   - Confirm empirically on a new repo; treat any `user.type == "Bot"` with an unknown login as a possible reviewer and note it rather than dropping it silently.

### Step 1. Settle — decide when to read (don't wait on the slow bot)

The bots are async (Codex can take 3–14 min; Copilot/Claude/Cursor usually ≤3). Don't block on the slowest.

- **`--settle fast` (default):** fire as soon as the **fast pack present on this repo** (Claude + Copilot + Cursor, intersected with `expected`) has posted on the current `head_sha`, **OR** a ~3-min timeout elapses — whichever first. Record any bot not yet in as `pending`.
- **The timeout is the real backstop, not the quorum** — a flaky/absent bot (e.g. Copilot's account-toggle on private repos) must never hang the run. A tiny PR where nobody finds anything fires at timeout → clean verdict → `go`.
- **`--settle full`:** wait for every `expected` bot up to a ~8-min timeout. Used for the merge-patience case (Step 3).
- **"Posted" ≠ "done" — but distinguish *in-progress* from *finished-clean*.** A bot can post a comment *before* it has findings: Claude's GitHub-App reviewer posts a checklist stub ("- [ ] Read changed files … - [ ] Post findings" + a "View job run" link) within seconds, then edits/replaces it once done. Treat **only an explicit in-progress signal** as still `pending`:
  - unchecked `- [ ]` task boxes, or a "reviewing…" / "Claude is working…" status, **with no findings yet** → `pending` (wait for the finished review).
  - **A *completed clean* review is SETTLED, not pending** — "LGTM", Codex's "Didn't find any major issues", Claude's all-boxes-*checked* summary with no flagged issues. These are a finished bot reporting zero findings; settle on them immediately (Step 2 drops them as non-findings). Do NOT hold a clean-but-done bot in `pending` until timeout — that's the over-broad reading and it defeats fast settle, especially on the `--settle full` merge path.

  Heuristic: *unchecked* boxes / "working" status = in progress (`pending`); *checked* boxes / "finished" / "no issues" / "LGTM" = settled (even with zero findings).

In an interactive session you may simply read what's already posted (the operator usually invokes this once the bots have landed). The settle logic matters most for the headless/work-driver path.

### Step 2. Ingest — read all three endpoints

A finding can live in any of three places. **Read all three** — Codex line comments live in `pulls/comments`, NOT issue-comments; miss an endpoint and you miss P1 flags.

**Always `--paginate`.** GitHub paginates list responses (~30 items/page). Without it you only see page 1, and on a busy PR a later P1/blocking finding falls off the back — the coordinator would then emit `gate: go` while a blocker exists. Pagination is a *correctness* requirement for the gate, not an optimization.

```
gh api --paginate repos/<o>/<r>/pulls/<n>/reviews   --jq '.[] | {login:.user.login, state:.state, body:.body}'
gh api --paginate repos/<o>/<r>/issues/<n>/comments --jq '.[] | {login:.user.login, body:.body}'
gh api --paginate repos/<o>/<r>/pulls/<n>/comments  --jq '.[] | {id:.id, login:.user.login, path:.path, line:.line, body:.body}'
```

**Optional local pre-pass on the inline endpoint (free, offline).** `pulls/comments` is where the
dense finding bodies live. If a local reviewer-extraction CLI is available (see `/review-digest`),
run it first — it extracts each comment's headline + the bot's own stated severity, one local-model
call per comment:

```
"$REVTRIAGE_BIN" -json -repo <o>/<r> <n>
```

Each row is `{comment_id, file, line, bot, severity, verdict, confidence, headline}`. Because this
skill's output **gates merges**, the digest pre-populates findings under two deterministic checks —
it never replaces the endpoint reads:

1. **Coverage** — still fetch the `pulls/comments` *listing* (the jq above; ids + metadata, no
   deep-reading). Every expected-bot comment id must have a digest row; any gap → read that
   comment body directly.
2. **Distrust the un-checkable row** — low `confidence`, or a severity of `unknown` from a bot
   that does emit labels (codex/cursor), or a headline that doesn't correspond to the comment's
   own title → read that comment body directly. (`unknown` from Copilot is normal — don't invent
   a severity.)

A wrong extraction can then only cost one direct read; it can never flip the gate. The digest
covers ONLY the inline endpoint — reviews and issue comments (endpoints 1–2) are read as before.
No local model running? Skip the pre-pass; this step works as before (read everything). Digest
`severity` feeds the severity-normalization step as `severity_raw` unchanged (it's the bot's own
scale: P1/P2, High/Medium, blocking).

Keep only authors in the `expected`-bot set. **Drop non-findings:**
- Boilerplate wrappers: Codex's "💡 Codex Review" header, Cursor's "Skipping Bugbot…" / `<!-- BUGBOT_REVIEW -->` header with no finding, "no major issues", any "LGTM".
- Bot status reactions, the operator's own `@bot review` pings and triage replies.
- This skill's own prior sticky comment (match the marker, Step 5).

Each surviving comment becomes a raw **Finding**: `{source, severity_raw, file, line, title, body, source_url, endpoint}`. Use the comment's `html_url` as `source_url` (attribution — every finding links back).

### Step 3. Normalize severity — four scales → one

Map each bot's native severity to one shared scale. **Each raw value maps to exactly ONE normalized level** — the mapping is a function, not a menu. (An ambiguous raw→two-levels mapping lets an agent pick the non-gating row for a real blocker and greenlight it. Every raw value below appears on exactly one row.)

| Normalized | Codex | Claude | Copilot | Cursor |
|---|---|---|---|---|
| **critical** | P0 | 🔴 important | High | **blocking** |
| **high** | P1 | (Claude has no distinct "high" — 🔴 → critical) | (Copilot has no distinct "high" — High → critical) | (Cursor has no "high" — blocking → critical) |
| **medium** | P2 | 🟡 nit | Medium | **non-blocking** |
| **low** | P3 | 🟣 pre-existing | Low | (Cursor has no "low" — non-blocking → medium) |

Deterministic rules, no judgment:
- **Cursor** is binary: `blocking → critical`, `non-blocking → medium`. Never anything else. (This is the gate-relevant one — Cursor `blocking` MUST land in the critical bucket so Step 4 gates on it.)
- **Codex:** `P0/P1 → critical`, `P2 → medium`, `P3 → low`. (Earlier drafts split P1 by "security/correctness"; that needs judgment — drop it. P1 → critical, full stop. Codex already filters P2/P3 off GitHub mostly, so most Codex findings you see are P1 → critical anyway.)
- **Claude:** `🔴 important → critical`, `🟡 nit → medium`, `🟣 pre-existing → low`.
- **Copilot:** `High → critical`, `Medium → medium`, `Low → low`.
- **No label?** Default to **medium** (never critical). When unsure between two levels, round **down** — over-escalation erodes gate trust faster than under-escalation (the gate is high-threshold by design).

> There is no separate "high" tier in v1: the four bots don't cleanly distinguish critical-vs-high, and a phantom tier between "blocks" and "advisory" just invites the pick-the-wrong-row bug. Two gate-relevant buckets only — **critical (blocks)** and **everything else (advisory)** — keep the gate unambiguous. (A real high/critical split can come in v1.5 alongside the FP-filter, if it earns its place.)

### Step 4. Group by location, then rank by agreement

1. **Group** findings whose `(file, line-range)` overlap (within ~5 lines, same file). Where `line` is null (file-level comment), group by `file` + same substantive issue. Each group is a **ConsolidatedFinding** with an `agreement` count = number of distinct bots in it.
   - **Grouping is line-distance only — deterministic, no semantic judgment.** Two findings that are the *same theme* but far apart in the file (e.g. the same `JSON.stringify`-returns-undefined risk at line 47 and line 163) stay **separate** in v1. That's correct and intended: semantic "same issue" merging needs an LLM, which is v1.5, not v1. Resist the urge to hand-merge by theme.
2. **Dedup here is rank-by-agreement, not compression.** With findings mostly unique, groups of size >1 are rare and *valuable*: two bots independently flagging the same line is the strongest "this is real" signal available without an LLM. A group's **rank severity** = max() of its members.
   - **But show the severity SPREAD, not just the max.** Bots routinely *agree on the location and disagree on severity* (e.g. one location drawing Cursor=blocking, Copilot=Medium, Codex=P3 — i.e. critical/medium/low). max() is right for ranking, but collapsing to it alone hides that 2 of 3 bots thought it minor. Carry each member's own *raw* label through to the output (e.g. "Cursor:blocking · Copilot:Medium · Codex:P3") so the reader sees the disagreement. Adjudicating it is v1.5's job (contradiction resolution) — v1 surfaces it honestly, doesn't resolve it.
3. **Rank** by `(rank-severity desc, agreement desc)`. Critical-and-corroborated floats to the top.
4. **Bucket** into exactly two (no third tier — see Step 3):
   - **critical** — normalized `severity == critical`. This is the ONLY block-worthy bucket. Includes any Cursor `blocking`, Codex `P0/P1`, Claude `🔴`, Copilot `High`.
   - **advisory** — everything else (medium + low). Never gates.

**Merge-patience (keys on green-while-slow-pending, NOT cycle number):** if the bucketing would yield `gate: go` **while a slow-pack bot (Codex) is still `pending` on the current `head_sha`**, do NOT emit `go` yet. Re-run with `--settle full` (wait up to ~8 min for Codex) before greenlighting. The fast path still governs *iteration* (start fixing the fast pack's findings immediately); the patient path governs *merge*. This covers cycle 1 and every later final pass uniformly.

### Step 5. Emit — JSON verdict + sticky comment

**JSON verdict** (the machine-readable product — `--format json|both`):

```json
{
  "pr": <n>, "head_sha": "<sha>", "cycle": <c>,
  "settled_on": ["claude","copilot","cursor"], "pending": ["codex"],
  "critical": [ {"file","line","title","severity","agreement","sources":[{"bot","url"}]} ],
  "advisory": [ ... ],
  "gate": "block" | "go",
  "gate_reason": "2 critical correctness findings" | "clean" | "..."
}
```

`gate = block` iff `critical` is non-empty (or, once Phase 4 lands, a `semgrep-critical` is present). Else `go`.

**Sticky comment** (the operator glance — `--format comment|both`): create-or-update a single comment on the PR. Find the existing one by its hidden marker and PATCH it (don't post a new one each cycle); else create it.

- Marker (first line, HTML comment): `<!-- review-coordinator-verdict -->`
- **Layer on top — never edit or delete the bots' own comments.** Attribution stays intact; every consolidated finding links back to its source bot comment(s).
- Suggested shape:

```markdown
<!-- review-coordinator-verdict -->
## 🧑‍⚖️ Review verdict — `<gate>` (cycle <c>)

**Gate:** <BLOCK ❌ / GO ✅> — <gate_reason>
Settled on: <bots>. Pending: <bots or "none">.

### Critical (<count>)
1. **<title>** — `<file>:<line>` · <agreement N✕: Cursor:High · Copilot:med · Codex:P3>
   <one-line gist> · <links to each source comment>

### Advisory (<count>)
- **<title>** — `<file>:<line>` · <bot:severity> · <link>   <!-- top-N in full; rest as a collapsed count -->

<sub>review-coordinator consolidates the bots' findings; it doesn't add its own. Source comments are unchanged above.</sub>
```

Render top criticals in full; collapse a long advisory tail to "+N more advisory (see bot comments above)" to keep the comment scannable.

Auth: in a GitHub Action, `GITHUB_TOKEN` with `pull-requests: read` + `issues: write` (sticky comment) + `checks: write` (the Phase-6 required check). Locally, the operator's `gh` auth covers it. The skill's own comment won't re-trigger a GHA coordinator (GitHub blocks token-authored recursion).

## How work-driver calls this (dispatch by N)

- **N=1 PR:** run inline — the findings stay hot in the driver's context for immediate fixing.
- **N≥3 PRs:** dispatch one subagent per PR (each ingests that PR's comments and returns just the clean verdict JSON), so the driver isn't juggling multiple raw comment dumps. Mirrors work-driver's existing sub-agent-per-PR review strategy.

The coordinator returns the verdict; **work-driver owns the policy** — whether to fix-and-re-ping, where the 3-cycle cap sits, and when to merge. This skill never merges, never pings, never decides cycles.

## Not in v1 (deliberately deferred)

- **No false-positive filtering.** v1 presents every finding (ranked); it never judges a finding false and suppresses it. The adversarial refute pass that *demotes (never deletes)* single-bot findings is **v1.5**.
- **No cross-cycle dedup.** Suppressing findings already fixed in a prior cycle (Copilot re-posts these) is v1.5.
- **No SAST.** The deterministic injection gate (Semgrep/CodeQL) is Phase 4.
- **No script.** v1 is this prose, executed by the agent. If a step proves non-deterministic enough to bite or too costly in context (watch Step 4's line-overlap grouping first), that's the signal to extract *that step* into a small script — earned, not pre-built.

## Worked example

A representative run, to ground the pipeline. A PR draws 3 bots — Codex, Copilot, Cursor (no Claude this time; not every bot reviews every PR, so `expected` ≠ all four).

- **Ingest:** drop the non-findings (Copilot's PR-overview summary, Codex's "💡 Codex Review" wrapper, Cursor's `<!-- BUGBOT_REVIEW -->` header). Say 8 real findings survive across the line-comment endpoint.
- **Group:** the headline bug draws **3-bot convergence** at `handler.ts:225–230` (Cursor, Copilot, and Codex all flag the same defect within ~5 lines) — one group, agreement = 3. A 2-bot group at `runner.ts:208–217` (Copilot + Codex, same memory issue). Three singletons elsewhere. Note: two findings of the *same theme* (e.g. a `JSON.stringify`-returns-`undefined` risk) but 100+ lines apart stay **separate** — line-distance rule; semantic merge is v1.5.
- **Severity spread:** the convergent group is **Cursor:blocking · Copilot:Medium · Codex:P3** (→ critical/medium/low) — agreement on *location*, disagreement on *severity*. Rank severity = critical (the max); output shows all three raw labels so the disagreement stays visible.
- **Verdict:** `gate: block` (Cursor `blocking` → critical bucket → block). Ranked #1 is the convergent bug, then the 2-bot memory issue, then the singletons.
- **Honest read:** `gate: block` here is v1 working as designed (honor the bot's severity; don't second-guess it). Whether a single bot's "blocking" *should* gate the merge is a v1.5/tuning question, not a v1 bug — v1's job is to *surface* faithfully, not adjudicate.

## Key reminders

- **Read all three endpoints.** Codex P1s hide in `pulls/comments`.
- **`expected` bots are per-repo.** Absent ≠ weak. Don't hang waiting for a bot that isn't wired here.
- **Timeout is the backstop.** Never block indefinitely on the slow bot; record it `pending` and move on.
- **Round severity down when unsure.** A trustworthy gate is a high-threshold gate.
- **Layer, never overwrite.** The bots' comments stay; the verdict sits on top and links back.
- **Pure judge.** No findings of its own; no validity judgments in v1.
- **Weight a low-volume bot by unique-valid-where-present, not raw count** — a reviewer that comments rarely but owns a niche (e.g. CI/workflow security) isn't weak; absence on a given PR ≠ weakness.

## Outcome

After a run: one sticky verdict comment on the PR (deduped, severity-ranked, links back to every source) + a JSON verdict the caller can act on / a future required check can gate on. The operator (or work-driver) reads one pane and makes one merge decision instead of triaging four comment streams by hand.
