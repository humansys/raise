# RAISE-1278: Work ID casing inconsistency generates duplicate learning records

WHAT:      write_record() preserves work_id casing from caller — lowercase "s1051.6" creates separate directory from uppercase "S1051.6"
WHEN:      Different sessions/agents pass work_id with different casing (branch regex captures case-insensitive)
WHERE:     packages/raise-cli/src/raise_cli/memory/learning.py:write_record(), read_record()
EXPECTED:  Single canonical directory per work_id regardless of input casing
Done when: work_id normalized to uppercase in write_record and read_record; existing lowercase dirs migrated; no duplicate dirs on disk
