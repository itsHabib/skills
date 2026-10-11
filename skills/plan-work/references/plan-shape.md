# Plan shape and task cards

Use this when an initiative needs a full hierarchy. Adapt or omit sections that
do not help a decision or handoff. This is an output pattern, not a fixed form.

## A readable plan

Start with a short vision and the current state. Then show the milestone map,
epic map, and task breakdown. Put detail close to the first work that can start.
Use a simple diagram only if it makes relationships clearer than the tables.

```markdown
# Initiative name

Status: proposed plan / revised plan / implementation in progress
Context: date, relevant sources or existing records

## Vision
Who this serves, what becomes better, and why.
Representative end-to-end sequence.
Requirements and constraints; provisional choices and their rationale.
First-delivery boundary; later ambitions.

## Milestones
| ID | Observable outcome | Smallest useful deliverable | Completion evidence | What remains unproved |
| --- | --- | --- | --- | --- |

## Epics
| ID | Outcome | Milestones served | How the outcome is demonstrated |
| --- | --- | --- | --- |

## Task breakdown
| ID | Epic / milestone | Task and bounded deliverable | Prerequisites | Done when | Status |
| --- | --- | --- | --- | --- | --- |

## First execution sequence
Ready work in dependency order; details for this milestone.
Parallel lanes only where useful, with shared-resource ownership and integration.

## Decisions, risks, and acceptance
Important assumptions, cheapest way to resolve them, and effects on scope.
Decision conditions and human/external acceptance conditions, kept separate
from the task prerequisite graph.

## Later work
Optional and candidate work with the evidence that would justify promotion.
```

For large programs, stable IDs such as `M0`, `E1`, and `T101` make cross-references
easy. These exact prefixes are optional. Keep an established project's IDs.
Counts are a consistency check, not a goal or a measure of progress. Include
project-specific requirements such as accessibility, privacy, recovery, or
maintainability where they affect outcomes; do not add a generic compliance epic.

## Near-term task card

```markdown
### T101 — Deliverable-oriented title
Epic / milestone: E1 / M0
Status: proposed / ready / in progress / blocked / verified / accepted
Owner: actual assignee, proposed role, or unassigned
Depends on: actual task IDs, or none
Other conditions: decision or acceptance reference, only when relevant

Outcome: the problem this resolves and the result it leaves.
Scope: included work and the meaningful boundary.
Inputs / touchpoints: observed artifacts, interfaces, materials, or locations;
mark any proposed additions.

Steps: enough detail to begin, without rewriting an entire future design.

Acceptance: observable result and relevant failure/recovery behavior.
Verification: command, walkthrough, measurement, or human observation.
Evidence: existing result/revision/artifact, or pending.
```

Use the task table as navigation when detailed cards follow: keep its acceptance
cell to a short summary and put the full criteria in the card. Avoid repeating
the same rationale in the vision, milestone, table, and card. A compact row
suffices for later tasks. Combine fields in prose when the hierarchy is clear.
Task cards should remove ambiguity that would otherwise stop a worker.

## Example of useful depth

For an enclosure-building task, "implement placement" is too vague. Useful
details describe a preview, changing its position/size, a quoted cost, bounds and
collision reasons, confirm/cancel, and evidence that rejected or repeated actions
cannot charge twice. A meaningful first work sequence could implement validation
and cost calculation, connect the preview and commit behavior, then demonstrate
valid, invalid, and canceled placements. Those steps need not become separate
tickets.

The example generalizes through invariants, not game features. A research task
might preserve a source trail and separate findings from inference. An assembly
task might check alignment and repairability before permanent fastening. Choose
acceptance that tests the real source of failure in the particular work.

## Keep acceptance and scheduling separate

Distinguish reading an existing artifact from waiting for its task to finish.
Inspecting a form draft is an available input; it does not create a dependency on
completing that form. State which usable output or decision a dependency requires
so unfinished acceptance or later revisions do not create false cycles.

Suppose `T101` produces a working prototype and `T102` prepares an observation
guide. A user trial needs both. Independent preparation of the guide need not wait
for prototype acceptance. Expensive expansion that depends on the trial's result
is conditional on that decision. The milestone is accepted only after the stated
observation happens, even if all implementation tasks pass their technical checks.

On updates, retain the distinction: "implemented; device trial pending" is more
useful than claiming completion or marking all related work blocked. If the trial
changes direction, revise affected milestones and tasks while preserving the
history of what was already demonstrated.
