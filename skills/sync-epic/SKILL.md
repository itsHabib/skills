---
name: sync-epic
description: Audit a Jira epic and bring each child ticket's status in line with its GitHub PR state (draft PR -> In Progress, open PR -> In Review, merged PR -> Done). Use when the user says "sync the epic", "fix the epic statuses", "the epic is out of date", or invokes `/sync-epic <epic-key>`. Presents a diff first; applies transitions after one confirmation.
user_invocable: true
---

# /sync-epic

Take a Jira epic, cross-reference every non-terminal child ticket against its
GitHub PR, and apply the status transitions that bring the epic in sync with
PR reality. One audit table, one confirmation, parallel transitions.

## Configuration

Set these (env vars / secret store; resolve at runtime):

- `JIRA_BASE_URL` - e.g. `https://jira.example.com`
- `JIRA_TOKEN` - PAT; Jira Server / DC uses **Bearer** auth (Cloud uses Basic
  with `email:api_token` - adjust the header if you're on Cloud)
- `JIRA_EPIC_FIELD` - the "Epic Link" custom field id (see `/spinup-ticket` for
  how to discover it)

## The rule

| PR state | Target status |
|---|---|
| Merged | Done |
| Open, ready for review | In Review |
| Open, draft | In Progress |
| No PR / only closed-unmerged PRs | (leave alone) |

Tickets already in **Done** or a canceled state are assumed correct and never
touched. Adapt the target status names to your workflow if they differ.

## Required input

- **Epic key or URL** - e.g. `PROJ-100`. Parse the key out of a URL before
  using it. If invoked with no argument, ask once.

## Step 1: Fetch the epic's children

```bash
KEY=<epic-key>
curl -s -H "Authorization: Bearer $JIRA_TOKEN" -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/2/search?jql=%22Epic+Link%22%3D$KEY+ORDER+BY+created+ASC&maxResults=100&fields=summary,status"
```

For each issue extract `key`, `fields.summary`, `fields.status.name`. Drop any
issue whose status is **Done** or **Canceled** - those are assumed correct.

If the response has `errorMessages`, surface them and stop.

## Step 2: Resolve each ticket's live PR

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr list --repo "$REPO" --state all --search "$TICKET_KEY in:title" \
  --json number,state,isDraft,mergedAt,url,createdAt
```

`gh pr list --search` matches PR title + body, so any PR with the ticket key
in its title is found. From the array, **pick the live PR**:

1. Drop any PR where `state == "CLOSED" && mergedAt == null` (dead).
2. From what remains, take the highest `number` (most recent attempt).
3. If nothing remains, skip this ticket (no live PR).

## Step 3: Compute the target status

| Condition | Target status |
|---|---|
| `mergedAt != null` | Done |
| `state == "OPEN" && !isDraft` | In Review |
| `state == "OPEN" && isDraft` | In Progress |

If `target == current`, no transition needed - still show the row as "already
correct" for confidence.

## Step 4: Present diff and confirm

Print one markdown table. Columns: **ticket | title | current | PR | PR state |
target | action**. Make ticket and PR cells clickable links. Sort: rows needing
a transition first, then "already correct", then "no PR - skipped".

Then ask once via `AskUserQuestion`:

> Apply N transitions?

Two options: **Apply all N** / **Cancel**.

## Step 5: Resolve transition ids, fire in parallel, verify

Transition ids are instance- and workflow-specific, so resolve them by **name**
at runtime rather than hard-coding. For each ticket needing a change, list its
available transitions and pick the one whose name matches the target status:

```bash
curl -s -H "Authorization: Bearer $JIRA_TOKEN" -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/2/issue/$TICKET_KEY/transitions" \
  | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const t=JSON.parse(d).transitions.find(t=>t.name==='$TARGET'||t.to.name==='$TARGET');console.log(t?t.id:'NO_TRANSITION')})"
```

Then POST the transition:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  -H "Authorization: Bearer $JIRA_TOKEN" -H "Content-Type: application/json" \
  -d "{\"transition\":{\"id\":\"$TRANSITION_ID\"}}" \
  "$JIRA_BASE_URL/rest/api/2/issue/$TICKET_KEY/transitions"
```

Issue the POSTs as separate calls in one message so they run concurrently. A
successful transition returns HTTP `204`. If the target status isn't directly
reachable from the current one (`NO_TRANSITION`), surface that ticket and skip
it - don't force a multi-hop path silently.

After the batch, re-run Step 1 and print the final status table.

## Edge cases

- **Multiple PRs per ticket** - pick the most recent OPEN-or-MERGED; ignore
  CLOSED-unmerged.
- **No PR found** - leave the ticket alone, show "no PR - skipped". Right for
  backlog tickets not yet started.
- **Already Done / Canceled** - filtered out in Step 1, never touched.
- **PR title doesn't mention the ticket key** - `--search` misses it. Out of
  scope.
- **Expired/missing token** - print which ticket was about to transition and
  stop; ask the user to refresh the token.
- **Bad epic key** - surface the `errorMessages` verbatim.

## Out of scope

- **Creating or editing tickets** (`/spinup-ticket`).
- **Editing PR descriptions** (a PR skill).
- **Cross-epic syncs.** One epic per invocation.
- **Walking back from Done.** Done is terminal; handle reverts manually.

## Conventions enforced

- Hyphens only, no em dashes.
- Never echo the token.
- Clickable links in the audit table.
- Resolve transition ids by name, never hard-code.
