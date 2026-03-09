# RAISE-502: Analysis

## Method: 5 Whys

Problem: Session IDs reset to SES-001 after index.jsonl lost.

| # | Why? | Evidence |
|---|------|----------|
| 1 | Counter resets | `get_next_id()` returns SES-001 when file missing (writer.py:343) |
| 2 | index.jsonl gone | `.raise/rai/personal/` gitignored → file lost on clone/new machine |
| 3 | Directory gitignored | Correct design — per-developer data shouldn't be committed |
| 4 | No recovery fallback | ID derived solely from index.jsonl contents |
| 5 | Single source of truth | Original design didn't contemplate file loss |

## Root Cause

`get_next_id()` has a single point of failure: it depends exclusively on
`index.jsonl` with no fallback. When the file is missing or empty, max_num
defaults to 0, producing SES-001 regardless of existing session directories.

## Fix Approach

**In `get_next_id()`**: After scanning index.jsonl (or when file missing), also
scan sibling directories matching the `{PREFIX}-{NNN}` pattern as a secondary
source for max ID. This is minimally invasive — same function, same return
contract, just a fallback data source.

The per-session directories (`SES-001/`, `SES-002/`, etc.) survive independently
of index.jsonl because they're filesystem directories, not lines in a file.

**NOT doing:**
- Index rebuild from directories (over-engineering for this bug)
- Changing storage format (out of scope)
- Backup mechanisms (complexity not justified)
