# shapes reference

The canonical shapes the skill reads and writes. The gold-standard live example is `docs/intern-talks/outline.md` + `interview.md`.

## outline.md header

```
# <Title> - outline

<one-paragraph what this is>

- Adapter: <deck|doc|adr|postmortem|onboarding|gamma>
- Expert: <name>
- Created: <YYYY-MM-DD>
- Status legend: [structure] = shape agreed, [raw] = raw bullets not yet expanded, [interview] = still needs stories.

## <spine / throughline note, if any>

## <Section> [structure]
- <sub-topic> [structure|raw|interview]
  - <notes>

Interview to capture: <the stories/opinions this section needs>
```

## interview.md header

```
# <Title> - interview

<one paragraph: fill answers inline, come back any time>

## How to use this doc
- Answer in your own words under each "Answer:" line. Brain-dump.
- Skip any question that does not spark.
- Check a section off in Progress as you go, so you can stop and resume.
- Add a "> Build note:" line under any answer to flag where it belongs in the artifact.
- When a section has enough captured, say so and it becomes part of the artifact.

## Progress
- [ ] <Section 1>
- [ ] <Section 2>
...
```

## question slot

```
## <Section>

_<promise>_

_Status: not started_

### <sub-topic>

**Q1.** <a deep, story-eliciting question in the second person>

_Answer:_ 


**Q2.** ...

_Answer:_ 
```

## build note (the bridge to synthesis)

A line under an answer that routes it to the artifact:

```
_Answer:_ <the captured story>

> Build note: this is the opener slide for S1; ties to the trust engine.
```

Synthesis reads build notes as placement hints that override defaults.
