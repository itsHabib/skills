# Patterns worth stealing

Cards are untracked-on-disk by design, so this file cannot ship a library of them. What it
ships instead: the three patterns that made the good ones good, and instructions for building
the index that makes *your* good ones findable.

## The exhaustive-input table

When a change hinges on how it handles an input it does not control - a feature-flag SDK, a
third-party response, a user-supplied field - enumerate every shape that input can take and
give each its own asserted row. A prose claim of "fails open" is unverifiable. A table with
seven rows is not.

| Input shape | Asserted outcome |
|---|---|
| value present, enabled | check enforced |
| value present, disabled | check skipped, logged |
| value absent | fail open, warn |
| malformed value | fail open, warn |
| upstream unreachable | fail open, warn |
| upstream timeout | fail open, warn |
| upstream returns wrong type | fail open, warn |

One row per shape, each backed by a command in the same section. The point is that a blank cell
is visible where a missing sentence is not.

## The counter-check

The single most persuasive paragraph a card can contain. Revert the fix, run the code over the
*real captured artifact*, print the wrong outputs and their count, restore the fix, show the
count is zero.

On the usual clean branch the fix is already **committed**, so `git stash` will not remove it -
stash only saves working-tree and index changes, and on a clean tree it saves nothing at all.
Both runs then exercise the fixed code and the counter-check silently proves nothing, which is
worse than omitting it. Move the *commit*:

```
git rev-parse HEAD                      # remember the exact revision to return to
git checkout --detach HEAD~1            # or the fix commit's parent, if it is not HEAD
<run the real entry point over the captured input>
  -> 8 wrongful FATAL verdicts across 3 real inputs
git checkout <the revision from step 1>
<run again>
  -> 0
```

`git revert --no-commit <fix-sha>` on a scratch branch works equally well when the fix is not
the tip. Either way, print both revisions in the card so the reader can see the two runs were
against different code.

That converts "I fixed a bug" into a measured blast radius. It is also the only way to
substantiate a claim that a new guard catches the bug it was written for: without the revert,
you have shown that the guard is quiet, not that it works.

## State the abstain path explicitly

A check that emits nothing is ambiguous between "evaluated and clean" and "never ran". Whichever
it is, say which, and show the numbers that prove it: how many records carried the trigger
field, how many did not, and why the ones that did not are correct to skip.

Worth writing out even when the answer is boring. A card that reports a live run which fired the
check is right as far as it goes, but a reader still cannot tell whether the *other* checks in
the same suite evaluated at all. The hydration table is what closes that. When in doubt, add it.

## Build your own index

Cards live on the tracker and, in draft form, untracked in the repo root. They are deliberately
**not committed**, so an index is the only durable record of where the good ones are. Without
one, every card is written from scratch, and the house format is much easier to copy than to
describe.

Keep the index outside this skill - it is yours, it names real tickets, and it does not belong
in a shared registry. A single untracked markdown file per repo (or one under your notes) is
enough:

| Ticket | Draft on disk | What makes it worth reading |
|---|---|---|
| KEY-961 | `key961-validation-comment.md` | Gold standard: unit -> integration -> live, plus the exhaustive-input table |
| KEY-971 | `key971-validation-comment.md` | Best counter-check; also states the abstain path |

Add a row whenever you post a card, and note what makes it worth reading rather than what it
covered. Read one or two before writing a new one.

Two entries worth keeping distinct in the index: the shortest useful card (your floor) and the
one that caught a real bug (your target). Also keep any re-card - a second card on the same
ticket after review changes - because re-carding without rewriting the original is its own
skill.
