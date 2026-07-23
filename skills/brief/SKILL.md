---
name: brief
description: Explore an unfamiliar code area and produce a code-anchored kickoff brief plus a ready-to-paste handoff prompt for another agent. Fans out read-only exploration over the target subsystem, maps the real flow with file:line anchors, surfaces the concrete weak spots / bail-points, then writes a local exploration doc under docs/features/<slug>/kickoff.md AND emits a handoff prompt that points the next agent at that doc as its starting data. Use when you say "get me a brief on X", "write a kickoff for X", "explore X and hand it off", "prep a doc for an agent to start on X", "brief this so someone else can pick it up", or invoke /brief <area or task>. For POC/exploration handoffs — NOT a full design doc (no rollout plan, no design gate); reach for /tdd when the work needs a reviewed design before build.
argument-hint: "[code area or task to brief] — e.g. /brief the auth middleware layer"
user_invocable: true
---

# /brief — explore a code area and hand it off

Turn "go understand this part of the code and prep it so someone else can start inside the
code instead of rediscovering it" into a repeatable move. The deliverable is two things: a
code-anchored orientation doc written to disk, and a paste-ready prompt that boots the next
agent off that doc.

This is for POC / exploration handoffs. It is deliberately NOT a full design doc: no rollout
plan, no phased tasks, no design gate. If the work needs a reviewed design before anyone
builds, that's `/tdd`, not this.

## 1. Scope the target (one exchange, then go)

From the argument, pin down what to explore. If the area is obvious from the prompt, just
proceed - do not interrogate. Only ask if the target is genuinely ambiguous (which of two
subsystems, which repo). Restate the target in one line before exploring so you can be
corrected cheaply.

## 2. Explore read-only, fanned out

Map the area with the search/read tools. For anything non-trivial, fan out parallel
read-only exploration agents rather than reading serially - one per distinct sub-area (e.g.
the engine vs the data model vs the UI/orchestration path). Give each agent a concrete
brief: what to answer, which files to start from, and "report file:line anchors + gaps you
actually saw in code, not speculation."

What every brief must end up capturing:
- The real flow, end to end, with `file:line` anchors (clickable).
- The data model / key types a reader needs to hold.
- The concrete weak spots, bail-points, TODOs/FIXMEs, silent failures - quoted from code,
  not guessed. These are the handoff's highest-value payload: they tell the next agent
  where to push.
- The honest unknowns - what you did NOT trace and why it matters (sets the first spike).

Verify anchors before writing them down. A wrong `file:line` in a handoff doc wastes the
next agent's first hour.

## 3. Write the brief to disk

Write `docs/features/<slug>/kickoff.md` (kebab-case slug from the target). Keep it to a page
or two of orientation - dense, skimmable, anchored. Suggested shape (adapt, don't pad):

- **Goal in one line** + a `Status: exploration / POC` marker.
- **The framing / concept** you're chasing, if any (state it in plain words).
- **How it works today** - the flow with anchors, the key types.
- **The concrete weak spots / bail-points** - the starting targets, each with a `file:line`.
- **Phase-0 spike** - the one unknown to resolve before committing to an approach.
- **Success metric** - what "done" looks like for the POC, honestly (gradeable, not binary
  where the truth is a gradient).

Respect the repo's doc conventions. In repos where `docs/` is local-only / untracked, this
doc stays local - never stage it. Do not invent LOC targets, diff-size limits, or wave
labels. New README sections (if any) go at the bottom.

## 4. Emit the handoff prompt

In chat (not a file, unless asked), produce a paste-ready prompt for the next agent. It must:
- Say this is exploratory / POC / throwaway-friendly up front.
- Point at `docs/features/<slug>/kickoff.md` as starting data, and tell the agent to trust
  its anchors but verify before building on them.
- Restate the goal and any concept framing.
- Name the phase-0 spike as the first thing to do, and ask the agent to report back before
  committing to an approach.
- State the deliverable + success metric.

Keep it tight - a prompt, not an essay. The doc carries the detail; the prompt carries the
intent and the entry point.

## Anti-triggers

- Needs a reviewed design before build → `/tdd`.
- Just "what does this code do" for your own understanding, no handoff → answer inline;
  don't write a doc.
- Cataloging which skills exist → `/skills`.
