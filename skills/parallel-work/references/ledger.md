# Parallel-work ledger

Read this file only when a run needs persistence or when handling `status` or
`resume`.

The ledger is private Claude state, not a repository artifact. Use one Markdown
file per run:

```markdown
---
parallel_work_version: 1
run: <short-slug>
repo: <absolute-repo-path>
base: <full-commit-sha>
through: local | pr | merge
delivery: combined | separate
status: planned | running | blocked | complete
created_at: <RFC3339>
updated_at: <RFC3339>
integration_branch: <branch-or-null>
integration_worktree: <absolute-path-or-null>
upstream:
  - repo: <absolute-path>
    commit: <full-sha>
    worktree: <absolute-clean-integration-worktree-path>
---

# <Run title>

## Tasks

| ID | Outcome | Owns | Depends on | Checks | State | Branch | Worktree | Commit | PR | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | ... | `path/**` | — | `cwd: command -> expected` | pending | ... | ... | — | — | — |

## Decisions

- <only material decisions that affect more than one task>

## Events

- <RFC3339> — <fact observed after it happened>
```

Allowed task states are `pending`, `running`, `blocked`, `done`, and
`integrated`. A `done` task has a preserved commit and passing task check. An
`integrated` task's commit is present on the combined integration branch.

Rules:

- Record full commit SHAs and absolute worktree paths.
- One ledger describes one repository. Cross-repository work uses ordered
  ledgers joined by full upstream integration SHAs.
- State is descriptive, never authority. Verify branches, commits, worktrees,
  checks, and PR heads live before acting.
- Append concise event facts; do not paste logs or Agent narration.
- Mark the run complete only at its chosen boundary: verified local result,
  verified open PR, or remotely confirmed merge.
- If blocked, name the exact task and missing decision, authority, dependency,
  or failing check.
