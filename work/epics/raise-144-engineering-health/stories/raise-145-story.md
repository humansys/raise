# RAISE-145: Remove vestigial "Unified" prefix from graph classes

## User Story

**As a** developer working on the raise-commons codebase,
**I want** all graph classes to use clean names without the "Unified" prefix,
**So that** the naming reflects the current architecture (single graph, no ambiguity).

## Acceptance Criteria

- No graph class in source code has the "Unified" prefix
- Discovery artifacts are regenerated with correct class names
- All tests pass
- All imports are correct and up to date

## Size

XS -- source classes already renamed; remaining work is artifact cleanup.
