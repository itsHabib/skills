---
name: parallel-work
description: >-
  Plan, run, inspect, or resume a bounded batch of repository work with Claude
  Code Agent workers and Git worktrees. Use when two or more write tasks can
  proceed independently and you want local parallel agents without
  Dossier, Ship, driver manifests, or cloud orchestration. Do not use for one
  ordinary task or cross-machine execution.
user_invocable: true
argument-hint: "<goal> | status <run> | resume <run> [--through local|pr|merge]"
---

# Parallel work

One front door for local multi-task work:

```text
/parallel-work <goal>
/parallel-work status <run>
/parallel-work resume <run>
```

Own decomposition, safe Agent fan-out, integration, validation, and compact
status. Do not require a Dossier phase, per-task spec documents, Ship, cloud
credentials, or a separate preparation command.

## Route by task shape

- One ordinary task: do it directly.
- One bounded task that needs a durable handoff: use `/work-contract` to manage
  one `WORK.md`.
- Two or three read-only questions: dispatch Agents directly and combine their
  answers; a ledger and worktrees add no value.
- Two or more write tasks, or a batch likely to cross sessions: use this skill.
- Cross-machine execution, organizational ticket ingestion, or an already-live
  Ship driver run: use the established system instead of translating it.

`WORK.md` and the parallel ledger solve different problems. A work contract is
one repository task's exact-subject handoff. A parallel ledger records the live
coordination state of several isolated tasks and stays outside the repository.

## Start

### Ground and divide

Read the applicable `CLAUDE.md`/`AGENTS.md`, repository charter, live Git
status, and the smallest relevant source set. Define each task with:

- one concrete outcome;
- owned paths or one explicitly named shared seam;
- upstream task IDs, if any;
- one observable done-check;
- a short out-of-scope boundary.

Parallelize only semantically independent tasks whose write paths do not
overlap. Put dependent or overlapping tasks in later waves. If the split is
clear and implementation is already authorized, show it briefly and proceed.
Stop for input only when decomposition exposes a material product, data,
publication, or architecture choice.

One run owns exactly one repository and one verified base commit. For a
cross-repository goal, use ordered repository stages and record the exact
upstream integration SHA consumed by each downstream stage. A shared seam has
one writer per wave and normally belongs to parent integration.

Choose `combined` when tasks are parts of one reviewable change; choose
`separate` when each task is independently valuable. Do not recreate stacked
PR machinery inside this skill.

### Set the stopping boundary

`--through local` is the default unless you clearly authorize more:

- `local`: verified local task/integration commits; no push.
- `pr`: push and open/update the intended PRs, then stop after required checks
  and review requests.
- `merge`: continue through the repository's own review and merge policy.
  Merge authority stays with whatever the repository designates — a required
  check, a protected branch, a merge gate. Never bypass it, reconstruct a
  command it emits, or merge past a block.

Execution convenience never widens the requested boundary.

### Persist only when useful

For four or more tasks, more than one dependency wave, or work likely to cross
sessions, create a private ledger under:

```text
${CLAUDE_CONFIG_DIR:-$HOME/.claude}/parallel-work/<repo>/<run>.md
```

Do not add orchestration state to the target repository. Read
[`references/ledger.md`](references/ledger.md) when creating, inspecting, or
resuming a ledger. Update it only after each transition is true in Git or
GitHub.

### Isolate writers and dispatch a wave

For every write task:

1. Create a distinct branch and worktree from the wave's verified base. Use
   `/worktree-add` when available so portfolio conventions are preserved.
2. Dispatch exactly one Claude Agent worker with ownership of that worktree and
   its declared paths. Agents may read the whole repository but may not edit
   another task's paths.
3. Pass real validation commands with working directory and expected result.
   Record prose or visual judgments as manual checks. Expected-red controls
   pass only when their declared failure occurs.
4. Ask the worker for the return shape in
   [`references/worker-contract.md`](references/worker-contract.md).
5. Use only the concurrency the harness actually exposes; run extra tasks in
   later waves.

Read the worker contract immediately before the first write dispatch. A
read-only Agent needs only a concise prompt and return request.

### Reconcile and integrate

For every returned worker:

- inspect its actual diff, commit, and check output;
- reject scope drift or unverifiable success claims;
- record the observed state in the ledger, if present;
- route blockers to the parent instead of letting another Agent guess.

For `combined`, integrate accepted commits in dependency order on a dedicated
integration branch/worktree and run the full relevant checks. For `separate`,
keep branches independent and verify each before any push. Start a dependent
wave only from the exact integrated upstream commit it needs.

Generated projections must consume an absolute path to a clean upstream
integration worktree at a verified full SHA. Stop on a dirty or mismatched
source unless you explicitly authorize that exact state. Never
hand-edit generated output when an exporter exists.

Use one final adversarial review when the integrated diff is substantial,
security-sensitive, or correctness-critical.

### Deliver and clean up

Stop at the selected boundary. Report branches/commits, checks, PRs, and
blockers. Remove worktrees only after their commits are integrated or otherwise
preserved; never discard a dirty worktree silently.

## Status and resume

`status` reads the ledger and reconciles it against live Git/worktree/PR state.
Return a compact table of task, state, branch or PR, check, and blocker.

`resume` performs the same reconciliation before acting:

- adopt an existing commit or PR instead of redispatching;
- inspect a dirty orphaned worktree before deciding how to continue;
- redispatch only when neither durable work nor a live worker exists;
- resume from the earliest incomplete dependency wave;
- never trust ledger state over live Git or GitHub.

## Deliberate omissions

No Dossier phase, per-task spec generation, Ship state, cloud-provider
selection, credential plumbing, review-spend telemetry, or generalized policy
engine. Those systems remain available when their durability, scale, or
organizational integration is the actual requirement.
