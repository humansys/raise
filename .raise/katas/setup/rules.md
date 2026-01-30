---
id: rules
titulo: "Rules: Generate IDE Context from Governance"
work_cycle: setup
frequency: once-per-solution
fase_metodologia: 0

prerequisites:
  greenfield: [setup/governance]
  brownfield: []
template: templates/raise/governance/ide-rules.md
gate: null
next_kata: setup/ecosystem

adaptable: true
shuhari:
  shu: "Generate all IDE context files systematically from guardrails"
  ha: "Focus on high-impact rules; defer tool-specific customization"
  ri: "Create specialized templates for different AI tools (Claude, Cursor, Copilot)"

multi_session: false
version: 1.0.0
---

# Rules: Generate IDE Context from Governance

## Propósito

Translate governance artifacts (Constitution, Solution Vision, Guardrails) into **AI-readable context files** that guide code generation tools. This kata bridges the gap between human-defined governance and machine-consumable instructions.

**Key insight:** Guardrails define WHAT must be enforced; IDE rules define HOW to communicate that to AI assistants.

## Contexto

**Ubicación en la jerarquía (ADR-010):**

```
SOLUTION LEVEL:
  solution/discovery → solution/vision → setup/governance → [setup/rules]
         ↓                   ↓                  ↓                 ↓
    Business Case      Solution Vision      Guardrails        IDE Rules
    "¿Por qué?"        "¿Qué sistema?"     "¿Qué estándares?"  "¿Cómo comunicar a AI?"
```

**Cuándo usar:**
- After `setup/governance` completes (greenfield)
- When adopting RaiSE on an existing codebase (brownfield)
- When guardrails change significantly
- When adding support for new AI tools

**Modos de ejecución:**

| Modo | Input | Proceso |
|------|-------|---------|
| **Greenfield** | Constitution + Solution Vision + Guardrails | Derive IDE rules from governance artifacts |
| **Brownfield** | Codebase + Guardrails | Extract patterns from code + derive from guardrails |

**Inputs requeridos:**
- `framework/reference/constitution.md` (RaiSE principles)
- `governance/solution/vision.md` (system identity, stack, architecture)
- `governance/solution/guardrails.md` (MUST/SHOULD rules)

**Outputs:**
- `CLAUDE.md` — Project context for Claude Code
- `.cursorrules` — Project context for Cursor
- `.cursor/rules/*.mdc` — Granular rules for Cursor (optional)

## Pasos

### Paso 1: Cargar Governance Artifacts

Load the three sources of governance context:

**Constitution (Principles):**
- §1-8 principles that apply universally
- Values and restrictions
- Terminology

**Solution Vision (Identity):**
- System description and mission
- Technical stack and patterns
- Architecture decisions
- Quality attributes

**Guardrails (Rules):**
- MUST rules (blocking)
- SHOULD rules (recommended)
- Verification commands

**Verificación:** All three artifacts loaded and understood.

> **Si no puedes continuar:** Artifacts missing → Execute prerequisite katas first.

### Paso 2: Identify Target AI Tools

Determine which AI tools need context files:

| Tool | Context File | Format |
|------|--------------|--------|
| Claude Code | `CLAUDE.md` | Markdown with structured sections |
| Cursor | `.cursorrules` | Markdown (single file) |
| Cursor (granular) | `.cursor/rules/*.mdc` | MDC files with YAML frontmatter |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown |

**Verificación:** Target tools identified.

> **Si no puedes continuar:** Unknown tool → Research tool's context format first.

### Paso 3: Generate Project Identity Section

Create the opening section that establishes project identity:

```markdown
# [Project Name]

## Project Identity

[1-2 sentence description from Solution Vision]

**Type:** [System type from Solution Vision]
**Stack:** [Primary technologies]
**Architecture:** [Key pattern]
```

**Verificación:** Identity section captures Solution Vision essence.

> **Si no puedes continuar:** Identity unclear → Review Solution Vision §Identity.

### Paso 4: Translate Guardrails to Instructions

Convert each guardrail to AI-readable instructions:

**For MUST guardrails:**
```markdown
## [Category] Standards

**REQUIRED:**
- [Guardrail description as imperative instruction]
- [Another guardrail...]

**Verification:** [How to check compliance]
```

**For SHOULD guardrails:**
```markdown
## [Category] Guidelines

**RECOMMENDED:**
- [Guardrail description as recommendation]
```

**Mapping table:**

| Guardrail Element | IDE Rule Element |
|-------------------|------------------|
| `id` | Reference in comments |
| `level: MUST` | "REQUIRED", "ALWAYS", "MUST" |
| `level: SHOULD` | "RECOMMENDED", "PREFER", "SHOULD" |
| `Contexto` section | Direct inclusion as instruction |
| `Verificación` section | How to validate |
| `Ejemplos` | Include as code examples |

**Verificación:** All MUST guardrails translated; SHOULD guardrails included.

> **Si no puedes continuar:** Guardrail unclear → Review guardrail's Golden Context section.

### Paso 5: Add Constitution Principles

Include relevant constitutional principles:

```markdown
## Development Principles

This project follows RaiSE methodology:

- **Humans Define, Machines Execute** — Specs are source of truth
- **Governance as Code** — Standards are versioned in Git
- **Validation Gates** — Quality checked at each phase
- [Other relevant principles...]

## Restrictions

NEVER:
- [From Constitution §Restricciones]

ALWAYS:
- [From Constitution §Restricciones]
```

