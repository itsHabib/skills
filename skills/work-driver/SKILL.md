---
name: work-driver
description: Drive N parallel tasks end-to-end through ship's `ship driver` engine — the state machine (import → dispatch → poll → judgment → land → record) that replaced the hand-run per-stream `mcp__ship__ship` loop. Resolves dossier task IDs (or a phase, or an existing driver.md), preps specs + a conflict-batched manifest, dispatches all streams (cloud by default), handles failures via `ship driver decide`, drives the resulting PRs through review→merge, records merges back, and logs friction. `--engine session` makes THIS session the engine for small runs (N≤3): it executes worktree→impl→PR→reviews→gate itself and records every transition through workbench-mcp, resumable from the ledger in a fresh session. Use when you want to fire one or several tasks in parallel and have an agent drive them to merge — "drive this impl work", "drive these 3 tasks", "run this batch through ship", "parallel-ship these", "ship and merge", "fire N parallel streams", explicit /work-driver.
argument-hint: "[task-ids... | phase:<slug> | project:<slug>:phase:<slug> | <path-to-driver.md>] [--runtime cloud|local] [--engine ship|session]"
user_invocable: true
---

# /work-driver — drive parallel work through the `ship driver` engine

Drive N tasks to merge using ship's **driver engine** (`ship driver <verb>`). The engine
owns the mechanism — dispatch → poll → judgment → land → record, with durable resumable
state in its own store. This skill is the **policy wrapper**: prep, review-cycle strategy,
the merge call, merge-recording, and a friction log. No sleep-polls, no YAML-as-database,
no resume bash — those are the engine's job now, not prose for the LLM to re-derive.

## Prerequisites

This skill orchestrates a personal toolchain — swap the names for your own equivalents:

- **ship** — the driver engine (`ship driver` CLI + `mcp__ship__*`); the state machine this
  skill wraps.
- **dossier** — the task/phase store the inputs resolve against.
- **gate** — the merge-authorization CLI (`gate` on PATH); emits a governed-path verdict per
  PR head. Build from its repo with `go build -o gate ./cmd/gate`.
- **workbench MCP** (`mcp__workbench__driver_*`) — the session-engine recording ledger.
- **tracelens** *(optional)* — agent-trace diagnostics for the advisory verdict step.
- `pnpm`, `gh`, and the target repo's own toolchain (for local streams).

## Inputs

- **Tasks:** dossier task IDs, a `phase:<slug>`, a `project:<slug>:phase:<slug>`, or a
  ready `driver.md` path. (Resolved the same way `/work-driver-prep` does.)
