---
name: work-driver
description: >-
  Drive N parallel tasks end-to-end through ship's `ship driver` engine — the
  state machine (import → dispatch → poll → judgment → land → record) that
  replaced the hand-run per-stream `mcp__ship__ship` loop. Resolves dossier task
  IDs (or a phase, or an existing driver.md), preps specs + a conflict-batched
  manifest, dispatches all streams (cloud by default), handles failures via
  `ship driver decide`, drives the resulting PRs through review→merge, records
  merges back, and logs friction. `--engine session` makes THIS session a THIN
  orchestrator: each task's impl runs in a delegated isolated-worktree subagent
  (fresh context, own model), the parent holds only structured summaries + PR
  URLs and records every transition through workbench-mcp (parent run + child
  sub-runs), and the whole run is resumable from the ledger in a fresh session
  (≥5 tasks, single writer per sub-run). Use when you want to fire one or
  several tasks in parallel and have an agent drive them to merge — "drive this
  impl work", "drive these 3 tasks", "run this batch through ship",
  "parallel-ship these", "ship and merge", "fire N parallel streams", explicit
  /work-driver.
argument-hint: "[task-ids... | phase:<slug> | project:<slug>:phase:<slug> | <path-to-driver.md>] [--runtime cloud|local] [--engine ship|session]"
user_invocable: true
---

# /work-driver — drive parallel work through the `ship driver` engine

