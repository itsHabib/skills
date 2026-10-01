---
name: cut
description: >-
  Find the smallest solution that preserves the intended outcome. Use for scope
  audits of a spec, implementation, or reviewer findings: "is this over-engineered",
  "what can we remove", "cut this down", or "the review is bloating the PR".
  Recommend concrete cuts and apply them when edits are already authorized.
argument-hint: "[spec <path> | diff <pr-or-range> | findings <pr>]"
user_invocable: true
---

# /cut

What can we remove while still solving the problem well?

Start with the outcome, not the proposed architecture. The answer may be to build
less, reuse something, or keep the current solution. Fewer lines are supporting
evidence, not the objective. Clever compression that makes maintenance harder is
not a cut.

## Start from the request

Infer the target and mode from the conversation or current work. `/cut` alone is
enough when that context is clear. Use `/cut spec <path>`, `/cut diff <pr-or-range>`,
or `/cut findings <pr>` to name a target explicitly. If the target is ambiguous,
ask one specific question rather than auditing an arbitrary checkout.

An audit request produces recommendations. An implementation request authorizes
appropriate edits within its existing scope; do not ask for the same permission
again. Publishing, installing and merging follow the existing task authorization.
Read the relevant repository instructions and acceptance criteria before cutting.

Identify the actual subject: spec version, PR head, commit range, or working tree.
For a PR, fetch and inspect its exact head and base; local branch names may be stale.
Preserve unrelated edits and other agents' work. If required evidence is unavailable,
say what is unknown rather than issuing a confident cut.

## Make the judgment

For each substantial piece, ask:

- What outcome requires it? Distinguish an explicit request, a necessary consequence,
  an established repository contract, and speculation. An unstated requirement is
  not automatically unnecessary.
- What concretely breaks without it? Trace callers and failure paths before assuming
  that one implementation, an internal check, or an awkward test is dispensable.
- What is the cheapest adequate alternative: omit it, reuse existing code, use the
  standard library or platform, or write a small direct implementation?

Look for speculative extension points, duplicate mechanisms, unnecessary options,
wrappers that add no decision, and tests coupled to replaceable implementation details.
A dependency or abstraction can be the simpler choice when it removes real complexity.
Consider setup, operation and maintenance as well as code size.

Preserve required behavior, security and authority boundaries, data integrity,
accessibility, error handling and evidence that checks them. Challenge an expensive
requirement openly; do not silently delete it to make the implementation smaller.

## Apply the lens where the work is

**Spec:** challenge the requirements and proposed solution before planning their
implementation. Name the smallest useful first slice, what to leave out, and the
observed need that would justify adding it later. When editing, update the existing
scope/non-goals section instead of appending another document or duplicate section.
Respect explicit budgets, but never invent a numeric gate or use a budget to waive
necessary behavior. Surface a real conflict with the agreed outcome.

**Diff:** read the changed behavior and its consumers, not just a size summary.
Give concrete removals or replacements with file references. Apply justified cuts
when authorized, then run the relevant checks. A failing test may expose necessary
behavior; changing or deleting that test is not proof of preservation. Remove a test
only when its assertion is obsolete and required behavior remains covered.

Use ordinary Git summaries if size helps explain a change. Name the base and whether
the measurement covers commits or working-tree edits; include untracked work in the
assessment. A committed range does not measure uncommitted cuts. Failed Git reads
are unavailable evidence, never a zero-size success. Do not guess cross-language
quality, dependency counts or test value from regex totals.

**Findings:** read current inline review threads and PR comments, including existing
dispositions, against the head they reviewed. Separate whether a finding is valid,
how serious it is, and whether its proposed fix adds unnecessary scope. Recommend:

- **Fix:** a demonstrated defect or unmet requirement, using the smallest adequate fix.
- **Defer:** valid, non-blocking work outside this task; name why and when to revisit.
- **Decline:** invalid, already addressed, or requesting an excluded capability;
  provide evidence. New evidence can invalidate an earlier design decision.

Use the repository's existing disposition record and review policy. At a panel cap,
stop requesting panels; mandatory defects still need a fix or a blocker. Report any
remaining required verification at the changed head. `/cut` does not accept residuals,
dismiss reviews, or replace independent verification or merge authority.

## Leave a short useful result

Lead with the recommendation: keep, simplify, or replace. For each worthwhile cut,
name the location, proposed change, behavior preserved, tradeoff and validation.
After edits, report what changed, what checks actually ran, and any uncertainty.
Keep decisions in the existing task/spec/PR when an update is authorized; a separate
report, per-requirement table, score and second reviewer are not required.

"No worthwhile cuts" is a valid result. Do not manufacture work to satisfy the skill.
