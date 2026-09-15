---
name: hackathon
description: >-
  Run a build competition where the judge re-runs everything. Turn a topic plus 2-10 idea one-liners into a pack (house rules, rubric, one self-contained brief per entry on a distinct domain x archetype cell), launch one fresh isolated builder per entry (paste-ready prompts or background agents in their own worktrees), then judge by re-running every entry's test and demo commands from clean, applying an honesty multiplier to self-reports, and proposing PROMOTE / SEED / PARK / DROP on one SCOREBOARD.md you ratify. Two modes: standalone (fresh repo per entry) or repo (one git worktree per entry inside an existing repo, for POCs against a real product surface). Use when the user says "run a hackathon on X", "bake-off", "have N entries compete", "spin up competing builds", "get me N POCs of X", "another round", or invokes /hackathon with prep, launch, judge, or archive.
argument-hint: "[prep <topic> <ideas | ideation-doc-path> [--mode standalone|repo] | launch [--spawn] | judge | archive] - bare /hackathon infers the verb from the pack's state"
user_invocable: true
---

# /hackathon - one topic, N isolated entries, a judge that re-runs, you ratify

Healthy competition as a harness. Several fresh builders work the same house
rules and the same rubric, nobody sees anybody else, every entry ends in a
facts-only result contract, and a judge re-runs each one from clean before any
score exists. Determinism is front-loaded into the pack; the only machinery
after that is the barrier before judging.

Proof point this generalizes: a 10-slot run on 2026-06-30 produced 10/10
verified green (judge re-ran every suite with a cold cache), zero dishonest
self-reports, three promoted. The earlier agent-orchestrated attempt at the same
run silently dropped one slot and never ran the judge, which is why the barrier
and the re-run are rules, not suggestions.

## The loop at a glance

    prep     topic + ideas  ->  pack: README (rules, rubric), one brief per entry, anti-clone grid
    launch   one fresh isolated builder per brief (paste prompts, or spawn background agents)
             each ends in RESULT.json (facts) + test-output.txt (verbatim)  ->  RUN.md ledger
    judge    barrier: every slot terminal  ->  re-run test_cmd + demo_cmd from clean
             -> honesty multiplier -> PROMOTE / SEED / PARK / DROP -> SCOREBOARD.md
    you      ratify the scoreboard; promote winners (repo mode: a draft PR from hack/<slug>)
    archive  freeze the wave on a shelf with its rules, scorecard, and per-entry briefs

Bare `/hackathon` picks the verb from the pack state:

| State | Verb |
|---|---|
| no pack for this topic | prep |
| pack exists, RUN.md empty | launch |
| every slot terminal in RUN.md | judge |
| SCOREBOARD.md ratified | archive |

## Taking pieces without taking the skill

Each part stands alone. Steal in this order of payoff:

1. **Judge re-runs from clean.** Nothing is green until a separate agent ran
   the suite itself. Drop this into any "N agents tried X" workflow first.
2. **Facts-only result contract.** `RESULT.json` with commands, counts, and
   status, never a self-score. It makes completion and comparison mechanical.
3. **Hard barrier.** Judge only when every slot is done, failed, or recorded
   as never-started. Prevents the silent-drop failure.
4. **Anti-clone grid.** One distinct (domain x archetype) cell per builder.
5. **Honesty multiplier.** Claimed green, re-ran red: x0.4, cannot promote.
6. **Stub-kill test.** One test that goes red when the core is stubbed, so a
   green suite certifies the interesting part.

## The rules that never move

Parameterize the details of each; never delete the rule.

1. **One builder, one cell, one isolated checkout.** Standalone mode: a fresh
   repo per entry at `~/projects/<slug>`. Repo mode: one git worktree per entry on
   branch `hack/<slug>`. Entries never share context, code, or progress
   reports, and never write above their own folder.
