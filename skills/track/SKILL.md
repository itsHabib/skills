---
name: track
description: Give the agent a sense of elapsed time while it waits on something — a heartbeat every N minutes reporting "+10m · 47m total · waiting on X". Use when the user says "track this", "keep time on this", "how long has this been going", "let me know how long we've been waiting", "start a timer on X", or invokes `/track`. Generic and repo-agnostic; anything that waits (a supervisor watching verdicts, a session watching CI, a person watching a long build) can run one. NOT a task scheduler — it reports elapsed time, it does not do work.
argument-hint: "[what you're waiting on] — e.g. 'CI on the release branch'; add --check '<cmd>' to re-run a status command each tick"
user_invocable: true
---

# /track — elapsed-time heartbeat

An agent session has no clock and no gap representation: between two turns, a
3-second reply and a 3-hour silence look identical in context. So it cannot tell
you how long something has taken, and it never notices that a wait has gone on
too long. `/track` fixes exactly that and nothing else.

It is `/loop` plus an anchor. `/loop` already re-invokes a prompt on an interval,
but each tick is amnesiac — it can say "run this again", never "you have been at
this 47 minutes". The anchor file is what makes the cumulative total possible.

## The one-liner it produces

```
⏱ +10m · 47m total · tick 5 · waiting on: review verdicts on the two open PRs
```

**The cumulative total is the payload.** `+10m` is noise; `47m total` is the part
that conveys cost. And the label is not decoration — a bare "10 minutes passed"
gets ignored or, worse, triggers busywork. Elapsed time is only actionable when
it is attached to a pending condition.

## Running one

Two steps. Write the anchor, then start the loop.

```bash
python ~/.claude/skills/track/track.py start --label "review verdicts on the two open PRs"
```

`start` echoes back the exact `/loop` line to run, with the track's name pinned
into it:

```
/loop 10m Run: python ~/.claude/skills/track/track.py tick --name <name>
```

Pass that to the `loop` skill (10m is its default). Under the hood `/loop`
schedules a cron job that fires only while the session is idle — so ticks
arrive between your turns, which is exactly when a heartbeat is worth having.
Two consequences worth knowing: a loop set up this way is **session-only** and
dies with the session, and any recurring job auto-expires after 7 days.

Prefer handing you that line over starting the loop for you. A recurring
wake-up is yours to switch on, and you are the one who will want to switch it
off.

Outside Claude Code there is no `/loop`, so nothing drives the ticks — wire
`tick` to whatever scheduler that environment has (cron, a watch loop), or run
it by hand. The anchor and the totals work the same either way; only the
wake-up is Claude-specific.

`--name` is pinned in that line on purpose. The default name embeds the cwd, so
a tick fired from a different directory would go looking for a track that isn't
there and exit 1. Naming it makes the loop immune to that.

### With a status check

Being woken while still blind is useless, so a tick can re-run a command and
tail its output:

```bash
python ~/.claude/skills/track/track.py start \
  --label "release CI" --check "gh pr checks 123 | tail -5"
```

Keep the check cheap. A tick costs a second or two before the check even runs
(python startup, more on machines with aggressive exec inspection), and a tick
that takes a minute defeats the purpose.

Keep it *small*, too. `--check-lines` (default 8) bounds the output, which caps
a tick at nine lines — enough for a real status board, still short enough to
read as a heartbeat rather than a log. Over a three-hour wait at 10m intervals
that is the difference between a couple of hundred lines of context and a
transcript. What gets bounded is the **tail**, so a check whose summary line
prints first will have that summary cut. Prefer a check that summarizes, and
put the part you actually want to see last.

The check runs under `bash -c`, not the platform shell, so POSIX syntax means
what you expect — `;`, `&&`, pipes, and `~` all work, and a check that runs in
your terminal runs the same way here. This matters most on Windows, where the
platform shell is `cmd.exe`: it silently mangles POSIX syntax rather than
failing, so `a; b` would run as `a` with the rest as literal arguments. It is
`-c` rather than `-lc` on purpose — a login shell sources your profile, which
measured over 10x slower per spawn and defeats a cheap tick. If no bash is
found at all it falls back to the platform shell and says so in the tick
output, because POSIX syntax will misbehave there.

## Verbs

| | |
|---|---|
| `start --label "..."` | anchor a new track; `--check`, `--check-lines` optional |
| `tick` | print the heartbeat, advance the counter, run the check |
| `status` | print totals without advancing |
| `stop` | end it, print the final total |
| `list` | every active track |

`--name` may go on either side of the verb (`tick --name x` and `--name x tick`
both work). State is one small JSON file per track under `~/.claude/track/`.

The default name is `<cwd-basename>-<first 8 of the session id>`, so two
sessions in the same repo get separate tracks. That holds inside Claude Code,
where the session id is both unique and stable across turns — and stability is
what a tick needs, since it runs in a much later turn than the `start`. Run
outside Claude Code there is no session id and the name falls back to the bare
cwd basename, which two concurrent shells in one repo *would* share. Pass
`--name` for those, and for running two tracks side by side in one session.

## When it ends

Stop the track and the `/loop` together once the thing you were waiting on
lands — a heartbeat for a wait that is over is pure noise. They are two
separate things to cancel: `stop` ends the track, and the loop is a cron job
that outlives it, so cancel that too (`CronList` to find the id it was created
with, `CronDelete` to cancel). A tick with no track behind it exits 1 and
prints nothing useful, which is a nuisance every interval until you do.

Report the final total; that number is usually the interesting part, and it is
the only record that the wait happened at all.

## What this is not

- **Not a scheduler.** It reports elapsed time. It does not do the work, chase
  anyone, or take action on a timeout.
- **Not continuous awareness.** The agent only exists during turns; the tick is
  what wakes it. This makes it *aware* of elapsed time, never *punctual*.
- **Not a progress bar.** If you want the state of the work, pass `--check`.
