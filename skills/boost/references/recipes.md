# Recipes to adapt, not a required sequence

Read the recipe matching the current uncertainty. Give helpers the actual
contract and relevant raw evidence; fill in the bracketed context. These
prompts work with the same model as the main worker. Combine or invent better
approaches when useful. Keep artifact size proportional to the decision.

**Evidence labels:** observed means a specific check or intervention produced
an observable result; prospective means the approach still needs a real trial.
Neither label establishes general model uplift. A favorable agent opinion is
feedback, not a controlled comparison.

## 1. Algorithm: independent derivation + counterexamples

**Use when:** correctness or complexity is uncertain, or repeated patches fix
examples without explaining the invariant.

**Helper prompt:**
> Given [contract, bounds, examples], independently derive an algorithm and
> its invariant. Do not assume the current approach is right. Return the key
> argument, complexity, and a small exhaustive oracle or discriminating cases.
> Separate a proof from checks that merely support it.

**Useful artifacts:** short derivation, executable small-case oracle, minimized
counterexample, implementation and replay command.

**Check whether it helped:** replay the counterexample before and after; compare
fresh cases against the oracle and exercise scale separately. Preserve the
original contract. If the only difference is more attempts, record that.

**Evidence:** exact synthetic flow and lease solvers were checked against
independent enumeration. Both solo models passed the screened cases; no team
advantage was established. Derivation helpers remain prospective.

## 2. Engineering design: alternatives + discriminating prototype

**Use when:** several architectures look plausible and the choice depends on
failure behavior, latency, resource use or operational complexity.

**Helper prompt:**
> Given [outcome, constraints, load and failure assumptions], propose the
> simplest adequate design and a materially different alternative. Name the
> assumption most likely to reverse your recommendation. Specify a cheap
> prototype or experiment that could distinguish them, including a rejection
> condition. Do not turn unknown requirements into invented requirements.

**Useful artifacts:** compact decision table, runnable prototype, measured
result and a short decision with remaining uncertainty.

**Check whether it helped:** show which observation changed the design or
eliminated unnecessary machinery. Passing a prototype does not prove production
readiness. If neither option differs on what matters, choose the simpler one.

**Evidence:** prospective; no measured design-quality gain yet.

## 3. Integration: follow the earliest broken contract

**Use when:** components pass their own tests but the combined workflow fails,
or retries and configuration changes are hiding the original cause.

**Helper prompt:**
> Trace [input/event] through [components] using [code, logs, failing command].
> Identify the earliest observable mismatch with the contract, including state,
> units, identity, ordering and error translation where relevant. Return a
> minimal reproducer and a test that distinguishes your explanation from the
> nearest alternative. Mark missing evidence instead of filling it in.

**Useful artifacts:** concise event trace, component-boundary test, reproducer,
verified patch. Use real boundaries when mocks would conceal the failure.

**Check whether it helped:** the same end-to-end failure is reproduced and
resolved; the test fails without the fix. A mocked happy path is insufficient.

**Evidence:** prospective as a helper strategy. One source review did identify
an error-reporting defect in the feedback recorder; a driver reproduced and
fixed it. That supports the concrete finding, not skill-level uplift.

## 4. Concurrency and reliability: challenge the invariant

**Use when:** the design depends on leases, retries, deduplication, restoration,
atomic claims or operations that span more than one state change.

**Helper prompt:**
> Given [state machine, consistency contract and implementation], try to
> violate [invariant]. Include overlapping operations and interruption between
> relevant steps; consider identity reuse or delayed replies if applicable.
> Return the smallest legal failing history and an executable replay or model.
> Distinguish safety, liveness, bounded-model evidence and unproved assumptions.

**Useful artifacts:** short state model, minimized schedule, fault-injection
replay, regression test. The artifact may be a tiny local program.

**Check whether it helped:** demonstrate the original invariant violation,
then test the repaired transition under the same schedule and fresh schedules.
Do not describe finite tests as a general proof or infer exactly-once effects
from a successful retry alone.

**Evidence:** a synthetic lease-history checker matched independent permutation
enumeration; solo models solved the sample task. Production integration and
an LLM reliability-helper advantage remain untested.

## 5. Boundary and environment critic

**Use when:** normal examples pass but the contract permits large inputs,
degeneracies, different runtimes, resource limits or unusually large outputs.

**Helper prompt:**
> Given [contract, implementation and existing tests], find assumptions the
> tests leave unchallenged. Pick relevant boundary cases, including output
> representation and runtime behavior. Return executable cases, expected
> behavior and why each could distinguish a real defect. Check the reference
> implementation too; avoid invalid inputs outside the contract.

**Useful artifacts:** small adversarial corpus, failing trace, minimized case,
root-cause control, replay command. Keep fresh evaluation cases separate from
examples used to repair the implementation.

