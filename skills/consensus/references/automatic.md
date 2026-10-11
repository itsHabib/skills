# Automatic Claude/Codex run

One question, independent answers, one proposal, one approval round. Finish with
**agreed**, **disagreed**, or **incomplete**, preserving objections and failures.
Agreement is agreement on the supplied evidence; it does not prove correctness.

## Run

Infer the question from the conversation. Freeze the relevant facts, constraints,
options and source references into one concise text packet. For repository work,
include the inspected revision and relevant code; the models receive the packet
instead of inspecting the repository. Do not fill missing facts with guesses.
The same question and evidence go to every participant.

Use the bundled script through the shell/exec tool. Resolve its path relative to
this skill folder. Save the question in a temporary text file and pass it on stdin
so user prose is never interpolated into shell code:

```sh
python3 <skill-folder>/scripts/consensus.py --context <packet-file> < <question-file>
```

Without additional evidence, omit `--context`. The default participants are
`claude,codex`, using installed CLI defaults and existing subscription logins.
Claude retains its model selection; Codex uses its CLI default with user config
disabled to isolate tools. If a specific model matters, name it explicitly:

```sh
python3 <skill-folder>/scripts/consensus.py --models claude:opus,codex:gpt-6.1-sol < <question-file>
```

`--models` accepts comma-separated `claude[:model]` or `codex[:model]` selections.
Use selections the user requested; otherwise the two defaults suffice. Multiple
Claude models are supported, but same-family judgments are not independent model
families. Other providers use the shared-folder workflow described in
folders.md; do not silently substitute another model in this automatic runner.

The script requires Python 3 and the installed CLIs on macOS/Linux. Calls use
temporary working directories, Claude tools/customizations disabled, and Codex
read-only mode with user config, shell, subagents, plugins, image tools and web
search disabled. Codex may still load skill descriptions. Models are instructed
to use only the supplied evidence. This is local opinion gathering,
not a security boundary against a hostile model or modified CLI.

Independent answers run in parallel, followed by one synthesis by the first
successful participant and parallel approvals of the exact proposal and tradeoffs.
No automatic debate loop or majority override.

Each call has a 180-second deadline (`--timeout <seconds>` to change it). Exit 0
means agreed, 1 disagreed, 2 incomplete or a local error, 130 interrupted. These
are expected workflow outcomes, not reasons to repeat the whole run blindly.

## Recover and report

The printed run path under `~/.consensus/runs/` contains frozen inputs, raw outputs,
errors, per-call results, `result.json` and readable `result.md`. Keep these private
when they contain private source. Completed calls are saved as they finish.

```sh
python3 <skill-folder>/scripts/consensus.py --resume <run-path>
```

Resume retries failed steps and reuses successful steps only when their exact
inputs and invocation match. Newly recovered answers may change synthesis inputs,
requiring a new proposal and votes. A run lock prevents concurrent resumes.

Read `result.md` and inspect errors in the per-call JSON when incomplete. Return
the proposal, who approved or objected, the substantive objection or missing model,
and the saved result link. Never call a partial panel consensus. A user request to
seek opinions authorizes those calls, not implementation, publication or deployment
of the proposal. Resume when useful within the requested scope; stop on provider
auth/capacity failures that need an external change.
