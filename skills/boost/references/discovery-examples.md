# Small discovery workflows

These are teaching examples and known elementary mathematics, not new discoveries
or evidence that Boost improves performance. They illustrate the
[discovery path](discovery.md) at a scale that needs no special runtime. The
proofs below are mathematical arguments; the Python checks only check their
concrete examples. Do not supply these examples as hidden benchmark answers.

## Pattern → representation → proof

**Request:** Investigate the sum of the first n odd positive integers, including
whether a pattern seen in small cases holds for every nonnegative integer n.

Use a short exploratory budget: enumerate small n, try a recurrence or geometric
interpretation, then reserve time for a proof and boundary check. A table of
1, 4, 9, 16 suggests n². Another curve can fit finitely many samples, so fitting
does not settle the conjecture. Changing representation to square increments
exposes the identity `2k−1 = k²−(k−1)²`.

**Proof:** For integer n ≥ 1, summing that identity for k=1,…,n cancels all
intermediate squares and leaves n². At n=0 the empty sum and n² both equal 0.
This establishes the exact claim for every nonnegative integer, independently
of how many examples were enumerated. Negative or nonintegral n are outside
the statement, not silent exceptions. A geometric gnomon picture explains the
representation but is not needed for the argument.

**Handback:** known identity/rediscovery; proved by telescoping; finite enumeration
served discovery and caught indexing errors. Stop here unless a broader question
was requested. No helper or higher model is needed for a settled claim.

## Geometry → falsification → a repaired statement

**Request:** Assess whether every convex quadrilateral with equal-length
diagonals is a rectangle.

Do not search for a proof first and treat failure as a reason for more attempts.
Try a coordinate construction outside the parallelogram family. In cyclic order,
take A=(0,0), B=(3,0), C=(2,1), D=(1,1). Each successive cross product is
positive (3,1,1,3), so this is a strictly convex quadrilateral. Both diagonals
have squared length 5. At B, BA·BC=3, so the angle is not right. This is an
exact counterexample to the original statement, not a numerical near miss.

**Restricted claim:** A nondegenerate parallelogram has equal diagonals if and
only if it is a rectangle. With adjacent edge vectors u,v its diagonals are
u+v and u−v, and

`‖u+v‖² − ‖u−v‖² = 4 u·v`.

Equality is equivalent to perpendicular adjacent edges, which is equivalent to
the parallelogram being a rectangle. Conversely perpendicular edges make the
diagonal lengths equal. The added hypothesis changes the claim; retain the
original refutation. Do not call this a proof of the original statement.

An independent helper could search for another exact counterexample without
seeing the favored construction. A certifier could check convexity and the dot
products separately. Both are optional when direct arithmetic settles it.

Replay the finite examples using Python's exact integer arithmetic:

```sh
python3 -B - <<'PY'
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])
def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]
def cross(a, b):
    return a[0]*b[1] - a[1]*b[0]
p = [(0, 0), (3, 0), (2, 1), (1, 1)]
edges = [sub(p[(i+1) % 4], p[i]) for i in range(4)]
turns = [cross(edges[i], edges[(i+1) % 4]) for i in range(4)]
ac, bd = sub(p[2], p[0]), sub(p[3], p[1])
angle = dot(sub(p[0], p[1]), sub(p[2], p[1]))
assert turns == [3, 1, 1, 3]
assert dot(ac, ac) == dot(bd, bd) == 5
assert angle == 3
assert all(sum(2*k-1 for k in range(1, n+1)) == n*n for n in range(101))
print({'turns': turns, 'diagonal_squared': 5, 'nonright_dot': angle,
       'odd_sum_cases': 101})
PY
```

## Scientific question → discriminating experiment → honest boundary

**Request:** Two dimensionless response models, H₁: y=x and H₂: y=x²,
both fit measurements at x=0 and x=1. Choose a useful next measurement in [0,1].

More repetitions at the endpoints cannot separate their exact predictions.
Their gap is `x−x² = 1/4−(x−1/2)²`, so the largest separation in that interval
is 1/4 at x=1/2. This is a proof about these models, not a scientific result
about the underlying system. A different noise model or experimental cost
could change which measurement is most useful.

Suppose independently established absolute measurement error is at most 0.05
and the two models have no additional predictive uncertainty. At x=1/2, their
allowable measured ranges are [0.45,0.55] and [0.20,0.30]. They do not overlap.
If the measurement falls only in one range, it rejects the other model under
these assumptions; outside both rejects both or an error assumption. If those
bounds were 0.15, the ranges would overlap: some outcomes would be inconclusive.
Unknown systematic error cannot be fixed merely by taking more repetitions.

Before collecting new data, record the prediction ranges, calibrated measurement
procedure, controls and what each outcome means. Check actual units, sample
independence and the effects of previous selection. If budget or lab access is
absent, return the design and required measurement. Do not invent an observed
outcome, label a simulation empirical confirmation or exclude a failed run.

**Handback here:** analytically justified experimental design only; no physical
experiment ran. Prior-art status of the real application is unchecked. Escalate
only if a named uncertainty, such as calibration or identifiability, needs
specialist evidence. The appropriate next experiment is already concrete.

## Two candidates → an existing judge → a bounded decision

This is an invented teaching scenario, not a recorded experiment or evidence of
a discovery gain. A previously validated exact batch-count judge is already on
disk. Counts are nonnegative integers, capacity is a positive integer, and a
partial batch counts as one. Its shared development rows are (items, batches) =
(0, 0), (7, 2). Two agents propose constant capacities that fit those rows:
A uses four items per batch, B uses six. Neither may change the judge.

Before consulting the judge's retained 12-item row, record the two-arm prediction:
at 12 items, A predicts three batches and B predicts two. A judge value of three
supports A over B on this case; two supports B; another value challenges both or
the reference contract. Keep this sealed comparison and each labelled variant
beside it. Do not replace a sealed artifact with the variant that later wins.

The retained row is (12, 3), so no new experiment is needed to reject B for
this case. Withdraw B's claim with that row as evidence. This comparison does
not prove capacity four is uniquely correct among all possible models, nor
validate a deployed implementation. A new claim would need its own coverage.

The supplied arithmetic can be checked without a model:

```python
saved_rows = ((0, 0), (7, 2), (12, 3))
def batches(items, capacity):
    return (items + capacity - 1) // capacity

a = tuple(batches(items, 4) for items, _ in saved_rows)
b = tuple(batches(items, 6) for items, _ in saved_rows)
reference = tuple(count for _, count in saved_rows)
assert a == reference == (0, 2, 3)
assert b == (0, 2, 2)
assert a[-1] != b[-1]  # The retained 12-item row distinguishes the candidates.
```

A saved judge is useful only after its identity, quantity, controls and coverage
have been checked. Its age or agreement with one candidate is not validation.
