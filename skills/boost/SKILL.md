---
name: boost
description: Improve execution of a difficult engineering, algorithm, debugging, or integration task using a brief intake, targeted assistance and evidence, then record what helped. Use when asked to boost a session, unblock an agent, add a thinking partner, or use /boost on ongoing work.
argument-hint: "[task or current difficulty]"
user_invocable: true
---

# Boost

Help the current agent deliver the requested outcome. Use this on real work;
there is no need to prove a model is weak first. No stronger model, special
platform, permanent team, or cloud runtime is required.

## Intake, then work

Infer the outcome, available evidence, uncertainty and practical budget from
context. Keep the intake to a few lines; ask only about missing information
that changes the next action. Start doing useful work immediately.

Choose assistance for the actual uncertainty. These are examples, not stages:

| Need | Useful intervention |
|---|---|
| Unclear problem or design tradeoff | Clarify constraints; compare concrete alternatives and a cheap prototype |
| Algorithm or invariant might be wrong | Independent derivation, small exhaustive oracle, counterexample search |
| Integration failure | Trace the contract across components; reproduce the earliest mismatch |
| Apparently correct code | Challenge boundary sizes, failure recovery, environment assumptions and output handling |
| Repeated unproductive attempts | Fresh diagnosis from raw evidence, without the existing explanation |
| Agent keeps parking itself | Separate missing authority from uncertainty; use existing authorization and available tools |

A tool, test, tighter representation or direct repair may be enough. When a
helper would add value and delegation is available, use an available model
(the same model is fine). Give it the goal, relevant raw evidence, constraints,
a bounded question and the requested artifact. Let an independent investigator
form a view before showing it your preferred diagnosis. Avoid duplicate edits.
If helpers are unavailable, perform the useful check locally and continue;
do not call self-review independent verification.

Integrate by testing the proposed change against the task's acceptance evidence.
Agreement or an agent saying "looks good" is not verification. Adapt the help as
the evidence changes; drop unhelpful roles. Continue the authorized task through
its requested outcome or an actual blocker, within the existing budget. This
skill adds no approval gate or required review round.

## Adapt the structure

Treat this skill as a starting point. Invent or combine useful structure for
this task: a work coordinator, specialist roles, a hypothesis ledger, a design
comparison, staged experiments, a verification loop, or something better.
The table above is not an exhaustive menu or a fixed team topology. Use your
judgment about when to add, change or remove structure; keep its overhead
proportional to the progress it produces.

Record what you added and why in the use note, including what you would change
in this skill. Reuse successful patterns when their context fits. A good local
experiment is a candidate improvement, not automatically a universal rule.

## Leave a small use note

At a meaningful checkpoint or completion, record a short, candid account:
what task you attempted, which model actually ran, the chosen intervention,
what changed, evidence, and your opinion of the skill. Include help that added
nothing, harmed progress, or was unavailable. Report unknown time/cost as unknown.
Successful work alone does not prove the skill caused improvement. Opinions
are feedback, not measured uplift.

Use the bundled recorder, resolving its path relative to this SKILL.md:

```sh
python3 <skill-directory>/scripts/record.py <<'JSON'
{"task":"brief non-sensitive description","model":"actual model or unknown","strategy":"solo / specific helper or check","outcome":"unclear","evidence":"observed result or artifact reference","opinion":"what to keep, change or remove","elapsed_seconds":null,"estimated_cost_usd":null}
JSON
```

Choose `outcome` deliberately: `helped`, `no_change`, `hurt`, or `unclear`.
Leave optional time/cost fields null when unknown. The recorder saves one
private local JSON file under `~/.local/state/agent-boost/uses/` and prints its
path. `--directory PATH` chooses another local destination. Keep notes concise;
exclude secrets, raw work material and sensitive identifiers. Nothing uploads
or enters a repository automatically. If recording is unavailable, leave the
same short note in the task handoff; do not delay the actual delivery.
