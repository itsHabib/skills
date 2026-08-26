---
name: transfer-context
description: Fork a thread that came up mid-task into its own briefed Claude Code session — without derailing the agent that's currently working. The source agent pauses just long enough to emit a thread-scoped context packet, spins a chip seeded with it, and resumes its main task untouched. The chip becomes a fresh session you can question about that one thread. Use when the user says "transfer context", "pull on that thread", "fork this thread off", "spin that tangent into its own session", "hand this thread to another agent", "don't derail — chip that thread with context", or invokes `/transfer-context`. Distinct from /chip (fires off a TASK, and explicitly avoids conversation-dependent context) and /continue (hands off the WHOLE session). This is thread-scoped, conversation-dependent, and non-disruptive to the source.
argument-hint: "[thread] + optional seed question — the called-out thread to fork, and what you want the sibling to chew on first"
user_invocable: true
---

# /transfer-context — fork one thread into a briefed sibling

The agent is mid-task and something it called out is worth pulling on — but not now, and not by derailing it. Snapshot just that thread, hand it to a fresh session that can carry a focused conversation about it, and get back to the main task in one beat.

Three moves, fast: **scope the thread → build the packet → spawn the chip → resume.** The source agent should spend the *minimum* to emit the packet. This runs while real work is paused, so **work from what's already in context** — one cheap grounding check is fine, exploration is not.

## Why this isn't /chip or /continue

- **/continue** hands off the *whole* session to a cold reader. This forks *one thread*.
- **/chip** fires a *task* ("go do X") and explicitly avoids anything that depends on this conversation. This is the opposite: it's *for* conversation-dependent threads, and its entire job is to package that dependency so the sibling can reason about it. The sibling is a **conversation partner to question**, not a worker to dispatch.

## What the chip inherits (so you know what MUST be in the packet)

Inherited automatically:
- The repo's `CLAUDE.md`
- Auto-memory for the project (`~/.claude/projects/<hash>/memory/`)
- Global skills, MCP servers, settings

NOT inherited:
- This conversation — zero memory of the thread, what was read, decided, or tried
- Files seen, diffs, uncommitted edits, the reasoning that surfaced the thread

So the packet carries **only what this conversation added about this thread**. Don't restate CLAUDE.md, memory, or house conventions — they load on their own. Every fact the thread rests on has to be in the packet or it's gone.

## Scope the thread (the hard part)

The value is in the scoping. Resist dumping the whole session.

- **Include:** the thread itself, the specific facts/decisions/paths it depends on, and the seed question or direction the operator wants explored.
- **Exclude:** the source agent's main task beyond one orienting line, unrelated threads, general session narration.
- If you can't tell which thread the operator means, or it needs context you'd have to go dig for, **ask one short question before forking** — don't guess and don't go exploring.

## The packet

Put this in the chip's `prompt`. Skip any section that's genuinely empty.

**Target 12-15 lines.** One line per bullet, max 4 bullets under "Context it depends on".
A packet longer than the thread is worth is a packet that failed to scope. If a fact is
already written into a doc, card, or ticket, point at it by path or ID instead of
restating it. Anything the sibling could get with one command (`gh pr view`, `git log`, a
test run) is not context, it's noise; the sibling inherits the repo and can run those.

````
Forked from another session that's still working its main task. This is a scoped
hand-off of ONE thread that came up there — not the whole session. You already
have CLAUDE.md, project memory, and skills; below is only the thread context.

## The thread
<what was called out, 1-3 sentences>

## What the operator wants from you
<the seed question or direction to explore first>

## Context it depends on (from the source session)
- <the specific facts / decisions / paths this thread rests on>
- <file:line, values, constraints the thread can't be understood without>
- <dead ends already hit on this thread, if any — don't repeat>

## Not yours
- The source session's main task is <one line>. You don't own it; don't try to continue it.

## Start by
<first concrete move — usually "confirm you've got what you need, then take on: <seed question>">
````

## Spawn the chip

Call `mcp__ccd_session__spawn_task` (same machinery as /chip):

- **`title`** — under 60 chars, imperative, thread-focused. e.g. `Explore <thread>`, `Dig into <thread>`.
- **`prompt`** — the packet above.
- **`tldr`** — 1-2 sentences, plain English, no paths/code. What the sibling will chew on and why.
- **`cwd`** — omit for same repo (default). Pass an absolute path only if the thread belongs in a different repo on this machine; then embed that repo's context in the packet too.

Keep the returned `task_id` in mind — if the thread later becomes moot, `mcp__ccd_session__dismiss_task` it.

## After forking

One short line: title, that the chip is up, and — the whole point — **the main task is resuming untouched.** Then actually resume it. Don't linger on the tangent; you just closed the detour so you wouldn't have to.
