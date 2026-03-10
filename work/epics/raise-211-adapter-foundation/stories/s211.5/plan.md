# Implementation Plan: TierContext

## Overview
- **Story:** S211.5
- **Size:** S
- **Tasks:** 3
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-22

## Tasks

### Task 1: TierConfig in manifest + TierContext core (enums, has, community)

**Objective:** Add `TierConfig` to `ProjectManifest` and implement `Capability`, `TierLevel`, `TierCapabilityError`, and `TierContext` with `has()` and `community()`.

**RED — Write Failing Tests:**
- **File:** `tests/tier/test_context.py`
- **Tests:**
  - `test_community_returns_community_tier` — `TierContext.community()` has tier=COMMUNITY, empty capabilities
  - `test_has_returns_false_for_missing_capability` — COMMUNITY context, `has(SHARED_MEMORY)` → False
  - `test_has_returns_true_for_present_capability` — context with SHARED_MEMORY, `has(SHARED_MEMORY)` → True
  - `test_capability_enum_has_seven_members` — all 7 from ADR-037
  - `test_tier_level_enum_values` — COMMUNITY, PRO, ENTERPRISE
- **File:** `tests/onboarding/test_manifest.py` (extend existing)
  - `test_manifest_with_tier_config` — YAML with tier section parses to `TierConfig`
  - `test_manifest_without_tier_config` — existing YAML without tier → `tier` is None

**GREEN — Implement:**
- **File:** `src/rai_cli/onboarding/manifest.py` — add `TierConfig` model + `tier: TierConfig | None = None` field
- **File:** `src/rai_cli/tier/__init__.py` — empty
- **File:** `src/rai_cli/tier/context.py` — `Capability`, `TierLevel`, `TierCapabilityError`, `TierContext` with `has()`, `community()`

**Verification:**
```bash
pytest tests/tier/test_context.py tests/onboarding/test_manifest.py -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenarios "Community tier by default", "Capability check"

---

### Task 2: require_or_suggest + from_manifest

**Objective:** Implement `require_or_suggest()` with actionable error messages and `from_manifest()` that reads tier via `load_manifest()`.

**RED — Write Failing Tests:**
- **File:** `tests/tier/test_context.py` (extend)
  - `test_require_or_suggest_raises_for_missing` — COMMUNITY context, `require_or_suggest(SEMANTIC_SEARCH)` raises `TierCapabilityError` with suggested_tier=PRO
  - `test_require_or_suggest_passes_for_present` — context with capability, no raise
  - `test_require_or_suggest_error_message_actionable` — error message contains tier name + capability
  - `test_from_manifest_no_manifest` — nonexistent path → COMMUNITY
  - `test_from_manifest_no_tier_section` — manifest without tier key → COMMUNITY
  - `test_from_manifest_pro_tier` — manifest with tier.level=pro + capabilities → PRO TierContext with capabilities
  - `test_from_manifest_enterprise_tier` — manifest with tier.level=enterprise + backend_url

**GREEN — Implement:**
- **File:** `src/rai_cli/tier/context.py` — `require_or_suggest()`, `from_manifest()`

**Verification:**
```bash
pytest tests/tier/test_context.py -v
```

**Size:** S
**Dependencies:** T1
**AC Reference:** Scenarios "PRO tier from manifest", "Actionable suggestion for missing capability"

---

### Task 3 (Final): Integration Verification

**Objective:** Validate full story: all tests pass, types clean, lint clean, existing tests unbroken.

**Verification:**
```bash
pytest tests/tier/ -v
pytest tests/onboarding/test_manifest.py -v
pyright src/rai_cli/tier/
ruff check src/rai_cli/tier/
pytest --tb=short -q  # full suite — zero regression
```

**Size:** XS
**Dependencies:** T1, T2

## Execution Order
1. T1 — TierConfig + enums + has + community (foundation)
2. T2 — require_or_suggest + from_manifest (depends on T1)
3. T3 — Integration verification (final)

## Risks
- **Manifest backward compat:** Adding optional `tier` field to `ProjectManifest` — low risk, Pydantic ignores unknown/missing fields by default.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | S | -- | |
| T2 | S | -- | |
| T3 | XS | -- | Integration verification |
