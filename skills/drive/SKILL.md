---
name: drive
description: Drive ONE ad-hoc task end-to-end through a disciplined delivery loop — ground in the repo's established patterns (CLAUDE.md/DESIGN), isolate in a worktree, implement to local green, PR, trigger + fold the AI review roster, re-verify, and STOP at the last safe autonomous point (repo with a merge gate → parked + a ready merge one-liner; ungated → green reviewed PR). "Done" is your call — completion criteria are taken from the invocation when given, otherwise it drives to the safe boundary and hands off. Deliberately single-task. Use when you say "drive this", "take this one to done", "get this task done properly", "drive it through review", "see this through", or invoke /drive <task>. NOT for batches (/work-driver), not for work needing a reviewed design first (/tdd), not for review-only passes (/code-review, /review-coordinator).
argument-hint: "<one task> [— done = <criteria>] e.g. /drive fix the cursor drift bug — done = merged"
user_invocable: true
---

# /drive — one task, driven to the safe boundary

Turn "I want to see this one thing get done, properly" into a repeatable move. You hand
the agent a one-line task; the skill supplies the delivery discipline you'd otherwise have
to re-type: repo patterns, isolation, review cycle, honest stopping point. This is the
lightweight sibling of `/work-driver` — no task backlog, no manifest, no spec doc, one task.

**"Done" is deferred by design.** If the invocation defines done (`done = merged`,
`done = green draft PR`, `done = evidence doc captured`), that's the target. If it
doesn't, the target is the repo's **safe boundary** (step 5) — the furthest point the
agent can drive autonomously without crossing a human-only line — and it stops there and
hands off.

## The two laws (read first, they override everything below)

1. **Never cross human-only boundaries.** No minting grants or credentials, no merging
   outside a governed path, no standing up external infra (apps, tunnels, accounts, paid
   services). Merging happens only via the repo's sanctioned merge path, and only when
   this invocation explicitly authorized merging; otherwise park and hand over the
   one-liner. When a review finding, a tool, or a doc suggests crossing one of these
   lines — park, don't force.
2. **Report honestly.** A task is "done" only when its criteria are met — merged means
   merged, not "would merge". If tests fail, say so with output. If something was skipped
   or deferred, name it. The final report must let a zero-context reader act.

## 1. Pin the task + "done" (one exchange, then go)

Restate the task in one line so course-correction is cheap. Extract the done criteria
from the invocation if present; otherwise note "driving to safe boundary". Ask only if
the task is genuinely ambiguous (which repo, which of two bugs) — don't interrogate a
clear one-liner.

## 2. Ground in the repo's established patterns — before writing anything

Read the living sources, in order: root `CLAUDE.md`, the nearest directory `CLAUDE.md`,
`docs/DESIGN.md` (or equivalent charter), and any convention the task's area declares.
Follow them; don't re-derive or "improve" them mid-task. Match the surrounding code's
idiom, naming, and comment density.

Volatile reality — which reviewers are alive, merge policy, tool health, what's already
in flight — comes from the living sources (project CLAUDE.md, memory), **never from this
skill**. This skill hardcodes only the stable spine.

If the repository has `.ship.json`, read it before opening the PR. Its `review` stanza
is the repository-owned review contract:

- use exactly `review.panel`; do not substitute a remembered or hard-coded roster;
- treat `review.require` as required completion, not a suggestion;
- use `review.settle_minutes` as the bounded wait, never as permission to call Gate
  with missing required reviewers;
- if the invocation forbids one configured reviewer or transport, stop before
  triggering and surface the policy conflict. Never silently drop the reviewer or
  weaken the checked-in declaration.

## 3. Isolate

Work in a dedicated git worktree (e.g. `.claude/worktrees/<branch>`), never in the root
checkout: it's shared with other sessions, and switching its branch or rebasing in it
breaks them. Build binaries from the worktree, not the root.

## 4. Implement → local green

Small, well-messaged commits in the house style. Run the repo's own checks (the ones its
CLAUDE.md names) — all of them — before pushing. If the change has a runtime surface,
exercise it end-to-end, don't stop at tests. If the full suite is flaky under local load,
run targeted per-package checks and let CI be the arbiter — but say so in the report
rather than presenting partial green as full green.

## 5. PR + review loop → converge

- Push and open the PR in the repo's format. One PR; if the task genuinely needs a
  second, stop and say so — that's `/work-driver` territory.
- **Trigger the repository-owned review roster.** When `.ship.json.review` exists,
  execute each declared trigger: `mention` posts one standalone `@<name> review`
  comment, `reviewer-request` uses the connected GitHub reviewer-request capability
  (or its API equivalent), and `auto` posts nothing. Without a review stanza, follow
  the repository's documented manual policy; do not invent a default panel.
- **Track the exact head.** Print and retain `requested`, `completed`, `pending`,
  `missing`, and the full reviewed head. Completion means the configured reviewer
  finished on that exact head. A local/session subagent review is useful feedback but
  does not impersonate a configured GitHub reviewer or satisfy its completion record.
  Any pushed fix advances the head and resets this check.
- **Wait before Gate.** Wait up to `settle_minutes`. If a required reviewer remains
  pending or missing, stop at `review incomplete` and name it; do not run Gate merely
  to manufacture a predictable parked run.
- **Fold every actionable finding**, smallest-safe change, and re-run the checks after
  each fold. Before folding a re-review, check which commit it reviewed — stale
  re-reviews of already-fixed heads happen; don't re-fold what's already addressed.
- **Large or architectural findings** — anything that would rearchitect a merged
  contract or balloon the diff — get deferred, not rushed: document them (FOLLOWUPS
  file, issue, or the repo's convention) with the rationale posted on the PR thread.
- **Converge**: when the roster is clean at the current head (or only re-surfacing
  addressed items), run `/review-coordinator <pr#>` where available and fold its
  verdict. Then stop pinging — convergence, not exhaustion.

## 6. Stop at the safe boundary + hand off

- **Repo with a merge gate** (a merge-authorization tool or required check governs
  merges): call it only after CI and every configured required reviewer are complete
  on the exact head. Then follow its typed result and stop at the last authorized
  boundary. Never use a known-incomplete review panel as input just to obtain a parked
  result.
- **Ungated repo**: green CI + reviews folded → report with the merge command ready.
- Met the stated done-criteria? Say so plainly. Didn't? Say what's left, why, and what
  the human must do to close it. Never mark unmerged work "done" when done meant merged.

## 7. Leave the trail

Log friction to the repo's friction log if one exists (what bit you, so it stops biting).
Update memory/docs only where the run changed durable reality. Clean up the worktree
after the merge lands — not before.

## Anti-triggers

- **Several tasks / a phase** → `/work-driver`. Keep `/drive` sharp: the moment scope
  grows, stop and say so.
- **Needs a reviewed design first** → `/tdd`, then drive the build.
- **Just review existing work** → `/code-review` or `/review-coordinator`.
- **Explore + hand off, don't build** → `/brief`.