**Verificación:** Key principles included, restrictions clear.

> **Si no puedes continuar:** Principle unclear → Reference Constitution directly.

### Paso 6: Add Architecture Context

Include architecture-specific guidance:

```markdown
## Architecture

[Architecture pattern from Solution Vision]

### Directory Structure
```
[Expected structure]
```

### Key Patterns
- [Pattern 1]: [When/how to use]
- [Pattern 2]: [When/how to use]

### Boundaries
- [What this system does NOT do]
```

**Verificación:** Architecture guidance clear and actionable.

> **Si no puedes continuar:** Architecture unclear → Review Solution Vision §Dirección Técnica.

### Paso 7: Generate Tool-Specific Files

Create the actual context files:

**CLAUDE.md structure:**
```markdown
# [Project Name]

## Project Identity
[From Step 3]

## Development Principles
[From Step 5]

## Code Standards
[From Step 4 - Code guardrails]

## Testing Standards
[From Step 4 - Test guardrails]

## Architecture
[From Step 6]

## Active Technologies
[List from Solution Vision]

## Restrictions
[From Step 5]
```

**.cursorrules structure:**
Similar to CLAUDE.md but may use different conventions per Cursor docs.

**.cursor/rules/*.mdc structure:**
```yaml
---
name: [Rule name]
globs: ["pattern/**/*.py"]
---

# [Rule Title]

[Rule content from guardrail's Golden Context]

## Examples

### Correct
[From guardrail examples]

### Incorrect
[From guardrail examples]
```

**Verificación:** All target files created with complete content.

> **Si no puedes continuar:** Format incorrect → Verify against tool documentation.

### Paso 8: Validate Coherence

Cross-check generated files:

- [ ] All MUST guardrails represented in IDE rules
- [ ] No contradictions between files
- [ ] Examples are valid code for the stack
- [ ] File format matches tool requirements
- [ ] Terminology consistent with Constitution

**Verificación:** Coherence validated.

> **Si no puedes continuar:** Inconsistency found → Resolve and regenerate affected sections.

### Paso 9: Commit and Document

Commit the generated files:

```bash
git add CLAUDE.md .cursorrules .cursor/rules/
git commit -m "feat(governance): Generate IDE rules from guardrails"
```

Update governance index if applicable.

**Verificación:** Files committed and tracked.

> **Si no puedes continuar:** N/A — This step always completes.

## Output

- **Artefactos:**
  - `CLAUDE.md` — Claude Code context
  - `.cursorrules` — Cursor context (optional)
  - `.cursor/rules/*.mdc` — Granular Cursor rules (optional)
- **Ubicación:** Project root
- **Gate:** N/A (validation in Step 8)
- **Siguiente kata:** `setup/ecosystem`

## Notas por Modo

### Greenfield

In greenfield mode:

1. **Start** with Constitution as base principles
2. **Layer** Solution Vision for project-specific identity
3. **Add** Guardrails as specific rules
4. **Generate** complete IDE context files

The files will be comprehensive from the start.

### Brownfield

In brownfield mode:

1. **Analyze** existing code patterns (may run `setup/analyze` first)
2. **Extract** implicit conventions
3. **Merge** with formal guardrails
4. **Generate** IDE rules that reflect reality + aspirations
5. **Mark** aspirational rules (things to improve) separately

Use the `setup/analyze` kata for pattern extraction before this kata.

## Derivation Examples

### Guardrail → CLAUDE.md

**Input (guardrail):**
```yaml
id: MUST-CODE-001
level: MUST
Regla: Type hints on all code

Contexto:
  When writing Python code:
  - All function parameters must have type hints
  - All return types must be annotated
  - Use Pydantic models for complex types

Verificación:
  command: pyright --strict src/
```

**Output (CLAUDE.md section):**
```markdown
## Code Standards

**REQUIRED - Type Safety:**
- All function parameters must have type hints
- All return types must be annotated
- Use Pydantic models for complex types
- Verify with: `pyright --strict src/`
```

### Constitution → CLAUDE.md

**Input (Constitution §7):**
```markdown
### §7. Lean Software Development
| Principio Lean | Manifestación en RaiSE |
| Eliminar desperdicio | Context-first (no hallucinations) |
| Construir integridad | Jidoka (parar en defectos) |
```

**Output (CLAUDE.md section):**
```markdown
## Development Principles

This project follows Lean principles:
- **Context-first**: Always understand context before generating code
- **Jidoka**: Stop and fix defects immediately; don't accumulate errors
```

## ShuHaRi

| Nivel | Aplicación |
|-------|------------|
| **Shu** | Generate all IDE context files from template |
| **Ha** | Customize depth per tool; prioritize high-impact rules |
| **Ri** | Create tool-specific templates; automate regeneration on guardrail changes |

## Referencias

- **ADR-010**: `dev/decisions/framework/adr-010-three-level-artifact-hierarchy.md`
- **Constitution**: `framework/reference/constitution.md`
- **Prerequisite**: `setup/governance` (greenfield) or `setup/analyze` (brownfield)
- **Siguiente kata**: `setup/ecosystem`
