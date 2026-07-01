---
name: tdd
description: Turn a feature or initiative idea into a reviewed Technical Design Document — a markdown TDD at docs/features/<feature>/spec.md (problem, functional + non-functional requirements, architecture, key decisions/trade-offs, data model, API contract, key flows, a phased rollout plan with high-level tasks + dependencies + a validation gate, open questions) opened as a PR for agent review — AND seed the dossier corpus from it: create/locate the project, add phases mirroring the rollout plan, materialize tasks for the near-term phases, and link the doc back as a `doc` artifact. Use whenever the operator is starting a non-trivial new feature/system/initiative and says things like "write a TDD", "design doc for X", "let's spec out <thing>", "plan the rollout for <thing>", "turn this design into a doc and tasks", or wants the high-level design captured and tracked before implementation. Bridges design-doc <-> dossier and hands off to /work-driver-prep. Don't undertrigger — reach for this any time a chunk of new work needs a design pass before code, even if the operator just describes the system without saying "TDD".
argument-hint: "<feature-slug> [project:<slug>]"
user_invocable: true
---

# /tdd — design doc + dossier structure in one shot

Take a feature or initiative and produce two linked artifacts:

1. **A Technical Design Doc** — a markdown file at `docs/features/<feature>/spec.md` in the repo, opened as a PR so agents (and you) review it before any code is written.
2. **The dossier structure** seeded from it — the project, phases mirroring the TDD's rollout plan, near-term tasks, and a `doc` artifact linking back to the TDD.

Then hand off to `/work-driver-prep` (turns dossier tasks into per-task implementable specs) → `/work-driver` (ships them).

## The model: prose in the repo, structure in dossier

This is the core opinion the skill encodes, so internalize it before running:

- **The TDD prose lives in the repo**, version-controlled and reviewed via PR. The repo + PR review *is* the "Confluence" — better than Confluence: diffable, reviewed, next to the code. dossier does **not** store the TDD body.
- **dossier holds the structure and the link, not the prose**: a `project` (the initiative), `phases` mirroring the rollout plan, `tasks` (the implementable units), and a `doc` artifact pointing at the TDD file. dossier is the *index/graph* over the design, not its home.

A `/tdd` run that dumps the whole design into a dossier phase body is doing it wrong. The phase body is a short summary + a pointer; the design is the repo file.

## When to use

Triggers:
- "write a TDD for <thing>" / "design doc for <thing>" / "spec out <thing>" / "let's design <system>"
- "plan the rollout for <thing>" / "break <initiative> into phases"
- "turn this design into a doc + tasks" (a design discussed in-conversation that should be captured)
- Starting any non-trivial new feature/system where you'd want a reviewed design before implementation
- Explicit `/tdd`

Anti-triggers:
- A single small fix or one-PR change — `mcp__dossier__task_create` directly, then `/work-driver-prep`. A TDD for a 20-line fix is over-process.
- A batch of *already-scoped* tasks ready to ship — that's `/work-driver-prep`, not this.
- A polish/hygiene sweep — that's `/polish`.
- Pure research with no build intent — write a doc, but skip the dossier seeding (no project/phases to track yet).

## Arguments

`/tdd <feature-slug> [project:<slug>]`

