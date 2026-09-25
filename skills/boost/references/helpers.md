# Helper missions and handback

Use native delegation when available. The lead selects a question that could
change its next action and prepares the packet from the current task. Start with
one helper; add another only for a separate useful question that can progress
independently. Use existing resource limits; a helper does not expand authority.

## The packet

Keep it short and link existing artifacts:

- **Outcome and question:** acceptance criteria, one unresolved decision, and
  the observation that could change it.
- **Inputs:** source revision or snapshot, relevant files, raw results and a
  reproduction command. Preserve relevant failed experiments and constraints.
- **Scope:** allowed edits, separate ownership for concurrent writers, shared
  resources to avoid and the actual resource limits.
- **Return:** artifact location and how to hand findings back to the lead.

For fresh diagnosis, use a genuinely fresh context and omit the lead's favored
explanation. Do not hide necessary facts. For review of a specific proposal,
include that proposal and call it review. A neutral prompt inside an inherited
conversation is not a fresh investigation.

## Ready-to-use side-agent mission

The lead fills in the question and supplies the packet. Use the same mission in
a native subagent or a separate session:

> You are the Boost partner for this task. Answer **[one concrete unresolved question]** using the supplied packet. Read the Boost skill supplied by the lead. Inspect the relevant inputs and execute the smallest experiment, derivation or counterexample that could change the decision. Return a runnable probe, checked patch or concrete finding with evidence and limits. Preserve the best checked baseline and include an unfavorable case when proposing an improvement. Work only within the assigned edit scope; propose a diff if none is given. Do not launch more helpers by default. If evidence is missing, identify what would settle the question and complete the useful work available. Hand back your conclusion, artifact, command and observed result, assumptions and recommended next action. Distinguish measurements from inference. A useful negative result is a valid result.

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
