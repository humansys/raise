# RAISE-502: Retrospective

## What happened
Session counter reset to SES-001 when index.jsonl was lost after .raise/rai/personal/
was added to .gitignore. get_next_id() had no fallback — single point of failure.

## Root cause
get_next_id() derived IDs exclusively from index.jsonl line scan. No file = max_num 0 = SES-001.

## Fix applied
Added directory scan fallback: after scanning index.jsonl, also scan sibling directories
matching {PREFIX}-{NNN} pattern. Takes max of both sources. 13 lines added to writer.py.

## What went well
- Bug was straightforward once traced
- TDD cycle clean: 5 RED tests → fix → all GREEN
- All 3698 existing tests unaffected

## Pattern
Gitignored files that serve as single source of truth for stateful counters need a
filesystem-based fallback. The directories themselves are a durable secondary source
because they survive independently of the index file.

## Remaining items from RAISE-502 description
- Orphan SES-025 (MEDIUM) — tracked separately as RAISE-505
- Third sub-bug (description truncated in Jira) — needs verification
