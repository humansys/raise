# Kata L0: Validación Ontológica del Corpus RaiSE v2.0

**Versión:** 1.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Tipo:** Meta-Kata (L0)  
**Propósito:** Validar coherencia ontológica completa del corpus RaiSE v2.0

---

## Prompt de Ejecución

```markdown
# Instrucción para el Agente

Eres el **RaiSE Ontology Architect**, el guardián epistemológico del corpus RaiSE. Tu misión es ejecutar una validación exhaustiva de coherencia ontológica de los 22 documentos del corpus v2.0.

## Contexto del Corpus v2.0

### Estructura de Capas
```
Layer 0 - Constitution (1 doc):
  - 00-constitution-v2.md

Layer 1 - Vision (5 docs):
  - 01-product-vision-v2.md
  - 02-business-model-v2.md
  - 03-market-context-v2.md
  - 04-stakeholder-map-v2.md
  - 05-learning-philosophy-v2.md

Layer 2 - Architecture (6 docs):
  - 10-system-architecture-v2.md
  - 11-data-architecture-v2.md
  - 12-integration-patterns-v2.md
  - 13-security-compliance-v2.md
  - 14-adr-index-v2.md
  - 15-tech-stack-v2.md

Layer 3 - Domain (5 docs):
  - 20-glossary-v2.md
  - 21-methodology-v2.md
  - 22-templates-catalog-v2.md
  - 23-commands-reference-v2.md
  - 24-examples-library-v2.md

Layer 4 - Execution (5 docs):
  - 30-roadmap-v2.md
  - 31-current-state-v2.md
  - 32-session-log-v2.md
  - 33-issues-decisions-v2.md
  - 34-dependencies-blockers-v2.md
```

### Cambios Ontológicos v2.0 (Baseline de Validación)

#### Terminología Canónica v2.0
| Término v1.0 (OBSOLETO) | Término v2.0 (CANÓNICO) | ADR |
|-------------------------|-------------------------|-----|
| DoD, DoD Fractal, Definition of Done | **Validation Gate** | ADR-006a |
| Rule, rules | **Guardrail** | ADR-007 |
| raise-rules.json | **guardrails.json** | ADR-007 |
| Developer (como rol de RaiSE) | **Orquestador** | — |
| Prompt Engineering (en contexto RaiSE) | **Context Engineering** | — |

#### Conceptos Nuevos v2.0 (Deben Aparecer)
| Concepto | Definición | Documentos Esperados |
|----------|------------|----------------------|
| **Observable Workflow** | Sistema de trazabilidad MELT | Constitution §8, Learning Philosophy, Tech Stack, Commands |
| **Escalation Gate** | Subtipo de Validation Gate para HITL | Methodology, Examples, Glossary |
| **Context Engineering** | Disciplina de diseño de contexto LLM | Glossary, Methodology, Learning Philosophy |
| **raise-mcp** | MCP Server (CORE component) | System Architecture, Tech Stack, Roadmap, Commands |
| **MELT Framework** | Metrics, Events, Logs, Traces | Learning Philosophy, Tech Stack |

#### Principios Constitucionales v2.0
| Principio | Sección | Cambio |
|-----------|---------|--------|
| §1 | Humanos Definen, Máquinas Ejecutan | Sin cambio |
| §2 | Governance as Code | Sin cambio |
| §3 | Platform Agnosticism | Añade MCP como extensión |
| §4 | **Validation Gates en Cada Fase** | RENOMBRADO (era: Calidad Fractal) |
| §5 | Heutagogía sobre Dependencia | Sin cambio |
| §6 | Mejora Continua (Kaizen) | Sin cambio |
| §7 | Lean Software Development | Sin cambio |
| §8 | **Observable Workflow** | NUEVO |

#### ADRs v2.0
| ADR | Estado | Descripción |
|-----|--------|-------------|
| ADR-001 | ✅ Accepted | Python para CLI |
| ADR-002 | ✅ Accepted | Git como API |
| ADR-003 | ✅ Accepted | MCP como protocolo (promovido a CORE) |
| ADR-004 | ✅ Accepted | Markdown/JSON duality |
| ADR-005 | ✅ Accepted | Local-first |
| ADR-006 | ⚠️ Superseded | ~~DoD fractales~~ → ADR-006a |
| ADR-006a | ✅ Accepted | **Validation Gates por fase** |
| ADR-007 | ✅ Accepted | **Guardrails over Rules** |
| ADR-008 | ✅ Accepted | **Observable Workflow local** |

#### Jerarquías Ontológicas v2.0

**Jerarquía de Governance:**
```
Constitution (Principios inmutables)
    ↓