2. **Correctness is computed, never model-judged.** Grading, matching, gating,
   budgets live in deterministic, tested code. A model, if used at all, does
   phrasing only. Every entry ships at least one stub-kill test: a test that
   fails if the core mechanism is ripped out or stubbed.
3. **Facts, not self-scores.** Every entry ends in `RESULT.json` (facts only)
   plus a verbatim `test-output.txt`. Builders never grade themselves. A
   "tests pass" claim with no captured run is a failed entry.
4. **The judge re-runs from clean, then scores.** Nothing is green until the
   judge's own re-run exits 0. Self-reports are claims to verify.
5. **Mechanism, not apparatus.** No spec, no design doc, no frameworks, no
   seams for futures that don't exist. Negative controls and demo scaffolding
   stay local and are reported in `RESULT.json`, never committed. Simplify
   until it hurts.

## prep - write the pack

Collect in one question round at most (defaults in brackets):

- topic, plus 2-10 idea one-liners or a path to an ideation doc to pull them from
- mode [`standalone`]: `standalone` = fresh repo per entry; `repo` = one
  worktree per entry inside the repo at `<repo-root>`, for POCs against a
  real product surface
- pack dir [`docs/hackathon/<topic-slug>/` in the current repo, or
  `~/hackathons/<YYYY-MM-DD>/` when there is no repo]
- machine constraints: which toolchains are verified present, which are known
  broken, keyless or which local model [keyless; nothing known broken]
- rubric weight tweaks [house rubric below; slots fixed]

### Anti-clone grid

N builders from the same distribution converge on the same idea. Assign each
entry a distinct (domain x archetype) cell before writing briefs. The seed idea
is inspiration only; the cell is binding. Banned in every wave: a bare to-do
agent, a bare "chat with your docs" clone, a thin wrapper with no real logic.

| Slot | Slug | Domain | Archetype | Seed idea (optional) |
|---|---|---|---|---|
| 01 | `<slug>` | <domain> | <archetype> | <one line> |
| 02 | `tracelens` | agent observability | trajectory analyzer | JSONL agent trace in, loops / retry storms / cost hotspots out, one fix per finding |
| 03 | `warden` | security | capability guard | deny-by-default policy over proposed tool calls, returns allow/deny + matched rule |

Pin or allow-list a stack per cell when diversity matters. On 2026-06-30 all
ten entries rationally picked the default stack; monoculture is an artifact of
an unstated default, so state one per cell or accept it.

### Repo mode specifics

- Each entry works only inside its worktree:
  `git worktree add <repo-root>/.claude/worktrees/hack-<slug> -b hack/<slug> origin/main`.
- The demo runs against a fixture committed on the branch (a recorded input,
  a seeded sqlite file, a captured payload). No live services, no prod data.
- Entry edits stay inside its worktree. Shared config, CI, and root files are
  off limits unless the brief names them.
- The graduation path for a repo-mode winner is a draft PR from `hack/<slug>`,
  with the negative controls and scaffolding stripped first.

### Pack files

Write `README.md` from the template below and one `entry-<slug>.md` per idea.
Expand each one-liner into a brief a fresh session can build from with zero
other context: every path absolute, every constraint restated, nothing that
assumes this conversation. Scope each brief so its demo is buildable in one
session. The "What NOT to build" section is where you earn your keep. Mark
domain facts you are unsure of with TODO rather than inventing confidently.

### Rubric (100 points; weights adjustable, slots are not)

- **25 - verified green.** The judge's own re-run of `test_cmd` from clean
  exits 0 and the suite is non-trivial.
- **25 - the 60-second demo.** `demo_cmd` runs hands-free on a built-in
  example and a person watching gets it. Real code paths, no canned output.
- **20 - would someone use it.** Named user, evidence the pain is real.
  Assert it in `PITCH.md`; the judge pushes back.
- **15 - mechanism depth.** A real loop, router, planner, judge, policy, or
  critique path doing the work, not a wrapper. Includes the stub-kill test:
  the judge stubs the core and confirms the suite goes red.
