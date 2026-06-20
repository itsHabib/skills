---
name: polish
description: Audit a project in your portfolio for polish gaps (CI jobs, README, public-surface doc comments, lint strictness, coverage workflow, doc/code drift, etc.) and emit one dossier task per finding under a fresh `<project>-polish-<YYYY-MM-DD>` phase. Stack-aware — detects Rust / Go / Node / Python / Elixir / Ruby by manifest file and adapts every check to the detected stack. Hand-off chain ends at /work-driver. Triggers: "polish <project>", "what should we clean up in <project>", "audit <project>", explicit /polish.
argument-hint: "<project-slug> [--phase-slug <override>]"
user_invocable: true
---

# /polish — portfolio polish audit

Audit one project in your portfolio (e.g. `~/projects/<project>/`) for the kinds of gaps that don't bottleneck shipping but compound if left to drift: missing CI jobs, stale docs, undocumented public surface, weak coverage workflow, missing OS matrix on cross-platform projects, shipped items still listed as open in follow-ups. Emit one dossier task per finding under a fresh phase. **Stack-aware** — detects the project's stack via manifest file and adapts every check.

Pair with `/work-driver-prep` once you've reviewed the generated tasks; they run `/work-driver` to ship the batch in parallel.

## When to use

Triggers:
- "polish <project>" / "polish <any portfolio project>"
- "what should we clean up in <project>" / "audit <project>" / "hygiene pass on <project>"
- "what's the hygiene backlog for <project>"
- Explicit `/polish <project>`

Anti-triggers:
- Active feature work — write the spec + ship the feature; polish comes after the feature lands.
- A single fix you already know about — call `mcp__dossier__task_create` directly; you don't need an audit.
- Multi-repo refactor — this skill audits ONE project. Run it per repo.
- Generic "review my code" — this is not a correctness review; it's a polish/hygiene audit. Use `/code-review` for diff-level correctness.

## Arguments

`/polish <project-slug> [--phase-slug <override>]`

