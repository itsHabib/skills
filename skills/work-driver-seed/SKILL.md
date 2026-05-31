---
name: work-driver-seed
description: Seed a dossier phase + PR-sized task docs from a described chunk of work — sized and dependency-ordered for the /work-driver chain. The lightweight front-end to /work-driver-prep for work that's too big for a single hand-made task but too small for a /tdd (no thousands-of-lines reviewed design doc warranted). Composes dossier verbs only; no repo design doc, no spec docs, no execution. Triggers: "seed the phase + tasks", "set up dossier tasks for <chunk>", "break this chunk into tasks for the driver", "seed work-driver for <chunk>", a mid-size multi-PR chunk that's been discussed and just needs to land in dossier as tasks, explicit /work-driver-seed. Anti-triggers: a single one-off task (task_create directly), a real feature needing a reviewed design (/tdd), tasks already created and ready to spec (/work-driver-prep), a hygiene/polish sweep (/polish).
argument-hint: "[project:<slug>] [--phase <slug> | --into-phase <existing-slug>]"
user_invocable: true
---

# /work-driver-seed — seed a phase + tasks for the driver

Take a chunk of work that's already been thought through (in the conversation, or described in the argument) and turn it into a dossier **phase + PR-sized task docs**, dependency-ordered and shaped so `/work-driver-prep` can spec and batch them without further design. This is the missing front-end of the driver chain:

```
/work-driver-seed   →   /work-driver-prep   →   /work-driver
 (phase + tasks)        (specs + driver.md)      (ship + merge)
```

`/tdd` also seeds dossier — but it bundles seeding with writing a reviewed repo design doc, which is overkill for a chunk that's a few PRs of a couple hundred LOC each. This skill is the seed step alone: the design lives in the phase + task bodies (dossier-native), not in a repo doc. **One job: structure into dossier. No prose-in-repo, no spec docs, no fan-out.**

## When to use

Triggers:
- "seed the phase + tasks for <chunk>" / "set up dossier tasks for this" / "break this chunk into tasks for the driver"
- "seed work-driver for <chunk>" / "get this into dossier as tasks"
- A mid-size chunk (≈ 2–6 PRs, each a couple hundred LOC) that's been designed in conversation and just needs to land as tasks
- Explicit `/work-driver-seed`

Anti-triggers (each has a better front door):
- **A single one-off task** → `mcp__dossier__task_create` directly. One task needs no decomposition.
- **A real feature** (thousands of LOC, multiple validated phases, a design worth reviewing before code) → `/tdd`. That writes the repo design doc + seeds. If you'd want a reviewed spec.md, it's a `/tdd`, not this.
- **Tasks already in dossier, ready to ship** → `/work-driver-prep`. This skill *creates* tasks; prep *consumes* them.
- **A polish / hygiene sweep** → `/polish`. That audits and seeds in one pass.

The litmus: *the design is settled, it's more than one PR, and it doesn't need a reviewed repo doc.* That's this skill.

## Arguments

`/work-driver-seed [project:<slug>] [--phase <slug> | --into-phase <existing-slug>]`

- **`project:<slug>`** (optional): the dossier project the work belongs to. Default: infer from the repo (the cwd's project under `C:/Users/MichaelHabib/pers/`). If it can't be inferred and isn't given, ASK via `AskUserQuestion` — wrong project puts the phase in the wrong corpus.
- **`--phase <slug>`** (optional): slug for a NEW phase to create for this chunk. Default: a kebab-case slug derived from the chunk name. This is the common case.
- **`--into-phase <existing-slug>`** (optional): append the tasks to an EXISTING phase instead of creating one. Use when the chunk is the next batch under an umbrella phase that already exists. Mutually exclusive with `--phase`.

The chunk of work itself comes from the **conversation** (the common case — this skill usually follows a design discussion) or, if there's no prior context, from a short interview (Step 2).

## Steps

### 1. Pre-flight

Resolve `(dossier_project_slug, phase_mode, phase_slug)` or stop with a clear error:

- Resolve the project: `mcp__dossier__project_get { slug: <project> }`.
  - Not found → surface `dossier project '<project>' not found — create it via mcp__dossier__project_create or check the slug`. Don't auto-create; the project is the top-level unit.
- Phase mode:
  - `--into-phase <slug>` → verify that phase exists in the `project_get` response; error if not. New tasks append to it.
  - else (new phase) → compute `phase_slug` (`--phase` or derived). Reject if it already exists in the project: `phase '<slug>' already exists; pass --phase to rename or --into-phase to append`.

### 2. Gather + decompose the chunk into PR-sized units

The content comes from the conversation first (don't re-interview a design that's already been settled); interview only if there's no context, and in **batches** via `AskUserQuestion` (the goal: the chunk's shape, the natural seams, the dependency order, and what "done" looks like per unit).

**Decompose into units where each unit ≈ one PR** — a couple hundred LOC, inside the repo's "amazing/ideal" band (`< 700` weighted; prefer `< 500`). Find the natural seams; don't split mechanically:

