# skills

Opinionated dev-workflow skills for [Claude Code](https://claude.com/claude-code).

## Install

**Recommended — [skill-sync](https://github.com/itsHabib/skill-sync):**

```bash
go install github.com/itsHabib/skill-sync@latest

# Clone this repo, then sync its skills/ tree into Claude Code
git clone https://github.com/itsHabib/skills ~/dev/skills
skill-sync sync --source-dir ~/dev/skills/skills --target-dir ~/.claude/skills

# Check for drift any time
skill-sync status --source-dir ~/dev/skills/skills --target-dir ~/.claude/skills
```

Each skill appears as `/<skill-name>` in your next session. Use `skill-sync status` to catch drift before it becomes a problem.

A single canonical skill source also feeds future Managed-Agents drivers (MA loads Agent Skills), so skills stop being machine-local copies.

**No-deps fallback:**

```bash
git clone https://github.com/itsHabib/skills ~/dev/skills
cp -r ~/dev/skills/skills/* ~/.claude/skills/
```

Copy individual dirs if you want a subset.

## Skills

| Skill | What it does |
|---|---|
| `/work-driver` | Drive N parallel tasks to merge through ship's `ship driver` engine (import → dispatch → poll → judgment → land → record). The engine owns the loop; the skill keeps the policy — review-cycle cap, strategy selection, the merge call. |
| `/work-driver-prep` | Turn a backlog of dossier tasks into spec docs + a conflict-aware batched plan. |
| `/work-driver-seed` | Seed a dossier phase + PR-sized, dependency-ordered tasks from a described chunk — the front-end to `/work-driver-prep` for work too big for one task, too small for a `/tdd`. |
| `/drive` | Drive ONE ad-hoc task through the full delivery loop — repo patterns, worktree isolation, local green, PR, review-roster fold-and-converge — then stop at the last safe autonomous point and hand off. The lightweight single-task sibling of `/work-driver`; "done" is whatever you said it is. |
| `/shipped` | Retrospective: PRs merged, weighted-LOC, what's open, next moves. |
| `/status` | In-flight 4-section status (What happened / What's next / What I recommend / What I need). |
| `/skills` | Skill librarian — discover every skill on disk (personal / project / stranded in worktrees) and either lay them all out in a grouped table or recommend the best fit for a task you describe, with the exact command to type. |
| `/worktree-add` | Create a worktree at `.claude/worktrees/<branch>/`. |
| `/worktree-list` | List worktrees with dirty state + PR/CI. |
| `/worktree-remove` | Remove a worktree, dirty-state aware. |
| `/worktree-transfer` | Move a worktree's branch into root. |
| `/worktree-where` | Show current worktree, branch, cwd. |
| `/dev-workbench` | Scaffold a canonical `## Dev workbench` section into a repo's CLAUDE.md. |
| `/eng-philo` | Stamp an opinionated `## Engineering principles` house style (Dave Cheney lineage) into a repo's CLAUDE.md, paired with the lint that enforces it. |
| `/prep-public` | Pre-launch audit: secrets, LICENSE, package metadata, README, `.gitignore`, leaks. |
| `/polish` | Stack-aware portfolio hygiene audit (Rust / Go / Node / Python / Elixir / Ruby). |
| `/floor` | Render the effective Claude Code permission floor — every settings layer + guard hooks merged into one tiered view, with wildcard/asymmetry findings. |
| `/subagent-scaffold` | Write a canonical Cursor subagent set into `.cursor/`. |
| `/chip` | Spin an out-of-scope item out into its own Claude Code session. |
| `/brief` | Explore an unfamiliar code area and produce a code-anchored kickoff doc + a paste-ready handoff prompt for another agent — for POC/exploration handoffs, not a design doc. |
| `/continue` | Emit a paste-ready continuation prompt so a fresh session picks up exactly where this one left off when context fills up. |
| `/transfer-context` | Fork a mid-task thread into its own briefed session without derailing the working agent — thread-scoped and conversation-dependent (vs `/chip`'s fresh task and `/continue`'s whole-session handoff). |
| `/tdd` | Turn a feature idea into a reviewed Technical Design Document plus dossier structure — design doc and rollout tasks in one shot. |
| `/review-coordinator` | Consolidate AI PR reviewers into one deduped verdict and merge gate; the judge over the finders. |
| `/consult` | Summon another repo's steward agent for a same-turn answer — knowledge questions about a sibling repo go to a peer, not the operator. |
| `/interview` | Extract unwritten knowledge from a person via a fillable, resumable interview doc, then synthesize it into a target artifact (deck, design doc, ADR, post-mortem, onboarding guide) in their voice. |
| `/dojo` | Interactive teaching mode — diagnose silently, then drive a Socratic loop where the user runs every fix step themselves (escalating hint ladder, you only ask and verify), and close with a transferable rule + a lessons-ledger scroll. |
| `/ship-ticket` | Chain the post-implementation wrap-up: file the Jira ticket, open the PR, describe it, sync the epic. |
| `/spinup-ticket` | Create a Jira ticket under a given epic via the Jira REST API. |
| `/sync-epic` | Bring a Jira epic's child tickets in line with their GitHub PR states (draft → In Progress, open → In Review, merged → Done). |
| `/write-pr` | Write or update the current PR description in a standard format. |
| `/validation-card` | Produce the evidence CI cannot: run a branch against real infrastructure, write a card where every claim carries its re-runnable command, post it on the tracking issue, link it from the PR. A card that only lists passing tests is not a card. |
| `/ship-feature` | Take a design doc through to a PR with reviews requested — implement on a branch, open the PR, baby-sit CI to green, then address every actionable review comment. |
| `/recover` | After a crash or reboot, reconstruct interrupted Claude Code sessions — scan transcripts, classify done-vs-interrupted, detect dead background jobs, and emit a ranked resume plan with exact `--resume` commands. |
| `/wip` | Standing cross-project board of what's open or in-flight now — joins CI/driver runs, a task store, and open PRs into one liveness-ranked view. |
| `/pr-risk` | Route a PR to the right amount of review — an optional deterministic risk floor plus an escalate-only agent pass, tiered T0–T3. |
| `/review-digest` | Collapse a PR's four-bot comment pile into a line-grouped digest using a local model — each bot's own headline + severity, grouped by file:line. Offline, no cloud tokens. |
| `/ask-portfolio` | Answer questions about your own work — code, docs, notes, past decisions — via a local RAG second-brain over your corpus. Offline, cited, zero cost. |
| `/offload` | Hand a cheap, verifiable sub-task — narrowing a file list, extracting structure from noisy output, classifying log lines — to a local model. Offline, zero cloud tokens; you keep the judgment calls. |
| `/health` | Sign-on tool-health board — rolls the append-only friction log up per tool (recent friction, worst severity, one-line pain) into a "what needs attention" view. Local model, offline. |
| `/editorial-pass` | Multi-editor editorial pass over a draft in your voice — a mechanical AI-tell scan, six editor lenses fanned out via Workflow, and an editor-in-chief consolidation with verbatim fixes + a publish verdict. |
| `/voice-learn` | Mine AI-draft → final edit pairs to converge the agent's writing on your real voice — capture the AI version before you edit, then learn the diff into a voice profile. Corpus is yours, local, never in the repo. |

These encode one developer's workflow opinions. Fork and edit to match yours — the opinions ARE the value.

## Dependencies

Several skills call MCP servers; without them you'll see missing-tool errors.

- [ship](https://github.com/itsHabib/ship) — required by `/work-driver`, `/wip`.
- dossier — required by `/work-driver`, `/work-driver-prep`, `/work-driver-seed`, `/wip`, `/polish`, `/prep-public`, `/shipped`.
- [Ollama](https://ollama.com) (local model) — required by `/ask-portfolio`, `/review-digest`, `/offload`, and `/health` (which wants `qwen2.5:7b`); optional for `/pr-risk`'s deterministic floor. These run offline with no cloud tokens.
- `toolhealth` CLI — required by `/health`: a small local binary that summarizes an append-only friction log into a per-tool board. Operator-built; supply your own on PATH or adapt the skill to your own friction log.

## License

MIT.
