# Helper missions and handback

Use native delegation when available. The lead selects a question that could
change its next action and prepares the packet from the current task. Default to
one helper; add another only for a separate useful question that can progress
independently. Use existing resource limits; a helper does not expand authority.

## Temporary subteam

When complementary investigations would help, form a temporary subteam around
one result. The lead owns the deliverable and integration. Assign distinct
questions based on the missing evidence, with one shared acceptance check and
a clear place where each contribution will be used. Choose the smallest useful
team; no fixed roster is required.

For example, one helper can investigate a bottleneck while another prepares
independent counterexamples. Share the relevant input contract and revision,
and keep their edit ownership separate. Parallelize work that is ready; a check
that depends on a new artifact must wait for that artifact. The lead continues
useful work, verifies the returned contributions, resolves disagreements with
evidence, and checks the combined result against the actual caller. Follow the
handback steps below. End or shrink the subteam when its questions are settled
or further delegation stops helping.

## The packet

Keep it short and link existing artifacts:

- **Outcome and question:** acceptance criteria, one unresolved decision, and
  the observation that could change it. For a confirmatory check, include expected
  changes and relevant behavior that must remain unchanged.
- **Inputs:** source revision or snapshot, relevant files, raw results and a
  reproduction command through the actual caller with effective configuration.
  Preserve relevant failed experiments and constraints. For evaluation, use the
  relevant [evidence checks](evaluation.md), including how the checker was
  validated. Keep withheld answers out of candidate-building packets.
- **Scope:** allowed edits, separate ownership for concurrent writers, shared
  resources to avoid and a concrete time or effort limit within the task's budget.
  Verification preserves the tested subject; implementation may edit an assigned
  candidate. Neither changes frozen inputs or scoring rules silently.
- **Return:** artifact location and handback route. Return useful partial evidence
  and remaining uncertainty at the limit, without waiting for the lead to ask.

Save useful findings as they are discovered to the agreed artifact or lead
handback channel, especially near the limit and before long operations. A prompt
cannot force a handback after a hard kill; the lead should inspect retained
artifacts, reclaim timed-out work and decide what remains useful instead of
silently repeating it.

For a long or interruption-prone mission, choose a concrete checkpoint cadence
suited to the work, such as after each small batch of sources. Budget reading
missions for saved findings, not an open-ended survey. Use native completion
notifications; add a fallback only when notification risk warrants it and an
existing authorized mechanism supports it. This skill does not authorize new
schedules or background monitoring.

For fresh diagnosis, use a genuinely fresh context and omit the lead's favored
explanation. Do not hide necessary facts. For review of a specific proposal,
include that proposal and call it review. A neutral prompt inside an inherited
conversation is not a fresh investigation.

An existing peer can register criteria before a shared experiment. Supply the
proposed change, predicted changed and unchanged behavior, measures and scored
units, and expected output locations. Let it challenge the criteria before the
run; preserve its independent scoring afterward. Exposure to the proposal makes
this proposal review, not fresh diagnosis. Contact existing sessions only within
authorized coordination; a peer cannot supply missing operator permission.

## Ready-to-use side-agent mission

The lead fills in the question and supplies the packet. Use the same mission in
a native subagent or a separate session:

> You are the Boost partner for this task. Answer **[one concrete unresolved question]** using the supplied packet within **[time or effort limit]**. Read the supplied Boost skill and relevant reference. Run the smallest experiment, derivation or counterexample that could change the decision. Check actual inputs, execution path and the evaluator's validation before trusting a measurement. Use known-answer controls that could reveal a shared defect; account for established uncertainty even when displayed values match. If uncertainty permits both passing and failing outcomes, refine the check or report inconclusive. Before confirmation, record expected changes, what must stay unchanged and how outcomes affect the decision. Preserve the best checked baseline and include an unfavorable case when proposing an improvement.
>
> Work within your edit scope; propose a diff if none is given. Preserve frozen inputs and criteria; do not use withheld answers to build candidates. Do not launch helpers by default. Save findings as discovered, following **[checkpoint cadence if needed]**, especially before long operations. Return useful partial work at the limit without another request. Hand back a runnable probe, checked patch or concrete finding: conclusion, artifact, command and observed result, evaluator controls, material invalidated attempts, assumptions and next action. Distinguish measurements from inference and name missing evidence. Include failed work and verification in effort; mark unknowns. A useful negative result is valid.

The lead may tailor the mission with a [recipe](recipes.md). Give the helper the
skill's actual path or contents; do not assume the lead's loaded skills transfer.
If the helper cannot load it, the mission is sufficient to begin: report the
missing resource and continue useful work.

## Close the loop

The lead checks the returned evidence against the caller's contract, runs the
relevant reproduction or inspects the derivation, and integrates useful work.
For substantive findings record a short disposition:

> **Accepted / rejected / deferred:** finding. **Evidence:** command/result or derivation. **Effect:** what changed, stayed the same or still needs checking.

Keep the helper for a focused follow-up if its result exposes another question
in the same investigation. Stop the side investigation when the question is
settled or ordinary implementation is the next useful step. Continue the user's
main deliverable; the handback is not a substitute for finishing it.
