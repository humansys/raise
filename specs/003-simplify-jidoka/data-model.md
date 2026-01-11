# Data Model: Simplificar Jidoka

**Feature**: 003-simplify-jidoka
**Date**: 2026-01-11
**Phase**: 1 (Design)

## Document Structure

### Entity: Glossary Entry (Jidoka)

Represents the complete Jidoka entry in the glossary v2.1, structured with progressive disclosure.

**Attributes**:
- `term`: String ("Jidoka") - canonical, immutable
- `simple_interface_stage_0_1`: String (≤10 words, accessible language)
- `simple_definition_stage_0_1`: String (1-2 sentences, no TPS terminology)
- `example_stage_0_1`: String (concrete RaiSE workflow example)
- `formal_definition_stage_3`: String (4-step TPS cycle)
- `historical_context_stage_3`: String (optional: etymology, TPS origin)

**Constraints**:
- `simple_interface_stage_0_1` MUST be ≤10 words (SC-001)
- Stage 0-1 content MUST NOT contain: "TPS", "Toyota", "Lean", "自働化" (SC-002)
- `term` MUST remain "Jidoka" (canonical, FR-007)
- Stage indicator MUST be present: "(Stage 0-1)" or "(Stage 3)" (FR-006)

**Validation Rules**:
- Gate-Terminología: `term` matches glossary v2.1 canonical list
- Gate-Coherencia: No contradictions between simple and formal definitions
- SC-001: `wc -w simple_interface_stage_0_1` ≤ 10
- SC-002: `grep -c "TPS\|Toyota\|Lean\|自働化" stage_0_1_content` == 0

---

### Entity: Ontology Bundle Section (Jidoka References)

Represents references to Jidoka scattered throughout the ontology bundle v2.1 document.

**Attributes**:
- `section_name`: String (e.g., "Introduction", "Core Principles", "MCP Integration")
- `section_stage`: Enum (STAGE_0_1, STAGE_3) - inferred from content complexity
- `jidoka_reference_type`: Enum (SIMPLIFIED, FORMAL)
- `reference_text`: String (the actual text mentioning Jidoka)

**Constraints**:
- IF `section_stage == STAGE_0_1` THEN `jidoka_reference_type == SIMPLIFIED` (FR-004)
- IF `section_stage == STAGE_3` THEN `jidoka_reference_type == FORMAL` (FR-004)
- Consistency: All refs in same section use same type

**Relationships**:
- References → Glossary Entry (source of truth)
- Section → Learning Path Stages (determines which definition to use)

**Implementation Note**: Ontology bundle doesn't have explicit stage markers for all sections. Section classification is based on:
- Intro/Core Principles → STAGE_0_1
- Advanced topics (MCP, Ng Patterns, Metrics AI) → STAGE_3

---

## Markdown Template Structure

### Template: Glossary Entry (20-glossary-v2.1.md)

```markdown
### Jidoka

**Interfaz Simple (Stage 0-1)**: [simple_interface_stage_0_1]

[simple_definition_stage_0_1]

**Ejemplo**: [example_stage_0_1]

---

**Detalle Avanzado (Stage 3)**:

Jidoka (自働化) — [formal_definition_stage_3]

**Ciclo formal**:
1. **Detectar**: Identificar el defecto o anomalía
2. **Parar**: Detener el proceso inmediatamente
3. **Corregir**: Resolver la causa raíz
4. **Continuar**: Reanudar con mejora preventiva

**Contexto histórico**: [historical_context_stage_3]
```

**Filled Example** (based on D2 decision from research.md):

```markdown
### Jidoka

**Interfaz Simple (Stage 0-1)**: Parar si algo falla

Principio de detener el trabajo cuando detectas un problema, en lugar de acumular errores.

**Ejemplo**: Cuando ejecutas `/speckit.plan` y el gate de coherencia falla, el workflow para - no continúa generando tareas sobre una base inconsistente.

---

**Detalle Avanzado (Stage 3)**:

Jidoka (自働化) — Automatización con toque humano.

**Ciclo formal**:
1. **Detectar**: Identificar el defecto o anomalía
2. **Parar**: Detener el proceso inmediatamente
3. **Corregir**: Resolver la causa raíz
4. **Continuar**: Reanudar con mejora preventiva

**Contexto histórico**: Originado en telares automáticos de Sakichi Toyoda (1896), aplicado a manufactura por Taiichi Ohno en el Toyota Production System.
```

---

### Template: Ontology Bundle Reference (25-ontology-bundle-v2_1.md)

**For Stage 0-1 Sections** (Introduction, Core Principles):

```markdown
[Previous content...]

El framework RaiSE aplica [simple_interface_stage_0_1] (Jidoka) en cada fase del workflow. Ver [glosario](./20-glossary-v2.1.md#jidoka) para detalles.

[Next content...]
```

