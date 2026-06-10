---
name: worktree-list
description: List git worktrees in the current repo with branch, dirty state, and optional PR/CI status. Use whenever the user says things like "list worktrees", "what worktrees do I have", "show my worktrees", "which worktrees are open", or wants a status overview of in-flight work across worktrees. Pull PR/CI status from gh when worktrees correspond to branches with open PRs.
user_invocable: true
---

# worktree-list

Shows all worktrees for the current repo with state. Plain `git worktree list` is the foundation; this skill enriches it with dirty state and (optionally) PR/CI status from `gh`.

## Step 1 - Get the raw list

```bash
git worktree list --porcelain
```

The porcelain format is parseable: blank-line-separated records with `worktree`, `HEAD`, `branch` (or `detached`) lines. The first record is always the main worktree.

## Step 2 - Compute dirty state per worktree

For each worktree path from step 1:

```bash
git -C <path> status --porcelain | head -1
```

Empty output → clean. Any output → dirty (modified, staged, or untracked).

Optionally also compute ahead/behind vs the worktree's upstream:

```bash
git -C <path> rev-list --left-right --count @{u}...HEAD 2>/dev/null
```

Output is `<behind> <ahead>` if an upstream is set, empty otherwise.

## Step 3 - Optionally enrich with PR status

If the user asked for PR status or it's obvious from context (e.g. "what's in flight"), and `gh` is available, look up open PRs by branch:

```bash
gh pr list --json number,headRefName,url,state,statusCheckRollup --limit 100
```

Then for each worktree's branch, find the matching PR (if any) and surface: PR number, state, top-level CI status (PASS / FAIL / PENDING). Skip this step for routine "list my worktrees" asks - it's network and slow.

## Step 4 - Present

Render a compact table. Mark the main worktree clearly. Example shape:

```
* <root-path>          main                clean
  .claude/worktrees/x  auth-rewrite         dirty (3 files)   PR #123 PENDING
  .claude/worktrees/y  feature/foo          clean             PR #128 PASS
```

Keep it tight - operators usually scan this to remember what's in flight, not to read prose.
