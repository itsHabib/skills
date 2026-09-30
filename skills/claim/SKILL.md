---
name: claim
description: Claim the current agent session's unit of work (dossier task, Jira ticket, PR, or free text) by appending a claim/link event to the shared session-claims log. Use when the user says "/claim <work>", "claim this session", "this session is for X", or "link pr N to this session". Opt-in only - never claim without being asked.
user_invocable: true
---

# /claim - claim this session's unit of work

Append one JSON line to `~/.claude/session-claims/claims.jsonl`. Claude and Codex share this
append-only store.

Determine the current session UUID from `CODEX_THREAD_ID` (fall back to `CODEX_SESSION_ID`) in
Codex, or from the scratchpad directory in Claude. Refuse to append if no unambiguous current
session id is available. Then collect cwd, `owner/name` remote,
branch, optional linked-worktree name, UTC RFC3339 timestamp, and work argument. Parse `pr <n>`
or a PR URL as kind `pr`; Jira keys as `jira`; `dossier <id>` as `dossier`; otherwise use
`free`. A PR attached after an existing claim is a `link`; otherwise the event is `claim`.

Append exactly one event, creating the parent directory if necessary:

```json
{"ts":"2026-08-06T14:02:11Z","session":"<uuid>","event":"claim","work":{"kind":"jira","id":"ROX-142"},"repo":"itsHabib/roxiq","branch":"claude/search-p1","worktree":"epic-jennings","cwd":"~/dev/roxiq"}
```

Never edit or rewrite prior lines. Omit unavailable repo, branch, and worktree fields. Confirm:
`claimed: <work> (session <first 8 chars>...)`.
