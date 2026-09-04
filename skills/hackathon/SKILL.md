---
name: hackathon
description: >-
  Run a build competition — turn a topic + 2-5 idea one-liners into a hackathon pack (house-rules README with a 100-point rubric + one self-contained entry brief per idea), emit one launch prompt per entry for N independent fresh sessions, and after entries land generate a blank scorecard for YOU to fill. The skill never scores entries — judging is the human's job. Use when you say "run a hackathon on X", "hackathon this", "set up a bake-off", "have N entries compete on X", "spin up competing builds", "another round", or invoke /hackathon (alias: /hackathon-seat) with prep, launch, or judge.
argument-hint: "[prep <ideas | ideation-doc-path> | launch | judge] — bare /hackathon infers the verb from the pack's state"
user_invocable: true
---

# /hackathon — one topic, N independent entries, you judge

Healthy competition as a harness: several fresh sessions build against the same
house rules and the same rubric, nobody sees anybody else, and you
picks the winner from demos. All the determinism is front-loaded into the pack
— rules and rubric are fixed before any build starts — and there is zero
orchestration machinery after that. Rounds are cheap; run another whenever.

The genre this is NOT: a deterministic workflow runner with an automated
judge. That is a different tool; don't grow this skill toward it.

Three verbs, usually hours-to-days apart. Bare `/hackathon`: no pack for the
topic at hand → prep; pack exists, entries not started → launch; entries
landed → judge.

## prep — write the pack

Collect (one question round max; defaults in brackets):

- topic + 2–5 idea one-liners, or a path to an ideation doc to pull them from
- target docs dir for the pack [`docs/hackathon/` in the current repo]
- repo prefix [`hack-`]
- machine constraints: keyless? which local model, if any? anything known-broken
  worth warning every entry about? [keyless; whatever ollama serves; nothing]
- rubric weight tweaks [house rubric below]

Then write `README.md` from the house template plus one `entry-<slug>.md` per
idea. Expand each one-liner into a brief a fresh session can build from with
zero other context — every path absolute, every constraint restated, nothing
that assumes this conversation. Scope each brief so its demo is buildable in
one session; the "What NOT to build" section is where you earn your keep. Mark
domain facts you're unsure of with TODO rather than inventing confidently.

### Five load-bearing rules — parameterize the details, never delete the rule

1. **One session, one fresh repo** at `~/projects/<slug>`. Entries never share
   context, code, or progress reports.
2. **Correctness is computed, never model-judged.** Grading, matching, gating,
   budgets live in deterministic, tested code; a model (if used at all) does
   phrasing only.
3. **No spec, no design doc.** README + working demo + tests on the policy
   layer only. Simplify until it hurts.
4. **Keyless and local** unless you say otherwise — the demo must
   run on this machine with what's already here.
5. **Finish line:** (a) README with one command to run, (b) a canned demo mode
   needing no live input so judging is hands-free, (c) `DEMO.md` — the exact
   60-second walkthrough, (d) local green: build/vet/tests pass.

### House rubric (100 points; weights adjustable, slots are not)

- **30 — the 60-second demo.** Does a person watching get it, and does it land?
  Canned mode counts; a live moment that works is a bonus.
- **25 — would someone pay.** Named buyer, evidence money already moves in the
  space. Assert it in DEMO.md; the judge will push back.
- **20 — deterministic share.** How much of the correctness path is real code
  with tests vs model vibes. Show the test file.
