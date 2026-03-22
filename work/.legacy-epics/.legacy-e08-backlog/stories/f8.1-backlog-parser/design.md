# Feature Design: F8.1 Backlog Parser

```yaml
id: F8.1
name: Backlog Parser
epic: E8 Work Tracking Graph
size: S
sp: 2
status: designing
created: 2026-02-02
```

---

## What & Why

**Problem:** Work tracking (projects, epics) is not part of the queryable governance graph. Rai can't answer "what's the current epic?" because backlog data isn't extracted as concepts.

**Value:** Extract Project and Epic concepts from `backlog.md` files, enabling graph queries like `rai context query "current work"`.

---

## Approach

Parse `governance/projects/*/backlog.md` files to extract:
1. **Project concept** — from filename and frontmatter
2. **Epic concepts** — from "Epics Overview" table (index only, not full details)
3. **Current focus** — from "F&F Scope" line or explicit section

**Pattern:** Follow `prd.py` parser pattern — regex for tables, line-by-line parsing.

**Components affected:**
- `src/rai_cli/governance/parsers/backlog.py` — **CREATE**
- `src/rai_cli/governance/models.py` — **MODIFY** (add ConceptType.PROJECT, ConceptType.EPIC)
- `src/rai_cli/governance/parsers/__init__.py` — **MODIFY** (export new parser)

---

## Examples

### API Usage

```python
from pathlib import Path
from raise_cli.governance.parsers.backlog import extract_project, extract_epics

# Extract project from backlog
backlog_path = Path("governance/projects/raise-cli/backlog.md")
project = extract_project(backlog_path)

# Project concept
assert project.id == "project-raise-cli"
assert project.type == ConceptType.PROJECT
assert project.metadata["name"] == "raise-cli"
assert project.metadata["current_epic"] == "E8"
assert project.metadata["target_date"] == "2026-02-09"

# Extract epic index from same file
epics = extract_epics(backlog_path)

# Epic concepts (index only)
assert len(epics) == 9  # E1-E9
assert epics[0].id == "epic-e1"
assert epics[0].type == ConceptType.EPIC
assert epics[0].metadata["epic_id"] == "E1"
assert epics[0].metadata["name"] == "Core Foundation"
assert epics[0].metadata["status"] == "complete"
assert epics[0].metadata["scope_doc"] == "dev/epic-e1-scope.md"
```

### Input Format (backlog.md)

```markdown
# Backlog: raise-cli

> **Status**: Active
> **Date**: 2026-02-02

## 1. Epics Overview

| ID | Epic | Status | Scope Doc | Priority |
|----|------|--------|-----------|----------|
| E1 | **Core Foundation** | ✅ Complete | `dev/epic-e1-scope.md` | — |
| E8 | **Work Tracking Graph** | 📋 DRAFT | `dev/epic-e8-scope.md` | **P0 (next)** |

**F&F Scope (Feb 9):** E8 → E7 → E9
```

### Output Concepts

**Project:**
```python
Concept(
    id="project-raise-cli",
    type=ConceptType.PROJECT,
    file="governance/projects/raise-cli/backlog.md",
    section="Backlog: raise-cli",
    lines=(1, 6),
    content="Project backlog for raise-cli...",
    metadata={
        "name": "raise-cli",
        "status": "active",
        "current_epic": "E8",
        "target_date": "2026-02-09",
        "epic_count": 9
    }
)
```

**Epic (from index):**
```python
Concept(
    id="epic-e8",
    type=ConceptType.EPIC,
    file="governance/projects/raise-cli/backlog.md",
    section="E8: Work Tracking Graph",
    lines=(21, 21),  # Single table row
    content="Work Tracking Graph - DRAFT",
    metadata={
        "epic_id": "E8",
        "name": "Work Tracking Graph",
        "status": "draft",
        "scope_doc": "dev/epic-e8-scope.md",
        "priority": "P0",
        "project_id": "raise-cli"  # For relationship inference
    }
)
```

### Status Normalization

| Raw Status | Normalized |
|------------|------------|
| `✅ Complete` | `complete` |
| `📋 DRAFT` | `draft` |
| `Deferred` | `deferred` |
| `→ Replaced by X` | `deferred` |
| `✅ Via Skills` | `complete` |
| Other / blank | `pending` |

---

## Acceptance Criteria

**MUST:**
- [ ] `extract_project()` returns Project concept from backlog.md
- [ ] `extract_epics()` returns list of Epic concepts from table
- [ ] Project metadata includes `current_epic` from "F&F Scope" line
- [ ] Epic status normalized to WorkStatus enum values
- [ ] Tests cover raise-cli backlog.md (existing file)
- [ ] >90% coverage on new parser code

**SHOULD:**
- [ ] Lenient parsing — missing fields use defaults, don't fail
- [ ] Warning logged for unparseable rows (not error)
- [ ] Handle multiple projects (glob `governance/projects/*/backlog.md`)

**MUST NOT:**
- [ ] Parse epic scope docs (that's F8.2)
- [ ] Create relationships (that's F8.3)
- [ ] Fail on malformed backlog — return partial results

---

## Implementation Notes

**Regex patterns:**

```python
# Project name from H1
PROJECT_PATTERN = r"^# Backlog:\s*(.+)$"

# Epic table row: | E1 | **Name** | Status | `scope.md` | Priority |
EPIC_ROW_PATTERN = r"^\|\s*(E\d+)\s*\|\s*\*?\*?([^|*]+)\*?\*?\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|"

# Current focus: **F&F Scope (Feb 9):** E8 → E7 → E9
CURRENT_FOCUS_PATTERN = r"\*\*F&F Scope[^:]*:\*\*\s*(E\d+)"

# Or explicit: Epic: E8
EXPLICIT_FOCUS_PATTERN = r"^Epic:\s*(E\d+)"
```

**Status normalization:**

```python
def normalize_status(raw: str) -> str:
    """Normalize epic status to WorkStatus values."""
    raw_lower = raw.lower().strip()
    if "complete" in raw_lower or "✅" in raw:
        return "complete"
    if "draft" in raw_lower or "📋" in raw:
        return "draft"
    if "deferred" in raw_lower or "replaced" in raw_lower:
        return "deferred"
    if "progress" in raw_lower:
        return "in_progress"
    return "pending"
```

---

*Design created: 2026-02-02*
*Next: /story-plan*
