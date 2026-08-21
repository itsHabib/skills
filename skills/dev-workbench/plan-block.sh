#!/usr/bin/env bash
# Show the exact paired-entrypoint diff for the canonical dev-workbench block.
# Read-only: writes only unified diffs to stdout.

set -euo pipefail

repo_dir=""
requested_guides=()
while [ $# -gt 0 ]; do
  case "$1" in
    --repo-dir)
      [ $# -ge 2 ] || { echo "plan-block.sh: --repo-dir needs a path" >&2; exit 2; }
      repo_dir="$2"
      shift 2
      ;;
    --repo-dir=*) repo_dir="${1#*=}"; shift ;;
    --guide)
      [ $# -ge 2 ] || { echo "plan-block.sh: --guide needs a path" >&2; exit 2; }
      requested_guides+=("$2")
      shift 2
      ;;
    --guide=*) requested_guides+=("${1#*=}"); shift ;;
    *) echo "plan-block.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

[ -n "$repo_dir" ] || { echo "plan-block.sh: --repo-dir is required" >&2; exit 2; }
repo_dir=$(cd "$repo_dir" 2>/dev/null && pwd -P) \
  || { echo "plan-block.sh: directory does not exist: $repo_dir" >&2; exit 2; }

skill_dir=$(cd "${BASH_SOURCE[0]%/*}" && pwd)
repo_name=$(basename "$repo_dir")
git_root=$(git -C "$repo_dir" rev-parse --show-toplevel 2>/dev/null || true)
if [[ -n $git_root ]]; then
  repo_dir=$(cd "$git_root" && pwd -P)
  common_dir=$(git -C "$repo_dir" rev-parse --path-format=absolute --git-common-dir)
  case "$common_dir" in
    */.git) repo_name=$(basename "$(dirname "$common_dir")") ;;
    */.git/modules/*) repo_name=$(basename "$common_dir") ;;
    *) repo_name=$(basename "$repo_dir") ;;
  esac
fi
block=$(bash "$skill_dir/render-block.sh" --repo "$repo_name")

validate_markers() {
  local file="$1" begin_count end_count begin_line end_line
  begin_count=$(grep -c '^<!-- BEGIN dev-workbench' "$file" || true)
  end_count=$(grep -c '^<!-- END dev-workbench' "$file" || true)
  if [[ $begin_count -eq 0 && $end_count -eq 0 ]]; then
    return 1
  fi
  if [[ $begin_count -ne 1 || $end_count -ne 1 ]]; then
    echo "plan-block.sh: $file has unbalanced or duplicate dev-workbench markers; repair them before planning" >&2
    return 5
  fi
  begin_line=$(grep -n '^<!-- BEGIN dev-workbench' "$file" | cut -d: -f1)
  end_line=$(grep -n '^<!-- END dev-workbench' "$file" | cut -d: -f1)
  if [[ $begin_line -ge $end_line ]]; then
    echo "plan-block.sh: $file has out-of-order dev-workbench markers; repair them before planning" >&2
    return 5
  fi
}

replace_block() {
  local file="$1" line skipping=0 found=0
  while IFS= read -r line || [ -n "$line" ]; do
    if [[ $line == '<!-- BEGIN dev-workbench'* ]]; then
      printf '%s\n' "$block"
      skipping=1
      found=1
      continue
    fi
    if [[ $skipping -eq 1 ]]; then
      [[ $line == '<!-- END dev-workbench'* ]] && skipping=0
      continue
    fi
    printf '%s\n' "$line"
  done <"$file"
  [[ $found -eq 1 ]] || return 3
}

insert_before_line() {
  local file="$1"
  awk '
    /^## (State|Status)[[:space:]]*$/ && section == 0 { section = NR; next }
    section > 0 && NR > section && /^## / { print NR; found = 1; exit }
    END {
      if (found) exit
      if (section > 0) print NR + 1
    }
  ' "$file"
}

insert_block() {
  local file="$1" at="$2" line previous="" line_no=0 inserted=0
  while IFS= read -r line || [[ -n $line ]]; do
    line_no=$((line_no + 1))
    if [[ $line_no -eq $at ]]; then
      [[ $line_no -eq 1 || -z $previous ]] || printf '\n'
      printf '%s\n' "$block"
      [[ -z $line ]] || printf '\n'
      inserted=1
    fi
    printf '%s\n' "$line"
    previous=$line
  done <"$file"
  if [[ $inserted -eq 0 ]]; then
    [[ -z $previous ]] || printf '\n'
    printf '%s\n' "$block"
  fi
}

render_guide() {
  local file="$1" at
  if grep -q '^<!-- BEGIN dev-workbench' "$file"; then
    replace_block "$file"
    return
  fi
  if grep -q '^## Dev workbench[[:space:]]*$' "$file"; then
    echo "plan-block.sh: $file has an unmarked Dev workbench section; choose wrap, replace, or abort" >&2
    return 4
  fi

  at=$(insert_before_line "$file")
  if [[ -z $at ]]; then
    at=$(awk '/^## Architecture[[:space:]]*$/{print NR; exit}' "$file")
  fi
  if [[ -z $at ]]; then
    at=$(awk '/^## Develop/{print NR; exit}' "$file")
  fi
  if [[ -z $at ]]; then
    at=$(awk '/^## Source material[[:space:]]*$/{print NR; exit}' "$file")
  fi
  if [[ -z $at ]]; then
    at=$(awk 'END{print NR + 1}' "$file")
  fi
  insert_block "$file" "$at"
}

guides=()
if [[ ${#requested_guides[@]} -eq 0 ]]; then
  guides=(CLAUDE.md AGENTS.md)
else
  for requested in "${requested_guides[@]}"; do
    if [[ $requested == /* ]]; then
      file=$requested
    else
      file="$repo_dir/${requested#./}"
    fi
    parent=$(cd "${file%/*}" 2>/dev/null && pwd -P) \
      || { echo "plan-block.sh: guide parent does not exist: $requested" >&2; exit 2; }
    file="$parent/${file##*/}"
    case "$file" in
      "$repo_dir"/*) ;;
      *) echo "plan-block.sh: guide is outside the repository: $requested" >&2; exit 2 ;;
    esac
    guide=${file#"$repo_dir"/}
    case "${guide##*/}" in
      CLAUDE.md|AGENTS.md) ;;
      *) echo "plan-block.sh: guide must be named CLAUDE.md or AGENTS.md: $requested" >&2; exit 2 ;;
    esac
    guides+=("$guide")
  done
fi

found=0
for guide in "${guides[@]}"; do
  file="$repo_dir/$guide"
  [ -f "$file" ] || continue
  found=1
  marker_status=0
  validate_markers "$file" || marker_status=$?
  [[ $marker_status -eq 5 ]] && exit 5
  if [[ $marker_status -eq 1 ]] \
    && grep -q '^## Dev workbench[[:space:]]*$' "$file"; then
    echo "plan-block.sh: $file has an unmarked Dev workbench section; choose wrap, replace, or abort" >&2
    exit 4
  fi
  diff -u --label "a/$guide" --label "b/$guide" "$file" <(render_guide "$file") || true
done
[ "$found" -eq 1 ] || { echo "plan-block.sh: no selected CLAUDE.md or AGENTS.md exists in $repo_dir" >&2; exit 2; }
