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
   (credential bootstrap genericized), `hackathon` (private worked-example and
   sibling-repo references dropped; scaffold root is `~/projects/`),
   `parallel-work` (the Gate-authority paragraph generalized to "whatever the
   repository designates"), `fact-check` (ledger `source:` enum is
   `human`, not `operator`).

Before pushing: `scripts/check.sh` must pass AND
`git grep -riE "<employer>|<operator-username>|<private-repo-names>" -- skills`
must return nothing.

Synced 2026-09-03: `kickoff`, `fact-check`, `hackathon`, `parallel-work`,
`work-contract`. `kickoff` supersedes `brief`, which stays published for now —
retiring it is a separate call.

Pending: `work-driver` `--engine session` + panel-from-config were scrubbed and
synced 2026-07-20; the model-pool changes still await a scrubbed pass. `tdd` and
`work-driver-seed` had their **hard** identifying content (username paths, actor
strings) scrubbed 2026-07-20; the softer transforms — memory-slug citations (#5)
and second-person voice (#6) — remain for those two.