**For Stage 3 Sections** (MCP Integration, Advanced Patterns):

```markdown
[Previous content...]

La integración con MCP requiere aplicar el ciclo Jidoka completo:
1. **Detectar** anomalías en el contexto del agente
2. **Parar** la ejecución ante inconsistencias
3. **Corregir** el golden data o las reglas de contexto
4. **Continuar** con contexto validado

Ver [glosario detallado](./20-glossary-v2.1.md#jidoka) para fundamentos TPS.

[Next content...]
```

---

## Validation Schema

### Gate-Terminología

| Verification | Method | Expected Result |
|--------------|--------|-----------------|
| Canonical term preserved | Check `term == "Jidoka"` | TRUE |
| No new aliases created | Search for "Jidoka-simple", "Jidoka-avanzado" | 0 matches |
| Glosario v2.1 consistency | Compare against canonical list | MATCH |

**Command**:
```bash
grep -i "jidoka" docs/framework/v2.1/model/20-glossary-v2.1.md | grep -v "^### Jidoka$"
# Expect: only one canonical entry "### Jidoka"
```

---

### Gate-Coherencia

| Verification | Method | Expected Result |
|--------------|--------|-----------------|
| No contradictions between stages | Compare simple vs formal definitions | ALIGNED |
| Constitution §4 alignment | Verify Jidoka supports Validation Gates | ALIGNED |
| Constitution §8 alignment | Verify simplification reduces complexity | ALIGNED |
| No TPS in Stage 0-1 | `grep` for prohibited terms | 0 matches |

**Command**:
```bash
# Extract Stage 0-1 content (lines between "### Jidoka" and "---")
sed -n '/^### Jidoka$/,/^---$/p' docs/framework/v2.1/model/20-glossary-v2.1.md \
  | grep -iE "TPS|Toyota|Lean|自働化"
# Expect: 0 matches
```

---

### Success Criteria Validation

| Criterion | Validation Method | Command/Process |
|-----------|-------------------|-----------------|
| SC-001: ≤10 words | Word count | `echo "Parar si algo falla" \| wc -w` → 4 |
| SC-002: Zero prohibited terms | Text search | `grep -c "TPS\|Toyota\|Lean\|自働化" stage_0_1_section` → 0 |
| SC-003: Gate-Terminología | Manual check | Review canonical terms list |
| SC-004: Gate-Coherencia | Manual check | Cross-reference with Constitution |
| SC-005: 5% complexity reduction | Proxy metric | Prerequisite count: was 1 (TPS), now 0 |
| SC-006: <30s comprehension | User study proxy | Reading time: 4 words @ 200wpm ≈ 1.2s + 10s comprehension ≈ 11s |

---

## File Locations

| Artifact | Path | Size Est. | Purpose |
|----------|------|-----------|---------|
| Glossary v2.1 | `docs/framework/v2.1/model/20-glossary-v2.1.md` | ~45KB → ~45.5KB | Update Jidoka entry |
| Ontology Bundle v2.1 | `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md` | ~55KB → ~55.5KB | Update Jidoka refs |
| Glossary Seed (ref only) | `docs/framework/v2.1/model/20a-glossary-seed.md` | No change | Already simplified (Feature 002) |

**Storage**: All files in Git, plain text Markdown

**Versioning**: Git commit with descriptive message linking to Feature 003

---

## State Transitions

### Glossary Entry State Machine

```
[Current Jidoka Entry]
       |
       | (Read current content)
       v
[Backup Created]
       |
       | (Apply template)
       v
[Staged Entry with Stage 0-1 + Stage 3]
       |
       | (Validate SC-001, SC-002)
       v
[Validated Entry]
       |
       | (Gate-Terminología, Gate-Coherencia)
       v
[Approved Entry]
       |
       | (Git commit)
       v
[Published Entry]
```

### Ontology Bundle State Machine

```
[Current Bundle]
       |
       | (Search for Jidoka refs)
       v
[Refs Identified]
       |
       | (Classify by section stage)
       v
[Refs Categorized: STAGE_0_1 | STAGE_3]
       |
       | (Apply appropriate reference type)
       v
[Refs Updated]
       |
       | (Cross-check consistency)
       v
[Validated Bundle]
       |
       | (Git commit)
       v
[Published Bundle]
```

---

## Dependencies

- **Depends on**: Existing glossary v2.1 and ontology bundle v2.1
- **Depends on**: ADR-009 pattern definition
- **Depends on**: Learning path stages (Feature 001)

---

## Notes

- No database, no API contracts (this is documentation only)
- Validation is primarily text-based (grep, wc, manual review)
- Success relies on consistency between two markdown files
- Git provides versioning and rollback safety

---

*Data model complete. Proceeding to quickstart.md.*
