# Coordinator-only review rubric

Lock this rubric before dispatch. Do not include it in worker packets. All
behavioral requirements are visible in their FORMAT.md and case REQUEST.md.
Judge substance using the case's actual mathematical domain; do not require the
reference method or a prescribed narrative. Score each dimension separately.
Do not total them into a universal quality score.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Mathematical or empirical validity | Material error or unsupported central conclusion | Correct useful partial result; a gap is explicitly left open | Main conclusion justified within stated scope |
| Status and scope calibration | Finite observations promoted to proof; false claim accepted | Mostly scoped, with a material ambiguity | Proved/refuted/bounded/empirical/unresolved matches actual evidence |
| Independent checking and reproducibility | No usable check, fabricated experiment, or nonreproducible central evidence | Reproducible core computation or check with a stated limitation | Relevant independent check/control and documented reproducible evidence |
| Alternatives and information gained | Renaming or listing approaches without consequences | A substantive alternative evaluated, yielding a useful limitation or result | An alternative changes the argument, search, representation, or cost with evidence |
| Negative evidence and decision use | Failures hidden or conclusions survive a decisive contradiction | Informative failures/limits retained; next step partly clear | Failed directions or counterexamples materially refine the claim or stop wasted effort |

Negative-evidence dimension is **not applicable** if no informative failure occurs
and no known contradiction was ignored. Never require an invented failure to earn
a score. Reproducibility can be exact hand computation for a small witness; code
volume is not rewarded. Do not penalize an alternative valid representation.

Record false-proof acceptance independently as yes/no/unclear for tree-collision
and moment-tail. Read the argument and status together: JSON saying "refuted"
does not excuse prose that accepts the conjecture, and a schema error alone does
not show false-proof acceptance. Require the specific invalid implication in the
supplied argument to be identified, with a valid witness when one is claimed.
Track mathematical errors that cause false conclusions separately from missing
format fields. The automatic declared-acceptance flag is only a review cue.

For known rediscoveries, record finite artifact correctness separately from proof
validity. A recurrence without derivation can be useful partial evidence; many
matching values do not prove it. For lattice-area, assumptions must cover simple
integer polygons and boundary counting; a result extended to holes, self-crossing
polygons, or arbitrary coordinates needs a separate justification.

For explorations, report feasible objective, improvement over baseline, demonstrated
search coverage, and justified bound/gap when available. Quadratic-design's finite
oracle gap is exact; it does not validate a participant's claim about continuous
domains or arbitrary budgets. Grid-packing's grader verifies objective only;
review any claimed optimum independently. The fixed positive packing control has
minimum squared distance 8; this is a witness, not an oracle proof in the grader.

Assess information gained versus cost in a short evidence ledger:

| Claim or decision changed | Evidence/experiment | What uncertainty was removed | Actual cost | Remaining uncertainty |
|---|---|---|---|---|
| Reviewer fills from the submitted work | Artifact/trace reference | Concrete consequence | Calls/time/tokens or unknown | Exact scope |

Do not turn hypotheses listed, confidence, verbosity, question count, skill phrases,
or agreement with an evaluator's favored method into success metrics. Readable
presentation matters only when needed to inspect the evidence. Review an unpolished
correct proof as correct; reject a polished false proof.

Retain a case row for every selected run: opaque review ID, run state, integrity,
artifact result, the five dimension scores (or N/A with reason), false-proof
acceptance, objective/gap where relevant, costs, and reviewer disagreements.
Keep failed and timeout rows visible. After unblinding, show paired changes and
family/stratum breakdowns with no winner claim from the three-case smoke alone.
