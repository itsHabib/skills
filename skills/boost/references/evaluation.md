# Evaluation and evidence

Use this when a measurement, comparison or frozen experiment decides whether
to accept a result. Apply the parts relevant to the claim, reusing established
evidence; a small repair does not need an experimental protocol for everything.

## Establish what actually ran

Trace required inputs to their producer record, revision, content or other
authoritative identity. A filename or modification time alone may select the
wrong object. Verify that required inputs were consumed, not silently skipped.
Missing inputs, load errors and empty required outputs mean failure or unknown,
not a successful negative finding. A wrapper check can be sufficient.

Reproduce the relevant baseline through the actual caller or evaluator entry
point before extending it. Capture the effective arguments, defaults and relevant
environment, seeds or configuration as well as source and input identities.
Retyping an apparently equivalent call may exercise a different implementation.
For variable results, compare under the declared repeatability rule rather than
assuming identical bytes. Keep independent implementations as cross-checks:
replaying the same code establishes alignment, not independent correctness.
Use permitted baseline or development runs to distinguish a prediction of the
intended system from a prediction of defects in its implementation or judge.
Keep judged-case outcomes out of that preparation for a blind prediction.

## Validate the measurement

Name the quantity, units, scoring function and correspondence rule. A point sum
is not automatically an area or volume; nearest neighbors are not necessarily
the same entities. Use stable identity when the contract requires correspondence;
geometric matching can be correct when that is the intended measure. Exercise
reordering or nearby distinct entities when they could expose a pairing error.

Check an unchanged baseline and a known nonzero perturbation or deliberate defect
with established expected results. Self-comparison alone can pass a broken
checker. Test ranking as well as feasibility when choosing among candidates.
Identify shared parsing, transformations, data or assumptions that could conceal
the failure on both sides; use an independent check that bypasses the relevant
dependency. Preserve the controls and their observed results in the handback.

Repeat unchanged inputs when variability could affect the decision. Record the
observed variation; two matching runs neither prove determinism nor establish
an error bound. Repetition does not expose a shared systematic error.

Record established resolution and uncertainty for numerical comparisons,
including apparent matches. Nominal resolution alone is not a bound on error.
When uncertainty is unknown, do not invent a tolerance from the discrepancy.
Accept only if the full range allowed by the established uncertainty satisfies
the requirement; refine the check or report inconclusive if it spans passing
and failing outcomes. Freeze the mapping from values or bands to labels before
seeing confirmatory results. For one-sided guarantees, a symmetric comparison
tolerance can hide an invalid underestimate. Finite passes are not a general proof.

## Freeze a meaningful comparison

Before confirmation, record the proposed change, predicted changes and relevant
unchanged behavior, how each will be measured, acceptance rules, and what each
outcome means for the next decision. Include partial success and inconclusive
outcomes where meaningful. Exploration can discover new explanations; label it
as such instead of pretending its predictions were fixed in advance.

If an independent prediction is part of the test, dispatch it once the case's
inputs and scoring rule are frozen. Retain the prediction before the judged case
starts, with evidence of that ordering; a content hash alone proves neither
timing nor independence. Keep the lead's answer and judged outputs out of the
helper's packet. A prediction made after that case has started is a late
prediction, not its pre-registration; if informed by its result, label it post-hoc.
For a run already underway, coordinate a hold before the next case only within
existing authority and resource ownership. Otherwise target a later unstarted
case without interrupting the current run or claiming retroactive registration.

Declare the scored unit, exclusion rule, aggregation and required coverage.
Apply exclusions at that declared unit, not whichever level produces a favorable
answer; check mixed groups where aggregation could hide the distinction. Report
total, excluded, failed, empty and scored units with their relevant denominators.
A no-op control may prove alignment without testing the claimed improvement.

Estimate exclusion consequences using permitted development data or metadata.
Keep held-out outcomes out of rule design and candidate selection. If an allowed
exclusion depends on held-out outcomes, freeze its procedure and coverage rule
first, then report the resulting counts after evaluation. Too little scoreable
data can make the result inconclusive; do not silently shrink the denominator or
adopt a universal minimum fraction unrelated to the task.

Preserve the exact evaluated snapshot: source, input identities, effective call,
scoring rules and predictions. Use an immutable revision, protected copy or
appropriate identity checks, including checking for mutation during a run when
that is possible. A dedicated folder alone is not immutability. Write diagnostics
outside frozen inputs. Candidate builders must not receive withheld answers.
An implementation helper may edit an assigned candidate; a verifier preserves
the subject under test. Neither silently edits the frozen baseline or grader.

Include consequential disk and memory needs, waiting and resource coordination
in the budget. Keep scratch bounded. Remove only owned disposable scratch after
retaining the evidence needed to reproduce the result; cleanup must not erase
the sole reproducer or another worker's files.

## Preserve what the result means

Trace decision-bearing numbers to exact artifacts and fields, commands or
derivations and the input revision. One grouped source can support several
numbers. A peer's message is a lead to verify, not a substitute for checking the
files used in this run. Mark claims without adequate provenance unverified.

Keep the original verdict and failed cases. Label later analysis **post-hoc**,
link it to the frozen claim and state what it changes about the explanation.
Do not alter the original score or relax criteria to turn it into a pass.
An explicit section in the existing record is enough; a new file is optional.
When results guide a repair, those cases become development evidence. A later
confirmatory claim needs a fresh evaluation with rules fixed beforehand.

State what was validated, what failed and what was not tested. Keep unresolved
cases visible even when the aggregate looks good. Follow through on the decision:
integrate the checked improvement, keep the incumbent or narrow the claim.
A refuted prediction may still expose a useful distinction or failure mechanism;
retain that evidence alongside the failed prediction without changing its verdict.
