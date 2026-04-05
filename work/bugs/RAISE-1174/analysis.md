# RAISE-1174: Analysis

## Root Cause (XS — cause evident)

Confluence REST API `cql` endpoint requires CQL syntax. The `search()` method passed user input directly without validation or wrapping.

## Current State

Fix already applied in `784d1a56` (2026-04-01): `_ensure_cql()` static method detects plain text vs CQL and wraps plain text in `siteSearch ~ "..."`.

The fix is correct but **has zero test coverage**. The existing `TestSearch` tests either pass CQL directly or don't verify the wrapping behavior.

## Fix Approach

Add regression tests for `_ensure_cql()`:
1. Plain text → wrapped in `siteSearch ~ "..."`
2. CQL with operators (~, =, AND, OR, ORDER BY) → passthrough
3. Plain text with quotes → properly escaped
4. Edge cases: empty string, single word
5. Verify `search()` integration calls `_ensure_cql` transparently
