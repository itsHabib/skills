# Boost

A portable skill for difficult engineering, algorithms and research. It helps an
agent choose a useful experiment or delegate a focused investigation, verify the
result and finish the active task. It works with the agent and tools you already
use. Python is optional.

## Install or update

1. Choose your agent's skill directory: normally `~/.claude/skills/` for
   Claude Code or `~/.codex/skills/` for Codex. For a project-scoped Claude
   installation, use `<project>/.claude/skills/`. If `boost` already exists,
   move it to a backup **outside** the discovered skills directory first.
2. Copy this entire `boost` folder into the selected directory, with no old
   `boost` folder at the destination. Avoid overlaying files: an overlay can
   leave removed references from an older version behind.
3. Start a fresh session in the project you want to improve. Ask the agent to
   read the installed `boost/SKILL.md` if skill discovery is uncertain. No
   Python command or dependency installation is needed to check discovery.

In Claude Code:

> /boost Help with this task. Find the question most likely to change our next action, test it, and use the result to finish the work.

In Codex:

> Use $boost on this task. Test the important uncertainty and carry the result through to a checked deliverable.

## With a side agent

Paste into the active lead session:

> /boost Give one fresh side agent a concrete unresolved question from this task, with the relevant files, evidence and constraints. Have it return an executed probe, checked patch or counterexample. Continue independent work. Verify its result, integrate what helps and finish the task. Add another helper only for a separate useful question. Report what you accepted, rejected or still need to test, and why.

The lead prepares the packet and dispatches through native tools. For an existing
separate session, use the [side-agent mission](references/helpers.md). That file
also explains fresh versus inherited context and the lead's handback step.

## Useful requests

- `/boost the integration test fails only after reconnect; locate the earliest broken contract`
- `/boost this parser slows down on large inputs; preserve its outputs and measure the complete path`
- `/boost test whether these observations can actually distinguish the two explanations`

The result should include the work itself, evidence, and what the investigation
changed. If a helper returns only advice, ask: **Choose the claim most likely to
change our decision and test it now; return the evidence.** If a useful report
sits unused, ask: **Verify this result, record its disposition and continue the
deliverable.**

For a lighter steer, choose one question from [Questions to unstick an agent](references/questions.md), then ask the agent to run the experiment. The table is part of this skill bundle.

## Optional utilities and research

The normal workflow uses Markdown and the project's own tools. Existing
[Python utilities](references/utilities.md) can save local execution receipts or
summarize feedback when wanted. They do not orchestrate the agents and are not
required to run Boost. Task-specific experiments may use whatever language or
tools the project needs.

[Research inspiration](references/research.md) describes mechanisms from Google
DeepMind's FunSearch, AlphaEvolve and AlphaDev. These inspire the workflow; they
do not establish that this skill improves a model's performance. Judge it by the
checked result and the effort it adds on your task.
