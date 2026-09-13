---
name: pr-sweep
description: Per-PR accountability sweep across every open PR in the operator's portfolio — for each one, the ONE thing blocking merge, whose move it is, and how long it has sat. Catches agents that stopped short of the safe boundary — findings left unresolved, review roster never gathered, branch left behind, red check untouched, or a PR sitting fully green and reviewed that nobody drove to merge. Read-only report; the operator decides what to chip. Use when the operator says "sweep my PRs", "pr sweep", "why aren't my PRs merged", "are my agents driving things to merge", "what's stuck in review", "check my open PRs", "is anything rotting", "did the agents finish", or invokes /pr-sweep. Distinct from /wip (cross-store liveness board) — this goes deep on PRs only and assigns blame per PR.
argument-hint: "[--scope pers|all] [--repo <name>] [--stale <days>] — e.g. /pr-sweep, /pr-sweep --repo ship, /pr-sweep --stale 7"
user_invocable: true
---

# /pr-sweep — why isn't each PR merged yet

An open PR is an agent's unfinished sentence. The house delivery loop says a driven task
ends at the **safe boundary** — green, roster gathered, findings addressed, parked with a
merge one-liner in the operator's hand (`/drive` step 5). Agents routinely stop earlier
than that and report success anyway: the PR is *open*, so it looks driven.

This sweep audits every open PR against that boundary and says, per PR, **the one thing
blocking merge and whose move it is.**

**Read-only.** It never merges, never mints a grant, never chips, never pushes. It produces
a report; the operator decides what to spin off — usually a `/chip` carrying a `/drive`.

## Why this isn't `gh pr list`

Four signals decide whether a PR is genuinely ready, and the ones that matter most are
invisible on the PR list:

- **Unresolved review threads.** The highest-value signal. In these repos thread resolution
  is *not* a merge requirement, so `mergeStateStatus` reports `CLEAN` while a Codex or
  Cursor finding sits unaddressed. A PR that looks merge-ready with an open thread is the
  signature of an agent that gathered the panel and never read it. Only reachable via
  GraphQL `reviewThreads`.
- **Panel coverage.** The roster is codex + claude + cursor + copilot. A PR carrying one
  bot's comments never had the roster triggered — the agent skipped `/drive` step 2.
- **`reviewDecision` is empty in most portfolio repos** (no required approvals configured),
  so it is *not* the readiness signal here. `CLEAN` + full panel + zero unresolved threads
  is. Where `reviewDecision: REVIEW_REQUIRED` *does* appear (e.g. `dossier`), branch
  protection is real and it becomes a hard operator-move blocker.
- **Age against last movement.** A green reviewed PR opened two hours ago is in flight. The
  same PR at three days is abandoned. Same state, opposite verdict.

## When to use

Triggers: "sweep my PRs" · "why aren't my PRs merged" · "are my agents actually driving
things to merge" · "what's stuck" · "is anything rotting" · "did the agents finish" ·
explicit `/pr-sweep`.

Anti-triggers:
- "what's in flight across everything?" → `/wip` (joins ship runs + dossier tasks + PRs)
- "what did the bots say on PR N?" → `/review-digest N` then `/review-coordinator N`
- "how much review does this PR need?" → `/pr-risk`
- "what just merged?" → `/shipped`

## Arguments

`/pr-sweep [--scope pers|all] [--repo <name>] [--stale <days>]`

