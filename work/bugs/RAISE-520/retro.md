# RAISE-520 Retro — Path injection via --memory-dir flag

## Fix verified
- Root cause (missing .resolve()) addressed in writer.py + pattern.py
- Regression tests GREEN, all gates pass
- SonarQube finding addressed at source (writer.py) + defense-in-depth (CLI layer)

## Learnings
- SonarQube path injection findings on CLI tools require context: not all are
  web-style vulnerabilities, but the fix (resolve()) is cheap and correct anyway.
- Test assertions must match what's actually observable — CLI output doesn't
  always expose internal path representations. Unit tests on writer functions
  give more meaningful RED/GREEN for path-related fixes.

## Pattern
Not emitted — PAT-F-044 (ruff format post-edit) already covers related hygiene.
Fix is mechanical (add .resolve()), no new process insight.
