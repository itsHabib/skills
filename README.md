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
| `/shipped` | Retrospective: PRs merged, weighted-LOC, what's open, next moves. |
| `/status` | In-flight 4-section status (What happened / What's next / What I recommend / What I need). |
| `/worktree-add` | Create a worktree at `.claude/worktrees/<branch>/`. |
| `/worktree-list` | List worktrees with dirty state + PR/CI. |
| `/worktree-remove` | Remove a worktree, dirty-state aware. |
| `/worktree-transfer` | Move a worktree's branch into root. |
| `/worktree-where` | Show current worktree, branch, cwd. |
| `/dev-workbench` | Scaffold a canonical `## Dev workbench` section into a repo's CLAUDE.md. |
| `/eng-philo` | Stamp an opinionated `## Engineering principles` house style (Dave Cheney lineage) into a repo's CLAUDE.md, paired with the lint that enforces it. |
| `/prep-public` | Pre-launch audit: secrets, LICENSE, package metadata, README, `.gitignore`, leaks. |
| `/polish` | Stack-aware portfolio hygiene audit (Rust / Go / Node / Python / Elixir / Ruby). |
| `/subagent-scaffold` | Write a canonical Cursor subagent set into `.cursor/`. |
| `/chip` | Spin an out-of-scope item out into its own Claude Code session. |
| `/continue` | Emit a paste-ready continuation prompt so a fresh session picks up exactly where this one left off when context fills up. |
| `/tdd` | Turn a feature idea into a reviewed Technical Design Document plus dossier structure — design doc and rollout tasks in one shot. |
| `/review-coordinator` | Consolidate AI PR reviewers into one deduped verdict and merge gate; the judge over the finders. |
| `/consult` | Summon another repo's steward agent for a same-turn answer — knowledge questions about a sibling repo go to a peer, not the operator. |
| `/ship-ticket` | Chain the post-implementation wrap-up: file the Jira ticket, open the PR, describe it, sync the epic. |
| `/spinup-ticket` | Create a Jira ticket under a given epic via the Jira REST API. |
| `/sync-epic` | Bring a Jira epic's child tickets in line with their GitHub PR states (draft → In Progress, open → In Review, merged → Done). |
| `/write-pr` | Write or update the current PR description in a standard format. |

These encode one developer's workflow opinions. Fork and edit to match yours — the opinions ARE the value.

## Dependencies

Several skills call MCP servers; without them you'll see missing-tool errors.

- [ship](https://github.com/itsHabib/ship) — required by `/work-driver`, `/driver-run`.
- dossier — required by `/work-driver`, `/work-driver-prep`, `/work-driver-seed`, `/driver-run`, `/polish`, `/prep-public`, `/shipped`.

## License

MIT.
