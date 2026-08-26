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

# SYNC.md lists the public transforms, but its identifier scan was a MANUAL
# pre-push step - so check.sh passed while the tree still carried `~/pers/`
# roots. A documented rule nothing enforces is a rule that drifts. This makes
# transforms 2 and 3 part of the gate.
#
# Patterns are literal-ish EREs, one per line: <pattern>|<what it violates>
#
# Backslashes survive the quoted heredoc verbatim and are then consumed once by
# the ERE, so one literal `\` is written `\\` here. The original Windows pattern
# was `C:\\\\Users` - doubled one time too many. It asked for `C:\\Users`, two
# real backslashes, and so never matched the single-backslash path that had
# actually leaked. Same blind spot on the separator: `pers/` cannot see
# `pers\ship`.
#
# The patterns describe the *shape* of an operator path rather than naming the
# operator, so the gate stays useful without hardcoding an identity into a
# public file.
scrub_patterns() {
  cat <<'PATTERNS'
pers/|SYNC.md #3: operator path root (use the ~/projects/ placeholder)
pers\\|SYNC.md #3: operator path root, Windows separator (use ~/projects/)
C:\\Users\\[A-Za-z0-9._<>-]+|SYNC.md #3: Windows operator home path
\$HOME/pers|SYNC.md #3: operator path root
PATTERNS
}

# Placeholder spellings SYNC.md blesses. /recover has to show a real
# `C:\Users\you\projects` to explain how it decodes an encoded session path, so
# the gate has to tell a documented placeholder from a live home directory.
scrub_allowlist() {
  cat <<'ALLOWED'
C:\Users\you
C:\Users\<name>
C:\Users\<user>
C:\Users\username
ALLOWED
}

# True only when EVERY match on the line is a blessed placeholder. A line that
# mixes `C:\Users\you` with a real home path still fails.
scrub_line_is_allowed() {
  local pattern="$1" line="$2" allowlist="$3"
  local match ok found any=0

  while IFS= read -r match; do
    [[ -z "$match" ]] && continue
    any=1
    found=0
    while IFS= read -r ok; do
      [[ -z "$ok" ]] && continue
      [[ "${match,,}" == "${ok,,}" ]] && { found=1; break; }
    done <<<"$allowlist"
    [[ "$found" -eq 0 ]] && return 1
  done < <(printf '%s\n' "$line" | grep -oiE "$pattern" || true)

  # No matches extracted means the line reached us some way we do not model;
  # treat that as not-allowed rather than silently passing it.
  [[ "$any" -eq 1 ]]
}

check_scrub() {
  local pattern reason hits hit line allowlist
  allowlist="$(scrub_allowlist)"

  while IFS='|' read -r pattern reason; do
    [[ -z "$pattern" ]] && continue
    hits="$(grep -rniE "$pattern" skills/ 2>/dev/null || true)"
    [[ -z "$hits" ]] && continue
    while IFS= read -r hit; do
      line="${hit#*:}"
      line="${line#*:}"
      scrub_line_is_allowed "$pattern" "$line" "$allowlist" && continue
      fail "${hit%%:*}: ${reason} -> ${hit#*:}"
    done <<<"$hits"
  done < <(scrub_patterns)
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

echo "Checking public scrub (SYNC.md transforms)..."
check_scrub

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