- **Behavior-preserving refactor first, then the change.** Extract/move with the existing tests as the net as PR 1; build the new behavior on top. (The classic: lift shared code down/up, *then* use it.)
- **By layer** (e.g. `domain → store → server`) when the work crosses layers — one unit per layer touched.
- **By cluster** when one layer has independent groups (e.g. the task verbs vs the phase verbs).
- **Foundation → consumers.** The unit that adds a shared thing comes before the units that use it.

For each unit, capture three things the downstream chain needs:
- **Files it touches** — concrete paths (`src/store.rs`, `src/server.rs`, `tests/...`). `/work-driver-prep` infers parallel-safety from these.
- **Dependencies** — which other unit(s) must land first, by their task slug. The refactor-before-feature and foundation-before-consumer seams *are* dependency edges.
- **The acceptance / gate** — the observable signal the unit landed (often: a test passes, behavior unchanged, a field is gone).

If a unit busts the band (`> 700` weighted), split it before seeding — don't seed a task you already know is too big.

**Surface the proposed phase + task breakdown to the operator before writing anything to dossier.** A numbered list — phase, then each task with its one-line goal, files, and deps. Cheap insurance against a wrong decomposition becoming N wrong tasks.

### 3. Add the phase (unless `--into-phase`)

```
mcp__dossier__phase_add {
  project: "<project>",
  slug: "<phase_slug>",
  title: "<chunk title>",
  body: "<shared-design capture — see below>",
  actor: "claude-code:michael",
  after_phase: "<optional — the umbrella/preceding phase slug>"
}
```

The phase body is the **shared-design capture** — this is where "design-first" lives for a chunk that doesn't get a repo doc. Keep it a summary + the cross-cutting calls, not an essay:

- **Goal** (1–2 sentences): what the chunk does and why.
- **Approach**: the spine — what moves where, the shared mechanism (e.g. "service-layer get→transition→put CAS loop"), in a few lines.
- **Cross-cutting decisions** that span the PRs (the ones that shouldn't be re-litigated per task) with a recommended default — e.g. "keep vs. drop the process write_lock → recommend keep for now". These get *decided and reviewed when the PR that implements them lands*; the phase body just names them so they're not lost.
- **PR order + validation gate**: the unit list in order, and the gate that proves the chunk landed correctly (e.g. "behavior parity — existing suite green at each step").
- **Pointer** to any umbrella design doc this chunk sits under (e.g. `docs/features/<feature>/spec.md §N`).

### 4. Create the tasks — one per unit, prose carries the contract

For each unit, `mcp__dossier__task_create`. The body shape is the dossier task-spec shape `/work-driver-prep` consumes:

```markdown
## Problem

<2–4 sentences. Concrete. The current state and why it needs changing. File paths + call sites where you have them.>

## Fix

<Concrete steps: which files, what moves/changes. Name the specific functions/types. This is the unit's plan, not the whole chunk's.>

**Files:** `src/foo.rs`, `src/bar.rs`, `tests/baz.rs`   <!-- explicit — prep's conflict scan reads this -->
**Depends on:** `<upstream-task-slug>` (must land first — <one-line why>)   <!-- omit for unblocked units -->

## Acceptance

<Observable result that proves the unit landed. A test name, a behavior, a grep that should come back empty.>

## Test plan

<How to confirm post-merge — often one command (`make check`) + the specific test(s) added or retargeted.>

## Out of scope

<What this PR deliberately doesn't touch — bounds the diff. Critical: the agent uses this to keep the unit one-PR-shaped.>
```

Two non-negotiables for the chain to work — both are about **prose**, because `/work-driver-prep` scans the body text, not structured fields:

1. **Explicit file paths** in a `**Files:**` line. Prep's file-overlap pass (3a) reads these to decide what can run in parallel. No paths → it can't batch safely.
2. **Explicit dependency phrases** in a `**Depends on:**` line that names the upstream **task slug** with a dep verb (`depends on`, `after`, `requires`). Prep's dep scan (3b) is a prose scan — a dependency that lives only in a structured field is invisible to it.

Always set the dependency in the `**Depends on:**` prose line — that's what `/work-driver-prep` actually reads, so it's the carrier that makes the chain correct. The structured `depends_on` field is also a real arg on **`task_create` (create-time) and `task_update`** in current dossier; pass it there too so the dossier graph matches:

```
mcp__dossier__task_create { project, slug, title, actor, body, phase, depends_on: ["<upstream-slug>"] }
```

Caveat surfaced by this skill's first dogfood: a *running* dossier MCP server can lag the source — if the connected server's `task_create` / `task_update` schema doesn't advertise `depends_on`, you can't set the structured field until that server is rebuilt + restarted. The prose line is independent of the running build, so the chain still works regardless. **Prose mandatory; structured best-effort.**

**One task per shippable unit. Don't bundle** two PRs into one task, and **don't over-split** one PR into several tasks. The unit boundary from Step 2 is the task boundary.

### 5. Link the umbrella design doc (if any)

If the chunk sits under an existing repo design doc (e.g. it's a sub-feature of a `/tdd`'d initiative), link it once at the project level so the graph connects:

```
mcp__dossier__artifact_link { project: "<project>", kind: "doc", ref: "docs/features/<feature>/spec.md", label: "<feature> design", actor: "claude-code:michael" }
```

For a self-contained chunk with no umbrella doc, skip — the phase body is the design.

### 6. Print the operator-facing summary + hand-off

Tight, no process narration:

```
/work-driver-seed — done

Project: <project>
Phase:   <phase_slug>   (<new | appended to existing>)
Tasks:   <N> created

  1. <task-slug> — <one-line goal>            [files: ...]  [deps: none]
  2. <task-slug> — <one-line goal>            [files: ...]  [deps: #1]
  ...

Next:
  /work-driver-prep project:<project>:phase:<phase_slug>
```

## Key reminders

- **One task ≈ one PR (a couple hundred LOC).** If a unit busts the repo's PR band, split it before seeding — never seed a task you already know is too big.
- **Dependencies must be in the task-body prose**, naming the upstream **task slug** with a dep verb. `/work-driver-prep` scans prose, not the structured `depends_on` field — a dep that's only structured is invisible to batching. Set the structured `depends_on` too (it's a `task_create` / `task_update` arg in current dossier), but the prose is what makes the chain correct — and a stale running server may not accept the structured field anyway.
- **Explicit file paths in every task body.** Conflict-aware batching depends on them.
- **The phase body is the design.** For a chunk, "design-first" means a sharp phase body (approach + cross-cutting calls + gate), not a repo doc. If you find yourself wanting a reviewed spec.md, this was a `/tdd`, not a seed.
- **Surface the breakdown before writing.** Confirm the phase + task partition with the operator before any dossier write.

