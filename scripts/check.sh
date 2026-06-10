#!/usr/bin/env bash
# Dependency-free registry hygiene checks for skills/*/SKILL.md and README.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

errors=0
warnings=0

fail() {
  echo "ERROR: $*" >&2
  errors=$((errors + 1))
}

warn() {
  echo "WARN: $*" >&2
  warnings=$((warnings + 1))
}

extract_frontmatter() {
  local file="$1"
  # END guard: reaching EOF without a closing fence is a failure, not an
  # implicit success — otherwise a malformed SKILL.md sails through CI.
  awk '
    NR == 1 && $0 != "---" { exit 1 }
    NR == 1 { next }
    $0 == "---" { closed = 1; exit }
    { print }
    END { if (!closed) exit 1 }
  ' "$file"
}

check_frontmatter() {
  local skill_md="$1"
  local dir
  dir="$(basename "$(dirname "$skill_md")")"

  if [[ "$(head -n1 "$skill_md")" != "---" ]]; then
    fail "$skill_md: frontmatter must start with ---"
    return
  fi

  local fm
  if ! fm="$(extract_frontmatter "$skill_md")"; then
    fail "$skill_md: missing closing --- frontmatter fence"
    return
  fi

  local name description user_invocable argument_hint
  name="$(printf '%s\n' "$fm" | awk -F': ' '/^name:/ { sub(/^name: */, ""); print; exit }')"
  description="$(printf '%s\n' "$fm" | awk -F': ' '/^description:/ { sub(/^description: */, ""); print; exit }')"
  user_invocable="$(printf '%s\n' "$fm" | awk -F': ' '/^user_invocable:/ { sub(/^user_invocable: */, ""); print; exit }')"
  argument_hint="$(printf '%s\n' "$fm" | awk -F': ' '/^argument-hint:/ { sub(/^argument-hint: */, ""); print; exit }')"

  if [[ -z "${name// }" ]]; then
    fail "$skill_md: missing or empty name:"
  elif [[ "$name" != "$dir" ]]; then
    fail "$skill_md: name '$name' does not match directory '$dir'"
  fi

  if [[ -z "${description// }" ]]; then
    fail "$skill_md: missing or empty description:"
  fi

  if [[ -z "${user_invocable// }" ]]; then
    fail "$skill_md: missing user_invocable:"
  fi

  if [[ -z "${argument_hint// }" ]]; then
    warn "$skill_md: missing argument-hint (optional for auto-trigger-only skills)"
  fi
}

check_readme_consistency() {
  local -a readme_skills=()
  local -a dir_skills=()
  local line skill dir

  while IFS= read -r line; do
    if [[ "$line" =~ \`/([a-z0-9-]+)\` ]]; then
      readme_skills+=("${BASH_REMATCH[1]}")
    fi
  done < <(sed -n '/^## Skills$/,/^## /p' README.md | grep '^|' || true)

  for dir in skills/*/; do
    dir_skills+=("$(basename "$dir")")
  done

  for dir in "${dir_skills[@]}"; do
    local found=0
    for skill in "${readme_skills[@]}"; do
      if [[ "$skill" == "$dir" ]]; then
        found=1
        break
      fi
    done
    if [[ "$found" -eq 0 ]]; then
      fail "skills/$dir/ is missing from the README skills table"
    fi
  done

  for skill in "${readme_skills[@]}"; do
    if [[ ! -d "skills/$skill" ]]; then
      fail "README lists /$skill but skills/$skill/ does not exist"
    fi
  done
}

echo "Checking SKILL.md frontmatter..."
# Iterate directories, not the SKILL.md glob — a skill dir with no SKILL.md
# must fail loudly instead of being silently skipped.
for dir in skills/*/; do
  if [[ ! -f "$dir/SKILL.md" ]]; then
    fail "$dir is missing SKILL.md"
    continue
  fi
  check_frontmatter "$dir/SKILL.md"
done

echo "Checking README ↔ skills/ consistency..."
check_readme_consistency

if [[ "$warnings" -gt 0 ]]; then
  echo "Completed with $warnings warning(s)."
fi

if [[ "$errors" -gt 0 ]]; then
  echo "FAILED: $errors error(s)." >&2
  exit 1
fi

echo "All checks passed."
