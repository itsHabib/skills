---
name: pr-risk
description: Route a PR to the right amount of human review — classify a PR's risk so review attention goes where judgment is irreducible and the safe majority clears without a human. Review load should scale with risk, not PR count. Two layers — an optional deterministic floor (a small classifier you provide) plus an agent advisory pass (this skill) that may only escalate, never lower. Use when deciding how much review a PR needs, or invoke /pr-risk <owner/repo#num>.
argument-hint: "[owner/repo#num] — omit to use the current branch vs its base"
user_invocable: true
---

# /pr-risk — route a PR to the right amount of human review

Classify a PR's risk so review attention goes where judgment is irreducible and the safe majority clears without a human. Review load should scale with **risk**, not **PR count**.

Two layers: an optional **deterministic floor** (a small, reproducible classifier — the safety guarantee) and an **agent advisory pass** (this skill — may only *escalate* above the floor, never lower it). With no floor tool wired up, the skill runs advisory-only and fails closed.

## When to use

- Deciding how much review a PR needs before requesting reviewers or merging.
- Inside a driver/automation loop that wants to auto-clear safe PRs and escalate risky ones.
- `/pr-risk <owner/repo#num>` or `/pr-risk` (current branch vs its base).

Not for *reviewing* the PR — this only routes; it sits upstream of the actual review.

## Steps

### 1. Get the diff
- PR: `gh pr diff <num> -R <owner/repo>`
- Local branch: `git diff <base>...HEAD`

### 2. Deterministic floor — run the classifier, do NOT eyeball it
If you have a floor classifier (a tool that reads a diff on stdin and prints a tier + the signals it fired), run it — it's reproducible, so it's the authoritative baseline. Point `FLOOR_BIN` at it:
```
gh pr diff <num> -R <owner/repo> | "$FLOOR_BIN" -v
```
It prints `floor=Tx` and the fired signals (path / content / dependency / control-plane / policy / size). This floor is authoritative — you may raise it, never lower it. With no floor tool, start from T2 (fail-closed) and let the advisory pass set the tier.

### 3. Agent advisory pass (escalate-only)
Read the diff against your risk rubric. Propose an escalation **only** for the semantic residual a pattern-matcher can't express — the known triggers:
- a logic change widening a trust boundary with no telltale path (sandbox-disable, CI checking out untrusted PR-head, a loosened permission);
- a default whose production impact needs understanding, not pattern-matching;
- a refactor that relocates policy / invariant / state-machine-bearing code (mechanical-looking ≠ low-risk when the code owns invariants).

If nothing warrants it, escalation = none. **Never lower the floor.** When you escalate a *new* pattern, note it — recurring ones should graduate into a deterministic signal in the floor classifier, which is where trust belongs.

### 4. Reconcile + route
`final = max(floor, escalation)`. Route by tier:
- **T0** → auto-merge eligible, but only the narrow safe slice (tests-only / generated / non-policy docs, control-plane excluded). Default to recommend-only — don't auto-merge unless you've explicitly enabled it.
- **T1** → one peer review
- **T2** → owner (CODEOWNERS) review required
- **T3** → owner + adversarial skeptic pass + author "why this is safe" defense

### 5. Log (optional)
Append one JSON line to a decisions log so recurring escalations can graduate into the floor:
```json
{"pr":"owner/repo#123","floor":"T2","escalation":"T3","final":"T3","why":"CI checks out PR-head — fork trust boundary","route":"owner+adversarial"}
```

### 6. Print the verdict
One tight block: final tier + route, the fired floor signals, and the escalation (if any) with its reason. No narration.

## Invariants

- The floor is code, not judgment — reproducible across runs. All nondeterminism lives in this advisory pass, which can only escalate.
- Fail-closed: no diff / no rubric → **T2**, never T0.
- Control-plane edits (the rubric / this skill / CODEOWNERS) are **T3** — changing the classifier is the highest-risk class, not the lowest.

## Notes

- Keep new *policy* in your rubric, new *deterministic signals* in the floor classifier, and only genuinely-semantic judgment in this skill. The floor is the safety layer; the agent advisory reclaims the semantic residual and must keep earning its slot.
