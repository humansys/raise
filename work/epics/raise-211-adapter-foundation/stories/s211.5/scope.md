## Feature Scope: S211.5 — TierContext

**In Scope:**
- `Capability` StrEnum with capabilities from ADR-037 design
- `TierLevel` StrEnum (community, pro, enterprise)
- `TierContext` dataclass with `has()`, `require_or_suggest()`, `from_manifest()`, `community()`
- Module: `src/rai_cli/tier/context.py`
- Unit tests for all methods and edge cases

**Out of Scope:**
- Actual manifest file parsing (no `.raise/manifest.yaml` schema yet — use sensible defaults)
- Feature gating in existing commands (consumers come in S211.6+)
- PRO/Enterprise backend URL validation
- `rai tier status` CLI command (parking lot item)

**Done Criteria:**
- [ ] `TierContext.community()` returns COMMUNITY tier with empty capabilities
- [ ] `TierContext.from_manifest()` reads tier + capabilities from YAML
- [ ] `require_or_suggest()` raises for missing capabilities with actionable message
- [ ] All tests pass, pyright strict, ruff clean
- [ ] Retrospective complete
