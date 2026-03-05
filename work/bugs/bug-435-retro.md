# RAISE-435 Retrospective

## Summary
JQL queries with `!=` silently returned empty results when invoked from Claude
Code Bash tool, which escapes `!` to `\!`. Fixed by normalizing `\!` → `!` at
the adapter boundary.

## Learnings
- Claude Code Bash tool mangles `!` (bash history expansion char) even in
  single-quoted strings — this is a known quirk of the tool, not bash itself
- Silent failures (Jira returns empty for invalid JQL instead of error) are the
  worst kind — they erode trust without signaling anything wrong
- System boundary sanitization is essential when CLI input may arrive from
  different shell environments

## Initially misdiagnosed
Bug was first closed as "false positive" because it worked in a real terminal.
The right framing: our primary user interface IS Claude Code — if it breaks
there, it's a real bug regardless of terminal behavior.

## Pattern
Defensive input normalization at system boundaries for shell-mangled operators.
