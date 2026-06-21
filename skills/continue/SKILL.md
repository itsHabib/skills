---
name: continue
description: Emit a paste-ready continuation prompt that lets a fresh Claude Code session pick up exactly where this one left off. Use when context is filling up and the user says "continuation prompt", "continue prompt", "write me a continuation", "carry this over", "hand this off to a fresh session", "I'm running low on context", or invokes `/continue`. NOT the CLI `--continue` flag — this produces a self-contained handoff brief.
argument-hint: "[focus] — optional: narrow the handoff to one thread (e.g. 'just the ship PR work'); omit to capture the whole session"
user_invocable: true
---

# /continue — write a continuation prompt

The operator is running low on context and wants to resume this work in a fresh session. Synthesize the current conversation into a single paste-ready brief that a cold session can act on immediately.

This is invoked when context is tight, so **work from what's already in context** — don't go exploring. The conversation is the source. One cheap git check to ground the state is fine; a research sweep is not.

## What the fresh session already has (so you don't repeat it)

Inherited automatically:
- The repo's `CLAUDE.md`
- Auto-memory for the project (`~/.claude/projects/<hash>/memory/`)
- Global skills, MCP servers, settings

NOT inherited:
- This conversation — zero memory of what we discussed, read, decided, or tried
- Files read, diffs seen, uncommitted edits, dead-ends hit

So the brief carries **only what this conversation added**. Don't restate CLAUDE.md, memory, or house conventions — they load on their own. Every file path, decision, constraint, and failed approach that matters has to be in the brief or it's gone.

## Ground the state (best-effort, one pass)

If the session is in a git repo, a single quick check sharpens the "State" section — current branch, uncommitted files, last commit or two, and open PR/CI if relevant. Skip silently if not a repo or it'd cost too much. Never let grounding balloon into exploration.

## The brief

Emit it as one fenced code block so the operator can copy it clean. Use these headers; **skip any section that's genuinely empty** rather than padding it.

````
Continuing from a prior session that ran low on context. You already have CLAUDE.md,
project memory, and skills — below is only what that session added.

## Goal
<the overall objective, 1-2 sentences>

## State
- Done: <concrete outcomes — paths, SHAs, PR#s. No process narration.>
- In flight: <what's mid-stream right now, incl. uncommitted edits to <files>>
- Branch / PR: <branch>, <PR url if any>, CI <state>

## Next
1. <the immediate next action, concrete enough to start cold>
2. <then this>

## Key facts (this session only)
- <decision made + the one-phrase why>
- <constraint or API shape discovered>
- <dead end already tried — don't repeat: ...>

## Pointers
- <file:line worth opening first>
- <command to re-run / how to verify>
````

## Rules

- **Honest state.** Done means done and verified. If something's untested or half-applied, it goes under "In flight," not "Done." Don't launder hope into completion.
- **Tight.** Results, paths, PR#s, SHAs — not adjectives. If a section won't fit in a few bullets, the framing is off, not the cap.
- **Self-contained.** Assume the reader knows nothing about this chat. A path or decision that lives only in our conversation must appear here.
- **Don't re-derive the inherited.** No CLAUDE.md recap, no memory recap, no house-style boilerplate.
- If a `[focus]` arg is given, scope the brief to that thread and say so in the Goal line.

## After emitting

One line below the block: offer to save it to `docs/prompts/continue-<YYYY-MM-DD>.md` (scratch — not committed) if they'd rather keep it than paste it. Default is print-to-chat; only write the file if asked.
