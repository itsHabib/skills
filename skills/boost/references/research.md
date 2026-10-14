# Research mechanisms, not capability promises

These primary sources motivate the optional [discovery workflow](discovery.md).
The adaptations are design hypotheses. None establishes that Boost's wording
improves results at equal total effort. Read papers selectively when their
mechanism bears on the current uncertainty; a literature survey is not required
before an ordinary task. Dates below identify the consulted versions.

## Executable search and representation

[FunSearch (Nature, online December 2023)](https://www.nature.com/articles/s41586-023-06924-6)
evolves programs inside a constructive skeleton and preserves diversity.
[AlphaEvolve (June 2025, §§2–3)](https://arxiv.org/html/2506.13131v1)
can evolve a construction, constructor or bounded improver, with staged evaluation.
[Its mathematical study (December 2025 revision)](https://arxiv.org/html/2511.02864v3)
also studies generalization from examples to constructions and proofs.
**Adaptation:** choose the object of search; keep a small behaviorally distinct
frontier, a classical baseline and an independently checked finalist.

[PatternBoost (November 2024, §2.1)](https://arxiv.org/html/2411.00566v1)
combines learned proposals with local improvement, sometimes using a justified
partial-progress objective. [AlphaDev (June 2023)](https://www.nature.com/articles/s41586-023-06004-9)
searches in instruction space. **Adaptation:** change representation or search
signal when it removes a named obstacle; preserve the original acceptance rule.
These trained systems and their compute are not recreated by a prompt.

## Proof, conjecture and geometric state

[AlphaGeometry2 (December 2025 revision, §§5–7)](https://arxiv.org/html/2502.03544v3)
separates deduced facts, conditional deductions and numerical observations;
its search-width and image ablations also show limits. **Adaptation:** preserve
those distinctions and transfer only facts valid in the receiving branch.

[A Minimal Agent (February 2026, §§3–5)](https://arxiv.org/html/2602.24273v1)
studies verifier feedback and compact failure memory. [Learning to Disprove
(March 2026, §6)](https://arxiv.org/html/2603.19514v1) exposes a failure where a
formalizer does not validate the supplied witness. **Adaptation:** retain exact
failed obligations; bind proof/check output to the actual statement and object.
A proved lemma must recombine into the original target. Tactic failure, parsing
success and absence of a retrieved match establish neither truth nor novelty.

## Scientific evidence needs an external observation

[AI co-scientist (Nature, May 2026)](https://doi.org/10.1038/s41586-026-10644-y)
separates generated/ranked hypotheses from scientist-selected experiments.
[LLM-SR (April 2024)](https://arxiv.org/html/2404.18400v1) searches equation
structures and fits parameters. **Adaptation:** compare competing mechanisms,
choose an observation that separates their predictions, and distinguish fit,
simulation, prospective evidence and causal interpretation.

The [2026 AI Scientist account](https://www.nature.com/articles/s41586-026-10265-5)
describes human filtering before workshop submission. The [A-Lab correction
(January 2026)](https://www.nature.com/articles/s41586-025-09992-y)
revises identification results and clarifies the scope of novelty.
**Adaptation:** retain the selection funnel, failed attempts, controls and
measurement limits. Scientific novelty, identification and practical value
require different evidence.

## Negative results change the recipe

[Tao's author report (November 2025)](https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/)
documents verifier exploits, rediscovery and constructions beaten by a random
baseline. [Bijection discovery's negative study (November 2025)](https://arxiv.org/html/2511.20987v1)
shows how high scores can miss an explanatory goal. **Adaptation:** keep strict
terminal checks and inspect whether the result answers the intended question.

[HorizonMath (September 2026 revision, §4.2)](https://arxiv.org/html/2603.15617v2)
distinguishes numerical support for an expression from checking a finite
construction. **Adaptation:** report evidence type and scope separately from a
benchmark pass. Public open-problem benchmarks are not permanently immune to
contamination; recheck current prior art and retain exact evaluator versions.

## What would justify keeping an adaptation?

Compare the current skill and revision on the same models, tools, tasks and total
budgets, including reading, failed proposals, search, review and verification.
Use known rediscoveries, false near-neighbor conjectures and open exploration.
Measure valid results, false acceptance, useful negative evidence and cost;
never reward confidence, verbosity or novelty claims alone. Include ordinary
extra attempts and remove one mechanism at a time in later ablations. A short
pilot can reveal defects; it cannot establish general discovery improvement.
