---
name: worktree-where
description: Report the current git worktree, branch, and working directory for this Claude Code session. Use whenever the user says things like "where am I", "what branch am I on", "which worktree is this", "what repo are we in", "remind me where I'm pointing", "what are we working on right now", or is jumping between Claude Code tabs and needs to orient. Resolves the cwd to its worktree root and shows whether it's the main checkout or a secondary worktree.
user_invocable: true
---

# worktree-where

Answers "where is this session pointing right now?" - a quick orientation check across Claude Code tabs.

## Step 1 - Resolve cwd to a worktree

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null
```

If `git rev-parse` fails, the cwd isn't inside a git repo. Say so and stop. Suggest the user `cd` somewhere meaningful first.

## Step 2 - Determine whether this is the main or a secondary worktree

```bash
git worktree list
```

The first row is the main worktree. Compare to the path from step 1:
- Match → this session is on the main worktree
- Other row → this session is on a secondary worktree (note the path under `.claude/worktrees/` or wherever it lives)

## Step 3 - Branch + state

```bash
git branch --show-current
git log -1 --oneline
git status --short | head -5
```

Empty `branch --show-current` means detached HEAD - surface that explicitly with the commit SHA.

## Step 4 - Report

Render compact, scannable. Example:

```
cwd:      ~/dev/my-app/.claude/worktrees/auth-rewrite/web
worktree: secondary (.claude/worktrees/auth-rewrite)
branch:   auth-rewrite-wave-b
HEAD:     9e427c67ab refactor(auth): rename _sessionId -> sessionId, ...
state:    clean
```

If dirty, replace `clean` with `dirty (N files)` and list the first 3-5 from `status --short`.

If on the main worktree, say `worktree: main (<path>)` instead.

Keep it under 10 lines. The point is fast orientation, not a status dump.