- **`--scope pers`** (default) — portfolio only. Exclude day-job repos (`<work-org>/*`, your
  employer's GitHub org) and dead-org cruft (`drop-party/*`).
- **`--scope all`** — include day-job.
- **`--repo <name>`** — one repo (`ship`, `workbench`, `roxiq`…).
- **`--stale <days>`** — rotting threshold. Default **14**.

## Gather

One `gh search prs` for the roster, then per-PR detail. Run the per-PR fetches
concurrently — they're independent and there are usually 15–25.

```bash
gh search prs --author=@me --state=open --limit 60 \
  --json repository,number --jq '.[]|"\(.repository.nameWithOwner):\(.number)"' \
  | grep -v -e '^<work-org>/' -e '^drop-party/'
```

Per PR — state, checks, panel, age:

```bash
repo="${pr%%:*}"; num="${pr##*:}"
gh pr view "$num" --repo "$repo" \
  --json number,title,isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,comments,reviews,updatedAt,createdAt,url \
  --jq '{n:.number,t:.title,draft:.isDraft,ms:.mergeStateStatus,rev:.reviewDecision,upd:.updatedAt,crt:.createdAt,
         checks:[.statusCheckRollup[]?|{n:(.name//.context),c:(.conclusion//.state)}],
         panel:([.comments[]?|.author.login]+[.reviews[]?|.author.login]|unique)}'
```

Per PR — **unresolved review threads** (the signal that justifies this skill):

```bash
owner="${repo%%/*}"; name="${repo##*/}"
gh api graphql -f query="{repository(owner:\"$owner\",name:\"$name\"){pullRequest(number:$num){
  reviewThreads(first:50){nodes{isResolved isOutdated comments(first:1){nodes{author{login} path line}}}}}}}" \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[]
         |select(.isResolved==false and .isOutdated==false)
         |{bot:.comments.nodes[0].author.login, at:"\(.comments.nodes[0].path):\(.comments.nodes[0].line)"}]'
```

Notes that bite:
- **zsh does not word-split unquoted expansions.** Iterate `repo:num` strings and slice with
  `${p%%:*}` / `${p##*:}`; `set -- $p` silently yields one field.
- `gh pr view` needs the number as a **positional** arg even with `--repo`.
- An **empty** `conclusion` in `statusCheckRollup` means *pending*, not passing.
- Filter deploy bots out of the panel — `vercel`, `netlify`, `render` comment on PRs but
  review nothing. Reviewer roster is exactly: `chatgpt-codex-connector`, `claude`, `cursor`,
  `copilot-pull-request-reviewer`.

## The bands

Assign each PR to exactly one band — the **first** it matches, top down. The band is a claim
about *whose move it is*.

### ⏳ In flight — nobody's move
Any of:
- Required checks still **pending or running** (empty `conclusion` in the rollup).
- **Created** < 6h ago — the grace window for the panel to land and the agent to answer it.
- A **draft** < 24h old. A draft is legitimately mid-work until it isn't.

Judge freshness by **`createdAt`, never `updatedAt`.** A bot comment bumps `updatedAt`, so
the update clock makes a PR look fresh *precisely because* findings are piling up on it —
it would permanently excuse the exact failure this sweep exists to catch.

Do not prescribe here. But if an in-flight PR already carries unresolved threads, append a
bare `⚠ <n> open thread(s)` so they aren't invisible for the next 6h.

### 🟡 Agent stopped short — *the point of this skill*
Something mechanical and un-owned is blocking, and no human decision is needed. Any of:
- **Findings left on the floor** — unresolved, non-outdated review threads. Name the bot and
  `file:line`. This is the most common and most damning: panel gathered, panel ignored.
- **Thin or absent panel** — fewer than two roster bots, or none, on a non-draft PR.
- **Behind / dirty** — `mergeStateStatus: BEHIND` or `DIRTY`. Needs a rebase or conflict fix.
- **Red check untouched** — a `FAILURE` in the rollup with no commit after it.
- **Draft with no panel, aging** — a draft > 24h old whose roster was never triggered.
  A draft is a parking space, not a destination.

When two apply, the blocker to name is the one that must move **first**: unresolved
findings outrank a rebase (the rebase would only have to happen again), and both outrank
a missing approval — there is nothing to approve until the findings are answered.

### 🟢 Ready — mint and merge
`CLEAN` + every check green + ≥2 roster bots + **zero** unresolved threads + not a draft.
Nothing blocks it but authorization, which is the operator's to grant.

Emit the mint request — **never** a bare `gh pr merge`, never `--admin`:

```
gate grant -repo <owner/repo> -max-tier T2 -ttl 24h -state ~/dev/gate/state
```

Then note that `gate gate -repo <owner/repo> -pr <n> -grant grt_... -state ~/dev/gate/state`
emits the pinned merge command to run verbatim. **The agent never mints.** If several PRs in
one repo are ready, say so — one grant covers the repo for its TTL.

### 🔵 Needs your decision — operator's move
A human judgment blocks it, not work:
- `reviewDecision: REVIEW_REQUIRED` with branch protection — needs an approving review.
- A **TDD / design draft** awaiting sign-off (title contains `TDD:` or `(draft)`) — the
  design is the deliverable; merging is a decision, not a task.
- A finding whose fix crosses a human-only line (infra, spend, credentials, scope change).

Say what the decision *is*, in one line. Don't restate the PR title.

### ⚫ Rotting — decide: revive or close
No movement in `--stale` days (default 14). Include the age in days and a one-line read on
whether the work still matters. Offer closing as a live option — an abandoned PR costs
attention every sweep.

## Output format

Lead with the scorecard — it's the answer to "are my agents being lazy". Skip empty bands.

```markdown
**<N> open** · 🟡 <n> stopped short · 🟢 <n> ready · 🔵 <n> on you · ⏳ <n> in flight · ⚫ <n> rotting
<One-line verdict. e.g. "6 sat merge-ready for days — nothing blocked them but a grant.">

## 🟡 Agent stopped short (<n>)
- **repo#N** — <title, trimmed> · <age>
  ↳ <the one blocker, specific> — e.g. "codex thread unresolved at `src/store.rs:88`"

## 🟢 Ready — mint and merge (<n>)
- **repo#N** — <title> · <age> · green, <k>-bot panel, no open threads
`gate grant -repo <owner/repo> -max-tier T2 -ttl 24h -state ~/dev/gate/state`   ← covers <n> PRs in this repo

## 🔵 Needs your decision (<n>)
- **repo#N** — <title> · <age>
  ↳ <what the decision is>

## ⏳ In flight (<n>)
- **repo#N** <title> · <age> · <checks running | panel landing>

## ⚫ Rotting (<n>)
- **repo#N** — <title> · <age>d — <still relevant? | close?>
```

Close with **candidate chips** — a plain list, not an offer to act:

```markdown
**Worth chipping:** `repo#N` (resolve the codex thread, re-park) · `repo#M` (rebase + gather panel)
```

## Rules

- **Read-only. No exceptions.** No merges, no grants, no pushes, no `gh pr close`, no
  `spawn_task`. The sweep observes. If the operator wants action, they say so next turn.
- **One blocker per PR.** If three things are wrong, name the one that has to move first.
  A list of five problems per PR is a wall, not a report.
- **Fresh ≠ lazy.** A PR opened this morning with checks running is in flight. Judging it
  as "stopped short" trains the operator to ignore the band that matters.
- **Blame the state, not the agent.** "Codex thread unresolved at `store.rs:88`" — not
  "the agent was careless". The state is checkable; the adjective isn't.
- **Never suggest a bare merge.** Merges go through the gate flow, full stop. The sweep's
  strongest possible recommendation is a mint request.
- **Pers by default.** Day-job is a collapsed count behind `--scope all`. Never label a
  portfolio repo with the employer name.
- **No process narration.** Don't say "I queried 18 PRs, then checked threads". Show the board.
- **PR numbers, `file:line`, bot names, ages are first-class.** Adjectives aren't.

## Where it sits

Observability plane — read-only, storeless views over State. Pick by question:

- `/status` — **this session**, situational recap.
- `/wip` — **whole portfolio, all stores**: ship runs + dossier tasks + PRs, ranked by liveness.
- `/pr-sweep` (← this) — **PRs only, depth-first**: per-PR accountability, whose move, why not merged.
- `/shipped` — **just past**: retrospective on what landed.

`/wip` tells you a PR is open. `/pr-sweep` tells you *why it still is*.

Natural follow-ons, all operator-invoked: 🟡 band → `/chip` a `/drive <repo>#<n> — done =
parked on readiness`; a messy panel → `/review-digest N` then `/review-coordinator N`;
🟢 band → mint, then `gate gate`; ⚫ band → close.

## Source material

- `/drive` — the safe-boundary contract this sweep audits against.
- `/wip` — sibling board; keep the two distinct (liveness vs accountability).
- `/review-coordinator`, `review-digest` — where a messy panel goes next.
- `/chip` — how the operator spins a fix off; the sweep names candidates only.
- Global agent instructions (`CLAUDE.md`/`AGENTS.md`) — merge gate flow (operator mints, agent never does; `-state ~/dev/gate/state`).
