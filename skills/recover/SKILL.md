---
name: recover
description: Reconstruct and resume what an abrupt crash, reboot, or terminal loss interrupted. Scans recent Claude Code session transcripts, classifies each (task · cwd · last action · done-vs-interrupted), detects dead background jobs and crash-casualty dirty repos, and emits a ranked recovery plan with exact `claude --resume <id>` commands. Read-only — never auto-resumes, restarts, or kills anything. Use when the user says "my computer crashed", "I lost my terminals", "recover my sessions", "what was I running", "reboot ate my work", "reattach my sessions", "how do I get my sessions back", or invokes /recover. Distinct from /wip (live cross-store work board), /continue (deliberate handoff prompt), and /shipped (retrospective on landed work).
argument-hint: "[--all-projects] [--snapshot] [--since <hours>] — e.g. /recover, /recover --all-projects, /recover --snapshot"
user_invocable: true
---

# /recover — reconstruct and resume what a crash interrupted

A crash, reboot, or closed terminal barely destroys anything *durable* in this setup —
transcripts are append-only JSONL on disk, working-tree edits are just files, and cloud
CI/driver runs persist server-side. What's actually lost is **re-orientation**: which
terminal was doing what, which of them finished, and which had a live background job that
died with the process. This skill does that reconstruction — the ten minutes of hand-joining
session transcripts against `git status` and the process table — and hands back a ranked
resume plan with exact commands.

**Read-only.** It observes and advises. It never resumes a session, restarts a job, or kills
a process for you — the resumed session does the restart itself, with full context.

## When to use

Triggers:
- "my computer crashed" · "I lost my terminals" · "the reboot ate my work"
- "recover / reattach my sessions" · "what was I running" · "how do I get my sessions back"
- Start-of-session after an unclean shutdown, or when the terminal count dropped unexpectedly
- Explicit `/recover`

Anti-triggers:
- "what's in flight / queued right now?" (nothing crashed) → `/wip`
- "hand this session off to a fresh one" (deliberate, context still live) → `/continue`
- "what just shipped / merged?" → `/shipped`

## The recovery model — what a crash can and can't take

Lead the output by telling the user, honestly, how much survived. Usually it's "almost
everything."

**Survives a crash** (recover by resuming / re-attaching):
- **Transcripts** — append-only `*.jsonl` under `~/.claude/projects/<launch-dir>/`. Fully
  intact; the only per-session loss is the single tool call that was executing at the instant
  of the crash.
- **Working-tree edits** — a crash *interrupts*; it doesn't `rm`. Uncommitted files are still
  on disk. (The historical "lost work" failure mode was a concurrent `git reset`, not a
  crash — a different problem.)
- **Cloud CI / driver runs** — persist server-side and as GitHub PRs. Re-attach, don't
  restart.

**Dies with the process** (the real recovery work):
- **Local background jobs** — `run_in_background` commands, poll loops, a local model tagger
  (ollama/histminer), a dev server, a test/build run.
- **A driver's in-memory tick loop** — but its DB persists, so it re-attaches by its
  manifest path.
- **Terminal scrollback** — cosmetic; the transcript has the content.

So the recipe is: **resume each transcript · restart only the dead background jobs · re-attach
cloud runs · confirm edits survived.** Restart *only what's confirmed dead* — don't re-run a
job that's already back, and don't sweep working repos.

## Signals & the join

Run these, then merge. Skip a signal that yields nothing.

### 1. Sessions — the scan (mechanism)

```powershell
& "$env:USERPROFILE\.claude\skills\recover\scan-sessions.ps1" -Hours 6
```

Emits one JSON record per recent session: `id`, `project` (the launch-dir bucket),
`lastWrite`, `ageMin`, `task`, `cwd`, `branch`, `lastText`, `lastTool`, `pendingTool`,
`bgJob`, `bgCmd`. Args: `--since N` → `-Hours N`; `--all-projects` scans every bucket (default
already does, but pass `-ProjectDir <bucket>` to pre-narrow to one crash).

Two rows are **not** recovery candidates — drop them:
- **The current session** — the one this skill is running in. Pass its id as `-ExcludeId`, or
  just recognise the `ageMin ≈ 0` row that is obviously "now".
- **Any still-growing transcript** — another terminal you have open *right now*.
  Sample its `lastWrite` twice; if it moved, mark it "live elsewhere" and leave it alone.