- **Runtime:** `--runtime cloud` (default — cursor cloud, `autoCreatePR`, no local
  worktrees) or `local` (one worktree per stream; needs the target repo's toolchain).
- **Engine:** `--engine ship` (default — ship's driver engine owns the mechanism, below) or
  `session` (THIS session is the engine: it executes everything itself and records every
  transition through `workbench-mcp` — see **Engine: session**). Session scope is N≤3
  streams; more, or any need for tick leases / orphan re-attach, belongs on ship.

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
2. **Drive via the ship CLI**, from your ship checkout, with the cursor key set and
   **absolute** manifest paths (`pnpm --filter exec` changes cwd):
   ```
   # set CURSOR_API_KEY in your environment, then run from the ship repo
   cd <your ship checkout>
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
   (`go install ./cmd/tracelens` from the tracelens repo puts it on PATH; run refs resolve
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
   flips it ready at the poll boundary — a stream parked with a flip error is the exception,
   not a prompt to hand-run `gh pr ready`. (Local streams: the agent auto-commits now —
   verify with `git -C <wt> log -1`; only commit + push yourself if `git status` shows
   uncommitted changes — then `gh pr create`.) Request reviewers per the target repo's
   **Panel from config** stanza (the reviewer set is the repo's `.ship.json` `review` key,
   never this prose): `mention` entries as **standalone** comments (`@<name> review` —
   embedded pings don't trigger codex), `reviewer-request` entries via
   `gh pr edit <n> --add-reviewer`, `auto` entries get nothing posted. Each cycle,
   **when the bots surface real findings** (≥2 bots flag the same thing, or any
   `block`-severity), call **`/review-coordinator <n>`** for the consolidated `block`/`go`
   verdict — don't hand-triage four comment streams. On a clean pass (all bots green, or one
   stray advisory nit) skip the coordinator and merge: it earns its keep consolidating
   *conflicting or voluminous* findings, not rubber-stamping a clean PR (the coordinator owns
   the ingest mechanism; the merge grant owns the cycle cap; this skill owns the merge call).
6. **Merge gate (dry-run advisory) → record + close.** Once per repo in the run, mint a
   merge grant from a stable cwd (gate's default `-state` dir is cwd-relative and the grant
   only exists in the state dir it was minted into):
   `gate grant -repo <owner/repo> -action merge -max-tier T1 -ttl 6h`
   Don't pass `-max-cycles` — gate's CLI default IS the review-cycle policy; this skill
   states no cycle number. Hold the printed `grt_…` for every gate call this run. Per PR
   per cycle, call the gate as the merge step and branch on its exit code — requiring the
   code and the JSON `outcome` on stdout to **agree** (0 ⟺ `would_merge`,
   1 ⟺ `blocked`, 2 ⟺ `parked_for_judgment`, 3 ⟺ `capability_refused`); a bare code
   with missing/disagreeing JSON is a truncated run — treat it as exit 4:
   `gate gate -repo <owner/repo> -pr <n> -grant <grt_…>`   (never `-live`)
   - **0** `would_merge` → land via the existing ship path: `driver land <drv_id> --pr <n>`
     (ship merges, reads sha/time back from gh, records), then dossier `task_complete` +
     `artifact_link` the merge commit.
   - **1** `blocked` → stop the stream; do not merge. Red stays red.
   - **2** `parked_for_judgment` → read the JSON: a **ceiling park** (a coded tier- or
     cycle-over-ceiling) resolves by re-minting a wider grant (`-max-tier` /
     `-max-cycles`) and retrying — **a re-mint, never a judge, never `--admin`**; the
     over-cap park is the "ask a human" moment, not a prompt to loop. A **content
     escalation** resolves by `gate judge -run <run_…> -grant <grt_…> …` (a judge can
     pass an escalation but can never clear a ceiling).
   - **3** `capability_refused` → grant expired/mis-scoped; re-mint and retry once.
   - **4** error → surface it; no merge.
   Gate is **advisory dry-run** here: it records the decision but never executes a merge
   (`-live` stays off until its preconditions land); ship's `driver land` remains the
   merge writer. Advisory means gate doesn't *merge* — not that it's optional: gate is a
   **required** step of the merge tail, and a missing binary is a setup error to surface,
   not a step to skip. `driver status <drv_id> --json` / `driver render <drv_id>` to track.
   All streams merged → the run self-finishes to terminal `done`.

## Engine: session (`--engine session`)

The session IS the engine: it does the worktree, impl (inline or subagents), PR, reviews,
and gate tail itself — and after **every** transition calls `mcp__workbench__driver_record`,
so run state lives in the workbench ledger, never in conversation context. Design contract:
workbench's `driver-state` spec (the state machine, the record-from-facts rule, and the
resume invariants).

**Declared scope: N≤3 streams, single writer per run.** The run lease enforces it —
`ErrLocked{Holder}` = fail fast and report the holder; no queueing. Needing more parallelism
or orphan re-attach = use `--engine ship`.

0. **Grant first.** Resolve a live gate grant for the target repo before dispatching
   anything (check gate's state log for a `grant` on the repo — repo + `expires_at`).
   Absent/expired → PARK and emit the exact
   `gate grant -repo <r> -action merge -max-tier <T> -ttl <d>` command for a human to run.
   **Never mint a grant yourself** — minting is a human act. (Some repos own their own merge
   authority — a shared repo where the team's process merges. There, skip the gate step
   entirely and drive to review-complete, then stop.)
1. **Recording loop (F1).** Record via MCP immediately after each external act — the ledger
   is written from facts, never ahead of them: `run_imported` (manifest snapshot; omit
   `run` — the server mints; body must carry repo/source/generated_at) → `stream_dispatched`
   `{engine:"session", worktree, branch}` → impl → commit → `stream_attempt`
   `{seq, doc_path, terminal, commit}` (the commit SHA is load-bearing for resume) →
   push + PR → `stream_pr_opened` `{pr, url, head_sha}` → per settled panel round
   `review_cycle` `{cycle, panel_settled, findings, panel, verdict}` → merge →
   `stream_merged` `{pr, merge_commit, merged_at}` → all streams terminal → `run_finished`.
   **Event ids are the idempotency key: mint `evt_<32 hex>` client-side per event and
   resend the SAME event verbatim on any retry** — a lost-response retry that omits the id
   gets a fresh server-minted one and duplicates history (or draws `ErrIllegalTransition`)
   instead of returning the original committed event. Mint an id for `run_imported` too —
   the RUN mint additionally dedupes on `(repo, source, generated_at)` in the body, so
   always set those three.
   Actor: `session:<label>-<n>`, `<n>` incrementing per session generation (first resume
   = `-2`); a resumed session MUST use a NEW actor — two actors on one run is the audit
   trail working.
2. **The contract corrects you (F2).** An `ErrIllegalTransition` rejection means your
   picture is stale: re-read `driver_state`, reconcile, continue — never force past it.
3. **Resume (F3).** Fresh session: `driver_runs {live:true}` → `driver_state <run>` →
   `driver_verify <run>` → **reconcile external facts before any write** (branch? PR state?
   merge commit? — `stream_dispatched`'s branch/worktree and `stream_attempt`'s commit say
   where to look; if `RunState` doesn't surface those bodies, read the run's `events.jsonl`
   under the printed state root alongside `driver_state`) → record the missing events →
   continue the drive. Never act on ledger state alone. A run with only `run_imported`
   resumes from its manifest snapshot — and reconcile-first still applies: a branch/worktree
   the manifest names that already exists is adopted, never recreated (the prior session
   died between creating it and recording `stream_dispatched`).
4. **State root sanity.** The MCP server prints its resolved state root at startup and the
   `driverstate` CLI prints it on every call — if you touch both surfaces in one run,
   confirm they match (`~/.workbench/driver-state` unless `WORKBENCH_STATE_DIR`).
5. **Tail.** Same review-cycle policy, gate step, and merge rules as above — reviews come
   from **Panel from config** (unconfigured repo: no review step, record one
   `review_cycle {cycle:1, review:"unconfigured", panel_settled:true, findings:0}` and go
   straight to gate), gate authorizes per PR, and `stream_merged` is recorded only after
   the merge fact is readable from GitHub. Expect the harness to refuse a merge of a PR
   this same session authored (self-approval classifier) — that's a park: hand a human the
   exact `gh pr merge … --match-head-commit <full 40-char sha>` command and record
   `stream_merged` after their merge.
6. **Stopping without a merge.** A run legitimately ends without
   `stream_merged`/`run_finished` when the target repo's own process owns the merge
   (a shared repo — §0), or when you were asked to drive to a stopping point short of merge
   (e.g. draft-PR-open: no ready-flip, no reviewers). The run then stays `open` — the work
   continues outside the ledger, which is accurate state, not a leak. Do NOT fabricate
   `run_finished` (it asserts every stream reached a terminal merge/skip). At that stop,
   **ASK** whether to leave the run open or record a terminal handoff
   (`stream_skipped {reason}`) before ending — never silently close a still-in-flight run,
   and never silently leave one open without surfacing it.

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

## External-tracker ingestion (a mapping step, not a platform)

To drive work that originates in an external issue tracker: fetch the epic's child issues,
take the N≤3 smallest real ones, create one dossier task per issue (title = key + summary,
body = description + acceptance criteria, note = issue URL), then `/work-driver-prep` as
usual. Keep tracker content scoped to the project it belongs to. Credential rule: state
which token + which git account the run will use and confirm BEFORE dispatching — keep
per-project credential scopes separate so one project's credentials never drive another's.

## Review-cycle policy (the judgment the skill keeps)

- **Size review to risk (optional, invokable).** `/pr-risk <n>` classifies a PR's tier
  (deterministic floor + agent advisory) to inform *how much* review it needs: a T0 change
  (tests-only / generated / non-policy docs) can take a lighter panel or the safe-slice
  fast-path; a T2/T3 (migration, auth/secrets, supply-chain, isolation, a policy-relocating
  refactor) wants owner review + the adversarial pass, not a rubber-stamp. This is
  **recommend-only guidance you can invoke** — the driver does not auto-call it or auto-gate
  on it yet (same status as `/review-coordinator`). Don't skip a human on a low tier unless
  you've turned the safe-slice on.
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
  `driver_*` tools into the same ship-engine run: an MCP connector and a terminal CLI can
  use different stores (OS packaging virtualization), so they won't see each other's state.
  (The MCP surface also lacks `land`/`render`/`cancel`.) This is about SHIP's MCP only — the
  workbench MCP (`mcp__workbench__driver_*`, the session engine's recording surface) has a
  single canonical state root and is the preferred surface there; its CLI mirror
  `driverstate` prints the root on every call so drift is visible.
- `driver decide` is `<drv> <decision> --stream <ds>` (decision positional, `--stream` a
  flag) — easy to invert. PowerShell eats an unquoted leading `@` → quote `'@codex review'`.
- `pnpm --filter exec` prints a misleading `Command "tsx" not found` on ANY non-zero child
  exit — including a tick's legit exit-10 (`awaiting_judgment`). Don't read it as a broken
  toolchain.
- Cloud PRs open as **drafts**; the engine flips them ready at the poll boundary — only a
  stream parked with a flip error needs a hand-flip. `driver cancel` does **not** reliably
  stop the remote cloud agent (it may still push a branch + open a PR). Cloud runs can
  finish past 30 min — a moving `updatedAt` means alive, so don't cancel early. Cursor
  cloud sometimes commits an **abridged** spec copy — diff the PR's doc against the local
  copy before discarding the local one.
- **Local streams:** run the project's formatter + check locally before push — a background
  task's `exit code 0` can lie, so `grep -iE "error|fail|warning"` the output before
  trusting it. `/worktree-remove` handles cleanup, including the Windows long-path and
  agent-scratch gotchas.
- **Codex latency is variable (3–14 min)** — don't block cycle-1 progression past ~5 min;
  claude is usually enough signal to start fixing.

## Capture friction (mandatory)

Append a dated section to your friction log (`workbench-friction.md`), one line per rough
edge: the prep→import seam, the `import → run → decide → land` cadence (what felt manual),
N-parallel dispatch, judgment UX, `render`/`status` accuracy, kill+resume latency, CLI clunk
(startup, absolute-path requirement, key plumbing), the MCP-surface gap. The log is this
skill's learning corpus. End with `/shipped` for the recap.

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
