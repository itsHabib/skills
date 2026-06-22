---
name: ship-ticket
description: Chain the post-implementation wrap-up for committed work - file the Jira ticket, open + describe the PR, and sync the epic. Orchestrates /spinup-ticket -> push + PR -> /write-pr -> /sync-epic, threading the new ticket key through each step. Use when the work is committed on a branch and the user says "ship this ticket", "wrap this up", "file the ticket and open the PR", or "/ship-ticket <epic>". NOT for implementation, commits, or merging - the diff is assumed done.
user_invocable: true
---

# /ship-ticket

Take a branch that already has committed work and run the full tracker + GitHub
bookkeeping in one pass: create the ticket under an epic, open and describe the
PR, and bring the epic status in line. This is the orchestrator over
`/spinup-ticket`, `/write-pr`, and `/sync-epic` - it does not re-implement them,
it invokes them in order and threads the new ticket key through.

## Configuration

Inherited from the sub-skills - set once (see `/spinup-ticket`):
`JIRA_BASE_URL`, `JIRA_TOKEN`, `JIRA_PROJECT`, `JIRA_USER`, `JIRA_EPIC_FIELD`.

## Required input

- **Epic key or URL** - e.g. `PROJ-100`. If missing, ask once.
- **Summary** - short imperative title. Derive from commit messages if not
  given, then confirm.

Description body + acceptance criteria are derived from the commits + diff and
refined by the sub-skills.

## Preconditions

Run these first; stop with a clear message if any fails:

```bash
git branch --show-current             # must not be the default branch
git log origin/HEAD..HEAD --oneline   # must show >= 1 commit to ship
git status --short                    # note uncommitted work
```

If on the default branch, or there are no commits ahead, there is nothing to
ship - stop and say so.

## Steps

### 1. File the ticket - invoke `/spinup-ticket`

Invoke `spinup-ticket` with the epic key + summary + a 2-4 sentence description
and acceptance criteria derived from the diff. Capture the new `<PROJECT>-NNN`
key it returns. If ticket creation fails, stop - the rest depends on the key.

### 2. Rename the branch to convention

If the branch name does not already carry the ticket number, rename it to your
convention (e.g. `<project>-NNN_<lower_snake_slug>`):

```bash
git branch -m <old> <project>-NNN_<slug>
```

Skip if it already matches.

### 3. Push the branch

```bash
git push -u origin <project>-NNN_<slug>
```

Only ever push the feature branch, never the default branch. Invoking this
skill is the explicit go-ahead to push this branch.

### 4. Open the PR (ask draft vs ready)

Ask once via `AskUserQuestion` whether to open the PR as **draft** or **ready
for review** (default draft - most work wants a self-review first). Then:

```bash
gh pr create --base main --head <project>-NNN_<slug> \
  --title "<type>(<scope>): <summary> [<PROJECT>-NNN]" \
  [--draft] \
  --body "Closes [<PROJECT>-NNN]($JIRA_BASE_URL/browse/<PROJECT>-NNN)

Placeholder - description refreshed by /write-pr."
```

Capture the PR number + URL.

### 5. Describe the PR - invoke `/write-pr`

Invoke `write-pr`. It detects the PR + ticket from the branch and fills Summary
/ Closes / What this adds / Validation. Populate Validation from checks already
run this session rather than re-asking, when you have them.

### 6. (Optional) Record it in your task tracker

If you track work in something like dossier, create a matching task with the
ticket URL, branch name, PR link, and any key decisions worth surviving the
session. Skip if you don't.

### 7. Sync the epic - invoke `/sync-epic`

Invoke `sync-epic` with the epic key. The new ticket lands as **In Progress**
if the PR is a draft, **In Review** if ready. `sync-epic` presents its audit
table and confirms before applying - let that confirmation flow through to the
user; do not auto-confirm epic-wide status changes.

## Notes

- **Reuse, don't duplicate.** Token mechanics, wiki markup, and transition
  resolution live in the sub-skills. This skill only orchestrates and threads
  the ticket key.
- **One ticket, one PR per run.** Splitting work across tickets is a judgment
  call the user makes before invoking this.
- **Stop on the first hard failure** (ticket create, push, PR create) rather
  than limping forward with a half-filed chain.

## Out of scope

- **Implementation and commits.** The diff is assumed done and committed.
- **Merging the PR or driving review cycles.**
- **Creating the epic.** The epic is named, not created here.