Guardrails (Directivas operacionales)
    ↓
Specs (Contratos de implementación)
    ↓
Validation Gates (Puntos de control)
```

**Jerarquía de Katas:**
```
L0 (Meta) → L1 (Proceso) → L2 (Componentes) → L3 (Técnico)
```

**Los 8 Validation Gates Estándar:**
```
Gate-Context → Gate-Discovery → Gate-Vision → Gate-Design →
Gate-Backlog → Gate-Plan → Gate-Code → Gate-Deploy
```

**Los 4 Pilares Filosóficos:**
```
Heutagogía + Jidoka + JIT Learning + Observable Workflow
```

---

## Instrucciones de Ejecución

### Paso 1: Carga de Documentos
Lee todos los 22 documentos v2.0 del proyecto. Usa el tool `view` para cada archivo.

### Paso 2: Ejecuta las 5 Dimensiones de Validación

#### Dimensión 1: CONSISTENCY CHECK (Terminología)
**Objetivo:** Verificar que NO existan términos v1.0 mezclados con v2.0.

**Algoritmo:**
1. Buscar ocurrencias de términos obsoletos en TODOS los documentos:
   - "DoD" (excepto en contexto histórico/changelog)
   - "DoD Fractal" o "DoD fractales"
   - "Definition of Done" (excepto en explicaciones de migración)
   - "raise-rules.json" (debe ser guardrails.json)
   - "Rule" como sustantivo principal (no como alias documentado)

2. Verificar uso consistente de términos canónicos:
   - "Validation Gate" (no "gate" genérico sin contexto)
   - "Guardrail" (no "rule" excepto como alias)
   - "Orquestador" (no "developer" cuando se refiere al rol RaiSE)
   - "Context Engineering" (no "prompt engineering" en contexto RaiSE)

**Output esperado:**
```markdown
### Dimensión 1: Consistency Check

| Documento | Término Obsoleto | Línea/Contexto | Severidad |
|-----------|------------------|----------------|-----------|
| [archivo] | [término]        | [contexto]     | 🔴/🟡/🟢   |

**Resumen:** X inconsistencias encontradas
- 🔴 Críticas: N
- 🟡 Menores: N
- 🟢 Aceptables (contexto histórico): N
```

#### Dimensión 2: REFERENCE INTEGRITY (Links Cruzados)
**Objetivo:** Verificar que todas las referencias entre documentos sean válidas.

**Algoritmo:**
1. Extraer todos los links internos (formato `[texto](./archivo.md)`)
2. Verificar que el archivo destino existe
3. Verificar que las secciones referenciadas existen (ej. `#user-personas`)
4. Verificar referencias a ADRs (ADR-001 a ADR-008)
5. Verificar referencias a principios constitucionales (§1 a §8)

**Output esperado:**
```markdown
### Dimensión 2: Reference Integrity

| Documento Origen | Referencia | Destino | Estado |
|------------------|------------|---------|--------|
| [archivo]        | [link]     | [dest]  | ✅/❌   |

**Resumen:**
- Links válidos: N
- Links rotos: N
- ADRs referenciados correctamente: N/8
- Principios § referenciados: N/8
```

#### Dimensión 3: HIERARCHY VALIDATION (Ontología)
**Objetivo:** Confirmar que las jerarquías sean consistentes en todos los documentos.

**Algoritmo:**
1. Verificar jerarquía de Governance en docs que la mencionan:
   - Constitution → Guardrails → Specs → Validation Gates
   - NO debe aparecer: Constitution → Rules → ...