- **10 - restraint.** Small LOC, stdlib-first, deleted requirements beat
  built mechanisms, no seams for futures.
- **5 - legibility.** One-screen README, honest rough edges, `NEXT.md` for
  parked scope.

Floor to graduate: 75 total, plus mechanism depth at least 10 and would-use
at least 14. Tie-breaker: which entry would you would open again next week.

### README template

```markdown
# <Topic> hackathon - <N> entries, isolated builders, judge re-runs, you ratify

Mode: <standalone | repo (<repo-root>)>. Pack: <pack-dir>.

## Entries (anti-clone grid)

| Slot | slug | domain | archetype | bet |
|---|---|---|---|---|
| 01 | `<slug>` | <domain> | <archetype> | <one line> |

## House rules (same for every entry)

- One builder, one cell, one isolated checkout: <`~/projects/<slug>` | worktree
  `<repo-root>/.claude/worktrees/hack-<slug>` on `hack/<slug>`>. Create,
  edit, delete files only inside it. Never read or print anything outside it,
  never touch secret or dotfiles, no `../` imports, no cross-entry references.
- Stack: <verified present: ...; known broken: ...; preference order>. The
  canonical test command is the language-native runner. Stdlib-first; justify
  any dependency in the README; no frameworks, no code generation, no
  network at test time. Caps: ~600 LOC, 12 source files, 2 dependencies.
- Correctness is computed, never model-judged. Any grading, matching, gating,
  or budget lives in deterministic, table-tested code. Ship at least one
  stub-kill test.
- No spec, no design doc. README + working demo + tests on the policy layer.
- Mechanism, not apparatus: negative controls and demo scaffolding stay local
  and are listed under `whats_local` in RESULT.json, never committed.
- Budget discipline: vertical slice first, tree never red between steps. At
  ~20% budget left, stop adding, make what exists pass, park the rest in
  NEXT.md. If you cannot finish green, cut scope and say so.
- Neutral naming only. No employer, customer, or vendor names.

## Deliverables (exact names; not done until all exist)

    README.md        one screen: cell, one-line pitch, the mechanism hook,
                     how to run (exact test + demo commands), sharp / rough
    PITCH.md         problem, who it is for, why it could graduate, honest limits
    NEXT.md          parked scope
    RESULT.json      facts only (schema below), written as the final step in
                     EVERY terminal state, including failure
    test-output.txt  verbatim output of your real test run
    DEMO.md          the exact 60-second hands-free walkthrough
    <source + tests>

RESULT.json schema (no subjective self-score; the judge scores):

    {
      "slot": "01", "slug": "<slug>", "one_liner": "...",
      "domain": "...", "archetype": "...", "stack": "go",
      "mechanism_hook": "which code path IS the mechanism",
      "test_cmd": "go test -count=1 ./...", "demo_cmd": "go run ./cmd/demo",
      "stub_kill_test": "TestRouterRefusesWhenPolicyStubbed",
      "self_reported": "green" | "red", "build_ok": true,
      "tests_total": 24, "tests_passed": 24, "loc": 610,
      "status": "done" | "failed", "reason": "one line if failed",
      "whats_stubbed": ["..."], "whats_local": ["negative controls", "fixtures"],
      "graduate_pitch": "one sentence"
    }

Filled example from a real entry:

    {
      "slot": "05", "slug": "tracelens", "one_liner": "agent trace in, ranked loop/cost findings out",
      "domain": "agent observability", "archetype": "trajectory analyzer", "stack": "go",
      "mechanism_hook": "detect/*.go: each detector walks the step graph and emits evidence steps",
      "test_cmd": "go test -count=1 ./...", "demo_cmd": "go run ./cmd/demo",
      "stub_kill_test": "TestDetectorsFindNothingWhenWalkerStubbed",
      "self_reported": "green", "build_ok": true,
      "tests_total": 22, "tests_passed": 22, "loc": 780,
      "status": "done", "reason": "",
      "whats_stubbed": ["cost table is a fixed map"], "whats_local": ["negative-control traces"],
      "graduate_pitch": "wire as a -json gate on every agent run so loops and retry storms fail CI"
    }

## Judging (after every slot is terminal)

<the rubric above, with weights as set for this wave>
Honesty multiplier and promote signals as in the /hackathon skill.
Floor to graduate: <75>. Tie-breaker: which entry would you open next week.
```

