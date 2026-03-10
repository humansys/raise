# Consistency Audit: Framework v2.5

> Pre-release audit to ensure all artifacts are aligned

**Date:** 2026-01-30
**Auditor:** Claude Opus 4.5
**Target Version:** 2.5.0
**Status:** ⚠️ ISSUES FOUND

---

## Executive Summary

| Category | Status | Issues |
|----------|--------|--------|
| Path References | ❌ FAIL | 30+ stale references |
| Terminology | ✅ PASS | Only in meta-katas (correct) |
| Cross-References | ⚠️ WARN | Need validation after fixes |
| Version Numbers | ⚠️ WARN | Inconsistent versions |
| Structural Integrity | ✅ PASS | Good |

**Total Issues:** ~35 requiring fixes

---

## Detailed Findings

### 1. Path References

#### 1.1 Old `specs/` references (18 found)

**Critical - In .raise/ engine files:**

| File | Line | Issue |
|------|------|-------|
| `.raise/templates/solution/solution_vision.md` | 227,229 | refs `specs/main/`, `specs/raise/adrs/` |
| `.raise/templates/project/project_vision.md` | 7,192-194 | refs `specs/main/*.md` |
| `.raise/gates/gate-discovery.md` | 21 | refs `specs/main/project_requirements.md` |
| `.raise/gates/gate-estimation.md` | 3,35 | refs `specs/main/*.md` |
| `.raise/gates/gate-design.md` | 19 | refs `.raise/specs/` |
| `.raise/katas/story/*.md` | various | refs `specs/{feature}/` |
| `.raise/katas/setup/governance.md` | 390 | refs `specs/main/research/` |
| `.raise/README.md` | 133 | refs `specs/raise/adrs/` |

**In framework/ (glossary):**
| File | Line | Issue |
|------|------|-------|
| `framework/reference/glossary.md` | 406,422 | refs `specs/main/*.md` |

**Resolution:** Update to `governance/` or `work/` paths

---

#### 1.2 Old `framework/context/` references (4 found)

These now need to be `framework/reference/`:

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `.raise/templates/governance/guardrails.md` | 122 | `framework/context/constitution.md` | `framework/reference/constitution.md` |
| `.raise/templates/governance/governance-policy.md` | 119 | `framework/context/constitution.md` | `framework/reference/constitution.md` |
| `.raise/gates/gate-code.md` | 166 | `framework/context/work-cycles.md` | `framework/reference/work-cycles.md` |
| `.raise/katas/setup/governance.md` | 400 | `framework/context/constitution.md` | `framework/reference/constitution.md` |

---

#### 1.3 Old `framework/decisions/` references (8 found)

These now need to be `dev/decisions/framework/`:

| File | Lines |
|------|-------|
| `.raise/templates/governance/governance-policy.md` | 115-117 |
| `.raise/gates/gate-vision.md` | 141 |
| `.raise/katas/project/vision.md` | 183 |
| `.raise/katas/setup/governance.md` | 394-396 |

**Resolution:** Update to `dev/decisions/framework/` paths

---

#### 1.4 Old `.raise/context/` references (in framework/vision.md)

| File | Lines | Issue |
|------|-------|-------|
| `framework/vision.md` | 13-15, 135, 926-930 | refs `.raise/context/*.md` |

**Resolution:** Update to `framework/reference/` paths

---

#### 1.5 Old `docs/framework/` references (in work/)

| Location | Count | Action |
|----------|-------|--------|
| `work/analysis/` | 12 | Historical research - leave as-is or add note |
| `work/research/` | 8 | Historical research - leave as-is or add note |

**Note:** These are in research/analysis artifacts that document historical state. Consider adding deprecation notes rather than updating.

---

#### 1.6 CLAUDE.md references

| Line | Issue |
|------|-------|
| 118 | refs `specs/raise/roadmap.md` |
| 281 | refs `specs/main/` |
| 283 | refs `specs/main/` |

---

### 2. Terminology

✅ **PASS** - Deprecated terms only appear in meta-katas explaining the migration (correct behavior).

---

### 3. Version Numbers

#### framework/vision.md
- Frontmatter: `version: "2.4.0"` → Should be `2.5.0`
- References old changelog versions (OK - historical)

#### framework/reference/*.md
- No frontmatter versions (OK - managed by index.yaml)

