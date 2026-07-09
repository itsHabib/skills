---
name: health
description: Sign-on tool-health board — reads the workbench friction log and rolls it up per tool into a "how's each tool doing" view (recent friction, worst severity, one-line pain), using a LOCAL model (free, offline). Use when the operator asks "how are my tools doing", "tool health", "what's the friction", "how's everything doing", "anything need attention", "are my tools ok", or invokes /health, especially at sign-on. Distinct from /wip (in-flight work right now) and /status (session recap) — this is standing tool *health* from accumulated friction.
user_invocable: true
---

# Tool-health board (local, from the friction log)

Turns the append-only friction log into a five-second "how are my tools doing" view: per
tool, the recent friction sessions, worst severity, and a one-line pain, sorted by what needs
attention. A local model does the per-session summarization; the rollup is deterministic. Free,
offline.

## How to run
No cwd needed — it reads the friction log at its default path.

```
toolhealth
```

Optional: `-recent N` (default 14) to widen/narrow the window, `-log <path>` to point at a
different friction log.

## What to relay
- The board as-is, then a one-line read: which tool is the current hot spot (highest severity ×
  recency) and what's biting it.

## Rules
- **Trust the pain lines and the severity/recency ordering; treat the tool bucketing as a rough
  guide.** The local model is at its ceiling on attributing a multi-tool session to one owner, so
  the same friction can scatter across two tools. The *summaries* are reliable; the *bucketing* is
  approximate. (Escalating the attribution to a bigger model / cloud would sharpen it — not wired.)
- This is a digest of *logged* friction, not live state — pair it with `/wip` for what's running now.
- Prereqs: the `toolhealth` CLI on your PATH, and Ollama running with `qwen2.5:7b` pulled.
