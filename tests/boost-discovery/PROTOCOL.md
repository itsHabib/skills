# Frozen comparison protocol

## Freeze and separation

1. Freeze task wording, all inputs, artifact schemas, graders, controls, rubric,
   original skill, and revised skill before dispatch. Run the positive and
   deliberately invalid controls. The prepare command preserves exact bytes and
   per-file hashes, commit identity where available, model/effort, selected cases,
   pair ID, retrieval stratum, and common tool/time limits. Retain its printed
   FREEZE.json hash separately from the workspace. Do not edit sources during
   preparation. A directory snapshot records bytes, not an immutable Git history.
2. Give each fresh-context worker only its packet root. Never expose checkers,
   tests, controls, family labels, rubric answers, other-arm outputs, this protocol,
   or historical results. Do not launch workers from the author's conversation.
   The author and any worker who has seen an answer key are ineligible as fresh
   evaluators. These tasks become development cases once their outcomes inform
   a revision. Later confirmation needs new task instances or families.
3. Keep the packet task files and common instructions identical between arms.
   Only the actual Boost snapshot differs. Do not silently patch a packet after
   failure; retain the first run and create a new paired run if a correction is
   warranted. Verify protected-file hashes before review. Freeze and retain any
   runner prompt and environment deviations alongside the manifest.

## Budgets and repeats

Use the same model version, reasoning effort, available context, runner, tool
surface, hardware limits, and instruction priority in both arms. Count skill and
task reads against the same input/token, invocation, and elapsed-time allowance.
Do not grant extra calls to an arm whose skill takes longer to read. Record actual
skill-reading tokens where visible and snapshot byte sizes; equal caps do not
mean equal tokens spent or equal useful compute. Identical reading rules and
charged overhead are part of the end-to-end comparison. A separate equal
post-reading-work-budget sensitivity analysis can diagnose this cost, but must
not replace the main result or silently erase reading cost. Bytes are not tokens.

The live smoke recommendation is 24 total invocations and 600 elapsed seconds
per arm for the three selected cases. Use runner-enforced limits when available.
If the runner exposes only instructed caps or self-reported counts, preserve
that limitation as a protocol deviation; do not claim hard budget enforcement.
Record unavailable token counts as unknown; never infer them from tool calls.
Report time and tool counts alongside quality. Retain any skill instruction
that conflicts with the fixed runner limits and record which instruction won.

Predeclare repeats and order before runs. For a fuller pilot, use at least three
paired fresh runs per family across multiple instances, with arm dispatch order
and case order counterbalanced. This is a practical start, not a power claim.
Treat repeats sharing a case and multi-case worker as correlated. Prefer separate
fresh workers per case in a confirmation study. Analyze paired case-level changes
and display every pair, grouped by family and retrieval stratum. Do not treat
individual artifact assertions as independent samples or choose best runs.
Report ties, failures, missing outputs, and budget overruns in the denominator.
Do not drop a pair because one arm failed; mark infrastructure failure separately
and retain any replacement as an additional, clearly labelled pair.

## Retrieval and contamination

The default stratum is closed: no network and no external retrieval. Optional
`--retrieval-dir PATH` copies an identical frozen local source pack into each
packet and records its bytes. This is a distinct frozen-pack stratum; prepare
the source pack before task execution, with provenance and publication dates.
Never pool these strata without reporting them separately. A future live-retrieval
stratum requires a new protocol with matched sources, access, query budget,
timestamps, and captured responses; this harness makes no network calls.

Known rediscoveries may be recalled from training. Record disclosed recognition
without rewarding or punishing the disclosure itself; evaluate verification and
scope regardless. Closed access does not imply unfamiliarity or eliminate prior
contamination. Prompt variants alone do not establish novelty. Search prior task
exposure in authorized runner records, not unrelated projects or session stores.
The two exploratory cases are finite investigations with exact objectives, not
evidence of ability to solve research problems with unknown answers.

## Review and evidence retention

Run the frozen artifact grader for every selected case, even after timeout or
missing files. Preserve stdout, stderr, exit code, raw outputs, tool transcripts,
model/effort actually used, all failed attempts, and the final run record. Never
substitute a repaired result for the submitted result. Deterministic checks use
exact bounded data only; they never execute or import participant code. A passing
counterexample establishes that witness's validity, not that the worker found it
independently or diagnosed the supplied proof. A passing list of counts is not a
proof. Packing checks feasibility and reported distance, not optimality.

Create blinded review bundles after execution: random opaque labels, case input,
submitted result.json/report.md, generated artifacts, and relevant tool evidence.
Remove arm names, Boost files, paths identifying the arm, and assessor summaries.
Keep a reversible redaction log; do not remove mathematical evidence or polish
writing. Reviewers should not see the other arm until their per-case judgments
are locked. Use two independent reviewers where feasible and adjudicate factual
disagreements with an explicit reason. Full blindness cannot be guaranteed when
outputs quote a recognizable skill; record detected unblinding.

Apply RUBRIC.md before revealing arms. Keep deterministic results, human judgments,
and cost separate. Report evidence-backed information gained per cost, rather than
normalizing prose length or counting hypotheses. A faster correct narrow result
may be useful; an elegant but false proof is a failure. Describe what the actual
evidence supports and what a small correlated trial cannot establish.

## Follow-up ablations

After the frozen two-arm comparison, add ordinary effort with the same task/tools
and all reading charged, using a common prompt that omits only the supplied skill.
Predeclare its different instruction overhead. To test mechanisms, change one
specified component at a time (for example representation search or falsification
guidance) from a frozen skill; retain byte snapshots and repeat on new held-out
cases. Do not infer mechanism causality merely because a worker uses similar
words. Prefer behavioral evidence: a specific model change, invalidated claim,
new independent check, or cheaper discriminating experiment. Do not select the
best ablation after viewing all results and present it as a prespecified test.

## Historical lessons retained

The older boost-behavior bound replay accepted tiny invalid underestimates because
of symmetric floating tolerance; these checks use exact arithmetic. An older
reporting rubric exceeded the worker's visible requirements; every required
artifact field here is stated in FORMAT.md or REQUEST.md. Previous passing checks
also did not establish that the agent ran a check or that Boost caused it; this
protocol requires tool evidence and separates artifact validity from process and
mathematical review. These safeguards do not turn a small trial into a benchmark.