### Entry brief template

```markdown
# Entry <n>: <slug> - <one-line title>

Read <pack-dir>/README.md first; house rules, deliverables, and judging apply
verbatim. Cell: (<domain>, <archetype>). Checkout: <absolute path>. You never
see the other <N-1> entries.

## The bet
<Why this might win: the pain, who has it, why now, the wedge. 3-6 sentences.>

## What to build
<The ONE scenario. Which part is deterministic code (that part is usually the
product) vs model, what the visible surface is, the moment the demo turns on.
TODO-mark uncertain domain facts.>

## What NOT to build
<Adjacent features cut by name. No accounts, no persistence beyond the
session, no integrations that are not the demo.>

## Fixture (repo mode)
<The committed input the demo runs against, and where it lives on the branch.>

## Canned demo (required)
<The zero-arg run needing no live input; what the judge watches it do or catch.>

## The 60-second demo story
"<First-person walkthrough the builder refines into DEMO.md.>"
```

## launch - one fresh builder per entry

Always emit N paste-ready prompts, one per brief:

> Read <absolute path to brief> and build it. You are one of <N> independent
> entries; you win by a verified demo, not by design. Write RESULT.json as
> your final step no matter how you finish.

That is the deliverable; you can paste each into its own fresh session
on any surface. Then offer fan-out from this session:

- `--spawn` (or when asked): spawn one background agent per entry **in a single
  message** with `isolation: "worktree"`, each given only its own brief path
  and the launch prompt. Nothing else from this conversation. In repo mode
  the worktree is the entry's checkout; in standalone mode the agent creates
  `~/projects/<slug>` itself and the worktree is scratch.
- If your client offers one-click task chips, one chip per entry is an
  equivalent convenience.

Record the launch in `<pack-dir>/RUN.md`: slot, checkout, agent or session id
if known, started-at. This is the completion ledger the judge's barrier reads.

Independence is the harness: never relay one entry's progress into another,
never "check in" on a running entry, never merge or reconcile entries.

## judge - hard barrier, re-run, then score

### Barrier first

Judging starts only when every slot in `RUN.md` is terminal: `RESULT.json`
exists (done or failed) or the slot is recorded as `never-started` with a
reason. A slot with a running agent is not terminal; wait or record it. A
slot is never silently dropped. That is the exact failure this verb exists to
prevent.

Backfill is bounded: a never-started or incomplete slot may get at most one
re-dispatch with the same brief. After that, record it and move on.

### Re-run from clean

For each entry, in its own checkout:

1. Check deliverables exist by name. Missing file = note it, keep going.
2. Run `test_cmd` from a clean state (cold cache, fresh clone or `git clean`
   in repo mode). Record exit code, duration, test count. Missing toolchain =
   `UNVERIFIED (<reason>)`, never a guess.
3. Run `demo_cmd`, capture output, confirm it reflects real code paths.
4. Stub-kill check: temporarily neuter the named core path, re-run the suite,
   confirm it goes red, restore. Record the result.
5. Flag any secret access, any write outside the checkout, any `../` import,
   any employer or customer name.
6. Read README, PITCH, NEXT, RESULT. Count LOC.

Report negative controls you ran but do not commit them anywhere.

### Honesty multiplier

| self_reported | judge re-run | badge | effect |
|---|---|---|---|
| green | green | VERIFIED | scored as-is |
| red | red | HONEST-RED | verified-green slot = 0, no penalty, SEED-eligible |
| green | red | DISHONEST | total x0.4, capped at 40, cannot PROMOTE |
| red | green | UNDERCLAIMED | verified-green slot full |