The **crash time** is where a *cluster* stops together — several sessions whose `lastWrite`
falls within a few minutes of each other, then a gap. Don't just take the max: anything
written *after* that cluster is a session you already resumed, or a live terminal —
classify those **live elsewhere**, never as casualties. Use the cluster time to separate
crash casualties from ambient state below.

### 2. Background-job liveness — the highest-value check

For any candidate with `bgJob: true`, decide if the job is dead, alive, or finished. Parse
`bgCmd` for its **output artifact** (e.g. `tagged.jsonl`) and the **binary it launched** (e.g.
`histminer.exe`), then:

```powershell
# a) did the launched binary/artifact survive? Match the SESSION's own binary — not generic node/go.
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '<binary-or-script-from-bgCmd>' } |
  Select-Object ProcessId, @{n='Start';e={$_.CreationDate.ToString('HH:mm:ss')}}, CommandLine
# b) is the artifact still growing?
$a = '<artifact path from bgCmd>'
if (Test-Path $a) { $n1=(Get-Content $a -ReadCount 0|Measure-Object -Line).Lines; Start-Sleep 5
  $n2=(Get-Content $a -ReadCount 0|Measure-Object -Line).Lines
  "$a : $n1 -> $n2  [$(if($n2 -gt $n1){'ALIVE'}else{'static'})]" }
```

- **Dead** — no matching process **and** artifact static/incomplete → top-priority action:
  resume the session and tell it "the `<job>` died, re-run it." The transcript holds the exact
  invocation; don't reconstruct it from scratch.
- **Alive** — process present or artifact growing → something already restarted it. Leave it;
  just resume the session to keep watching.
- **Finished** — artifact hit its target → resume and consume the results.

**Two false-positive guards (both have bitten before):**
- **Claude Desktop is not agent work.** `…\WindowsApps\Claude_*\Claude.exe` plus its ~8 child
  `claude` processes are the Electron app relaunching after the reboot — renderers, GPU, MCP
  connectors. Never read them as a running workflow.
- **MCP servers are not your jobs.** `go run ./cmd/huddle`, `tsx …/mcp-server/src/bin.ts`,
  `@playwright/mcp`, other node MCP procs are connectors any Claude session spawns. Match dead
  jobs by the *artifact/binary the session launched*, never by generic `node`/`go` presence.

### 3. Uncommitted work — casualties vs ambient

```powershell
$root = "$env:USERPROFILE\projects"; $crash = Get-Date '<crash time from step 1>'
Get-ChildItem $root -Directory | ForEach-Object { $d=$_.FullName
  if (Test-Path (Join-Path $d '.git')) {
    $n = (git -C $d status --porcelain 2>$null | Measure-Object -Line).Lines
    if ($n -gt 0) { [pscustomobject]@{ Repo=$_.Name; Branch=(git -C $d rev-parse --abbrev-ref HEAD 2>$null);
      Dirty=$n; Touched=$_.LastWriteTime.ToString('MM-dd HH:mm'); Casualty=($_.LastWriteTime -gt $crash.AddMinutes(-30)) } }
  } } | Sort-Object Casualty,Dirty -Descending | Format-Table -AutoSize
```

Only **casualties** (a repo touched within ~30 min of the crash, or a crashed session's own
cwd repo) matter here — and even those are safe on disk. **Ambient dirty** repos (dirty but
last touched days ago) are pre-existing WIP, *not* crash damage: mention them as a one-line
aside, never as something to "recover." Offer to snapshot casualties (a WIP commit or
`git stash`) **only** with `--snapshot`, and only per-repo on confirmation — never a blind
sweep.

### 4. Cloud CI / driver runs — re-attach, don't restart

If a crashed session was driving a cloud CI/driver tool (like `ship`): a cloud run persists
server-side and as GitHub PRs, so its workflow-run list and open PRs show its state — do not
start a second run. If it was a *local* driver run, it typically re-attaches by its manifest
path — resume the session; don't spawn a rival driver.

## Classification — the verdict per session

- **✅ Done** — `lastText` is a wrap/recap (merged / shipped / "all wrapped" / a `## Recap`)
  and not `pendingTool`/`bgJob`. Nothing to recover; list it as done and move on.
- **🔴 Dead background job** — `bgJob: true` and step 2 says dead/incomplete. The lead action.
- **🔴 Interrupted mid-tool** — `pendingTool: true`. The crash hit during a tool call. Resume;
  the model re-issues it. If that tool had side effects (a write/commit/push), flag "verify
  the last `<tool>` landed" before continuing.
