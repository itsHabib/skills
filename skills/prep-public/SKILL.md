---
name: prep-public
description: Pre-launch audit for any project in your portfolio. Detects stack (Rust/Go/Node/TS/Python/Elixir/Ruby), runs the public-readiness checklist (secrets in history, LICENSE, package metadata, README first-impression, .gitignore, personal/employer leaks, tags, CHANGELOG), and materializes findings as dossier tasks under a fresh prep-public-<date> phase ready for /work-driver-prep. Use when you're about to take a project public — link from a tweet or blog post, push to crates.io / npm / pypi / hex.pm, Show HN, "is <project> ready to launch", "prep <project> for public", "what's missing before I tag v0.1.0", or invokes /prep-public.
argument-hint: "<project-slug> [--skip-secret-scan]"
user_invocable: true
---

# /prep-public — pre-launch public-readiness audit

Take any project in your portfolio (typically `~/pers/<project>/`) from "I'm about to announce this" to "I have a punch-list of P0–P3 findings I can fan out via /work-driver". Single-pass audit; materializes findings as dossier tasks under a fresh phase. Distinct from `/polish` (ongoing quality maintenance) — `/prep-public` is a one-shot pre-launch gate; the categories overlap on README but otherwise diverge (secrets-over-history, license alignment, package metadata, no-internal-leaks are public-readiness-specific).

## When to use

User-facing triggers:
- "prep <project> for public" / "is <project> ready to launch" / "Show HN check"
- "what's missing before I tag v0.1.0" / "pre-launch audit" / "tweet-ready check"
- "publish-ready check" / "crates.io / npm / pypi / hex.pm readiness"
- Any explicit invocation: `/prep-public <project-slug>`

Anti-triggers:
- Ongoing quality maintenance → `/polish`
- "Is this PR ready to merge" → `/work-driver`'s review-cycle step
- "What's the state of the project" → `mcp__dossier__project_get`
- One-file rewrite (just the README, just the LICENSE) → edit directly; you don't need a phase + tasks for that

## Arguments

`/prep-public <project-slug> [--skip-secret-scan]`

- **`<project-slug>` (required)** — resolves to `~/pers/<project-slug>/` (or wherever your portfolio root lives). Bail with a clear error if that dir doesn't exist.
- **`--skip-secret-scan` (optional)** — skips Step 3a (gitleaks / trufflehog over full git history). Useful for fast mid-development iteration when you know secrets aren't the gap and the scan adds minutes. Surfaces a "secret scan skipped" line in the summary so it isn't forgotten.

If no project-slug is given, ASK via `AskUserQuestion` which project to audit; populate options from the immediate subdirectories of your portfolio root.

## Steps

### 1. Pre-flight

1. **Resolve path**: `~/pers/<project-slug>/` (adjust to your portfolio root). Bail if missing.
2. **Verify git repo**: `git -C <path> rev-parse --git-dir` succeeds. Bail if not a repo.
3. **Resolve dossier project**:
   - `mcp__dossier__project_list {}` → match `<project-slug>` against each project's `slug` or `name`.
   - Exactly one match → use it.
   - Zero matches → ASK via `AskUserQuestion` whether to create one via `mcp__dossier__project_create { slug: <project-slug>, name: <project-slug> }` or abort.
   - Multiple matches → ASK which.
4. **Cache repo state once**: `git -C <path> ls-files` (universe of tracked files), the README path, the stack manifest paths from Step 2. Re-reading these per check is wasteful and racy.

### 2. Stack detection (FIRST audit step)

Detect by file presence at repo root. First match wins, but if multiple manifests are present (polyglot / monorepo), report ALL and run all matching Step 4 sections.

| Manifest at repo root | Stack |
|---|---|
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `package.json` | Node/TS |
| `pyproject.toml` or `setup.py` | Python |
| `mix.exs` | Elixir |
| `Gemfile` or `*.gemspec` | Ruby |
| None of the above | `unknown` — skip Step 4; still run Step 3 (universal) and Step 5 (soft) |

Print the detected stack(s) in the operator-facing summary (Step 7) so a wrong inference is visible immediately.

### 3. Universal audits (run on every stack)

Each sub-step produces zero or more findings. Each finding becomes one dossier task in Step 6 with a severity prefix in the title (`P0:`, `P1:`, `P2:`, `P3:`). One finding = one task; never bundle distinct gaps.