## Anti-patterns

- **Don't write a repo design doc.** That's `/tdd`. This skill is dossier-native — the design lives in the phase + task bodies.
- **Don't write spec docs or a `driver.md`.** That's `/work-driver-prep`. Tasks land with a `## Fix` outline; prep turns each into a spec and batches them.
- **Don't fan out / ship.** That's `/work-driver`. This skill stops at created tasks + the printed hand-off.
- **Don't propose new MCP verbs.** Compose `mcp__dossier__*` (phase_add, task_create, task_update, artifact_link). If a step seems to need a new verb, re-frame it. (`feedback_skills_compose_mcps_dont`.)
- **Don't bundle or over-split.** One shippable PR = one task. A "do the whole refactor" mega-task defeats the per-task parallelism the chain exists for; ten tasks for one PR is noise.
- **Don't seed speculative work.** Only units that are actually committed and unblocked-or-soon. Post-gate / maybe-later work stays out — name it in the phase body if it must be remembered. (`feedback_killer_per_step`.)
- **Don't make it configurable.** No strictness knobs, no per-task templates. The shape is the operator's chain convention. (`feedback_opinionated_not_generic`.)
- **Don't use it for one task or a whole feature.** Below the band → `task_create`. Above it → `/tdd`. This is the middle.

## Source material

- `~/.claude/skills/work-driver-prep/SKILL.md` — the consumer; its Step 3 (file + dep prose scan) is *why* this skill's task bodies must carry explicit `**Files:**` and `**Depends on:**` lines.
- `~/.claude/skills/tdd/SKILL.md` — the heavy sibling; its Step 5 (seed dossier from the rollout) is the same operation this skill does standalone. Same task-body shape, same actor, same phase-body-as-summary rule. (If `/tdd`'s seeding and this ever drift, reconcile toward this skill.)
- `~/.claude/skills/polish/SKILL.md` — sibling seeding skill; same phase + task pattern, same hand-off chain.
- Dossier task-body shape: any `~/pers/dossier-state/projects/<project>/tasks/*.md` — mirror the voice.
- Operator memory:
  - `feedback_design_doc_then_pr.md` — substantial work goes design → reviewable units; this skill is the lightweight front door for chunks (the heavy one is `/tdd`).
  - `feedback_pr_sizing_bigger.md` — units are PR-sized; prefer fewer, bigger PRs over a swarm of tiny ones, but keep each inside the band.
  - `feedback_killer_per_step.md` — seed only committed, near-term units; park the rest in the phase body as prose.
  - `feedback_skills_compose_mcps_dont.md` — no new MCP verbs; dossier-seeding is the one blessed cross-MCP write.
  - `feedback_opinionated_not_generic.md` — the shape is an opinion, not config.

## Outcome

After this skill runs, the operator has:
- A dossier phase whose body captures the chunk's shared design (approach + cross-cutting decisions + PR order + validation gate).
- N PR-sized tasks under it, each with `## Problem / ## Fix / ## Acceptance / ## Test plan / ## Out of scope` and explicit `**Files:**` + `**Depends on:**` prose (the dependency carrier `/work-driver-prep` reads), plus the structured `depends_on` when the running server accepts it.
- A printed `/work-driver-prep project:<project>:phase:<phase_slug>` hand-off.

Hand-off chain: **`/work-driver-seed` → operator skims the tasks in dossier → `/work-driver-prep project:<project>:phase:<phase>` → `/work-driver <driver.md>` → PRs ship → `artifact_link` the PRs back.** The seed becomes the structure; prep specs it; the driver ships it; the index closes the loop in dossier.
