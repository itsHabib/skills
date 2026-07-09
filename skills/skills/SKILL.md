---
name: skills
description: Skill librarian - catalog every skill available in this session and recommend the best fit for a task. Discovers all skills on disk (personal ~/.claude/skills, project .claude/skills, and skills stranded in .claude/worktrees) by reading their frontmatter, so the catalog is always current. Run alone (/skills) for a grouped tabular overview of everything you have; run with a prompt (/skills post the daily bomb-out triage) to rank the catalog against that task and recommend the top matches with the exact command to type. Use when the operator asks "what skills do I have", "which skills are available", "what can I run", "is there a skill for X", "which skill should I use for Y", "recommend a skill", "I forget what skills I built", "what's available to me", or invokes /skills.
argument-hint: "[a task or question] — omit for the full overview, e.g. /skills, /skills check copilot web APM for anything actionable"
user_invocable: true
---

# /skills — the skill librarian

The operator has built dozens of skills across several roots and forgets what exists. This
skill is the index: it reads every skill's frontmatter off disk and either lays them all out
or points at the right one for a task. It never guesses from memory or from the harness's
injected skill list - it reads the source of truth so a skill added yesterday shows up today.

## Discover first (always)

Build the catalog by running the discovery script from the current repo root:

```bash
bash ~/.claude/skills/skills/discover.sh
```

It emits one tab-separated row per skill: `source<TAB>name<TAB>invocable<TAB>description`,
where `source` is `personal`, `project`, or `worktree:<branch>`. Parse every row - the
`description` field is the full frontmatter description and is what you rank against in
recommend mode.

If the script errors or returns nothing, fall back to globbing `SKILL.md` under
`~/.claude/skills/*/`, `.claude/skills/*/`, and `.claude/worktrees/*/.claude/skills/*/`
and read the frontmatter yourself.

## Mode A — overview (no argument)

Render the whole catalog as a grouped table. One group per source, in this order: **project**
(most relevant to the current repo), **personal**, then each **worktree** group. Within a
group, sort by name.

Columns:
- **Skill** — the invocation, e.g. `/wip`. Suffix with ` ·auto` only when `invocable` is
  explicitly `false` (it triggers automatically / isn't meant to be typed). A missing/`?`
  value means the field was omitted - treat it as invocable, no marker.
- **What it's for** — the first sentence of the description (up to the first `. `), trimmed.
  Do not paste the whole description; the point is scannability.

Above the table, one line with the total count and how many sources were scanned. Below it,
one line: "Run `/skills <task>` to get a recommendation for a specific job."

Keep the whole thing tight - this is a glance tool, not a report. Do not editorialize per
skill.

## Mode B — recommend (argument given)

The argument is a task, question, or rough intent. Rank the catalog against it and answer:

1. **Top pick** — the single best-fit skill: its `/command`, and one sentence on why it fits
   *this* task (reference the operator's actual words). If it takes arguments worth passing,
   show the full command to type.
2. **Runners-up** — up to two more plausible skills, one line each (`/command` — why), only
   if they're genuinely relevant. Omit this section if nothing else fits.
3. **If nothing fits** — say so plainly and suggest either the closest general tool or that
   this might be a skill worth creating (offer `/skill-creator`-style help only if asked).

Match on intent, not keyword overlap. A skill's description lists its trigger phrases and its
"Distinct from ..." notes - use those to disambiguate near-neighbors (e.g. /status vs /wip vs
/shipped). Prefer a **project** skill over a **personal** one when both fit and the task is
clearly about the current repo. Call out when the best fit lives in a **worktree** branch
that isn't checked out, since the operator may need to switch to reach it.

## Notes

- This is read-only. It never runs, edits, or creates skills - it only tells the operator
  what exists and what to reach for. If they then want to run one, they invoke it themselves.
- Descriptions are the ground truth for behavior. If two skills look redundant, surface that
  as an observation ("`/write-pr` exists in both project and personal roots") rather than
  picking silently.
