# Spec-kit & RaiSE Integration - Research Notes

**Date**: 2026-01-12
**Purpose**: Consolidated reference for integrating RaiSE methodology with spec-kit tooling
**Status**: Work assigned to developer - use as reference

---

## TL;DR - Viability Conclusion

**✅ Integration is fully viable without forking spec-kit.**

Spec-kit is designed to be methodology-agnostic and extensible through:
- Configuration files (`.specify/config.json`)
- Template customization
- Command extensibility (via `.specify/` scripts)

RaiSE's governance layer can be injected through configuration and templates, not code modification.

---

## Key Finding: Spec-kit Extensibility Model

After analyzing spec-kit's source code (`src/specify_cli/__init__.py`), we confirmed:

**Spec-kit is a bootstrapper, not a monolithic tool.**

- Commands like `/speckit.specify`, `/speckit.plan` are NOT hardcoded in the Python binary
- They live as configurations/scripts in `.specify/` directory after project initialization
- The CLI downloads a template ZIP from GitHub and decompresses it locally
- All customization happens via files in `.specify/`, no binary modification needed

**Implication**: We can extend spec-kit with RaiSE-specific commands by adding files to `.specify/` directory.

---

## Configuration Schema Design

### Extending `.specify/config.json`

**Decision**: Add `mode` field and nested `raise` object to existing config.

**Rationale**: Maintains simplicity while allowing methodology switching.

**Schema**:
```json
{
  "base_branch": "string",
  "git_platform": "string",
  "repository": "string",
  "merge_request_target": "string",
  "metadata": { ... },

  "mode": "default" | "raise",

  "raise": {
    "templates": "string (path)",
    "constitution": "string (path)",
    "gates": "string (path)",
    "glossary": "string (path)",
    "extendedArtifacts": "boolean"
  }
}
```

**Alternatives Rejected**:
- Separate `raise.config.json` → Adds complexity, multiple files to check
- Environment variables → Not "Governance as Code", harder to version
- Command-line flags → Repetitive, error-prone, not persistent

**Backwards Compatibility**:
- `mode` defaults to `"default"` if absent
- All `raise.*` fields optional - graceful degradation

---

## RaiSE Document Format Analysis

### Constitution Format

**Source**: `docs/framework/v2.1/model/00-constitution-v2.md`

**Structure**:
```markdown
## Principios Innegociables

### §1. [Principle Name]
[Description]
**Implicación práctica:** [Guidance]

### §2. [Principle Name]
...
```

**Parsing Strategy**:
- Regex: `### §(\d+)\. (.+)` to extract number and name
- All §N principles are MUST-level (constitution is "innegociable")
- Text after "**Implicación práctica:**" = actionable guidance

### Glossary Format

**Source**: `docs/framework/v2.1/model/20-glossary-v2.1.md`

**Key Section**: "Anti-Términos (Qué NO Usamos)"

```markdown
| Evitar | Usar en su lugar | Razón |
|--------|------------------|-------|
| "DoD" | "Validation Gate" | HITL estándar |
| "Rule" | "Guardrail" | Más específico |
```

**Parsing Strategy**:
- Locate `## Anti-Términos` section
- Column 1 = deprecated term
- Column 2 = canonical term
- **Case-insensitive matching** when scanning artifacts

### Validation Gate Format

**Source**: `src/gates/gate-*.md`

**Structure**:
```yaml
---
id: gate-discovery
fase: 1
titulo: "Gate-Discovery: Validación del PRD"
blocking: true
version: 1.0.0
---
```

```markdown
## Criterios de Validación

### Criterios Obligatorios (Must Pass)
| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **X** | ... |

### Criterios Recomendados (Should Pass)
| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | **Y** | ... |
```

**Parsing Strategy**:
- Extract YAML frontmatter for metadata
- "Criterios Obligatorios" → MUST items
- "Criterios Recomendados" → SHOULD items
- Convert to spec-kit checklist format with `- [ ]` checkboxes

---

## Methodology Mapping: RaiSE vs. Spec-kit

### Phase Mismatch Analysis

**Problem**: Spec-kit operates at **feature level**, RaiSE operates at **project/context level**.

| Level | RaiSE Phase | Spec-kit Command | Gap |
|-------|-------------|------------------|-----|
| **Strategy** | Fase 0: Context | — | ❌ Missing |
| **Product** | Fase 1: Discovery | (implicit in `specify`) | ⚠️ Partial |
| **Architecture** | Fase 2: Vision | — | ❌ Missing |
| **Tactics** | Fase 4: Backlog | — | ❌ Missing |
| **Execution** | Fase 5-6: Plan/Dev | `/speckit.plan` | ✅ Exists |

**Implication**: To fully implement RaiSE, we need additional commands:
- `/raise.context` - Project context and stakeholder analysis
- `/raise.discovery` - Product-level PRD (not just feature)
- `/raise.vision` - Solution architecture and high-level design
- `/raise.backlog` - MVP definition and prioritization

These can be added as new command definitions in `.specify/` without touching spec-kit binary.

---

## Integration Strategy

### Minimal Viable Change (MVC)

1. **Mode Detection**: Add logic to each spec-kit command to:
   - Read `.specify/config.json`
   - Check `mode` field
   - If `mode == "raise"`, load RaiSE templates from `raise.templates` path
   - If `mode == "default"`, use standard behavior

2. **Template Customization**:
   - Create RaiSE-specific templates in `.specify/templates/raise/`
   - Include Validation Gate checklists in spec/plan templates
   - Embed Constitution principles in planning phase

3. **Constitution Injection**:
   - Replace default `.specify/memory/constitution.md` with RaiSE Constitution v2.1
   - Forces agent to follow RaiSE principles (Heutagogía, Simplicidad, etc.)

4. **New Commands** (optional, higher effort):
   - Define `/raise.*` commands in `.specify/` for project-level phases
   - Create templates for context, vision, backlog

---

## Templates Created (Reference)

During preliminary work, these templates were drafted:

- `.specify/templates/raise/spec-template.md` - RaiSE spec with gates
- `.specify/templates/raise/plan-template.md` - RaiSE plan with Constitution check
- `.specify/templates/raise/tasks-template.md` - Task breakdown template
- `.specify/templates/raise/mode-detection-snippet.md` - Reusable mode detection logic

**Note**: These templates are **not production-ready** and should be redesigned by the implementing developer.

---

## References

- **Spec-kit Source**: `/home/emilio/Code/spec-kit`
- **RaiSE Methodology**: `docs/framework/v2.1/model/21-methodology-v2.md`
- **RaiSE Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`
- **Validation Gates**: `src/gates/`
- **Katas v2.1**: `src/katas-v2.1/`

---

*This document consolidates research from an abandoned feature branch. Use as reference material for future spec-kit integration work.*
