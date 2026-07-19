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

Before pushing: `scripts/check.sh` must pass AND
`git grep -riE "<employer>|<operator-username>|<private-repo-names>" -- skills`
must return nothing.

Pending: behavioral re-sync of the 2026-07-18 canonical changes (work-driver
--engine session, panel-from-config, model-pool) awaits a scrubbed pass; two
pre-existing files (`tdd`, `work-driver-seed`) also need an identifying-content
cleanup.
