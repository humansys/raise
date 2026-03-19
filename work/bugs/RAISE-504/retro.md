# RAISE-504: Retrospective

## What was done
- Removed `rai discover build` command (dead code from E13, superseded by `rai graph build` in E11)
- Removed 4 deprecated discovery skills (start, scan, validate, document) from both .claude/skills/ and skills_base/
- Cleaned all references in CLI hints, methodology.yaml, skills_base/__init__.py, and tests
- Net: -1,623 lines, discovery surface reduced from 5 skills + 1 command to 1 skill

## Root cause
Post-unification cleanup was never done. When `rai graph build` absorbed component loading,
`rai discover build` should have been removed. When `/rai-discover` unified the pipeline,
the 4 granular skills should have been deleted, not just marked deprecated.

## Pattern
Deprecation without deletion creates cognitive load. "Kept for backward compatibility" with
zero base installed means keeping dead code. Remove immediately when there are no consumers.

## Pre-existing issues found
- tests/cli/commands/test_adapters.py::test_check_json_all_builtins_compliant — failing
- tests/memory/test_loader.py::test_load_with_real_rai_directory — invalid isoformat in patterns.jsonl