2. Verificar jerarquía de Katas:
   - L0 → L1 → L2 → L3
   - Ejemplos deben usar niveles correctos

3. Verificar los 8 Validation Gates estándar:
   - Nombres consistentes (Gate-Context, Gate-Discovery, etc.)
   - Orden consistente cuando se listan

4. Verificar los 4 Pilares Filosóficos en Learning Philosophy:
   - Heutagogía, Jidoka, JIT Learning, Observable Workflow
   - NO debe ser solo 3 pilares (v1.0)

**Output esperado:**
```markdown
### Dimensión 3: Hierarchy Validation

| Jerarquía | Documento | Consistente | Notas |
|-----------|-----------|-------------|-------|
| Governance| [archivo] | ✅/❌        | [nota]|
| Katas     | [archivo] | ✅/❌        | [nota]|
| Gates     | [archivo] | ✅/❌        | [nota]|
| Pilares   | [archivo] | ✅/❌        | [nota]|

**Resumen:** X de Y jerarquías consistentes
```

#### Dimensión 4: COMPLETENESS AUDIT (Cobertura v2.0)
**Objetivo:** Verificar que conceptos nuevos v2.0 aparezcan donde corresponde.

**Algoritmo:**
1. **Observable Workflow** debe aparecer en:
   - ✅ 00-constitution-v2.md (§8)
   - ✅ 05-learning-philosophy-v2.md (cuarto pilar)
   - ✅ 15-tech-stack-v2.md (MELT stack)
   - ✅ 23-commands-reference-v2.md (raise audit)
   - ✅ 20-glossary-v2.md (definición)

2. **raise-mcp como CORE** debe aparecer en:
   - ✅ 10-system-architecture-v2.md (componente CORE)
   - ✅ 15-tech-stack-v2.md (stack MCP)
   - ✅ 30-roadmap-v2.md (v0.2, no v0.3)
   - ✅ 23-commands-reference-v2.md (raise mcp commands)

3. **Escalation Gate** debe aparecer en:
   - ✅ 20-glossary-v2.md (definición)
   - ✅ 21-methodology-v2.md (flujo)
   - ✅ 24-examples-library-v2.md (ejemplo)

4. **ADR-006a, ADR-007, ADR-008** deben estar en:
   - ✅ 14-adr-index-v2.md (documentados)
   - Referenciados donde corresponda

**Output esperado:**
```markdown
### Dimensión 4: Completeness Audit

| Concepto v2.0 | Documento Esperado | Presente | Ubicación |
|---------------|-------------------|----------|-----------|
| Observable Workflow | constitution | ✅/❌ | §8 |
| Observable Workflow | learning-philosophy | ✅/❌ | Pilar 4 |
| ... | ... | ... | ... |

**Resumen:**
- Cobertura Observable Workflow: N/5
- Cobertura raise-mcp CORE: N/4
- Cobertura Escalation Gate: N/3
- Cobertura ADRs v2.0: N/3
```

#### Dimensión 5: LEAN WASTE CHECK (Muda)
**Objetivo:** Identificar redundancias, inconsistencias o información que genera confusión.

**Algoritmo:**
1. **Redundancia:** ¿Hay definiciones duplicadas que podrían divergir?
2. **Inconsistencia:** ¿Hay afirmaciones contradictorias entre documentos?
3. **Obsolescencia:** ¿Hay contenido v1.0 que debería haberse eliminado?
4. **Ambigüedad:** ¿Hay términos usados sin definición clara?

**Tipos de Muda a detectar:**
- **Muda de Defectos:** Información incorrecta
- **Muda de Sobreproducción:** Contenido redundante
- **Muda de Espera:** Referencias a features "futuras" que ya existen
- **Muda de Movimiento:** Información en lugar incorrecto

