---
name: plan-work
argument-hint: "[idea or initiative]"
user_invocable: true
description: >-
  Turn a substantial idea or initiative into a coherent vision, outcome-based
  milestones, epics, and dependency-ordered tasks with acceptance evidence and a
  concrete first deliverable. Use for "plan this out", "give me the epics and
  tasks", "break this big idea into work", "make a roadmap and backlog", or
  revising an existing initiative plan. Applies to software, research, courses,
  operations, and physical projects. Scale down for small work; do not replace a
  straightforward execution request with a planning exercise.
---

# Plan Work

Turn ambition into a plan someone can act on. Preserve the whole vision, identify
the smallest meaningful result, and make its work concrete enough to hand off.
Success is a coherent, reviewable plan with a credible next action; the plan is
not evidence that the work has been built or accepted.

## Ground the plan

Use the conversation and current project records first. Recover decisions,
constraints, existing work, and authorization instead of re-interviewing them.
For an existing project, inspect the relevant instructions and implementation or
source material before inventing new work. Distinguish observed facts, user
requirements, provisional choices, and open questions.

Ask only for missing information that changes the outcome, scope, or first
milestone. Continue independent planning while answers are pending. Choose and
label reasonable defaults for reversible details; do not make the user become a
domain expert to choose a direction. If an unresolved decision controls later
work, identify the decision and its dependent tasks rather than making it a
silent assumption. Verify current technical, cost, or domain claims when they
affect the plan; do not disguise estimates as researched facts.

Scale the artifact to the work. A small job may need an outcome and a few tasks.
A substantial initiative needs the hierarchy below. The number of epics, tasks,
documents, and agents follows the problem; never inflate the plan to fill a
template. Read [plan-shape.md](references/plan-shape.md) when producing a full
plan or writing detailed task cards.

## Build the hierarchy

1. **Vision:** Name who benefits, the change they should experience, why it
   matters, and the essential constraints. Describe a representative use or work
   sequence. State what the first delivery includes and what remains later.
2. **Milestones:** Describe observable increases in capability or knowledge.
   Each has a deliverable, completion evidence, and a boundary on what it proves.
   The first milestone should complete one representative end-to-end loop under
   a real constraint. Preserve the project's essential difficulty: a polished
   shell or isolated component often cannot test the main idea.
3. **Epics:** Group work by meaningful outcomes. Each epic explains what becomes
   possible and how that will be demonstrated. Milestones usually cut across
   several epics; they are not successive departments such as "all backend"
   followed by "all frontend". Use domain-appropriate language for nonsoftware
   work instead of forcing it into engineering categories.
4. **Tasks:** Give every scoped task a stable ID, parent epic, milestone,
   bounded deliverable, prerequisites, and observable done condition. Name
   useful ownership roles without pretending an agent or person is assigned.
   Use scope and uncertainty to size tasks, not arbitrary line counts. A task
   should yield a reviewable result; split unrelated outcomes and merge tiny
   steps that have no independent value.
5. **First sequence:** Detail the next meaningful milestone with task cards and
   a dependency order. Break its first ready task into concrete implementation
   or investigation steps. Keep later milestones as outcome-level tasks until
   evidence makes their design worth committing to. Mark optional and speculative
   work explicitly; do not bury it among ready tasks.

For research, evidence and a justified decision can be the deliverable. For a
course, test learner performance rather than treating finished slides as learning.
For a physical project, a measured fit or usable assembly can be the first slice.
Do not translate every project into a software MVP.

## Make the task plan executable

For each near-term task, state:

- The problem or outcome, and what the deliverable changes.
- Included work and the boundary that prevents unbounded expansion.
- Required inputs and explicit task IDs it depends on. Use actual files,
  interfaces, source material, materials, or locations when known; label proposed
  ones and avoid invented code locations.
- Acceptance evidence: what to run, inspect, measure, or observe, and the expected
  result. Include a meaningful failure/recovery case when the task's risk calls
  for it. Tests are one form of evidence, not a universal requirement.
- Current status and remaining uncertainty. Record evidence only after it exists.

Separate three kinds of conditions:

- **Task prerequisite:** a named input needed to start or finish the work.
- **Decision condition:** a choice or experiment whose result determines whether
  a branch of work should proceed.
- **Acceptance condition:** who must judge the delivered outcome, using what
  evidence, before calling the milestone accepted.

Acceptance conditions do not automatically block independent preparation.
Conversely, implementation or automated checks do not satisfy human acceptance.
When a decision is pending, state which work is ready, which is conditional, and
what evidence will resolve it. Do not impose new approval rituals on work already
authorized by the user.

Where parallel work helps, identify independent deliverables and shared seams,
give each overlapping file/resource a single writer, and name integration work.
Propose roles and handoffs; use agents for bounded planning research or critique
when useful. Do not confuse a proposed team with dispatched implementation.

## Check and deliver

Before presenting the plan, check:

- Every essential promised outcome has both work and verification; every scoped
  task supports an outcome or reduces a named uncertainty.
- IDs are unique, references resolve, prerequisites have a feasible order, and
  there are no cycles or impossible milestone conditions. Check inherited
  conditions too. For a large graph, use a small local check rather than trusting
  a visual skim; no special task database or file format is required.
- The first milestone can demonstrate the central value. Counts agree with the
  actual task list and distinguish scoped, optional, and candidate work.
- Time, cost, workload, and performance numbers have a basis or are labeled
  targets/estimates. State the uncertainty instead of inventing precision.
- Unknowns and genuine external blockers have a next action. Completed work
  retains its evidence and remaining limits.

For a complex initiative, a bounded independent critique can test the weakest
assumption or first milestone. Resolve material contradictions once; do not build
an endless review process around the plan.

Save in the user's requested or established destination. Reuse existing planning
records and their IDs; avoid a second competing backlog. If no destination is
specified, use the available document workflow for a discoverable plan and tell
the user where it lives. One document with sections is enough until separate
vision/backlog/detail documents improve navigation. No particular tracker,
repository, cloud service, or plugin is required. Verify saved content before
claiming delivery.

On revision, reconcile changed scope, dependencies, evidence, and status in place.
Preserve stable IDs; record superseded or deferred work rather than silently
renumbering it. Distinguish proposed, implemented, verified, and accepted when
those differences affect the next action. Do not reset real progress to a draft.

Finish with the vision, first milestone, plan link/location, and next ready task
or material decision. A planning request alone does not authorize implementation,
external ticket creation, publication, spending, or messages to other people.
Existing explicit authorization still applies. If execution is also requested,
continue with the ready work rather than asking for the same permission again.

## Fit with other planning tools

This skill produces the overall work plan. Use a technical design workflow only
when a specific architecture decision needs it; use tracker/driver workflows
when the user wants the ready tasks materialized or executed. Other planning and
handoff skills can consume or deepen parts of the plan, but are not prerequisites
and must not silently expand its scope.
