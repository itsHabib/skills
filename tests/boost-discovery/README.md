# Boost discovery trials

A small local evaluation of mathematical, geometric, and scientific investigation.
The harness prepares packets and checks data artifacts; it never launches a
model, imports participant code, or grades proof prose. Python 3.9+ standard
library only. Keep this directory, its controls, and the coordinator files away
from workers. See [PROTOCOL.md](PROTOCOL.md) and [RUBRIC.md](RUBRIC.md).

| Case | Family | Domain | Exact artifact check |
|---|---|---|---|
| cycle-count | Known rediscovery | Combinatorics | Twelve finite counts; transfer recurrence checked against direct enumeration |
| lattice-area | Known rediscovery | Geometry | Shoelace area, gcd boundary count, independent integer-point winding count |
| tree-collision | False conjecture | Graph theory | Equal degree multisets; distinct tree counts by enumerating edge subsets |
| moment-tail | False conjecture | Probability | Exact probability mass, symmetry, moments and separated tails |
| grid-packing | Exploration | Geometry | Feasibility, actual minimum distance, improvement over supplied baseline |
| quadratic-design | Exploration | Experimental design | Exact determinant and gap to exhaustive finite-domain optimum |

`smoke` selects cycle-count, tree-collision, quadratic-design in that order. These
are bounded tasks, not frontier open problems. A three-case two-arm run tests the
workflow and exposes concrete failures; it does not establish a performance gain.

Run controls before freezing:

```sh
python3 -B -m unittest discover -s tests/boost-discovery -p 'test_*.py' -v
```

Prepare from the repository root after both skill versions and this harness are
final. The original ref defaults to `4b4a3d987ec2a556581ffd55bfd9dfa5c9449838`.
If your clone is shallow, fetch that historical commit before preparing a trial.
Unit tests use the current checkout commit and do not require historical data.
The revised directory is copied byte for byte, excluding Python caches and
`.DS_Store`; it is not replaced with a summary. `--revised-ref COMMIT` is an
alternative to `--revised-dir`. `--cases all` or comma-separated case IDs work too.

Replace `MODEL_ID` and `EFFORT_LEVEL` with values actually exposed by your runner.
Recording a requested value does not configure or verify that routing.

```sh
python3 -B tests/boost-discovery/harness.py prepare \
  --revised-dir skills/boost \
  --out /tmp/boost-discovery-trial \
  --cases smoke --model MODEL_ID --effort EFFORT_LEVEL --pair-id smoke-01 \
  --tool-limit 24 --seconds 600
```

The output contains separate `packets/original/` and `packets/revised/` worker
roots. Give each fresh worker access to exactly its root and the instruction to
follow WORKER.md. The coordinator directory contains a frozen evaluator copy,
FREEZE.json (per-file SHA-256 and byte sizes), and one run-record template per arm.
Keep coordinator inaccessible to workers. Snapshot integrity is checked again at
grading. Existing output directories are refused so prior runs are retained.

After the run, fill the coordinator's `original-run.json` and `revised-run.json`
from actual execution evidence. Use completed, failed, timeout, interrupted, or
not_run; retain missing values as null, and retain the raw transcript separately.
Do not mark a timeout completed because its files happen to pass artifact checks.

Use the frozen grader copy, writing reports outside packets:

```sh
python3 -B /tmp/boost-discovery-trial/coordinator/evaluator/harness.py grade \
  --run /tmp/boost-discovery-trial --arm original \
  > /tmp/boost-discovery-trial/coordinator/original-grade.json
python3 -B /tmp/boost-discovery-trial/coordinator/evaluator/harness.py grade \
  --run /tmp/boost-discovery-trial --arm revised \
  > /tmp/boost-discovery-trial/coordinator/revised-grade.json
```

Exit 0 means all deterministic artifact checks passed and protected inputs match;
1 means at least one failed/missing artifact or integrity mismatch; 2 is an
invocation/infrastructure error. None is a proof-quality judgment. The grader
retains every selected case, reports declared acceptance of the two false
conjectures separately, and does not collapse exploration quality to a pass bit.
Human review must inspect status claims even when the data are correct.

The harness is a coordinator utility, not an isolation sandbox or budget enforcer.
Workers' filesystem access and time/tool caps must be enforced by the runner.
Do not execute participant scripts on the coordinator host; independent replay
belongs in a disposable, equally restricted worker environment.
