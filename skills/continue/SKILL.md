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

## The cut filter (apply before writing a single line)

A brief competes with the work for attention. If reading it costs what re-deriving the state
would cost, it has failed. So the test for every candidate line is: **could a cold session get
this with one command?** If yes, cut it.

Cut:
- Anything one command away: PR title/draft/mergeable state (`gh pr view`), commit SHAs and
  messages (`git log`), uncommitted file lists (`git status`), test counts and pass/fail (re-run it),
  file contents (open the file).
- Findings already written into a doc, card, or ticket. Point at it by path or ID; don't restate it.
- Process narration: what was explored, what was considered, how long something took.

Keep only what dies with this conversation:
- Decisions and the one-phrase why.
- Dead ends already tried, so they aren't repeated.
- Non-obvious constraints and gotchas discovered the hard way.
- Paths and IDs the reader would have no way to guess.

## Ground the state (best-effort, one pass)

If the session is in a git repo, one quick check keeps the "State" lines **accurate**. It is not
a content source: don't transcribe branch names, SHAs, CI status, or file lists into the brief
just because you looked them up. Include one only when a decision hangs on it. Skip the check
silently if not a repo or if it'd cost too much, and never let it balloon into exploration.

## The brief

Emit it as one fenced code block so the operator can copy it clean. Use these headers; **skip any
section that's genuinely empty** rather than padding it.

**The whole brief targets 15-20 lines.** The per-section caps below are hard, not aspirational.
Every line is one line: no sub-bullets, no wrapped paragraphs. If something won't fit, that's a
signal it belongs in a doc the brief points at, not in the brief.

````
Continuing from a prior session that ran low on context. You already have CLAUDE.md,
project memory, and skills — below is only what that session added.

## Goal
<the overall objective, 1-2 sentences>

## State                              [one line per work item; if over 6, group the quiet ones]
- Done: <item> (<what makes it done>)
- In flight: <item> (<exactly what's mid-stream, incl. uncommitted edits>)

## Next                               [max 3, ordered]
1. <the immediate next action, concrete enough to start cold>

## Key facts                          [max 5 bullets, one line each]
- <decision + the one-phrase why>
- <dead end already tried, so it isn't repeated>

## Pointers                           [max 2, only if not obvious from the above]
- <file:line worth opening first, or the command to verify>
````

One line per work item means one line: a PR that was opened, reviewed, redesigned, and is now
awaiting CI still gets a single line naming where it stands and why the redesign happened. The
history is not the state. Items with nothing actionable pending (a background task still running,
a PR sitting green and waiting) share one line rather than each taking their own.

The bracketed caps are instructions to you, not part of the emitted brief. Strip them.

## Rules

- **Honest state.** Done means done and verified. If something's untested or half-applied, it goes under "In flight," not "Done." Don't launder hope into completion. This rule outranks the caps: never drop an in-flight item to hit a line count, and never promote one to Done to save a line.
- **Tight.** Results, paths, IDs, not adjectives. A section that overflows its cap means the framing is wrong, not that the cap is.
- **Self-contained.** Assume the reader knows nothing about this chat. A path or decision that lives only in our conversation must appear here. This also outranks the caps: if five decisions genuinely can't be rediscovered, five bullets is right, and something re-derivable elsewhere is what gets cut.
- **Don't re-derive the inherited.** No CLAUDE.md recap, no memory recap, no house-style boilerplate.
- If a `[focus]` arg is given, scope the brief to that thread and say so in the Goal line.

## After emitting

One line below the block: offer to save it to `docs/prompts/continue-<YYYY-MM-DD>.md` (scratch — not committed) if they'd rather keep it than paste it. Default is print-to-chat; only write the file if asked.
