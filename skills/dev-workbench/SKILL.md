---
name: dev-workbench
description: Scaffold (or refresh) a compact `## Dev workbench` section in a repo's CLAUDE.md — a COMPOSITIONAL map of the operator's portfolio workbench (MCPs dossier/ship/huddle/playwright + the work-driver / review-coordinator / consult / shipped / status / worktree-* skills), NOT an exhaustive per-verb manual. The harness already injects each tool's description + signature into every session; this section captures only what injection can't give: the roster (one line each), the end-to-end loop, the seams, and the behavioral nudge ("call the verb, don't ask"). Same shape across every repo. Idempotent re-run between guarded markers. Use when onboarding a fresh repo, when the workbench's composition changes, or when an existing repo's CLAUDE.md is missing the workbench map.
argument-hint: "[path/to/CLAUDE.md] — defaults to ./CLAUDE.md at repo root"
user_invocable: true
---

# /dev-workbench — scaffold the workbench MAP into a CLAUDE.md

**This skill is portfolio-specific.** It documents the operator's dev-workflow infrastructure — dossier, ship, huddle, playwright as MCPs; `/work-driver`, `/work-driver-prep`, `/review-coordinator`, `/consult`, `/shipped`, `/status`, and the `/worktree-*` family as skills — into a target CLAUDE.md. The canonical set is hardcoded below; this is not a generic "document any MCP" tool.

## The core principle: map, not manual

The harness already injects each tool's full description + signature into every session — every skill's `description`, every MCP tool's schema, always current. So this section must **not** restate verb signatures or trigger-phrase lists: that's a redundant, staler second copy of what the model already has, it needs a per-repo edit every time a skill changes, and it renders as a wall nobody reads. (It also fights "cores stay minimal; grow naturally" and "opinionated, not generic.")

The section's job is to carry **only what injection cannot**:

