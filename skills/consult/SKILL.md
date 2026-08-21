---
name: consult
description: Summon another portfolio repo's steward agent and get a same-turn answer to a question about that repo — instead of asking the operator. Use when the user says "ask the <repo> agent", "what does the ship steward think", "consult payments-service about X", or invokes /consult <repo> "<question>". Also use PROACTIVELY mid-task, without being asked, whenever you're stuck on a KNOWLEDGE question about another portfolio repo's behavior, design, or conventions — consult that repo's steward before asking the operator. Only AUTHORITY questions (product direction, spend, irreversible calls) go to the operator.
argument-hint: "<repo> \"<question>\" — repo is a portfolio directory name or path; several repos may be consulted in parallel"
user_invocable: true
---

# /consult — summon another repo's steward

## The model

Every portfolio repo has a steward — the agent that manages it. The steward's
knowledge is not a running process or an open tab; it's the repo itself:
CLAUDE.md, docs/, the dossier project, the code, the git history. Any agent can
summon an ephemeral incarnation of that steward and get an answer within the
same turn. A tab the operator keeps open on that repo is one incarnation of the
steward; your consult is another. Same character, same sources.

## The escalation ladder

When you're stuck, classify the blocker before doing anything:

- **Knowledge about another repo** (how does its API behave, what's its
  convention, why is it designed this way, what's in flight there) →
  **consult its steward.** Never route these to the operator — they would just
  go read that repo anyway.
- **Authority** (product direction, spending money, irreversible or
  outward-facing actions, cross-repo priority calls) → **the operator.**
  A steward can advise; only the operator decides.

Operator attention is the scarcest resource in the system. Peer consults are
free. Exhaust the free channel first.

## Invocation

```
/consult <repo> "<question>"
```

- `<repo>`: a directory under your portfolio root (the directory holding your
  project checkouts) or an explicit path. Fail loud if it doesn't exist — don't
  guess a similarly-named repo.
- Several repos may be consulted at once (e.g. a contract question that spans
  ship and rooms): spawn the consults in parallel, one steward each.

## Mechanics

1. Resolve the repo path.
2. Spawn one subagent per target repo — `Explore` for lookups ("what does verb
   X return"), `general-purpose` when the question needs judgment or synthesis
   ("would this approach fit your design"). Prompt shape:
   - You are the steward of `<repo>` at `<path>` — the agent that manages this
     repo. Answer as its owner.
   - Orient first: read the repo's CLAUDE.md, then whatever docs/ and code the
     question actually demands. For live state (open PRs, CI), read-only `git`
     / `gh` is fine.
   - Answer from the repo's contents; cite files and symbols (never line
     numbers). State unknowns plainly instead of speculating.
   - Include the full question, plus enough of the asking context that the
     steward understands why it's being asked.
3. Relay the steward's answer (with citations) and continue the original task.
   The consult's output is an input to your work, not a deliverable — restate
   what mattered, don't dump the transcript.

## Rules

- **A consult is read-only and leaves no trace.** No writes to the target
  repo, no dossier entries, no huddle posts, no logs. Most consults are
  throwaway lookups; recording them is noise.
- **If the answer surfaces actionable work in the target repo** (a bug, a
  missing doc, a follow-up), that's a real finding — say so in your reply and
  offer to file a dossier task in that repo's project. Don't file silently.
- **If the exchange is genuinely discussion-shaped** — opinion-gathering
  across stewards, no same-turn answer required — a huddle is the right
  channel instead. Only then; don't post a huddle for a lookup that already
  got answered.
- The steward speaks for its repo, not for the operator. If its answer would
  change your task's scope or direction, that's an authority question — take
  it to the operator.