Drive N tasks to merge using ship's **driver engine** (`ship driver <verb>`). The engine
owns the mechanism — dispatch → poll → judgment → land → record, with durable resumable
state in its own store. This skill is the **orchestration wrapper**: prep, invocation of
Workbench's review policy, engine-specific execution adapters, the Gate-authorized merge,
merge-recording, and a friction log. It does not reinterpret tier or cycle policy. No
sleep-polls, no YAML-as-database, no resume bash — those are the engine's job now, not prose
for the LLM to re-derive.

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
2. **Drive via the ship CLI**, with `CURSOR_API_KEY` already set and **absolute**
   manifest paths (`pnpm --filter exec` changes cwd):
   ```
   cd <ship-repository>
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
   (`go install ./cmd/tracelens` from `~/projects/tracelens` puts it on PATH; run refs resolve
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
5. **Land → PR → exact-head review.** Each succeeded cloud stream opened a **draft** PR; the engine
   flips it ready at the poll boundary (ship #177) — a stream parked with a flip error is
   the exception, not a prompt to hand-run `gh pr ready`. (Local streams: the agent
   auto-commits now — verify with `git -C <wt> log
   -1`; only commit + push yourself if `git status` shows uncommitted changes — then `gh pr
    create`.) If `.ship.json.review.tier_aware` is `true`, run **Tier-aware exact-head
    review** below; Workbench selects the panel and continuation. Otherwise preserve the
    repository's existing **Legacy panel from config** behavior unchanged. Per cycle,
    append the raw per-bot `review_cycle` spend event; Ship also emits the consumed
    Workbench `review_decision` event.
6. **Merge gate → exact emitted merge → record + close.** Resolve a live
    **operator-minted** grant for the repository. Never call `gate grant`. If none is
    available, park and hand the operator this exact request:
    `gate grant -repo <owner/repo> -action merge -max-tier <required-tier> -ttl 24h`.
    T3 cycles 4–8 additionally need the operator to choose a sufficient `-max-cycles`;
    Workbench's cap never widens Gate authority. Run Gate from the stable state root:
    `gate gate -repo <owner/repo> -pr <n> -grant <grt_…> -state ~/projects/gate/state`.
    Branch on its exit code — requiring the
   code and the JSON `outcome` on stdout to **agree** (0 ⟺ `would_merge`,
   1 ⟺ `blocked`, 2 ⟺ `parked_for_judgment`, 3 ⟺ `capability_refused`); a bare code
   with missing/disagreeing JSON is a truncated run — treat it as exit 4:
    - **0** `would_merge` → run the **exact commit-pinned `gh pr merge
      --match-head-commit …` command Gate emits**; never reconstruct or loosen it. After
      GitHub reports the merge, call `driver land <drv_id> --pr <n> --stream <ds_id>
      --cycles <n> --reviewed-head <exact-reviewed-head> --gate-run <run_…>` so Ship reads
      the merged fact and records closure, then dossier `task_complete` + `artifact_link`.
   - **1** `blocked` → stop the stream; do not merge. Red stays red.
   - **2** `parked_for_judgment` → read the JSON: a **ceiling park** (a coded tier- or
      cycle-over-ceiling) requires the operator to mint a wider grant (`-max-tier` /
      `-max-cycles`) or stop — **never mint it yourself, never judge a ceiling, never
      `--admin`**. A **content
     escalation** resolves by `gate judge -run <run_…> -grant <grt_…> …` (a judge can
     pass an escalation but can never clear a ceiling).
    - **3** `capability_refused` → grant expired/mis-scoped; ask the operator for a fresh
      correctly scoped grant.
   - **4** error → surface it; no merge.
    Gate is the required authorization boundary; its emitted command is the only merge
    writer. A missing binary is a setup error to surface, not a step to skip. Resolve it as
    `gate` on PATH, built from the workbench repo via
   `go build -o gate ./cmd/gate`. `driver status <drv_id> --json` /
   `driver render <drv_id>` to track. All streams merged → the run self-finishes to
   terminal `done`. At each terminal — merge **or** close — record review-spend: the engine
   emits `terminal {merged:true}`, but closed-unmerged PRs and fixes-PR linkage are the
   skill's to append (see **Review-spend telemetry**).

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

Resolve a live, operator-minted gate grant for a **merged**-boundary personal repo before
dispatching (`grep '"kind":"grant"' ~/projects/gate/state/log.jsonl | tail -5`, check repo +
`expires_at`). Absent/expired → PARK and emit the exact
`gate grant -repo <r> -action merge -max-tier <T> -ttl <d> -state ~/projects/gate/state` for the
operator. **Never mint.** Work repos and `pr-open`/`green`-boundary local repos: gate does not
apply — state which Claude token + gh account the run uses, get confirmation, drive to the
boundary, stop.

### 1. Done-boundary (per run) — pick it up front

The manifest's `done_boundary` decides how far each stream is pushed (spec §4 D7):

- **`merged`** (personal-repo default): drive through the panel → gate → merge; parent records
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
confirm they match (the configured Workbench driver-state directory).

### 6. Merge tail (merged boundary only)

Use the same **Tier-aware exact-head review** procedure as the Ship engine when the repo opts
in; the Workbench plan/request/decision artifacts must be byte-equivalent for the same inputs.
Only an `address` decision selects the session adapter:
`reviewfindings address accept -run <child> -stream <stream> -artifact <findings.json>
-decision <decision.json> -max-cycles <plan.max_cycles>`. Follow its claim/start/completed
runbook, then re-read the live head and start a fresh exact-head plan. If the repo has not
opted in, preserve its legacy panel behavior. Gate authorizes per PR; record `stream_merged`
only after the merge fact is readable from GitHub.
Expect the harness to refuse a merge of a PR this same session authored (self-approval
classifier) — that's a park: hand the operator the exact
`gh pr merge … --match-head-commit <full 40-char sha>` and record `stream_merged` after their
merge. A run that stops at a non-merge boundary (§1 `pr-open`/`green`, or a work repo) stays
`open` — do NOT fabricate `run_finished`. At that stop, **ASK** whether to leave the run open or
record a terminal handoff (`stream_skipped {reason}`); never silently close an in-flight run,
never silently leave one open without surfacing it. **Review-spend telemetry** (per-cycle
`review_cycle` events + terminal spend) applies here too — the skill appends it in session
mode exactly as in ship mode.

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

## Review opt-in and legacy panel (`.ship.json` — both engines)

Tier-aware review is a double opt-in. The target repo must set
`.ship.json.review.tier_aware: true`, and Workbench's checked-in canary policy
must list the same `owner/repo`. Either side absent means no reduced route.
The remaining panel fields preserve the repo's legacy review contract:

```json
"review": {
  "tier_aware": true,
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

- With `tier_aware: true`, Workbench `review plan` is authoritative. A
  `full_panel_fallback` or `parked_unverified` plan requests the complete
  safe panel it carries; never reinterpret an error into fewer reviewers.
- Without `tier_aware: true`, preserve the legacy behavior below exactly. Do
  not invoke tier routing and do not edit work/employer repository config.
- `mention` → standalone `@<name> review` comment; `auto` → the bot fires on PR open, post
  nothing; `reviewer-request` → `gh pr edit --add-reviewer` (copilot needs the API form:
  `gh api repos/<r>/pulls/<n>/requested_reviewers -f 'reviewers[]=copilot-pull-request-reviewer[bot]'`
  — the `--add-reviewer copilot` login doesn't resolve).
- **Settled** = every `require` member reported, or `settle_minutes` expired — then record
  the cycle as degraded, naming the silent bots, and proceed on the signal you have.
- **No implicit default:** absent/empty `review` key = NO automated review step — no pings,
  no consolidation — recorded as `review: unconfigured` so the omission is visible. Never
  substitute a remembered panel; follow the contract that's there.

## Tier-aware exact-head review (both engines)

Workbench `review` owns reviewer and continuation policy. The skill only
orchestrates its artifacts. Use a new evidence directory for every
`{repo, pr, head}`; never overwrite or reuse an older head's plan, request,
panel, findings, cycle input, or decision.

1. Read the live 40-character `headRefOid` with `gh pr view`. Run:
   `review plan -repo <owner/repo> -pr <n> -head <sha> -out <head-dir>/plan.json`.
   The built-in checked-in policy is the default; callers do not select a
   policy revision. `-policy` is only for an explicit validated experiment.
2. Inspect the emitted plan, not prose:
   - `tier_routed` → follow its reviewers, requirements, and `max_cycles`;
   - `full_panel_fallback`, `deliberately_overridden`, or
     `parked_unverified` → follow the full panel carried by the plan and
     record its reason;
   - malformed/missing output → stop. Infrastructure uncertainty never becomes
     a reduced route.
3. Initial cycle:
   - T0 requests no cloud reviewer. Run and record the required local
     adversarial pass.
   - T1/T2/T3 call `review request -plan <plan> -out <request>`; the command
     checks the live head before and after every GitHub write.
   - Observe completion with `review observe -plan <plan> -out <panel>`.
     Produce a sourced exact-head `ReviewFindingsV1` when findings exist.
     Run the coordinator/adversarial work exactly when the plan requires it.
4. Build `ReviewCycleInputV1` with explicit state for every finding and call
   `review decide -plan <plan> -input <cycle-input> -out <decision>`.
   Set `completed_reviewers` to the exact `panel.completed` identities; set
   `panel_complete` only when every `plan.required` reviewer is present.
   Workbench validates both fields and derives `decision.next_reviewers` from
   required reviewers still missing, so later cycles never blindly re-request
   a reviewer that already completed.
   Noncritical findings may be deferred with a rationale; genuine debt also
   requires a follow-up reference. Critical findings, failed tests, and
   missing required evidence cannot be deferred. On T0–T2 later cycles,
   exact-head deterministic proof may replace bot rereview for noncritical
   findings. Cycles 4–8 require T3 plus a continuation rationale.
5. Execute only the emitted action:
   - `address` → pass the exact findings and decision to one adapter:
     - Ship: `driver address <drv> --stream <ds> --findings <findings>
       --decision <decision> --max-cycles <plan.max_cycles>`;
     - session: `reviewfindings address accept -run <child> -stream <stream>
       -artifact <findings> -decision <decision>
       -max-cycles <plan.max_cycles>`, then claim/start/complete the durable
       work item.
     A different action, head, cycle, or finding set must refuse before work.
   - `continue` → request only `decision.next_reviewers`.
   - `stop` → proceed to Gate only after CI and all plan requirements are green.
   - `escalate` → re-read the head and produce a new plan; never widen the tier
     locally.
   - `park` → surface its reason and wait for operator judgment/authority.
6. A push invalidates all prior-head authorization. Re-read the live head,
   create a fresh evidence directory, reclassify, and regenerate every required
   artifact before another request, adapter call, or Gate run. For a later
   post-fix cycle at the same or lower tier, deterministically request only the
   intersection of the new plan with
   `new_plan.required ∪ prior_decision.next_reviewers`. If the tier increased
   or the new plan is a fallback, request the complete new plan. This keeps
   rereview focused without skipping newly required reviewers.
7. Record `cycle`, `continuation_weight`, and `cumulative_weight` from the
   decision as shadow telemetry. They explain why another cycle was expensive;
   they do not independently authorize or suppress review.

## Epic ingestion (work demo — a mapping step, not a platform)

To drive a work epic: fetch its child tickets, take the N≤3 smallest real ones, create one
dossier task per ticket on the WORK side (title = key + summary, body = description +
acceptance criteria, note = ticket URL), then `/work-driver-prep` as usual. Ticket content
never crosses into personal files or memory. Credential rule: state which Claude token + gh
account the run will use and get operator confirmation BEFORE dispatching; personal
credentials never touch work repos, work credentials never drive personal repos.

## Review-cycle orchestration (Workbench keeps the policy)

- Do not infer a tier, reviewer set, cap, or stop condition in this skill.
  `ReviewPlanV1` and `ReviewDecisionV1` are authoritative for both engines.
- Caps are ceilings, not required loop counts. Stop immediately when the
  decision says `stop`; continue only for its named reviewers. Gate's grant is
  an independent authority ceiling and can be narrower, never wider, than the
  review plan.
- Be opinionated in the explicit finding disposition: fix, prove safe, defer
  with rationale/follow-up, or leave unresolved. Do not silently suppress a
  finding because other bots disagreed. Workbench deterministically decides
  whether the resulting evidence can stop.
- A push always invalidates prior-head review. The old decision may guide the
  deterministic targeted-reviewer calculation described above, but it cannot
  authorize an adapter or merge against the new head.
- **Strategy by N** (pick one up front; don't drive reviews on all N PRs in parallel for
  N≥3 — cycle-1 fixes land on every PR at once and thrash context):
  - **Serial** — finish one PR's cycles before opening the next's. Lowest context, longest
    wall-clock. Best for N≥3 dissimilar PRs.
  - **Subagent-per-PR** — spawn one `Agent` per PR (PR number + the cap + the coordinator
    call), coordinate only at merge. Highest parallelism.
  - **Batched** — first cycle across all N (small fixes are often the same shape), then
    serialize the remaining cycles. Best for N≤2 or same-shape work.
- Only escalate genuinely major issues (product direction, auth/CI infra) or a
  Workbench/Gate park. Otherwise drive all the way to the Gate-emitted
  commit-pinned merge; never use `--admin`.

## Review-spend telemetry (per cycle + per bot — feeds the tiering measurement)

The `review-credit-tiering` loss-analysis needs per-bot review spend the engine
cannot see from the consolidated findings artifact. Ship writes
`review_decision` when its adapter consumes an exact-head `address` decision
and `terminal` at merge. This skill writes the raw per-bot `review_cycle` event
for every decision, including `stop`/`continue`/fallback and session runs, into
the **same** append-only log.

**File** — `review-spend.jsonl` in ship's state dir, beside `state.db`:
`dirname($SHIP_DB_PATH)/review-spend.jsonl` when `SHIP_DB_PATH` is absolute, else
`<userConfigDir>/ship/review-spend.jsonl` (Windows → `%APPDATA%\ship\review-spend.jsonl`).
One JSON object per line. **Best-effort: a write failure warns and is dropped — it never
blocks a cycle, a land, a merge, or the run.** This is the JSONL *spend* log, distinct from
the driver-state ledger's `review_cycle` transition — don't conflate them.

**Per review cycle** (after `review decide`), append one `review_cycle` event —
the skill has the raw per-bot comments the engine lacks:

```json
{"ts":"<RFC3339>","event":"review_cycle","repo":"owner/name","pr":<n>,"head_sha":"<sha>",
 "tier":"T0|T1|T2|T3","tier_reasons":[],"policy_id":"tier-aware-canary",
 "policy_digest":"sha256:…","route_disposition":"tier_routed|full_panel_fallback|…",
 "route_reason":null,"cycle":<1-based>,"continuation_weight":1,"cumulative_weight":1,
 "decision_action":"stop|continue|address|escalate|park","decision_reasons":[],
 "reviewers_requested":["codex"],"reviewers_completed":["codex"],"next_reviewers":[],
 "findings_per_bot":{"codex":{"total":N,"unique":N,"critical":N},"claude":{"total":N,"unique":N,"critical":N}},
 "claude_cost_proxy":<int|null>}
```

- `findings_per_bot` — from the panel's raw per-bot comments (the `/review-coordinator` /
  `/review-digest` ingest): `total` = that bot's actionable findings this cycle, `unique` =
  findings NOT duplicated by another bot at the same `file:line` (reuse the coordinator's
  grouping — **don't re-judge**), `critical` = block-severity count.
- `claude_cost_proxy` = (diff bytes fed to claude in) + (claude review-body bytes out) this
  cycle; **bytes, not tokens** (the 30-day re-eval calibrates bytes/4 ≈ tokens against the
  operator-pulled Claude usage total). `null` when claude didn't review that cycle.
- Policy, route, tier, cycle, weights, action, and reason fields are copied
  from Workbench artifacts; never reconstruct them from prose.
- The shape is skill-defined raw JSONL. Ship's typed union covers its
  `review_decision` and `terminal` events; readers union all three event shapes.

**At terminal**:

- **Closed-unmerged** (the engine's `markMerged` never fires for these — the abandoned/stuck
  tail the strategy doc weighs most): the skill appends the `terminal` event itself:
  `{ts, event:"terminal", repo, pr, tier?, tier_source?, cycles_used, merged:false, fixes_pr}`.
- **Merged with a declared fixes-PR**: the engine's `terminal {merged:true}` lacks
  `fixes_pr` (it doesn't parse the PR body; the skill does). When the PR body **explicitly**
  declares it fixes a prior PR, append `{ts, event:"terminal", repo, pr, …, merged:true,
  fixes_pr:<n>}`. The analysis keys terminal events by `{repo,pr}` and **unions their
  fields**, so this coexists with the engine's terminal for the same PR by design — the
  union picks up `fixes_pr`. Explicit declaration only; otherwise don't append (the engine's
  terminal already covers a plain merge).

**Both engines** — identical in `--engine ship` (Flow steps 5–6) and `--engine session`
(§6 merge tail); the skill owns this append in both, since both process raw PR comments.

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

Append a dated section to `~/projects/workbench-friction.md`, one line per rough edge: the
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
