# Improve an algorithm with evidence

Use this when correctness, performance or solution quality is the obstacle.
Keep doing the requested work. The comparison below helps choose an approach;
it is not a qualification gate before helping someone.

## Make the uncertainty executable

Write down the input contract and what would count as better. Separate hard
correctness requirements from an objective such as runtime, memory or packing
quality. A faster invalid answer cannot win. Profile before assuming the
algorithm is the bottleneck.

Build the cheapest trustworthy check for the uncertainty: a slow exact oracle
on small inputs, independent implementation, exhaustive enumeration, invariant,
metamorphic relation, or minimized regression. Validate the checker against a
known-good control and deliberate defects. A checker sharing the candidate's
core algorithm can share its mistake. Floating-point checks need explicit
error bounds; passing finite cases is not a general proof.

Before writing another patch, ask what observation would distinguish the
current explanation from an alternative. Run that probe. Concrete failed
inputs and measurements are usually better feedback than another general
request to "think harder."

## Keep useful work while exploring

Preserve the best checked implementation as the incumbent. Try candidate
changes in an isolated copy or branch so a failed experiment cannot erase it.
Compare complete outputs and requirements, not just a summary score. Record
the exact candidate, input set, command and measurement conditions. Recheck a
candidate before replacing the incumbent; measure plausible speed gains more
than once with a comparable runtime environment.

Choose the next intervention from the evidence. Some useful possibilities:

| Observation | Intervention worth trying |
|---|---|
| Examples pass, but the invariant is unclear | Derive it independently; enumerate small cases |
| Repeated patches break different inputs | Shrink a counterexample; reconsider the representation |
| Correct but too slow | Profile; compare a materially different algorithm or data structure |
| Search quality plateaus | Inspect failure families; vary the search policy or decomposition; validate the evaluator (recipe 8) |
| Tests pass but the caller still fails | Add a caller-owned contract check and replay the boundary |
| Long reasoning yields no discriminating test | Ask a fresh investigator for one falsifiable hypothesis |

A helper is optional. Give it the contract, source and raw evidence before
your preferred diagnosis. Ask for a concrete artifact: a derivation,
counterexample, profile interpretation or alternative implementation. Test its
claims. Change or remove the structure when it stops producing progress.

Example helper prompt:

> Here is the goal, current implementation and observed failure. Independently
> identify the most useful uncertainty to resolve. Return an executable probe
> or a precise alternative with its invariant and tradeoff. Do not invent new
> requirements. Separate what you established from what still needs testing.

## Know what improved

For ordinary work, delivering the checked improvement is sufficient. To claim
the assistance itself helped, compare against ordinary effort with the same
model, tools, feedback and comparable total budget. Extra calls alone can help;
include additional ordinary attempts as a control. Count helper, selection,
repair and verification costs, including failed work. A larger model supplying
the solution is escalation, not evidence that the smaller model improved.

Use development cases for feedback. Freeze unfamiliar final cases before
comparing approaches and keep their answers out of candidate selection. Once
a final failure guides repair, it is development evidence; retain that result
and use fresh cases for a later evaluation. Report both the selected final
candidate and the incumbent so a bad last attempt does not erase a useful
earlier result or silently disappear from the record.

Save portable lessons only after testing them: what failed, what observation
changed the approach, and when the fix applies. Source reuse can be more useful
than another paragraph of advice. Revalidate a reused component against the
new task; earlier acceptance does not cover new integration requirements.

## Optional check recorder

Use the existing test or benchmark command directly, or keep a local receipt
with the bundled stdlib helper. Resolve its path relative to this skill:

```sh
python3 <skill-directory>/scripts/check.py \
  --cwd /path/to/repository --file src/solver.py --file tests/test_solver.py \
  -- python3 -m unittest discover -s tests
```

Each invocation creates a new private directory under
`~/.local/state/agent-boost/checks/`. `--directory PATH` changes that parent.
It saves the chosen source bytes and hashes **before** execution, the exact
command, stdout/stderr, wall time, exit status, and whether selected files
changed during the command. It does not interpret benchmark scores or make an
acceptance decision. Only chosen files are snapshotted; this is not a complete
build manifest or a claim that those bytes were the ones the command executed.

**This runs your command on the host**, in the chosen directory with its normal
environment and permissions. It is not a sandbox. The recorder makes no network
calls, but your command may do anything it normally can, including modifying
files or using the network. Use trusted commands and select only files you intend
to retain. Source, paths and logs remain local; nothing is uploaded or published.

There is no default deadline. `--timeout SECONDS` is optional when the task needs
one. A timeout, SIGINT or SIGTERM during command execution triggers cleanup
and records the interruption. On POSIX this terminates the launched process
group; processes that deliberately escape that group are outside this mechanism.
Windows cleanup covers the launched process, not its descendants. Previous
signal handlers are restored after execution. SIGKILL or a host failure cannot
be handled: an unfinished run retains its starting record and logs and is not
a completed check.

This is a portable operating recipe. Its usefulness must be measured on the
task at hand; it does not establish general intelligence amplification.