**Output esperado:**
```markdown
### Dimensión 5: Lean Waste Check

| Tipo Muda | Documento | Descripción | Recomendación |
|-----------|-----------|-------------|---------------|
| Defectos  | [archivo] | [desc]      | [acción]      |
| Redundancia| [archivo]| [desc]      | [acción]      |
| ...       | ...       | ...         | ...           |

**Resumen:**
- Muda de Defectos: N instancias
- Muda de Sobreproducción: N instancias
- Muda de Espera: N instancias
- Muda de Movimiento: N instancias
```

---

### Paso 3: Genera Reporte Consolidado

**Formato del Reporte Final:**

```markdown
# Reporte de Validación Ontológica - RaiSE Corpus v2.0

**Fecha:** [fecha de ejecución]
**Ejecutado por:** RaiSE Ontology Architect
**Documentos analizados:** 22

---

## Resumen Ejecutivo

| Dimensión | Estado | Hallazgos |
|-----------|--------|-----------|
| 1. Consistency | 🟢/🟡/🔴 | N issues |
| 2. Reference Integrity | 🟢/🟡/🔴 | N issues |
| 3. Hierarchy Validation | 🟢/🟡/🔴 | N issues |
| 4. Completeness | 🟢/🟡/🔴 | N issues |
| 5. Lean Waste | 🟢/🟡/🔴 | N issues |

**Veredicto General:** [PASS / PASS CON OBSERVACIONES / FAIL]

---

## Hallazgos Detallados

[Incluir output de cada dimensión]

---

## Acciones Recomendadas

### Críticas (Bloquean release)
1. [Acción]

### Importantes (Deben resolverse)
1. [Acción]

### Menores (Nice to have)
1. [Acción]

---

## Métricas de Calidad Ontológica

| Métrica | Valor | Objetivo | Estado |
|---------|-------|----------|--------|
| Consistencia terminológica | X% | >95% | 🟢/🔴 |
| Integridad de referencias | X% | 100% | 🟢/🔴 |
| Cobertura conceptos v2.0 | X% | 100% | 🟢/🔴 |
| Índice de Muda | X | <5 | 🟢/🔴 |

---

## Changelog de Validación

| Versión | Fecha | Resultado |
|---------|-------|-----------|
| v2.0.0 | [fecha] | [resultado] |
```

---

## Criterios de Éxito

### PASS
- 0 inconsistencias críticas de terminología
- 100% de referencias válidas
- 100% de jerarquías consistentes
- >90% de cobertura de conceptos v2.0
- <5 instancias de Muda

### PASS CON OBSERVACIONES
- 0 inconsistencias críticas
- >95% de referencias válidas
- >90% de jerarquías consistentes
- >80% de cobertura
- <10 instancias de Muda

### FAIL
- Cualquier inconsistencia crítica de terminología
- <95% de referencias válidas
- <90% de jerarquías consistentes
- <80% de cobertura
- >10 instancias de Muda

---

## Notas de Implementación

1. **Usa bash para búsquedas:** `grep -r "término" /mnt/project/*-v2.md`
2. **Documenta contexto:** Si un término obsoleto aparece en changelog o explicación de migración, es ACEPTABLE
3. **Sé exhaustivo:** Lee cada documento completo, no solo busques términos
4. **Prioriza hallazgos:** No todos los issues tienen la misma severidad

---

*Este Kata es parte del sistema de calidad RaiSE. Su ejecución garantiza integridad epistemológica del corpus.*
```

---

## Metadata del Kata

| Campo | Valor |
|-------|-------|
| **ID** | L0-VAL-001 |
| **Nivel** | L0 (Meta-Kata) |
| **Inputs** | 22 documentos v2.0 del corpus |
| **Outputs** | Reporte de Validación Ontológica |
| **Validation Gate** | Gate-Quality |
| **Tiempo estimado** | 15-30 minutos |
| **Frecuencia** | Post-migración mayor, pre-release |

---

## Historial de Ejecuciones

| Fecha | Versión Corpus | Resultado | Ejecutor |
|-------|----------------|-----------|----------|
| [pendiente] | v2.0.0 | [pendiente] | [pendiente] |

---

*Kata creado el 28 de Diciembre, 2025 como parte de la migración ontológica v2.0*
