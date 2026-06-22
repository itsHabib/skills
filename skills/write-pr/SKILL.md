---
name: write-pr
description: Write or update the current PR description in a standard format (Summary, Closes [ticket], What this adds, Validation). Use when opening a new PR or refreshing an existing one.
user_invocable: true
---

# /write-pr

Write or update the PR description for the current branch. Derives the ticket, summary, and high-level intent automatically, then asks about validation before writing.

## Configuration

This skill assumes a Jira-style tracker. Set these (env vars, or adapt inline):

- `JIRA_BASE_URL` - e.g. `https://jira.example.com`
- `JIRA_PROJECT` - the project key tickets live under, e.g. `PROJ`

Branches are expected to embed the ticket as `<project>-<number>` (e.g.
`proj-123_short_slug`). If you use Linear or GitHub Issues, adjust the regex
and URL in step 2.

## Steps

### 1. Gather branch context

Run these to understand what's on the branch:

```bash
# current branch name
git branch --show-current

# commits ahead of the default branch
git log origin/HEAD..HEAD --oneline

# files changed vs the default branch
git diff origin/HEAD..HEAD --name-only
```

Store results as `$BRANCH`, `$COMMITS`, `$FILES`. (Substitute `main` for
`origin/HEAD` if your local default-branch ref is current.)

### 2. Derive the ticket

Parse `$BRANCH` for a ticket identifier matching your project key:

- Pattern `<JIRA_PROJECT>-\d+` (case-insensitive) -> `<KEY>`
  Ticket URL: `<JIRA_BASE_URL>/browse/<KEY>`
- No match -> `$TICKET` is empty; omit the "Closes" line.

Store as `$TICKET` and `$TICKET_URL`.

### 3. Read diffs to understand what's landing

For each file in `$FILES`, run:

```bash
git diff origin/HEAD..HEAD -- <file>
```

Read diffs plus commit messages. You need this for the "What this adds" section.

### 4. Draft the Summary

Write 2-4 sentences summarising what the PR does and why, derived from the commit messages and diffs. The Summary is the "what and why at a glance" paragraph - do not repeat the Changes list here.

### 5. Draft "What this adds"

This section answers: what does a reviewer see as *new capability or surface area* when this merges? Think in terms of concepts, not files.

Format as bold concept headers, each followed by a tight bullet list:

```
**N new [things]** for [purpose]:
- name1, name2, name3

**N new fields** (brief description):
- `fieldName` — what it is
- `fieldName2` — what it is

**Renamed: oldName → newName** — one sentence why.
```

Only include headers that have real content. If the PR is a pure refactor with no new public surface area, omit this section entirely and add a sentence to the Summary instead.

Good "What this adds" headers:
- `**N new [features/rules/endpoints]**`
- `**N new [thing] fields**`
- `**Renamed: X → Y**`
- `**New API endpoint: POST /api/...`**`
- `**Test coverage for ...**`

### 6. Ask about Validation

Use `AskUserQuestion` with these options:

- **Tested locally** — I'll describe where/how
- **CI / automated** — covered by tests or CI run (provide run link if you have one)
- **Ticket** — validation captured in the tracker ticket
- **N/A** — no runtime behaviour changed (types-only, docs, config, etc.)
- **Other** — I'll type it

Branch on the answer:
- "Tested locally" → ask a follow-up: "What commands or steps did you run?"
- "Other" → ask a follow-up: "Describe the validation (one or two sentences)."
- "CI / automated" → ask: "Link to the CI run, or just say 'see CI'."
- "Ticket" → use `Validation captured in [$TICKET]($TICKET_URL).` (or just "Validation captured in the ticket." if no ticket).
- "N/A" → use `N/A — no runtime behaviour changed.`

For "Tested locally" responses, format as a checkbox list. Use `[x]` for steps the user confirmed ran successfully, `[ ]` for integration or follow-up steps that are captured in a ticket:

```
- [x] unit tests pass (`<test command>`)
- [x] No type errors (`<typecheck command>`)
- [ ] Live integration - see [$TICKET]($TICKET_URL)
```

### 7. Compose and write the description

Assemble the body:

```
## Summary
$SUMMARY

Closes [$TICKET]($TICKET_URL)

## What this adds
$WHAT_THIS_ADDS

## Validation
$VALIDATION
```

Omit the `Closes` line if `$TICKET` is empty.
Omit `## What this adds` if there is nothing to put in it (pure refactor, etc.).

Check if a PR already exists for the branch:

```bash
gh pr view --json number,url 2>/dev/null
```

- PR exists → `gh pr edit --body "..."` to update it. Print the PR URL.
- No PR → print the body to stdout so the user can paste it, or suggest running `gh pr create`.

## Notes

- The Summary is a paragraph, not bullets.
- "What this adds" is about capability and surface area - what a future reviewer or user now has access to. The diff covers the file-level mechanism; don't restate it as a Changes list.
- No `Generated with ...` footer.
