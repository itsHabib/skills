# Research behind candidate search

These Google DeepMind projects offer concrete mechanisms to study. The
adaptations below are proposals for Boost, not reproductions of those systems
or evidence that this skill improves results. Each project used its own search
setup, evaluators and resources.

## FunSearch: generate programs and evaluate them

**The authors' mechanism:** FunSearch starts from a seed program and a program
evaluator. A language model proposes programs using selected earlier programs
as context. Automated evaluation determines which candidates return to the
program pool, and the search maintains diversity to reduce stagnation.
[Google DeepMind's FunSearch explanation](https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/).

**Proposed adaptation:** isolate a small replaceable function, keep a checked
baseline and evaluate executable alternatives against a caller-owned check.
Retain useful differences between candidates instead of asking for repeated
paraphrases of one approach. Use a fixed budget and separate final evaluation.
An automated score still needs validation against the real contract.

## AlphaEvolve: use evaluation to guide program evolution

**The authors' mechanism:** AlphaEvolve combines language-model proposals,
automated verification and scoring, and a program database whose evolutionary
selection guides later prompts. Its search can change larger programs rather
than being confined to a single function.
[Google DeepMind's AlphaEvolve explanation](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/).

**Proposed adaptation:** keep a small record of candidate source, its evaluation
results and the reason to try its next change. Reject incorrect candidates
before comparing performance. Explore a different formulation when tuning
stalls, and retain the incumbent unless a candidate meets the acceptance rule.
A short assisted coding session does not reproduce the published system.

## AlphaDev: change the search representation

**The authors' mechanism:** AlphaDev uses reinforcement learning to construct
algorithms as assembly instructions. The agent adds instructions in a game
whose rewards account for correctness and latency. This is a trained search
system, not a language-model prompting recipe.
[Google DeepMind's AlphaDev explanation](https://deepmind.google/blog/alphadev-discovers-faster-sorting-algorithms/).

**Proposed adaptation:** when a formulation limits progress, examine whether a
different representation exposes useful choices. For performance work, inspect
the actual bottleneck and generated operations when relevant, then verify
semantics and measure the complete workload. Moving to a lower level adds
verification work and does not by itself establish an improvement.

## What to test in a Boost run

Use [recipe 8](recipes.md#8-candidate-search-and-selection-trust-the-evaluator-first)
to validate the evaluator and bound candidate search. Record baseline and
selected-candidate outcomes on fresh cases, including failures and total
effort. To attribute a gain to the assistance method, compare against ordinary
work with comparable resources. These research results do not establish such
a gain for Boost.
