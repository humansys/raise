# ISSUE-005: DX Audit Findings — Pre-F&F Quality Review

> **Status:** Partially Resolved
> **Priority:** HIGH (F&F quality gate)
> **Created:** 2026-02-05
> **Updated:** 2026-02-05
> **Scope:** Skills, CLI, Schemas, New User Experience, Code Quality
>
> **Resolved:** #1 (init output), #2 (context command split), #4 (MemoryGraph removed), #6 (post-init guidance)

---

## Executive Summary

Comprehensive DX audit of raise-cli revealed **5 critical issues** and **10+ high-priority improvements** needed before F&F release. The most impactful finding: **new users hit a wall after `raise init`** — they're told to run `/session-start` but don't know that's a Claude Code skill, not a CLI command.

---

## Critical Issues (Block F&F Quality)

### 1. CLI → Claude Code Skills Gap ✅ RESOLVED

**Severity:** CRITICAL
**Impact:** All new users
**Resolution:** Updated Ri output to use "Editor:" vs "CLI:" labels with download link (commit 9daac97)

**Problem:**
- User runs `raise init`
- Output says "Run /session-start when ready"
- User tries `raise session-start` → command not found
- User doesn't know `/session-start` is a Claude Code skill

**Evidence:**
```
Next steps:
1. Open Claude Code in this directory
2. Run /session-start to begin our first session together
```

But nothing explains:
- That `/session-start` is NOT a CLI command
- What Claude Code is
- How to access skills

**Fix:** Update `raise init` output to clearly distinguish CLI vs Claude Code:
```
Next steps:
  CLI commands:     raise --help (in terminal)
  Claude Code:      /session-start (in Claude Code editor)

Don't have Claude Code? Visit: https://claude.ai/claude-code
```

---

### 2. `raise context query` Is Two Commands ✅ RESOLVED

**Severity:** CRITICAL
**Impact:** Usability, discoverability
**Resolution:** Simplified to ONE command querying ONE graph:
- `raise context query` — queries unified graph (all context in one place)
- Removed governance-only query (unified includes everything)
- Options: `--types`, `--limit`, `--strategy`, `--format`, `--output`

One graph, one command. Updated 10 skills and all references.

---

### 3. Skill Bloat (Epic Skills)

**Severity:** HIGH
**Impact:** New contributor overwhelm, maintenance burden

**Problem:**
| Skill | Lines | Steps |
|-------|-------|-------|
| epic-plan | 736 | 14 |
| epic-design | 601 | 15 |
| epic-start | 205 | 6 |

Epic-plan includes 50+ lines of "Sequencing Strategies Deep Dive" — reference material, not executable steps.

**Fix:**
- Extract reference sections to separate files
- Keep core skills under 400 lines
- Create `_references/` directory in skills

---

### 4. Deprecated MemoryGraph Still Active ✅ RESOLVED

**Severity:** HIGH
**Impact:** Code quality, confusion
**Resolution:** MemoryGraph fully removed in commit 299d982. Deleted: cache.py, builder.py, query.py and their tests. Only remaining "deprecated" is CLI `--memory-dir` option (backward compat, appropriate to keep).

---

### 5. Governance vs Context Query Duplication

**Severity:** HIGH
**Impact:** Maintenance, API confusion

**Problem:** Two query systems:
- `governance/query/models.py` → ContextQuery, ContextResult
- `context/query.py` → UnifiedQuery, UnifiedQueryResult

Both define similar Query + Metadata + Result patterns with 85% overlap.

**Fix:** Consolidate to single query interface before public launch.

---

## High Priority Issues

### 6. No Post-Init Guidance ✅ RESOLVED

**Problem:** After `raise init`, user sees brief "Next steps" but:
- No explanation of what `/session-start` does
- No explanation of what was created
- No "first 5 minutes" guide

**Resolution:** Updated Shu output (commit a59a8a4):
- Files now show purpose: "manifest.yaml — project metadata", "developer.yaml — your preferences"
- /session-start explains: "Loads your context, remembers patterns, proposes focused work"
- Numbered steps with clear action items
- "First 5 minutes guide" and `raise help` command deferred (YAGNI for F&F)

---

### 7. Telemetry Boilerplate in 7 Skills

**Problem:** Step 0 (telemetry emit) and Step 0.5 (context query) duplicated in:
- epic-design, epic-plan, feature-design, feature-plan
- feature-implement, feature-review, research

~30-50 lines × 7 skills = 210-350 lines of duplication

**Fix:** Create shared `_setup-steps.md` template, skills reference it.

---

### 8. ID Sanitization Duplicated

**Files:**
- `governance/parsers/vision.py:14-40` (_sanitize_id)
- `governance/parsers/constitution.py:14-40` (_sanitize_principle_id)

