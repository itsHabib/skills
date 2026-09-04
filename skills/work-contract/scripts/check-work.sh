#!/usr/bin/env bash
set -euo pipefail

repo_root=$(pwd)
output=human
work_file=WORK.md
work_file_set=""

fail() {
  local code=$1
  local detail=$2
  printf 'work_contract:%s: %s\n' "$code" "$detail" >&2
  exit 1
}

usage() {
  printf 'usage: check-work.sh [--root PATH] [--json] [WORK.md]\n' >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || usage
      repo_root=$2
      shift 2
      ;;
    --json)
      output=json
      shift
      ;;
    --help | -h)
      usage
      ;;
    --*)
      usage
      ;;
    *)
      [[ -z $work_file_set ]] || usage
      work_file=$1
      work_file_set=yes
      shift
      ;;
  esac
done

if [[ ! -d $repo_root ]]; then
  fail root_missing "repository root does not exist: $repo_root"
fi
repo_root=$(cd "$repo_root" && pwd)
cd "$repo_root"

field() {
  local name=$1
  local count
  local value
  count=$(awk -v prefix="$name: " 'index($0, prefix) == 1 { found++ } END { print found + 0 }' "$work_file")
  [[ $count -eq 1 ]] || fail metadata_count "$name must appear exactly once"
  value=$(awk -v prefix="$name: " 'index($0, prefix) == 1 { print substr($0, length(prefix) + 1) }' "$work_file")
  [[ -n $value ]] || fail metadata_empty "$name must not be empty"
  printf '%s\n' "$value"
}

heading_line() {
  local heading=$1
  local count
  local line
  count=$(awk -v heading="$heading" '$0 == heading { found++ } END { print found + 0 }' "$work_file")
  [[ $count -eq 1 ]] || fail section_count "$heading must appear exactly once"
  line=$(awk -v heading="$heading" '$0 == heading { print NR }' "$work_file")
  printf '%s\n' "$line"
}

require_list_item() {
  local heading=$1
  local start=$2
  local end=$3
  awk -v start="$start" -v end="$end" \
    'NR > start && NR < end && /^- / { found=1 } END { exit !found }' "$work_file" ||
    fail section_empty "$heading needs at least one list item"
}

require_prefix() {
  local code=$1
  local prefix=$2
  local start=$3
  local end=$4
  awk -v prefix="$prefix" -v start="$start" -v end="$end" \
    'NR > start && NR < end && index($0, prefix) == 1 {
       rest = substr($0, length(prefix) + 1)
       gsub(/^[[:space:]]+|[[:space:]]+$/, "", rest)
       found = found || rest != ""
     }
     END { exit !found }' "$work_file" ||
    fail "$code" "missing or empty $prefix item"
}

[[ -f $work_file ]] ||
  fail missing "cannot read $work_file beneath $repo_root"

first_line=$(sed -n '1p' "$work_file")
[[ $first_line == "<!-- reaper-work:v1 -->" ]] ||
  fail schema "first line must be <!-- reaper-work:v1 -->"

line_count=$(awk 'END { print NR }' "$work_file")
[[ $line_count -le 120 ]] ||
  fail too_large "$work_file has $line_count lines; maximum is 120"

if tail -n +2 "$work_file" | grep -En '(^|[^A-Za-z])(TODO|TBD|FIXME)([^A-Za-z]|$)|<[A-Za-z][^>]*>'; then
  fail placeholder "replace every placeholder before validation"
fi

work_id=$(field Work-ID)
status=$(field Status)
subject=$(field Subject)
stop_at=$(field Stop-at)

