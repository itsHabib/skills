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
Label a port, mock or reimplementation as a proxy in each reported result and
name the gap to the deployed path; its pass is not a pass by the product.
For variant runs, read the changed input or setting back from each run's actual
target and retain evidence that the intended write reached that target. A run
label does not establish that anything changed.
Use permitted baseline or development runs to distinguish a prediction of the
intended system from a prediction of defects in its implementation or judge.
Keep judged-case outcomes out of that preparation for a blind prediction.

## Validate the measurement

Name the quantity, units, scoring function and correspondence rule. A point sum
is not automatically an area or volume; nearest neighbors are not necessarily
the same entities. Use stable identity when the contract requires correspondence;
geometric matching can be correct when that is the intended measure. Exercise
reordering or nearby distinct entities when they could expose a pairing error.
Revalidate correspondence for each new input set, including a change of producer,
version or source. An unexpectedly empty or near-empty join, or all-zero scores,
requires checking keys and expected overlap before interpreting performance.
Zero can be a legitimate result; establish that it is not a failed join first.

Check an unchanged baseline and a known nonzero perturbation or deliberate defect
with established expected results. Self-comparison alone can pass a broken
checker. Test ranking as well as feasibility when choosing among candidates.
Identify shared parsing, transformations, data or assumptions that could conceal
the failure on both sides; use an independent check that bypasses the relevant
dependency. Preserve the controls and their observed results in the handback.

State what the reference cannot observe before freezing predictions: later
processing steps, unsampled entities and classes it cannot distinguish. Keep
those units separate under the declared coverage policy. Unknown reference
coverage makes the affected comparison unknown, not evidence of a prediction
failure. Discovering a gap later does not authorize changing a sealed verdict.

For sample-based statistics, inspect where samples fall, including the boundaries
or extremes the claim concerns, and report the per-unit evidence-count
distribution and observed minimum, including zero-support units. Set any minimum
usable evidence from the task before confirmation;
below it, mark the unit unmeasured rather than agreeing. Do not choose the floor
after seeing which cases it removes.

Give each consequential output stage its own check. Selection accuracy does not
validate grouping, ordering or execution. Compare relevant counts, group sizes
and distributions with the reference at each stage; identify unmeasured stages.

Repeat unchanged inputs when variability could affect the decision. Record the
observed variation; two matching runs neither prove determinism nor establish
an error bound. Repetition does not expose a shared systematic error.

Record established resolution and uncertainty for numerical comparisons,
including apparent matches. Nominal resolution alone is not a bound on error.
Compare each decision margin or threshold with the precision and established
error of the input it uses. When admissible input error can change the verdict,
refine the input or report inconclusive; do not call it a coin flip or loosen a
requirement merely because the data are coarse.
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
outcomes where meaningful. Freeze the baseline's design as well as the candidate
and acceptance rule. Beside accuracy thresholds, report the relevant uninformed
baseline per stratum, such as the majority-class share, or a justified chance
level. A majority-class predictor is not automatically a random-chance model.
Exploration can discover new explanations; label it
as such instead of pretending its predictions were fixed in advance.

If an independent prediction is part of the test, dispatch it once the case's
inputs and scoring rule are frozen. Retain the prediction before the judged case
starts, with evidence of that ordering; a content hash alone proves neither
timing nor independence. Take descriptive timestamps from the system clock when
writing, rather than estimating them. File times and local commit dates can
corroborate an order but cannot establish independent pre-registration alone.
An existing harness transcript or independently retained
message/receipt that records the prediction and places it before execution is
enough; no separate recorder or hash manifest is required. Self-reported times
or local commit dates alone do not establish the order.
Keep the lead's answer and judged outputs out of the helper's packet.
A prediction made after that case has started is a late
prediction, not its pre-registration; if informed by its result, label it post-hoc.
For a run already underway, coordinate a hold before the next case only within
existing authority and resource ownership. Otherwise target a later unstarted
case without interrupting the current run or claiming retroactive registration.

Declare the scored unit, exclusion rule, aggregation and required coverage.
Apply exclusions at that declared unit, not whichever level produces a favorable
answer; check mixed groups where aggregation could hide the distinction. Report
total, excluded, failed, empty and scored units with their relevant denominators.
A no-op control may prove alignment without testing the claimed improvement.

When units share a source or experimental condition, report results by the
relevant group as well as pooled, with both unit and group counts. State the
basis for treating groups as independent; group labels alone do not establish
independence. Many correlated units must not stand in for many independent cases.

