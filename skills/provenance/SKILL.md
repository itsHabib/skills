---
name: provenance
description: >-
  Per-PR attribution report — which pipeline produced each merged PR
  (engine-cloud / engine-local / seat-hand-driven / human) plus model, provider,
  effort, and review cycles, derived from ship's driver store, PR-body
  Provenance footers, and commit trailers. Turns tool usage into numbers instead
  of vibes. Use when the operator asks "which pipeline produced these PRs",
  "how much of this repo did the engine ship", "attribution report",
  "provenance report", "what share of PRs are agent-authored", or invokes
  /provenance [repo] [--since date | --limit N]. Add --by-model for a
  per-implementer-model rollup — which model earns its keep: correction rounds,
  driver interventions, panel findings, tracelens verdict, and a
  cost-per-useful-PR headline, scoped to a driver batch via --manifest or
  windowed over the store. Triggers on "which model earns its keep", "model
  comparison", "model scorecard", "cost per useful PR", "compare implementer
  models". Also defines the Provenance PR-footer convention every seat-authored
  PR must carry going forward.
argument-hint: "[repo ...] [--since YYYY-MM-DD | --limit N] [--by-model [--manifest <driver.md> ...]] — e.g. /provenance, /provenance ship --limit 20, /provenance --by-model --manifest docs/features/model-lottery/phase3/driver.md"
user_invocable: true
---

# /provenance — which pipeline produced each PR

One table that answers "what actually built this repo": for every merged PR, the
pipeline (engine-cloud / engine-local / seat-hand-driven / human), the model and
provider that did the work, the effort tier, and how many review cycles it took.
**Derived, not declared** — ship's driver store is ground truth for engine runs,
the `Provenance:` PR footer for seat runs that stamped one, commit trailers as
the fallback. Nothing is stamped retroactively; older PRs classify on trailers
alone and that's fine.

Read-only everywhere: SQLite opened readonly, `gh` reads only. No new MCP verb,
no daemon, no GitHub Action (skills compose; this is a cross-store join).

Two views over the same join: the default **per-PR** ledger below, and a
**per-model** rollup (`--by-model`) that pivots the same data to answer "which
implementer model earns its keep" — see [Per-model rollup](#per-model-rollup---by-model).

## Inputs

- `repo ...` — one or more repos, `name` (assumes `itsHabib/<name>`) or `owner/repo`.
  Default portfolio set: `ship`, `workbench`.
- `--limit N` — last N merged PRs per repo (default 15).
- `--since YYYY-MM-DD` — alternative window; overrides `--limit`.

## Procedure

### 1. Resolve ship's store (per-platform; mind the Windows MSIX split)

`SHIP_DB_PATH` always wins when set. Otherwise the store is per-platform.

**macOS / Linux:**

```bash
DB="${SHIP_DB_PATH:-$HOME/.config/ship/state.db}"
[ -f "$DB" ] || { echo "ship store not found at $DB (set SHIP_DB_PATH)" >&2; exit 1; }
```

**Windows:**

```
$db = $env:SHIP_DB_PATH
if (-not $db) { $db = "$env:APPDATA\ship\state.db" }   # terminal sessions → real Roaming
```

On Windows, if that file is missing and the session was launched by Claude
Desktop (connector), the canonical store is the virtualized one:
`%LOCALAPPDATA%\Packages\<claude-desktop-pkg>\LocalCache\Roaming\ship\state.db`.
That MSIX split is Windows-only — it has no macOS/Linux equivalent.

Prefer `SHIP_DB_PATH` whenever it's set; report which store you read.

### 2. Pull engine facts (one query, keyed by pr_url)

Query with node + ship's own better-sqlite3 (no new deps). Resolve `$SHIP` to the
first path that exists — never hardcode a portfolio root:

