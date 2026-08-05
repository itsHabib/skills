# Card format

House style. The organizing principle: **every section is a command or an API call the reader
can re-run.** A number with no command beside it is not evidence.

## Shape

```
<One-paragraph lede: what was validated, across which layers, ending with>
Every section below is a command you can re-run to reproduce the same result.

## <Subject> validation [TRACKER-KEY]

Identity: branch `<branch>` at `<short-sha>`, <where it ran>, <infra: app port,
DB container + port, live upstream / staging endpoint>.

<Verdict paragraph. Top-line pass/fail, then the load-bearing guarantee in one sentence -
the thing that would matter most if it were wrong.>

### Prerequisites

<Commands that make the branch runnable. Repo gotchas belong here, not in a footnote.>

### 1. <cheapest layer>
### 2. <next layer>
### ...
### N. <live layer>

<Then, as applicable:>
### <Bug found by the validation>
### <What this does not change yet>
### <Notes / dependencies for whoever merges>
```

## Rules

**Identity block is mandatory.** Branch, commit SHA, where it ran, what infra. A card without a
SHA cannot be trusted later, because the branch has moved.

**Layer cheapest to most expensive.** Gate, unit, integration, live. The reader stops as soon as
they are convinced; do not make them read the live section to learn the typecheck passed.

**Every claim gets its command.** Fenced block with the command, then the exact expected output
("`Test Files 83 passed`, `Tests 910 passed`"), then what it covers.

**Tables for anything enumerable.** Input shape -> asserted outcome. Case -> environment ->
result. Field -> hydration count. Prose hides gaps; a table with a blank cell shows one.

**Say what did not change.** A check behind an allowlist is logged, not enforced.

**No em dashes.** Use a hyphen with spaces, or restructure.

**Write UTF-8 explicitly.** On Windows, Python's `Path.write_text` defaults to cp1252 and
corrupts non-ASCII.

## Where it goes

- **A comment on the tracking issue.** The card lives here.
- **PR body** links it: `**Full validation card: [KEY comment <id>](<comment anchor URL>)**`,
  then a short bullet summary.
- **Repo root**, untracked, as `<tracker-key-lowercase>-validation-comment.md`. Never committed.

If an earlier card on the issue still covers part of the change, link both and say what each
one covers rather than superseding it silently.

## Adapter: Jira Server / Data Center (WIKI markup)

Authoring stays Markdown for every tracker. This is the one adapter that needs a conversion
pass on the way out, because Jira Server renders WIKI markup and posts Markdown raw.

| Markdown | WIKI |
|---|---|
| `## H` / `### H` | `h2. H` / `h3. H` |
| `**bold**` | `*bold*` |
| `` `code` `` | `{{code}}` |
| ```` ```bash ```` | `{code:bash}` ... `{code}` |
| `[text](url)` | `[text\|url]` |
| `- item` | `* item` |
| table header + `\|---\|` | `\|\|A\|\|B\|\|`, separator row dropped |

Convert outside fenced blocks only - fence contents stay literal. After posting, read the
comment back and count `## ` and `|---|` occurrences; both must be zero.

Jira Cloud accepts the same WIKI markup on `/rest/api/2/issue/<KEY>/comment`, or ADF on
`/rest/api/3`. GitHub Issues and Linear take the Markdown unchanged - no adapter, post as
written. Whichever tracker you use, read the posted comment back and confirm it rendered.
