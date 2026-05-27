---
name: worktree-add
description: Create a new secondary git worktree under .claude/worktrees/ for isolated work on a branch. Use whenever the user says things like "create a worktree for X", "add a worktree", "spin up a worktree for this ticket", "make a new isolated checkout", "start a branch in a worktree", or wants to do a piece of work in parallel without disturbing the root checkout. Defaults to the .claude/worktrees/<branch>/ convention so the new dir is sandboxed from the main checkout.
---

# worktree-add

Creates a secondary git worktree so a branch can be worked on without disturbing the root checkout. Uses plain `git worktree add` - no external state store needed.

## Inputs to gather

- **branch** (required) - The branch name. Examples: `auth-rewrite-wave-b`, `feature/foo`.
- **path** (optional) - Where the worktree lives. Default: `<repo-root>/.claude/worktrees/<branch>/`. Override only if the user asks.
- **base** (optional) - Branch to fork from when the branch doesn't already exist. Default: `main`. Ask the user if their flow isn't main-based.

## Step 1 - Locate the repo root

```bash
git -C . rev-parse --show-toplevel
```

This anchors the default worktree path.

## Step 2 - Decide branch handling

Check if the branch already exists locally or on the remote:

```bash
git show-ref --verify --quiet refs/heads/<branch> && echo local
git ls-remote --exit-code --heads origin <branch> && echo remote
```

- **Local branch exists** - use it directly: `git worktree add <path> <branch>`
- **Only on remote** - create a tracking branch: `git worktree add -b <branch> <path> origin/<branch>`
- **Neither exists** - create new from base: `git worktree add -b <branch> <path> <base>`

## Step 3 - Add the worktree

Run the chosen variant from step 2. Example for the common new-branch case:

```bash
git worktree add -b <branch> .claude/worktrees/<branch> <base>
```

## Step 4 - Copy CLAUDE.md if the repo has one

If the repo root has a `CLAUDE.md` that isn't tracked by git (a common convention for per-machine AI context), copy it into the new worktree so agents working there get the same entry-point context:

```bash
test -f CLAUDE.md && ! git ls-files --error-unmatch CLAUDE.md >/dev/null 2>&1 && cp CLAUDE.md .claude/worktrees/<branch>/CLAUDE.md
```

Skip if it's tracked (the worktree will already see it via git) or absent.

Do **not** copy `.claude/` or `.keys/` - per-worktree state and secrets should stay scoped to root.

## Step 5 - Confirm

Report:
- Path: `<full-path>`
- Branch: `<branch>` (newly created from `<base>`, or reused if existing)
- Whether `CLAUDE.md` was copied over

Note that subsequent agent sessions should `cd` into the worktree path (or be launched with that cwd) to operate on it.