```bash
export SHIP=$(for c in "${SHIP_REPO:-}" "$HOME/dev/ship"; do [ -d "$c" ] && echo "$c" && break; done)
[ -n "$SHIP" ] || { echo "ship repo not found (set SHIP_REPO, or clone to ~/dev/ship)" >&2; exit 1; }

node -e "const D=require(process.env.SHIP + '/packages/store/node_modules/better-sqlite3');
const db=new D(process.argv[1],{readonly:true});
console.log(JSON.stringify(db.prepare(\`
  SELECT pr_url, pr_number, runtime, provider, dispatch_provider, dispatch_model,
         dispatch_model_params, model_tier, effort_tier, effort_degraded,
         cycles, merged_at, task_slug
  FROM driver_streams WHERE pr_url IS NOT NULL\`).all()));" "<db-path>"
```

(If migration 0014 has landed, also select `review_cycles` and prefer it over
`cycles` for the cycle count — `cycles` is seat-reported at land time,
`review_cycles` is engine-incremented per `driver address` dispatch.)

### 3. Pull merged PRs per repo

Choose the query from the requested window. `--since` overrides `--limit` and
must not inherit its cap:

```
# --limit mode
gh pr list --repo <owner/repo> --state merged --limit <N> \
  --json number,title,mergedAt,url,body,author

# --since mode — gh paginates internally up to the requested maximum
gh pr list --repo <owner/repo> --state merged --limit 1000 \
  --search "merged:>=<YYYY-MM-DD>" \
  --json number,title,mergedAt,url,body,author
```

Validate the date before calling `gh`, and filter the returned `mergedAt` values
against the same UTC boundary as a defensive check. If a repo can exceed 1000
merges in the window, switch this branch to `gh api graphql --paginate`; never
silently fall back to the unrelated `--limit N` window.

For PRs not matched in step 2, fetch classification evidence lazily (only the
unmatched ones — keep `gh` calls bounded):

```
gh pr view <n> --repo <owner/repo> --json commits,comments
```

### 4. Classify each PR (first match wins)

1. **Engine** — `url` (or number) matches a `driver_streams.pr_url` row →
   pipeline `engine-<runtime>` (`engine-cloud`, `engine-local`);
   model = `dispatch_model`, provider = `dispatch_provider`,
   effort = the `effort` entry of `dispatch_model_params` (cursor) or the
   `reasoning` entry (claude), falling back to `effort_tier` (+ `!` suffix when
   `effort_degraded`); cycles = `review_cycles` ?? `cycles`.
2. **Footer** — PR body contains a `Provenance:` line → parse its
   `key=value` fields verbatim (see convention below); pipeline is whatever the
   footer declares (normally `hand-driven` → report `seat-hand-driven`).
3. **Trailers** — commit messages carry
   `Co-authored-by: Cursor <cursoragent@cursor.com>` → `seat-hand-driven`
   (provider cursor, model unknown); `Co-Authored-By: Claude <model>` →
   `seat-hand-driven` (provider claude, model from the trailer). Matching is
   case-insensitive.
4. **Human** — none of the above.

