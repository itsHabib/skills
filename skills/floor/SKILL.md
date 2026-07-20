---
name: floor
description: Render the EFFECTIVE Claude Code harness rulebook for this machine/project — what the current session may actually do — by merging every settings layer (global ~/.claude/settings.json, project .claude/settings.json, project settings.local.json) plus PreToolUse/PostToolUse hooks into one tiered view (free / consequential / guarded), flagging cross-shell asymmetries (a Bash rule with no PowerShell twin), wildcards that undo curated per-verb rules, and denies shadowed by allows. Use when you ask "what am I allowed to do", "what's my floor", "show the effective permissions", "render my rulebook", "why did that prompt", "audit my settings", "what's changed in my permissions", or invoke /floor. Read-only — it never edits settings.
user_invocable: true
---

# /floor — render the effective harness rulebook

You are rendering the *effective* policy a session runs under, which no single
file shows: it is the merge of global settings, project settings, project-local
scratch, and guard hooks. Read-only: never modify any settings file here.

## Gather

1. Read, tolerating absence:
   - `~/.claude/settings.json` (global)
   - `<project>/.claude/settings.json` (project, checked in)
   - `<project>/.claude/settings.local.json` (local scratch)
2. From each: `permissions.allow`, `permissions.deny`, `hooks.PreToolUse`,
   `hooks.PostToolUse`.
3. For each PreToolUse hook script that exists on disk, read it and extract
   what it blocks (grep the deny/refuse messages) — the hook layer is part of
   the floor even though it lives outside permissions.

## Classify

Bucket every allow rule by capability tier:

- **Tier 1 — free**: read-only or trivially reversible (git status/log/diff,
  gh pr view/list/checks, builds, MCP list/get verbs).
- **Tier 2 — consequential, auditable**: durable-but-undoable state (gh pr
  create/edit/comment, task-tracker writes, CI dispatch).
- **Tier 3 — guarded**: anything matching deny rules or guard-hook blocks
  (merge, force-push, delete, credentials, publish).

When a rule's tier is ambiguous, say so rather than guessing.

## Analyze — the checks that earn the render

- **Cross-shell asymmetry**: a curated `Bash(gh pr view:*)` set with a
  `PowerShell(gh *)`-style wildcard (or vice versa) — the wildcard silently
  undoes the curation. Flag any wildcard that is a superset of per-verb rules
  in the other shell.
- **Shell escapes**: allows that grant another interpreter wholesale
  (`Bash(powershell.exe *)`, `PowerShell(bash *)`, `Bash(sh -c *)`).
- **Deny shadowing**: denies that a broader allow would still route around
  (note: deny wins in the harness — flag only genuine gaps, e.g. deny in one
  shell only).
- **Local-scratch accretion**: count `settings.local.json` entries; anything
  tier-2+ living there belongs in a designed layer. Suggest promotions.
- **Hook coverage**: which tier-3 categories a guard hook covers vs. deny
  rules only vs. nothing.

## Render

One markdown report, in this order:

1. **Headline** — one sentence: how open is this floor, and the single most
   important gap (or "no gaps found").
2. **Tier table** — three rows (free / consequential / guarded), each with
   rule count per layer and representative examples, not exhaustive dumps.
3. **Guard hooks** — per hook script: what it blocks, one line each.
4. **Findings** — the analyze results, ranked, each with the exact rule text
   and the one-line fix (but do not apply it).
5. **Drain candidates** — local-scratch entries worth promoting or deleting.

If you ask for a diff ("what changed"), snapshot the merged rule set to
`~/.claude/floor-snapshots/<date>.json` and diff against the most recent
prior snapshot; report added/removed/changed rules only. Always write a fresh
snapshot after rendering so the next diff has a baseline.

## Boundaries

- Never edit settings or hooks from this skill — hand findings to a settings
  skill (e.g. the built-in /update-config or /fewer-permission-prompts).
- Do not read other projects' settings unless asked; default scope is the
  current project + global.
- Session-level context (mode, active grants) is out of scope — this renders
  the standing rulebook, not the live session state.
