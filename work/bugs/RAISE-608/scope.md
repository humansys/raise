# Scope: RAISE-608

WHAT:      `rai pattern add` defaults to personal scope, writing to `.raise/rai/personal/patterns.jsonl`.
           `rai pattern reinforce` defaults to project scope, reading from `.raise/rai/memory/patterns.jsonl`.
           These are different files — add reports success, reinforce can't find the pattern.

WHEN:      When `rai pattern add` is called without explicit --scope flag (default behavior).

WHERE:     src/raise_cli/cli/commands/pattern.py:176 — `scope` default = "personal"
           src/raise_cli/cli/commands/pattern.py:72  — `scope` default = "project" (reinforce)

EXPECTED:  `rai pattern add` without --scope writes to project scope (.raise/rai/memory/patterns.jsonl),
           consistent with `rai pattern reinforce` default scope.

Done when: `rai pattern add "..."` (no --scope) writes to .raise/rai/memory/patterns.jsonl.
           `rai pattern reinforce <id> --vote 1` (no --scope) can find that pattern.
           All gates pass.

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Incorrect
