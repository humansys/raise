# RAISE-511: Retrospective

## Fix verified
- Root cause addressed: all `rai-cli` occurrences replaced with `raise-cli` in `docs/src/`
- No regressions: change is purely textual, no logic affected
- CHANGELOG updated under [Unreleased] for 2.2.3

## Learning
The `rai-cli → raise-cli` rename (s369.5/s463.4) missed the Astro docs site directory.
Future renames should include an explicit grep across all directories before closing.

## Pattern
Recurring risk: multi-location renames that don't cover the docs site source.