### Promote signals (exactly one per entry)

- **PROMOTE**: VERIFIED and total at or above the floor and mechanism depth
  at least 10 and would-use at least 14. Write a one-line graduation path.
- **SEED**: total at or above 60, or HONEST-RED with a strong core.
- **PARK**: interesting, no clear use.
- **DROP**: dishonest or broken.

### One file: SCOREBOARD.md

Write `<pack-dir>/SCOREBOARD.md`, optimized so you spend under
fifteen minutes: TL;DR (30s), ranked table (3m), top PROMOTE cards (5m),
hands-on demo of one or two (5m), ratify.

```markdown
# SCOREBOARD - <topic> <date>

**<n>/<N> verified green · <m> dishonest · <k> never-started · Proposed PROMOTE: <slugs>**

Judge re-ran every suite from clean (<command>) and every demo. <one line on
the field: stacks, deps, isolation violations, secrets touched.>

## Ranked table

| Rank | Slot | Score | Tests (judge re-run) | Demo | Mechanism | Would use | Badge | Signal | One-line pitch |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05-tracelens | 93 | 22 tests, 0.21s, exit 0 | 24/25 | 14/15 | 18/20 | VERIFIED | PROMOTE | agent trace in, ranked loop and cost findings with a fix each |
| 7 | 03-reapply | 71 | 16 tests, 0.20s, exit 0 | 20/25 | 9/15 | 15/20 | VERIFIED | SEED | fuzzy patch applier, refuses with a typed conflict |
| 10 | 08-gclint | 34 | judge re-run exit 1 | 18/25 | 11/15 | 14/20 | DISHONEST | DROP | self-reported green, suite red on re-run |

## Proposed PROMOTE cards
### <slug> - <score> · <domain> / <archetype>
- Pitch, verified result (tests, duration, exit), stub-kill result, LOC and deps
- Graduation path: <one line; repo mode: draft PR from hack/<slug> after stripping whats_local>
- Demo: `<demo_cmd>`

## Per-entry cards (4 lines each)
What · Mechanism · Verified result · Sharp / Rough · Badge + Signal

## Your ratification
Ratified PROMOTE: ____   Overrides and why: ____   Date: ____
```

The judge proposes; you ratify. Scores and signals are the
judge's computed proposal from the re-run, never "preliminary" guesses and
never the builders' own numbers. The winner line stays blank until the
operator fills it.

## archive - retire the wave to the shelf

After ratification, move the wave to `~/hackathons/archive/<category>-<MM-DD>/`:

- `RULES.md` = the pack README (rules and rubric as they were).
- `SCORECARD.md` = the ratified SCOREBOARD.md.
- `<slug>/BRIEF.md` = the entry brief, travelling with its code.
- `<slug>/` = the entry with regenerable dirs dropped (`.git`, `node_modules`,
  `target`, `.venv`). Repo-mode entries archive as a patch or a branch name,
  not a copy of the repo.
- Add the wave to the shelf README's map with a status per entry: `built`,
  `reference`, `rejected - <floor missed>`, `graduated -> <url>`.

Promotion is the one live path out: copy the folder to `~/projects/<name>`,
`git init`, BRIEF.md becomes the starting spec, tests come along, flip the
status. Repo mode: open the draft PR from `hack/<slug>`.

## Rounds

Round N+1 is prep again: new cells, or survivors sharpened, into a fresh
pack dir. Same five rules. Reweight the rubric per wave if the topic demands
it; the slots stay.

## What this skill refuses to grow

No orchestration engine or run-state daemon: the Claude Code Workflow tool or
a background Agent fan-out already gives fan-out, a completion gate, and a
barrier, and `RUN.md` plus the judge's barrier check is the whole state
machine this needs. No team or phase machinery. No cross-entry communication, shared libraries
between entries, or plugin seams. No model-judged correctness anywhere. A
requirement deleted beats a mechanism added, inside the packs and inside this
skill.