#### 3a. Secret scan against full git history

**Skip entirely if `--skip-secret-scan` was passed**; print `Secret scan: skipped (--skip-secret-scan)` in the summary.

Try in order:
1. `gitleaks detect --source . --no-banner --log-level error --report-format json --report-path <tmp>/gitleaks-<slug>.json` — recommended default (install: `brew install gitleaks` on macOS, `scoop install gitleaks` on Windows).
2. If gitleaks isn't installed: `trufflehog git file://. --only-verified --no-update --json`.
3. If neither is installed: emit a single **P1 finding** `P1: install gitleaks for pre-launch secret scanning` and **stop the scan**. Do NOT fall through to a homegrown grep — the false-positive rate is worse than no scan and the operator will tune it out.

For each high-confidence hit (gitleaks default rules; trufflehog `--only-verified`):
- **P0 finding** per distinct secret. Title: `P0: secret detected — <rule-id> in <file>:<line>`.
- Body: rule ID, file path, commit SHA where introduced (gitleaks reports both), link to the rule doc. **Never include the secret value in the task body** — work from a redacted reference; the leaked material doesn't need a second copy in dossier.
- Remediation guidance: "rotate first (don't trust history rewrites; old clones still have the secret), then optionally rewrite history via `git filter-repo --invert-paths --path <file>` or BFG. This skill does NOT auto-rotate or auto-rewrite — blast radius (rotated production tokens, force-pushed history) is operator's call."

#### 3b. LICENSE present + matches the manifest declaration

1. `git -C <path> ls-files | rg -i '^license(\.(md|txt))?$'` — case-insensitive, root only.
2. Read the license declaration from the stack manifest:
   - Rust: `Cargo.toml` `[package] license = "..."` or `license-file = "..."`
   - Go: no manifest field; LICENSE file alone is the signal
   - Node/TS: `package.json` `"license": "..."`
   - Python: `pyproject.toml` `[project] license = { ... }` (PEP 621) or `[tool.poetry] license = "..."` (Poetry)
   - Elixir: `mix.exs` `project[:package][:licenses]`
   - Ruby: `<project>.gemspec` `spec.license` / `spec.licenses`

Findings:
- **P1: LICENSE file missing at repo root** — if no license file is tracked.
- **P1: LICENSE declared as `<X>` in `<manifest>` but file is missing** — manifest claims a license; file isn't there.
- **P0: LICENSE file declares `<X>` but `<manifest>` declares `<Y>`** — high-blast misalignment that forks legal exposure; consumers see one source of truth, the legal record shows another.

#### 3c. No personal absolute paths leaked into committed files

Catches any user-home-shape path that shouldn't appear in source meant for public consumption (Windows / macOS / Linux variants):

```
git -C <path> grep -niE 'C:\\\\Users\\\\[A-Za-z][A-Za-z0-9._-]+|/Users/[A-Za-z][A-Za-z0-9._-]+/|/home/[A-Za-z][A-Za-z0-9._-]+/'
```

Filter out hits in (intentional test data / auto-generated content):
- `**/test/**`, `**/tests/**`, `**/fixtures/**`, `**/__fixtures__/**`
- `*.lock`, `*-lock.{json,yaml}`, `package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`, `mix.lock`
- `CHANGELOG.md` historical entries

For each remaining hit:
- **P0 finding** — title: `P0: personal path leaked in <file>:<line>`.
- Body: the file:line, the literal path string, suggested replacement (`~/`, `$HOME/`, `<project-root>`, or a config-loaded value).

#### 3d. No employer / internal-codename references leaking

Personal portfolio repos shouldn't carry day-job names in source, docs, READMEs, or manifest fields. Maintain a short list of strings specific to your situation:

```bash
# Adjust to your case
EMPLOYER_NAMES=("acme" "globex" "your-employer-codename")
for name in "${EMPLOYER_NAMES[@]}"; do
  git -C <path> grep -ni "$name"
done
```

Explicitly EXCLUDED (not findings):
- Author email metadata on commits (work email in `git log` history is not the same as repo content; revising commit history is high-blast and is a separate decision).
- Strings buried in `.git/` blobs — `git ls-files`-based grep already misses these; don't re-scan.