- **⏸️ Handoff / paused** — `lastText` is a kickoff or continuation prompt, or a design/prep
  doc was mid-write. Nothing was running; the artifact is on disk. Resume, or point at the file.
- **🟢 Resume (safe)** — a strategy/discussion session that ended on a normal answer, zero side
  effects. Resume to keep the thread; no risk.
- **⏸️ Live elsewhere** — transcript still growing, or written *after* the crash cluster.
  Another terminal, or one already resumed. Don't resume, don't kill.
- **⚪ Trivial / ephemeral** — a one-line ping, a bare `/clear` with no work after, a scratchpad
  shakedown task. Drop silently; don't clutter the plan.

## The resume command — get the directory right

`claude --resume <id>` only finds a session whose **launch directory** matches the current
working directory. The launch dir is the un-escaped bucket name, *not* the session's work cwd —
so a session that was editing a subdirectory still resumes from the projects root if that's
where its terminal was started. The bucket name is the launch path with `:`, `\`, and `.` each
replaced by `-`; to reverse it, take the drive letter, add `:\`, and turn every remaining `-`
into `\` (`C--Users-you-projects` → `C:\Users\you\projects`). Emit each command with the `cd`
baked in:

```powershell
cd "C:\Users\you\projects"; claude --resume <full-session-id>
```

Fallback if an id is fiddly: `cd "<launch-dir>"; claude --resume` (no id) opens the picker.
**Resume, don't restart** — a fresh `claude` loses the background-job command, the plan, the reasoning.

## Output format

Rank 🔴 first. Skip empty sections. Open with the one-line reassurance when it's true.

```markdown
_Almost nothing durable was lost — <n> transcripts intact, edits on disk, <n> cloud run(s) persisting. One job to restart._

## 🔴 Needs action
- **<id8>** · <task> — <verdict: dead tagger, 1/1630 lines · histminer.exe not running>
  → `cd "<launch-dir>"; claude --resume <full-id>`  then tell it: "<what to say>"

## 🟢 Resume (safe — no side effects)
- **<id8>** · <task>  (<cwd>, <branch>) — <where it landed> → `cd "<launch-dir>"; claude --resume <full-id>`

## ✅ Already done — ignore
- **<id8>** · <task> — <outcome, e.g. PR #181 merged>

## ⏸️ Live elsewhere / paused
- **<id8>** · <task> — <another terminal, still writing | kickoff saved to <file>>

## Uncommitted (crash casualties — safe on disk)
- **<repo>** (<branch>): <n> files, touched ~<crash time> — `--snapshot` to WIP-commit
_Ambient dirty (pre-existing, not this crash): <repo> (<n>), <repo> (<n>) — ignore._
```

## Rules

- **Read-only unless `--snapshot`.** Emit a plan; don't resume, restart, or kill. The one
  write action is the opt-in WIP-snapshot of crash casualties, confirmed per repo.
- **Reassure honestly.** Lead with what survived when it's true — but never launder a dead job
  or a half-applied edit into "fine." A pending-tool write is "verify," not "done."
- **Restart only the confirmed-dead.** Don't re-run a job that's already back; don't touch
  working repos for symmetry.
- **Guard the process table.** Claude Desktop and MCP subprocesses are never your
  work. Match jobs by their own artifact/binary.
- **Casualties, not ambient.** Separate crash-time dirt from pre-existing WIP; never dump
  every dirty repo in the tree as "damage."
- **Resume from the launch dir.** Every emitted command carries the correct `cd`.
- **Ids and exact commands are first-class.** No process narration ("I scanned, then…") — show
  the plan.

## Where it sits

The recovery member of the status family — pick by tense and trigger:
- `/wip` — **now, whole portfolio**, nothing crashed (what's open + in-flight).
- `/continue` — **deliberate handoff**, context still live (a paste-ready brief).
- `/recover` (← this) — **after a crash**, reconstruct what was interrupted and how to resume.
- `/shipped` — **just past** (retrospective on what landed).

## Source material

- `scan-sessions.ps1` (this dir) — the extraction mechanism; classification lives here (policy).
- `~/.claude/skills/wip/SKILL.md`, `.../continue/SKILL.md` — the sibling surfaces; keep distinct.