- **`<feature-slug>`** (required): kebab-case slug for the feature/initiative. Becomes the doc dir (`docs/features/<feature-slug>/`) and, for a new initiative, the dossier project/phase naming root. Example: `cloud-backend`, `remote-sync`, `billing-v1`.
- **`project:<slug>`** (optional): the dossier project this belongs to. Default: infer from the repo (the repo's own dossier project) or, for a brand-new initiative, propose creating a new project named `<feature-slug>` (or a sensible parent). If ambiguous, ASK via `AskUserQuestion` — don't guess which project gets the phases.

If the design hasn't been discussed yet and there's no context to draw on, interview first (Step 2) before writing anything.

## Steps

### 1. Pre-flight

Resolve `(repo_dir, dossier_project_slug, feature_slug, branch)` or stop with a clear error.

- Confirm the repo (the cwd's project, under `C:/Users/MichaelHabib/pers/` for portfolio work).
- Resolve the dossier project: `mcp__dossier__project_get { slug: <project> }`.
  - Exists → use it.
  - Not found AND this is a new initiative → propose `mcp__dossier__project_create { slug, title, description, actor: "claude-code:michael" }`. Confirm the slug/title with the operator before creating — a project is the top-level unit and the slug is immutable.
- Pick a branch for the doc PR: `docs/<feature-slug>-tdd` (no forced prefix, per `/worktree-*` convention). Prefer a worktree off `main` so the operator's working tree is untouched (`/worktree-add` or `git worktree add -b <branch> .claude/worktrees/<branch> origin/main`).

### 2. Gather the design

The design content comes from one of two places, in priority order:

1. **The current conversation.** If the operator just discussed the architecture, decisions, trade-offs, or phases (the common case — `/tdd` usually follows a design discussion), extract from there. Don't re-interview what's already been decided.
2. **An interview.** If there's no prior context, ask — but ask in *batches* via `AskUserQuestion`, not one question at a time. The minimum you need to write a useful TDD: the problem/hypothesis, the one or two load-bearing decisions (and their alternatives), the rough phase breakdown, and what "validated / done" looks like.

Don't write a TDD full of `TBD`s. If a section genuinely can't be filled, mark it an **Open question** (§ template) rather than padding it — an honest open question is worth more than a fabricated decision.

### 3. Write the TDD

Write to `docs/features/<feature-slug>/spec.md` using this section template. It's the same shape proven on the dossier-cloud TDD (`docs/features/cloud-backend/spec.md` — the canonical example to imitate). Adapt depth to the size of the initiative; a smaller feature collapses several sections into a paragraph.

```markdown
# <Feature> — Technical Design Document

**Status:** draft / proposal — NOT a build commitment. The artifact we decide from.
**Owner:** @<operator-handle>
**Date:** <today, YYYY-MM-DD>
**Related:** <links to vision.md / PROTOCOL.md / prior docs / the dossier project>

> **Reviewers — focus areas:** <2-4 pointers to the sections that most need scrutiny — the load-bearing decisions and the riskiest flows.>

## 1. Problem & hypothesis
<Why this exists. The bet. What we're NOT doing (non-goals) and why.>

## 2. Functional & non-functional requirements
<FR as a short list. NFR as a table (latency / durability / consistency / security / operability / cost — whichever apply), each with a concrete target, not an adjective.>

## 3. Architecture overview
<The spine. A small diagram. What's new vs what's reused. Name the seam(s).>

## 4. Key decisions & trade-offs
<One row/subsection per real decision: the choice, the alternative, why. Mark any still-open fork as a decision the reviewer must weigh in on. This is where reviews earn their keep — make the trade-offs explicit.>

## 5. Data model
<Entities, shapes, storage layout, versioning. What changes vs today.>

## 6. API contract
<The interface(s): function/trait signatures, endpoints, config surface, error model. Be concrete enough that a reviewer can spot a wrong type or a missing case.>

## 7. Key flows
<Step-by-step for the load-bearing paths — the write path, the failure/retry path, the concurrency race, the degraded mode. Pseudocode or numbered steps. Cover what goes wrong, not just the happy path.>

## 8. Concurrency / consistency / failure model (if applicable)
<Retry policy, consistency guarantees, what happens when a dependency is down. State the model explicitly; "handle errors gracefully" is not a model.>

## 9. Rollout / implementation plan
<A table of PHASES. Each phase: goal, high-level tasks, depends-on, and a gate marker. Sequence them. If the initiative is big or unvalidated, put a VALIDATION GATE after the cheapest phase that proves the thesis — phases before the gate are what you commit to; phases after are gated on it. Note rough per-phase scope (e.g. weighted-LOC band) so "what are we committing to" is answerable.>

## 10. Open questions
<Genuine unknowns + decisions that need the operator. Better than fake certainty.>

## 11. Validation plan
<The gate. What measurable signal flips go/no-go. Prefer a binary, baseline-free signal over a vibe.>
```

Keep it honest about magnitude: a real initiative is a *program* (many phases, each with tasks), not a single feature — §9 is where that shows. But don't write deep specs for phases gated behind validation; that's speculative design and violates killer-per-step. Breadth (the full phase map) now; depth (per-phase detail) just-in-time.

### 4. Open it as a PR for review

The whole point of a TDD is that it's reviewed before code. Mirror the portfolio design-doc → branch → PR flow:

```bash
git add docs/features/<feature-slug>/spec.md
git commit -m "docs(<feature-slug>): TDD — <one-line>"   # + Co-Authored-By trailer
git push -u origin <branch>
gh pr create --base main --title "TDD: <feature> (draft)" --body "<summary + the decisions that need a call>"
```

Then request the canonical reviewer set via a PR comment: `@codex review` / `@claude review` / `@cursor review` (Copilot auto-reviews on open). This is a design review, not code review — say so in the comment and point reviewers at the §4 decisions and the riskiest §7 flows. **Don't merge it** — the operator decides when the design is locked. Surface the review feedback; fold actionable items into a v2 of the doc.

### 5. Seed dossier from the rollout plan

Now mirror §9 into dossier structure. **Structure and links only — never the prose.**

1. **Phases** — one `mcp__dossier__phase_add` per phase in §9, in order:
   ```
   mcp__dossier__phase_add {
     project: "<project>",
     slug: "<feature-slug>-<phase-slug>",   # or just <phase-slug> if unambiguous in the project
     title: "<phase title>",
     body: "<goal (1-2 sentences) + the phase's high-level tasks as a short list + depends-on + gate status>. Design: docs/features/<feature-slug>/spec.md §<n>.",
     actor: "claude-code:michael"
   }
   ```
   The phase body is a *summary + pointer*, not the design. It carries the high-level task list as prose so the work is visible even before tasks are materialized.

2. **Tasks — near-term phases only.** Materialize `mcp__dossier__task_create` tasks for the phases that are (a) unblocked (no upstream `depends_on`) AND (b) at or before the validation gate. Leave post-gate / blocked phases as task-less stubs (their high-level tasks live in the phase body as prose, materialized when the phase unblocks). This keeps the corpus from filling with speculative tasks for work you haven't earned — killer-per-step. Each task body uses the standard `## Problem / ## Fix / ## Acceptance / ## Test plan / ## Out of scope` shape so `/work-driver-prep` can spec it directly. Also tag each task with a recommended **model** + **effort** (a `**Model/effort:**` body line) so the operator dispatches it at the right tier: `opus` for correctness-critical or novel work, `sonnet` for mechanical / type-enforced changes (the cheaper default), `fable` rarely for production code; effort `extra`/`max` single-agent, `ultracode` reserved for adversarial review/verification. Tier tracks correctness-risk and design-novelty, not size - default `sonnet`/`extra` and justify each escalation in one line.

3. **Link the TDD** as a doc artifact to the project:
   ```
   mcp__dossier__artifact_link {
     project: "<project>",
     kind: "doc",
     ref: "docs/features/<feature-slug>/spec.md",   # stable repo path; also link the PR (kind: "pr") for the review thread
     label: "<feature> TDD",
     actor: "claude-code:michael"
   }
   ```

### 6. Print the operator-facing summary

Tight, no process narration:

```
/tdd <feature> — done

TDD:     docs/features/<feature-slug>/spec.md   (PR #<n>, reviews requested)
Project: <project>
Phases:  <N> added (mirrors the rollout plan)
Tasks:   <M> materialized for <near-term phase(s)>; <K> phases left as stubs (gated)
Doc link: artifact linked to project <project>

Next:
  1. Review PR #<n> (the design) — merge when the decisions are locked
  2. /work-driver-prep project:<project>:phase:<first-phase-slug>
```

## Key reminders

- **Prose in the repo, structure in dossier.** If you're about to paste the design into a phase body, stop — link it instead.
- **A TDD is reviewed before it's built.** Open the PR; request the agents; don't merge it yourself. The review is the value.
- **Breadth now, depth later.** Seed *all* phases (so the magnitude is visible) but materialize tasks only for the near-term/unblocked ones. Don't spec work gated behind validation.
- **Mark the gate.** For a big or unvalidated initiative, the §9 validation gate is the most important line in the doc — it's what separates "committed" from "speculative."
- **Open questions beat fake decisions.** An honest §10 entry is more useful to a reviewer than a fabricated §4 decision.
- **Surface ambiguity, don't guess.** Wrong project resolution puts phases in the wrong corpus; wrong feature slug puts the doc in the wrong dir. Confirm before creating.

## Anti-patterns

- **Don't store the TDD prose in dossier.** dossier indexes the design; the repo holds it. (The whole reason this skill exists.)
- **Don't propose new MCP verbs.** This skill composes dossier + filesystem + `gh`/`git`. If a step seems to need a new verb, re-frame it. (`feedback_skills_compose_mcps_dont`.)
- **Don't materialize tasks for every phase.** Post-gate phases are stubs until they unblock. Over-tasking is speculative design.
- **Don't write per-task implementation specs here.** Tasks land with a `## Fix` outline; `/work-driver-prep` turns each into a spec doc — that's its job. (`feedback_design_doc_then_pr`: smaller reviewable units, design → branch → PR.)
- **Don't make it generic.** The section template, the reviewer set, the prose-in-repo split — these are the operator's conventions, not knobs. (`feedback_opinionated_not_generic`.)
- **Don't bloat the doc to look thorough.** A 1,000-line TDD for an unvalidated bet is the opposite of killer-per-step. Match depth to what's been earned; defer the rest to §10 / post-gate phases.
- **Don't merge the design PR.** The operator locks the design.

## Source material

- `~/.claude/skills/work-driver-prep/SKILL.md` — the downstream consumer; turns the dossier tasks this skill creates into per-task specs + batches.
- `~/.claude/skills/work-driver/SKILL.md` — ships the batches.
- `~/.claude/skills/polish/SKILL.md` — sibling skill; same phase+task seeding pattern, same hand-off chain.
- `~/pers/dossier/docs/features/cloud-backend/spec.md` — the canonical TDD this template was extracted from (the dossier-cloud design). Imitate its section depth and the §9 rollout-plan table.
- Operator memory:
  - `feedback_design_doc_then_pr` — substantial work goes design-doc → branch → PR; smaller reviewable units. This skill *is* that front door.
  - `feedback_killer_per_step` — breadth now, depth just-in-time; park future phases as stubs, don't over-spec.
  - `feedback_skills_compose_mcps_dont` — no new MCP verbs; skills are the composition layer; the one blessed cross-MCP write is structure-seeding into dossier.
  - `feedback_opinionated_not_generic` — the template and conventions are opinions, not config.
  - `feedback_dossier_tool_not_protocol` — dossier is our index/graph; keep it lean, link don't store.

## Outcome

After `/tdd` runs, the operator has:
- A reviewed TDD at `docs/features/<feature-slug>/spec.md`, open as a PR with the canonical agents requested.
- A dossier project (created or located) with phases mirroring the rollout plan, near-term tasks materialized, and the TDD linked as a `doc` artifact.
- A printed next-step: review/merge the design PR, then `/work-driver-prep project:<project>:phase:<first-phase>`.

Hand-off chain: **`/tdd <feature>` → review/merge the design PR → `/work-driver-prep` → `/work-driver` → PRs ship → `artifact_link` the PRs back to the tasks.** The design becomes the index; the index drives the implementation; the implementation links back. The loop closes in dossier.
