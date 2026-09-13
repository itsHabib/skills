---
name: release
description: Release the current agent session's claims in the shared session-claims log. Use when the user says "/release", "release this session", "done with this session", or "hand this off", optionally with a note. The note becomes the generated handoff.
user_invocable: true
---

# /release - release this session's claims

Append one `release` event to `~/.claude/session-claims/claims.jsonl`, closing this session's
open claims. Determine the session UUID from `CODEX_THREAD_ID` (fall back to
`CODEX_SESSION_ID`) in Codex, or from the scratchpad directory in Claude. Refuse to append if
no unambiguous current session id is available. Include a user note;
if a handoff was requested or meaningful loops remain, draft and show a 1-3 sentence state and
next-step note before appending it.

```json
{"ts":"2026-08-06T18:40:00Z","session":"<uuid>","event":"release","note":"PR #73 green, awaiting review; next: fold panel findings."}
```

Append-only: never edit prior lines. A release with no prior claim is harmless and still valid.
Confirm: `released: session <first 8 chars>...`.
