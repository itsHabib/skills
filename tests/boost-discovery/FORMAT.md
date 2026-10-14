# Common deliverables

For each selected case, leave result.json and report.md in its case directory.
Keep supplied REQUEST.md and input files unchanged. Extra local code and data
are welcome. Do not edit the supplied skill or another case's inputs.

result.json has this shape (replace example values):

```json
{
  "case_id": "case-directory-name",
  "status": "unresolved",
  "claim": "The precise main conclusion and its domain",
  "evidence": {},
  "limitations": ["What remains unchecked or outside the result"],
  "reproduction": ["python3 investigate.py"]
}
```

Use one status: proved (a general argument), refuted (a checked counterexample),
bounded (a stated finite exhaustive result), empirical (nonexhaustive evidence),
or unresolved. For conjecture-assessment cases the status refers to the supplied
conjecture. For other cases it refers to your main stated claim. Status is a
claim to be reviewed, not automatic proof credit. Use an empty limitations list
only if there is no relevant limitation. If no computation was used, reproduction
may instead describe an explicit manual verification. Exact evidence schemas are
in each REQUEST.md. Rational quantities must use integers or fraction strings.
The data parser accepts result.json up to one MiB, with unique object keys and
finite JSON numbers. Numeric and rational tokens may contain at most 64 characters
(including sign and slash). Rational strings use signed integer or a/b syntax
with a positive integer denominator; decimal or exponent strings are not accepted.
There is no separate numerator or denominator magnitude cap.
Other evidence integers must fit the finite task domains. Keep report.md as an
ordinary nonempty file. These format limits bound parsing, not the mathematics.

report.md should contain your argument, evidence needed to check it, what changed
your understanding, a substantive alternative you investigated or evaluated, any
informative failures, exact scope, and actual reproduction commands. Include
search settings and seeds where relevant. Keep useful unfinished work. A status
of unresolved is better than presenting finite observations as a theorem.

Record actual commands, tool calls, elapsed time, and token usage when observable.
Mark unobservable costs unknown. Length, confidence, skill terminology, and a
particular discovery narrative earn no credit. Do not invent experiments or
negative results. Independent review will assess the mathematics and evidence;
finite artifact checks alone do not establish a proof.
