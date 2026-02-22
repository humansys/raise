## Epic Scope: RAISE-211 Adapter Foundation

**Objective:** Implement ADR-033/034/035/036/037 as Python code — Protocol contracts, entry point registry, TierContext, and KnowledgeGraphBackend. Without this foundation, raise-pro (RAISE-208/209) cannot build and RAISE-207 (repo separation) has no clean code boundary.

**In Scope:**
- Protocol contracts as Python code (ADR-033/034)
- Entry point registry for adapter discovery (ADR-033)
- Governance extensibility — schema providers + parsers via registry (ADR-034)
- KnowledgeGraphBackend Protocol + FilesystemGraphBackend (ADR-036)
- TierContext — tier detection + progressive enrichment (ADR-037)
- `rai adapters list/check` CLI surface
- Refactor `rai memory build` input side to use registry

**Out of Scope:**
- Concrete PRO adapters (JiraAdapter, SupabaseGraphBackend) → raise-pro (RAISE-208/209)
- IdentityProvider / Profile sync → PRO onboarding
- SecretManagerAdapter → Enterprise (RAISE-142)
- AuditAdapter → Enterprise compliance
- SearchAdapter (semantic search, pgvector) → PRO
- SkillRegistryAdapter → org governance

**Stories (6):**
- S211.1: Protocol contracts — Python Protocol classes + Pydantic models
- S211.2: Entry point registry — importlib.metadata discovery
- S211.3: rai memory build — refactor input side to registry
- S211.4: KnowledgeGraphBackend Protocol + FilesystemGraphBackend
- S211.5: TierContext — capability detection, progressive enrichment
- S211.6: rai adapters list/check — CLI surface

**Critical path:** S1 → S2 → S3, S4 (parallel after S2), S5 (parallel after S1), S6 (after S2+S5)

**Done when:**
- [ ] All 6 stories complete
- [ ] All existing tests still pass (zero regression)
- [ ] `rai memory build` produces identical output via registry path
- [ ] Epic retrospective done
- [ ] Merged to v2
