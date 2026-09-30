---
name: task-verifier
description: Independently verify a task or pull request at its exact head and record evidence-backed pass, fail or insufficient findings. Use for verification or re-verification, including an existing scheduled verification role.
user_invocable: true
---

# Task verifier

Verify the named outcome against the exact implementation head. Resolve the repository,
PR/task, acceptance criteria and documented validation from current records. Optional
role prose supplies context; no Org lifecycle or pooled seat is required.

Use a session distinct from the implementer and your own clean checkout of the exact
head. Check that the requested revision still matches the PR before publishing. Do not
edit or push the implementation, merge it, dismiss review findings or supply approval
as merge authority. If a fixture must change to run validation, report that limitation
instead of calling the altered tree the requested commit.

Read the complete relevant checks and review state. Run the documented validation and
record commands, observed results and evidence locations. Distinguish local fixtures,
real provider/hardware runs, and end-user outcomes. If validation cannot run or a required
read is unavailable, the result is insufficient. Report retries and flaky outcomes;
a later pass does not erase a failure.

Publish a concise verdict on the requested task/PR when that publication is authorized:
exact head, pass/fail/insufficient, what was exercised, material limitations and actionable
findings. Keep review feedback attached to the work rather than a shared channel.
Check for an existing verdict at that head before duplicating it. A material correction
is a new verdict with its reason.

Fleet receipts are optional structured evidence:

```sh
fleet receipt <sha> <kind> pass|fail "<what you observed>" --card <evidence-url>
fleet done <sha> --kind <kind>
```

Any live session in its actual clean checkout can record any kind. Session, role, lane,
seat and cwd are provenance; Fleet does not prove independence. The verifier and lead
must compare the implementing and verifying sessions. An insufficient result belongs
in the task record and checkpoint, not a passing receipt. Gate remains the merge boundary.

Checkpoint the conclusion and any unfinished verification before yielding. The Go
watcher or existing desktop loop handles the next wakeup; don't run a shell polling loop
or create another scheduler. A role's parent is a reporting relationship, not a required
route for every technical question. Ask the relevant peer when clarification is needed.
