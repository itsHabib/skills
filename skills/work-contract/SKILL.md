---
name: work-contract
description: Create, refresh, validate, or close one compact exact-subject WORK.md for a bounded repository task. Use when the user asks for a work contract, minimal driver, frontier-model handoff, or durable task packet; do not use for multi-task orchestration or a design document.
argument-hint: "<task, spec path, or close>"
user_invocable: true
---

# Work contract

Create the smallest durable state packet another capable model needs to resume
one repository task. Record facts the model cannot safely infer. Leave general
coding guidance in repository instructions and executable policy in checks.

This skill manages `WORK.md`; it does not implement the work unless the user
also asks for implementation. It grants no commit, push, review, merge, release,
or infrastructure authority.

## Resolve the action

- No `WORK.md`, or a completed contract and a new task: create a new contract.
- Matching `ready`, `active`, or `blocked` contract: update the existing facts.
- Different unfinished contract: stop and surface the collision. Never overwrite it.
- Close request: verify evidence first, then mark `done`.
- Validation request: inspect and validate without rewriting unless asked.

Before writing, read the nearest repository instructions, resolve the repository
root and full `HEAD`, inspect `git status --short`, and read the task source plus
the closest relevant code and tests. Preserve unrelated dirty paths explicitly.

## Write the contract

Aim for 40–80 lines; 120 is the hard ceiling. Use exactly this shape:

```markdown
<!-- reaper-work:v1 -->
# Work: Concrete outcome name

Work-ID: lowercase-kebab-case
Status: ready
Subject: git:FULL_40_CHARACTER_SHA
Stop-at: local-green

## Outcome

One observable sentence describing what becomes true.

## Preserve

- Existing behavior, user changes, and authority boundaries that cannot move.

## Change

- `exact/path`: the one responsibility changing there.

## Prove

- Green: `exact command` and its required observation.
- Red: deterministic rejection, mutant, or failure that demonstrates sensitivity.

## Stop

- Stop when a named decision, authority, or scope boundary is reached.

## Evidence

- Pending: verification has not run yet.

## Handoff

- Last: last established fact or completed action.
- Next: exact next action.
```

Use `Subject: recipe:sha256:<digest>` only for an uncommitted generated
repository whose `REAPER.lock.yaml` contains that exact origin digest. Otherwise
use the full Git commit that grounded the contract. A dirty worktree is not part
of that commit: name every pre-existing path that must be preserved, and stop if
it overlaps the requested change without a safe boundary.

Allowed statuses are `ready`, `active`, `blocked`, and `done`. Allowed stop
boundaries are `local-green`, `pr-ready`, `reviewed-change`, and
`operator-decision`. A blocked contract replaces `Next` with `Blocked`; a done
contract has no `Pending` evidence, includes at least one exact `Verified`
record, and names the next archival or replacement action.

Keep `Change` path-exact. Keep both proof polarities. Link to deeper sources
instead of copying their prose. Do not add diaries, implementation narration,
option catalogs, invented requirements, or instructions already enforced by the
repository.

## Validate

Run the bundled validator from the repository root:

```sh
bash <this-skill-directory>/scripts/check-work.sh --root "$repo_root" --json
```

Replace `<this-skill-directory>` with the directory containing this `SKILL.md`.
If the repository has its own `make work` or equivalent, run that too; the
repository-owned check may be stricter. Report the contract path, status,
subject, stop boundary, and validator result.
