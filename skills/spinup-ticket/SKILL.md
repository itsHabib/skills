---
name: spinup-ticket
description: Create a Jira ticket under a given epic via the Jira REST API. Use when the user says "spin up a ticket", "create a Jira ticket", "open a ticket in <epic>", or similar - typically just before kicking off a new piece of work that needs tracking. This skill only deals with the ticket itself; branches, PRs, and implementation are out of scope.
user_invocable: true
---

# /spinup-ticket

Create a ticket on a Jira Server / Data Center instance via REST. Stops at the
ticket - the user (or another skill) handles the branch, the implementation,
and the PR separately.

## Configuration

Set these (env vars, a local secrets file, or your secret store - resolve at
runtime, never hard-code):

- `JIRA_BASE_URL` - e.g. `https://jira.example.com`
- `JIRA_TOKEN` - a personal access token. Jira Server / DC uses **Bearer**
  auth (`Authorization: Bearer $JIRA_TOKEN`). Jira Cloud differs - it uses
  Basic auth with `email:api_token`; adjust the header if you're on Cloud.
- `JIRA_PROJECT` - project key, e.g. `PROJ`
- `JIRA_USER` - your account name for the assignee, e.g. `you@example.com`
- `JIRA_EPIC_FIELD` - the "Epic Link" custom field id, e.g. `customfield_10100`.
  This is instance-specific. Find it once with:
  ```bash
  curl -s -H "Authorization: Bearer $JIRA_TOKEN" \
    "$JIRA_BASE_URL/rest/api/2/field" \
    | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>JSON.parse(d).filter(f=>/epic link/i.test(f.name)).forEach(f=>console.log(f.id,f.name)))"
  ```

## Required inputs

- **Epic key or URL** - e.g. `PROJ-100` or `$JIRA_BASE_URL/browse/PROJ-100`.
- **Summary** - short imperative title (no `[PROJ-NNN]` suffix; Jira attaches
  the key on its own)
- **Description body** - 2-4 sentences, high level, what + why. Link the design
  doc if one exists
- **Acceptance criteria** - bulleted "done" checklist

If any are missing, ask once. Don't invent epic keys.

## Steps

### 1. Pull a sibling ticket for tone

Find one recent ticket in the same epic to match section depth and voice:

```bash
curl -s -H "Authorization: Bearer $JIRA_TOKEN" -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/2/search?jql=%22Epic+Link%22%3D<EPIC-KEY>+ORDER+BY+created+DESC&maxResults=3&fields=summary,description"
```

Read one of those bodies; mirror its voice. Don't copy content.

### 2. Draft the Jira wiki-markup description

Two sections, in this order, with bold headers:

```
*Description*
<2-4 sentences. Capability and motivation, not implementation. Link the
design doc if one exists.>

*Acceptance Criteria*
* <bullet>
* <bullet>
* <bullet>
```

Wiki-markup conventions:

- `*Section*` for bold headers (not `## Section`)
- `{{foo}}` for inline code (not backticks)
- `* ` for bullets
- `[link text|https://...]` for links
- No em dashes (use hyphens)

Hard rules:

- **No low-level impl details** unless the ticket *requires* an architectural
  decision in the description. Default to capability + outcome.
- **No diff-size or LOC constraints** ("small PR", "~N lines").

### 3. POST to the Jira REST API

Jira Server / DC, API v2, Bearer auth. Field mappings:

- Project key: `$JIRA_PROJECT`
- Issue type: `Task` for most tickets
- Epic Link: `$JIRA_EPIC_FIELD` - set to the epic key string
- Priority: pick what your project defaults to (e.g. `Low`)
- Assignee: usually your own `$JIRA_USER`

```bash
cat > /tmp/jira-ticket.json <<EOF
{
  "fields": {
    "project": { "key": "$JIRA_PROJECT" },
    "issuetype": { "name": "Task" },
    "summary": "<short imperative title>",
    "$JIRA_EPIC_FIELD": "<EPIC-KEY>",
    "priority": { "name": "Low" },
    "assignee": { "name": "$JIRA_USER" },
    "description": "*Description*\n<body>\n\n*Acceptance Criteria*\n* <bullet>\n* <bullet>"
  }
}
EOF
curl -s -X POST \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data @/tmp/jira-ticket.json \
  "$JIRA_BASE_URL/rest/api/2/issue"
```

The response is `{"id":"...","key":"PROJ-NNN","self":"..."}`. Echo the new
ticket key + URL back to the user.

### 4. Verify (optional but recommended)

GET the new ticket back and confirm the description / epic link / assignee
landed before declaring success:

```bash
curl -s -H "Authorization: Bearer $JIRA_TOKEN" -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/2/issue/PROJ-NNN" \
  | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const o=JSON.parse(d);console.log('summary:',o.fields.summary);console.log('assignee:',o.fields.assignee&&o.fields.assignee.name);console.log(o.fields.description)})"
```

If the POST fails (token missing / expired, validation error, etc.), print the
prepared payload + the ticket body in chat and ask the user to paste it into
Jira manually. Return the ticket key they provide.

## Out of scope

- **Branches.** Not this skill's job.
- **Pull requests.** A separate PR skill handles descriptions; `gh pr create`
  is the user's invocation.
- **Implementation.** Whoever picks up the work owns the diff.

## Conventions enforced

- Wiki markup, not GFM, in the description.
- No em dashes.
- No diff-size or LOC constraints.
- Link the design doc inside the Description when one exists.
- Default `Task` issue type, assignee = the user.
- Never echo the token in user-facing output; resolve its location at runtime.
