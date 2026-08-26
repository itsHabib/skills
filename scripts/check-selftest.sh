#!/usr/bin/env bash
# Guard test for check.sh's public-scrub gate.
#
# The gate exists because SYNC.md's identifier grep was a manual pre-push step
# that nobody ran. Folding it into check.sh only helps if the patterns actually
# match what leaks - and for a while they did not: `C:\\\\Users` was escaped one
# level too deep and `pers/` could not see a Windows separator, so the exact
# string that reached the public repo sailed through a passing check.
#
# Every case below is a real shape from that history, plus the placeholders the
# docs legitimately need. A regression in the patterns fails here loudly instead
# of quietly re-opening the hole.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK="$ROOT/scripts/check.sh"

failures=0

# A fixture repo shaped enough like this one that check.sh's other gates pass,
# so the exit code reflects the scrub result and nothing else.
make_fixture() {
  local dir="$1" body="$2"

  mkdir -p "$dir/scripts" "$dir/skills/fixture"
  cp "$CHECK" "$dir/scripts/check.sh"

  cat > "$dir/README.md" <<'README'
# Fixture

## Skills

| Skill | What it does |
| --- | --- |
| `/fixture` | fixture skill |

## Other
README

  {
    cat <<'FRONTMATTER'
---
name: fixture
description: fixture skill
argument-hint: "<none>"
user_invocable: true
---

FRONTMATTER
    printf '%s\n' "$body"
  } > "$dir/skills/fixture/SKILL.md"
}

# expectation is `leak` (check.sh must fail) or `clean` (must pass).
case_is() {
  local expectation="$1" name="$2" body="$3"
  local dir output status

  dir="$(mktemp -d)"
  make_fixture "$dir" "$body"

  status=0
  output="$(cd "$dir" && bash scripts/check.sh 2>&1)" || status=$?
  rm -rf "$dir"

  case "$expectation" in
    leak)
      if [[ "$status" -eq 0 ]]; then
        echo "FAIL: $name - check.sh passed on a line it must reject" >&2
        printf '  body: %s\n' "$body" >&2
        failures=$((failures + 1))
        return
      fi
      ;;
    clean)
      if [[ "$status" -ne 0 ]]; then
        echo "FAIL: $name - check.sh rejected a line it must accept" >&2
        printf '  body: %s\n' "$body" >&2
        printf '%s\n' "$output" | sed 's/^/  /' >&2
        failures=$((failures + 1))
        return
      fi
      ;;
  esac

  echo "ok: $name"
}

# The literal string that reached the public repo: a credentials-file path under
# a Windows operator home. This is the case the old patterns missed.
case_is leak 'windows home path with .keys' \
  '   $env:CURSOR_API_KEY = (Get-Content C:\Users\Bob\pers\ship\.keys -Raw)'

case_is leak 'windows home path in a cd' \
  '   cd C:\Users\Bob\pers\ship'

case_is leak 'operator path root, posix separator' \
  'Source: `~/pers/dossier/`.'

case_is leak 'operator path root, windows separator' \
  'Resolve it as `pers\gate\gate.exe`.'

case_is leak 'HOME-relative operator path root' \
  'State lives under $HOME/pers/gate/state.'

# A blessed placeholder alone is documentation, not a leak.
case_is clean 'documented windows placeholder' \
  'Decode `C--Users-you-projects` back into `C:\Users\you\projects`.'

case_is clean 'placeholder path root' \
  'Source: `~/projects/dossier/`.'

# Mixing the two must not launder the real one.
case_is leak 'placeholder alongside a real home path' \
  'Rewrite C:\Users\you\projects as C:\Users\Bob\projects.'

if [[ "$failures" -gt 0 ]]; then
  echo "FAILED: $failures scrub-gate case(s)." >&2
  exit 1
fi

echo "All scrub-gate cases passed."
