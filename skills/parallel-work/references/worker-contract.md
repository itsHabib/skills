# Parallel-work Agent contract

Give each write Agent:

- task ID and one-sentence outcome;
- absolute repository worktree path and branch;
- verified base commit;
- paths it owns;
- upstream facts it may rely on;
- exact done-checks, each with command, working directory, expected result, and
  any named manual review checks;
- explicit out-of-scope boundary;
- whether it should commit locally.

Required behavior:

1. Work only in the assigned worktree and read repository instructions first.
2. Change only owned paths plus directly necessary tests inside those paths.
   Stop if completion needs another task's path or a material design choice.
3. Preserve user changes. Do not push, open a PR, merge, delete a worktree, or
   edit coordination state.
4. Run the exact task checks and inspect their output.
5. If asked to commit, stage only intended paths and create one local commit.
6. Return this compact object plus a one-line note only when necessary:

```json
{
  "task": "T1",
  "state": "done|blocked",
  "worktree": "/absolute/path",
  "branch": "branch-name",
  "commit": "full-sha-or-null",
  "filesChanged": ["repo/relative/path"],
  "checks": [{"cwd": "/absolute/path", "command": "...", "expected": "exit 0|exit 1|predicate", "result": "pass|fail", "note": "short"}],
  "blocker": null
}
```

Treat this as a lead, not proof: independently inspect the commit, diff, and
relevant checks before integration.
