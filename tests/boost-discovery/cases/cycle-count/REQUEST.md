# Circular configurations

A configuration is a labelled binary string of length n, with positions arranged
in a circle. No two adjacent positions may both be 1, including positions n and
1. Rotations are distinct unless the labelled strings are identical. Assume n >= 3.

Investigate the number C(n) of configurations. Compute C(n) for every n from 3
through 14, develop a useful general description, and establish as much of it as
you can. Explain the scope of any proof or finite evidence. Record a substantive
alternative representation or approach you considered, and what it contributed
or failed to contribute. Include reproducible local code if you compute results.

Follow the common output format. In result.json, evidence is
`{"counts": [{"n": 3, "count": INTEGER}, ...]}`, with one row per required n.
The status refers to your general description; finite agreement alone is not a
proof for all n. Put the description and argument in report.md.
