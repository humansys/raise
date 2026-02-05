# ISSUE-002: Pattern type "collaboration" not valid

> Parked: 2026-02-05
> Priority: P2 (workaround exists)
> Status: PARKED

---

## Problem

When adding a pattern with type "collaboration", the CLI rejects it:

```bash
uv run raise memory add-pattern "..." -c "collaboration,dx" -t collaboration
```

**Error:**
```
Error: Invalid pattern type: collaboration
Valid types: codebase, process, architecture, technical
```

**Expected:** "collaboration" should be a valid pattern type for patterns about human-AI interaction, communication, and developer experience.

## Impact

- Patterns about collaboration, communication, DX must use `process` type
- Reduces semantic precision of pattern categorization
- Minor inconvenience (workaround is easy)

## Evidence

### Session SES-054 (2026-02-05)

```bash
# This failed:
uv run raise memory add-pattern "Show modified/created files list after commits — helps humans track changes across folders" -c "collaboration,dx,communication" -t collaboration

# Workaround used:
uv run raise memory add-pattern "..." -t process  # Works
```

### Cascade Failure

When run in parallel with other Bash calls, the failure caused sibling tool calls to error:

```
● Bash(uv run raise memory add-pattern ... -t collaboration)
  ⎿  Error: Exit code 1
     Error: Invalid pattern type: collaboration
     Valid types: codebase, process, architecture, technical

● Bash(uv run raise memory add-session ...)
  ⎿  Error: Sibling tool call errored

● Bash(uv run raise telemetry emit-session ...)
  ⎿  Error: Sibling tool call errored
```

## Current Workaround

Use `process` type for collaboration patterns:

```bash
uv run raise memory add-pattern "..." -t process
```

The `-c` context tags can still include "collaboration" for searchability.

## Proposed Fix

Add "collaboration" to valid pattern types in the CLI:

```python
# Likely in src/raise_cli/memory/schemas.py or similar
PatternType = Literal["codebase", "process", "architecture", "technical", "collaboration"]
```

## Questions

1. Is "collaboration" the right term? Alternatives: "dx", "communication", "workflow"
2. Should we add multiple new types or keep it minimal?
3. Where is the pattern type validation defined?

## Related

- Session: SES-054
- Pattern: PAT-108 (added with `process` type as workaround)

---

*Created: 2026-02-05*
