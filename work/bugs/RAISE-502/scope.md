# RAISE-502: Session counter reset

WHAT:      Session index (index.jsonl) lost when .raise/rai/personal/ added to .gitignore.
           get_next_id() derives next ID from max ID in file — no file means reset to SES-001.
           ID collision with historical sessions. Pattern references (learned_from: SES-009) broken.
WHEN:      After .raise/rai/personal/ was gitignored and git removed tracked files.
WHERE:     src/raise_cli/memory/writer.py:get_next_id (lines 320-361)
           .raise/rai/personal/sessions/index.jsonl (missing)
EXPECTED:  Session IDs never collide. Lost index recoverable or preventable.
Done when: 1. get_next_id is resilient to missing/empty index.jsonl
           2. Recovery mechanism exists for lost session history
           3. Regression test covers empty-file and recovery scenarios