Identical 26-line functions.

**Fix:** Extract to `core/text.py` shared utility.

---

### 9. Graph Methods Duplicated 3×

**Problem:** Same methods in 3 classes:
- `ConceptGraph.get_node()`, `get_outgoing_edges()`, `get_incoming_edges()`
- `UnifiedGraph` same methods
- `MemoryGraph` same methods (deprecated)

~80 lines duplicated.

**Fix:** Create base class or mixin for graph operations.

---

### 10. Inconsistent Command Naming

| Command | Issue |
|---------|-------|
| `raise profile session` | Starts session, but no `session-start` |
| `raise profile session-end` | Inconsistent with `session` |
| `raise telemetry emit` | Bare, while others are `emit-session`, `emit-calibration` |
| `raise memory dump` | "dump" sounds raw; should be `list` or `export` |

**Fix:** Standardize naming:
- `raise profile session-start` / `session-end`
- `raise telemetry emit-work` (not bare `emit`)
- `raise memory list` (not `dump`)

---

## Medium Priority Issues

### 11. Convention Schema Over-Engineered

**File:** `onboarding/conventions.py`

8 Pydantic models for style detection where 3-4 would suffice. Each convention type (indentation, quote, line_length, naming) has identical fields.

**Fix:** Flatten to single `Convention` model with `type` discriminator.

---

### 12. XDG Path Helpers Repeated

**File:** `config/paths.py:13-64`

Three nearly identical functions for config/cache/data directories.

**Fix:** Extract parameterized `_get_xdg_dir(var_name, fallback)` helper.

---

### 13. Skill Section Names Inconsistent

| Pattern | Skills Using |
|---------|--------------|
| "## Purpose" | 17 skills |
| "## When to Use" | session-start, session-close |
| "## Integration with Memory Model" | epic-design, epic-plan |
| "## Relationship to Other Skills" | Some skills |
| (No integration section) | feature-design, feature-plan |

**Fix:** Enforce standard template with consistent sections.

---

### 14. Output Format Names Inconsistent

| Command | Formats |
|---------|---------|
| discover scan | human, json, summary |
| memory dump | table, json, markdown |
| context query | markdown, json |
| graph extract | human, json |

"markdown" vs "human" inconsistency.

**Fix:** Standardize on `human`, `json`, `table` everywhere.

---

### 15. Generic `metadata: dict` Escape Hatches

7 models have `metadata: dict[str, Any]` with <8 actual usages. YAGNI violation.

**Fix:** Remove or convert to specific typed fields when actually used.

---

## Recommendations by Phase

### Before F&F (Feb 9) — Must Fix ✅ ALL RESOLVED

| Issue | Effort | Impact | Status |
|-------|--------|--------|--------|
| #1 CLI→Skills gap (init output) | 1h | Critical | ✅ Done |
| #6 Post-init guidance | 2h | High | ✅ Done |
| #4 Deprecation cleanup (decision) | 1h | High | ✅ Done (was already removed) |

### Before Public Launch (Feb 15) — Should Fix

| Issue | Effort | Impact | Status |
|-------|--------|--------|--------|
| #2 Split context query command | 3h | Critical | ✅ Done |
| #5 Consolidate query schemas | 2h | High | Pending |
| #10 Command naming consistency | 2h | Medium | Pending |
| #8 ID sanitization extraction | 30m | Low | Pending |

### Post-Launch — Nice to Have

| Issue | Effort | Impact |
|-------|--------|--------|
| #3 Skill bloat refactor | 4h | Medium |
| #7 Skill boilerplate extraction | 2h | Medium |
| #9 Graph base class | 2h | Medium |
| #11-15 Polish items | 4h total | Low |

---

## Quick Wins (< 1 hour each)

1. **Delete duplicate `/epic-close/skill.md`** — Old version, confusing
2. **Fix session skill headers** — "When to Use" → "Purpose"
3. **Add JSON output to telemetry commands** — Scriptability
4. **Update `raise init` output** — Explain CLI vs Skills
5. **Rename `raise memory dump`** → `raise memory list`

---

## Metrics

| Category | Current | Target |
|----------|---------|--------|
| Pydantic models | 44 | 25-30 |
| Skill average lines | 350 | <300 |
| Duplicated code | ~450 lines | <100 lines |
| Commands with >6 options | 2 | 0 |
| Deprecated but active code | 5 classes | 0 |

---

## Related Issues

- ISSUE-003: Directory Structure Ontology
- ISSUE-004: Epic/Feature Tree Structure
- E14: Rai Distribution (affected by these findings)

---

*Created: 2026-02-05*
*Based on: 5 parallel DX audits (skills, CLI, schemas, new user, DRY)*