For each remaining hit in source / docs / READMEs / manifest authors field / config files:
- **P0 finding** — title: `P0: employer reference '<name>' leaked in <file>:<line>`.
- Body: file:line, the line content, suggested neutral replacement (project-specific naming or generic placeholder).

#### 3e. `.gitignore` covers env-secret patterns

Required universal entries (present in any line of `.gitignore`):
- `.env`
- `.env.*`
- `*.pem`
- `*.key`
- `credentials*`
- `secrets/`

Plus stack-specific (run only the row matching Step 2's detection):

| Stack | Additional `.gitignore` entries to require |
|---|---|
| Rust | `target/` |
| Go | `vendor/` (only if `go.mod` doesn't intentionally vendor); compiled binary outputs (`<project>`, `*.exe`) |
| Node/TS | `node_modules/`, `dist/`, `.next/`, coverage outputs (`coverage/`) |
| Python | `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/` |
| Elixir | `_build/`, `deps/`, `.elixir_ls/` |
| Ruby | `.bundle/`, `vendor/bundle/` |

Bundle missing entries into ONE task per `.gitignore` (these are correlated — one missing usually means the whole convention was skipped):
- **P2 finding** — title: `P2: .gitignore missing <N> standard entries for <stack>`.
- Body: the missing entries as a copy-pasteable block.

(Exception: if `.gitignore` is missing entirely, that's a **P1** — title: `P1: .gitignore missing`.)

#### 3f. README first-impression checks

Read `README.md` (or `README` / `README.rst` if `.md` is absent). Each gap is its OWN task (these are independent fixes):

| Check | Severity | Title format |
|---|---|---|
| README missing entirely | P0 | `P0: README missing at repo root` |
| First 2 lines don't describe what the project IS | P1 | `P1: README opening doesn't say what <project> is` |
| No install / setup command | P1 | `P1: README missing install/setup command` |
| No working example (runnable code block, CLI invocation, or call sample) | P1 | `P1: README missing working example` |
| No license badge | P3 | `P3: README missing license badge` |
| No CI / build status badge | P3 | `P3: README missing CI badge` |

For "what counts as an install command", adapt per Step 2's stack:
- Rust binaries: `cargo install <crate>`. Rust libs: `cargo add <crate>` snippet or `[dependencies]` block.
- Go: `go install <module>@latest`, `go get`, or `go build ./...` for clone-and-build.
- Node/TS: `npm install <pkg>` / `pnpm add <pkg>` / `yarn add <pkg>`.
- Python: `pip install <pkg>` / `uv add <pkg>` / `poetry add <pkg>`.
- Elixir: hex dep snippet (`{:<pkg>, "~> ..."}` in `mix.exs`) or `mix archive.install`.
- Ruby: `gem install <pkg>` or `bundle add <pkg>`.
- Self-hosted CLIs / MCPs / tools not on a public registry: a clone-and-build snippet counts.

For "what counts as a working example", any code block that an isolated reader could copy-paste and run within 60 seconds of cloning. Don't accept "see the docs" as an example.

#### 3g. CHANGELOG or release notes

`git -C <path> ls-files | rg -i '^changelog(\.md)?$|^CHANGES(\.md)?$'`

If missing: **P2 finding** — title: `P2: no CHANGELOG.md`. Body: recommend keepachangelog.com format before the first tagged release so consumers can diff between versions.

#### 3h. Tagged release exists

`git -C <path> tag --list` → empty?

If no tags: **P1 finding** — title: `P1: no git tags — pre-launch project should anchor at least v0.1.0 (or stack-appropriate first tag)`. A public consumer needs an anchor; "latest commit" is not a version.

### 4. Stack-specific package metadata audits

Run only the section matching Step 2's detected stack. If stack is `unknown`, skip this entire step. If multiple stacks were detected (polyglot), run all matching sections.

#### 4a. Rust (`Cargo.toml`)

Required `[package]` fields for crates.io publishability + discoverability:
- `name`, `version`, `edition` — usually present.
- `description` — short tagline.
- `license` (or `license-file`) — must align with Step 3b.
- `repository` — public git URL.
- `readme = "README.md"` — explicit, not implicit.
- `keywords` (1–5) — crates.io search.
- `categories` (1–5, drawn from crates.io's category slug list) — crates.io browse pages.
- `authors` — must NOT contain an employer email (commit metadata is fine; manifest authors field is in scope for the no-leak rule).

Nice-to-have (not required):
- `documentation` (docs.rs link).
- `homepage`.

Each missing required field → **P2 finding** — title: `P2: Cargo.toml missing <field>`. The exception is `authors` containing employer naming, which is **P0** under Step 3d's rule (don't double-create).

#### 4b. Go (`go.mod`)

Go has minimal manifest metadata; public-readiness lives in module path + godoc:

- **Module path matches public repo URL**: read first line of `go.mod` → `module github.com/<owner>/<name>`. If `<owner>/<name>` doesn't match the public-repo destination you're about to push to (typically `<your-org>/<project>`), this is a **P0 finding** — title: `P0: go.mod module path '<X>' doesn't match expected public URL '<Y>'`. The module path is part of every consumer's import URL; getting it wrong breaks downstream.
- **Godoc on exported symbols**: `git -C <path> grep -nE '^(func|type|var|const) [A-Z]'` → for each hit, the immediately preceding line should be a `// <Name> ...` doc comment. Bundle ALL missing comments into ONE task: **P2 finding** — title: `P2: <N> exported Go symbols missing godoc comments`, body lists the file:line set. (Per-symbol tasks would explode and aren't usefully parallelizable.)
- **Package-level doc comment**: each public package should have a `// Package <name> ...` comment in `doc.go` or at the top of the primary file. Missing → **P2 finding** per package — title: `P2: package <pkg> missing package-level doc comment`.

#### 4c. Node/TS (`package.json`)

Required for npm publish and any public consumer:
- `name`, `version`, `description`, `license`, `author`, `repository.url`, `homepage`.
- `keywords` — npmjs.com search.
- `main` or `exports` — entry points.
- For libraries: `types` (or `exports["."].types`) so TS consumers get typings.
- `files` allowlist — what gets packed into the npm tarball. Default packs everything in cwd minus `.npmignore`; explicit `files` prevents shipping `.env` / `tests/` / scratch files inadvertently.
- `engines.node` — declared Node version range.

Each missing required field → **P2 finding** — title: `P2: package.json missing <field>`. Exception: `repository.url` wrong / pointing at a private fork is **P0** (consumers' install instructions go to the wrong place) — title: `P0: package.json repository.url points to <wrong>, expected <right>`.

Also:
- **Dependency hygiene**: anything imported by `src/**` must be in `dependencies`, not `devDependencies`. Quick check: `git -C <path> grep -h "^import" src/ | rg "from ['\"]([^./]" | sort -u` → cross-check against `dependencies` in `package.json`. Misplaced runtime deps break consumer installs silently. **P1 finding** if any are misplaced — title: `P1: package.json has runtime imports in devDependencies (<list>)`.

#### 4d. Python (`pyproject.toml`)

PEP 621 `[project]` table required for PyPI:
- `name`, `version` (or dynamically derived from VCS / `__version__`), `description`, `requires-python`.
- `license = { text = "..." }` or `license = { file = "LICENSE" }` — align with Step 3b.
- `authors` (list of `{ name, email }` tables).
- `urls.Homepage`, `urls.Repository`.
- `keywords`, `classifiers` (PyPI classifier list — `License ::`, `Programming Language ::`, `Topic ::`, etc.).

Each missing → **P2 finding** — title: `P2: pyproject.toml missing project.<field>`.

For Poetry-style repos using `[tool.poetry]` instead of `[project]`, audit the equivalent fields, AND surface a single **P3 finding** recommending migration to PEP 621 — title: `P3: pyproject.toml uses [tool.poetry]; consider migrating to [project] (PEP 621) for first-class packaging`.

#### 4e. Elixir (`mix.exs`)

Required `project/0` return fields + `package` block for hex.pm:
- `:name`, `:version`.
- `:description`.
- `:source_url` — public git URL.
- `:package[:licenses]` — list, aligns with Step 3b.
- `:package[:links]` — at minimum `%{"GitHub" => "<repo-url>"}`.
- `:package[:maintainers]`.

Nice-to-have:
- `:docs` (main, extras).
- `:homepage_url`.

Each missing required field → **P2 finding** — title: `P2: mix.exs missing <field>`.

#### 4f. Ruby (`<project>.gemspec`)

Required for rubygems.org publish:
- `spec.name`, `spec.version`, `spec.summary`, `spec.description`.
- `spec.license` or `spec.licenses` — align with Step 3b.
- `spec.authors`, `spec.email`.
- `spec.homepage`, `spec.metadata['source_code_uri']`.
- `spec.required_ruby_version`.

Each missing → **P2 finding** — title: `P2: <project>.gemspec missing spec.<field>`.

### 5. Soft / nice-to-have audits (P3)

Each is at most one P3 task; skip silently if the project doesn't have a `.github/` dir (private mirror case — these only apply once the public repo is the canonical one):

- `CONTRIBUTING.md` — guidance for external PRs.
- `CODE_OF_CONDUCT.md` — sets expectations.
- `SECURITY.md` — vuln-reporting address.
- `.github/ISSUE_TEMPLATE/` + `.github/PULL_REQUEST_TEMPLATE.md`.
- Coverage / build badge in README (sourced from CI artifacts or shields.io).
- `docs/` index page that links the main docs (README → vision → PROTOCOL → CHANGELOG).

### 6. Materialize findings as dossier tasks

1. **Create phase**: `mcp__dossier__phase_add { project: <slug>, slug: "<project>-prep-public-<YYYY-MM-DD>", title: "<Project> public-launch prep (<YYYY-MM-DD>)" }`. Today's date as `YYYY-MM-DD`. If a phase with this slug already exists (re-running on the same day), append `-2`, `-3`, ... suffix.
2. **One task per finding** via `mcp__dossier__task_create { project, phase, slug, title, body }`:
   - `title`: `P<N>: <one-line finding>` exactly as drafted in Steps 3–5.
   - `slug`: short kebab-case derived from the finding (e.g. `license-missing`, `cargo-toml-missing-description`, `readme-no-install-cmd`, `gitignore-missing-stack-entries`).
   - `body`:
     ```
     **Severity**: P<N>
     **Stack**: <detected-stack>
     **Source check**: <Step ID, e.g. 3b, 4a>

     ## What
     <specific evidence: file:line, missing manifest field, scan rule ID, exact diff>

     ## Why it blocks launch
     <one paragraph: why a public consumer would notice, be misled, or break>

     ## Suggested fix
     <concrete, stack-appropriate action. NO auto-application — operator decides.>

     ## Out of scope
     <related-but-separate concerns that should NOT be bundled here>
     ```
3. **Create tasks in severity order** (P0s first, then P1, P2, P3) so `mcp__dossier__task_list` reads top-down by priority.
4. **Do NOT auto-claim, auto-start, or auto-link artifacts.** Operator triages; the next step in the chain is `/work-driver-prep`, not direct execution.

### 7. Print operator-facing summary + hand-off

After tasks are created:

```
## /prep-public <project-slug> — <YYYY-MM-DD>

Stack: <detected> (manifest: <path>)
Dossier project: <project-slug>
Phase: <project>-prep-public-<YYYY-MM-DD> (id: <phase-id>)

Findings by severity:
  P0: <count>
    - <slug> — <one-line title>
    - ...
  P1: <count>
    - ...
  P2: <count>
    - ...
  P3: <count>
    - ...

Scan notes:
  Secret scan: <ran with gitleaks | ran with trufflehog | skipped (--skip-secret-scan) | not installed — P1 emitted>
  Stack-specific section: <stack> (Step 4<x>)
  Soft checks: <N> findings

Next:
  /work-driver-prep project:<project-slug>:phase:<project>-prep-public-<YYYY-MM-DD>
```

Always print the exact ready-to-paste `/work-driver-prep` invocation — the operator should be able to copy without editing.

If zero findings: print the summary with all-zero counts and recommend `git tag v0.1.0 && gh release create v0.1.0` as the next move instead of the work-driver invocation. (Empty audits should be celebrated, not padded.)

## Severity tiers

| Tier | Meaning | Examples |
|---|---|---|
| **P0** | Hard blocker — public consumers see broken / misleading / leaked content | Secrets in git history; LICENSE-vs-manifest mismatch; personal path leaked into source/docs; employer reference in personal-portfolio source; README missing; Go module path wrong; npm `repository.url` pointing elsewhere |
| **P1** | Strong blocker — anyone trying to use it hits a wall fast | LICENSE file missing; no install/setup command in README; no working example; no first tag (v0.1.0); `.gitignore` missing entirely; runtime imports in `devDependencies`; gitleaks not installed (can't verify) |
| **P2** | Should-fix before launch — visible polish gap, not a wall | Missing CHANGELOG; missing package metadata fields; `.gitignore` standard entries; thin godoc / docstrings on exported symbols; no package-level doc comments |
| **P3** | Nice-to-have — community-onramp hygiene | CONTRIBUTING / CODE_OF_CONDUCT / SECURITY templates; issue/PR templates; README badges (license, CI); `docs/` index; Poetry → PEP 621 migration |

Task titles MUST carry the severity prefix (`P0: ...`). Phase-level `task_list` becomes the severity-sorted punch-list.

## What it produces

- One dossier phase: `<project>-prep-public-<YYYY-MM-DD>`.
- N tasks under the phase, one per finding, severity-prefixed in title.
- One operator-facing summary printed in chat, ending with the ready-to-paste `/work-driver-prep` invocation (or the `git tag` suggestion when zero findings).
- **Zero file edits in the audited repo.** The skill never modifies the project being audited — every fix is operator-driven follow-on.

## Anti-patterns

- **No new MCP verbs.** Compose `dossier`, `gh`, file reads, and shell — don't propose a `prep.audit` MCP tool. Cross-cutting joins like this one belong in skills.
- **Don't auto-rotate, auto-delete, or auto-rewrite history on secret hits.** Blast radius (rotated production tokens, force-pushed history that leaves old clones with the secret) is the operator's call. Surface the finding and stop.
- **Don't bundle multiple distinct gaps into one task.** A bundled task can't fan out into a parallel `/work-driver` batch. One finding = one task = one PR. (The two narrow exceptions: 3e bundles missing `.gitignore` entries since they're correlated, and 4b bundles missing godoc comments since per-symbol tasks would explode — both are documented in their steps.)
- **Don't audit stack-specific categories for stacks they don't apply to.** No npm checks on a Rust crate; no `Cargo.toml` checks on a Go module. Step 2 detection is the gate.
- **Don't hardcode Rust idioms anywhere.** Every "check the manifest" / "what's the install command" / "where do doc comments live" step is stack-branched. When adding a new universal check later, add per-stack adapters at the same time — don't ship a Rust-only branch and TODO the rest.
- **Don't generalize away your own bar.** When forking this skill for your portfolio, hardcode the specific employer/internal strings you care about in Step 3d's `EMPLOYER_NAMES` list. Don't replace it with `--internal-strings <list>` for hypothetical other shops. Bake in the opinion.
- **Don't pad empty severity tiers in the summary.** If P0 has zero findings, the summary line is `P0: 0` and that's it — no "P0: 0 (great!)" cheerleading. Operator reads the count and moves on.
- **Don't run `/prep-public` in a loop on every project.** It's one-shot per project per launch. Polish work between launches lives in `/polish` or chips. The previous layer has to be solid before adding the next; don't grow this skill into a recurring audit runner.

## Source material

Adjacent skills:
- `work-driver-prep` — direct consumer of this skill's phase output (`project:<slug>:phase:<slug>` form).
- `work-driver` — final consumer of the spec docs that `/work-driver-prep` emits.
- `shipped` — natural follow-up after the launch PRs merge; recaps what shipped + suggests `git tag` if it sees a project hit zero open public-readiness tasks.

Design rules baked into the audit:
- **Stack detection first** — every check adapts to the manifest-detected stack; never hardcode Rust/Go/Node idioms.
- **Compose existing MCPs** — no new MCP verbs; skills compose shell + dossier.
- **Opinionated, not generic** — encode your own launch bar; don't add `--strictness` knobs.
- **Single-pass audit** — no options menu, no per-category opt-out flags.

## Outcome

After this skill runs, the operator has:
- A severity-sorted dossier punch-list of every public-readiness gap.
- A printed `/work-driver-prep` invocation that turns those tasks into spec docs and parallel-safe batches.
- Zero changes to the audited project itself.

Hand-off chain: `/prep-public <project>` → operator triages tasks → `/work-driver-prep project:<slug>:phase:<phase-slug>` → `/work-driver <driver.md>` → launch-ready PRs ship → operator tags v0.1.0 + creates GH release + announces.