1. **The roster** — one line per tool: name + the single sentence of what it owns. Answers "what's in the workbench?" at a glance and serves the read-outside-a-session case (someone browsing the repo on GitHub). NOT verb signatures — those are injected.
2. **The loop** — how the pieces chain end-to-end (the diagram). This is genuinely absent from per-tool injection; it's the compositional knowledge.
3. **The seams** — why the layers are separable / swappable, and which tool owns which responsibility (so an agent doesn't reach for the wrong one). Includes the non-obvious "reach for X not Y" calls.
4. **The nudge** — the behavioral instruction ("when the signal matches, call the verb; don't ask permission") + the dogfood call-out when the repo IS a workbench tool.

If a line you're about to write is a verb signature or a trigger-phrase list, **cut it** — the harness already said it. If it's about how tools *compose* or *which to reach for*, keep it.

Target: the rendered section is **~50-70 lines**. Roster is terse; the loop + seams earn the space. If it's drifting past ~100, it's slipping back into per-verb blocks — pull back.

## When to use

User-facing signals:
- "add the workbench section to this CLAUDE.md"
- "document the dev workbench in this repo"
- "refresh the workbench section — composition changed"
- Onboarding a fresh repo where CLAUDE.md was just `/init`-ed and lacks the workbench map
- Any explicit invocation: `/dev-workbench`

Don't use for:
- Authoring the rest of CLAUDE.md (use `/init` for greenfield, hand-edit otherwise). This skill owns only the marked section.
- Re-documenting individual verb signatures — that's the harness's job, not this section's.
- Documenting non-workbench MCPs (Neon, computer-use, ccd_session, anthropic-skills:*) — different tier.

## The canonical workbench (hardcoded, not discovered)

**MCP servers** (workflow order, dossier-first):

1. **dossier** — project memory: projects → phases → tasks → artifacts, markdown-on-disk. Source: `~/projects/dossier/`.
2. **ship** — workflow execution: hands a task doc to cursor, persists the run, lets you inspect/cancel/replay. Source: `~/projects/ship/`.
3. **huddle** — multi-agent / multi-seat coordination via Slack channels + per-seat keys. Source: `~/projects/huddle/`.
4. **playwright** — browser automation (Playwright MCP plugin).

**Skills** (workflow order):

1. **/work-driver** — drive agent-led impl end-to-end (one or N streams: fan out → poll → land → review → merge → cleanup). Source: `~/.claude/skills/work-driver/`.
2. **/work-driver-prep** — spec docs + batched plan from a backlog of dossier tasks. Pairs with `/work-driver`. Source: `~/.claude/skills/work-driver-prep/`.
3. **/review-coordinator** — the judge over the AI PR reviewers: consolidate codex/claude/cursor/copilot findings on a PR into one severity-ranked verdict + block/go gate. Invoke at the review step to get one verdict instead of reading four comment streams. (Standalone today; folding it into `/work-driver`'s review cycle is a planned step, not yet wired — don't imply the driver calls it automatically.) Source: `~/.claude/skills/review-coordinator/`.
4. **/shipped** — retrospective recap after a chunk lands (PRs + weighted-LOC, dossier closures, friction delta, what's open). Post-`/work-driver` follow-up. Source: `~/.claude/skills/shipped/`.
5. **/status** — tight 4-section in-flight status update. Mid-session counterpart to `/shipped`. Source: `~/.claude/skills/status/`.
6. **/consult** — summon another portfolio repo's steward (an ephemeral subagent scoped to that repo) for a same-turn answer to a knowledge question. The stuck-path escalation before the operator; read-only, no side effects. Source: `~/.claude/skills/consult/`.
7. **/worktree-*** — thin family over `git worktree` (add / list / remove / transfer / where). Source: `~/.claude/skills/worktree-*/`.

**Explicitly NOT in the section**:

- `orchestra` — DAG runner; parked / not in the active flow (2026-04 pivot). Add when/if it re-enters.
- `Neon`, `computer-use`, `ccd_session`, `anthropic-skills:*`, `claude-in-chrome`, MCP registry, etc. — utility tier, not dev-workflow infra.
- Standalone skills outside the impl flow (`init`, `update-config`, `simplify`, `eng-philo`, `subagent-scaffold`, etc.) — useful but not the workbench composition.

## Steps

### 1. Locate target + sanity check

Resolve the path (arg or `./CLAUDE.md`). Bail clearly if:
- File doesn't exist → suggest `/init` first.
- Not named `CLAUDE.md` (case-insensitive) → ask via `AskUserQuestion` (some repos use `AGENTS.md`).
- Repo root has no `.git` → ask whether to proceed.

Read current content; you'll diff later.

### 2. Detect existing section + choose insert point

Search for `<!-- BEGIN dev-workbench -->` / `<!-- END dev-workbench -->`.

- **Markers present**: refresh path — replace between them, touch nothing outside. **If the existing block is a long per-verb section, the refresh shrinks it** — expected; the diff in step 5 will be large and mostly deletions. Say so.
- **A `## Dev workbench` heading but no markers**: surface to operator. Offer (a) wrap as-is + stop, (b) replace with the compositional shape, (c) abort. Default rec: **(b)** now — the whole point of this version is to replace verbose hand-rolled sections.
- **Neither**: insert after `## State`/`## Status` if present; else before `## Architecture`; else before first `## Develop*`; else end of file (before trailing `## Source material`).

### 3. Generate the section content (the compositional shape)

Assemble these parts, in order. Keep it tight — roster lines are ONE line each.

**(a) Intro + nudge** (2-4 sentences):
- One sentence: "these MCPs + skills are available in any Claude session on this machine; the harness injects each tool's signature, so this section is the *map* — how they compose — not the per-verb manual."
- The nudge: "when the signal matches, just call the verb; don't ask permission."
- The escalation ladder: "stuck on a *knowledge* question about another portfolio repo → `/consult` its steward; only *authority* questions (direction, spend, irreversible calls) go to the operator."
- The dogfood call-out IF the repo is itself a workbench tool (see step 3e).

**(b) Roster** — two short lists, one line per entry. Format:

```
**MCPs:**
- **dossier** — project memory: projects → phases → tasks → artifacts.
- **ship** — hand a task doc to cursor, persist/inspect/replay the run.
- **huddle** — multi-seat coordination channels (Slack-backed).
- **playwright** — browser automation when a task needs a real DOM.

**Skills:**
- **/work-driver** [+ **/work-driver-prep**] — drive agent-led impl end-to-end; prep builds the specs + batches.
- **/review-coordinator** — consolidate the AI PR reviewers into one verdict + merge gate (the judge over the finders).
- **/shipped** / **/status** — retrospective recap / in-flight update.
- **/consult** — summon a sibling repo's steward for a same-turn answer; knowledge questions go to a peer, authority questions to the operator.
- **/worktree-*** — add · list · remove · transfer · where, over `git worktree`.
```

No verb signatures, no trigger lists. One line, what-it-owns only. (The reader who needs the signature already has it injected; the reader browsing on GitHub needs the one-liner.)

**(c) The loop** — the end-to-end diagram. THIS is the highest-value part (injection never shows composition). Render the chain:

```
dossier task → /worktree-add → write spec → ship run
   → /work-driver coordinates: poll → land → PR
   → reviewers fire → /review-coordinator → verdict + gate
   → merge (dep order) → dossier close-out → /worktree-remove
```

Keep it readable; a compact ASCII flow is fine. Annotate the one or two steps `/work-driver` automates — and scope that annotation to what the driver *actually* does today (it runs its own review triage inline). **Place `/review-coordinator` at the review step as a step you can invoke**, not as something the driver calls for you — the driver→coordinator wiring is planned, not built, so the rendered loop must not imply automatic delegation. (When that integration lands, update this annotation.)

**(d) The seams** (3-6 sentences, the swappability rationale): each layer is independently substitutable and owns one responsibility — dossier owns "what needs doing" (could be Linear), worktree skills own "where work happens", ship owns "drive an agent + persist", review-coordinator owns "consolidate the finders' output" (the four bots are swappable finders under it), consult owns the stuck path (peer knowledge before operator attention), huddle owns multi-seat, playwright owns browser. Substituting one doesn't ripple. End with: "the workbench is a menu, not a checklist — skip what a given flow doesn't need."

**(e) Dogfood call-out** (only if the repo IS a canonical tool): inline in the intro, e.g. inside `~/projects/ship/`: *"**This is ship — the execution plane itself** — so the ship verbs are the most directly relevant here."* Inside `~/projects/dossier/`, `~/projects/huddle/` same pattern. Inside `cc-skills`/`skills` (the skill registries): *"**This is the skills registry** — the workbench skills live here; editing one ships it portfolio-wide via sync."* Otherwise no call-out.

**Voice**: match the repo's CLAUDE.md. Terse, lowercase technical errors, operator-facing — not marketing. **Resist re-expanding** any entry into a full block; if you feel the urge to add a verb signature, that's the harness's job.

**Time-sensitive notes**: if a workbench tool has live friction worth flagging (dated `**Note (YYYY-MM-DD):**`), put it in the seams prose, not as a per-tool block. Drop it on the next refresh once resolved.

### 4. Assemble + insert between markers

```
<!-- BEGIN dev-workbench (managed by /dev-workbench skill — re-run to refresh; hand-edits inside this block will be overwritten) -->
## Dev workbench

<intro + nudge (+ dogfood call-out)>

<roster: MCPs list + Skills list>

### The loop

<diagram>

### Why this shape

<seams / swappability>
<!-- END dev-workbench -->
```

### 5. Diff + confirm before writing

Show a unified diff. If the refresh shrinks a long per-verb section, **say so explicitly** ("this replaces a long per-verb section with a compact compositional map; the deleted verb signatures are auto-injected by the harness, so nothing is lost"). Then `AskUserQuestion`: **Write** (rec) / **Edit then write** / **Abort**. Don't write without confirmation.

### 6. Report

- File path + new line range (and the before→after line-count delta — the shrink is the headline).
- What's in the section: roster (N MCPs + M skills), the loop, the seams; dogfood call-out (which tool | none).
- Any dated time-sensitive note embedded.

## Updating the canonical set

When the workbench evolves, edit the canonical list in THIS skill, then re-run on every CLAUDE.md with the markers. But first ask: **does this change the composition, or just add a tool?**

- **Composition change** (a new tool changes the loop or a seam — e.g. review-coordinator slotting into the review step): update the loop diagram + seams + add a one-line roster entry. This earns a refresh everywhere.
- **Tool added that doesn't change any flow**: a one-line roster entry only. Do NOT add a block, a signature, or a trigger list. If it doesn't touch the loop or a seam, it barely earns the roster line — consider whether it belongs in the workbench framing at all.
- **Time-sensitive note resolves**: re-run to drop the dated note.

Treat THIS skill's canonical list + loop as the single source of truth. Don't auto-discover; don't hand-curate per-repo fragments.

## Key reminders

- **Map, not manual.** The harness injects every verb signature + skill description already. This section is the composition (roster + loop + seams + nudge) — the part injection can't give. Cutting a verb signature is correct, not lossy.
- **~50-70 lines.** If the rendered section is creeping long, you're re-expanding into per-verb blocks. Stop.
- **New skills enter via the loop/roster, not a block.** review-coordinator is represented as a loop step + a one-line roster entry — that's the template for every future addition.
- **Opinionated, not generic.** Canonical set is fixed. Don't add anti-set tools (Neon, computer-use) even if present in the session.
- **Idempotent via markers.** Always wrap output. Re-runs replace; never duplicate.
- **Don't touch content outside the markers.**
- **Confirm before write** (diff + AskUserQuestion).

## Anti-patterns

- **Don't render per-tool verb blocks.** They duplicate the harness's injected schemas with a staler copy — the single biggest way this section goes wrong.
- **Don't list trigger phrases.** A skill's `description` (injected) already carries its triggers. Listing them here is the same redundancy in a worse place.
- Don't ask "which MCPs do you want?" — the set is canonical.
- Don't auto-discover from `~/.claude.json` — fragmented + noisy, and the workbench is a curated subset.
- Don't include anti-set tools (orchestra, Neon, ccd, anthropic-skills:*) even when in the session tool list.
- Don't re-expand a roster line into a paragraph "to be helpful" — the help is the loop + seams, not a second copy of the manual.

## Outcome

The target CLAUDE.md has a compact `## Dev workbench` section between guarded markers: a one-line roster, the end-to-end loop, and the swappability seams — the *compositional* knowledge the harness's per-tool injection can't provide. Same shape across every repo, ~50-70 lines. Re-runs refresh in place; a long per-verb section shrinks on the next run. "What's in the workbench and how does it chain?" is answered in a 20-second scroll; "what are this verb's args?" is answered by the harness, where it belongs.