[[ $work_id =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] ||
  fail work_id "Work-ID must be lowercase kebab-case"
[[ $status =~ ^(ready|active|blocked|done)$ ]] ||
  fail status "Status must be ready, active, blocked, or done"
[[ $stop_at =~ ^(local-green|pr-ready|reviewed-change|operator-decision)$ ]] ||
  fail stop_at "Stop-at is not a supported authority boundary"

subject_kind=${subject%%:*}
subject_value=${subject#*:}
if [[ $subject_kind == git ]]; then
  [[ $subject_value =~ ^[0-9a-f]{40}$ ]] ||
    fail subject "git subject must contain a full lowercase commit SHA"
  git cat-file -e "${subject_value}^{commit}" 2> /dev/null ||
    fail subject_unknown "git subject does not exist in this repository"
  git merge-base --is-ancestor "$subject_value" HEAD ||
    fail subject_not_ancestor "git subject is not an ancestor of HEAD"
fi
if [[ $subject_kind == recipe ]]; then
  [[ $subject_value =~ ^sha256:[0-9a-f]{64}$ ]] ||
    fail subject "recipe subject must contain a sha256 digest"
  [[ -f REAPER.lock.yaml ]] ||
    fail subject_receipt "recipe subject requires REAPER.lock.yaml"
  receipt_digest=$(awk '$1 == "originRecipeDigest:" { print $2 }' REAPER.lock.yaml)
  [[ $receipt_digest == "$subject_value" ]] ||
    fail subject_mismatch "WORK.md subject does not match the generation receipt"
fi
[[ $subject_kind =~ ^(git|recipe)$ ]] ||
  fail subject_kind "Subject must use git: or recipe: identity"

title_count=$(awk '/^# / { found++ } END { print found + 0 }' "$work_file")
[[ $title_count -eq 1 ]] || fail title "exactly one top-level title is required"
grep -Eq '^# Work: .+$' "$work_file" || fail title "top-level title must start with # Work:"

sections=("## Outcome" "## Preserve" "## Change" "## Prove" "## Stop" "## Evidence" "## Handoff")
section_lines=()
previous=0
for section in "${sections[@]}"; do
  line=$(heading_line "$section")
  [[ $line -gt $previous ]] || fail section_order "$section is out of order"
  section_lines+=("$line")
  previous=$line
done

unknown_sections=$(awk '/^## / { print }' "$work_file" | grep -Fvx -f <(printf '%s\n' "${sections[@]}") || true)
[[ -z $unknown_sections ]] ||
  fail section_unknown "unsupported section: $(printf '%s' "$unknown_sections" | head -1)"

outcome_start=${section_lines[0]}
preserve_start=${section_lines[1]}
change_start=${section_lines[2]}
prove_start=${section_lines[3]}
stop_start=${section_lines[4]}
evidence_start=${section_lines[5]}
handoff_start=${section_lines[6]}
document_end=$((line_count + 1))

awk -v start="$outcome_start" -v end="$preserve_start" \
  'NR > start && NR < end && NF > 0 { found=1 } END { exit !found }' "$work_file" ||
  fail outcome_empty "Outcome needs one concrete observable result"

require_list_item Preserve "$preserve_start" "$change_start"
require_list_item Change "$change_start" "$prove_start"
require_list_item Stop "$stop_start" "$evidence_start"
require_list_item Evidence "$evidence_start" "$handoff_start"
require_list_item Handoff "$handoff_start" "$document_end"

bad_change=$(awk -v start="$change_start" -v end="$prove_start" \
  'NR > start && NR < end && /^- / && $0 !~ /^- `[^`]+`: / { print; exit }' "$work_file")
[[ -z $bad_change ]] ||
  fail change_path "Change items must start with one exact backticked path: $bad_change"

require_prefix green_proof_missing "- Green:" "$prove_start" "$stop_start"
require_prefix red_proof_missing "- Red:" "$prove_start" "$stop_start"
require_prefix last_handoff_missing "- Last:" "$handoff_start" "$document_end"

if [[ $status == blocked ]]; then
  require_prefix blocked_handoff_missing "- Blocked:" "$handoff_start" "$document_end"
  if awk -v start="$handoff_start" -v end="$document_end" \
    'NR > start && NR < end && /^- Next:/ { found=1 } END { exit !found }' "$work_file"; then
    fail blocked_has_next "blocked work replaces Next with Blocked"
  fi
fi
if [[ $status != blocked ]]; then
  require_prefix next_handoff_missing "- Next:" "$handoff_start" "$document_end"
fi
if [[ $status == "done" ]]; then
  require_prefix done_needs_verified_evidence "- Verified:" "$evidence_start" "$handoff_start"
  if awk -v start="$evidence_start" -v end="$handoff_start" \
    'NR > start && NR < end && /^- Pending:/ { found=1 } END { exit !found }' "$work_file"; then
    fail done_has_pending_evidence "done work cannot retain pending evidence"
  fi
fi

if [[ $output == json ]]; then
  printf '{"schema":"reaper-work/v1","workId":"%s","status":"%s","subject":"%s","stopAt":"%s","verdict":"pass"}\n' \
    "$work_id" "$status" "$subject" "$stop_at"
  exit 0
fi

printf 'work contract passed: %s (%s, %s)\n' "$work_id" "$status" "$subject"
