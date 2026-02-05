# Feature F7.1: `raise init` Command

> **Status:** In Progress
> **Epic:** E7 Onboarding
> **Size:** M (3 SP)
> **Branch:** `feature/e7/f7-1-raise-init`

---

## Scope

### In Scope

- `raise init` CLI command
- Greenfield vs brownfield project detection (file count heuristic)
- Create `.rai/` project structure (minimal: manifest.yaml)
- Load existing `~/.rai/developer.yaml` or create new one (via F7.8 module)
- Display appropriate welcome message based on experience level
- Output guidance for next steps (Claude Code, /session-start)

### Out of Scope

- Convention detection (F7.2)
- Guardrails generation (F7.3)
- Enhanced CLAUDE.md generation (F7.4)
- Skills bundling (F7.6 — already done)
- Guided first session logic (F7.7)
- `--quick` flag (COULD, not MUST)

### Done Criteria

- [ ] `raise init` runs successfully on greenfield project
- [ ] `raise init` runs successfully on brownfield project
- [ ] Detects and reports greenfield/brownfield status
- [ ] Creates `.rai/manifest.yaml` with project metadata
- [ ] Loads existing developer profile if present
- [ ] Creates new developer profile if first time
- [ ] Adapts output verbosity to experience level (Shu=verbose, Ri=concise)
- [ ] Unit tests (>90% coverage)
- [ ] Integration test on real directory

---

## Design Notes

### Project Detection

```python
# Simple heuristic
files = list(Path(".").rglob("*"))
code_files = [f for f in files if f.suffix in CODE_EXTENSIONS]

if len(code_files) == 0:
    project_type = "greenfield"
elif len(code_files) < 10:
    project_type = "small_brownfield"
else:
    project_type = "brownfield"
```

### .rai/ Structure (Minimal for F7.1)

```
.rai/
└── manifest.yaml    # Project metadata
```

Full structure (conventions, components) added by later features.

### manifest.yaml Schema

```yaml
# .rai/manifest.yaml
version: "1.0"
project:
  name: my-project
  type: brownfield  # greenfield | brownfield
  detected_at: 2026-02-05T10:00:00Z

# Populated by later features
conventions: {}
components: []
```

### CLI Output Examples

**Shu (new user):**
```
Welcome to RaiSE!

I'm Rai — your AI partner for reliable software engineering.

Project detected: Brownfield (47 code files)
Created: .rai/manifest.yaml
Created: ~/.rai/developer.yaml (first time setup)

Next steps:
1. Open Claude Code in this directory
2. Run /session-start to begin our first session together
3. I'll guide you through understanding your project

Questions? Visit https://raise.dev/docs
```

**Ri (experienced):**
```
Brownfield project initialized (47 files).
Created .rai/manifest.yaml

Run /session-start when ready.
```

---

## References

- Epic scope: `dev/epic-e7-scope-v2.md`
- Personal memory module: `src/raise_cli/personal/` (F7.8)
- ADR-021: Brownfield-First Onboarding

---

*Created: 2026-02-05*