#### framework/index.yaml
- constitution.md: `version: 2.0.0` (unchanged - OK)
- Others: `version: 2.5.0` (correct)

---

## Priority Matrix

| Priority | Category | Count | Effort |
|----------|----------|-------|--------|
| P1 | `.raise/` engine files with old paths | 18 | Medium |
| P2 | `framework/context/` → `framework/reference/` | 4 | Low |
| P3 | `framework/decisions/` → `dev/decisions/framework/` | 8 | Low |
| P4 | `framework/vision.md` paths and version | 7 | Low |
| P5 | `CLAUDE.md` paths | 3 | Low |
| P6 | Historical research docs | 20 | Skip or note |

**Recommended approach:** Fix P1-P5 (~40 edits), skip P6 (historical context).

---

## Process Documentation (for skill creation)

### Audit Commands Used

```bash
# 1. Check for old specs/ references
grep -rn "specs/" .raise framework governance --include="*.md" --include="*.yaml" | grep -v DEPRECATED

# 2. Check for old docs/framework/ references
grep -rn "docs/framework" .raise framework governance work dev --include="*.md" --include="*.yaml"

# 3. Check for old .raise/context/ references
grep -rn "\.raise/context/" .raise framework governance work --include="*.md" --include="*.yaml" | grep -v DEPRECATED

# 4. Check for old framework/context/ references (now reference/)
grep -rn "framework/context/" .raise framework governance --include="*.md" --include="*.yaml" | grep -v DEPRECATED

# 5. Check for old framework/decisions/ references (now dev/decisions/framework/)
grep -rn "framework/decisions/" .raise framework governance --include="*.md" --include="*.yaml"

# 6. Check for deprecated terminology
grep -rEn "\\bDoD\\b|Definition of Done" .raise/katas .raise/gates --include="*.md" | grep -v "Validation Gate"

# 7. Check version inconsistencies
grep -rn "version.*2\.[0-4]" framework --include="*.md" --include="*.yaml" | grep -v "schema_version"

# 8. Check CLAUDE.md
grep -n "specs/\|docs/framework\|\.raise/context" CLAUDE.md
```

### Path Migration Map

| Old Path | New Path |
|----------|----------|
| `specs/main/business_case.md` | `governance/solution/business_case.md` |
| `specs/main/solution_vision.md` | `governance/solution/vision.md` |
| `specs/main/project_requirements.md` | `governance/projects/{project}/prd.md` |
| `specs/main/tech_design.md` | `governance/projects/{project}/design.md` |
| `specs/main/project_backlog.md` | `governance/projects/{project}/backlog.md` |
| `specs/{feature}/` | `work/stories/{feature}/` |
| `specs/raise/adrs/` | `dev/decisions/framework/` |
| `.raise/context/*.md` | `framework/reference/*.md` |
| `framework/context/*.md` | `framework/reference/*.md` |
| `framework/decisions/*.md` | `dev/decisions/framework/*.md` |
| `docs/framework/v2.1/model/` | `framework/reference/` |

---

## Checklist for Fixes

### Batch 1: .raise/ templates
- [ ] `.raise/templates/solution/solution_vision.md`
- [ ] `.raise/templates/project/project_vision.md`
- [ ] `.raise/templates/governance/guardrails.md`
- [ ] `.raise/templates/governance/governance-policy.md`

### Batch 2: .raise/ gates
- [ ] `.raise/gates/gate-discovery.md`
- [ ] `.raise/gates/gate-estimation.md`
- [ ] `.raise/gates/gate-design.md`
- [ ] `.raise/gates/gate-code.md`
- [ ] `.raise/gates/gate-vision.md`

### Batch 3: .raise/ katas
- [ ] `.raise/katas/story/implement.md`
- [ ] `.raise/katas/story/plan.md`
- [ ] `.raise/katas/story/review.md`
- [ ] `.raise/katas/project/vision.md`
- [ ] `.raise/katas/setup/governance.md`

### Batch 4: Framework
- [ ] `framework/vision.md`
- [ ] `framework/reference/glossary.md`
- [ ] `.raise/README.md`

### Batch 5: CLAUDE.md
- [ ] `CLAUDE.md`

### Batch 6: Deprecation notices
- [ ] `.raise/context/DEPRECATED.md` - update to reference/

---

*This audit process will be converted to a skill: `dev/skills/consistency-audit.md`*
