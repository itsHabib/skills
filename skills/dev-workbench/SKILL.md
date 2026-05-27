---
name: dev-workbench
description: Scaffold (or refresh) a `## Dev workbench` section in a repo's CLAUDE.md, listing the maintainer's canonical portfolio workbench — MCP servers (dossier, ship, huddle, playwright) and skills (work-driver, work-driver-prep, shipped, status, worktree-add, worktree-list, worktree-remove, worktree-transfer, worktree-where) with purpose + when-to-use signals + example invocations. Same shape across every repo in the portfolio. Idempotent re-run between guarded markers. Use when onboarding a fresh repo, when a workbench MCP / skill lands or changes and existing CLAUDE.mds go stale, or when an existing repo's CLAUDE.md is missing the workbench context. Fork and edit the canonical list to match your own workbench.
argument-hint: "[path/to/CLAUDE.md] — defaults to ./CLAUDE.md at repo root"
user_invocable: true
---

# /dev-workbench — scaffold THE workbench section into a CLAUDE.md

**This skill is portfolio-specific.** It documents one developer's canonical dev-workflow infrastructure — dossier, ship, huddle, playwright as MCPs; `/work-driver`, `/work-driver-prep`, `/shipped`, `/status`, and the `/worktree-*` family as skills — into a target CLAUDE.md. The canonical set is hardcoded below; **when you fork this skill, edit the canonical list to match your own workbench.** This is not a generic "document any MCP" tool.

When a new workbench MCP or skill lands (or one is retired), edit the canonical set in this skill and re-run on every CLAUDE.md that already has the section — markers make refreshes idempotent.

## When to use

User-facing signals:
- "add the workbench section to this CLAUDE.md"
- "document the dev MCPs in this repo"
- "refresh the workbench section — new MCP / new skill"
- Onboarding a fresh repo where CLAUDE.md was just initialized via `/init` and lacks the workbench context
- Any explicit invocation: `/dev-workbench`

Don't use for:
- Authoring or rewriting the rest of CLAUDE.md (use `/init` for greenfield, hand-edit for existing). This skill only owns the section between its markers.
- Documenting MCPs that aren't in the canonical set below. Those aren't part of the curated dev-workflow infra and don't belong in this section.

## The canonical workbench (hardcoded, not discovered)

This is the maintainer's set — when you fork the skill for your portfolio, replace these with yours.

**MCP servers** (in workflow order, dossier-first):

1. **dossier** — project memory plane. Markdown-on-disk corpus, MCP server in Rust.
2. **ship** — workflow execution: hands task doc to cursor, persists run, lets you inspect/cancel/replay. TypeScript.
3. **huddle** — multi-agent / multi-seat coordination via Slack channels + per-seat keys.
4. **playwright** — browser automation (Playwright MCP plugin).

**Skills** (in workflow order — driver + recap first, then infrastructure):

