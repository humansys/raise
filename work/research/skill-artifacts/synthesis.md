# Skill Artifacts: Research Synthesis

> Date: 2026-03-03
> Sources: 3 evidence catalogs, 50+ sources, 6+ domains analyzed
> Status: Complete

---

## The Problem

RaiSE skills produce free-form markdown. No typed artifacts, no schema validation,
no governance verification on outputs. Docs for humans and memory for Rai are the
same unstructured representation.

**Goal:** Structured, verifiable artifacts (source of truth for Rai) with human docs
generated as a derivative. Open-core YAML in repo, with a path to Pro/Enterprise.

---

## Five Key Findings

### 1. YAML Frontmatter + Markdown Body Is the Proven Pattern

**Confidence: Very High** — MADR, Hugo, Jekyll, Obsidian, Docusaurus converged independently.

MADR's ADR-0013 explicitly evaluated alternatives and chose this pattern because:
- Machine-parseable metadata (YAML) colocated with human narrative (Markdown)
- Single file eliminates drift (Backstage's two-file approach causes drift at scale)
- Standard across ecosystems — every static site generator, every doc tool

**For RaiSE:** Each skill artifact = YAML frontmatter (typed, validated, dense for Rai)
+ Markdown body (human narrative, generated or authored). But see Finding #2.

### 2. For Pure Machine Artifacts, YAML-Only Is Better Than Hybrid

**Confidence: High** — SARIF, CycloneDX, JUnit XML, DORA events, Design Tokens.

The hybrid pattern works when you need BOTH machine and human consumption in ONE file.
But if the primary consumer is Rai (machine), and human docs are a separate generated
output, then **pure structured YAML is simpler and more validatable**.

The design tokens pattern (W3C DTCG) is instructive: one typed format serves machine
needs perfectly, with `$description` fields carrying enough human context that separate
narrative docs become optional for most use cases.

**For RaiSE:** Two-layer approach:
- **Layer 1 (source of truth):** Pure YAML artifacts — typed, schema-validated, dense
- **Layer 2 (generated):** Human-readable docs — Markdown/Confluence, generated from Layer 1

### 3. Schema + Semantic Linting Is the Gold Standard for Validation

**Confidence: High** — OpenAPI + Spectral, CUE, SARIF JSON Schema.

Structural schema validation (JSON Schema / Pydantic) catches "is this well-formed?"
Semantic linting catches "does this make sense?" — like Spectral rules for OpenAPI.

GitLab's insight: **type declaration beats schema definition** for usability. User declares
`artifact_type: story-design`, system knows the schema. No need for users to understand
the schema — the skill knows what it should produce.

**For RaiSE:**
- Pydantic models per artifact type (structural validation)
- Governance rules as semantic linting (content validation)
- Skill declares its output type → system validates automatically

### 4. Configuration Stays in Repo; State/Aggregation Moves to Service

**Confidence: Very High** — Terraform, Pulumi, Backstage, GitLab, Snyk all confirm.

The three things that consistently move to Pro/Enterprise:
1. **Cross-repo aggregation** (pattern propagation, team dashboards)
2. **Collaboration** (locking, RBAC, audit trails)
3. **Policy enforcement** (compliance, standards)

Definitions/config NEVER move. They stay in `.raise/`.

**For RaiSE:**
- Open-core: YAML artifacts in `.raise/artifacts/` — always in repo
- Pro/Enterprise: `rai login` switches backend for aggregation/state
- Same CLI, same artifact format, different backend (Terraform pattern)

### 5. SARIF's Separation of Concerns Is the Best Structural Model

**Confidence: High** — SARIF is an OASIS standard with wide adoption.

SARIF separates: tool metadata, rule definitions (define once, reference many),
results, and examined artifacts. This enables cross-tool aggregation.

**For RaiSE:** Separate:
- **Skill metadata** (who produced it, version, when)
- **Governance rules** (defined once in governance, referenced by artifacts)
- **Artifact content** (the actual design/plan/review data)
- **References** (what was examined — files, stories, epics)

---

## Proposed Model for RaiSE

### Artifact Schema (Conceptual)

```yaml
# .raise/artifacts/s347.1-design.yaml
artifact:
  type: story-design           # skill output type → drives schema selection
  version: 1                   # schema version
  skill: rai-story-design      # producing skill
  created: 2026-03-03T10:00:00Z
  story: S347.1
  epic: E347

# Governed fields — validated against governance rules
content:
  summary: "Adapter default selection for backlog CLI"
  complexity: small
  acceptance_criteria:
    - id: AC1
      description: "CLI auto-selects adapter when only one configured"
      verifiable: true
  integration_points:
    - module: rai_cli.backlog
      type: modification
      files: ["src/rai_cli/backlog/cli.py"]
  decisions:
    - id: D1
      choice: "Implicit default over explicit --adapter flag"
      rationale: "Single adapter case is 90%+ of usage"
      alternatives_considered: ["Always require flag", "Config file default"]

# References — what was examined
refs:
  backlog_item: RAISE-350
  epic_scope: work/epics/e347-backlog-automation/scope.md
  related_artifacts: []
```

### Human Docs (Generated)

```markdown
# S347.1 Design: Adapter Default Selection

**Story:** S347.1 | **Epic:** E347 | **Complexity:** Small

## Summary
Adapter default selection for backlog CLI...

## Acceptance Criteria
1. CLI auto-selects adapter when only one configured

## Integration Points
- `rai_cli.backlog` — modification to `src/rai_cli/backlog/cli.py`

## Decisions
### D1: Implicit default over explicit --adapter flag
**Rationale:** Single adapter case is 90%+ of usage
**Alternatives:** Always require flag, Config file default
```

### Storage Model

```
Open Core (always in repo):
  .raise/artifacts/           ← YAML artifacts (source of truth)
  .raise/schemas/             ← Pydantic-derived JSON Schemas
  .raise/governance/          ← Rules for semantic validation

Generated (disposable):
  work/docs/                  ← Human-readable Markdown (generated)
  Confluence/wiki             ← Published via rai docs publish

Pro/Enterprise (service):
  rai login                   ← Switches backend
  Cross-repo aggregation      ← Pattern propagation, dashboards
  Team collaboration          ← RBAC, audit, locking
  Policy enforcement          ← Org-wide governance
```

### Validation Pipeline

```
Skill produces artifact
  → Pydantic model validates structure (schema)
  → Governance rules validate content (semantic linting)
  → References validated (integrity checking)
  → Artifact written to .raise/artifacts/
  → Human docs generated to work/docs/ (or published)
```

---

## Open Questions

1. **Artifact granularity:** One YAML per skill execution, or one per story/epic with sections?
2. **Schema evolution:** How to handle schema version changes across artifacts?
3. **Narrative content:** Some skills (design, research) have significant narrative. Does it
   go in the YAML (as multiline strings) or stay as separate Markdown with a reference?
4. **Graph integration:** How do artifacts feed the knowledge graph? Direct ingestion?
5. **Migration:** How to migrate existing `work/epics/` Markdown artifacts to the new model?
6. **Skill SKILL.md update:** Each skill needs `output_type` declaration — incremental rollout?

---

## Evidence Catalogs

- [Dual Representation Patterns](../dual-representation-patterns/evidence-catalog.md)
- [Structured Process Artifacts](../structured-process-artifacts/evidence-catalog.md)
- [Open-Core Storage Patterns](../open-core-storage-patterns/evidence-catalog.md)
