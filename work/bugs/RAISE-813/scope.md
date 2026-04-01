WHAT:      rai signal emit-work --event complete displays "{phase} complete" instead of "{work_type} complete"
WHEN:      rai signal emit-work story S789.1 --event complete (without explicit --phase)
WHERE:     signal.py:118 (_print_work_result) — output uses {phase} in label; signal.py:152 — --phase defaults to "design"
EXPECTED:  Output should say "story complete" or require explicit --phase when using --event complete
Done when: Display output reflects the work type or enforces explicit phase

TRIAGE:
  Bug Type:    UX
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Missing

ROOT CAUSE (5 Whys):
  1. Why wrong label? _print_work_result uses {phase} not {work_type} in the complete message
  2. Why phase=design? --phase defaults to "design" — always, regardless of --event value
  3. Why no coupling? --event and --phase are independent options with no cross-validation
  4. Why independent? Design assumed callers (skills) always pass both flags explicitly
  5. Why no guard? No integration test for CLI output when only --event is passed

PROCESS IMPROVEMENT:
  CLI commands with coupled semantics (event+phase) need cross-validation or required groups.
  Default values that produce misleading output are worse than requiring the flag.

STATUS: Reproduced — "✓ Story S789.1 → design complete" when --phase was never specified.
