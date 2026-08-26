---
name: chip
description: Spin the current discussion item off into its own Claude Code session via a chip in the UI. Use when the user says "chip this", "I'd like to do this on a chip", "spin this off", "make a chip for this", or invokes `/chip`. The chip launches a fresh session with its own worktree — useful for out-of-scope fixes, hygiene work, or anything you noticed in passing that shouldn't bloat the current turn.
argument-hint: "[what to chip] — short description of the work; omit if it's clear from context"
user_invocable: true
---

# /chip — spin work into its own session

Take the thing the user just pointed at and turn it into a `mcp__ccd_session__spawn_task` call. The chip appears in the UI; one click spins a fresh session + worktree, dismissal discards it. The current turn keeps running.

## What gets inherited (so you know what to embed in the prompt)

Inherited automatically:
- The target repo's `CLAUDE.md`
- Auto-memory for the target project (`~/.claude/projects/<hash>/memory/`)
- Global skills, MCP servers, settings

NOT inherited:
- This conversation — zero memory of what we discussed
- Files I've read, diffs I've seen, decisions we made
- Any other repo's context

So: any file path, line number, or decision that matters has to appear in the prompt body.

## Three cases

1. **Same repo** (default) — omit `cwd`. Chip roots in the current project.
2. **Different repo on this machine** — pass `cwd: <absolute path>`. The chip's auto-memory will be that other repo's, not this one's.
3. **Cross-repo work** — pick a primary `cwd`, then embed the other repo's path(s) and relevant context in the prompt body. The spawned session won't magically know about them.

If you can't tell which case applies, ask the user one short question before chipping.

## Writing the chip

Call `mcp__ccd_session__spawn_task` with:

- **`title`** (under 60 chars, imperative, starts with a verb) — chip label and spawned session title. Examples: `Fix stale README badge`, `Remove dead config option`, `Add missing test for X`.
- **`prompt`** — self-contained brief, target under 10 lines. Must include:
  - what to do (specific, not "clean this up")
  - file paths + line numbers when known
  - any decision or constraint from this conversation that the spawned session needs
  - acceptance criteria if non-obvious

  Point at paths rather than pasting code; the chip inherits the repo and can open them.
  A chip prompt that runs long is usually a task that wasn't scoped down far enough.
- **`tldr`** (1–2 sentences, plain English, no code or paths) — tooltip text the user sees on hover.
- **`cwd`** (optional) — only if the work belongs in a different repo than the current one. Absolute path.

## What NOT to chip

- Vague observations ("this could be cleaner")
- Trivial fixes you could do inline in seconds — just do them
- Anything that depends on this conversation's context to even understand
- Low-confidence hunches

If the user explicitly says to chip something that falls into one of these, do it anyway — they asked. But for proactive chipping, hold to the bar.

## After chipping

Confirm in one short line: title, repo (if not current), and that the chip is up. Then resume whatever the current turn was doing.
