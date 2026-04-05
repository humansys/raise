# Retrospective: RAISE-1272

## Summary
- Root cause: Substring matching (`keyword in title_lower`) cannot distinguish container pages from individual artifact pages
- Fix approach: Regex filter `^[A-Z]+-\d+\s*:` skips artifact-like titles before keyword matching
- Classification: Logic/S3-Low/Code/Incorrect

## Process Improvement
**Prevention:** Any title-matching logic against user-generated content should include a negative filter for known artifact patterns — titles are not controlled vocabulary.
**Pattern:** Logic + Code + Incorrect → substring match too permissive for structured naming conventions.

## Heutagogical Checkpoint
1. Learned: Confluence spaces frequently have individual artifacts at top level — matching logic must distinguish containers from artifacts.
2. Process change: When writing keyword matching against user-generated titles, test with realistic mixed content (containers + artifacts).
3. Framework improvement: None needed — the fix is minimal and self-contained.
4. Capability gained: Understanding of suggest_routing's role in the adapter-setup flow (advisory, not authoritative).

## Patterns
- Added: PAT-E-730 (artifact-title filtering before substring match)
- Reinforced: none evaluated
