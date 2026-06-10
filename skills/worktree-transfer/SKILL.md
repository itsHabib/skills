---
name: worktree-transfer
description: Transfer work from a secondary worktree to the root/main worktree by checking out its branch in root and removing the secondary worktree. Use whenever the user says things like "transfer the worktree to root", "bring this work over to main", "move the branch from the worktree", "switch root to the worktree's branch", "pull this into the main worktree", or is working in a .claude/worktrees/ subdirectory and wants to continue in the root. Invoke this proactively any time the user's intent is to consolidate a secondary worktree back into root.
argument-hint: "[branch-or-path]"
user_invocable: true
---

# worktree-transfer

**The intent:** the user has picked a branch (or pointed at a worktree) and wants that branch checked out in the root/main worktree so they can keep working there. Git only allows one checkout per branch, so the secondary worktree must be removed before root can switch to that branch.

## Step 1 - Resolve the input to a (worktree-path, branch) pair

The argument is whatever the user passed - treat it as **"this is what should end up in root"** and figure out the source worktree. Run:

```bash
git worktree list
```

The first row is the root (main) worktree. Match the user's input against the other rows:

- **A branch name** (e.g. `auth-rewrite-wave-b`) → the most natural form. Find the row whose branch matches; that's the worktree to drain.
- **A worktree path or short directory name** (e.g. `payments-refactor` or `.claude/worktrees/payments-refactor`) → use that row directly; read the branch from its column.
- **Nothing supplied** → list active worktrees and ask the user which one to transfer.

Always confirm the resolved branch + secondary path + root path with the user before doing anything destructive.

Capture the secondary worktree's **path** and **branch** and the root worktree's **path** - all three are referenced through the rest of the skill.

## Step 2 - Check the secondary worktree's state

```bash
git -C <worktree-path> status --short
```

This catches both modifications and untracked files (lines prefixed with `??`).

**If clean:** skip to step 3.

**If dirty:** stop and ask the user to choose before touching anything. Don't proceed without explicit confirmation:

- **Commit as WIP** - `git -C <worktree-path> add -A && git -C <worktree-path> commit -m "wip: pre-transfer"`. User can amend after the branch lands in root.
- **Stash** - Stash with a unique tag so step 6 can find it again:
  ```bash
  git -C <worktree-path> stash push --include-untracked -m "pre-transfer:<branch>"
  ```
  The stash is repo-wide so it survives the worktree removal and surfaces in root.
- **Discard** - Warn that uncommitted work will be permanently lost. Require explicit confirmation. Step 4 uses `--force` to drop the worktree along with the changes.

## Step 3 - Check root's state

```bash
git -C <root-path> status --short
```

If root has uncommitted changes, `git checkout` may refuse to switch branches. Warn the user and let them decide - usually they'll want to stash or commit root's work first.

## Step 4 - Remove the secondary worktree

```bash
git worktree remove <worktree-path>
```

If the user chose **discard** in step 2 (or there are stubborn untracked files), use `--force`:

```bash
git worktree remove --force <worktree-path>
```

## Step 5 - Check out the branch in root

```bash
git -C <root-path> checkout <branch>
```

## Step 6 - Apply stash if applicable

Only if the user chose **stash** in step 2. Apply the specific stash by its tag (don't blindly use `stash apply` which targets the most recent stash and could be someone else's):

```bash
git -C <root-path> stash apply "stash^{/pre-transfer:<branch>}"
```

**Common failure: untracked-file collisions.** If the stash includes untracked files (created with `--include-untracked`), `stash apply` refuses the whole operation when even one of those paths already exists in root - even if the contents are identical. The error looks like:

```
<file> already exists, no checkout
error: could not restore untracked files from stash
```

When this hits, fall back to per-file extraction. The stash commit has 3 parents: `^1` = HEAD, `^2` = index, `^3` = untracked-files tree. Pull only the files the user actually wants from `^3`:

```bash
# inspect what the stash holds
git -C <root-path> stash show "stash^{/pre-transfer:<branch>}" --include-untracked --name-only

# for each file worth keeping (skip ones that already exist in root with same content):
git -C <root-path> checkout "stash@{N}^3" -- <path>
```

(Resolve `stash@{N}` from `git stash list` - the message-search `stash^{/...}` syntax doesn't accept `^3`.)

After the apply (or per-file extraction) is done, drop the stash so it doesn't linger:

```bash
git -C <root-path> stash drop "stash^{/pre-transfer:<branch>}"
```

## Step 7 - Confirm

Report concisely:
- Worktree removed: `<path>` (was on `<branch>`)
- Root is now on: `<branch>`
- Dirty-state action taken (commit / stash / discard) - if any
