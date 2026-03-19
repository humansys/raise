# Epic Design: E493 — Developer Setup Experience

## Gemba Findings

Codebase walk (2026-03-06) on `v2.1.0`:

| Area | State | Location |
|------|-------|----------|
| Profile model | Mature — Pydantic, load/save, session mgmt | `src/rai_cli/onboarding/profile.py` |
| Profile CLI | Only `show` subcommand | `src/rai_cli/cli/commands/profile.py` |
| Doctor module | Does not exist | — |
| `.env` loading | Not implemented — `python-dotenv` not in deps | `pyproject.toml` |
| Console script | `rai` declared in `[project.scripts]` | `pyproject.toml:55` |
| Welcome skill | Claude skill only, no Python code | `.claude/skills/rai-welcome/` |
| Installation docs | Referenced but not found | `docs/new-machine-setup.md` missing |

## Target Components

### S1 — Installation Guide (docs-only)
- **Output:** `docs/installation.md` with macOS, Linux, WSL sections
- **Touches:** README.md (simplify, link to docs)
- **No code changes**

### S2 — Profile Export/Import
- **New:** `rai profile export [--output PATH]` and `rai profile import PATH`
- **Touches:** `src/rai_cli/cli/commands/profile.py` (add subcommands)
- **New:** `src/rai_cli/onboarding/profile_portability.py` (export/import logic)
- **Contract:** Export produces a YAML bundle with profile + metadata (source machine, timestamp). Import validates, clears machine-local state (active_sessions, current_session), adjusts paths.

### S3 — Welcome Returning Developer
- **Touches:** `/rai-welcome` skill (already exists in `.claude/skills/`)
- **Logic:** If `~/.rai/developer.yaml` missing but repo has `PAT-{prefix}-*` patterns, offer identity reclaim
- **Skill-only change** — no new Python code needed

### S4 — Doctor New Machine
- **New:** `src/rai_cli/diagnostics/doctor.py` — check categories: tools, profile, env vars, MCP, Claude memory
- **New:** `src/rai_cli/cli/commands/doctor.py` — `rai doctor` with `--new-machine` flag
- **Pattern:** Each check returns `CheckResult(name, status, message, fix_hint)`. Doctor aggregates and presents.

### S5 — CLI .env Loading
- **Add dep:** `python-dotenv` to `pyproject.toml`
- **Touches:** CLI entrypoint (`src/rai_cli/cli/main.py`) — load `.env` from CWD at startup
- **Scope:** Only project-root `.env`, no recursive search

### S6 — Pipx Install Fix
- **Investigation:** Verify if `rai` console_script already works with plain `pipx install .`
- **If broken:** Fix is in package metadata — ensure `rai-cli` declares deps correctly so pipx resolves them
- **May be already fixed** — `[project.scripts] rai = ...` is declared

## Key Contracts

### Profile Bundle Format (S2)
```yaml
_meta:
  version: 1
  exported_at: "2026-03-06T21:00:00Z"
  source_machine: "hostname"
profile:
  # Full DeveloperProfile minus machine-local fields
  name: "Emilio"
  experience_level: "ha"
  communication: { ... }
  # active_sessions: EXCLUDED
  # current_session: EXCLUDED
```

### Doctor Check Result (S4)
```python
class CheckResult(BaseModel):
    name: str           # e.g., "python-version"
    status: Literal["ok", "warn", "fail"]
    message: str        # Human-readable description
    fix_hint: str | None  # Actionable fix suggestion
```

## Dependencies (acyclic)

```
S1 (docs) ─────────────────> S4 (doctor references install docs)
S2 (profile export/import) ─> S3 (welcome uses profile detection)
S5 (.env loading) ──────────> independent
S6 (pipx fix) ─────────────> independent
```

Critical path: S2 -> S3 (welcome needs profile portability concepts)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| S6 already fixed (wasted story) | Medium | Low | Investigate first, close as N/A if fixed |
| Doctor scope creep (too many checks) | Medium | Medium | Cap at 8 checks matching the 8 friction points |
| Cross-platform path differences | Low | Medium | Use `pathlib` consistently, test on macOS + Linux |

## Decisions

No formal ADRs needed — all changes follow established patterns (Typer CLI, Pydantic models, YAML config).

**Implicit decisions:**
- Profile bundle is YAML (consistent with existing `developer.yaml`)
- Doctor is a new module, not bolted onto existing commands
- `.env` loading at CLI entrypoint, not per-command
