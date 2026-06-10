# Security policy

## Reporting a vulnerability

For security concerns, **don't file a public issue**. Use [GitHub's private vulnerability reporting](https://github.com/itsHabib/skills/security/advisories/new) or email the maintainer privately.

Expect acknowledgment within 7 days. Coordinated disclosure timing depends on severity.

## Supported versions

Only `main` (latest) receives security fixes.

## Scope

This repository is a registry of prompt/markdown skills (`skills/<name>/SKILL.md` with YAML frontmatter). There is no runtime executable surface beyond the dependency-free CI check script (`scripts/check.sh`).

**Security-relevant surfaces:**

- `scripts/check.sh` — runs in CI and locally; reads skill markdown and the README table. A malicious PR could in theory craft inputs that confuse the parser, but the blast radius is limited to failing or passing the check in that environment.

**Out of scope:**

- Claude Code, Cursor, or other assistants that load these skills (report to the respective vendor).
- [skill-sync](https://github.com/itsHabib/skill-sync) and other install/sync tooling (separate repos).
- Third-party MCP servers referenced by individual skills.

## Threat model

These skills are not network-facing. They are markdown instructions loaded by an operator's AI assistant on their own machine. The realistic threats are:

1. **Malicious skill content** causing an assistant to take unintended actions when invoked. Mitigation is review before install and least-privilege tool access in the assistant.
2. **CI script parsing bugs** on crafted frontmatter or README table rows. Mitigation is keeping `scripts/check.sh` small, dependency-free, and covered by the registry checks themselves.

Internet-facing attacks (RCE via external network, supply-chain on the markdown itself) aren't in scope — this repo doesn't bind to ports or download executables at runtime.
