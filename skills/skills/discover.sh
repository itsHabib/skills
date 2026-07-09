#!/usr/bin/env bash
# Emit a TSV catalog of every discoverable skill, one row per skill:
#   source <TAB> name <TAB> invocable <TAB> description
#
# Sources scanned (a skill missing from one root just yields no rows there):
#   personal        ~/.claude/skills/*/SKILL.md
#   project         <cwd>/.claude/skills/*/SKILL.md
#   worktree:<br>   <cwd>/.claude/worktrees/*/.claude/skills/*/SKILL.md
#
# Assumes single-line `description:` frontmatter (the house convention). A
# folded/multi-line description would be truncated to its first line.
set -euo pipefail

emit_root() {
  local label="$1" dir="$2"
  [ -d "$dir" ] || return 0
  local f
  for f in "$dir"/*/SKILL.md; do
    [ -f "$f" ] || continue
    awk -v src="$label" '
      # frontmatter is the block between the first two --- fences
      /^---[[:space:]]*$/ { fm++; if (fm == 2) exit; next }
      fm == 1 {
        if      ($0 ~ /^name:[[:space:]]*/)           { sub(/^name:[[:space:]]*/, "");           name = $0 }
        else if ($0 ~ /^description:[[:space:]]*/)    { sub(/^description:[[:space:]]*/, "");    desc = $0 }
        else if ($0 ~ /^user_invocable:[[:space:]]*/) { sub(/^user_invocable:[[:space:]]*/, ""); inv  = $0 }
      }
      END {
        if (name == "") { exit }
        if (inv == "")  { inv = "?" }
        gsub(/\t/, " ", desc)
        printf "%s\t%s\t%s\t%s\n", src, name, inv, desc
      }
    ' "$f"
  done
}

emit_root "personal" "$HOME/.claude/skills"
emit_root "project"  "$PWD/.claude/skills"
for wt in "$PWD"/.claude/worktrees/*/.claude/skills; do
  [ -d "$wt" ] || continue
  branch=$(basename "$(dirname "$(dirname "$wt")")")
  emit_root "worktree:$branch" "$wt"
done
