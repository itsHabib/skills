---
name: wip
description: Standing cross-store board of what's open or in-flight RIGHT NOW — joins ship (workflow + driver runs), dossier (claimed/in_progress/blocked tasks + the fresh todo queue), and open PRs into one liveness-ranked view, with a red "on fire" band for stuck ship dispatches and stale rows quarantined into a reconcile bucket. Personal-scoped by default (everything behind --all). Use when the user asks "what's in flight", "anything running", "what's queued", "what's cooking", "where are things", "what's open right now", "any work in progress", "wip", or invokes /wip. Distinct from /status (situational session recap) and /shipped (retrospective on landed work).
argument-hint: "[--scope personal|all] [--project <slug>] [--reconcile] — e.g. /wip, /wip --all, /wip --project ship"
user_invocable: true
---

# /wip — what's open or in-flight, right now

One board that answers "any work in progress or queued?" without you hand-joining
three stores. The state lives in **ship's run store**, **dossier's task store**, and **open
PRs across N repos** — none of which join on their own. This skill does the join, ranks by
liveness, and quarantines the noise so two live items don't drown under twenty dead
`in_progress` rows.

**Not** a session recap (that's `/status`) and **not** a post-merge retrospective (that's
`/shipped`). This is the real-time cross-project board: *what is actually moving, what's stuck,
what's queued.*

## Prerequisites

This board joins three tools the author uses: **`ship`** (a CI/driver tool that exposes
workflow + driver runs), **`dossier`** (a task store), and **`gh`** (the GitHub CLI, for open
PRs). It expects the `mcp__ship__*` and `mcp__dossier__*` MCP verbs plus `gh` on your `PATH`.
If you don't run ship and dossier, point the two store steps at your own run store / task
store — the value here is the cross-store join and the liveness ranking, not the specific
backends.

## When to use

Triggers:
- "any work in progress / queued?" · "what's in flight" · "anything running"
- "what's cooking" · "where are things" · "what's open right now" · "wip"
- Start-of-session orientation across your projects
- Explicit `/wip`

Anti-triggers:
- "where are we on *this*?" (current session) → `/status`
- "what just shipped / merged?" → `/shipped`
- "full state of project X" → `mcp__dossier__project_overview { slug }`

## Arguments

`/wip [--scope personal|all] [--project <slug>] [--reconcile]`

- **`--scope personal`** (default) → your personal projects only. Excludes any repos or
  projects you've marked as separate (e.g. a work or client bucket you don't want in the
  default view).
- **`--scope all`** (`--all` for short) → include every bucket, personal and otherwise.
- **`--project <slug>`** → narrow to one project (e.g. `ship`, `<your-project>`).
- **`--reconcile`** → after the board, act on the stale bucket: offer to close tasks that
  look done (linked PR merged, or the capability now exists). Opt-in; never auto-writes
  without this flag.

## Sources & the join

