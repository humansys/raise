# ISSUE-005: DX Audit Findings — Pre-F&F Quality Review

> **Status:** COMPLETE
> **Priority:** HIGH (F&F quality gate)
> **Created:** 2026-02-05
> **Updated:** 2026-02-05
> **Scope:** Skills, CLI, Schemas, New User Experience, Code Quality
>
> **Resolved:** All items complete including post-launch cleanup
> - F&F + Feb 15: #1, #2, #4, #5, #6, #8, #10 ✅
> - Post-launch: #3, #7, #9 ✅ (graph consolidated -2510 lines, skill extracted -54 lines)

---

## Executive Summary

Comprehensive DX audit of raise-cli revealed **5 critical issues** and **10+ high-priority improvements** needed before F&F release. The most impactful finding: **new users hit a wall after `rai init`** — they're told to run `/session-start` but don't know that's a Claude Code skill, not a CLI command.

---

## Critical Issues (Block F&F Quality)

### 1. CLI → Claude Code Skills Gap ✅ RESOLVED

**Severity:** CRITICAL
**Impact:** All new users
**Resolution:** Updated Ri output to use "Editor:" vs "CLI:" labels with download link (commit 9daac97)

**Problem:**
- User runs `rai init`
- Output says "Run /session-start when ready"
- User tries `rai session-start` → command not found
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

**Fix:** Update `rai init` output to clearly distinguish CLI vs Claude Code:
```
Next steps:
  CLI commands:     raise --help (in terminal)
  Claude Code:      /session-start (in Claude Code editor)

Don't have Claude Code? Visit: https://claude.ai/claude-code
```

---

### 2. `rai context query` Is Two Commands ✅ RESOLVED

**Severity:** CRITICAL
**Impact:** Usability, discoverability
**Resolution:** Simplified to ONE command querying ONE graph:
- `rai context query` — queries unified graph (all context in one place)
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

### 5. Governance vs Context Query Duplication ✅ RESOLVED

**Severity:** HIGH
**Impact:** Maintenance, API confusion
**Resolution:** Deleted governance/query module as dead code (commit 5f26b24). The unified query in context/query.py is the only query system now. Removed 2,689 lines and 112 tests.

**Problem:** Two query systems with 85% overlap — governance/query operated on the old ConceptGraph while context/query operates on UnifiedGraph. Since ADR-019 unified everything, governance/query was dead code.

---

## High Priority Issues

### 6. No Post-Init Guidance ✅ RESOLVED

**Problem:** After `rai init`, user sees brief "Next steps" but:
- No explanation of what `/session-start` does
- No explanation of what was created
- No "first 5 minutes" guide

**Resolution:** Updated Shu output (commit a59a8a4):
- Files now show purpose: "manifest.yaml — project metadata", "developer.yaml — your preferences"
- /session-start explains: "Loads your context, remembers patterns, proposes focused work"
- Numbered steps with clear action items
- "First 5 minutes guide" and `rai help` command deferred (YAGNI for F&F)

---

### 7. Telemetry Boilerplate in 7 Skills

**Problem:** Step 0 (telemetry emit) and Step 0.5 (context query) duplicated in:
- epic-design, epic-plan, story-design, story-plan
- story-implement, story-review, research

~30-50 lines × 7 skills = 210-350 lines of duplication

**Fix:** Create shared `_setup-steps.md` template, skills reference it.

---

### 8. ID Sanitization Duplicated ✅ RESOLVED

**Resolution:** Already extracted to `core/text.py` as `sanitize_id()`. Both parsers import from there. Issue was stale when written.

---

### 9. Graph Methods Duplicated 3×

**Problem:** Same methods in 3 classes:
- `ConceptGraph.get_node()`, `get_outgoing_edges()`, `get_incoming_edges()`
- `UnifiedGraph` same methods
- `MemoryGraph` same methods (deprecated)

~80 lines duplicated.

**Fix:** Create base class or mixin for graph operations.

---

