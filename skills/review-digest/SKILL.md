---
name: review-digest
description: Turn a PR's AI-reviewer comment pile (codex / cursor / claude / copilot) into a clean, line-grouped digest using a LOCAL model — each bot's own headline + stated severity + verdict, extracted (not re-judged), grouped by file:line. Free, offline, no cloud tokens. Use when someone says "triage the comments on PR N", "what did the bots flag on PR N", "digest the review comments", "summarize the PR feedback", or invokes /review-digest N. A pre-pass that feeds a review coordinator — advisory only, it never gates a merge.
argument-hint: "<pr-number> [-repo owner/name] — e.g. /review-digest 181"
user_invocable: true
---

# Review-comment digest (local reviewer-triage)

Collapses the four-bot comment flood on a PR into a scannable, line-grouped list, using a **local**
model. For each inline bot comment it *extracts* the bot's own headline + stated severity — it does
not re-judge whether the finding is valid (small local models comprehend dense findings poorly but
extract reliably). One model call per comment; grouped by `file:line` so same-line findings sit
together.

## Prerequisites

- A local reviewer-extraction CLI that pulls a PR's bot comments (via `gh`) and prints one row per
  finding. Set `REVTRIAGE_BIN` to its path, or edit the command below. A reference implementation is
  a small Go tool that calls Ollama over HTTP — swap in whatever you have.
- [Ollama](https://ollama.com) running with a small instruct model pulled (e.g. `qwen2.5:7b`).
- `gh` authenticated.

## How to run

No cwd needed — it uses `gh` + Ollama over HTTP. Pass the PR number (and the repo if it isn't the
current one):

```
"$REVTRIAGE_BIN" <pr-number>
"$REVTRIAGE_BIN" -repo owner/name <pr-number>
"$REVTRIAGE_BIN" -json -repo owner/name <pr-number>
```

It prints one row per bot finding: `line · severity · verdict · confidence · bot · headline`.
`-json` emits the same findings as a JSON array with `comment_id`/`file`/`url` for joining back to
the source comments — the form a review coordinator consumes as its ingest pre-pass.

## What to relay

- The digest as-is, then a one-line read: which findings cluster on the same locus, and which look
  like the real must-fixes (trust `severity` over `verdict` — verdict is the soft field).

## Rules

- **Trust `severity` over `verdict`.** Severity is read off the bot's own text; verdict is a softer
  inference. `unknown` severity is normal for Copilot (it doesn't emit a severity badge) — don't
  invent one.
- This is a pre-pass, not a gate. It reduces noise before human/coordinator review; it never
  decides merge/no-merge.
- Prereqs: Ollama running with a small model pulled; `gh` authenticated. First call cold-loads the
  model (~30-60s); subsequent comments are a few seconds each.
- If a headline comes out as a long sentence, the bot led with prose instead of a title — the
  severity + line are still reliable.
