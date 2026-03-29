# Analysis: RAISE-1007

## Tier: XS — cause evident from upstream research

## Root Cause

claude-agent-sdk v0.1.48 timing issue: stdin channel to subprocess closes before
in-flight hook callbacks (PreToolUse, PostToolUse, Stop) complete. The SDK's
ProcessTransport.write() throws after the stream is already shut down.

## Evidence

- SDK PRs #731, #746, #729 (v0.1.51) + #751 (v0.1.52) directly fix the lifecycle
- anthropics/claude-agent-sdk-python#578 (CLOSED) — ProcessTransport crash with string prompts
- Workaround in codebase: `and False` at runtime.py:305, 3 tests skipped

## Fix Approach

1. Bump claude-agent-sdk 0.1.48 → 0.1.52
2. Remove `and False` hack from runtime.py:305
3. Unskip 3 tests
4. Verify no ProcessTransport crash
