---
name: self-play
description: Exploratory lab skill — set up and run an inference-time self-play loop (generator vs adversarial verifier with a decidable win condition) for a task, via a guided interview. We are still LEARNING when this beats a straight pass, so every run is an experiment - it runs a baseline comparison by default and appends a verdict to the lab log. Use when the operator says "self-play this", "set up the game for X", "run this adversarially" (as a full loop, not a one-off review), "attacker/defender this task", or invokes /self-play [task]. NOT for one-shot review of an existing diff (/code-review) or the PR bot panel (/review-coordinator) — this is generate→attack→fix→repeat on work being produced.
user_invocable: true
---

# /self-play — set up a generator-vs-verifier game

A self-play loop is three things, none of which is a literal game board:

1. **Two roles in opposition.** A defender produces the artifact. An attacker — fresh
   context, blind to the defender's reasoning, ideally a different model family — is
   rewarded for breaking it, never for approving it.
2. **A decidable win condition.** Some check that scores a round without anyone's
   judgment: a test crashes, a script exits non-zero, a blind judge with a rubric rules
   on evidence. If the win condition is "sounds good," there is no game.
3. **Iteration with banked residue.** Fix what scored, re-attack, terminate when the
   attacker comes up dry twice. Every attack that ever scored becomes a permanent test
   case / rule / checklist line — that's the consolidation step, stored in files instead
   of weights.

**This skill is a lab.** We don't yet know which tasks the ceremony pays off on. So:
default to the smallest game that could work, run a straight-pass baseline alongside,
and log an honest verdict every time.

## Phase 0 — read the lab log

Read `LOG.md` next to this file. Tell the operator in one or two sentences what past
runs concluded (task shapes that won, shapes that were overhead). If a past run already
covers this task shape, say so — maybe we skip the baseline this time, or skip the game.

## Phase 1 — construct the game (interview)

Use the harness's available user-input surface. The interview's real job is **coaching the win condition into
existence** — everything else is defaults.

1. **The task.** What artifact are we producing? (From `$ARGUMENTS` if given.) If the
   artifact already exists and they want it attacked, that's fine — the loop starts at
   the attack step.
2. **The win condition.** Ask: "how would we know an attempt is wrong, without trusting
   the model's word?" Walk the ladder top-down and push hard for the highest rung:
   - **Mechanical** — test suite, compiler, schema check, script exit code. Best.
   - **Empirical** — run it and observe (screenshot, hit the endpoint, real data).
   - **Blind adversarial** — no oracle exists; a judge agent rules on a written rubric
     with evidence quotes. Weakest — offer to write the rubric with them first.

   If nothing on the ladder is constructible, **say self-play doesn't apply here**, the
   operator stays the verifier, log that finding, and stop. That's a valid lab result.
3. **The attacker's brief.** What does the attacker see (spec but not implementation is
   the default), and what counts as a scored point? Must be phrased as an attack
   ("produce an input that breaks it", "construct a state where the gate wrongly
   passes"), never as a review.
4. **Scale + models.** Defaults unless the operator overrides:
   - v0 game: 1 defender, 1–2 attackers, hard cap 3 rounds, terminate early on 2 dry rounds.
   - Models: defender inherits the session model; attackers = fresh blind instances,
     down-tier (sonnet) when the attack is search-shaped, cross-family (bot panel) when
     available and the artifact is a PR; judge (if rung 3) = strongest tier until a
     smoke test shows the verdict is tier-insensitive.
   - Baseline: also produce one straight-pass attempt (same defender prompt, no loop) so
     the debrief can compare. Default ON while we're learning; skip only if the log
     already settled this task shape.

## Phase 2 — the game sheet

Print a compact game sheet and get one confirm before spending:

```
GAME: <task, one line>
WIN CONDITION: <check + how a round is scored, decidable>
DEFENDER: <model/effort> — sees <...>
ATTACKER(S): <n> × <model/effort> — sees <...>, scores by <...>
ROUNDS: max 3, stop on 2 dry
BASELINE: <on/off>
RESIDUE PLAN: where surviving attacks get banked (test file / rule / doc)
```

## Phase 3 — run it

Small games: plain Agent calls (defender agent, then attacker agents in parallel, blind
— never paste the defender's reasoning into the attacker prompt). Bigger fan-outs (≥3
attackers or multi-stage): a Workflow with per-stage `model`/`effort`, attack results
scored by the win condition, loop in script.

Between rounds, show the operator the score: what the attacker found, one line each.
The win condition referees — you don't overrule it in either direction.

## Phase 4 — debrief + bank + log

1. **Scorecard vs baseline:** what did the loop catch that the straight pass missed
   (and vice versa)? Rough cost (rounds, agents).
2. **Verdict:** `game-won` / `tie` / `overhead` — honest, one line of why.
3. **Bank the residue** per the game sheet: scoring attacks → permanent test cases;
   recurring fix classes → a lint/rule/CLAUDE.md line. Residue nobody will re-run is
   not residue — put it where the check actually fires.
4. **Append to `LOG.md`:**

```
## <date> — <task, one line>
- win condition: <rung + what it was>
- setup: <defender/attackers/models/rounds used>
- attacker found: <n scored attacks, headline ones>
- vs baseline: <what the loop uniquely caught, or "nothing">
- verdict: game-won | tie | overhead — <why, one line>
- residue: <where it was banked>
- lesson: <one line that should change the NEXT run's defaults>
```

If a lesson generalizes (e.g. "task shape X: skip the game"), fold it into the defaults
in Phase 1 of this file — the skill is itself under the consolidation rule.
