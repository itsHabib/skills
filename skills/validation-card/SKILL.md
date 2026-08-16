---
name: validation-card
description: Run a branch's real validation against live infrastructure and post a reproducible "validation card" as a comment on the tracking issue, then link it from the PR body. Use when the user says "validation card", "validate this branch and post it", "post the validation", "card this PR", "/validation-card", or when a PR needs evidence beyond CI before merge. NOT for writing the PR description itself (that is /write-pr) and NOT a substitute for CI - a card exists to show what CI cannot: live runs against real infra, before/after through the real entry point, and proof a guard fails on the bug it claims to catch.
user_invocable: true
argument-hint: "[tracker-key or PR ref] - omit to derive from the current branch"
---

# /validation-card

Produce a validation card for the current branch: run the branch's own validation against
real infrastructure, write a card where every section is a command someone can re-run, post
it as a **comment on the tracking issue**, and link it from the PR body.

The card's job is to show what CI cannot. CI proves the tests pass. A card proves the code
does the right thing against real data - which is where ported logic, new producer fields,
and anything reverse-engineered from another system actually break.

## The rule that makes a card worth writing

**A card that only lists passing tests is not a card.** Unit tests are the smallest and least
interesting layer, and they are written from the same understanding as the code, so they
encode the author's misreads. Every card must contain at least one of:

- a **live run** against real infrastructure (real upstream service, real staging, real DB), or
- a **before/after** measured through the real changed entry point, or
- a **counter-check**: revert the fix, show the real artifact produces the wrong answer, restore it.

Worked instance from the flow this skill came out of: a validation rule had 15 passing unit
tests and would still have emitted 8 wrongful FATAL verdicts on every real input, blocking
every upload. The tests could not catch it because they were built from the same misreading as
the rule. The live capture caught it in one run.

## Configuration

Two things vary per repo. Resolve both before step 1.

**Tracker.** Where the card lives and what markup it takes:

| Tracker | Set | Markup |
|---|---|---|
| Jira Server / Data Center | `TRACKER=jira-server`, `JIRA_BASE_URL` | WIKI markup, see [references/card-format.md](references/card-format.md) |
| Jira Cloud | `TRACKER=jira-cloud`, `JIRA_BASE_URL` | ADF via `/rest/api/3`, or WIKI via `/rest/api/2` |
| GitHub Issues | `TRACKER=github` | Markdown, post with `gh issue comment` |
| Linear | `TRACKER=linear` | Markdown, post via the GraphQL `commentCreate` |

Markdown is the authoring format in every case; both Jira targets need a conversion pass on
the way out, and which one depends on the endpoint you post to. `jira-server` and Jira Cloud's
`/rest/api/2` both take WIKI markup; Cloud's `/rest/api/3` takes ADF, and posting Markdown to
it is rejected or renders raw. GitHub and Linear take the Markdown unchanged. Do not let the
tracker choice change the card's content - only its markup.

**Credentials.** A token read from a gitignored file at the repo root or from an env var -
whichever the repo already uses. Never inline a token into the card, the command log, or a
committed file. If the repo has no convention, prefer an env var.

## Steps

### 1. Identify the subject

Take both endpoints from the PR itself. Anything derived from the local checkout can only
confirm what the checkout already says: `origin/main` is the wrong ref for a PR onto a release
branch, `origin/$BASE` is missing or stale on a fork or an unfetched remote, and a local `HEAD`
compared against itself proves nothing about the commit under review.

```bash
eval "$(gh pr view <n> --repo <owner/repo> --json headRefOid,baseRefOid \
  --jq '@sh "SUBJECT=\(.headRefOid) BASE=\(.baseRefOid)"')"
git fetch -q origin "$SUBJECT" "$BASE"

git log "$BASE..$SUBJECT" --oneline
git diff --shortstat "$BASE...$SUBJECT"
```

`$SUBJECT` is now the commit the tracker's PR is reviewing, and every later check compares
against it rather than against a local guess.

Derive the tracker key from the branch, commits, or PR body. Confirm the PR number with
`gh pr list --repo <owner/repo> --head <branch>`.

**Prefer the primary checkout** over a secondary worktree, and say so in the card. A secondary
worktree can have stale dependencies, a missing env file, or an ungenerated client, and each of
those produces failures that look like real breakage.

That preference has a trap. If the branch was created by a worktree flow it is already checked
out in the secondary worktree, and git refuses to check the same branch out twice - so
"validate in the primary checkout" silently becomes "validate the default branch" while the
card goes on naming the PR SHA. A card that attests a revision it never exercised is the one
failure this skill exists to prevent.

Pick one deliberately: transfer the branch to the primary checkout, or validate in the
worktree that already holds it after refreshing its dependencies and generated files. Then,
either way, prove where you are before running anything:

```bash
test "$(git rev-parse HEAD)" = "$SUBJECT" || { echo "checkout is not the PR head; stop"; exit 1; }
```

