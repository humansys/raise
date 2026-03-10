# RAISE-520 Scope — Path injection via --memory-dir flag

WHAT:      `--memory-dir` CLI flag in pattern commands accepts arbitrary paths without
           sanitization, allowing path traversal via `../` sequences.

WHEN:      Any call to `rai pattern add|reinforce|sync` with a crafted `--memory-dir` value.
           Example: `rai pattern add "x" --memory-dir ../../../../tmp/evil/`

WHERE:     `src/raise_cli/cli/commands/pattern.py` — lines 110, 211, 282
           (three commands: reinforce, add, sync)

EXPECTED:  Paths supplied via `--memory-dir` should be canonicalized before use,
           eliminating `../` traversal components.

Done when: `.resolve()` applied to all `memory_dir` values before file operations.
           SonarQube finding closed. All gates pass.
