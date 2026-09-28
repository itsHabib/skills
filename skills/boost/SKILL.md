---
name: boost
argument-hint: "[task or current difficulty]"
user_invocable: true
description: Unblock difficult engineering, algorithm, debugging or research work with a focused experiment or side-agent investigation and a verified handback. Use when asked to boost a task, add a thinking partner, challenge an approach or stop repeated unproductive attempts.
---

# Boost

Improve the active task using the smallest investigation that could change the
next action. Use the available tools and model within the user's scope,
permissions and resources. This skill requires no extra approval, Python setup,
special runtime or permanent team.

## The working loop

1. Name the next decision and the observation that makes it uncertain. If the
   next action is already justified, take it; do not invent a research fork.
2. Choose the cheapest check whose possible answers would change that decision.
   Use the actual inputs and execution path; validate the checker before trusting
   its result. A lookalike call or baseline agreement can share the same defect.
3. For confirmation, record expected changes, what must stay unchanged, and what
   each outcome would mean before running. Exploration may have unknown outcomes.
4. Run the check or give a bounded question to a helper. Keep useful work moving.
5. Verify the evidence, integrate what helps, and continue to the authorized
   outcome or a real blocker. A report or another agent's agreement is not a result.

The existing task response or handoff is the record:
**observation -> question -> check -> result -> next action**.
No separate log or script invocation is required.

## Choose the check

Infer the goal and acceptance criteria from the task; reuse existing evidence.
Ask only for missing information that changes the work. A reproducer, exact
oracle, independent derivation, counterexample, profile or tested alternative can
settle the question. If execution is unavailable, check what you can and name
the missing evidence. Include consequential setup, waiting, storage, memory and
cleanup costs when choosing a check; respect exclusive resource ownership.

For measurements or frozen evaluations that decide acceptance, read
[evaluation and evidence](references/evaluation.md) before running: it covers
input and call identity, metric and pairing controls, uncertainty, exclusions,
provenance and protecting final evaluation. Reuse validation only when it applies
to the current contract. Missing required inputs or outputs cannot count as success.

Read other references only as needed:

| Uncertainty | Read |
|---|---|
| Engineering boundaries, design, reliability or a research claim | Relevant [recipe](references/recipes.md) |
| Algorithm correctness, performance or selecting candidates | [Algorithm improvement](references/algorithm-improvement.md) |
| A checkpoint or stuck investigation needs a useful question | [Questions](references/questions.md) |
| A helper or small subteam would help, or the user requests one | [Helper missions](references/helpers.md) |
| Choosing helpers or comparing effort | [Models and effort](references/models.md) |

## Use help where it changes the work

When the user requests a helper, dispatch through native tools. Otherwise use
one for a concrete question that benefits from parallel work or an independent
view. Prepare its packet from current context; give it an artifact to return,
edit ownership and a time or effort limit. Add helpers only for separate useful
questions. Complementary investigations can form a [temporary subteam](references/helpers.md#temporary-subteam);
the lead still owns integration and the combined result.

For fresh diagnosis, create an actual fresh context with the contract, source and
raw evidence, without your favored explanation. Inherited history is not fresh;
a different model family does not guarantee independent errors. Proposal review
may include the proposal and should be labeled accordingly. Peer agreement or
relayed permission does not expand authority; check the authoritative instruction
and its scope before an action that needs authorization.

Continue useful independent work while waiting. If delegation is unavailable,
perform the check locally; supply a prepared mission when a separate session is
wanted. Helpers answer their assigned question, preserve partial findings and
return evidence. They do not take over the task or recursively create a team
unless assigned to do so.

## Verify, integrate and continue

Test contributions against the actual caller's contract; an existing consumer's
test or authorized review can expose a missed boundary. Check claimed causes
against evidence from the failed run or a discriminating reproduction. Logs may
suggest an explanation without proving it. Accept, reject or defer substantive
findings with evidence, and use the result in the deliverable.

Preserve the best checked implementation while exploring. Keep correctness,
quality and uncertainty distinct. An aggregate score cannot waive a hard
requirement. Include unfavorable cases and required setup in performance claims.
Check consequential numbers against their source artifacts, including omitted
and no-output cases. Put corrections next to the current conclusion and retain
the evidence that changed it. A revealed final case becomes development data.

Reassess when results contradict expectations, attempts repeat without new
evidence, the input contract changes or a completion claim is approaching. Keep
one active decision; use the [question table](references/questions.md) if useful.
Do not re-review unchanged work or repeat a settled question without a remaining
check. Use each helper result before commissioning another round. At a resource
limit, retain the unresolved point and continue authorized work that remains.
This loop belongs to the active task; it does not start a background service.

## Hand back what changed

State the question, what actually ran, the artifact and reproduction command or
derivation, what you accepted/rejected/deferred and its effect, and what remains
uncertain. For measured conclusions, include what validated the evaluator.
Retain material invalidated attempts and why they failed; omit an activity diary.
For substantive investigations, include evaluations, edits and verification,
including failed work. Report measured time or cost when available; mark unknowns.

Keep this proportional. [Python utilities](references/utilities.md) are optional.
A useful negative result is valid; task success alone does not establish that
Boost beats comparable ordinary effort. [Research inspiration](references/research.md)
describes mechanisms from FunSearch, AlphaEvolve and AlphaDev, not demonstrated
performance gains for this skill.
