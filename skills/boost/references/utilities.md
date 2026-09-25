# Optional local utilities

Use the project's existing commands and a short Markdown handback by default.
These standard-library Python 3.9+ helpers are optional. Do not install Python
just to activate Boost or make any of these steps a prerequisite for delivery.
Resolve `<boost>` below to the installed skill folder. On Windows, `python` or
`py -3` may be available instead of `python3`.

## Execution receipts

`scripts/check.py` runs a trusted host command and saves selected source
snapshots, command output, exit status and elapsed time. See the
[check recorder details](algorithm-improvement.md#optional-check-recorder) for
its scope and cleanup limits. Existing test output is often sufficient.

## Feedback notes

If durable feedback would be useful, write a brief JSON note and run:

```sh
python3 <boost>/scripts/record.py --file note.json
```

Example fields:

```json
{"task":"brief non-sensitive description","model":"actual model and effort or unknown","strategy":"specific check or helper","outcome":"unclear","evidence":"observed result or artifact reference","opinion":"what to keep or change","elapsed_seconds":null,"estimated_cost_usd":null}
```

Outcomes are `helped`, `no_change`, `hurt` or `unclear`. Use `helped` only when
you can name the added intervention and its observed benefit. This is feedback,
not causal evidence. Leave unknown time or cost null.

Notes stay under `~/.local/state/agent-boost/uses/`; `--directory PATH` selects
another destination. Exclude secrets and sensitive task material. The note
recorder and reporter do not upload anything.

Read previous notes only when they could inform the current task:

```sh
python3 <boost>/scripts/report.py --brief
python3 <boost>/scripts/report.py --since 7 --output boost-feedback.md
```

Use `--output` for a UTF-8 report on any platform. If a helper is unavailable,
leave the same concise observation in the existing task handoff and continue.