**Check whether it helped:** a valid boundary input fails before repair and
passes after it. Isolate the mechanism with a minimal control; do not credit
that manually supplied fix as an unassisted model success.

**Evidence:** observed in synthetic exact geometry. A valid 60-vertex input
produced a 12,147-character rational answer. Two returned programs failed on
Python's integer-string limit; a serialization-only control fixed both. An
earlier candidate already handled it. This demonstrates the value of that
boundary check, not a stable stronger-model gap or a tested LLM critic policy.

## 6. Stalled execution: fresh diagnosis + useful work coordination

**Use when:** a session repeats the same attempt, loses track of dependencies,
or parks on uncertainty while authorized work could continue.

**Helper prompt:**
> Here are [goal, current state, attempts, raw evidence and actual constraints].
> Give a fresh diagnosis without assuming the previous explanation is right.
> Identify the next action that reduces uncertainty or delivers value. If
> several work items need coordination, propose only the roles or tracking
> needed to keep them moving. Name actual missing authority separately from
> things the worker can investigate now. Return a concrete next action.

**Useful artifacts:** executable next step, short hypothesis ledger or work
map when needed, updated handoff with the true blocker and completed work.

**Check whether it helped:** record the substantive work unblocked and the
remaining blocker. More messages, plans or roles alone are not progress.
Remove coordination that consumes effort without changing delivery.

**Evidence:** one focused Haiku continuation of a stalled local 7B geometry run produced a subsequently accepted candidate in 35 seconds. This changed models, so it demonstrates a useful escalation, not same-model uplift. The run reached its call allowance without declaring completion; external checks established correctness.

## Comparing cheaper models with assistance

Use Sonnet, Haiku, or another available cheaper model without depending on a
stronger model's answer. Begin with tasks the model can meaningfully attempt;
diagnose transport, output-format and runtime failures separately.

Compare solo, boost with same-model helpers, and solo with a comparable total
budget. Let boost choose or invent its strategy. Count intake, helpers, retries,
verification and consolidation in its cost and time. Freeze acceptance criteria
and fresh final cases before calls; do not repair against those final answers.
Existing stronger-model results are reference observations, not a matched
control unless task, budget and environment match.

Record correctness, wall time, available token/cost evidence, strategy changes,
and the agent's opinion. Prefer cost per correctly completed task; unknown cost
stays unknown. Several cheap calls may cost more than one stronger call.

**Evidence:** a synthetic exact-geometry pilot found no critic rescue. Sonnet
and Haiku calls hit deadlines; local Llama 3.2 1B returned invalid/empty code and
an unhelpful critic. Removing stray closing XML tags from one Sonnet solo
candidate made it pass 18/18 cases (post-hoc formatting diagnostic, not a boost
win). A source-only schema and an explicitly supplied algorithm guide also
failed for local 1B/7B models. These are small observations, not capability
ceilings. A later iterative repair experiment let workers inspect, edit, test and retry: Haiku produced an accepted geometry candidate in 40 seconds; local 7B still failed. A prose lesson did not rescue it. Reusing verified source fixed its geometry, but it stalled on a CLI requirement. Keep execution
failures separate from mathematical errors; never ask a critic to invent a
diagnosis of code that was not produced.

## 7. A repair loop with checks and reusable work

**Use when:** repeated edits are not converging, or tests pass while the actual
contract is still unmet.

**Working pattern:** retain the current files and failing command; run relevant
tests after edits. For a missing requirement, supply a caller-owned development
check whose output goes back to the worker. Keep final evaluation separate. If
progress stalls, hand a fresh worker the current patch and raw failures. Preserve
original regression tests and include all prior spend when assessing the rescue.

**Helper prompt:**
> Keep correct work intact. Reproduce this observed failure against this contract.
> Make the smallest justified repair, then run regression and development checks.
> Green tests do not excuse an unmet requirement. Return the patch and evidence.

**Useful artifacts:** source snapshots, executable check, per-call receipts, and
a short continuation packet. Export accepted code as an inspectable dependency
when useful; bind its evidence to the exact task and source. Distill lessons
without final answers, then test them on new work before promoting them.

**Evidence:** Haiku initially passed visible tests but missed required compact
JSON output. An external development check exposed the defect; the same model
produced a fully accepted patch in 23 seconds (45 seconds to self-completion,
$0.119 reported CLI cost). This is a concrete verifier-guided repair. A fresh full-task CLI run also passed in 122 seconds for $0.210. These runs do
not establish an advantage from extra agents or broad self-learning.

Runnable Python/Docker implementation, negative trials and receipts:
[Boost workloop](https://github.com/itsHabib/specialist-workshop/tree/codex/boost-workloop/experiments/boost_workloop).
