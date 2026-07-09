---
name: offload
description: Offload a cheap, verifiable sub-task to the LOCAL model (Ollama, $0, offline) via the `local` CLI — narrow a big file list, extract structure from noisy tool output, classify log lines or command success/failure. Use PROACTIVELY mid-task when a sub-step is mechanical narrowing/extraction/shallow-classification AND you can verify the result at a glance; also when the operator says "offload that", "run that locally", "use the local model", or invokes /offload. NEVER for deep judgment (code review, risk calls, dense-diff reasoning) — that stays with you.
---

# Offload to the local co-processor

`local` (a small CLI on your PATH) runs a structured extract/classify task on the local model:

```
local -prompt "<task>" -schema '<json-schema | @file>' [-min-confidence 0.7] < input
```

Pipe the raw material on stdin; output is one JSON line: `{"source","reason","result"}`.

## The rule

Offload only sub-tasks that are **verifiable or escalate-safe**. Never trust-without-re-check:

- **Read the narrowed result yourself.** The local model shrinks your input; you still do the
  judgment on what comes back. A summarize-and-believe offload is the forbidden shape.
- A wrong answer must cost you only a redo (you fall back to doing the sub-task yourself),
  never a flipped decision.

Decision rule (validated S0/S1/S2, 2026-07): **extract / shallow-classify / retrieve → local;
deep judgment → cloud (you).** Good fits: filter a 500-file list down to candidates, pull
structured fields out of verbose tool output, classify log lines by severity, bucket command
outcomes. Bad fits: judging a diff's risk, reviewing code, anything where being wrong is silent.

## Reading the output

- `"source":"local"` with no `reason` — the gate trusted it. Still spot-check against the input.
- `reason` non-empty — the gate distrusted the result (verifier fail ranks above self-reported
  confidence; no escalator is wired in the CLI). **You are the escalation:** discard the result
  and do the sub-task yourself.
- Prefer extract-shaped schemas that demand a **verbatim evidence field** (a quote from the
  input) — that's the trust signal; self-reported confidence is confidently-wrong.

## Prereqs

Ollama running with `qwen2.5:7b` pulled, and the `local` CLI on your PATH — a thin wrapper
that runs a structured extract/classify prompt against the local model. Operator-built; supply
your own or adapt the skill to your local-model runner.