A local branch that is behind the remote, or carries unpushed commits, fails this - which is
the point. Comparing HEAD to a SHA you read out of that same checkout would pass in exactly
the cases worth catching.

Name the checkout you used and the verified `$SUBJECT` in the card.

### 2. Stand the branch's code up against real infrastructure

Not the deployed service - that runs the default branch. The point is to exercise *this* branch.

The prerequisites are repo-specific: read the project's own CLAUDE.md (or README) for the
codegen step, the env file, the containers that must be up, the port the app expects, and any
sibling component that has to be built first. Reproduce that list in the card's Prerequisites
section rather than assuming the reader has it.

### 3. Run the layers, cheapest first

Gate first (typecheck, lint), then the layers that matter. Record the exact command and the
exact expected output for each - a number with no command beside it is not reproducible.

When the change ports or reimplements behavior that exists elsewhere, the load-bearing layer is
a **parity run**: drive the real reference implementation over a real input, feed that exact
captured input to the new implementation, and diff the two verdicts. Any disagreement is a port
defect rather than a data difference. Wire this as a script the reader can re-run.

### 4. Distinguish a pass from an abstention

The single most common way a card lies. In any system whose output is sparse by design - it
records only failures, only fires, only diffs - a check that evaluated and passed and a check
that silently abstained both leave zero rows and both look green.

Prove the trigger inputs were actually present. Dump the real upstream payload, count
hydration per field over the records the check actually considered, and show it compared real
values against real thresholds. Account for every gap or it reads as an unexplained hole.

### 5. Confirm magic constants against the live source

Look up ids, thresholds, enum names, and case labels in the source of truth rather than
assuming them. A card asserting the wrong constant is worse than no card.

### 6. Write the card

Format in [references/card-format.md](references/card-format.md). Patterns worth copying,
with no repo specifics attached, are in [references/patterns.md](references/patterns.md).

Write UTF-8 explicitly. On Windows, Python's `Path.write_text` defaults to cp1252 and corrupts
non-ASCII.

Save as `<tracker-key-lowercase>-validation-comment.md` in the repo root, **untracked**. Cards
are not committed; they live on the tracker. Add a row to your own local index (see
[references/patterns.md](references/patterns.md)) so the next run has one more example.

### 7. Post it

Post the Markdown to the tracker with the adapter from Configuration, converting first on
whichever path needs it:

- **WIKI** - `jira-server`, and Jira Cloud via `/rest/api/2`. Run the Markdown through the
  conversion table in [references/card-format.md](references/card-format.md). Both render WIKI
  markup and post Markdown raw, so an unconverted card looks broken and has to be edited in
  place.
- **ADF** - Jira Cloud via `/rest/api/3`. The body is a JSON document, not a string; posting
  Markdown there is rejected outright or stored as one literal paragraph. Convert, or post to
  `/rest/api/2` with WIKI instead - the simpler choice when no ADF converter is at hand.
- **Markdown as-is** - GitHub and Linear.

Read the comment back and check for leaked source markup before declaring it posted. For the
WIKI path, that means counting `## ` and `|---|` occurrences in the rendered body; both must
be zero. For ADF, confirm the response body parsed as a document rather than a single
paragraph of escaped Markdown.

### 8. Link it from the PR body

The card goes on the tracker; the PR body **references** it, matching `/write-pr`:

```
**Full validation card: [<KEY> comment <id>](<link to the comment anchor>)**
```

Then a short bullet summary in the PR body. If an earlier card exists on the issue and is
still accurate for part of the change, link both and say what each covers.

### 9. Scan before finishing

Scan the card for anything that should not be published: credentials, tokens, absolute paths
containing secrets, customer data. Cards are internal but they are permanent.

## What belongs in a card that authors usually leave out

- **What the change does NOT do yet.** A check that ships behind an allowlist or a flag is
  logged, not enforced. Say so, or a reader assumes protection that is not there.
- **A bug the validation found.** Its presence is evidence the validation was real. Include the
  measured blast radius.
- **Unexplained gaps, explained.** "154/174 records carry the trigger field" needs the sentence
  saying the other 20 have no value for it and the check abstains by design.
- **Scope drift.** If folding changed what the PR is, say the approval predates it rather than
  letting a large diff ride a description written for a small one.
- **A dependency the card revealed.** Migration ordering, merge order, a map that must be
  updated by future PRs.

## Anti-patterns

- A card that is only a test-count table. See the rule above.
- `toHaveLength(0)` as evidence. Absence assertions pass on broken code; assert *which*, not
  *how many*, and mutate to confirm.
- Claiming a guard works without reverting the fix and watching it fail.
- Validating in a secondary worktree and reporting its stale-dependency errors as findings.
- Posting the card into the PR body instead of the tracker. The body links; the tracker holds.
- Committing the card to the repo.
