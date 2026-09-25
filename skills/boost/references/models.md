# Models and total effort

Start with the model, tools and budget already approved for the task. Boost
does not require a particular provider, a model change or a higher reasoning
setting. A focused check or a smaller question may be more useful than another
model call.

## Choose help by the missing evidence

| Need | Useful assignment |
|---|---|
| A fresh explanation | Give a helper the contract and raw evidence without the current diagnosis |
| A different formulation | Request one alternative with a runnable candidate and rejection condition |
| A correctness challenge | Ask for a counterexample, independent oracle or invariant check |
| Repetitive mechanical work | Use an existing script or available local tool with checkable output |

A different model family does not guarantee independent errors. Fresh context,
different methods and executable checks matter more than a provider label.
State what evidence a helper saw; do not call its conclusion independent if
it was given the answer it was meant to assess. If helpers are unavailable,
perform the focused check directly and record that limitation.

## Stay within the agreed budget

Do not automatically increase model cost, reasoning effort, helper count or
retry allowance when progress stalls. Narrow the uncertainty, inspect the
failure and use the existing budget first. If additional resources are needed,
describe the specific question and expected evidence; follow the caller's
existing authorization.

Count intake, helpers, tool execution, failed attempts, retries, verification
and consolidation. Report elapsed time separately from total compute effort;
parallel calls reduce elapsed time without making their work free. Record
available token and cost evidence, leaving unavailable values unknown.

To assess whether Boost helped, compare verified outcomes under comparable
total budgets and conditions. A stronger model providing a solution is a model
change; extra attempts are extra effort. Neither alone demonstrates a benefit
from the working method.
