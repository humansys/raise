---
description: Enforce structure and standards for RaiSE v2.1 Katas (Frontmatter, Sections, Jidoka).
globs:
  - src/katas-v2.1/**/*.md
---

# Kata Structure v2.1

This rule enforces the standard structure for Kata files in the RaiSE v2.1 framework.

## 1. Frontmatter Validation

All Kata files MUST start with a YAML frontmatter block containing the following fields:

```yaml
---
id: [string, format: {nivel}-{number}-{name}]
nivel: [enum: flujo, patron, principios, tecnica]
titulo: [string]
audience: [enum: beginner, intermediate, advanced]
template_asociado: [string path or null]
validation_gate: [string path or null]
prerequisites: [list of strings]
tags: [list of strings]
version: [semver string]
---
```

**Verification:**
- Ensure `id` matches the folder and filename context.
- Ensure `template_asociado` and `validation_gate` are present (even if null).

## 2. Mandatory Sections (Structure)

The document MUST follow this high-level structure (H2 headers):

1.  `## Propósito`
2.  `## Contexto` OR `## Cuándo Aplicar`
3.  `## Pasos` (for 'flujo') OR `## Estructura` (for 'patron')
4.  `## Output`
5.  `## Validation Gate` (if applicable, or explicitly None/N/A)
6.  `## Referencias`

## 3. Jidoka Inline Pattern

For every actionable step (usually H3 headers under `Pasos` or `Estructura`), you MUST include the "Jidoka Inline" pattern to enable self-correction.

**Pattern:**

```markdown
### [Step Title]

[Step Description/Instructions]

**Verificación:** [Criteria to verify success]

> **Si no puedes continuar:** [Condition/Cause] → [Resolution/Action]
```

**Rule:**
- Every `###` header inside the main execution section MUST be followed eventually by a `**Verificación:**` line.
- Immediately after verification, there MUST be a blockquote starting with `> **Si no puedes continuar:**`.

## 4. Anti-Patterns to Reject

- **Missing Jidoka**: Steps that give instructions but no way to verify or recover.
- **Vague Verification**: Verifications that say "Check if it looks good" without specific criteria.
- **Inconsistent ID**: `id` in frontmatter does not match the file path logic.
