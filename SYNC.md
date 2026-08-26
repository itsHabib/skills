# Syncing this repo from the canonical `~/.claude/skills`

This is the **public** MIT subset of the operator's skills. It is NOT a blind
mirror — every sync is a *scrubbed behavioral port*, never a byte-copy.

Public transforms (apply to every synced file):

1. `user_invocable: true` in frontmatter; frontmatter `name` == dir name.
2. No employer names, internal hostnames, or ticket-system URLs.
3. No operator-identifying paths or repo names: `C:\Users\<name>`, `~/pers/`
   roots, private `owner/repo` names → placeholders (`~/projects/`, `my-app`).
4. Private local-binary paths → env vars with a `## Prerequisites` note.
5. Memory-slug citations (`feedback_*`, `reference_*`) stripped from source
   material sections.
6. Reader voice is second-person ("you/your"), not "the operator".
7. Known divergent-by-design skills: `write-pr` (generic Jira config),
   `polish` / `prep-public` / `wip` (audit rules genericized), `work-driver`
   (credential bootstrap genericized).

Before pushing: `scripts/check.sh` must pass. Transforms 2 and 3 are part of
that gate now — `check_scrub` carries the path and identifier patterns, so the
scan is no longer a manual grep you have to remember. `scripts/check-selftest.sh`
is the gate's own guard test; both run in CI.

The manual grep is still worth running for anything the patterns cannot know
about — a new employer, project or repo name:

```
git grep -riE "<employer>|<operator-username>|<private-repo-names>" -- skills
```

When it finds something, add the pattern to `check_scrub` rather than only
fixing the line, or the same class of leak returns on the next sync.

Branch tips count as published. A stale branch pushed here keeps serving
whatever it was carrying even after `main` is clean, so scrub or delete
abandoned branches instead of leaving them parked.

Pending: `work-driver` `--engine session` + panel-from-config were scrubbed and
synced 2026-07-20; the model-pool changes still await a scrubbed pass. `tdd` and
`work-driver-seed` had their **hard** identifying content (username paths, actor
strings) scrubbed 2026-07-20; the softer transforms — memory-slug citations (#5)
and second-person voice (#6) — remain for those two.
