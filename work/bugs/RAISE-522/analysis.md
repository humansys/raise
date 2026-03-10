# RAISE-522 — Analysis

## Tier: XS — Single causal chain, cause evident

## Root Cause

`reinforce_pattern(file_path, ...)` in `writer.py` receives a `Path` derived from
the user-controlled `--memory-dir` CLI option and passes it to `read_text()` (line 463)
and `write_text()` (line 507) without normalizing it internally.

The previous fix (RAISE-520) applied `.resolve()` only in `pattern.py:110` (the call
site). SonarCloud's interprocedural taint analysis traces the source (CLI arg) through
the call stack to the sinks inside `reinforce_pattern`, ignoring the caller's resolution.

## Causal Chain (5 Whys)

Problem:  SonarCloud BLOCKER — path injection in reinforce_pattern
Why 1:    file_path reaches read_text/write_text without resolve() inside the function
Why 2:    RAISE-520 fix applied resolve() only at the call site in pattern.py
Why 3:    reinforce_pattern is a library function — its safety should not depend on callers
Root:     Defense-in-depth missing at function boundary

## Fix Approach

Add `file_path = file_path.resolve()` as first statement in `reinforce_pattern`,
before any file I/O. Idempotent (already resolved paths stay resolved). No behavior
change for compliant callers.
