# Recipes to adapt

Choose the recipe that addresses the current uncertainty. Replace bracketed
context with the actual contract and raw evidence. Each prompt can guide your
own next pass or a helper using an existing approved model. Keep the work
bounded by a concrete output, a check and a stopping condition.

These are proposed working methods, not evidence of improved model capability.
Record what changed on the task and count all attempts when comparing effort.
For algorithm work, also see [algorithm improvement](algorithm-improvement.md).

## 1. Algorithm correctness: derive and try to falsify

**Use when:** patches fix individual examples without establishing why the
algorithm works, or correctness and complexity are uncertain.

**Prompt:**

> Given [contract, input bounds and examples], derive an algorithm and its
> invariant without assuming the current approach is correct. Return the
> argument, complexity, and an executable small-case oracle or discriminating
> cases. Separate a proof from finite checks that support it.

**Deliver and check:** retain the derivation, minimized counterexample and
replay command. Compare the implementation with an independently constructed
oracle on fresh cases; exercise scale separately. Preserve the original
contract, including ties, numeric precision and output requirements.

## 2. Engineering design: test the assumption that decides

**Use when:** several designs look plausible and the choice depends on failure
behavior, latency, resource use or operational complexity.

**Prompt:**

> Given [outcome, constraints, workload and failure assumptions], propose the
> simplest adequate design and one materially different alternative. Name the
> assumption most likely to reverse the choice. Specify a small runnable
> experiment that distinguishes them, with a rejection condition. Identify
> unknown requirements without inventing answers.

**Deliver and check:** build the discriminating prototype, run the stated
workload and record which observation changed the choice. If the options do
not differ on the required outcome, prefer the simpler one. Limit conclusions
to what the prototype exercised.

## 3. Integration: find the earliest broken contract

**Use when:** components pass their own checks but the combined workflow fails,
or retries and configuration changes are obscuring the cause.

**Prompt:**

> Trace [input or event] through [components] using [code, logs and failing
> command]. Find the earliest observable mismatch with the contract. Consider
> state, units, identity, ordering and error translation where relevant. Return
> a minimal reproducer and a check that distinguishes your explanation from
> the nearest alternative. Mark missing evidence.

**Deliver and check:** retain a short event trace and an executable boundary
test. Reproduce and resolve the same end-to-end failure; establish that the
test fails without the fix. Exercise real boundaries when mocks would hide
the suspected behavior.

## 4. Reliability: challenge the invariant

**Use when:** correctness depends on retries, leases, deduplication, restoration
or operations spanning multiple state changes.

**Prompt:**

> Given [state machine, contract and implementation], try to violate
> [invariant]. Include overlapping operations and interruption between relevant
> steps. Consider delayed replies and identity reuse where applicable. Return
> the smallest legal failing history and an executable replay or model.
> Distinguish safety, liveness and assumptions outside the model.

**Deliver and check:** replay the failing schedule before and after repair,
then challenge the repair with fresh schedules. State the bounds of any model
or fault-injection run. Finite tests do not establish a general proof, and a
successful retry does not establish exactly-once effects.

## 5. Performance and boundaries: measure the complete workload

**Use when:** typical cases pass but large inputs, numeric extremes, output
size, runtime behavior or resource limits may change the result.

**Prompt:**

> Given [contract, implementation, baseline and workload], find valid cases
> that challenge untested assumptions. Profile the complete operation before
> proposing changes. Return runnable cases, expected behavior, measurements
> and one change aimed at the observed bottleneck. Check the reference too.

**Deliver and check:** preserve correctness while comparing baseline and
candidate under the same conditions. Include setup, serialization and other
required work in timing; report repeated measurements, variation and
regressions. Keep fresh evaluation cases separate from repair examples. Stop
if the apparent gain disappears within measurement noise.

## 6. Research: test whether the question is identifiable

**Use when:** several explanations fit the observations, a benchmark is a
proxy for the intended outcome, or more analysis may not answer the question.

**Prompt:**

> Given [question, available evidence and proposed conclusion], identify
> plausible competing explanations when the evidence admits them; do not
> invent alternatives. Identify an observation or intervention that would
> distinguish them, or try to falsify the remaining explanation. State required assumptions,
> confounders and a result that would change the conclusion. If the evidence
> cannot identify the answer, specify the smallest additional measurement or
> narrow the claim to what is supported.

**Deliver and check:** produce a compact hypothesis table and a runnable
analysis or bounded experiment with its decision rule fixed in advance.
Check that the proposed measurement actually separates the explanations.
Report unresolved ambiguity; a plausible narrative is not a causal result.

If the same observed inputs admit different required answers, name the input
set and assumptions under which the ambiguity holds. Seek a distinguishing
measurement, narrow the claim or preserve an unknown result. This does not
establish that the answer is unknowable with other inputs.

## 7. Stalled repair: give the worker decisive feedback

**Use when:** edits repeat without convergence, or visible tests pass while
the actual requirement remains unmet.

**Prompt:**

> Here are [goal, current patch, failed attempts and raw check output]. Keep
> correct work intact. Reproduce the failure and question the current diagnosis.
> Make the smallest justified repair, then run regression and development
> checks. Return the patch, evidence and any remaining blocker.

**Deliver and check:** use a caller-owned development check for the missing
requirement and feed its output back to the worker. Keep final evaluation
separate. If the same approach stalls, give a fresh helper the current files
and raw failure rather than restarting everything. Stop on verified completion,
the agreed budget or a concrete blocker; plans and messages alone are not
progress.

## 8. Candidate search and selection: trust the evaluator first

**Use when:** selecting among formulations, heuristics or parameter choices,
especially when search produces only small or inconsistent gains.

Before generating more candidates:

- Validate feasibility separately from the score. Use exact checks where the
  contract requires exactness, and explicit tolerances where it permits them.
- Test the evaluator with known-valid, known-invalid and deliberately defective
  candidates. Confirm that known-better solutions rank above known-worse ones.
- Measure the caller's objective. A faster inner loop matters only to the
  extent that it improves the required workload.
- When scoring predicted outcomes, distinguish simulated behavior from assumed
  success. Compare a selected candidate with an independent execution or known
  answer at the point the outcome is observed. Agreement on cases used to tune
  the predictor is calibration evidence. If the check is unavailable, retain
  the prediction and uncertainty without calling the outcome verified.
- Keep required outputs and acceptance limits independent of the candidate.
  Unknown cases remain unresolved; an aggregate score cannot waive a hard
  requirement or hide a critical failure.
- Check room for improvement with a lower bound or a known better feasible
  solution, when available.
- Freeze the acceptance rules, search budget and final evaluation cases before
  search. Candidate generation must not silently change the evaluator.

**Prompt:**

> Given [contract, feasibility rules, objective, validated evaluator and
> development results], propose one materially different formulation. Return
> a runnable candidate and explain where you expect it to beat or lose to the
> incumbent. Stay within [budget] and mark anything you have not run.

**Deliver and check:** retain the best checked incumbent and a candidate table.
Select using development cases, then run the final evaluation on the frozen
holdout. Report feasibility, the caller's objective, variation and
regressions across the workload. If the holdout guides another repair, it has
become development data and a new final evaluation is needed.

Keep the incumbent when candidates do not meet the acceptance rule. Any claim
that assistance itself helped also needs a comparable ordinary-work budget,
including generation, failed attempts, verification and integration.
