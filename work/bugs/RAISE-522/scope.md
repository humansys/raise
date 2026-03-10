# RAISE-522 — Scope

WHAT:      reinforce_pattern() uses file_path (user-controlled via --memory-dir) in
           read_text() and write_text() without calling .resolve() inside the function.
           SonarCloud traces the taint interprocedurally from CLI arg to sink.

WHEN:      Any call to `rai pattern reinforce` with a crafted --memory-dir value.
           The caller (pattern.py:110) resolves, but the function itself does not.

WHERE:     src/raise_cli/memory/writer.py — reinforce_pattern(), lines 463 and 507

EXPECTED:  reinforce_pattern() is safe regardless of caller — .resolve() applied
           at function entry before any file access.

Done when: file_path = file_path.resolve() present at entry of reinforce_pattern().
           SonarCloud BLOCKER AZybe_Id00NbGlYNRMea resolves on next scan.
           Regression test GREEN.