Cycles for non-engine PRs: count `@codex review` trigger comments (one per
panel cycle, the seat's own convention) — 0 comments on a reviewed PR = 1 cycle
(single pass, early ship-it). When comments weren't fetched, leave the cell `—`
rather than guessing.

### 5. Emit the report

One table per invocation (all repos merged together, repo column when >1),
newest first, then one totals line:

```
| PR | repo | merged | pipeline | provider | model | effort | cycles |
|----|------|--------|----------|----------|-------|--------|--------|
| #184 | ship | 07-09 | engine-local | claude | claude-opus-4-8 | high | 1 |
| #183 | ship | 07-09 | seat-hand-driven | claude | claude-fable-5 | auto | 3 |
...
Totals: N PRs — engine-cloud X · engine-local Y · seat-hand-driven Z · human W; agent-authored share P%
```

Flag in one line anything anomalous (engine row whose PR isn't merged, footer
that contradicts trailers) — don't silently reconcile.

## Per-model rollup (`--by-model`)

The same cross-store join, pivoted by **implementer model** instead of by PR — the
read side of the model-lottery experiment: *which model earns its keep*. Derived from
data the pipeline already emits; adds no instrumentation. Reproduces the hand-written
per-model verdict tables (the runway grok-4.5 readout, the model-lottery Phase 3 trio)
so they never get hand-edited again.

### Scope

- `--manifest <path> ...` — scope to a driver batch (one experiment). The manifest
  frontmatter `streams:` is the authoritative stream→model map and **wins over the
  store when the store under-counts**: a flip-failed stream merged out-of-band shows
  `failed` (or no row), but the manifest still names its model. The manifest also
  locates the address dossiers (same directory). This is the acceptance path — point
  it at `docs/features/runway-1-local-controller/driver.md` (workbench) or
  `docs/features/model-lottery/phase3/driver.md` (ship).
- No `--manifest` — window-scoped: every engine stream in the `--since` / `--limit`
  window, grouped by model. "How do my models compare across recent work."

### Extra inputs (beyond the per-PR join in steps 1–4)

1. **Manifest frontmatter** — `streams[].{task_slug, model_id, pr_number, provider}`
   plus `assignment.effective_pool`. Structured; **never parse the prose ledger
   table** — that hand-written table is the thing this rollup replaces.
2. **Address dossiers** — `<manifest-dir>/address-<streamId>-cycle<N>-<sha12>.md`, one
   per engine correction round (`driver address` writes them there). Each lists the
   findings it addressed, tagged `[block]` / `[medium]` / `[minor]`, with a `Sources:`
   block (which bot, which PR). Present only for engine-driven rounds — **absent for
   out-of-band drives** (the Phase 3 case); fall back to gh review comments there.
3. **PR commits** (`gh pr view <n> --json commits`) — a commit whose author login is
   NOT the dispatched agent (`cursoragent` for cursor; the claude-runner bot for
   claude) is a **driver intervention**: a seat hand-fix beyond dispatching the agent.
   Count them per PR. This is a **lower bound** — several logical fixes (a CI fix, a
   doc fix) can share one commit, so the count trails a per-fix hand-tally; it is
   reproducible and never over-counts. (Validated: the runway escalated PR shows
   exactly the two `itsHabib`+`claude` commits the hand-ledger recorded as the
   driver's final round.)
4. **`cursor_runs.duration_ms`** — real agent wall-clock, joined
   `driver_streams.workflow_run_id` → `cursor_runs.workflow_run_id`. Fallback
   `created_at` → `merged_at` (import-to-merge) when there's no run row.
5. **tracelens** (best-effort) — per stream that has a resolvable workflow-run id:
   `tracelens ship -json <wf-id>` — prefer the installed binary; tracelens is a workbench
   tenant, so the fallback is `go run ./cmd/tracelens ship -json <wf-id>` from the workbench
   repo (needs a Go toolchain + the run's `events.ndjson` under
   `${SHIP_RUNS_DIR:-<config-home>/ship/runs}/<wf-id>/`). Take `decision`
   (`block`|`escalate`|`pass`) and the `findings` list (severity + pathology kind, which
   lives in the finding `title`). **The verdict is not self-keyed** (its `subject` is
   zero) — carry the wf-id yourself and associate the result with the stream. `—` when
   Go or the run dir is absent.

### Reconcile merge state against gh — never trust store status alone

The store under-counts flip-failed batches: a stream can read `failed` /
`awaiting_judgment` in `driver_streams` yet be merged on GitHub (the draft→ready flip
blipped and the seat merged out-of-band). **Merge facts come from gh**
(`gh pr view <n> --json state,mergedAt,mergeCommit`); attribution comes from the
manifest + store. When store status and gh disagree, use gh and **flag the row** —
never drop a merged stream because its store row says `failed`.

**Key streams on `pr_url`, not `pr_number`.** On a flip-failed row `pr_number` is
`NULL` while `pr_url` is still set (the URL is written at PR creation, the number
column later) — so parse the number out of `pr_url` and key on that. A store row whose
`error_message` starts `draft→ready flip failed` is the signal that this stream was
driven out-of-band; expect its `merged_at`/`review_cycles` to be `NULL` and derive
those from gh. (Miss this and the tool silently drops exactly the streams the
under-count caveat is about.)

### Per-model derivation (roll each model's streams up)

| metric | source (→ fallback) | cell is `—` when |
|---|---|---|
| streams / merged | with `--manifest`: manifest `streams`; without: the store window (`driver_streams` over `--since`/`--limit`) — either × gh merged-state | never (both scopes carry a stream source) |
| rounds | `review_cycles ?? cycles` (store); cross-check address-dossier count | no store row and no dossiers |
| driver interventions | non-agent-authored PR commits (gh) | commits not fetched |
| findings B/M/m | address-dossier severity tags → gh review-comment badges | neither present |
| wall-clock | `cursor_runs.duration_ms` → `created_at`→`merged_at` | no `workflow_run_id` and unmerged |
| tracelens | `tracelens ship -json <wf-id>` decision + findings | Go / run dir absent |

**Cost.** Ship's store persists no tokens and no dollar cost — confirmed absent from
`driver_streams`, `cursor_runs`, and every other table. The headline is therefore a
**correction-cost proxy**, the same currency both hand-written verdicts already used:

```
correction-cost per useful PR = (rounds + driver interventions) / merged PRs
```

Lower earns its keep. Report wall-clock as a **separate** latency axis — a model can be
cheap-to-correct but slow, or fast but correction-heavy (the grok pattern: ~10-min PRs,
zero boundary violations, but every stream shipped Windows-broken round 1). Never impute
a dollar figure. If per-step token telemetry ever lands in the store, swap the proxy for
real cost-per-useful-PR and keep the same table.

### Emit

One row per model, newest-experiment-first, then a one-line reading each:

```
| model | provider | effort | streams | merged | rounds | driver interventions | findings B/M/m | tracelens | wall-clock | corr-cost/PR |
|-------|----------|--------|---------|--------|--------|----------------------|----------------|-----------|------------|--------------|
| grok-4.5 | cursor | max | 3 | 3/3 | 6 | 6 | 19/10/6 | escalate | ~10m | 4.0 |
```

(`effort` carries the `!` degraded suffix from step 4.) After the table, one line per
model on *where* its cost fell — CI vs review vs escalation — the "reading the ledger"
prose the hand tables carried. Close with only the caveats that actually applied this
run: store under-count reconciled via gh, any tracelens cell that went `—`,
effort-degraded models, and single-stream-per-model samples (n=1 — a signal, not a
result). Flag, don't smooth over, any store/gh disagreement.

## The `Provenance:` footer convention

Every **seat-authored** PR body (hand-driven by a Claude Code seat, not
engine-dispatched) ends with one machine-parseable line:

```
Provenance: seat=claude-code model=<model-id> effort=<effort> pipeline=hand-driven skills=<comma-list-or-none> offload=<what-or-none>
```

- `model` — the exact seat model id (e.g. `claude-fable-5`).
- `effort` — the session effort setting (`auto` when unset).
- `pipeline` — `hand-driven` for seat PRs. Engine PRs do NOT need the footer
  (the store already has better data); don't fight the engine for the byline.
- `skills` — skills that materially produced the change (`work-driver,tdd`),
  `none` otherwise.
- `offload` — what was offloaded to the local model (qwen) during the work,
  `none` otherwise. This is the one un-derivable input; the footer is its only
  record. Nothing heavier gets built for it.

One line, no markdown formatting around it, placed after the standard
`🤖 Generated with...` attribution. Never stamped retroactively onto old PRs.

## Anti-triggers

- "what's in flight" → `/wip` · "what just shipped" → `/shipped`
- Per-PR review-risk routing → `/pr-risk`
- Anything requiring a write to GitHub — this skill never writes.
