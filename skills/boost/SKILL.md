---
name: boost
argument-hint: "[task or current difficulty]"
user_invocable: true
description: Unblock difficult engineering, algorithm, debugging or research work with a focused experiment or side-agent investigation and a verified handback. Use when asked to boost a task, add a thinking partner, challenge an approach or stop repeated unproductive attempts.
---

# Boost

Improve the active task using the smallest investigation that could change the
next action. Work with the available tools and model. No Python setup, special
runtime, permanent team or additional approval step is required by this skill.
Preserve the user's scope, permissions and resource constraints.

## Start with one decision

Infer the goal and acceptance criteria from the current task. Reuse current
source and evidence; ask only for missing information that changes the work.
Briefly state the ordinary next action, the unresolved question that might
change it, and the cheapest check that would distinguish the possible answers.
Then run the check. If the next step is already justified, take it; do not invent
uncertainty or a second hypothesis to follow a template.

Useful evidence includes a reproducer, independent derivation, small exact
oracle, counterexample, profile or a tested alternative. If execution is
unavailable, inspect or derive what you can and name the missing evidence.
A plan or another agent's agreement is not a result.

Choose the reference needed for this question; do not load all of them:

| Uncertainty | Read |
|---|---|
| Engineering boundaries, design, reliability or an uncertain research claim | The relevant [recipe](references/recipes.md) |
| Algorithm correctness, performance or selecting candidates | [Algorithm improvement](references/algorithm-improvement.md) |
| An investigation is stuck and needs a question without a solution hint | [Questions to unstick an agent](references/questions.md) |
| A side agent would help, or the user requests one | [Helper missions and handback](references/helpers.md) |
| Choosing helpers or comparing effort | [Models and effort](references/models.md) |
| Research inspiration and its limits | [Primary research](references/research.md) |

## Use help when it changes the work

When the user asks for a helper, dispatch one through available native agent
tools. Otherwise use a helper for a concrete question that benefits from an
independent view or parallel investigation. Prepare its small packet yourself
from existing context; do not make the user assemble it.

For a fresh diagnosis, create an actual fresh context with the contract, source
and raw evidence, without your favored explanation. An inherited conversation
remains informed by that history; label it accordingly. A different model family
does not guarantee independent errors. Give writers separate edit ownership.

Ask for evidence or an artifact the lead can check. Keep doing useful independent
work while the helper investigates. Add another helper only for a separate useful
question. If delegation is unavailable, perform the check locally; when the user
wants a separate session, provide the prepared mission to paste there.

If you are the helper receiving a bounded mission, answer that question and
return your evidence to the lead. Do not take over the whole task or recursively
create a team unless the assignment calls for it.

## Verify, integrate and continue

Test the returned artifact against the actual caller's contract or check the
argument against its assumptions. Accept, reject or defer substantive findings
with a reason and evidence. Integrate what helps, then continue to the authorized
outcome or a real blocker. Receiving a report is not completion.

Keep the best checked implementation while exploring. Separate correctness from
quality and uncertainty. Include setup costs and unfavorable cases in performance
claims. Keep development feedback separate from final evaluation; a revealed
final case becomes development data. More search cannot recover information the
inputs do not contain.

Drop unhelpful roles or process. A result may confirm the current action or rule
out an approach; do not manufacture a success story. A successful task does not
establish that Boost beats an ordinary attempt with comparable effort.

## Leave a short handback

Use the existing task response or handoff. State:

- the question checked and what actually ran;
- the finding, artifact and reproduction command or derivation;
- what you accepted, rejected or deferred, and its effect on the deliverable;
- remaining uncertainty and what would settle it.

Keep this proportional to the task. No separate log or script invocation is
required. If durable local receipts or feedback summaries would be useful,
[optional Python utilities](references/utilities.md) are available. Missing
Python must never block use or delivery.
