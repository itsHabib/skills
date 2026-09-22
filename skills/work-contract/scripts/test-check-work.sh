#!/usr/bin/env bash
# Runs check-work.sh against generated contracts: literal markup passes, unfilled
# placeholders and malformed handoffs fail with their codes.
set -euo pipefail

validator="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-work.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
repo="$tmp/repo"

git init -q "$repo"
git -C "$repo" -c user.name=test -c user.email=test@example.invalid commit -q --allow-empty -m fixture
sha=$(git -C "$repo" rev-parse HEAD)

# contract STATUS OUTCOME PRESERVE [HANDOFF...] writes WORK.md. HANDOFF lines
# follow "- Last:" and default to a single "- Next:".
contract() {
  local status=$1 outcome=$2 preserve=$3
  shift 3
  [[ $# -gt 0 ]] || set -- "- Next: run the validator."
  cat >"$repo/WORK.md" <<EOF
<!-- reaper-work:v1 -->
# Work: Validate contract text

Work-ID: contract-text
Status: $status
Subject: git:$sha
Stop-at: local-green

## Outcome

$outcome

## Preserve

$preserve

## Change

- \`check-work.sh\`: the rule under test.

## Prove

- Green: \`bash test-check-work.sh\` exits 0.
- Red: a malformed contract is rejected.

## Stop

- Stop at local green.

## Evidence

- Pending: not run yet.

## Handoff

- Last: fixture written.
EOF
  printf '%s\n' "$@" >>"$repo/WORK.md"
}

# expect VERDICT DESCRIPTION: VERDICT is pass or the failure code.
expect() {
  local verdict=$1 description=$2
  if bash "$validator" --root "$repo" >"$tmp/out" 2>"$tmp/err"; then
    [[ $verdict == pass ]] && return 0
    printf 'FAIL %s: passed, expected %s\n' "$description" "$verdict" >&2
    exit 1
  fi
  grep -q "^work_contract:$verdict:" "$tmp/err" && return 0
  printf 'FAIL %s: expected %s, got: %s\n' "$description" "$verdict" "$(cat "$tmp/err")" >&2
  exit 1
}

# outcome VERDICT DESCRIPTION TEXT checks one Outcome line in a valid contract.
outcome() {
  contract active "$3" "- Existing contracts keep validating."
  expect "$1" "$2"
}

outcome pass "plain contract" "The validator accepts literal markup."

# Literal markup passes, in prose or code spans.
outcome pass "JSX component in a code span" "Render the \`<Button>\` component in the header."
outcome pass "JSX component in prose" "Render the <Button> component in the header."
outcome pass "acronym-led JSX component" "Swap \`<SVGIcon>\` for the sprite."
outcome pass "attributed tag" "Replace \`<div class=\"card\">\` with the card component."
outcome pass "unquoted attribute in prose" "Validate the <input type=email> field."
outcome pass "self-closing tag" "Put a <br/> after the title and render \`<Card />\` below it."
outcome pass "fragment closed on its line" "Wrap each entry as \`<li>Item</li>\` inside the list."
outcome pass "closing tag" "Close the list with \`</ul>\`."

# Unfilled placeholders fail wherever they sit.
outcome placeholder "placeholder in prose" "Record the digest as <digest>."
outcome placeholder "placeholder phrase in a code span" "Run \`<exact command>\` before handing off."
outcome placeholder "placeholder with a slash" "Open the pull request against <owner/repo>."
outcome placeholder "equals sign without an attribute" "Record <owner=repo> before continuing."
outcome placeholder "slash placeholder ending in />" "Copy the files to <owner/repo/>."
outcome placeholder "sentence-case placeholder" "<Describe the change in one sentence>"
outcome placeholder "uppercase placeholder" "Retry <N> times."
outcome placeholder "placeholder after markup" "Render \`<Button>\` and wire it to <handler>."
outcome placeholder "placeholder in an attribute value" "Link it as \`<a href=\"<url>\">docs</a>\`."
outcome placeholder "placeholder in a JSX prop" "Render \`<Button onClick={<handler>}>\` in the form."
outcome placeholder "bare lowercase tag reads like <path>" "Open the \`<dialog>\` on save."
outcome placeholder "TODO marker" "Finish the TODO list."

# Handoff and list rules.
contract active "Plain outcome." "- "
expect section_empty "list item without content"
contract active "Plain outcome." "- Existing contracts keep validating." \
  "- Next: run the validator." "- Blocked: waiting on review."
expect nonblocked_has_blocked "Blocked handoff on active work"
contract active "Plain outcome." "- Existing contracts keep validating." \
  "- Next: run the validator." "- Next: something else."
expect handoff_count "two Next handoffs"
contract blocked "Plain outcome." "- Existing contracts keep validating." \
  "- Blocked: waiting on review." "- Blocked: waiting on CI."
expect handoff_count "two Blocked handoffs"
contract blocked "Plain outcome." "- Existing contracts keep validating." "- Blocked: waiting on review."
expect pass "blocked contract"
