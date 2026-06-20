---
name: work-driver
description: Drive N parallel tasks end-to-end through ship's `ship driver` engine — the state machine (import → dispatch → poll → judgment → land → record) that replaced the hand-run per-stream `mcp__ship__ship` loop. Resolves dossier task IDs (or a phase, or an existing driver.md), preps specs + a conflict-batched manifest, dispatches all streams (cloud by default), handles failures via `ship driver decide`, drives the resulting PRs through review→merge, records merges back, and logs friction. Use when you want to fire one or several tasks in parallel and have an agent drive them to merge — "drive this impl work", "drive these 3 tasks", "run this batch through ship", "parallel-ship these", "ship and merge", "fire N parallel streams", explicit /work-driver.
argument-hint: "[task-ids... | phase:<slug> | project:<slug>:phase:<slug> | <path-to-driver.md>] [--runtime cloud|local]"
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
   # set CURSOR_API_KEY in your environment, then run from the ship repo
   cd pers/ship
   pnpm --filter @ship/cli exec tsx src/bin.ts driver <verb> ...
   ```
   - `driver run <ABSOLUTE driver.md path> --max-wait 30m --poll-interval 30s --json`
     → imports + dispatches all streams in parallel, polls. Note the `driverRunId`.
   - Re-invoke `driver run <drv_id> ...` to keep polling; exit **10** = `awaiting_judgment`.
3. **Judgment.** On a failed stream: `driver decide <drv_id> <decision> --stream <ds_id>
   [--reason "..."]` (`retry` re-dispatches the same branch; `skip`/`abort` need a reason),
   then re-run. Be opinionated about retry-vs-skip — judgment is the LLM's actual job here.
4. **Land → PR → review.** Each succeeded cloud stream opened a **draft** PR; `gh pr ready
   <n>` first. (Local streams: the agent auto-commits now — verify with `git -C <wt> log
   -1`; only commit + push yourself if `git status` shows uncommitted changes — then `gh pr
   create`.) Request reviewers as **standalone** comments (`@codex review`, `@claude
   review`, `@cursor review` — embedded pings don't trigger codex) plus `gh pr edit <n>
   --add-reviewer @copilot`. Each cycle, **when the bots surface real findings** (≥2 bots
   flag the same thing, or any `block`-severity), call **`/review-coordinator <n>`** for the
   consolidated `block`/`go` verdict — don't hand-triage four comment streams. On a clean
   pass (all bots green, or one stray advisory nit) skip the coordinator and merge: it earns
   its keep consolidating *conflicting or voluminous* findings, not rubber-stamping a clean
   PR (the coordinator owns the ingest mechanism; this skill owns the cap + the merge call).
5. **Record + close.** Per merge: `gh pr merge <n> --squash --admin --delete-branch`, then
   `driver land <drv_id> --pr <n>` (merges if not already, reads sha/time from gh, records),
   then dossier `task_complete` + `artifact_link` the merge commit. `driver status <drv_id>
   --json` / `driver render <drv_id>` to track. All streams merged → the run self-finishes
   to terminal `done`.

## Review-cycle policy (the judgment the skill keeps)

- **≤3 cycles per PR**, counted per PR (three open PRs each get three). After cycle 3, ping
  the operator — never auto-spiral into cycle 4.
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
  - **Batched** — cycle-1 across all N (small fixes are often the same shape), then
    serialize cycles 2-3. Best for N≤2 or same-shape work.
- Only escalate genuinely major issues (product direction, auth/CI infra). Otherwise drive
  all the way to merge. Admin-merge is fine on the operator's own repos.

## Kill + resume (the engine's resilience)

Killing the `driver run` tick is safe — progress is durable in the store. Re-run `driver
run <drv_id>` to continue; a killed-mid-flight cloud stream is re-attached and harvested
after the ~5-min staleness window. A re-tick within that window sees the orphan as "fresh"
and waits it out — expected.

## Gotchas

- **Drive via the CLI throughout — one store.** Don't mix the ship MCP `driver_*` tools
  into the same run: the connector and a terminal CLI use different stores (MSIX
  virtualization), so they won't see each other's state. (The MCP surface also lacks
  `land`/`render`/`cancel` — converging the stores + exposing them is the tracked follow-up
  that would let an agent drive natively via MCP.)
- `driver decide` is `<drv> <decision> --stream <ds>` (decision positional, `--stream` a
  flag) — easy to invert. PowerShell eats an unquoted leading `@` → quote `'@codex review'`.
- `pnpm --filter exec` prints a misleading `Command "tsx" not found` on ANY non-zero child
  exit — including a tick's legit exit-10 (`awaiting_judgment`). Don't read it as a broken
  toolchain.
- Cloud PRs open as **drafts** → `gh pr ready` before merge. `driver cancel` does **not**
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
