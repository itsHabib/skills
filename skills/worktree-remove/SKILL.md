---
name: worktree-remove
description: Remove a secondary git worktree, handling dirty state interactively. Use whenever the user says things like "remove the worktree", "drop the worktree", "clean up the worktree", "kill this worktree", "delete the worktree at X", or wants to free up a branch so another checkout can use it. Refuses to remove the main worktree.
argument-hint: "<branch-or-path>"
user_invocable: true
---

# worktree-remove

Removes a secondary worktree via plain `git worktree remove`. Handles dirty state by surfacing options to the user rather than silently force-removing.

## Step 1 - Resolve the target

If the user gave a short name (e.g. `bar`) or a path fragment, resolve it via:

```bash
git worktree list
```

Match against the row's path. Confirm with the user if more than one matches.

Refuse to proceed if the target is the main worktree (first row). Tell the user `git worktree remove` won't touch the main checkout.

## Step 2 - Check dirty state

```bash
git -C <worktree-path> status --short
```

If clean, skip to step 3.

If dirty (modified, staged, or untracked), present options before doing anything destructive:

- **Commit as WIP** - `git -C <worktree-path> add -A && git -C <worktree-path> commit -m "wip: pre-remove"`, then a clean removal in step 3.
- **Stash** - `git -C <worktree-path> stash push --include-untracked -m "pre-remove:<branch>"`, then clean removal. The stash is repo-wide and stays available on the branch (the user can apply it later from anywhere).
- **Discard** - Warn that uncommitted work will be lost. Require explicit confirmation. Step 3 will use `--force`.

Never default to `--force` without the user picking discard.

## Step 3 - Remove

Clean case:

```bash
git worktree remove <worktree-path>
```

Discard case (user-approved):

```bash
git worktree remove --force <worktree-path>
```

If `git worktree remove` refuses with a state error, surface the message verbatim - don't silently retry with `--force`.

## Step 4 - Confirm

Report:
- Path removed
- Branch that was checked out there (still available - the branch isn't deleted, only the worktree)
- Any pre-remove action (commit / stash / discard)

Mention that the branch is now free for checkout in any other worktree (including root).
