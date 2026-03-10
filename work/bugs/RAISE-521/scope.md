# RAISE-521 — Scope

WHAT:      add_gitignore_personal() returns True on every code path, including
           when the file write operation fails with OSError. run_fixes() trusts
           this return value to report success/failure to the user.

WHEN:      Any call to `rai doctor --fix` that triggers the "add-gitignore-personal"
           fix on a read-only filesystem or when a permissions error occurs.

WHERE:     src/raise_cli/doctor/fix.py:49 — add_gitignore_personal()
           Lines 63-65: write always returns True regardless of outcome.

EXPECTED:  Function returns False when the file write fails, so run_fixes()
           correctly reports the fix as failed.

Done when: OSError on write causes False return. All other paths still return True.
           SonarCloud BLOCKER AZy-yCoI4PF7cDTLpgfn resolves on next scan.
