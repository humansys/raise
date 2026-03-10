# Epic Design: E354 — Typed Skill Artifacts

> **Date:** 2026-03-03
> **Branch:** `epic/e354/typed-skill-artifacts`
> **Jira:** [RAISE-402](https://humansys.atlassian.net/browse/RAISE-402)

---

## Gemba: Current State

Skills produce free-form Markdown files written directly to `work/epics/e{N}-{name}/stories/`. No structured schema, no validation, no machine-readable output. The graph builder (`GraphBuilder`) has 7 loaders but none read skill outputs as structured data.

**Key integration points:**
- `src/rai_cli/skills/schema.py` — skill frontmatter parsing (add `output_type`)
- `src/rai_cli/context/builder.py` — graph build pipeline (add `load_artifacts()`)
- `src/rai_cli/skills_base/rai-story-design/SKILL.md` — pilot skill to rewire
- `.raise/gates/` — governance rules (inform Pydantic validators)

## Architecture Decisions

### AD1: New `src/rai_cli/artifacts/` module
Dedicated module for artifact models, validation, reader/writer. Follows existing module pattern (`governance/`, `memory/`, `skills/`). Clean separation from governance (artifacts are validated *by* governance rules, not *part of* governance).

### AD2: Pydantic validators as governance rules
Semantic validation encoded as `@model_validator` and `@field_validator` directly on artifact models. No rule engine, no gate file parsing. Simple and sufficient for 1-3 artifact types. Structure allows extraction to engine later if needed.

### AD3: `raise.output_type` in SKILL.md frontmatter
Skills declare their artifact type via existing metadata mechanism:
```yaml
metadata:
  raise.output_type: story-design
```
System uses this to select the Pydantic model for validation. No Python registration needed per skill.

### AD4: Replace, not transition (from research D1)
Pilot skill (`rai-story-design`) switches cleanly from Markdown to YAML artifact. No dual output, no feature flag. YAML is source of truth; human docs are generated.

## Target Components

```
src/rai_cli/artifacts/
├── __init__.py
├── models.py          # SkillArtifact base + ArtifactType enum
├── story_design.py    # StoryDesignArtifact + content model + validators
├── writer.py          # YAML serializer → .raise/artifacts/
├── reader.py          # YAML deserializer + validation
└── renderer.py        # YAML → Markdown doc generator

src/rai_cli/context/builder.py  # Add load_artifacts() method
src/rai_cli/skills/schema.py    # Add output_type to SkillFrontmatter
```

## Key Contracts

### SkillArtifact (base)
```yaml
artifact:
  type: story-design       # ArtifactType enum
  version: 1               # Schema version (D5: additive only)
  skill: rai-story-design  # Producing skill name
  created: 2026-03-03T10:00:00Z
  story: S354.1            # Work item context
  epic: E354

content: {}                # Type-specific, validated by subclass

refs:                      # References to external items
  backlog_item: RAISE-XXX
  epic_scope: work/epics/e354-.../scope.md
```

### StoryDesignArtifact (content)
```yaml
content:
  summary: "..."
  complexity: small|medium|large
  acceptance_criteria:
    - id: AC1
      description: "..."
      verifiable: true
  integration_points:
    - module: rai_cli.artifacts
      type: new|modification
      files: ["src/rai_cli/artifacts/models.py"]
  decisions:
    - id: D1
      choice: "..."
      rationale: "..."
      alternatives_considered: ["..."]
```

### Governance Validators (Pydantic)
- AC count between 1-10
- All AC must be verifiable
- Complexity must match story size heuristic
- Integration points must reference existing modules
- Decisions must have rationale

## Storage Layout

```
.raise/artifacts/           ← YAML typed artifacts (source of truth)
  s354.1-design.yaml        ← {story_id}-{artifact_type}.yaml
  s354.2-design.yaml

work/docs/                  ← Generated human-readable Markdown
  s354.1-design.md          ← Generated from .yaml, disposable

work/epics/                 ← Historical (read-only, D3)
```

## Story Dependency Graph

```
S354.1 (base model + storage)
  ├── S354.2 (story-design schema)
  │     ├── S354.4 (doc generation)  ─┐
  │     └── S354.5 (pilot wiring)  ←──┘
  └── S354.3 (graph ingestion)
```

S354.3 and S354.4 can run in parallel (independent consumers of S354.1/S354.2).

## Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Schema too rigid for design variability | M | H | Validate against 3-5 historical designs before fixing |
| Clean replacement breaks existing workflow | L | M | E2E test in S354.5 before merge |
| Pydantic validators don't scale to 10+ types | L | L | Additive schema (D5) + extractable structure |
