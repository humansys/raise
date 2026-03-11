# RAISE-533: Retrospective

## Summary
User-controlled JSONL content logged without sanitization. ANSI escapes, null bytes, and control characters passed through to log output.

## Root Cause
`line[:50]` logged directly via `%s` formatting. `splitlines()` prevents newline injection but not other control characters.

## Fix
Apply `str.encode("unicode_escape").decode("ascii")` before logging — escapes all non-ASCII and control characters to safe representations.

## Note
Low practical risk (local CLI tool, file content is developer-controlled), but good hygiene for an OSS project where SonarCloud gates matter.
