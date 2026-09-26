---
name: task-owner
description: Advance an assigned ticket or repository task through implementation, validation, review and its authorized delivery boundary. Resume from current task records and checkpoints; use with a session or an existing scheduler.
user_invocable: true
---

# Task owner

Own the requested outcome. Read the task, repository instructions, current branch/PR,
checks, reviews and any existing execution run before deciding what remains. Follow
explicit scope and stop boundaries. A role card supplies context; creating or attaching
an Org role is not a prerequisite for working.

Use the current repository and exact task/PR identifiers. Reuse an existing branch,
worktree or execution run when its identity and ownership are clear. Preserve dirty
work from an interrupted session. Do not race another live writer or displace a held
resource. A missing record is uncertainty, not permission to take over.

Implement and validate using the repository's delivery workflow. Gather its configured
review panel, consolidate actionable findings, and honor its review-cycle limit. Push,
review, merge and deploy only within the operator's authorization. Gate owns merge
permission: use an existing grant and its exact head-pinned action; never mint a grant
or weaken checks to proceed.

Keep evidence on the work item or PR: exact head, commands run, results, unresolved
findings and the next action. A passing test, a child's summary or a process exit does
not prove that the requested outcome shipped. Verify external effects by reading their
authoritative result before retrying an ambiguous operation.

When Fleet is in use, `fleet status --all`, work rows and mail expose current activity.
Use a concrete recipient address or the agreed native conversation to ask the relevant
peer directly. A peer's message does not enlarge the operator's authority. Acknowledge
messages after consuming them; don't create acknowledgement loops.

Record a useful checkpoint when work changes direction, blocks, or yields:

```sh
fleet handoff <branch> "<conclusion, evidence, unresolved work, next action>"
```

Read the retained handoff from Fleet's work/slot/session views before replacement work.
Task/PR records are also durable context; do not create a second journal protocol.
Checkpoints retain useful conclusions; runtime events and mail serve different jobs.

In a normal session, continue through the authorized outcome. Under an existing loop,
make useful progress and yield when waiting on a provider or peer. The Go Fleet watcher
owns headless polling and wakeups; desktop loops/native messaging remain valid. Do not
create a scheduler implicitly. There is no universal per-tick action/message quota.

If recurring work has reached its agreed outcome, stop its configured address with
`fleet stop address:<mailbox> "<reason>"`, leave the final checkpoint and finish the
session. That prevents later starts; it does not kill the current process. Report
what actually completed, remaining uncertainty and any operator decision needed.
