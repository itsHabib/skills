# skills

Opinionated dev-workflow skills for [Claude Code](https://claude.com/claude-code).

## Install

```bash
git clone https://github.com/itsHabib/skills ~/dev/skills
cp -r ~/dev/skills/skills/* ~/.claude/skills/
```

Each appears as `/<skill-name>` in your next session. Copy individual dirs if you want a subset.

## Skills

| Skill | What it does |
|---|---|
| `/work-driver` | Drive one or N parallel agent-led impl streams: fan out → poll → land → review → merge → cleanup. |
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

These encode one developer's workflow opinions. Fork and edit to match yours — the opinions ARE the value.

## Dependencies

Several skills call MCP servers; without them you'll see missing-tool errors.

- [ship](https://github.com/itsHabib/ship) — required by `/work-driver`.
- dossier — required by `/work-driver`, `/work-driver-prep`, `/work-driver-seed`, `/polish`, `/prep-public`, `/shipped`.

## License

MIT.