Run these concurrently (they're independent), then merge:

### 1. Ship — live runs + stuck dispatches
```
mcp__ship__list_workflow_runs { limit: 20 }
```
- **Live**: any run `status: running | pending` → in flight now.
- **🔴 On fire — the signal most worth surfacing**: group recent runs by `docPath`. Three or
  more failures of the *same doc* is a stuck dispatch loop (e.g. a task re-dispatched hourly,
  every run `status: failed`). Report the doc, the count, the window, and the
  `errorMessage` + `failureCategory` from the last phase. A dozen silent retries reads as
  "nothing happening" on every other surface — this is the whole reason the board exists.
- If a `driverRunId` is discoverable (recent `docs/features/*/driver.md` frontmatter, or a
  dossier task note), `mcp__ship__driver_status { driverRunId }` for per-stream detail.
- **Store caveat (sandboxed MCP):** if your MCP connector runs in a sandboxed or virtualized
  environment, `list_workflow_runs` may read a different store than a run started from the
  terminal CLI — that CLI-driven run won't show up here. If the user mentions a CLI-driven run
  you don't see, say so rather than reporting "no runs".

### 2. Dossier — active set + queue head
```
mcp__dossier__task_list { status: ["in_progress","claimed","blocked"], bodies: false, order_by: "updated_at", desc: true }
mcp__dossier__task_list { status: ["todo"], bodies: false, order_by: "updated_at", desc: true, limit: 40 }
mcp__dossier__project_list { order_by: "updated_at", desc: true }
```
- The first is the "in flight" set. The second is the queue — **counts + slugs only, never a
  full backlog dump**. The third gives project recency + status for grouping.
- Map `project_slug` → bucket. Any project you've marked as non-personal is hidden unless
  `--scope all`.

### 3. PRs — open, authored by you, all repos
```
gh search prs --author=@me --state=open --limit 60 --json number,title,repository,isDraft,updatedAt,url
```
- Group by repo. Split three ways: **personal** (your own repos, e.g. `<your-user>/*`),
  **other** (repos you've marked as separate, e.g. a work or client org), **ancient cruft**
  (updated >1yr ago — surface as a one-line "close these?" aside).

## Liveness ranking (the value-add)

The raw dossier `in_progress` list is mostly lies — tasks get claimed and never closed. Rank
every item; float the live, sink the dead:

- **🔴 On fire** — stuck ship dispatch loop, or a `blocked` task with no path forward.
- **🟢 Live** — updated <3 days, **or** has a linked open PR, **or** an active/pending ship run.
- **🟡 Idle** — open but no movement in 3–14 days (a PR sitting unreviewed, a task claimed but quiet).
- **⚫ Stale** — `claimed`/`in_progress` >14 days with **no** linked open PR and **no** recent
  ship run → collapse into a "reconcile?" bucket. Do not rank these inline; they exist to be
  closed, not tracked.

A task's liveness is the freshest of: its `updated_at`, its linked PR's `updatedAt`, or a
ship run whose `docPath` matches its spec. Cross-reference before ranking — a task quiet for
20 days but whose PR merged yesterday is done (→ reconcile), not stale-forgotten.

## Output format

Skip any empty section. Lead with fire if there is any.

```markdown
## 🔴 On fire
- <what> — <why> (<error / count / window>) — <pointer: run id, PR#, task slug>

## In flight (<scope>)
**<project>** — <n live>
- <task or run title> — <state> — <PR# / run id> — <age>
**<project>** — ...

## Queued
- **<project>**: <n> todo (<slug>, <slug>, <slug>…)

## Open PRs
- **personal**: #<n> <title> — <repo> · <draft?> · <age>
- **other**: <n> PRs — `--scope all` to expand
- **cruft**: <n> PRs >1yr old — close?

## ⚫ Stale — reconcile?  (<n>)
- <slug> — claimed <age>, no PR/run — <likely-done? | genuinely dropped?>
```

With `--reconcile`, replace the last section with concrete offers:
"`<slug>` — PR #N merged <date>; mark done? [y/n]" and act on confirmation via
`mcp__dossier__task_complete` + `artifact_link`. One confirmation per item or a batched
"close all N?" — never a blind sweep, and never touch non-personal tasks without `--scope all`.

## Rules

- **Fire first.** A stuck dispatch loop or a hard block leads the board — everything else is
  backlog by comparison.
- **Quarantine stale.** Never let dead `in_progress` rows bury the live ones. If >10 tasks
  are stale, that itself is a finding: recommend a `--reconcile` pass.
- **Counts for the queue, not a dump.** The todo backlog is `<project>: <n> (slugs)`, not
  forty bullets.
- **Personal by default.** Non-personal buckets stay a collapsed count behind `--scope all`.
- **Read-only unless `--reconcile`.** The board observes; closing tasks is an explicit,
  confirmed action.
- **No process narration.** Don't say "I queried ship, then dossier". Just show the board.
- **PR numbers, run ids, task slugs are first-class.** Adjectives aren't.

## Where it sits

The third of the status triad — pick by tense:
- `/status` — **now, this session** (situational recap: happened / next / rec / need).
- `/wip` (← this) — **now, across every project** (what's open + in-flight, cross-store).
- `/shipped` — **just past** (retrospective on what landed).

Natural follow-ons: `/wip` surfaces a stuck ship run → investigate or `/work-driver` a retry;
surfaces a ripe queue → `/work-driver-prep <phase>`; surfaces a stale pile → `/wip --reconcile`.

## Source material

- `~/.claude/skills/status/SKILL.md`, `~/.claude/skills/shipped/SKILL.md` — the sibling
  status surfaces; keep the three distinct.
- `~/.claude/skills/work-driver/SKILL.md` — the natural action when the board shows ready
  work or a stuck run.
- dossier verbs: `task_list`, `project_list`, `project_overview`, `task_complete`.
- ship verbs: `mcp__ship__list_workflow_runs`, `mcp__ship__driver_status`.
