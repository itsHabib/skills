---
name: ask-portfolio
description: Answer a question about YOUR OWN work — your code, docs, notes, past decisions and conventions — using a LOCAL offline second-brain (Ollama RAG over an index of your corpus). Free, no cloud, no data egress. Use when you ask "have we solved this before", "what's my convention for X", "where did I do Y", "what did I decide about Z", "search my own work / docs / notes", or invoke /ask-portfolio. ONLY for questions grounded in your own corpus — never general-knowledge questions.
argument-hint: "\"<your question, verbatim>\""
user_invocable: true
---

# Ask the portfolio (local second-brain)

Answers questions about your *own* body of work by running a **local** RAG tool over an embedded
index of your docs plus your notes/memory files. Grounded, cited, offline, zero cost. The model only
synthesizes retrieved text — it does not reason from scratch.

## Prerequisites

- A local RAG CLI that embeds and queries your corpus and prints a grounded answer + its sources.
  Set `BRAIN_BIN` to its path. A reference implementation is a small Go tool over Ollama
  embeddings — swap in whatever you have.
- [Ollama](https://ollama.com) with an instruct model + an embedding model pulled (e.g.
  `qwen2.5:7b` + `nomic-embed-text`).

## How to run

Run the tool from the directory holding its index (it reads the index relative to cwd):

```
pushd <dir-with-your-index>
"$BRAIN_BIN" "<your question, verbatim>"
popd
```

It prints a grounded answer, a confidence, and the source files it retrieved.

## What to relay

- The answer, plus the **top 1-2 cited source files** — always surface the source so you can
  verify. Grounding is the whole point; do not paraphrase the citations away.
- If it's a decision/convention question, quote the specific fact and where it came from.

## Rules

- Trigger only on questions about your *own* corpus (your code, docs, notes, decisions,
  conventions). For anything general/world-knowledge, don't use this — answer normally.
- **The corpus can be stale.** A note or doc may hold an old fact whose correction lives in a later
  file; RAG can surface the outdated one. If the answer smells superseded, say so and check for a
  newer source before trusting it.
- If retrieval confidence is low or the cited sources look off-topic, say so — offer to rebuild the
  index (needed after adding new docs) or fall back to a normal file search.
- Prereqs: Ollama running with the instruct + embedding models pulled. If the tool errors on a
  missing index, build it once per its docs.
