# skills

Portfolio dev-workflow skills for [Claude Code](https://claude.com/claude-code). Drop them into `~/.claude/skills/` (user-global) or `.claude/skills/` in a project repo — they show up as `/<skill-name>` commands.

These are **opinionated**. They encode one developer's workflow — reviewer set, branch convention, PR sizing, the dossier-ship-worktree loop. Fork and edit to match yours; the value is the opinions, not the configurability.

## Install

```bash
git clone https://github.com/itsHabib/skills ~/pers/skills
```

Then either copy individual skills:

```bash
cp -r ~/pers/skills/skills/work-driver ~/.claude/skills/
```

Or all of them:

```bash
cp -r ~/pers/skills/skills/* ~/.claude/skills/
```

After install, the skills appear as slash commands (`/work-driver`, `/status`, etc.) in your next Claude Code session.

## What's here

### Workbench — drive impl work end-to-end

The core loop for taking a task from "queued" to "merged."

- **`/work-driver`** — coordinate one or N parallel agent-led impl streams through fan-out → poll → land → review → merge → cleanup.
- **`/work-driver-prep`** — turn a backlog of tasks into spec docs + a conflict-aware batched plan ready for `/work-driver`.
- **`/shipped`** — retrospective recap after a chunk of work lands: PRs merged, task closures, what's open, suggested next moves.
- **`/status`** — tight in-flight 4-section status update (What happened / What's next / What I recommend / What I need from you).

### Worktree family — manage secondary git worktrees

Thin skills over plain `git worktree`. Convention: branch name is user-chosen; path is `<repo>/.claude/worktrees/<branch>/`. Use these instead of reaching for a worktree-management MCP — they cover the verbs that mattered (add, list, remove, transfer, where) without an external state store.

- **`/worktree-add`** — spin up a new worktree for a branch.
- **`/worktree-list`** — list worktrees with dirty state + optional PR/CI status (via `gh`).
- **`/worktree-remove`** — clean up a worktree (dirty-state aware: commit-WIP / stash / discard).
- **`/worktree-transfer`** — move a worktree's branch into the root checkout.
- **`/worktree-where`** — orient: which worktree, branch, and cwd is the current session pointing at.

### Lifecycle & meta

- **`/dev-workbench`** — scaffold a `## Dev workbench` section into a repo's `CLAUDE.md` listing the maintainer's canonical workbench (MCPs + skills). Idempotent re-run between guarded markers. Fork and edit the canonical list to match yours.
- **`/prep-public`** — pre-launch audit for a project you're about to take public. Stack-aware (Rust / Go / Node / Python / Elixir / Ruby). Checks: secrets in git history, LICENSE alignment, package metadata, README first-impression, `.gitignore`, personal/employer leaks, tags, CHANGELOG.
- **`/polish`** — ongoing portfolio hygiene audit. Same stack detection. Checks: CI workflows, README quality, follow-ups doc, doc/code drift, spec/plan freshness, stub tests, per-stack lint/coverage/doc-comments/security gaps.
- **`/subagent-scaffold`** — write a canonical Cursor subagent set into a repo's `.cursor/` tree. Five agents (`code-reviewer`, `scope-tracker`, `test-author`, `validator`, `ci-checker`) + a dispatch rule. Idempotent.
- **`/chip`** — spin out an out-of-scope item into its own Claude Code session via the chip UI.

## External dependencies

Several of these skills compose with MCP servers. Without them, the skill will surface as a missing-tool error when its verb is called.

- **[ship](https://github.com/itsHabib/ship)** — workflow execution (hands a task doc to cursor, persists the run). Required by `/work-driver`.
- **dossier** — project memory (markdown-on-disk corpus). Required by `/work-driver`, `/work-driver-prep`, `/polish`, `/prep-public`, `/shipped`. Currently private to the maintainer; the skills will degrade visibly without it.
- **huddle**, **playwright** — referenced by `/dev-workbench`'s canonical workbench list; not required by other skills.

## License

MIT — see [LICENSE](LICENSE).
