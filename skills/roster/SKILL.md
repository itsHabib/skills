---
name: roster
description: Render the cross-harness session-claims roster - session to work to PRs to last activity - from ~/.claude/session-claims/claims.jsonl plus transcript, PR, and worktree signals. Use when the user asks "roster", "what are my sessions doing", "which session owns what", or invokes /roster. Read-only.
user_invocable: true
---

# /roster - Claude and Codex session claims

Reduce `~/.claude/session-claims/claims.jsonl` without writing it. Per session, the latest
`claim` is the work label, PR `link` events accrete, and a newer `release` closes the row.
Default output hides closed rows; `--all` includes them with the release note.

Best-effort enrich each row with transcript activity: Claude uses
`~/.claude/projects/<cwd-slug>/<session-id>.jsonl`; Codex uses the matching
`~/.codex/sessions/**/rollout-*<session-id>.jsonl`. Then add linked PR state via `gh pr view`
and linked worktree existence. Fall back to the latest event timestamp when no transcript exists. Mark rows
older than 24h stale and hide rows older than seven days unless `--all`.

Render `SESSION | AGE | WORK | BRANCH / WORKTREE | PRS | LAST`. Flag a work unit claimed by two
live sessions. All linked PRs closed or merged with no other open claim is `done (unreleased)` and
hidden by default. Empty log is a one-line empty result; do not scaffold state.