- **15 — <topic>-necessity.** If it would be just as good as the obvious
  alternative form, it loses these points. Name the alternative in the README
  (for voice entries it was "a text app"; pick the topic's equivalent).
- **10 — restraint.** Small LOC, no seams for futures that don't exist,
  deleted requirements > built mechanisms.

Tie-breaker: which repo would you actually open again next week.

### README template

```markdown
# <Topic> hackathon — <N> entries, independent sessions, you judge

<N> self-contained briefs. Each goes to a FRESH session that has never seen
the others — do not share context between entries. Every entry ends in a
runnable demo you can judge in under five minutes, hands-free.

## Entries

| # | slug | bet |
|---|------|-----|
| 1 | `<prefix><slug>` | <one-line bet> |

Launch one per session with:

> Read <pack-dir>/entry-<slug>.md and build it. You are one of <N>
> independent entries; you win by demo, not by design.

## House rules (same for every entry — fairness is the point)

- **One session, one repo.** Scaffold at `~/projects/<slug>`. <stack bias, e.g. Go
  stdlib or plain Node; vanilla web UI>; NO build steps, NO frameworks, NO
  new deps unless unavoidable.
- **Keyless and local.** <what exists on this machine, what doesn't, how to
  reach the local model if any. If an idea "needs" a better model, the demo
  must work without one and merely note the upgrade path.>
- <known machine breakage, so no entry burns time rediscovering it — omit if none>
- **Correctness is computed, never model-judged.** Any grading, matching,
  gating, or budget lives in deterministic, table-tested code. The model (if
  used at all) is phrasing only. House invariant, every entry.
- **No spec, no design doc.** README + working demo + tests on the policy
  layer only. Simplify until it hurts.
- <optional: "steal mechanism, not architecture" pointers into existing repos>
- **Required at the finish line:** (a) README with one command to run, (b) a
  scripted/canned demo mode that needs no <live input> so the judge runs it
  hands-free, (c) `DEMO.md` — the exact 60-second walkthrough, (d) local
  green: build/vet/tests pass.

## Judging (yours, after all <N> land)

100 points:
<the rubric above, with the -necessity slot named for this topic>

Tie-breaker: which repo would you actually open again next week.

## After judging

Winner gets the follow-through: <your call — deeper brief, live
session, whether it earns a spec>. Losers keep their repos as reference —
nothing gets ported into a platform.
```

### Entry brief template

```markdown
# Entry <n>: <prefix><slug> — <one-line title>

Read <pack-dir>/README.md first — house rules and judging apply verbatim.
Repo: `~/projects/<prefix><slug>`. You never see the other <N-1> entries.

## The bet
<Why this might win: the pain, who has it, why now, the wedge. 3-6 sentences.>

## What to build
<The ONE scenario. Be specific about which part is deterministic code (that
part is usually the product) vs model, what the visible surface is, and the
moment the demo turns on. TODO-mark uncertain domain facts.>

## What NOT to build
<Adjacent features cut by name. No accounts, no persistence beyond the
session, no integrations that aren't the demo. Guardrails against
re-inflating.>

## Canned demo (required)
<The scripted run needing no live input; what the judge watches it do/catch.>

## The 60-second demo story
"<First-person walkthrough the builder refines into DEMO.md — the pitch
spoken over the demo.>"
```

## launch — one prompt per entry, one fresh session each

Emit N paste-ready prompts, one per brief:

> Read <absolute path to brief> and build it. You are one of <N> independent
> entries; you win by demo, not by design.

That's the whole mechanism — you paste each into its own fresh
session on whatever surface. If this session's UI has chips
(`mcp__ccd_session__spawn_task` available), offer one chip per entry as a
convenience — title `Build <slug> — hackathon entry`, prompt = the launch
prompt, cwd = the repo holding the pack — but the prompts are the deliverable,
chips are sugar.

Independence is the harness: never launch two entries from one session, never
relay one entry's progress into another, don't "check in" on running entries.

## judge — blank scorecard, human pen

When you say entries are in, write `scorecard.md` next to the pack
README: one column per entry, one row per rubric line, every score cell blank,
a notes row, tie-breaker and winner lines at the bottom. The one row you may
fill is the finish-line checklist (repo exists / README run command / canned
demo present / DEMO.md present / local green) — that's computable fact, so
verify it by looking, not by trusting the entries' claims. Scores, ranking,
and the winner are yours; never suggest them, even as "preliminary".

```markdown
# <Topic> hackathon — scorecard

| Criterion (weight) | <slug-1> | <slug-2> |
|---|---|---|
| Finish line (README / canned demo / DEMO.md / green) | | |
| 60-second demo (30) | | |
| Would someone pay (25) | | |
| Deterministic share (20) | | |
| <topic>-necessity (15) | | |
| Restraint (10) | | |
| **Total (100)** | | |
| Notes | | |

Tie-breaker — which repo would you open again next week: ____
Winner: ____
```

## Rounds

Round N+1 is just prep again — new ideas, or the survivors sharpened, into a
fresh pack dir (`docs/hackathon-r2/` or similar), same five rules. Winner
follow-through (research brief, live session, whether it earns a spec) belongs
to you, outside this skill.

## What this skill refuses to grow

No automated judging or scoreboards, no orchestration engine (that design
belongs in a separate workflow runner), no team/phase machinery, no
cross-entry communication, no
shared libraries between entries, no plugin seams. A requirement deleted beats
a mechanism added — inside the packs and inside this skill.
