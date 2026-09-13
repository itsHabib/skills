---
name: push
description: Push the current session's work to another agent surface so it pops up there as a live, resumable session — `push codex` teleports this conversation into the Codex desktop app as a real thread (transcript injection, zero tokens), `push chip` spins a Claude Code chip, `push cloud` is reserved. Use when the user says "push this to codex", "push codex", "hand this to codex", "get this session into my codex tab", "push this to a chip", or invokes /push [target]. Distinct from /continue (paste-ready prompt, no session created) and /chip (Claude-only, task-shaped) — /push materializes a real session on the target surface, pre-warmed with this session's context.
argument-hint: "<codex|chip> [focus] — target surface; optional focus narrows the handoff to one thread"
user_invocable: true
---

# /push — pop this session up on another agent surface

Take what this session is doing and materialize it as a real session on the target surface. The user then continues the work *there*, warm, instead of cold-starting.

Argument: first word is the target (`codex` | `chip`); the rest is an optional focus that narrows the push to one thread. No target → ask one short question, don't guess.

## Step 1 — build the handoff packet (both targets)

Same discipline as /continue: work from what's already in context, one cheap git check to ground state, no exploration sweep. The packet carries **only what this conversation added** — the target session loads its own repo instructions and memory (Codex loads `AGENTS.md`, not `CLAUDE.md`, so anything that lives only in CLAUDE.md and matters must go in the packet).

Packet shape (skip empty sections):

```
Handoff from a Claude Code session; you are picking this work up mid-stream.

## Goal
<1-2 sentences>

## State
- Done: <concrete outcomes — paths, SHAs, PR#s>
- In flight: <mid-stream work, incl. uncommitted edits to <files>>
- Branch / PR: <branch>, <PR url>, CI <state>

## Next
1. <immediate next action, concrete enough to start cold>

## Key facts (this session only)
- <decision + one-phrase why>
- <dead end already tried — don't repeat>

## Pointers
- <file:line to open first>
- <command to verify>
```

Determine the working directory for the target session: the repo the work lives in, absolute path. Never the scratchpad.

## Step 2a — target `codex` — transcript injection

Codex's session store is plain files: rollout JSONL under `~/.codex/sessions/YYYY/MM/DD/` plus a `threads` row in `~/.codex/state_5.sqlite`. A fresh `codex app-server` serves hand-written threads via `thread/list` / `thread/read` (verified 2026-08, codex-cli 0.146), so an injected conversation is a genuine, resumable thread — no tokens spent. The desktop groups threads by project (`cwd` / git origin).

1. **Mint a UUIDv7 session id** (time-ordered, like every real Codex id):
   ```sh
   python3 -c "import time,os; ms=int(time.time()*1000); r=os.urandom(10).hex(); t=f'{ms:012x}'; print(f'{t[:8]}-{t[8:12]}-7{r[0:3]}-{hex(int(r[3],16)&0x3|0x8)[2:]}{r[4:7]}-{r[8:20]}')"
   ```
2. **Write the rollout file** to `~/.codex/sessions/<YYYY/MM/DD>/rollout-<YYYY-MM-DDTHH-MM-SS>-<id>.jsonl` (UTC). Lines, in order — each `{"timestamp":"<iso-ms>Z","type":...,"payload":...}`:
   - `session_meta`: `{"session_id":<id>,"id":<id>,"timestamp":<iso>,"cwd":<repo>,"originator":"Codex Desktop","cli_version":"<from an existing thread row>","source":"vscode","thread_source":"user","model_provider":"openai"}`
   - One `response_item` per conversation turn: `{"type":"message","role":"user"|"assistant","content":[{"type":"input_text"|"output_text","text":...}]}` (`input_text` for user, `output_text` for assistant).
   - **Plus one `event_msg` per turn** — the UI renders from the event stream, not from response_items (verified 2026-08: model saw injected response_item-only history, UI displayed none of it): user turns `{"type":"user_message","client_id":"<uuid4>","message":<text>,"images":[]}`, assistant turns `{"type":"agent_message","message":<text>}`. Emit the response_item and its event_msg adjacent, in turn order.
   - **First user message = the handoff packet.** Then the real turns of this session, condensed: keep the user's messages near-verbatim, condense long assistant turns, render tool activity as bracketed notes inside the assistant text (`[ran tests: 34 pass]`). Skip system noise.
   - **Final assistant message**: a short "state of play + next step" so the thread reads as parked, ready to continue.
3. **Insert the thread row** (values copied from a real row where noted):
   ```sh
   sqlite3 ~/.codex/state_5.sqlite "insert into threads (id, rollout_path, created_at, updated_at, source, model_provider, cwd, title, sandbox_policy, approval_mode, tokens_used, has_user_event, archived, git_origin_url, cli_version, first_user_message, memory_mode, model, reasoning_effort, thread_source, preview, history_mode, recency_at) values ('<id>', '<rollout_path>', strftime('%s','now'), strftime('%s','now'), 'vscode', 'openai', '<repo>', '<short imperative title>', '{\"type\":\"disabled\"}', 'never', 0, 0, 0, '<git origin or NULL>', '<cli_version>', '<first line of packet>', 'enabled', '<model from a real row>', 'high', 'user', '<last assistant line>', 'legacy', strftime('%s','now'))"
   ```
   `source` must be `vscode` — the desktop list filters out other sources (verified: `exec` threads are hidden).
