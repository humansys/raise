# Retrospective: S17.4 — Analyzer Adjustments

## Summary
- **Story:** S17.4
- **Size:** S (estimated 30 min, actual ~15 min)
- **Velocity:** 2x

## What Went Well
- Design identified formatter was already done (saved a task)
- TDD cycle clean and mechanical
- Integration test on real zambezi PHP data validated categories work
- Jidoka caught vendor duplicate IDs (safety net working)

## What Could Improve
- Scanner lacks `--exclude` for vendor/node_modules (PAT-247)

## Heutagogical Checkpoint

### What did you learn?
- Laravel uses PascalCase dirs (Controllers/, Models/) vs Python/JS lowercase
- Category map needs both conventions for multi-language support
- Subdirectory scans produce relative paths, so patterns match regardless of tree position

### What would you change about the process?
- Nothing — right amount of ceremony for S-sized story

### Are there improvements for the framework?
- No framework changes needed

### What are you more capable of now?
- Multi-language path convention mapping — generalizes to any framework with directory-based conventions

## Patterns Persisted
- PAT-247: Scanner needs exclude patterns for vendor/node_modules

## Action Items
- [ ] Future story: add --exclude to raise discover scan
