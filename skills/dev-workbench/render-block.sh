#!/usr/bin/env bash
# Render the canonical, harness-neutral dev-workbench managed block.
# Read-only: emits markdown to stdout and never edits a target file.

set -euo pipefail

repo_name=""
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      [ $# -ge 2 ] || { echo "render-block.sh: --repo needs a name" >&2; exit 2; }
      repo_name="$2"
      shift 2
      ;;
    --repo=*) repo_name="${1#*=}"; shift ;;
    *) echo "render-block.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

[ -n "$repo_name" ] || { echo "render-block.sh: --repo is required" >&2; exit 2; }

case "$repo_name" in
  dossier) callout=' **This is dossier - the State plane work-item store - so dossier verbs are most directly relevant here.**' ;;
  ship) callout=' **This is ship - the Execution plane driver - so Ship workflows are most directly relevant here.**' ;;
  channel) callout=' **This is channel - the optional agent message bus itself.**' ;;
  workbench) callout=' **This is workbench - the repository that hosts the Gate, Flare, Console, Escalate, review, and dispatch planes.**' ;;
  skills) callout=' **This is the scrubbed public skills projection, not the private catch-all.**' ;;
  hooks) callout=' **This is hooks - the cross-harness lifecycle bookkeeping layer.**' ;;
  skill-sync) callout=' **This is skill-sync - a catalog projection engine for agent skill homes.**' ;;
  *) callout='' ;;
esac

cat <<EOF
<!-- BEGIN dev-workbench (managed by /dev-workbench skill - re-run to refresh; hand-edits inside this block will be overwritten) -->
## Dev workbench

These MCPs, planes, and skills are available in Claude and Codex sessions on this machine; each harness injects tool signatures, so this is the map of how they compose, not a second verb manual.${callout} When the signal matches, call the verb. Knowledge questions about another portfolio repo go to \`/consult\`; authority questions - direction, spend, credentials, irreversible actions - go to the operator.

**MCPs (in-session):**
- **dossier** - durable project memory: projects -> phases -> tasks -> artifacts.
- **ship** - dispatch an agent and persist dispatch -> poll -> judgment -> land -> record.
- **channel** - optional append-only agent message bus (\`channel.post/read/list\`); off the normal PR path and supersedes huddle.
- **playwright** - browser automation when the task requires a real DOM.

**Planes (workbench CLIs composed through exit codes and JSONL, not MCPs):**
- **gate** - authorization at the exact PR head against an operator-minted grant; findings are not authorization. Exit 0 pass / 1 block / 2 park / 3 refuse / 4 error.
- **flare** - best-effort notification sink over authoritative receipts; never gates.
- **console** - read-only local view of Gate's inbox and grant ledger; explains, never decides.
- **escalate** - agent -> human -> agent resolution channel for a parked Gate run.

**Skills:**
- **/work-driver** + **/work-driver-prep** - drive implementation; prep builds specs and conflict-safe batches.
- **/pr-risk** - decide how much review a change needs; reviewers perform it.
- **/review-coordinator** + **/review-digest** - consolidate reviewer findings; digest is the deterministic pre-pass.
- **/shipped** / **/status** / **/wip** - retrospective / current-session / portfolio-liveness views.
- **/consult** - ask a sibling repo's steward; knowledge to peers, authority to the operator.
- **/worktree-*** - add / list / remove / transfer / locate isolated checkouts.

### The loop

\`\`\`text
dossier task -> /worktree-add -> spec -> ship driver (dispatch -> poll -> judgment -> land -> record)
  -> PR + CI -> /pr-risk -> reviewer panel -> /review-coordinator -> one findings artifact
  -> gate evaluates the exact head -> 0: emitted head-pinned merge command -> merge
  -> authoritative receipts -> dossier close-out -> /worktree-remove
       \\-> 2: park -> console / gate next -> human decision -> escalate -> gate resolve -> gate next
       \\-> attention or terminal receipt -> flare -> Slack (best effort; never gates)
\`\`\`

\`/work-driver\` coordinates dispatch -> poll -> land and runs its own review triage inline. \`/pr-risk\` and \`/review-coordinator\` are explicit steps; the driver does not invoke them automatically.

### Why this shape

Each layer owns one responsibility and can be replaced without rippling: dossier owns what needs doing; worktree skills own where work happens; Ship owns agent execution and durable run state; pr-risk owns review depth; reviewer bots are swappable finders; review-coordinator owns their consolidated artifact; Gate alone owns exact-head merge authorization; Escalate carries a human resolution without deciding it; Console explains Gate state; Flare notifies; Consult handles cross-repo knowledge; Channel owns optional agent-to-agent messaging and supersedes Huddle. The workbench is a menu, not a checklist.

### The shape underneath

The contract planes are **State** (dossier plus run, verdict, grant, and receipt artifacts), **Execution** (Ship), **Verification** (review and Gate's escalate-only verifier ladder), **Capability** (scoped operator-minted grants), and **Observability** (Console, Flare, /wip, /shipped, /status). This section is **Composition**. Planes share typed artifacts - evidence -> verdict -> action - rather than call stacks.
<!-- END dev-workbench -->
EOF