### 10. Inconsistent Command Naming ✅ RESOLVED

**Resolution:** Standardized command naming (commit 6cb2eb8):
- `rai profile session` → `rai profile session-start` (matches session-end)
- `rai telemetry emit` → `rai telemetry emit-work` (matches emit-session, emit-calibration)
- `rai memory dump` was already `rai memory list` (stale info)

Updated 10 skills to use new command names.

---

## Medium Priority Issues

### 11. Convention Schema Over-Engineered — NOT AN ISSUE

**Analysis:** Each convention type has distinct fields (style vs pattern vs max_length). The shared fields (confidence, sample_count) provide consistent structure but the models are NOT identical. Collapsing them would lose type safety. Current design is appropriate.

---

### 12. XDG Path Helpers Repeated ✅ RESOLVED

**Resolution:** Already extracted — `_get_xdg_dir()` helper exists at line 117-129. Issue was stale when written.

---

### 13. Skill Section Names Inconsistent ✅ RESOLVED

**Resolution:** Standardized session-start and session-close to match the majority pattern (commit c4d91ec):
- "When to Use" → "Purpose" + "Context"
- "Shu/Ha/Ri Adaptation" → "Mastery Levels (ShuHaRi)"

All 19 skills now follow: Purpose → Mastery Levels → Context → Steps → Output.

---

### 14. Output Format Names Inconsistent ✅ RESOLVED

**Resolution:** Standardized on `human`, `json`, `table` (commit 7afce95). Changed context.py and memory.py from "markdown" to "human".

---

### 15. Generic `metadata: dict` Escape Hatches — NOT AN ISSUE

**Analysis:** The metadata fields are actually used extensively for domain-specific data (requirement_id, epic_id, needs_context, learned_from, etc.). They're legitimate extension points, not escape hatches. 20+ usages found across parsers, graph building, and CLI output.

---

## Recommendations by Phase

### Before F&F (Feb 9) — Must Fix ✅ ALL RESOLVED

| Issue | Effort | Impact | Status |
|-------|--------|--------|--------|
| #1 CLI→Skills gap (init output) | 1h | Critical | ✅ Done |
| #6 Post-init guidance | 2h | High | ✅ Done |
| #4 Deprecation cleanup (decision) | 1h | High | ✅ Done (was already removed) |

### Before Public Launch (Feb 15) — Should Fix ✅ ALL RESOLVED

| Issue | Effort | Impact | Status |
|-------|--------|--------|--------|
| #2 Split context query command | 3h | Critical | ✅ Done |
| #5 Consolidate query schemas | 2h | High | ✅ Done (dead code removed) |
| #10 Command naming consistency | 2h | Medium | ✅ Done |
| #8 ID sanitization extraction | 30m | Low | ✅ Done (was already extracted) |

### Post-Launch — Nice to Have

| Issue | Effort | Impact | Status |
|-------|--------|--------|--------|
| #3 Skill bloat refactor | 4h | Medium | ✅ Partial — extracted 54 lines from epic-plan |
| #7 Skill boilerplate extraction | 2h | Medium | ✅ Skipped — boilerplate is actually customization |
| #9 Graph base class | 2h | Medium | ✅ Done — consolidated to UnifiedGraph (-2510 lines)
| #11 Convention schema | - | - | ✅ Not an issue (models are distinct) |
| #12 XDG path helpers | - | - | ✅ Already extracted |
| #13 Skill section names | 1h | Low | ✅ Done |
| #14 Output format names | - | - | ✅ Done |
| #15 Metadata dict fields | - | - | ✅ Not an issue (legitimately used) |

---

## Quick Wins (< 1 hour each)

1. **Delete duplicate `/epic-close/skill.md`** — Old version, confusing
2. **Fix session skill headers** — "When to Use" → "Purpose"
3. **Add JSON output to telemetry commands** — Scriptability
4. **Update `rai init` output** — Explain CLI vs Skills
5. **Rename `rai memory dump`** → `rai memory list`

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
