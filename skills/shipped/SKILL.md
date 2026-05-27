---
name: shipped
description: Retrospective recap after a chunk of work lands — what shipped (PRs merged + shas + weighted-LOC, dossier task closures, friction-log entries), what changed about main, what's open, and what you might do next. Use after /work-driver, a chip blitz, a manual phase, or anytime the operator asks "what just shipped", "what did we ship", "what merged today", "post-run summary", "what now". Auto-detects work-driver manifests for ground truth; falls back to git/gh/dossier signals otherwise. Distinct from /status — /status is an in-flight ping, /shipped is a retrospective on landed work.
argument-hint: "[manifest.md] [--since <window>] [--scope repo|portfolio] — e.g. /shipped, /shipped docs/features/polish-round-1/driver.md, /shipped --since 24h"
user_invocable: true
---

# /shipped — what just shipped + what now

Produce a tight retrospective after a chunk of work lands. Backward-looking on what merged, forward-looking on what's available next. **Not** an in-flight check-in (that's `/status`) and **not** a project-wide dump (that's `mcp__dossier__project_get` + `task_list`).

## When to use

Triggers:
- "what just shipped" / "what did we ship" / "what merged today"
- "post-run summary" / "shipped recap" / "wrap-up"
- "what now" / "what can I do now" — when paired with a recent merge
- End of a `/work-driver` run, a chip blitz, or a manual phase day
- Explicit `/shipped`

Anti-triggers:
- In-flight "where are we?" → use `/status`
- "What's the state of project X?" → use `mcp__dossier__project_get`
- Single-PR summary → use `gh pr view N` directly

## Arguments

`/shipped [manifest.md] [--since <window>] [--scope repo|portfolio]`

- **No args** → auto-detect: if a `docs/features/*/driver.md` exists with recent `merged_at` timestamps in its frontmatter, use it as ground truth. Otherwise scan git/gh for merges in the last 24h.
- **`<manifest.md>`** → explicit work-driver manifest path. Use its per-stream `pr_number` / `merge_commit` / `merged_at` for the truth, and ignore manifest entries with `status != done`.
- **`--since <window>`** → time window for git/gh fallback. Accepts `1h`, `24h`, `today`, `yesterday`, `<yyyy-mm-dd>`. Default: 24h.
- **`--scope portfolio`** → cross-repo. Default is the current repo. Portfolio scope iterates `gh repo list <owner>` and aggregates. Rare.

## Steps

### 1. Detect ground truth

Priority order (use the first that hits):

1. **Explicit manifest arg**: read its YAML frontmatter, extract every `streams[].pr_number` / `merge_commit` / `merged_at` where `status: done`. This is the cleanest signal.
2. **Auto-detected recent manifest**: glob `docs/features/*/driver.md`; pick any with at least one batch `status: done` and a `merged_at` within the `--since` window (default 24h). Same extraction as above.
3. **No manifest** → git/gh fallback: `gh pr list --state merged --search "merged:>=<since>" --json number,title,url,headRefName,mergedAt,mergeCommit,additions,deletions,author` filtered to the operator's commits (`--author @me`). Pair with `git log --merges --since=<since> --oneline` to cross-check.

### 2. Compute weighted-LOC per merged PR

For each PR, fetch the diff stat:

```
gh pr view <n> --json files --jq '.files[] | {path, additions, deletions}'
```

Weight per the standard PR sizing rule:

| Bucket | Weight |
|---|---|
| Production source + SQL + bash | 1.0× |
| Tests / fixtures | 0.5× |
| Lockfiles, generated, configs (`tsconfig.json`, `vitest.config.ts`, `package.json`), docs (`*.md`) | 0× |

Heuristic globs to drive weighting:
- `1.0×`: `src/**/*.{ts,tsx,js,go,rs,py}`, `**/*.sql`, `scripts/**/*.sh`, `**/*.bash`
- `0.5×`: `**/*.test.*`, `**/test/**`, `**/tests/**`, `**/fixtures/**`, `**/__fixtures__/**`
- `0×`: `**/*.lock`, `**/*-lock.{json,yaml}`, `**/package.json`, `**/tsconfig*.json`, `**/*.md`, `**/dist/**`, `**/generated/**`

Report total weighted LOC per PR; flag any that landed outside the standard bands (`<500` amazing / `<700` ideal / `<1000` stretch).

### 3. Pull dossier closures

```
mcp__dossier__task_list { project: "<inferred-from-repo>", status: ["done"] }
```

Filter to tasks whose `completed_at` is within `--since`. For each, surface:
- `slug` + 1-line title
- Linked artifacts of `kind: "pr"` or `kind: "commit"` — should match step 1's findings
- Any notes added during the session (last few entries from the `notes[]` array)

If repo→project mapping is ambiguous, run `mcp__dossier__project_list` and pick the one whose `name` matches the repo. Skip silently if no match — not every repo has a dossier project.

### 4. Check friction-log delta (optional)

If you maintain a friction log (e.g. `docs/friction.md` or any markdown file you append to after sessions), and it's under git, pull recent diffs:

```
git log --since=<since> -p -- <friction-log-path>
```

Surface the headlines of any new entries — they signal patterns worth remembering for next session. Skip silently if no friction log exists; this section is operator-style-dependent.

### 5. Detect "what changed about main"

For each merged PR, parse its body's `## Summary` / `## What this adds` / `## Validation` sections (whatever your repo's PR template uses). Pull 1-line "what's new" bullets that name new capabilities reachable from the CLI / API:

