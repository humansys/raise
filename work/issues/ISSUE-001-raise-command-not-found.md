# ISSUE-001: `raise` command not found in non-interactive shells

> Parked: 2026-02-05
> Priority: P2 (workaround exists)
> Status: PARKED

---

## Problem

The `raise` command is not available in Claude Code's bash environment, requiring `uv run raise` instead.

**Expected:** `raise profile show` works
**Actual:** `bash: raise: command not found`

## Evidence

### Environment Analysis (2026-02-05)

1. **Interactive shell:** `raise` works (PATH includes `~/.local/bin`)
2. **Non-interactive shell (Claude Code):** `raise` not found
3. **BASH_ENV not set** in Claude Code's environment

### Root Cause (Ishikawa, SES-048)

```
                    Environment
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   Claude Code    Non-interactive   BASH_ENV
   spawns bash    shells skip       not set
   non-interactive  .bashrc          │
        │               │               │
        └───────────────┴───────────────┘
                        │
                        ▼
              PATH not configured
                        │
                        ▼
              `raise` not found
```

**Root cause:** Claude Code spawns non-interactive bash. Non-interactive bash only reads `BASH_ENV`, not `.bashrc`. Without `BASH_ENV` pointing to a file that sets PATH, the `~/.local/bin` directory isn't in PATH.

### Attempted Fixes

| Fix | Result | Why Failed |
|-----|--------|------------|
| Add to `.bashrc` | Works in terminal, not in Claude | Non-interactive shell skips `.bashrc` |
| Add to `.profile` | Works for login shells only | Claude spawns non-login non-interactive |
| Set `BASH_ENV` in `.bashrc` | Circular | `.bashrc` not read in non-interactive |
| Set `BASH_ENV` in `.profile` | Partial | Only works if login shell sourced first |

### Working Configuration (Needs Verification)

From PAT-102/103/104 session:

```bash
# ~/.profile (for login shells)
export BASH_ENV="$HOME/.bash_env"

# ~/.bash_env (sourced by BASH_ENV)
export PATH="$HOME/.local/bin:$PATH"
```

**But:** This requires the login shell to have been sourced first to set `BASH_ENV` in the environment.

## Current Workaround

Use `uv run raise` instead of `raise` in Claude Code sessions.

## What Needs Investigation

1. **How does Claude Code spawn bash?** — What environment variables are inherited?
2. **Can we configure Claude Code's environment?** — Is there a `.claude/env` or similar?
3. **direnv as solution?** — Does `.envrc` get sourced in non-interactive shells?
4. **System-wide BASH_ENV?** — Can we set it in `/etc/environment` or similar?

## Related Patterns

- PAT-102: Structural vs patch fixes (fix the system, not symptoms)
- PAT-103: BASH_ENV for non-interactive shells
- PAT-104: Environment inheritance chain

## Sessions

- SES-048 (2026-02-05): Ishikawa analysis, BASH_ENV identified
- SES-049 (2026-02-05): Attempted fix, still not working

---

*Created: 2026-02-05*
