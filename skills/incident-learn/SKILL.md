---
name: incident-learn
description: Verify recovery from an operational incident, reconstruct an evidence-backed timeline, append a reusable incident record, and turn gaps into owned preventive controls and safer maintenance automation. Use after an outage, degraded service, stale data, failed scheduled task, emergency repair, monitoring alert, near miss, or whenever the user asks to log, review, close, or learn from an incident or wants agents to manage a stack more autonomously.
argument-hint: "[incident, alert, or evidence source]"
user_invocable: true
---

# Incident Learn

Turn an operational event into a durable control. Treat an incident as a state transition backed by receipts, not as a story about what an agent remembers doing.

## Boundaries

- Diagnose with read-only evidence by default.
- Require explicit user approval or an already-valid scoped capability before changing a live environment.
- Use the smallest documented, bounded, and reversible recovery action.
- Never declare recovery from command success alone. Verify the affected runtime invariant independently.
- Separate `impact_status` from `root_cause_status`. Impact may be recovered while prevention remains open.
- Record exact timestamps, identifiers, links, commands, and observed outputs when available. Mark estimates and unknowns; never invent them.
- Exclude secrets, tokens, personal data, and raw sensitive payloads from the record.
- Do not create issues, tasks, schedules, deployments, or other external state unless the user authorized them.

## Workflow

### 1. Establish the incident boundary

Identify:

- the affected project, service, and runtime surface;
- the user-visible or operational invariant that failed;
- the first known bad observation and last known good observation;
- current impact and blast radius;
- authoritative observers such as monitors, scheduler history, logs, metrics, API state, or datastore state.

If the incident is still active, continue diagnosis or recovery within authority. Do not write a recovered retrospective prematurely.

### 2. Reconstruct from receipts

Build the shortest timeline that explains detection, diagnosis, authority, action, and verification. Prefer provider timestamps and immutable identifiers over recollection. Distinguish:

- **Trigger:** the runtime condition that exposed the defect.
- **Failure mechanism:** how the system turned that condition into impact.
- **Root defect:** the missing or broken engineering control.
- **Detection path:** how the system or a person learned about it.

Do not use “human error” or “agent error” as a root cause. Name the system control that failed to prevent, contain, detect, or recover from the event.

### 3. Verify recovery independently

Require both:

1. the recovery action reached a successful terminal state; and
2. an observer outside that action confirms the affected invariant is healthy and current.

Run the narrow runtime check first, then the broader documented confidence check when available. Record residual risk. An alert or incident ticket may remain open after impact recovery; report that as reconciliation lag, not ongoing impact, when live evidence is green.

### 4. Append the incident record

First inspect project instructions and existing incident or postmortem conventions. Use the established location and format when present. Otherwise create `incident-log.md` at the affected project’s root. Use a shared platform log only when the incident belongs to shared infrastructure rather than one project.

Keep the record append-only. Preserve prior entries. Use this shape:

```markdown
## YYYY-MM-DD — concise incident title

- **Impact status:** active | mitigated | recovered | no impact (near miss)
- **Root-cause status:** unknown | understood, fix open | fixed, awaiting verification | fixed and verified
- **Window:** <first known bad> to <verified recovery>
- **Affected surface:** <user-visible or operational behavior>
- **Detection:** <observer and receipt>

### Impact
<What users or systems experienced and what stayed healthy.>

### Timeline
- `<timestamp>` — <evidence-backed event and receipt>

### Cause
- **Trigger:** <runtime condition>
- **Failure mechanism:** <causal chain>
- **Root defect:** <missing or broken control>

### Recovery and verification
<Authorized action, terminal receipt, and independent runtime verification.>

### What worked
- <Control that reduced detection, impact, or recovery time.>

### Gaps and durable actions
- [ ] **<action>** — Owner: <person, agent, team, or unassigned>; Gate: <verification that closes it>; Link: <existing task, or untracked>

### Portable lessons
- <Rule that applies beyond this project and where it should be enforced.>
```

Use prose only where it adds causal information. Do not pad the entry with generic postmortem language. If an active incident already has an entry, append a dated update instead of rewriting its historical evidence.

### 5. Turn lessons into controls

For every gap, name:

- the smallest durable action;
- whose move it is;
- the verification gate that proves it closed;
- the existing issue or task link, or `untracked` if creating one was not authorized.

Prefer enforcement in this order:

1. deterministic check or invariant;
2. independent runtime observer;
3. bounded self-heal with a circuit breaker;
4. user decision gate for ambiguous or high-blast-radius action;
5. prose guidance only when enforcement would not help.

### 6. Design agent-managed maintenance

Describe each recurring maintenance loop as:

`schedule/trigger -> observe -> classify -> authorize -> act -> verify -> record -> escalate`

Every loop needs:

- an explicit service-level objective or runtime invariant;
- an observer independent of the system doing the work;
- a schedule tighter than the allowed detection window;
- an idempotent action with narrow scope and least-privilege identity;
- a bounded retry budget and circuit breaker;
- post-action verification that cannot be satisfied by the action itself;
- an append-only receipt and a clear owner when automation stops.

Allow self-healing only when diagnosis is deterministic, the action is bounded and reversible, blast radius is low, and verification is independent. Require user authority for deployments, schema or data destruction, credential or permission expansion, uncertain diagnosis, repeated recovery failure, or actions outside a pre-authorized catalog.

## Handoff

Report:

1. impact status;
2. root-cause status;
3. incident-record path;
4. the highest-value open prevention action and whose move it is;
5. any alert or ticket state that still needs reconciliation.

Do not say “incident closed” unless the affected runtime invariant is green. Do not say “fixed” without specifying whether that means impact recovered or root defect fixed.
