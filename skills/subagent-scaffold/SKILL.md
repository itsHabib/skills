---
name: subagent-scaffold
description: Scaffold (or refresh) the maintainer's canonical Cursor subagent set into a repo's `.cursor/` tree. Writes five `.cursor/agents/*.md` files (code-reviewer, scope-tracker, test-author, validator, ci-checker) plus `.cursor/rules/use-subagents.mdc` (the dispatch nudge). Same shape across every portfolio repo so any `ship.ship` run anywhere gets the same inner-loop coverage. Idempotent re-run — preserves user-added agents that aren't in the canonical set; prompts on per-file drift before overwriting customizations to canonical files. Use when onboarding a fresh repo for ship dogfood, when one of the canonical agents is updated upstream, or when an existing repo's `.cursor/agents/` is missing or partial. Fork and edit the canonical set under `templates/` to match yours.
argument-hint: "[path/to/repo-root] — defaults to the current repo root (cwd / git toplevel)"
user_invocable: true
---

# /subagent-scaffold — write the canonical Cursor subagent set into any repo

**This skill is portfolio-specific.** It carries one developer's canonical Cursor subagent set + dispatch rule and writes them into a target repo's `.cursor/` tree. The canonical content is bundled under `templates/` in this skill directory; this is not a generic "discover any agents" tool. When you fork, edit the bundled templates to match your own preferred subagents.

When one of the canonical files is updated, edit it under this skill's `templates/` directory and re-run the skill on every portfolio repo that already has the set — markers + drift detection make refreshes idempotent.

## When to use

User-facing signals:

- "scaffold the subagents into this repo"
- "set up cursor subagents here"
- "copy the standard subagent set into `<repo>`"
- "refresh subagents — code-reviewer was updated upstream"
- Onboarding a fresh portfolio repo where `.cursor/agents/` is absent or partial
- Any explicit invocation: `/subagent-scaffold`

Don't use for:

- Adding a one-off custom agent the operator wants in only one repo — that's a manual file edit, not this skill's job.
- Discovering or documenting *Claude Code* skills or agents (different namespace; that's plugin / skill territory).
- Modifying the canonical agent definitions themselves — edit the files under `templates/` in this skill directory, then re-run the skill against each consuming repo.

## The canonical set (hardcoded under `templates/`)

**Subagents** — five files, all `inherit` model by default, all fire during `ship.ship` impl runs:

1. **`code-reviewer.md`** — pre-PR self-review; returns P0–P3 findings on the diff against CLAUDE.md conventions.
2. **`scope-tracker.md`** — classifies each touched file as in-scope / adjacent / out-of-scope vs the task doc's Scope section; flags scope creep.
3. **`test-author.md`** — drafts vitest tests for new production code that landed without matching tests.
4. **`validator.md`** — runs `make check` (or repo equivalent) + reports green/red verdict with diagnosis on failure.
5. **`ci-checker.md`** — post-PR-open: polls `gh pr checks` until terminal, returns green or failing-check name + log excerpt. Dormant in pure impl runs (cursor doesn't open PRs there); useful in any future post-PR cursor flow.

**Dispatch rule** — one file, instructs the parent agent to invoke the four impl-time subagents at natural points (`use-subagents.mdc`):

- `code-reviewer`, `scope-tracker`, `validator` → before the final structured summary
- `test-author` → after writing new exports without matching tests

The rule file explicitly does NOT enumerate `ci-checker` because cursor inside `ship.ship` is told to never open a PR, so a post-PR subagent has nothing to feed it. It's registered for any future post-PR flow.

**Explicitly NOT in the canonical set**:

- Repo-specific subagents (e.g. a `naming-cop` that encodes one repo's local conventions). Those live in the consuming repo's `.cursor/agents/` outside the canonical names; the skill won't touch them on refresh.

## Steps

### 1. Resolve target + sanity check

Resolve the target repo root: arg, else `git rev-parse --show-toplevel`, else cwd. Bail clearly if:

- Resolved path doesn't exist → ask the operator for a path
- No `.git/` at the resolved path → ask via `AskUserQuestion` whether to proceed (some scaffolding flows want to seed before `git init`)
- The path is the source-of-truth repo where the canonical agents originated → ask whether to proceed (the source IS the source of truth; re-running there is normally a no-op, but allowed)

Read the existing `.cursor/agents/` and `.cursor/rules/` directories if present; note which canonical files exist and which don't.

### 2. Detect drift on canonical files

For each canonical filename (the five `agents/*.md` + the one `rules/*.mdc`):

- **File absent in target** → planned action: `write` (clean install).
- **File present in target, byte-identical to skill's template** → planned action: `skip` (already in sync).
- **File present in target, differs from skill's template** → planned action: `prompt`. Show a unified diff (template → target) via `git diff --no-index --color`. Ask via `AskUserQuestion` whether to (a) overwrite, (b) keep target's version, (c) view full content + decide. Default: (b) — never silently clobber a customization.

User-added agent files (filenames not in the canonical set) are never touched. The skill only manages the canonical names.

### 3. Apply the plan

For each `write` / `overwrite` action:

- Ensure parent directory exists (`mkdir -p .cursor/agents/`, `mkdir -p .cursor/rules/`).
- Copy the template file from this skill's `templates/<subdir>/<file>` to `<target>/.cursor/<subdir>/<file>`.
- No managed-block markers inside the file content — each file is a single logical unit; "managed" is at the filename level. Customizations live under different filenames.

For `skip` actions: no-op, but log to stdout so the operator sees the file was checked.

For `keep` actions (operator chose to preserve their customization): log a warning that the file is now drifted from the canonical and won't be refreshed by future re-runs until the operator either renames it (preserves their fork) or accepts an overwrite.

### 4. Verify + summarize

After all writes:

- Re-list `<target>/.cursor/agents/` and `<target>/.cursor/rules/`. Print a table: filename / canonical y/n / action taken (write / overwrite / skip / keep).
- Suggest a smoke test: `mcp__ship__ship` against any small task doc in the target repo, then grep the run's `events.ndjson` for `"subagentType"` — expect at least one natural fire.
- Suggest committing the changes via a small chip-PR (`git add .cursor/ && git commit -m 'chore(.cursor): seed canonical subagent set via /subagent-scaffold'`).

## Source of truth

The canonical content lives at `templates/agents/*.md` and `templates/rules/use-subagents.mdc` inside this skill directory. To update a canonical agent:

1. Edit the file under this skill's `templates/` directory.
2. Re-run `/subagent-scaffold` against every portfolio repo that consumes the set. The drift detection in step 2 will flag the difference and prompt for refresh.

If your subagent set originated in a different source repo and the templates here are a copy, re-syncing is a manual `cp` step today. In practice the canonical set changes rarely.

## Caveats

- **No marker-based partial-overwrite.** Each canonical file is a single logical unit (one agent definition). Marker-based merges would split the YAML frontmatter or the instruction body unnaturally. The drift-prompt UX is the substitute.
- **Skill doesn't dispatch the subagents.** It only writes the files. The actual dispatch comes from the parent cursor agent during `ship.ship` runs, nudged by the `use-subagents.mdc` rule the skill writes alongside.
- **`ci-checker` is dormant in impl runs.** It's registered so a future post-PR cursor flow can use it without per-repo file scaffolding. If you don't want it in a particular repo, delete it after the scaffold and the skill's drift-prompt will leave you alone on re-run (you'll choose `keep` on a delete-then-add diff).
- **Re-syncing from an upstream source repo.** If your templates are a copy of agents authored in another repo, the templates don't auto-update when that repo's agents change. Manual step: re-copy the agents into this skill's `templates/agents/` then re-run `/subagent-scaffold` across consuming repos.

## Example flow

```sh
# Onboard a fresh repo:
cd <repo-root>
/subagent-scaffold                # writes .cursor/agents/* + .cursor/rules/use-subagents.mdc
git add .cursor/
git commit -m "chore(.cursor): seed canonical subagent set via /subagent-scaffold"

# Smoke test:
# (from a Claude Code session in the same repo)
mcp__ship__ship { workdir: "...", docPath: "docs/features/...", repo: "<repo-name>", branch: "..." }
# Wait for terminal, then:
grep '"subagentType"' <runs-dir>/<wf>/events.ndjson | head -5
# Expect: at least one natural fire (code-reviewer, scope-tracker, etc.)
```

```sh
# Refresh after a canonical update:
# (operator edits this skill's templates/agents/code-reviewer.md)
cd <other-repo-root>
/subagent-scaffold                # detects drift on code-reviewer.md, prompts; operator chooses overwrite
```

```sh
# Fork an agent for a single repo:
cd <repo-root>
cp .cursor/agents/code-reviewer.md .cursor/agents/code-reviewer-strict.md
# Edit code-reviewer-strict.md to add repo-specific rules
# Re-running /subagent-scaffold leaves the fork untouched (filename not in the canonical set);
# the original code-reviewer.md stays in sync with the canonical.
```

## Cross-refs

- Sibling skill (same scaffolding pattern, different target): `dev-workbench`.
