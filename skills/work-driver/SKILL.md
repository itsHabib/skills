---
name: work-driver
description: Drive N parallel tasks end-to-end through ship's `ship driver` engine — the state machine (import → dispatch → poll → judgment → land → record) that replaced the hand-run per-stream `mcp__ship__ship` loop. Resolves dossier task IDs (or a phase, or an existing driver.md), preps specs + a conflict-batched manifest, dispatches all streams (cloud by default), handles failures via `ship driver decide`, drives the resulting PRs through review→merge, records merges back, and logs friction. `--engine session` makes THIS session a THIN orchestrator: each task's impl runs in a delegated isolated-worktree subagent (fresh context, own model), the parent holds only structured summaries + PR URLs and records every transition through workbench-mcp (parent run + child sub-runs), and the whole run is resumable from the ledger in a fresh session (≥5 tasks, single writer per sub-run). Use when you want to fire one or several tasks in parallel and have an agent drive them to merge — "drive this impl work", "drive these 3 tasks", "run this batch through ship", "parallel-ship these", "ship and merge", "fire N parallel streams", explicit /work-driver.
argument-hint: "[task-ids... | phase:<slug> | project:<slug>:phase:<slug> | <path-to-driver.md>] [--runtime cloud|local] [--engine ship|session]"
user_invocable: true
---

# /work-driver — drive parallel work through the `ship driver` engine

Drive N tasks to merge using ship's **driver engine** (`ship driver <verb>`). The engine
owns the mechanism — dispatch → poll → judgment → land → record, with durable resumable
state in its own store. This skill is the **policy wrapper**: prep, review-cycle strategy,
the merge call, merge-recording, and a friction log. No sleep-polls, no YAML-as-database,
no resume bash — those are the engine's job now, not prose for the LLM to re-derive.

## Inputs

- **Tasks:** dossier task IDs, a `phase:<slug>`, a `project:<slug>:phase:<slug>`, or a
  ready `driver.md` path. (Resolved the same way `/work-driver-prep` does.)
