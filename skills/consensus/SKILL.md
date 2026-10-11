---
name: consensus
argument-hint: "[goal, folder, or command]"
user_invocable: true
description: Keep a shared consensus folder with a goal, source snapshots, proposals and explicit votes from agents in any provider or app. Use for consensus across models, manual app handoffs, or resuming an ongoing decision. Also supports automatic Claude/Codex runs.
---

# /consensus

One folder per decision. Agents contribute independently using the same goal,
sources and proposal. Any provider can participate through files or pasted JSON;
no provider integration is needed. Agreement records judgments, not proof.

## Shared folder workflow

Use this mode by default for a continuing decision or cross-app work. Infer the
goal and relevant sources from the conversation. Choose expected participants
from the user's request; otherwise start with `codex,claude`. Use arbitrary
labels for other apps/models, such as `gemini` or `claude-opus`.

Read [references/folders.md](references/folders.md) for the command and JSON
formats. The helper is `scripts/topic.py`, relative to this skill folder.

- `/consensus start <goal>`: create a folder under `~/.consensus/topics/` or the
  user's chosen location. Freeze the goal, selected source text and participant
  roster. Leave its path and README for the next agent.
- `/consensus <folder>`: inspect status and the actual sources. As the current
  participant, propose a solution when none exists, or approve/object to the
  selected proposal. Record only your own judgment and actual provider/model;
  use `unknown` when identity details are unavailable. Do not vote for others.
- `/consensus prompt <folder> <participant>`: print a packet to paste into any
  app, including source text, the exact proposal and a JSON reply template. The
  other app needs no filesystem access. Save its returned JSON with `submit`.
- `/consensus revise <folder>`: use a revision prompt containing the selected
  proposal and objections. Submit a new proposal; collect fresh votes for it.

If several proposals exist, use the one named in the conversation or ask which
one to review. Do not silently choose one from timestamps. The helper's status
lists each proposal separately; `--proposal` selects an exact subject.

Inputs stay fixed within a folder. Changed goals, sources or rosters start a new
folder. Revised proposals receive fresh IDs, and old approvals never carry over.
Each participant explicitly approves, including the proposal author. A known
objection means `disagreed`, with any missing participants still shown; no
objections but missing votes means `incomplete`. Only a full approving roster
means `agreed`.

Files are immutable and checked on read. Identical vote retries are accepted;
conflicting second votes are rejected. Use the helper to publish records, rather
than editing them directly. Status is derived, so agents do not update a shared
status document. Keep private source out of public artifacts; pasted packets
still share that source with the receiving provider.

Return the folder link, exact proposal ID, approvals, substantive objections,
missing participants and the next useful step. Consensus does not authorize
implementation, publication or deployment of the proposal. Finish the bounded
contribution requested; do not manufacture an endless negotiation loop.

## Automatic run

For a one-shot automatic comparison using the installed Claude and Codex CLIs,
read [references/automatic.md](references/automatic.md) and run
`scripts/consensus.py`. This mode preserves saved calls and bounded timeouts.
Other providers use the shared-folder workflow above.
