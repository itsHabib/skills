---
name: kickoff
description: Turn a task, spec, or code area into a code-anchored kickoff.md and a paste-ready handoff prompt. First detect existing grounding; DISTILL a reviewed spec, dossier task, or design review, EXPLORE unfamiliar code with read-only agents when grounding is thin, or use HYBRID for the gaps. Write docs/features/SLUG/kickoff.md, verify file:line anchors, and link it as a dossier artifact when a task exists. Use for "write a kickoff", "hand this off", "distill this task into a brief", "explore X and hand it off", or /kickoff. Supersedes /brief. For POC and build handoffs, not designs that need review before implementation; use /tdd for those.
argument-hint: "[dossier task / spec / code area to hand off] — e.g. /kickoff the p2-netns-veth-allocator task"
user_invocable: true
---

# /kickoff — turn a task, spec, or area into a rippable handoff

Turn "prep this so someone else — a fresh session, a Fable POC run, a delegated build — can
start *inside* the work instead of rediscovering it" into a repeatable move. The deliverable
is always two things: a dense, code-anchored orientation doc written to disk, and a
paste-ready prompt that boots the next agent off that doc.

This is for POC / build handoffs. It is deliberately NOT a TDD: no rollout plan, no phased
tasks, no design gate. If the work needs a *reviewed design before anyone builds*, that's
`/tdd`, not this.

The one thing that makes `/kickoff` more than "write a doc": it **matches effort to what
already exists**. A task that already has a reviewed spec + a dossier entry + a design review
does not need a fresh exploration fan-out — it needs *distillation*. An unfamiliar corner of
the codebase with nothing written needs the opposite. Step 2 routes between them.

## 1. Scope the target (one exchange, then go)

From the argument, pin down the handoff target and restate it in one line so you can
correct cheaply. If it's obvious, just proceed — don't interrogate. Only ask if genuinely
ambiguous (which subsystem, which repo, which of two tasks).

## 2. Detect the grounding — pick the mode

Before exploring anything, look for durable grounding that already answers "what is this and
where does it live." Check, cheaply and in parallel:

- **A dossier task or phase** matching the target. Dossier has no direct `task_get` verb:
  call `project_list`, then `project_get` for the candidate projects and scan their phases and
  tasks. A task body often already carries scope, acceptance, and anchors.
- **A spec / design doc** — `docs/features/<slug>/spec.md`, a linked TDD, a kickoff already
  present, or any design doc the task references.
- **A design review** — prefer the consolidated review verdict. Review notes, a `§Review
  revisions` section, PR threads, and channel review posts are finder evidence: retain only
  accepted, still-applicable findings; discard rejected, resolved, or superseded ones.
- **Recent conversation context** — if this same session already explored/spec'd/reviewed the
  work (as often happens right after `/tdd` or a review), that IS the grounding.

Then route:

- **Rich grounding exists → DISTILL (§3A).** Do not re-explore what's already written. Read the
  authoritative sources, extract, and *verify the anchors still resolve*.
- **No / thin grounding → EXPLORE (§3B).** Fan out read-only exploration to build the map from
  the code itself.
- **Partial grounding → HYBRID.** Distill what exists; spike-explore only the genuine gaps the
  grounding leaves open. Don't re-derive what the spec already settled.

State which mode you picked in one line ("distilling from the spec + review" / "no spec —
exploring cold") so you see the call.

## 3A. Distill mode (grounding exists)

Read the spec / task body / review and pull out what a builder needs, in their source's own
terms. You are compressing and code-anchoring, not re-deciding:

- **Goal + scope boundaries** — in-scope vs explicitly-out-of-scope (a good spec already draws
  this line; carry it verbatim — it's what keeps the handoff from sprawling).
- **The constraints that already have answers** — decisions the spec/review locked (e.g. "use a
  separate chain," "reuse these primitives," "this must stay byte-for-byte unchanged"). Number
  them if the review did.
- **The code to mirror / touch**, each with a `file:line` anchor — and **verify every anchor
  still resolves** before writing it down (open the file, confirm the symbol is there). A spec
  written weeks ago drifts; a wrong anchor wastes the next agent's first hour.
- **Acceptance / definition of done** — lifted from the spec, made concrete and checkable.
- **The sharp edges** — accepted, still-applicable findings from the consolidated verdict are
  bail-points; fold them in as "where this gets hard." Never promote every raw reviewer comment
  into a constraint.

Distill mode does NOT spawn a cold exploration fan-out. If you find the grounding is thinner
than it looked (anchors don't resolve, scope is vague), drop to hybrid and spike the gap.

## 3B. Explore mode (unfamiliar area, no grounding)

Map the area from the code. For anything non-trivial, fan out parallel read-only Explore
agents rather than reading serially — one per distinct sub-area (engine vs data model vs
orchestration path). Give each a concrete brief: what to answer, which files to start from,
and "report `file:line` anchors + gaps you actually saw in code, not speculation."

Capture: the real end-to-end flow with anchors; the data model / key types a reader must hold;
the concrete weak spots / bail-points / TODOs / silent failures quoted from code (the
highest-value payload — they tell the next agent where to push); and the honest unknowns you
did NOT trace (which set the first spike). **Verify anchors before writing them.**

## 4. Write the kickoff to disk

Write `docs/features/<slug>/kickoff.md` (kebab-case slug from the target; if the work already
lives under a feature dir, put it there beside the spec). Dense, skimmable, anchored — a page
or three. Adapt the shape to the mode; don't pad:

- **Audience line** ("the implementing agent — rip this and build; it's self-contained") + a
  status/grounding marker naming the source docs to read first.
- **Goal in one line** + **what you're building AND explicitly NOT building** (scope boundaries).
- **Distill mode adds:** the locked constraints (numbered), the code-to-mirror/touch with
  anchors, acceptance / definition of done.
- **Explore mode adds:** how it works today (flow + key types), the phase-0 spike (the one
  unknown to resolve before committing to an approach), an honest success metric.
- **Both:** the concrete weak spots / bail-points, each with a `file:line` — the starting
  targets.
- **A ready-to-paste handoff prompt** at the bottom (also emitted in chat per §6).

Respect repo doc conventions. Where `docs/` is local-only / untracked, the doc stays local —
never stage it. Don't invent LOC targets or wave labels unless the grounding already set them.

## 5. Link it (when a task exists)

If the target maps to a dossier task, link the doc as an artifact
(`mcp__dossier__artifact_link` kind `doc`, anchored to the task) so the handoff is discoverable
from the corpus, and drop a one-line note on the task that the kickoff exists.

## 6. Emit the handoff prompt

In chat (not only in the file), produce a paste-ready prompt for the next agent. It must:
- Point at `docs/features/<slug>/kickoff.md` as the starting data, and tell the agent to trust
  its anchors but verify before building on them.
- Restate the goal and the scope boundaries (what NOT to touch).
- Name the first thing to do — the phase-0 spike (explore mode) or "start with the constraints
  in §X and the first sub-task" (distill mode).
- State the deliverable + definition of done, and (if the repo is gated) the review/merge path.

Keep it tight — a prompt, not an essay. The doc carries the detail; the prompt carries the
intent and the entry point.

## Anti-triggers

- Needs a *reviewed design before build* → `/tdd` (which can hand off to `/kickoff` after).
- Just "what does this code do" for your own understanding, no handoff → answer
  inline; don't write a doc.
- Driving the work to done yourself, not handing it off → `/drive` or `/work-driver`.
- Cataloging which skills exist → `/skills`.