4. **Append the index line** to `~/.codex/session_index.jsonl`:
   `{"id":"<id>","thread_name":"<title>","updated_at":"<iso>Z"}`
5. **Warm the thread — one real Codex turn** (default, not optional):
   ```sh
   codex exec resume <id> --skip-git-repo-check \
     "You've just been handed this session. Read the files under Pointers. Post a short arrival message: 2-3 bullets on the state as you understand it, then stop and wait for the operator. Do not modify any files."
   ```
   This does two jobs (verified live 2026-08): the operator opens a thread where Codex has already read the state and spoken last — nothing to type — and Codex's own writer rewrites the hand-made rollout into the full format (turn_context, world_state, event stream) that the UI renders cleanly; a raw injected skeleton can open blank until poked. The resume rewrites the thread title to the warm-up prompt, so re-set it:
   ```sh
   sqlite3 ~/.codex/state_5.sqlite "update threads set title='<short imperative title>' where id='<id>'"
   ```
6. **Fire the live deep link**: `open "codex://threads/<id>"`. The Codex desktop (inside ChatGPT.app) fronts and opens the thread. A stale instance shows "Conversation not found" — harmless; the app refreshes its list on navigation, so **fire the link a second time** after a beat (verified live 2026-08: second fire landed with no restart).
7. Report: title, id, project grouping, and `codex resume <id>` as the terminal route. If the deep link misses twice, the thread is guaranteed present on next app launch; *offer* (never just do — it kills in-flight Codex turns):
   ```sh
   osascript -e 'quit app "ChatGPT"' && sleep 2 && open -a ChatGPT && sleep 8 && open "codex://threads/<id>"
   ```

Boundaries: only ever *add* — never edit or delete existing rollout files or threads rows (the warm-up's title re-set on the pushed thread's own row is the one exception), never touch `~/.codex/auth.json` or other config.

Known-fragile (internals, not contract — re-verify if a codex update breaks this): the `source='vscode'` filter, the `threads` schema, the rollout line shapes, the desktop only re-reading the store on cold start (Cmd+R does not refresh; the IPC socket rejects outside connections).

### Fallback — exec seeding (public interface only)

If injection breaks after a codex update: `codex exec --json -C <repo> --skip-git-repo-check "<packet> ... Reply with a 3-bullet summary of your understanding, then stop and wait for the operator."` — capture the id from the `{"type":"thread.started","thread_id":...}` JSONL event (supported interface, don't scrape stdout), then flip that thread's `source` to `vscode` as in step 3 and deep-link it. Costs one model turn; the packet lands as a single message instead of a conversation.

### Variant — `push codex --composer` (supported surfaces only)

Zero tokens, zero internals, one manual click: `open "codex://new?prompt=$(jq -rn --arg v "$(cat <packet>)" '$v|@uri')&path=$(jq -rn --arg v "<repo>" '$v|@uri')"` opens a new desktop chat in the right workspace with the packet prefilled in the composer; the operator reads and hits send. Use when the operator wants nothing undocumented touched.

### Context doc

`~/dev/workbench/docs/features/codex-external-session-ingress/notes.md` — a Codex-side investigation of the same problem (2026-08): documents the deep links, `codex exec --json`, and the app-server protocol (`thread/start`, `turn/start`, `turn/steer`; handshake is `initialize` **then an `initialized` notification`). It recommends against direct rollout/sqlite writes — that is the vendor-contract view; this skill accepts the risk knowingly (new threads only, warm-up normalizes state through codex's own writer) and keeps the supported paths above as escape hatches.

The sanctioned endgame is an app-server client — **verified working 2026-08**: spawn `codex app-server` (stdio JSONL; handshake is `initialize` request THEN an `initialized` notification — omit the notification and the server silently drops you), then `thread/start` `{"cwd":<repo>,"approvalPolicy":"never","sandbox":"read-only"}` returns a thread with **`source:"vscode"` natively** — desktop-visible with zero sqlite touches. Follow with `turn/start` carrying the packet for the warm arrival, then the deep link. Everything injection buys except the multi-turn transcript replay; prefer it for a future `push` binary, keep injection for when the operator wants the conversation itself rendered as chat.

**Turn lifecycle (learned the hard way, 2026-08):** the client that called `turn/start` must stay connected until the turn truly completes — killing the app-server process mid-turn persists `turn_aborted` and the reply is lost even after `item/agentMessage/delta` events streamed (a delta is not a commit). Don't trust ad-hoc event matching: after the turn, re-read the thread's rollout and confirm an `event_msg`/`agent_message` line exists before exiting. This is the strongest argument for the dedicated binary over inline scripting.

## Step 2b — target `chip`

Follow the /chip skill's contract: `mcp__ccd_session__spawn_task` with an imperative title, the packet as the prompt body, `cwd` set to the repo if it differs from the current one. The packet already satisfies chip's "self-contained prompt" rule.

## Rules

- Honest state in the packet and the injected transcript: done means verified; untested work goes under "In flight". Never fabricate turns that didn't happen — condense, don't invent.
- A pushed thread always ends parked ("ready to continue — waiting on you"); /push hands off, it never launches autonomous work on the other surface.
- One push per invocation; if the user wants both targets, run the steps twice from the same packet.

## After pushing

One short line: target, thread title + id / chip title, project grouping, and (codex) whether the deep link landed live or the thread waits for next app launch.