Derive expected units from the evaluation contract, not the candidate's output.
Report absent candidate answers as **MISSING**, retaining their identities and
the expected denominator. Apply the declared failure or unknown policy; reduced
coverage must not improve a candidate's standing by silently dropping units.
Reject or resolve duplicate and unexpected identities before scoring joins.

When records span producer versions, stratify before fitting a rule and state
which versions it applies to. For a system compared with human-edited records,
classify faithful output, edited output, removed output and human additions per
unit before aggregating; preserve how identities and omissions were resolved.

Compare with the incumbent by identity, especially for the most costly error
class. Retain each newly failing unit and its group even if the pooled score
improves. Investigate those regressions before adoption and apply the frozen
acceptance rule: an explanation cannot waive a hard requirement. If tradeoffs are
allowed, account for their declared costs rather than inventing a universal ban.

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

## Check a repair before the next batch

Trace the changed value to every downstream check that reads it, using code
search and the actual caller. Probe those readers with the repaired input before
a costly batch, and name which could refuse next in the prediction.
For an added or changed condition, exercise both reachable branches: force the
condition true and false separately and confirm that a check detects each wrong
behavior. Pair the motivating failure with an input that worked before; explain
any unreachable branch rather than manufacturing an invalid case.
Also replay a second, unlike case from the same input family. Compare its whole
downstream output with the baseline against the predeclared changed and unchanged
requirements. Trace unexpected shifts in counts, coverage or routing before handoff.

If the evaluator itself changes after revealing a failure, treat that repair as
a candidate. Retain the old rule, old verdict and reason beside the revised rule
and verdict. Add a case beyond the relaxed boundary that the new check must still
reject, as well as a valid control. Until these controls pass, label any rescued
result "passed under revised check; old verdict: fail" with its reason.
Passing those controls validates the repair only within their scope; a later
confirmatory claim still needs the frozen evaluation required below.

## Replay instruction or context changes

When the proposed change is an agent's instructions or supplied context, use
recorded episodes held out from those used to diagnose or design the change.
Choose them before writing the change, or reserve an untouched set. Freeze each
episode's inputs byte for byte and its execution conditions; vary only the
intended instructions or context and identify that difference explicitly.
Define success from an independently recorded resolution after the episode,
not the replaying agent's claim. If the record cannot determine success, mark it
unknown. Keep the later resolution out of the agent's inputs.
First check the judge with scripted known-right and known-wrong responses,
without a model call. Compare the old and changed instructions on the same
episodes and per-episode budget; report the share resolved within budget beside
median cost, failures and unknowns. Name the cost measures, such as tokens,
turns or elapsed time. This is a recipe, not evidence that a
particular instruction change improves outcomes.

## Preserve what the result means

Trace decision-bearing numbers to exact artifacts and fields, commands or
derivations and the input revision. One grouped source can support several
numbers. A peer's message is a lead to verify, not a substitute for checking the
files used in this run. Mark claims without adequate provenance unverified.

Keep the original verdict and failed cases. Label later analysis **post-hoc**,
link it to the frozen claim and state what it changes about the explanation.
Do not alter the original score or relax criteria to turn it into a pass.
An explicit section in the existing record is enough; a new file is optional.
If a proposed cause is withdrawn while the measured effect stands, add a dated
correction beside each affected claim, separating what stands from what does
not. Preserve sealed text. Check whether the frozen rule or its tolerances
depended on that cause before scoring; an explanatory correction cannot quietly
change the rule.

A baseline redesigned after scoring is post-hoc even when stronger. Keep the
sealed comparison as the verdict of record and report the new baseline beside
it, with its changed design and why it was not sealed. Report both actual
verdicts. If the candidate passes the sealed comparison but fails the new one,
say "passes the sealed bar; does not pass the stronger post-hoc baseline"
rather than selecting the favorable verdict. Seal the stronger baseline for a
later confirmatory evaluation.
When results guide a repair, those cases become development evidence. A later
confirmatory claim needs a fresh evaluation with rules fixed beforehand.

A reusable scorer makes repeated selection cheap. Cases used to choose or revise
candidates are development data, even if each candidate is called a frozen
version. Keep a sealed final set and a predeclared evaluation procedure; freezing
another version does not restore the independence of already revealed cases.

Lead with a violated frozen bound and its affected cases, even when the aggregate
improves; then explain the diagnosis without rewriting the bound.
State what was validated, what failed and what was not tested. Keep unresolved
cases visible even when the aggregate looks good. Follow through on the decision:
integrate the checked improvement, keep the incumbent or narrow the claim.
A refuted prediction may still expose a useful distinction or failure mechanism;
retain that evidence alongside the failed prediction without changing its verdict.
