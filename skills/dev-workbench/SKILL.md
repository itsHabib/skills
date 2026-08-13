---
name: dev-workbench
description: >-
  Scaffold (or refresh) a compact `## Dev workbench` section in a repo's
  `CLAUDE.md` and `AGENTS.md` — a COMPOSITIONAL map of the operator's portfolio workbench (MCPs
  dossier/ship + the workbench planes gate [flagship] / flare / console /
  escalate + the work-driver / pr-risk / review-coordinator / consult / shipped
  / status / wip / worktree-* skills; channel/playwright optional), NOT an
  exhaustive per-verb manual. The harness already injects each tool's
  description + signature into every session; this section captures only what
  injection can't give: the roster (one line each), the end-to-end loop, the
  seams, the five-plane shape underneath, and the behavioral nudge ("call the
  verb, don't ask"). Same shape across every repo. Idempotent re-run between
  guarded markers. Use when onboarding a fresh repo, when the workbench's
  composition changes, or when existing agent guidance is missing the
  workbench map.
argument-hint: "[path/to/CLAUDE.md|AGENTS.md] — no argument updates every existing root entrypoint"
user_invocable: true
---

# /dev-workbench — scaffold the workbench MAP into agent guidance

**This skill is portfolio-specific.** It documents the operator's dev-workflow infrastructure — dossier, ship as MCPs; the artifact-coupled workbench planes: gate (the flagship), flare, console, escalate; `/work-driver`, `/pr-risk`, `/review-coordinator`, `/consult`, `/shipped`, `/status`, `/wip`, and the `/worktree-*` family as skills; channel + playwright optional (channel supersedes huddle) — into the repo's agent entrypoints. The canonical set is hardcoded below; this is not a generic "document any MCP" tool.

## The core principle: map, not manual

The harness already injects each tool's full description + signature into every session — every skill's `description`, every MCP tool's schema, always current. So this section must **not** restate verb signatures or trigger-phrase lists: that's a redundant, staler second copy of what the model already has, it needs a per-repo edit every time a skill changes, and it renders as a wall nobody reads. (It also fights "cores stay minimal; grow naturally" and "opinionated, not generic.")

The section's job is to carry **only what injection cannot**:

1. **The roster** — one line per tool: name + the single sentence of what it owns. Answers "what's in the workbench?" at a glance and serves the read-outside-a-session case (someone browsing the repo on GitHub). NOT verb signatures — those are injected.
2. **The loop** — how the pieces chain end-to-end (the diagram). This is genuinely absent from per-tool injection; it's the compositional knowledge.
3. **The seams** — why the layers are separable / swappable, and which tool owns which responsibility (so an agent doesn't reach for the wrong one). Includes the non-obvious "reach for X not Y" calls.
4. **The nudge** — the behavioral instruction ("when the signal matches, call the verb; don't ask permission") + the dogfood call-out when the repo IS a workbench tool.

If a line you're about to write is a verb signature or a trigger-phrase list, **cut it** — the harness already said it. If it's about how tools *compose* or *which to reach for*, keep it.

Target: the rendered section is **~65-80 lines**. Roster is terse; the loop + seams earn the space. If it's drifting past ~100, it's slipping back into per-verb blocks — pull back.

## When to use

User-facing signals:
- "add the workbench section to the agent guides"
- "document the dev workbench in this repo"
- "refresh the workbench section — composition changed"
- Onboarding a fresh repo whose `CLAUDE.md` or `AGENTS.md` lacks the workbench map
- Any explicit invocation: `/dev-workbench`

Don't use for:
- Authoring the rest of an agent guide (use the harness initializer for greenfield, hand-edit otherwise). This skill owns only the marked section.
- Re-documenting individual verb signatures — that's the harness's job, not this section's.
- Documenting non-workbench MCPs (Neon, computer-use, ccd_session, anthropic-skills:*) — different tier.

## The canonical workbench (hardcoded, not discovered)

`<portfolio-root>` below is the operator's portfolio root — resolve it to the first of
`$PORTFOLIO_ROOT`, `~/dev`, `~/pers` that exists; never emit a hardcoded absolute root
into a generated section.

**MCP servers** (in-session, workflow order, dossier-first):

1. **dossier** — durable project memory: projects → phases → tasks → artifacts, markdown-on-disk. The State substrate's work-item incumbent. Source: `<portfolio-root>/dossier/`.
2. **ship** — the driver engine: dispatch a task to a cloud/local agent and persist the run (dispatch→poll→judgment→land→record); inspect/cancel/replay. The Execution plane. Source: `<portfolio-root>/ship/`.
3. **channel** — *optional* agent message bus: append-only JSONL channels under `~/.channel`, CLI + MCP (`channel.post/read/list`), self-declared identity, no lifecycle. Supersedes huddle (Slack-backed, retired from the map). Source: `<portfolio-root>/channel/`.
4. **playwright** — browser automation when a task needs a real DOM (supporting).

**Planes** (workbench tenants — CLIs coupled by exit codes + JSONL artifacts, NOT MCPs, NOT skills; all live in `<portfolio-root>/workbench/cmd/<tool>` since the 2026-07-17 monorepo migration):

1. **gate** — the flagship: authorization. Evaluates the exact PR head against an operator-minted grant + the escalate-only verifier ladder, emits governed-path merge authorization into a hash-chained audit log (Verification + Capability). Findings ≠ authorization; gate is the merge boundary. Exit contract: 0 pass / 1 blocked / 2 parked / 3 refused / 4 error. Source: workbench `cmd/gate`; state + keys stay in the gate checkout's `state/` (operational data, never in-repo).
2. **flare** — notification: best-effort escalation sink over authoritative receipts → its own Slack app/channel (Observability). Pure sink; never gates; independent of channel. Source: workbench `cmd/flare`.
3. **console** — a local, read-only web view of gate's inbox: parked runs + the grant ledger. Shells the gate binary for data, never imports it; owns no authoritative state (Observability). Source: workbench `cmd/console`.
4. **escalate** — the agent→human→agent resolution back-channel: ingests the human's decision for a parked escalation and drives `gate resolve`, closing the loop a park opens. A contract + seam, not a plane of its own. Source: workbench `cmd/escalate`.

**Skills** (workflow order):

1. **/work-driver** [+ **/work-driver-prep**] — drive agent-led impl end-to-end (fan out → poll → land → review → merge → cleanup); prep builds specs + the conflict-batched plan. Source: `<portfolio-root>/cc-skills/skills/work-driver*/`.
2. **/pr-risk** — size how much review a PR needs (deterministic floor + agent advisory); upstream of the reviewers — it decides *how much*, they *do* it. Source: `<portfolio-root>/cc-skills/skills/pr-risk/`.
3. **/review-coordinator** [+ **/review-digest**] — the judge over the AI PR reviewers: consolidate codex/claude/cursor/copilot findings into one severity-ranked verdict + block/go gate; digest pre-triages the bot pile locally. (Standalone today; folding into `/work-driver`'s review cycle is planned, not yet wired — don't imply the driver calls it automatically.) Source: `<portfolio-root>/cc-skills/skills/review-coordinator/`.
4. **/shipped** · **/status** · **/wip** — retrospective recap / in-flight update / cross-store live board (Observability views). Source: `<portfolio-root>/cc-skills/skills/{shipped,status,wip}/`.
5. **/consult** — summon another portfolio repo's steward (an ephemeral subagent scoped to that repo) for a same-turn answer to a knowledge question. The stuck-path escalation before the operator; read-only, no side effects. Source: `<portfolio-root>/cc-skills/skills/consult/`.
6. **/worktree-*** — thin family over `git worktree` (add / list / remove / transfer / where). Source: `<portfolio-root>/cc-skills/skills/worktree-*/`.

**The five-plane shape** (the redesign's contract taxonomy the block names at the end): **State** (dossier + gate's hash-chained log + run/verdict/grant/receipt artifacts) · **Execution** (ship's driver) · **Verification** (the escalate-only ladder — gate's reducer, review-coordinator, triage/tracelens) · **Capability** (scoped/timed grants) · **Observability** (flare, console, /wip, /shipped, /status). The sixth, **Composition** — the agent + thin policy — is this section itself. gate is the flagship: the one tool that spans Verification + Capability and holds the merge boundary.

**Explicitly NOT in the section**:

- `orchestra` — DAG runner; parked / not in the active flow (2026-04 pivot). Add when/if it re-enters.
- `Neon`, `computer-use`, `ccd_session`, `anthropic-skills:*`, `claude-in-chrome`, MCP registry, etc. — utility tier, not dev-workflow infra.
- Standalone skills outside the impl flow (`init`, `update-config`, `simplify`, `eng-philo`, `subagent-scaffold`, etc.) — useful but not the workbench composition.

## Steps

### 1. Locate target + sanity check

With an explicit path, target that one file. With no argument, target every
existing root `CLAUDE.md` and `AGENTS.md`; when both exist, the managed block
must be byte-identical in both. Bail clearly if:
- Neither entrypoint exists → suggest initializing both first.
- Not named `CLAUDE.md` or `AGENTS.md` (case-insensitive) → ask the operator whether to proceed.
- Repo root has no `.git` → ask whether to proceed.

Read every target's current content; you'll diff each later.

### 2. Detect existing section + choose insert point

Search for `<!-- BEGIN dev-workbench -->` / `<!-- END dev-workbench -->`.

- **Markers present**: refresh path — replace between them, touch nothing outside. **If the existing block is a long per-verb section, the refresh shrinks it** — expected; the diff in step 5 will be large and mostly deletions. Say so.
- **A `## Dev workbench` heading but no markers**: surface to operator. Offer (a) wrap as-is + stop, (b) replace with the compositional shape, (c) abort. Default rec: **(b)** now — the whole point of this version is to replace verbose hand-rolled sections.
- **Neither**: insert after `## State`/`## Status` if present; else before `## Architecture`; else before first `## Develop*`; else end of file (before trailing `## Source material`).

### 3. Generate the section content (the compositional shape)

Locate `render-block.sh` beside this loaded `SKILL.md` and render the canonical block:

```bash
repo_root=<confirmed-repository-directory>
bash <this-skill-directory>/render-block.sh --repo "$(basename "$repo_root")"
```

Use that output byte-for-byte for every target in the repo. The renderer owns the shared
wording and repo-specific dogfood callout; this skill owns placement and operator review.
Do not hand-compose a near-copy. The deterministic renderer is what makes the Claude and
Codex entrypoints, and separate runs of this skill, converge.

The rendered block contains these parts, in order. Keep any future renderer change tight —
roster lines are ONE line each.

**(a) Intro + nudge** (2-4 sentences):
- One sentence: "these MCPs + skills are available in any agent session on this machine; the harness injects each tool's signature, so this section is the *map* — how they compose — not the per-verb manual."
- The nudge: "when the signal matches, just call the verb; don't ask permission."
- The escalation ladder: "stuck on a *knowledge* question about another portfolio repo → `/consult` its steward; only *authority* questions (direction, spend, irreversible calls) go to the operator."
- The dogfood call-out IF the repo is itself a workbench tool (see step 3e).

**(b) Roster** — two short lists, one line per entry. Format:

```
**MCPs (in-session):**
- **dossier** — durable project memory: projects → phases → tasks → artifacts (markdown-on-disk).
- **ship** — the driver engine: dispatch a task to a cloud/local agent and persist the run (dispatch→poll→judgment→land→record); inspect/cancel/replay.
- **channel** — *optional* agent message bus (append-only JSONL, `channel.post/read/list`); post/read to coordinate with peer agents or leave word for the operator; off the normal PR path.
- **playwright** — browser automation when a task needs a real DOM.

**Planes (workbench tenants — CLIs composed via exit codes + JSONL, not MCPs):**
- **gate** — the flagship: authorization. Evaluates the *exact* PR head against an operator-minted grant + the escalate-only verifier ladder; hash-chained audit log; exit 0 pass / 1 blocked / 2 parked / 3 refused / 4 error. Findings ≠ authorization; gate is the merge boundary.
- **flare** — notification: best-effort escalation sink over authoritative receipts → its own Slack app/channel. Pure sink; never gates; independent of channel.
- **console** — read-only local web view of gate's inbox (parked runs + grant ledger); shells the gate binary, owns no authoritative state.
- **escalate** — the agent→human→agent back-channel: ingests the human's decision for a parked escalation and drives `gate resolve`.

**Skills:**
- **/work-driver** [+ **/work-driver-prep**] — drive agent-led impl end-to-end; prep builds the specs + conflict-batched plan.
- **/pr-risk** — size how much review a PR needs (deterministic floor + agent advisory); upstream of the reviewers — it decides *how much*, they *do* it.
- **/review-coordinator** [+ **/review-digest**] — consolidate the AI PR reviewers into one verdict (the judge over the finders); digest pre-triages the bot pile locally.
- **/shipped** · **/status** · **/wip** — retrospective recap · in-flight update · cross-store live board.
- **/consult** — summon a sibling repo's steward for a same-turn answer; knowledge → peer, authority → operator.
- **/worktree-*** — add · list · remove · transfer · where, over `git worktree`.
```

No verb signatures, no trigger lists. One line, what-it-owns only. (The reader who needs the signature already has it injected; the reader browsing on GitHub needs the one-liner.)

**(c) The loop** — the end-to-end diagram. THIS is the highest-value part (injection never shows composition). Render the chain:

```
dossier task → /worktree-add → spec → ship driver (cloud-first: dispatch→poll→judgment→land→record)
   → PR + CI → /pr-risk tiers it → reviewers fire → /review-coordinator → one verdict
   → gate evaluates the exact head → 0: governed-path authorization → merge
   → authoritative receipts → dossier close-out → /worktree-remove
        ↘ 2: gate PARKS → console / gate next surface it → human decides → escalate → gate resolve → re-judge
        ↘ any attention/terminal receipt → best-effort flare sweep → Slack   (independent; never gates)
```

Keep it readable; a compact ASCII flow is fine. Annotate the one or two steps `/work-driver` automates — and scope that annotation to what the driver *actually* does today (it runs its own review triage inline). **Place `/review-coordinator` at the review step as a step you can invoke**, not as something the driver calls for you — the driver→coordinator wiring is planned, not built, so the rendered loop must not imply automatic delegation. (When that integration lands, update this annotation.)

**(d) The seams** (3-6 sentences, the swappability rationale): each layer is independently substitutable and owns one responsibility — dossier owns "what needs doing" (could be Linear), worktree skills own "where work happens", ship owns "drive an agent + persist the run", pr-risk owns "how much review a change needs", review-coordinator owns "consolidate the finders" (the bots are swappable finders under it), **gate owns authorization — is this exact head allowed to merge — which is not the reviewers' findings**, **escalate owns resolution — closing the agent→human→agent loop a park opens, without ever deciding for the human**, **console owns the read-only view of gate's inbox — it explains, never decides (shells the binary, owns no authoritative state)**, **flare owns notification — a best-effort sink on authoritative receipts, its own Slack app, never gating and never built on channel**, consult owns the stuck path, channel owns optional agent-to-agent messaging (superseding huddle), playwright owns browser. Substituting one doesn't ripple. End with: "the workbench is a menu, not a checklist — skip what a given flow doesn't need."

**(f) The shape underneath** (the five-plane close): after the seams, name the redesign's contract planes the tools instantiate — **State** (dossier + gate's hash-chained log + run/verdict/grant/receipt artifacts) · **Execution** (ship's driver) · **Verification** (the escalate-only ladder: deterministic floor → local → premium; gate's reducer, review-coordinator, triage/tracelens) · **Capability** (scoped/timed grants; every effectful verb needs a live grant + a supporting verdict) · **Observability** (read-only, storeless views: flare, console, /wip, /shipped, /status) — coupled only by typed artifacts (`evidence → verdict → action`), never call stacks; note this section itself is the sixth, **Composition**. The block's boundary lines *are* the plane laws.

**(e) Dogfood call-out** (only if the repo IS a canonical tool): inline in the intro, e.g. inside the `ship` checkout: *"**This is ship — the execution plane itself** — so the ship verbs are the most directly relevant here."* Inside the `dossier` and `channel` checkouts, same pattern. Inside `cc-skills`/`skills` (the skill registries): *"**This is the skills registry** — the workbench skills live here; editing one ships it portfolio-wide via sync."* Otherwise no call-out.

**Voice**: match the repo's agent guidance. Terse, lowercase technical errors, operator-facing — not marketing. **Resist re-expanding** any entry into a full block; if you feel the urge to add a verb signature, that's the harness's job.

**Time-sensitive notes**: if a workbench tool has live friction worth flagging (dated `**Note (YYYY-MM-DD):**`), put it in the seams prose, not as a per-tool block. Drop it on the next refresh once resolved.

### 4. Assemble + insert between markers

The renderer output already includes exactly one complete marker pair. Replace an existing
managed block with that output, or insert it at the Step 2 location. Do not wrap it again.

### 5. Diff + confirm before writing

Locate `plan-block.sh` beside this loaded `SKILL.md` and show its complete output:

```bash
repo_root=<confirmed-repository-directory>
bash <this-skill-directory>/plan-block.sh --repo-dir "$repo_root"
```

When the operator explicitly selected one guide, add `--guide <that-path>` so
the preview contains only the authorized target.

If the refresh shrinks a long per-verb section, **say so explicitly** ("this replaces a long
per-verb section with a compact compositional map; the deleted verb signatures are injected by
the harness, so nothing is lost"). Ask through the harness's available user-input surface:
**Write all** (recommended) / **Edit then write** / **Abort**. Never update only one member of
an existing pair unless the operator explicitly narrows the target.

### 6. Report

- File paths + new line ranges (and the before→after line-count delta — the shrink is the headline).
- What's in the section: roster (N MCPs + M skills), the loop, the seams; dogfood call-out (which tool | none).
- Any dated time-sensitive note embedded.

## Updating the canonical set

When the workbench evolves, edit the canonical list in THIS skill, then re-run on every `CLAUDE.md`/`AGENTS.md` pair with the markers. But first ask: **does this change the composition, or just add a tool?**

- **Composition change** (a new tool changes the loop or a seam — e.g. review-coordinator slotting into the review step): update the loop diagram + seams + add a one-line roster entry. This earns a refresh everywhere.
- **Tool added that doesn't change any flow**: a one-line roster entry only. Do NOT add a block, a signature, or a trigger list. If it doesn't touch the loop or a seam, it barely earns the roster line — consider whether it belongs in the workbench framing at all.
- **Time-sensitive note resolves**: re-run to drop the dated note.

Treat THIS skill's canonical list + loop as the single source of truth. Don't auto-discover; don't hand-curate per-repo fragments.

## Key reminders

- **Map, not manual.** The harness injects every verb signature + skill description already. This section is the composition (roster + loop + seams + nudge) — the part injection can't give. Cutting a verb signature is correct, not lossy.
- **~65-80 lines.** If the rendered section is creeping long, you're re-expanding into per-verb blocks. Stop.
- **New skills enter via the loop/roster, not a block.** review-coordinator is represented as a loop step + a one-line roster entry — that's the template for every future addition.
- **Opinionated, not generic.** Canonical set is fixed. Don't add anti-set tools (Neon, computer-use) even if present in the session.
- **Idempotent via markers.** Always wrap output. Re-runs replace; never duplicate.
- **Don't touch content outside the markers.**
- **Confirm before write** (diff + an explicit operator choice).

## Anti-patterns

- **Don't render per-tool verb blocks.** They duplicate the harness's injected schemas with a staler copy — the single biggest way this section goes wrong.
- **Don't list trigger phrases.** A skill's `description` (injected) already carries its triggers. Listing them here is the same redundancy in a worse place.
- Don't ask "which MCPs do you want?" — the set is canonical.
- Don't auto-discover from `~/.claude.json` — fragmented + noisy, and the workbench is a curated subset.
- Don't include anti-set tools (orchestra, Neon, ccd, anthropic-skills:*) even when in the session tool list.
- Don't re-expand a roster line into a paragraph "to be helpful" — the help is the loop + seams, not a second copy of the manual.

## Outcome

Every existing root agent entrypoint has the same compact `## Dev workbench` section between guarded markers: a one-line roster, the end-to-end loop, and the swappability seams — the *compositional* knowledge the harness's per-tool injection can't provide. Same shape across every repo, ~65-80 lines. Re-runs refresh in place; a long per-verb section shrinks on the next run. "What's in the workbench and how does it chain?" is answered in a 20-second scroll; "what are this verb's args?" is answered by the harness, where it belongs.
