# Questions to unstick an agent

Questions that improve how an agent investigates without supplying the answer.

Choose a question yourself at a meaningful checkpoint. Start from an actual
result, repeated attempt, untested assumption or gap between the evidence and
the required outcome. Prefer the question whose answer could most change the
next action and can be checked with available resources. Adapt it to the
specific evidence; this table supplies examples, not a list to cycle through.

Before choosing one, ask: **Would plausible answers lead to different next
actions?** If not, drop the question and continue the justified work. A check
that confirms the current action can still be valuable.

Costly reversal or a downstream contract makes a fork consequential, but a cheap
discriminating check can also be worth doing. Routine wiring with a settled
contract usually needs implementation and validation, not a research mission.

| When… | Ask… |
|---|---|
| It has several explanations | What’s the smallest experiment that would distinguish them? |
| It’s too confident | What observation would make you abandon this explanation? |
| It keeps gathering context | What do you already know enough to test? |
| It keeps building infrastructure | What result would change your next decision? |
| It’s tweaking without progress | Which assumption have all your attempts shared? |
| It passes the supplied examples | What’s the simplest new case that could break it? |
| It’s solving everything at once | Which uncertainty is blocking the rest? |
| Two approaches disagree | What’s the smallest input where their answers differ? |
| It treats unlike cases alike | Which cases need different decisions but look the same to your approach? What information would distinguish them? |
| A rule uses information from completed examples | Could it still make the decision using only information available at decision time? |
| A number is being used to choose a repair | What does it measure, and does applying the implied change satisfy the whole requirement? |
| A predictor agrees with examples | Where can you check its recommendation against an executed outcome? Which behavior or inputs did it assume? |
| Success is measured only on what it returns | Could it pass by omitting a difficult required case? |
| It disagrees with a reference answer | Which disagreements violate requirements, and which are acceptable alternatives? |
| Two reported improvements seem comparable | Are they solving the same problem on the same inputs under the same conditions? |
| Another component depends on an identifier | What can change without the thing named changing? Does this ID preserve that identity across those changes? |
| A helper reproduces a result differently from the caller | Did both execute the same entry point, effective defaults and input revision? |
| A whole class has the same offset or scale error | Which unit conversion, transform or configuration could cause it, and what observation would distinguish those causes? |
| The results look suspiciously good | Could your evaluator reward the wrong behavior? |
| An aggregate score looks good | Which required cases or serious failures could that summary hide? |
| It’s stuck in one approach | What would a fundamentally different explanation predict? |
| It claims success | What did you demonstrate, and what are you still assuming? |
| It requests more resources | What can you establish with what you already have? |

Use one question at a time. State what observation would change the next
decision, then run the experiment or give a helper a bounded check. Report the
result and what follows; a useful negative result or confirmation can settle
the question. If no discriminating check is available, name the missing evidence
and do the useful work that remains. Do not repeat the same question without
new evidence or a concrete unresolved check. Questions alone are not progress.