- New workflows in `.github/workflows/*` → "trigger with `gh workflow run <name>`"
- New scripts in `package.json` / `Makefile` → "now available: `pnpm run <script>`"
- New CLI verbs → "try `<bin> <verb>`"
- New MCP tools → "try `mcp__<server>__<verb>`"
- New skill files in `.claude/skills/` or `~/.claude/skills/` → "now invokable: `/<name>`"

Be specific, not abstract. "Mutation workflow now triggerable via `gh workflow run mutation.yml`" beats "added mutation testing".

### 6. Surface what's open

Forward-looking signals:

- **Open todo tasks in scope** — `mcp__dossier__task_list { project, status: ["todo"] }`. Bullet each with `id` + slug + 1-line title.
- **Chips filed during the session** — chips aren't queryable on disk; if invoked mid-session, the operator's UI shows the chip backlog. Skip unless you can see chip-spawn events in the current conversation; if so, list their titles.
- **Stale `in_progress` tasks** — flag any task that's `in_progress` but has no `notes` added in the last 7 days. Often the sign of work that fell off the radar.
- **Newly-unblocked work** — if a closed task was a `blocker` for another (per dossier's `blocked_by`), surface the unblocked one as "now ready".

### 7. Recommend next moves

1-3 concrete recommendations, each with a verb the operator can act on. Examples:

- "Run `/work-driver-prep <project>:<phase>` — N todo tasks are ready and conflict-free per their file lists."
- "Drain the chip backlog — M chips filed, none addressed; `/work-driver` once they're spec'd."
- "Write the next phase spec — current phase done, `docs/features/<next>/spec.md` is empty."
- "Nothing else queued — fair to log off."

Match the recommendation count to the actual signal density. If there's genuinely one thing, say one thing. Don't pad to three.

## Output format

```markdown
## Shipped (<window>)

- **PR #<n>** [<title>](<url>) — <weighted-LOC>w / <raw-LOC> raw — <merge-sha>
  - <1-line of what it does>
  - dossier: <task-slug> → done
- **PR #<n+1>** ...

## What changed about main

- <1-line: new capability + how to reach it>
- <1-line: ...>

## Open

- **todo**: <n> tasks (<slug-1>, <slug-2>, ...)
- **stale in_progress**: <slug> (no notes since <date>) — flag or pick up
- **chips**: <n> filed this session, not yet drained

## Next moves

1. <verb> — <reason in one phrase>
2. <verb> — <reason in one phrase>
```

If a section is empty, omit it entirely. Don't write "N/A" placeholders.

## Rules

- **No process narration.** Don't say "I queried dossier, found N tasks". Just list them.
- **PR shas + numbers + dossier slugs are first-class.** Adjectives are not.
- **Weighted LOC over raw LOC** when both are computable. Raw alone is misleading on lockfile-heavy PRs.
- **Skip empty sections.** A retrospective with one merge gets one bullet, not a padded report.
- **Don't recompute what the manifest already knows.** If the work-driver manifest says `merged_at: <ts>`, trust it — don't re-derive from `gh`.
- **Cap recommendations at 3.** If you have more, the prioritization is wrong, not the cap.

## Source material

- `work-driver` — produces the manifests this skill consumes.
- `work-driver-prep` — emits one of the natural next-move recommendations.
- `status` — the in-flight counterpart; don't confuse the two.
