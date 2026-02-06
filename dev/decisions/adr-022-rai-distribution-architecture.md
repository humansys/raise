# YesADR-022: Rai Distribution Architecture

**Status:** Accepted
**Date:** 2026-02-05
**Deciders:** Emilio, Rai
**Informs:** E14 Rai Distribution

---

## Context

E14 needs to distribute "Base Rai" — identity, methodology knowledge, and universal patterns — to users who install raise-cli.

### Requirements

1. **F&F:** Assets versioned with CLI, offline-capable, simple
2. **V3 Corporate:** Organizations can maintain their own "Corporate Rai" with custom methodology
3. **Updates:** Base Rai updates should flow naturally (CLI upgrade for public, git pull for corporate)
4. **Format:** V3-ready (portable, syncable)

### The Corporate Scenario

Enterprises adopting RaiSE will want:

- Custom methodology (different gates, custom skills)
- Corporate patterns (company coding standards)
- Internal distribution (not dependent on public PyPI)
- Independent update cycle (don't wait for public releases)

This rules out tightly coupling base Rai content to the CLI package.

---

## Decision

**Pluggable Base Rai with Git-based Corporate Override**

### Architecture

```
PUBLIC (raise-commons repo):
├── src/raise_cli/           # CLI code
└── src/raise_cli/rai_base/  # Default public base Rai (bundled)
    ├── identity/
    │   ├── core.md
    │   └── perspective.md
    ├── memory/
    │   └── patterns-base.jsonl
    └── framework/
        └── methodology.yaml

CORPORATE (any git repo, e.g., gitlab.acme.com/rai/rai-base-acme):
└── (same structure as above, corporate content)

USER CONFIG:
~/.rai/config.yaml
  base_source: <git-url>     # Optional, overrides bundled
```

### Resolution Order

```python
def resolve_base_source() -> Path | str:
    """Determine where to load base Rai from."""

    # 1. Project override (.rai/manifest.yaml)
    if project_manifest.base_source:
        return project_manifest.base_source

    # 2. User config (~/.rai/config.yaml)
    if user_config.base_source:
        return user_config.base_source

    # 3. Default: bundled in package
    return importlib.resources.files("raise_cli.rai_base")
```

### Commands

```bash
# F&F: Use bundled public base (default)
raise init

# Corporate: Configure base source (once per user)
raise config set base_source https://gitlab.acme.com/rai/rai-base-acme.git

# Update base from configured source
raise base update
# If git URL: clone or pull latest
# If bundled: check for CLI update, prompt if available

# Check current base
raise base show
# Source: bundled (raise-cli 2.1.0)
# -- or --
# Source: https://gitlab.acme.com/rai/rai-base-acme.git (v1.3.0)
```

### Bootstrap Flow

```
raise init
    │
    ├── Resolve base source (config → bundled)
    │
    ├── If git URL:
    │   └── Clone to ~/.rai/cache/base/{hash}/
    │
    ├── Copy base assets to project
    │   .rai/identity/     ← from base
    │   .rai/memory/patterns.jsonl ← from base (marked base: true)
    │
    └── Generate MEMORY.md from methodology.yaml
```

### Update Flow

```
raise base update
    │
    ├── Resolve base source
    │
    ├── If git URL:
    │   ├── git pull in cache
    │   └── Prompt: "Base Rai updated. Apply to current project? [Y/n]"
    │
    ├── If bundled:
    │   ├── Check PyPI for raise-cli update
    │   └── Prompt: "New CLI version available (includes base Rai update). Upgrade? [Y/n]"
    │
    └── If applied:
        ├── Update .rai/identity/ (overwrite, it's base content)
        ├── Merge base patterns (add new, update existing base:true, preserve personal)
        └── Regenerate MEMORY.md
```

---

## Consequences

### Positive

- **F&F stays simple:** Bundled by default, no config needed
- **Corporate ready:** Git repo override, no private PyPI needed
- **Natural updates:** Git pull for corporate, pip upgrade for public
- **Access control:** Leverages existing git permissions
- **Content-only repos:** Corporate base is just files (md, jsonl, yaml), not Python

### Negative

- **Two update paths:** Git for corporate, pip for public (manageable)
- **Cache management:** Need to handle ~/.rai/cache/ for git sources

### Neutral

- **Base Rai format identical** whether bundled or from git
- **Project .rai/ is source-agnostic** — doesn't know where base came from

---

## Implementation Phases

### F&F (E14)

1. Bundle base Rai in `src/raise_cli/rai_base/`
2. `raise init` copies from bundled source
3. `raise base show` displays current base info
4. No git source support yet (config ignored)

### Post-F&F

1. Add `~/.rai/config.yaml` support
2. Implement git source resolution
3. Add `raise base update` command
4. Add `raise config set base_source` command

### V3

1. Document corporate base Rai creation
2. Support branch/tag pinning for git sources
3. Team-level base source override (.rai/manifest.yaml)

---

## Base Rai Content Structure

```yaml
# Required structure for any base Rai source (public or corporate)

identity/
  core.md           # Name, values, boundaries, essence
  perspective.md    # How Rai approaches collaboration

memory/
  patterns-base.jsonl   # Universal methodology patterns
                        # Each pattern: {id, content, context, base: true, version: N}

framework/
  methodology.yaml      # Skills list, gates, process rules
                        # Used to generate MEMORY.md
```

### methodology.yaml Schema

```yaml
version: 1

skills:
  session:
    - name: /session-start
      purpose: Begin session with context loading
      when: Start of any working session
    - name: /session-close
      purpose: Capture learnings, prepare for next session
      when: End of significant sessions

  epic:
    - name: /epic-start
      purpose: Create epic branch and scope commit
      when: Starting new epic
    # ... etc

gates:
  blocking:
    - before: epic design
      require: Epic branch exists (/epic-start)
    - before: feature work
      require: Feature branch and scope commit (/feature-start)
    - before: implementation
      require: Plan exists
    - before: commit
      require: Tests pass
    - before: epic merge
      require: Retrospective done (/epic-close)

principles:
  - name: TDD Always
    rule: RED-GREEN-REFACTOR, no exceptions
  - name: Commit After Task
    rule: Each completed task gets a commit
  - name: Ask Before Subagents
    rule: Inference economy — confirm before expensive operations
```

---

## Corporate Base Rai Example

```
# gitlab.acme.com/rai/rai-base-acme

identity/
  core.md           # "I am Acme Rai, your engineering partner..."
  perspective.md    # Acme-specific collaboration approach

memory/
  patterns-base.jsonl
    # Acme patterns:
    # - "All PRs require two approvals"
    # - "Use internal component library for UI"
    # - "Follow Acme API naming conventions"

framework/
  methodology.yaml
    # Acme skills (may include custom ones)
    # Acme gates (may be stricter)
    # Acme principles
```

---

## References

- E14 Scope: `dev/epic-e14-scope.md`
- Research: `work/research/rai-distribution/`
- ADR-013: Rai as Entity
- ADR-014: Identity Core Structure
- ADR-016: Memory Format (JSONL + Graph)