1. **/work-driver** — drive agent-led impl end-to-end (one or N parallel streams: fan out → poll → land → review → merge → cleanup).
2. **/work-driver-prep** — spec docs + batched plan from a backlog of dossier tasks. Pairs with `/work-driver`.
3. **/shipped** — retrospective recap after a chunk of work lands: PRs merged + weighted-LOC, dossier task closures, chips filed, what's open, next moves. Pairs as the natural post-`/work-driver` follow-up.
4. **/status** — tight 4-section in-flight status update (What happened / What's next / What I recommend / What I need from you). Mid-session counterpart to `/shipped`.
5. **/worktree-add** — create a secondary worktree (`git worktree add` under `.claude/worktrees/<branch>/`).
6. **/worktree-list** — list worktrees with dirty state + optional PR/CI status.
7. **/worktree-remove** — remove a secondary worktree with dirty-state handling.
8. **/worktree-transfer** — move a secondary worktree's branch back into root.
9. **/worktree-where** — report which worktree + branch the current session is on.

**Explicitly NOT in the workbench section**:

- Orchestration tools currently parked / not in active rotation. When/if one re-enters the active workbench, add it here.
- Utility-tier MCPs (Neon, computer-use, ccd_session, anthropic-skills:*, claude-in-chrome, MCP registry, etc.) — not dev-workflow infra.
- Any other skill that isn't directly about the agent-led impl flow (`init`, `update-config`, etc. are useful but live outside the workbench framing).

## Steps

### 1. Locate target + sanity check

Resolve the target path (arg or `./CLAUDE.md`). Bail clearly if:
- File doesn't exist → suggest `/init` first
- File isn't named `CLAUDE.md` (case-insensitive) → ask via `AskUserQuestion` whether to proceed (some repos use `AGENTS.md`)
- Repo root has no `.git` → ask whether to proceed

Read current content into memory; you'll diff against it later.

### 2. Detect existing section + choose insert point

Search for `<!-- BEGIN dev-workbench -->` and `<!-- END dev-workbench -->` markers.

- **Markers present**: capture current content between them; this is a refresh path. Don't touch anything outside the markers.
- **Markers absent but a `## Dev workbench` / `## Development workbench` heading exists**: surface to the operator. Offer (a) wrap the existing section in markers as-is and stop (lets operator re-run later for refresh), (b) replace the existing section with a freshly-generated one, (c) abort. Default recommendation: (a) — preserves hand-curated content already there.
- **Neither present**: pick insert point in this priority order:
  1. After `## State` (or `## Status`) if present
  2. Before `## Architecture` if present
  3. Before the first `## Develop` / `## Development` heading if present
  4. End of file (before any `## Source material` / `## How <X> fits` trailing sections)

### 3. Generate the section content

Use the canonical set from above. For each MCP and each skill, author the block per the shapes below. Pull verb signatures + concrete signals from each source repo's own CLAUDE.md / README (for the MCP servers) or from the skill source (for skills). Fetch live tool schemas via `ToolSearch` when in doubt about an exact signature — don't fabricate.

**Per-MCP block shape**:

```
### <name> — <one-line purpose>

<2-3 sentence elaboration: what it owns, what it doesn't, why it's distinct from the others in the workbench>

**Use proactively for:**

- *"<signal phrase from the user>"* → `<verb / invocation>`
- *"<another signal>"* → `<another verb>`
- ...

**Don't use for:**

- <exclusion that operators routinely confuse with this MCP>
- ...
```

**Per-skill block shape**:

```
### `/<name>` — <one-line purpose>

<2-3 sentences: what the skill orchestrates, what it doesn't do>

**Triggers:** "<phrase 1>", "<phrase 2>", explicit `/<name>` invocation.

**Pair with:** `/<other-skill>` when <condition>.
```

For the five `/worktree-*` skills, render them as a single grouped subsection rather than five near-identical blocks — they're a coherent family. Use this shape:

```
### `/worktree-*` — manage secondary git worktrees

Thin skill family over plain `git worktree`. Use these instead of reaching for an MCP — they cover the verbs that mattered (add, list, remove, transfer, where) without an external state store.

- **`/worktree-add`** — *"spin up a worktree for <ticket>"* → creates `.claude/worktrees/<branch>/`, copies untracked CLAUDE.md if present
- **`/worktree-list`** — *"what worktrees do I have"* → branch, dirty state, optional PR/CI from `gh`
- **`/worktree-remove`** — *"clean up the worktree"* → dirty-state aware (commit-WIP / stash / discard)
- **`/worktree-transfer`** — *"bring this work over to main"* → removes secondary, checks out branch in root
- **`/worktree-where`** — *"where am I"* → which worktree, branch, and cwd this session is pointing at
```

After all per-tool blocks, write one closing subsection:

```
### The loop

<ASCII diagram showing how the canonical set chains end-to-end:
dossier task → /worktree-add → ship run → /work-driver coordinates →
PR → review → merge → dossier close-out + /worktree-remove (or /worktree-transfer).>
```

And one short rationale subsection:

```
### Why this shape

<3-5 sentences: each layer is independently swappable; dossier could be Linear,
the worktree skills could be hand-rolled `git worktree` calls, ship could be a
different agent runner. The seams are deliberate — substituting one doesn't
ripple into the others.>
```

**Voice + tone**: match the existing CLAUDE.md's style. Direct + terse — operator-facing instructions, not marketing copy.

**Per-repo adaptation**: if the target repo IS one of the canonical MCPs (e.g. running `/dev-workbench` inside a repo whose name matches one of the canonical MCP slugs), the description of THAT MCP should call out the dogfood relationship inline. Example: inside the `dossier` repo, the dossier block opens with *"**This is dossier — the project-memory plane itself** — so the dossier verbs are the most directly relevant when working in this repo."* Same pattern for the other MCP source repos. For any other repo: no dogfood call-out; the intro is just "Several MCP servers + skills are available in any Claude session on this machine..."

**Time-sensitive notes**: if a workbench MCP currently has a known issue worth flagging, include it inline as a dated `**Note (YYYY-MM-DD):**` so future re-runs naturally update it (or drop it if the issue is gone). Don't omit — future sessions need to know about live friction.

### 4. Assemble + insert between markers

Wrap the generated content:

```
<!-- BEGIN dev-workbench (managed by /dev-workbench skill — re-run to refresh; hand-edits inside this block will be overwritten) -->
## Dev workbench

<intro paragraph: 1-2 sentences setting context, with the dogfood call-out if applicable>

<per-MCP blocks in canonical order: dossier, ship, huddle, playwright>

<per-skill blocks: /work-driver, /work-driver-prep, /shipped, /status, then the grouped /worktree-* subsection>

### The loop

<diagram>

### Why this shape

<rationale>
<!-- END dev-workbench -->
```

Insert at the location determined in step 2 (or replace existing marker block in the refresh case).

### 5. Diff + confirm before writing

Show the operator a unified diff of the changes (`git diff --no-index <old> <new>` against a temp file if needed). Then `AskUserQuestion`:
- **Write** (recommended) → save the file
- **Edit then write** → operator hand-tweaks; surface the proposed content, take edits, write
- **Abort** → discard

Don't write without confirmation. The diff step is what makes the skill idempotent-safe across re-runs.

### 6. Report

After write, report:
- File path + line range of the new/updated section
- Summary: "Added 4 MCP blocks + 4 standalone skill blocks + 1 grouped worktree-* block. Repo-specific dogfood call-out: <dossier|ship|huddle|none>."
- Any time-sensitive notes embedded (so the operator can grep for them in 6 months and decide if they're still relevant)

## Updating the canonical set

When the workbench evolves:

- **New MCP lands**: add to the canonical list in this skill, append a per-MCP block template if its shape diverges from the standard, then re-run on every CLAUDE.md that has the markers.
- **Skill added/retired**: same — update the canonical list here, refresh in place.
- **Time-sensitive note resolves**: re-run to regenerate without the dated note.

Treat THIS SKILL's canonical list as the single source of truth for the portfolio's workbench. Don't auto-discover; don't hand-curate per-repo fragments. Edit here, re-run everywhere.

## Key reminders

- **Opinionated, not generic.** The canonical set is fixed for the maintainer's portfolio. Don't add anti-set MCPs even if the operator's `~/.claude.json` has them — that's a different tier.
- **Idempotent via markers.** Always wrap output in `<!-- BEGIN dev-workbench -->` / `<!-- END dev-workbench -->`. Re-runs detect + replace; never duplicate.
- **Don't touch content outside the markers.** This skill owns one section.
- **Same shape across repos.** Per-repo customization is the dogfood call-out only — the canonical set, block shapes, and closing sections are identical everywhere.
- **Confirm before write.** Diff + AskUserQuestion is the safety net.
- **Pull verb signatures from source, don't fabricate.** When uncertain, `ToolSearch` for the live schema or read the source repo's CLAUDE.md (or the relevant skill's SKILL.md).

## Anti-patterns

- Don't ask the operator "which MCPs do you want?" — the set is canonical. The only thing worth asking is the diff-confirm in step 5.
- Don't auto-discover from `~/.claude.json` MCP servers — config sources are fragmented and noisy, and the canonical workbench tier is a curated subset anyway.
- Don't write generic descriptions ("dossier tracks tasks") when the source CLAUDE.md says something sharper ("dossier is project memory for the solo developer — one place to track design docs, TDDs, and task notes across a portfolio"). Pull from the source repo.
- Don't include MCPs from the explicit-NOT list even when they're present in this session's tool list.
- Don't run on a CLAUDE.md that lacks any standard headings without picking a sensible insert point. Falling back to "end of file" is fine; silently appending to a structureless file isn't.

## Outcome

After running, the target CLAUDE.md has a `## Dev workbench` section between guarded markers, with the canonical portfolio workbench listed in canonical order, in the same shape as every other CLAUDE.md in the portfolio. Re-runs refresh the section in place when the workbench evolves. The "what tools do I have in this repo?" question is answered by a 30-second scroll, identically across every repo.
