---
name: eng-philo
description: Scaffold (or refresh) a `## Engineering principles` section in a repo's CLAUDE.md — the operator's house style (Dave Cheney lineage, https://dave.cheney.net/practical-go): no `else` / line-of-sight, shallow nesting (≤2 per scope), policy vs mechanism, composition of single-responsibility swappable layers, small sharp APIs, errors-as-values, simplicity over cleverness. Stack-aware: detects Rust / Go / Elixir / Node / Python and tailors the idioms + the lint that ENFORCES each principle. Idempotent re-run between guarded markers, same shape across every repo. Use when onboarding a repo, when the principles evolve, or when a CLAUDE.md is missing the house-style context. Triggers: "add my code style / principles to this repo", "stamp the house style / eng philosophy", "the cheney section", explicit /eng-philo.
argument-hint: "[path/to/CLAUDE.md] — defaults to ./CLAUDE.md at repo root"
user_invocable: true
---

# /eng-philo — stamp the operator's engineering philosophy into a CLAUDE.md

**Portfolio-specific.** This documents how the operator writes code — a fixed,
opinionated set in the **Dave Cheney lineage** ([Practical Go](https://dave.cheney.net/practical-go)):
simplicity, clarity, line-of-sight — plus the architectural principles that sit
above it (policy/mechanism, composition). It stamps that into a target CLAUDE.md
so **every agent run in the repo writes code that way** — the payload that shapes
the actual generated code, not just how anyone talks about it.

Same relationship as `/dev-workbench`: the **skill is the stamper**, the CLAUDE.md
section is the payload. The canonical principles are hardcoded below; edit them
here and re-run everywhere — markers make refreshes idempotent.

## When to use

- "add my code style / principles to this repo"
- "stamp the house style / eng philosophy" / "the cheney section"
- Onboarding a fresh repo whose CLAUDE.md (just `/init`'d) lacks the principles
- The principles evolved — refresh in place across repos
- Any explicit invocation: `/eng-philo`

Don't use for:
- Rewriting the rest of CLAUDE.md (this skill owns only the section between its markers).
- Configuring the lint toolchain itself — this references the enforcing lints; it
  doesn't write `clippy.toml` / `.golangci.yml` (that's the repo's own setup).

## The canonical principles (hardcoded — the house style)

**Dave Cheney lineage** ([Practical Go](https://dave.cheney.net/practical-go)):
simplicity, clarity, line-of-sight. These six are UNIVERSAL; the per-stack block
(next section) translates them into the language's grammar and names the lint
that guards each.

1. **No `else` — line-of-sight.** Handle errors / edge cases with early returns
   and guard clauses; keep the happy path un-indented, flowing down the left
   margin. Reaching for `else` → return early instead.
2. **Shallow nesting — ≤2 levels *per scope*.** A `for` + an `if` is the ceiling
   in one scope. The budget is per-scope, not per-function — a closure / anon fn
   is its own scope, so a `for`+`if` inside a closure is fine. Deeper in one scope
   → extract a function.
3. **Policy vs mechanism.** Separate the decisions (policy: validation, state
   machines, business rules) from the plumbing (mechanism: persistence, transport,
   I/O). Mechanism is dumb and swappable; policy lives in a layer above it. Never
   let policy leak into a mechanism layer.
4. **Composition of single-responsibility layers.** Each layer / package owns ~one
   responsibility; the app is a *composition* of them; any piece is swappable
   without rippling into the others. Dependencies flow one direction.
5. **Small, sharp APIs.** Export the least callers need. Intention-revealing
   names. Accept the narrowest input, return concrete types. Make the zero value
   useful.
6. **Errors are values; simplicity over cleverness.** Handle or propagate errors
   explicitly — never swallow. Readable > clever > short. A little copying beats a
   premature abstraction or dependency.

## Per-stack idioms + enforcement (skill tailors to the detected stack)

Detect the stack from the manifest file at repo root (`Cargo.toml` → Rust,
`go.mod` → Go, `mix.exs` → Elixir, `package.json` → Node/TS, `pyproject.toml` /
`setup.py` → Python). Render ONLY the detected stack's block. Each pairs the
universals with the lint that **enforces** them — opinions become guarantees, not
a doc that rots.

- **Rust:** `?` over nested `match`; early-return guards, no `else` after a
  `return`; newtypes for domain values; minimal surface (lean on `pub(crate)`,
  `unreachable_pub`). *Enforce:* clippy `cognitive_complexity` + `too_many_lines`,
  `clippy.toml` complexity caps, `-D warnings`.
- **Go:** accept interfaces, return structs; small interfaces (1–2 methods);
  errors lowercase + wrapped (`%w`); early-return / line-of-sight. *Enforce:*
  golangci-lint — `gocognit`, `nestif`, `cyclop`, `revive`.
- **Elixir:** `with` for the happy path; pattern-match in function heads, not
  `if`; pipelines; small modules. *Enforce:* Credo — `Refactor.Nesting`,
  `CyclomaticComplexity`, `Refactor.UnlessWithElse`.
- **Node / TS:** early-return; no nested ternaries; no `else` after `return`;
  narrow exported surface. *Enforce:* eslint — `complexity`, `max-depth`,
  `no-else-return`, `sonarjs/cognitive-complexity`.
- **Python:** guard clauses; early return; small public surface (`__all__`); type
  hints. *Enforce:* ruff — `C901`, `PLR0912`, `PLR0915`.

If no manifest is detected, emit the universals only + a one-line note that the
stack wasn't detected.

## Steps

### 1. Locate target + sanity check
Resolve the target (arg or `./CLAUDE.md`). Bail clearly if the file doesn't exist
(suggest `/init`), isn't named `CLAUDE.md`/`AGENTS.md` (ask via `AskUserQuestion`),
or the repo root has no `.git` (ask). Read current content into memory.

### 2. Detect existing section + insert point
Search for `<!-- BEGIN eng-philo -->` / `<!-- END eng-philo -->`.
- **Markers present** → refresh path: replace between them, touch nothing else.
- **A `## Engineering principles` / `## Code style` heading without markers** →
  surface it; offer (a) wrap as-is in markers, (b) replace with a fresh stamp, (c)
  abort. Default (a) — preserve hand-curated content.
- **Neither** → insert after `## Lint discipline` / `## Conventions` if present
  (the principles are the *why*, those sections are the enforcement detail);
  else before `## Architecture`; else end of file (before trailing `## Source` /
  `## How <X> fits`).

### 3. Generate content (stack-aware)
Detect the stack (§ above). Render the six universals verbatim (they're identical
everywhere — that's the point) + the ONE detected stack's idioms+enforcement
block. Match the target CLAUDE.md's voice: terse, lowercase technical errors,
operator-facing, no marketing.

### 4. Assemble between markers
```
<!-- BEGIN eng-philo (managed by /eng-philo — re-run to refresh; hand-edits inside this block will be overwritten) -->
## Engineering principles

How code is written here — Dave Cheney lineage ([Practical Go](https://dave.cheney.net/practical-go)):
simplicity, clarity, line-of-sight. Apply on every change; the lint below catches the slips.

<the six universals>

### <detected stack> idioms + enforcement
<the one stack block>
<!-- END eng-philo -->
```

### 5. Diff + confirm before writing
Show a unified diff. `AskUserQuestion`: **Write** (recommended) / **Edit then write** /
**Abort**. Don't write without confirmation — the diff is the idempotency safety net.

### 6. Report
File path + line range; "6 universals + <stack> idioms/enforcement block"; whether
it was a fresh stamp or an in-place refresh.

## Updating the canonical set
The principles evolve rarely. When they do (operator refines a rule, adds one):
edit the canonical list HERE, then re-run on every CLAUDE.md with the markers.
This skill is the single source of truth — don't hand-curate per-repo fragments.

## Key reminders
- **Keep the skill itself sharp.** Six universals + one stack block. A sprawling
  style bible would betray the minimalism it preaches — resist growth.
- **Opinionated, not generic.** This is the operator's house style, not "configure
  any style guide." The set is fixed.
- **Universals identical everywhere; only the stack block varies.** That's the
  language-agnostic contract — same principles, translated per stack.
- **Pair each principle with its enforcement.** The lint reference is what turns a
  read-once doc into a guarantee. Don't drop it.
- **Idempotent via markers; confirm before write; own only the section.**

## Anti-patterns
- Don't render every stack's block — only the detected one.
- Don't expand into a 40-section style guide. If a principle isn't load-bearing,
  it doesn't earn a line.
- Don't write the lint config files — reference the enforcing lints; the repo owns
  its own toolchain.
- Don't duplicate an existing `## Lint discipline` / `## Conventions` section —
  the principles are the *why* above those; cross-reference, don't restate.

## Outcome
The target CLAUDE.md gains a `## Engineering principles` section between guarded
markers: six universal principles (identical across the portfolio) + the detected
stack's idioms and the lint that enforces them, with [Practical Go](https://dave.cheney.net/practical-go)
linked as the lineage source. Every agent run in the repo now writes code in the
house style by default — and re-running refreshes it in place as the principles sharpen.
