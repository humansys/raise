# Retrospective: RAISE-162

## Summary
- **Story:** RAISE-162 — Add encoding="utf-8" to read_text() calls in test suite
- **Size:** XS
- **Completed:** 2026-02-17
- **Commits:** 2 (fix + hook)

## What Went Well
- Fully deterministic fix — `sed` replaced 123 call sites cleanly, zero manual edits
- Regression prevention added via pre-commit hook — future-proofed
- Interactive design taught encoding fundamentals without slowing delivery

## What Could Improve
- Nothing — XS story executed as XS story

## Learnings
- `pathlib.read_text()` without encoding defaults to OS encoding (cp1252 on Windows). UTF-8 default comes in Python 3.15 (PEP 686).
- `! grep` as pre-commit hook is the simplest regression prevention for textual anti-patterns (PAT-E-334)

## Patterns Persisted
- PAT-E-334: Grep-negated pre-commit hooks for regression prevention
