---
name: driver-run
description: Drive N parallel tasks end-to-end through ship's `ship driver` engine — the state machine (import → dispatch → poll → judgment → land → mark-merged) that replaces the hand-run /work-driver loop. Resolves dossier task IDs (or a phase, or an existing driver.md), preps specs + a conflict-batched manifest, dispatches all streams (cloud by default), handles failures via `ship driver decide`, drives the resulting PRs through review→merge, records merges back, and logs friction. Use when you want to fire several tasks in parallel and have an agent drive them to merge via the engine — "drive these 3 tasks", "run this batch through ship driver", "parallel-ship these", explicit /driver-run. The engine-based successor to /work-driver (which is the older per-stream `mcp__ship__ship` loop).
argument-hint: "[task-ids... | phase:<slug> | project:<slug>:phase:<slug> | <path-to-driver.md>] [--runtime cloud|local]"
user_invocable: true
---

# /driver-run — drive parallel work through the `ship driver` engine

Drive N tasks to merge using ship's **driver engine** (`ship driver <verb>`), not the
old per-stream `mcp__ship__ship` loop. The engine owns dispatch → poll → judgment →
land; this skill wraps it with prep, review/merge, merge-recording, and a friction log.

> **This is the v0 of the P5 `/work-driver` rewrite.** It's grounded in real runs but
> still maturing — **every invocation appends to `pers/workbench-friction.md`**, and that
> log is what hardens this skill. Treat rough edges as output, not failure.

## Inputs

- **Tasks:** dossier task IDs, a `phase:<slug>`, a `project:<slug>:phase:<slug>`, or a
  ready `driver.md` path. (Resolve the same way `/work-driver-prep` does.)
- **Runtime:** `--runtime cloud` (default — cursor cloud, `autoCreatePR`, no local
  worktrees) or `local` (one worktree per stream; needs the target repo's toolchain).

## Flow

1. **Prep (skip if given a driver.md).** Check the tasks are file-disjoint via their
   `touches`; overlapping tasks can't share a parallel batch. Then `/work-driver-prep
   <inputs>` → one spec doc per task + a conflict-batched `driver.md` in the target repo.
   Its frontmatter matches the engine's import schema (incl. `repo_url` for cloud streams).
   For **local** streams, pre-flight a worktree per stream with `/worktree-add <branch>`
   (cloud streams need none — cursor cloud provides the workspace).
2. **Drive via the ship CLI**, from `pers/ship`, with the cursor key set and **absolute**
   manifest paths (`pnpm --filter exec` changes cwd):
   ```
   # set CURSOR_API_KEY in your environment, then run from the ship repo
   cd pers/ship
   pnpm --filter @ship/cli exec tsx src/bin.ts driver <verb> ...
   ```
   - `driver run <ABSOLUTE driver.md path> --max-wait 30m --poll-interval 30s --json`
     → imports + dispatches all streams in parallel, polls. Note the `driverRunId`.
   - Re-invoke `driver run <drv_id> ...` to keep polling; exit **10** = `awaiting_judgment`.
3. **Judgment.** On a failed stream: `driver decide <drv_id> <stream_id>
   retry|skip|abort --reason "..."` (retry re-dispatches; skip/abort need a reason), then
   re-run. Be opinionated about retry-vs-skip.
4. **Land → PR → review.** Each succeeded stream's cloud agent opened a **draft** PR
   (`local` streams: the agent didn't auto-commit — commit + push, then open the PR). Per
   PR: `gh pr ready <n>` → request reviewers as **standalone** comments (`@codex review`,
   `@claude review`, `@cursor review` — embedded pings don't trigger codex). Each cycle,
   call **`/review-coordinator <n>`** for the consolidated `block`/`go` verdict over the
   four bots (it's the review judge; don't hand-triage four comment streams). Fix
   criticals, re-ping, ≤3 cycles → `gh pr merge <n> --squash --admin --delete-branch`.
5. **Record + close.** After each merge: `driver mark-merged <drv_id> --stream <ds_id>
   --pr <n> --sha <sha>`, then dossier `task_complete` + `artifact_link` the merge commit.
   `driver status <drv_id> --json` / `driver render <drv_id>` to track. All streams merged
   → the run goes terminal `done`.

## Kill + resume (the engine's resilience)

Killing the `driver run` tick is safe — progress is durable in the store. Re-run
`driver run <drv_id>` to continue; a killed-mid-flight cloud stream is re-attached and
harvested after the ~5-min staleness window (the fire-and-forget resume from #138). A
re-tick within that window sees the orphan as "fresh" and waits it out — expected.

## Policy (operator standing)

- ≤3 review cycles per PR with @codex + @claude + @cursor; merge on clean; admin-merge is
  fine on the operator's own repos.
- Be opinionated — don't take every review comment; push back with rationale.
- Only escalate genuinely major issues (product direction, auth/CI infra). Else drive all
  the way to merge.

## Gotchas

- **Drive via the CLI throughout — one store.** Don't mix the ship MCP `driver_*` tools
  into the same run: the connector and a terminal CLI use different stores (MSIX
  virtualization), so they won't see each other's state. (The MCP surface also lacks
  `mark-merged`/`render`/`cancel` — exposing them + converging the stores is the tracked
  follow-up that would let an agent drive natively via MCP.)
- Cloud PRs open as **drafts** → `gh pr ready` before merge.
- `driver cancel` does **not** reliably stop the remote cloud agent — it may still push a
  branch + open a PR after you cancel.
- Cloud runs can legitimately finish past 30 min; a moving `updatedAt` means alive — don't
  cancel early.
- Cursor cloud agents sometimes commit an **abridged** copy of a spec/phase doc — diff the
  PR's doc against the local copy before discarding the local one.

## Capture friction (mandatory — this is how the skill matures)

Append a dated section to `pers/workbench-friction.md`, one line per rough edge: the
prep→import seam, the `import → run → decide → mark-merged` cadence (what felt manual /
should be one verb), how N-parallel dispatch feels, judgment UX, `render`/`status`
accuracy, kill+resume latency, CLI clunk (`pnpm --filter exec` startup, absolute-path
requirement, key plumbing), and the MCP-surface gap. End with `/shipped` for the recap.

## Where it sits in the chain

`seed → prep → drive → review → recap`:

- **Seed** (produce dossier tasks): `/tdd`, `/work-driver-seed`, `/polish`, `/prep-public`.
- **Prep** (tasks → specs + conflict-batched manifest): **`/work-driver-prep`** — this
  skill calls it (step 1), or accepts its `driver.md` directly.
- **Drive** (← this skill): `ship driver` engine. For **local** streams, `/worktree-*`
  manage the per-stream checkouts.
- **Review** (per PR, per cycle): **`/review-coordinator`** — the consolidated verdict
  over the four bots.
- **Recap** (after the run lands): **`/shipped`**.

Distinct from **`/work-driver`** — that's the older hand-run `mcp__ship__ship` per-stream
loop; this drives the same shape through the `ship driver` engine instead, so the rest of
the chain is identical (same prep, same review judge, same recap). It's the drop-in
engine-based replacement for the drive step.