- **Runtime:** `--runtime cloud` (default — cursor cloud, `autoCreatePR`, no local
  worktrees) or `local` (one worktree per stream; needs the target repo's toolchain).
- **Engine:** `--engine ship` (default — ship's driver engine owns the mechanism, below) or
  `session` (THIS session is a THIN orchestrator: it delegates each task's impl to an
  isolated-worktree subagent and records every transition through `workbench-mcp` — see
  **Engine: session**). Session scope is ≥5 streams, single writer per sub-run; needing cloud
  dispatch or cross-machine orphan re-attach belongs on ship.

If no input is given, ask (via `AskUserQuestion`) for the task IDs / phase / `driver.md`
path, and the runtime if it isn't obvious.

## Flow

1. **Prep (skip if given a driver.md).** Check the tasks are file-disjoint via their
   `touches`; overlapping tasks can't share a parallel batch. Then `/work-driver-prep
   <inputs>` → one spec doc per task + a conflict-batched `driver.md` in the target repo
   (its frontmatter matches the engine's import schema, incl. `repo_url` for cloud streams).
   For **local** streams, pre-flight a worktree per stream with `/worktree-add <branch>`,
   then fast-forward each to `origin/main` so you don't dispatch against stale code:
   `git -C <wt> fetch origin && git -C <wt> merge --ff-only origin/main`. If `--ff-only`
   refuses on an untracked-file collision, handle each file deliberately (**don't** blind
   `git stash` — forgotten stashes lose drafts; `rm` it or `mv` to `<file>.bak`) or reach
   for `/worktree-transfer`. Cloud streams need no worktree — cursor cloud is the workspace.
2. **Drive via the ship CLI**, from `pers/ship`, with the cursor key set and **absolute**
   manifest paths (`pnpm --filter exec` changes cwd):
   ```
   $env:CURSOR_API_KEY = [regex]::Match((Get-Content C:\Users\MichaelHabib\pers\ship\.keys -Raw), '"cursor":\s*"([^"]+)"').Groups[1].Value
   cd C:\Users\MichaelHabib\pers\ship
   pnpm --filter @ship/cli exec tsx src/bin.ts driver <verb> ...
   ```
   - `driver run <ABSOLUTE driver.md path> --max-wait 30m --poll-interval 30s --json`
     → imports + dispatches all streams in parallel, polls. Note the `driverRunId`.
   - Re-invoke `driver run <drv_id> ...` to keep polling; exit **10** = `awaiting_judgment`.
3. **Trace verdict (advisory).** When a stream reaches terminal state, run tracelens on
   its workflow run before (or with) the judgment call:
   ```
   tracelens ship -json <workflowRunId>
   ```
   (`go install ./cmd/tracelens` from `pers/tracelens` puts it on PATH; run refs resolve
   under `%APPDATA%\ship\runs` / `SHIP_RUNS_DIR` — the store the terminal CLI writes.)
   Surface `health` + the top finding in the stream's judgment context, and record one
   verdict line per stream in the manifest notes or the dossier task note, e.g.
   `tracelens: pathological — loop: Write x6 src/foo.ts (wf_01…)`. **Advisory in v0:** it
   informs retry-vs-skip (a pathological trace argues against a blind same-spec retry —
   rescope instead) but never auto-blocks a merge or fails a stream. Exit 1 just means
   pathological — that's signal, not a step failure. Skip gracefully when the `tracelens`
   binary, the runs dir, or the run's `events.ndjson` is absent (exit 2): an advisory
   step must never break a driver run on a machine without it.
4. **Judgment.** On a failed stream: `driver decide <drv_id> <decision> --stream <ds_id>
   [--reason "..."]` (`retry` re-dispatches the same branch; `skip`/`abort` need a reason),
   then re-run. Be opinionated about retry-vs-skip — judgment is the LLM's actual job here.
5. **Land → PR → review.** Each succeeded cloud stream opened a **draft** PR; the engine
   flips it ready at the poll boundary (ship #177) — a stream parked with a flip error is
   the exception, not a prompt to hand-run `gh pr ready`. (Local streams: the agent
   auto-commits now — verify with `git -C <wt> log
   -1`; only commit + push yourself if `git status` shows uncommitted changes — then `gh pr
   create`.) Request reviewers per the target repo's **Panel from config** stanza (the
   reviewer set is the repo's `.ship.json` `review` key, never this prose): `mention`
   entries as **standalone** comments (`@<name> review` — embedded pings don't trigger
   codex), `reviewer-request` entries via `gh pr edit <n> --add-reviewer`, `auto` entries
   get nothing posted. Each cycle, **when the bots surface real findings** (≥2 bots
   flag the same thing, or any `block`-severity), call **`/review-coordinator <n>`** for the
   consolidated `block`/`go` verdict — don't hand-triage four comment streams. On a clean
   pass (all bots green, or one stray advisory nit) skip the coordinator and merge: it earns
   its keep consolidating *conflicting or voluminous* findings, not rubber-stamping a clean
   PR (the coordinator owns the ingest mechanism; the merge grant owns the cycle cap; this
   skill owns the merge call).
6. **Merge gate (dry-run advisory) → record + close.** Once per repo in the run, mint a
   merge grant, from `pers/gate` as the stable cwd (gate's default `-state` dir is
   cwd-relative and the grant only exists in the state dir it was minted into):
   `.\gate.exe grant -repo <owner/repo> -action merge -max-tier T1 -ttl 6h`
   Don't pass `-max-cycles` — gate's CLI default IS the review-cycle policy; this skill
   states no cycle number. Hold the printed `grt_…` for every gate call this run. Per PR
   per cycle, call the gate as the merge step and branch on its exit code — requiring the
   code and the JSON `outcome` on stdout to **agree** (0 ⟺ `would_merge`,
   1 ⟺ `blocked`, 2 ⟺ `parked_for_judgment`, 3 ⟺ `capability_refused`); a bare code
   with missing/disagreeing JSON is a truncated run — treat it as exit 4:
   `.\gate.exe gate -repo <owner/repo> -pr <n> -grant <grt_…>`   (never `-live`)
   - **0** `would_merge` → land via the existing ship path: `driver land <drv_id> --pr <n>`
     (ship merges, reads sha/time back from gh, records), then dossier `task_complete` +
     `artifact_link` the merge commit.
   - **1** `blocked` → stop the stream; do not merge. Red stays red.
   - **2** `parked_for_judgment` → read the JSON: a **ceiling park** (a coded tier- or
     cycle-over-ceiling) resolves by re-minting a wider grant (`-max-tier` /
     `-max-cycles`) and retrying — **a re-mint, never a judge, never `--admin`**; the
     over-cap park is the "ping the operator" moment, not a prompt to loop. A **content
     escalation** resolves by `gate judge -run <run_…> -grant <grt_…> …` (a judge can
     pass an escalation but can never clear a ceiling).
   - **3** `capability_refused` → grant expired/mis-scoped; re-mint and retry once.
   - **4** error → surface it; no merge.
   Gate is **advisory dry-run** here: it records the decision but never executes a merge
   (`-live` stays off until its preconditions land); ship's `driver land` remains the
   merge writer. Advisory means gate doesn't *merge* — not that it's optional: gate is a
   **required** step of the merge tail, and a missing binary is a setup error to surface,
   not a step to skip. Resolve it as `pers/gate/gate.exe`, built there via
   `go build -o gate.exe ./cmd/gate`. `driver status <drv_id> --json` /
   `driver render <drv_id>` to track. All streams merged → the run self-finishes to
   terminal `done`.

## Engine: session (`--engine session`) — the THIN orchestrator

The session is the engine, but a **thin** one: it runs the state machine and records every
transition, while each task's **impl runs in a delegated subagent** — its own isolated git
worktree, fresh context, and model. The parent holds only task state + each child's structured
summary + its PR URL. Heavy context (files, diffs, test output) lives and dies in the child, so
orchestrator context grows `O(#tasks)`, not `O(Σ diffs)`. Design contract: workbench
`docs/features/session-orchestrator/spec.md` (extends `session-engine-skill/spec.md` and
`driver-state/spec.md` §4/§7).

**Scope: ≥5 streams, single writer per SUB-RUN.** The old inline engine capped at N≤3 because
it held every task's impl context at once; the thin orchestrator moves that ceiling. Each child
writes its OWN sub-run ledger under its OWN lease, so parallel children never contend
(`ErrLocked` between siblings can't happen). Needing cloud dispatch or cross-machine orphan
re-attach is still the signal to use `--engine ship`.

### The two-ledger model

- **Parent run** (`dsr_P`) — orchestration altitude, `O(#tasks)`, resumable. Records the
  manifest and a **coarse mirror** per stream (`stream_dispatched {child_run}` →
  `stream_attempt {terminal, commit}` → `stream_pr_opened` → `stream_merged`) built from each
  child's structured return. This is an ordinary driver run — the state machine is unchanged.
- **Child sub-run** (`dsr_Ca`) — impl altitude, `O(diff)`, disposable. The subagent mints it
  (`run_imported` carrying `parent`/`parent_stream`) and records its own detail: dispatched
  (with `worktree_conflict`), attempts (retries), pr_opened, review cycles. Friction lives here.
- Join them with **`driver_rollup {run: dsr_P}`** — one row per stream: parent status, child
  status, PR, friction, and `agrees` (false = the parent recorded ahead of the child's facts).

### 0. Grant + credentials first

Resolve a live, operator-minted gate grant for a **merged**-boundary pers/ repo before
dispatching (`grep '"kind":"grant"' ~/pers/gate/state/log.jsonl | tail -5`, check repo +
`expires_at`). Absent/expired → PARK and emit the exact
`gate grant -repo <r> -action merge -max-tier <T> -ttl <d> -state ~/pers/gate/state` for the
operator. **Never mint.** Work repos and `pr-open`/`green`-boundary local repos: gate does not
apply — state which Claude token + gh account the run uses, get confirmation, drive to the
boundary, stop.

### 1. Done-boundary (per run) — pick it up front

The manifest's `done_boundary` decides how far each stream is pushed (spec §4 D7):

- **`merged`** (pers/ default): drive through the panel → gate → merge; parent records
  `stream_merged`; all streams terminal → `run_finished`.
- **`pr-open`** (local-only / human-merge repos): drive to an open PR and STOP — no bot
  reviewers, no gate merge. The stream sits at `pr_open`, so the parent run stays `open`
  legitimately (the human merges later). Never fabricate `run_finished`.
- **`green`**: like `pr-open` but wait for the repo's local gate/CI to report green first.

Never bake a cloud-reviewer or auto-merge dependency into the drive — the boundary is the switch.

### 2. Reconcile before dispatch (GIT IS TRUTH)

Before dispatching ANY task, cross-check live git — trusting tracker/dossier status is the
failure that a baseline run hit (tracker said "backlog" while the work was already pushed and
open as a draft PR). For each task: `git ls-remote --heads origin '*<ticket-or-branch>*'` and
`gh pr list --search '<ticket-id or touched path>' --state open`. A match is **adopted** — record
its branch/PR as the stream's dispatch (`stream_dispatched {branch, child_run?}` +
`stream_pr_opened` from the live PR), never re-dispatched. An ambiguous match → surface to the
operator. Only a clean no-match dispatches a fresh child. On resume this same rule adopts a
branch/worktree the ledger names that already exists.

### 3. Dispatch each task to an isolated-worktree subagent

Per task (up to the batch's file-disjoint width), spawn `Agent(isolation:"worktree",
model:<tier>)` with the **per-task impl contract** (below). Record `stream_dispatched
{engine:"session-orchestrator", child_run}` on the parent as each child returns its sub-run id.
Consume ONLY the child's structured return — never read its raw impl context.

### 4. Record via `driver_transition` (no id minting)

Record every transition with **`mcp__workbench__driver_transition`** — pass `{run, kind,
stream, actor, facts}` and the server builds the body, mints a **deterministic** id from the
transition's natural key, and stamps the time. A retry with identical facts is idempotent by
construction, so there is **no client-minted `evt_` id and no reuse-on-retry discipline** (the
old `driver_record` burden). Omit `run` on a `run_imported` to mint one (facts must carry
`repo`/`source`/`generated_at`; a child import also carries `parent`/`parent_stream`). Record
each act immediately AFTER it happens — the ledger is written from facts, never ahead of them.
Actor: `session:<label>-<n>`, `<n>` incrementing per session generation (first resume = `-2`);
a resumed session MUST use a new actor. An `ErrIllegalTransition` means your picture is stale
(F2): re-read `driver_rollup`/`driver_state`, reconcile, continue — never force past it.

### 5. Resume (F3, across the parent/child boundary)

Fresh session: `driver_runs {live:true}` → pick the parent → **`driver_rollup {run}`**. The
rollup names every stream's `child_status`, `pr`, friction, and whether the parent mirror
`agrees` — the whole fan-out WITHOUT re-reading any child's impl context. For a mid-flight child
(dispatched, no PR mirrored): reconcile git (the child's `stream_dispatched.branch`/`worktree`
say where to look) → if the PR exists, mirror it up; else re-dispatch a fresh child. Never act on
ledger state alone. `driver_verify` the parent and any suspect child. State-root sanity: the MCP
server prints its root at startup and the `driverstate` CLI on every call — if you touch both,
confirm they match (`C:\Users\<user>\.workbench\driver-state` unless `WORKBENCH_STATE_DIR`).

### 6. Merge tail (merged boundary only)

Same review-cycle policy, gate step, and merge rules as below — reviews from **Panel from
config** (unconfigured repo: no review step, record one `review_cycle {cycle:1,
review:"unconfigured", panel_settled:true, findings:0}` and go straight to gate). Gate
authorizes per PR; record `stream_merged` only after the merge fact is readable from GitHub.
Expect the harness to refuse a merge of a PR this same session authored (self-approval
classifier) — that's a park: hand the operator the exact
`gh pr merge … --match-head-commit <full 40-char sha>` and record `stream_merged` after their
merge. A run that stops at a non-merge boundary (§1 `pr-open`/`green`, or a work repo) stays
`open` — do NOT fabricate `run_finished`. At that stop, **ASK** whether to leave the run open or
record a terminal handoff (`stream_skipped {reason}`); never silently close an in-flight run,
never silently leave one open without surfacing it.

## Per-task impl contract (the dispatched subagent)

Each `Agent(isolation:"worktree", model:<tier>)` gets this exact contract — it is the seam that
keeps impl context out of the orchestrator:

- **Input:** one spec path; the target repo + branch base; **the repo's local gate command set
  (passed in — never hardcoded)**; the parent run id + this task's parent stream id + the
  resolved `done_boundary`.
- **Behavior:** mint a child sub-run via `driver_transition run_imported`
  (`parent`/`parent_stream` set) → create the worktree → implement the spec → run the local
  gate → open the PR (unless the boundary is a pre-PR stop) → STOP. Record its own sub-run
  transitions as it goes (dispatched with `worktree_conflict` if the worktree/branch collided,
  each attempt, pr_opened, review cycles).
- **Output — structured, consumed by the parent as DATA (no prose beyond `oneLineSummary`):**
  ```json
  { "childRun": "dsr_…", "branch": "feat/…", "prUrl": "https://…", "gateStatus": "pass|fail",
    "gateLog": "<tail>", "filesTouched": ["…"], "oneLineSummary": "…",
    "friction": { "gateCycles": 0, "retries": 0, "worktreeConflict": false }, "blockers": [] }
  ```
The parent mirrors the stream up from this return (`stream_dispatched {child_run}` →
`stream_attempt {terminal, commit}` → `stream_pr_opened`), then drives the merged-boundary tail.
`/work-driver-task-session` is the invokable form of this contract; inline `Agent` with the same
input/output is equivalent.

## Panel from config (`.ship.json` `review` — both engines)

The reviewer set is per-repo contract, read at drive time from the target repo's
`.ship.json`:

```json
"review": {
  "panel": [
    { "name": "codex", "trigger": "mention" },
    { "name": "claude", "trigger": "mention" },
    { "name": "cursor", "trigger": "mention" },
    { "name": "copilot", "trigger": "reviewer-request" }
  ],
  "require": ["codex", "claude", "cursor"],
  "settle_minutes": 15
}
```

- `mention` → standalone `@<name> review` comment; `auto` → the bot fires on PR open, post
  nothing; `reviewer-request` → `gh pr edit --add-reviewer` (copilot needs the API form:
  `gh api repos/<r>/pulls/<n>/requested_reviewers -f 'reviewers[]=copilot-pull-request-reviewer[bot]'`
  — the `--add-reviewer copilot` login doesn't resolve).
- **Settled** = every `require` member reported, or `settle_minutes` expired — then record
  the cycle as degraded, naming the silent bots, and proceed on the signal you have.
- **No implicit default:** absent/empty `review` key = NO automated review step — no pings,
  no consolidation — recorded as `review: unconfigured` so the omission is visible. Never
  substitute a remembered panel; follow the contract that's there.

## Epic ingestion (work demo — a mapping step, not a platform)

To drive a work epic: fetch its child tickets, take the N≤3 smallest real ones, create one
dossier task per ticket on the WORK side (title = key + summary, body = description +
acceptance criteria, note = ticket URL), then `/work-driver-prep` as usual. Ticket content
never crosses into pers/ files or memory. Credential rule: state which Claude token + gh
account the run will use and get operator confirmation BEFORE dispatching; personal
credentials never touch work repos, work credentials never drive pers/.

## Review-cycle policy (the judgment the skill keeps)

- **Size review to risk (optional, invokable).** `/pr-risk <n>` classifies a PR's tier
  (deterministic floor + agent advisory) to inform *how much* review it needs: a T0 change
  (tests-only / generated / non-policy docs) can take a lighter panel or the safe-slice
  fast-path; a T2/T3 (migration, auth/secrets, supply-chain, isolation, a policy-relocating
  refactor) wants owner review + the adversarial pass, not a rubber-stamp. This is
  **recommend-only guidance you can invoke** — the driver does not auto-call it or auto-gate
  on it yet (same status as `/review-coordinator`). Don't skip a human on a low tier unless
  the operator has flipped the safe-slice on.
- **The cycle cap rides the merge grant**, not this prose: gate's `-max-cycles` CLI
  default is the policy (no number restated here), and gate derives each PR's count from
  its own state — N open PRs each get their own count under one grant. An over-cap gate
  park (exit 2) is the escalation point: re-mint a wider grant or stop — never auto-spiral
  into another cycle, never a judge, never `--admin` past the cap.
- **Address-inline-and-merge (skip the re-ping)** when the next findings are pure follow-ons
  to the prior cycle's reasoning, or strict mechanical fixes (CI compile error, format
  drift): fix inline + post a close-out comment + merge, no fresh review wait. Re-ping only
  when a fix changes shape/behavior enough to warrant fresh eyes — and post a re-ping as a
  **standalone single-line** `@bot review` comment, never folded into the close-out
  (embedded mentions don't trigger codex).
- **Be opinionated** — don't take every comment; push back with rationale. Treat a lone
  "blocking" against two "minor" as advisory unless you concur it's real.
- **Strategy by N** (pick one up front; don't drive reviews on all N PRs in parallel for
  N≥3 — cycle-1 fixes land on every PR at once and thrash context):
  - **Serial** — finish one PR's cycles before opening the next's. Lowest context, longest
    wall-clock. Best for N≥3 dissimilar PRs.
  - **Subagent-per-PR** — spawn one `Agent` per PR (PR number + the cap + the coordinator
    call), coordinate only at merge. Highest parallelism.
  - **Batched** — first cycle across all N (small fixes are often the same shape), then
    serialize the remaining cycles. Best for N≤2 or same-shape work.
- Only escalate genuinely major issues (product direction, auth/CI infra). Otherwise drive
  all the way to merge — through the gate step; never hand-`--admin` past a gate outcome
  (ship's `driver land` carries whatever branch-protection capability the merge needs).

## Kill + resume (the engine's resilience)

Killing the `driver run` tick is safe — progress is durable in the store. Re-run `driver
run <drv_id>` to continue; a killed-mid-flight cloud stream is re-attached and harvested
after the ~5-min staleness window. A re-tick within that window sees the orphan as "fresh"
and waits it out — expected.

## Gotchas

- **Ship engine: drive via the ship CLI throughout — one store.** Don't mix the ship MCP
  `driver_*` tools into the same ship-engine run: the connector and a terminal CLI use
  different stores (MSIX virtualization), so they won't see each other's state. (The MCP
  surface also lacks `land`/`render`/`cancel`.) This is about SHIP's MCP only — the
  workbench MCP (`mcp__workbench__driver_*`, the session engine's recording surface) has a
  single canonical state root and is the preferred surface there; its CLI mirror
  `driverstate` prints the root on every call so drift is visible.
- `driver decide` is `<drv> <decision> --stream <ds>` (decision positional, `--stream` a
  flag) — easy to invert. PowerShell eats an unquoted leading `@` → quote `'@codex review'`.
- `pnpm --filter exec` prints a misleading `Command "tsx" not found` on ANY non-zero child
  exit — including a tick's legit exit-10 (`awaiting_judgment`). Don't read it as a broken
  toolchain.
- Cloud PRs open as **drafts**; the engine flips them ready at the poll boundary (ship
  #177) — only a stream parked with a flip error needs a hand-flip. `driver cancel` does **not**
  reliably stop the remote cloud agent (it may still push a branch + open a PR). Cloud runs
  can finish past 30 min — a moving `updatedAt` means alive, so don't cancel early. Cursor
  cloud sometimes commits an **abridged** spec copy — diff the PR's doc against the local
  copy before discarding the local one.
- **Local streams:** run the project's formatter + check locally before push — a background
  task's `exit code 0` can lie, so `grep -iE "error|fail|warning"` the output before
  trusting it. `/worktree-remove` handles cleanup, including the Windows long-path and
  agent-scratch gotchas.
- **Codex latency is variable (3–14 min)** — don't block cycle-1 progression past ~5 min;
  claude is usually enough signal to start fixing.

## Capture friction (mandatory)

Append a dated section to `pers/workbench-friction.md`, one line per rough edge: the
prep→import seam, the `import → run → decide → land` cadence (what felt manual), N-parallel
dispatch, judgment UX, `render`/`status` accuracy, kill+resume latency, CLI clunk (startup,
absolute-path requirement, key plumbing), the MCP-surface gap. The log is this skill's
learning corpus. End with `/shipped` for the recap.

## Where it sits in the chain

`seed → prep → drive → review → recap`:

- **Seed** (produce dossier tasks): `/tdd`, `/work-driver-seed`, `/polish`, `/prep-public`.
- **Prep** (tasks → specs + conflict-batched manifest): **`/work-driver-prep`** — this
  skill calls it (step 1), or accepts its `driver.md` directly.
- **Drive** (← this skill): the `ship driver` engine. For **local** streams, the
  `/worktree-*` family manages the per-stream checkouts.
- **Review** (per PR, per cycle): **`/review-coordinator`** — the consolidated verdict over
  the four bots.
- **Recap** (after the run lands): **`/shipped`**.