- **`<project-slug>`** (required): directory name under your portfolio root AND the dossier project slug. Examples: `my-cli`, `my-server`, `my-app`. The two must match — if the dir is `my-app` but the dossier project is `app`, that's a setup gap and the skill surfaces it.
- **`--phase-slug <override>`** (optional): override the default phase slug. Default: `<project>-polish-<YYYY-MM-DD>` (today's date, ISO). Use the override for a focused mini-pass (e.g. `--phase-slug ci-only-polish`).

No interactive mode. No options menu. No per-category opt-out. One audit pass, one phase, N tasks.

## Steps

### 1. Pre-flight

Resolve `(project_dir, dossier_project_slug, phase_slug)` or stop with a clear error:

- Verify `~/projects/<project>/` exists (adjust path to your portfolio root). If not → error: `project directory not found at ~/projects/<project>/`.
- Verify the dossier project exists: `mcp__dossier__project_get { slug: "<project>" }`. If not-found → surface: `dossier project '<project>' not found — create it first via mcp__dossier__project_create`. Don't auto-create; that's a separate decision.
- Compute `phase_slug`: `--phase-slug` if provided, else `<project>-polish-<YYYY-MM-DD>`.
- Reject collisions: if `phase_slug` already exists in the project (check `phases[]` in the `project_get` response) → error: `phase '<phase_slug>' already exists; pass --phase-slug to override`.

### 2. Stack detection

Detect by manifest file presence in the project root:

| Manifest file in project root | Stack tag |
|---|---|
| `Cargo.toml` | `rust` |
| `go.mod` | `go` |
| `package.json` | `node` (also flag `is_typescript` if `tsconfig.json` present) |
| `pyproject.toml` or `requirements.txt` | `python` |
| `mix.exs` | `elixir` |
| `Gemfile` | `ruby` |

**Multi-stack** repos: if more than one manifest is present (e.g. `Cargo.toml` + `package.json` for a Rust core with a TS wrapper), record both stacks and run every per-stack section that matches. Tasks are tagged per stack so the operator can drop a stack's findings if they're out of scope for this pass.

**Unknown stack**: if zero recognized manifests in the project root → ASK via `AskUserQuestion` how the project ships (canonical test command, lint command, doc-comment convention). Don't guess. An audit grounded in the wrong stack is noise.

Also record these project-shape flags (drives Step 5):

- `is_cli` — `Makefile`, `package.json:bin`, `src/bin/`, `cmd/`, or `bin/` present.
- `is_server` — quick grep across the source dirs for any of `axum`, `actix`, `gin`, `chi`, `express`, `fastify`, `fastapi`, `flask`, `phoenix`, `rmcp`, `mcp.server`, `mcp-server`. Hit on any → true.
- `is_frontend` — `vite.config.*`, `next.config.*`, `astro.config.*`, `svelte.config.*`, or a `public/index.html` present.
- `has_migrations` — `migrations/`, `db/migrate/`, `prisma/schema.prisma`, `priv/repo/migrations/` present.

### 3. Universal audit checks (every stack)

For each finding, prepare a task draft. **Don't create tasks yet** — create in Step 6 after the full sweep so the printed summary is one block.

**Always cross-check against recent merges before flagging.** Run `git -C <project_dir> log --since=60.days.ago --oneline` once and grep for the relevant keyword before recording any finding. If a fix already shipped, skip silently.

**3a. CI workflows** (`.github/workflows/*.yml` or `.gitlab-ci.yml`):

Enumerate workflow files locally (`<project_dir>/.github/workflows/*.yml`). For each missing-or-weak item below, one task:

- **`test` job** — required everywhere. If absent → task.
- **`lint` / `fmt` job** — stack-specific tool wired strictly (Step 4 per-stack). One task per missing strict-lint piece.
- **Security audit job** — stack-specific tool (Step 4). If absent → task.
- **Dependency-update bot** — `.github/dependabot.yml` OR `renovate.json` OR `.github/renovate.json`. If none → task.
- **OS matrix on `test`** — if the project's `CLAUDE.md` or `README.md` mentions Windows / macOS / cross-platform behavior (grep for `windows`, `macos`, `cross-platform`, `linux/macos/windows`) AND the test job runs on a single OS → task. High signal for any project that has Windows-specific gotchas.
- **Coverage workflow** — stack-specific (Step 4).
- **Mutation workflow** — stack-specific (Step 4); skip silently for stacks without a maintained tool.

**3b. README quality** (`README.md` at project root):

- Has install/quickstart? Grep for `## Install`, `## Quick`, `### Quick`, `cargo install`, `npm install`, `pnpm`, `pip install`, `go install`, `mix deps.get`, `bundle install`.
- Has a usage example showing the public surface (not just the install one-liner)?
- Has CI badge? Grep for `badge.svg` / `actions/workflows/.*badge`.
- Has license badge OR a `LICENSE` file in the project root?
- `wc -l README.md` < 30 → flag as too thin (one task for expansion).
- Mentions the project's actual public verbs/CLI/API? Run a quick consistency check: grep the top-level source dir for exported symbols and confirm at least the top 3-5 appear in README. If not → task "docs: README missing public-surface walkthrough".

**3c. Follow-ups doc** (`docs/follow-ups.md`, `TODO.md`, or `BACKLOG.md` — whichever exists in the project):

- Pull every checkbox / bullet entry.
- For each, `git log --since=60.days.ago --grep="<short keyword from item>" --oneline` → if it hits, flag as likely-shipped.
- Entries citing `PR #N` → `gh pr view N --json state,mergedAt` → if merged, flag as definitely-shipped.
- **One task** to prune the shipped entries (not N tasks for N stale entries — pruning is one PR).

**3d. Doc/code drift**:

Walk top-level docs that exist: `README.md`, `PROTOCOL.md`, `LAYOUT.md`, `docs/vision.md`, `docs/architecture.md`, `SPEC.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`.

- Extract obvious claims: feature lists, "NOT building" lists, verb/command tables.
- Cross-check against recent shipped work (`git log --since=60.days.ago --grep -iE '(add|implement|ship|feat)'`). Features named in the log that don't appear in the docs → task ("docs: <doc-name> drift — <feature> shipped without doc update").
- Reverse direction: doc names a feature that doesn't exist in code → task.
- One task per doc with material drift. Two docs both stale on the same feature can be one task ("docs: reconcile <feature> across <doc-a> and <doc-b>"); separate docs on unrelated features are separate tasks.

**3e. Spec/plan freshness** (`docs/features/*/plan.md` or equivalent):

For each plan with phase checkboxes (`- [ ]` / `- [x]`): unchecked boxes whose keywords appear in recent merge commits → flag. One task per stale plan ("docs: <feature>/plan.md — mark shipped phases").

**3f. Empty or stub test files**:

Glob test files per stack (per-stack patterns in Step 4). Count assertion-shaped lines: `assert`, `expect`, `should(`, `require.`, `assert!`, `assert_eq!`, `t.Errorf`, `t.Fatal`, `it(`, `test(`, `describe(` (with body), `assert.Equal`.

Any test file with < 3 such lines → stub. Group all stubs in the same module into ONE task; don't spam.

### 4. Stack-specific audit checks

Run only the section(s) for the detected stack(s). Each item is a candidate task; flag only when the gap is real (cross-check Step 3's "already shipped?" rule).

#### 4-rust (`Cargo.toml` present)

- **Coverage workflow**: grep `.github/workflows/*.yml` for `llvm-cov` / `tarpaulin`. If absent → task "CI: coverage as workflow_dispatch job using cargo-llvm-cov".
- **Lint strictness**: CI step running `cargo clippy --all-targets --all-features -- -D warnings`? Grep workflows for `-D warnings`. If absent → task "CI: clippy with -D warnings".
- **Doc comments on public surface**: for each `pub fn` / `pub struct` / `pub enum` / `pub trait` in `src/**/*.rs`, count missing preceding `///` lines. If any file has > 200 LOC AND > 20% of its public items lack doc comments → one task per such file (or grouped per module if siblings).
- **Mutation testing**: `.cargo/mutants.toml` present? If yes-but-no-CI → task "CI: mutation testing as workflow_dispatch job using cargo-mutants". If absent and test coverage already strong → consider proposing it (one task), else skip.
- **Property tests**: grep for `proptest` in `tests/`. If absent AND the codebase has parsers / serialization / state machines → task "tests: add proptest coverage for <surface>".
- **Security audit**: `cargo audit` (or `cargo-deny`) in CI? If not → task "CI: cargo-audit on PRs".

#### 4-go (`go.mod` present)

- **Coverage workflow**: grep workflows for `-coverprofile`. If absent → task "CI: coverage as workflow_dispatch job using `go test -coverprofile`".
- **Lint strictness**: `.golangci.yml` present? CI step running `golangci-lint run`? Missing config → task "lint: add .golangci.yml mirroring portfolio strictness". Config-but-no-CI-step → task "CI: add golangci-lint step".
- **Exported-symbol doc comments**: for each exported (capitalized) identifier in `**/*.go` (excluding `*_test.go`), count missing preceding `// <Name> ...` lines. Same 20%/200-LOC threshold. Don't forget `// Package X ...` at package level — that's a frequent miss.
- **Security audit**: `govulncheck` step in CI? If not → task "CI: govulncheck on PRs".
- **Mutation testing**: `go-mutesting` exists but is rarely maintained; only flag if the project already has it configured-but-not-CI'd. Don't propose adding cold.
- **Property tests**: `gopter` or `testing/quick` imports anywhere? Same shape rule — flag only if code shape calls for it AND it's absent.

#### 4-node (`package.json` present)

- **Detect test runner**: read `package.json:devDependencies` for `vitest`, `jest`, `mocha`, `@vitest/coverage-v8`, `node:test`. Use whichever is present in the per-stack commands below.
- **Coverage workflow**: grep workflows for `coverage`. If absent → task "CI: coverage as workflow_dispatch job using <vitest|jest> --coverage".
- **Lint strictness**: `eslint.config.*` / `.eslintrc*` present AND CI step runs it? `tsconfig.json` present AND CI step runs `tsc --noEmit`? One task per missing piece.
- **JSDoc on exported public surface**: count exported functions / classes / types in `src/**/*.{ts,tsx,js,jsx}` missing `/** ... */` immediately above. Same threshold. Skip the audit entirely if the project marks most exports `@internal` (grep `@internal` density > 50%).
- **Security audit**: `npm audit --audit-level=high` / `pnpm audit` step in CI? If not → task.
- **Mutation testing**: `stryker` config (`stryker.conf.*`) present? Flag only if absent AND coverage strong, OR present-but-not-CI'd.

#### 4-python (`pyproject.toml` / `requirements.txt` present)

- **Coverage workflow**: `pytest --cov` step in CI? If not → task.
- **Lint strictness**: `[tool.ruff]` AND `[tool.mypy]` (or `pyright`) in `pyproject.toml` AND CI steps running them? One task per missing piece.
- **Docstrings on public defs**: count public defs (not `_private` / `__dunder__`) without a docstring in `**/*.py`. Same threshold.
- **Security audit**: `pip-audit` or `safety` step in CI? If not → task.
- **Mutation testing**: `mutmut` configured? Same conditional rule.
- **Property tests**: `hypothesis` imports — same shape rule.

#### 4-elixir (`mix.exs` present)

- **Coverage**: `mix coveralls` (or `mix test --cover`) step in CI? If not → task.
- **Lint strictness**: `mix credo --strict` AND `mix dialyzer` steps in CI? One task per missing piece.
- **`@moduledoc` / `@doc` on public surface**: count modules in `lib/**/*.ex` missing `@moduledoc`; count public functions missing `@doc`. Same threshold.
- **Security audit**: `mix audit` (via `:mix_audit` dep) step in CI? If not → task.
- **Property tests**: `stream_data` — same shape rule.

#### 4-ruby (`Gemfile` present)

- **Coverage**: `simplecov` wired AND CI uploads the report? If not → task.
- **Lint strictness**: `.rubocop.yml` present AND `bundle exec rubocop` step in CI? Missing → task per piece.
- **YARD/rdoc on public methods**: count public methods in `lib/**/*.rb` without `@param`/`@return` or rdoc. Same threshold.
- **Security audit**: `bundle audit` step in CI? If not → task.
- **Mutation testing**: `mutant` — same conditional rule.

#### Multi-stack repos

Run every section that matches a present manifest. Group findings into per-stack tasks — separate "CI: coverage workflow" tasks for the Rust side and the TS side if both manifests are present, since they're separate jobs and separate PRs.

### 5. Project-shape audit checks

Fire based on the shape flags from Step 2:

- **`is_cli`**: are there integration tests that subprocess-invoke the binary (not just unit tests of inner functions)? Glob `tests/cli_*.{rs,go,ts,py}`, `tests/integration/`, `e2e/`. If absent → task "tests: add CLI integration tests (subprocess invocations of the actual binary, asserting on exit codes + stdout/stderr)".
- **`is_server`**: are there E2E tests against the actual transport (HTTP / gRPC / MCP stdio)? Look for `tests/e2e_*`, `tests/server_*`, or a harness that boots the real server. If absent → task "tests: add server E2E tests against the real transport".
- **`is_frontend`**: Playwright/Cypress E2E config present? `axe-core` or similar accessibility check wired? Visual regression (Percy / Chromatic / a snapshot harness)? One task per missing layer — these are independent surfaces.
- **`has_migrations`**: roundtrip test that runs migrations against an ephemeral DB and asserts the resulting schema serves the expected queries? If absent → task "tests: migration roundtrip test against ephemeral DB".

### 6. Create the phase + tasks in dossier

Once all findings are collected (Steps 3 + 4 + 5):

1. **Add the phase**:

   ```
   mcp__dossier__phase_add {
     project: "<project>",
     slug: "<phase_slug>",
     title: "Polish — <YYYY-MM-DD> audit",
     body: "<rollup body>",
     actor: "human:operator"
   }
   ```

   `<rollup body>` is a short paragraph: audit date, detected stack(s), findings count, one-line summary per finding. Mirror the voice of existing dossier polish phases in your project.

2. **For each finding**, one `mcp__dossier__task_create`. Task body shape:

   ```markdown
   ## Problem
   
   <2-4 sentences. Concrete. File paths / commands / counts where you have them.>
   
   ## Fix
   
   <Concrete steps: which file(s), which workflow, which tool. Match the strictness level of sibling repos in the portfolio — opinionated, not generic.>
   
   ## Acceptance
   
   <Observable result that proves the gap closed. Specific commands welcome:
   "gh workflow run mutants.yml produces an artifact + summary";
   "grep -c '^pub fn' src/store.rs matches grep -c '///' immediate predecessors".>
   
   ## Test plan
   
   <How to confirm post-merge. Often one command or one file read.>
   
   ## Out of scope
   
   <Related work explicitly punted to keep this task one-PR-shaped. Critical —
   the agent picking up the task uses this to bound the diff.>
   ```

   **One task per shippable unit. Don't bundle.** A 50-line workflow PR is healthier than a "fix CI" mega-task; per-task parallelism is the whole point of the `/work-driver-prep` → `/work-driver` chain.

### 7. Print the operator-facing summary

End with a tight summary:

```
/polish <project> — audit complete

Stack: <rust | go | node | python | elixir | ruby | rust+node | ...>
Phase: <phase_slug>   (project: <project>)
Tasks created: <N>

  1. <task-slug> — <one-line title>
  2. <task-slug> — <one-line title>
  ...

Next:
  /work-driver-prep project:<project>:phase:<phase_slug>
```

No process narration. No "I queried X then Y." The list of created tasks + the next-step command is the whole output.

## What it produces

After this skill runs:
- A new dossier phase under the project (number auto-assigned).
- N dossier tasks under that phase, each one-PR-shaped with `## Problem` / `## Fix` / `## Acceptance` / `## Test plan` / `## Out of scope`.
- A printed summary with the ready-to-paste `/work-driver-prep` invocation.

Hand-off chain: `/polish <project>` → operator skims tasks in dossier → `/work-driver-prep project:<project>:phase:<phase_slug>` → `/work-driver <generated driver.md>` → polish PRs ship.

## Anti-patterns

- **Don't propose new MCP verbs.** This skill composes existing MCPs (dossier) + shell tools (`gh`, `git`, `grep`). If a check seems to need a new MCP verb, you're scoping wrong — re-frame as a shell check or skip the category.
- **Don't bundle findings.** "Fix CI" with three sub-items belongs as three tasks, not one. Per-task parallelism is the value of the work-driver chain.
- **Don't audit categories the stack can't support.** Skip mutation testing for Go silently. Skip JSDoc for Python silently. Skip `@moduledoc` for Rust silently. A finding shows up only when the stack has a maintained tool AND the project lacks it.
- **Don't re-flag already-shipped items.** Step 3's `git log --since=60.days.ago` cross-check is the first defense; apply the same skepticism to every category. If the last merge says "add coverage workflow", don't surface "missing coverage workflow".
- **Don't hardcode Rust idioms.** Stack detection is the FIRST step; every check below it adapts. If you're about to write `cargo` / `clippy` / `///` in a check that should apply to Go or TS, stop and re-route.
- **Don't make it configurable.** No `--strictness=low/med/high`, no per-category opt-out flags. The polish bar is your polish bar; the only knob is `--phase-slug` for renaming.
- **Don't write spec docs in this skill.** Tasks land in dossier with a `## Fix` outline. `/work-driver-prep` turns each task into a spec doc — that's its job. Doing it here bloats the audit and the spec gets re-derived anyway.
- **Don't audit private surfaces.** Doc-comment audits are public-API only. Lint / coverage audits cover all code, but the public-surface doc rule stops at the visibility boundary or the task count explodes for no signal.
- **Don't audit work/employer repos with this skill.** Personal portfolio only. The opinions baked in are this portfolio's opinions; adapt them to yours.

## Source material

- `work-driver-prep` — consumer of this skill's output (resolves the generated phase into spec docs + conflict-aware batches).
- `work-driver` — downstream consumer that drives the batches to merge through the `ship driver` engine.

Design rules baked into the audit:
- **Stack detection first** — every check adapts to the manifest-detected stack; never hardcode Rust/Go/Node idioms.
- **Compose existing MCPs** — no new MCP verbs; skills compose shell + dossier.
- **Opinionated, not generic** — encode your polish bar; resist `--strictness=low/med/high` knobs.
- **One sharp audit pass** — no options menu, no per-category opt-out.
