---
id: "TEC-RAISE-F1.2"
title: "Tech Design: raise.feature.stories Command"
version: "1.0"
date: "2026-01-28"
status: "Draft"
feature_ref: "F1.2"
backlog_ref: "raise-v2-feature-commands"
template: "lean-spec-v1"
---

# Tech Design: raise.feature.stories Command

> **Feature**: F1.2 - Comando para generar User Stories desde Feature Tech Design
> **Epic**: E1 - Feature-Level Commands para RaiSE v2

## 1. Approach

**Qué hace este feature**:
Genera User Stories estructuradas a partir de un Feature Tech Design, descomponiendo el approach técnico en unidades de trabajo implementables con criterios de aceptación claros.

**Cómo lo implementamos**:
Comando Markdown (`.raise/commands/03-feature/raise.feature.stories.md`) que lee el tech-design del feature, extrae componentes afectados y contratos, y genera stories siguiendo el formato "Como [rol], quiero [acción], para [beneficio]" con acceptance criteria técnicos.

**Componentes afectados**:
- `.raise/commands/03-feature/raise.feature.stories.md`: Nuevo comando
- `.claude/commands/03-feature/raise.feature.stories.md`: Copia para Claude Code
- `.raise/templates/feature/user-story.md`: Template de User Story (si no existe, crear)
- `specs/features/{feature-id}/stories/`: Directorio de salida para stories generadas

---

## 2. Interfaz / Contrato

```yaml
# Comando: /raise.feature.stories
input:
  - feature_id: string       # ID del feature (e.g., "F1.2", "raise-feature-stories")
  - tech_design_path: string # Path al tech-design.md (auto-detectado si no se provee)

output:
  - stories_dir: "specs/features/{feature-id}/stories/"
  - files:
    - "US-001-{slug}.md"     # Una story por archivo
    - "US-002-{slug}.md"
    - "index.md"             # Índice con lista de stories y estado

handoffs:
  - next: "/raise.feature.plan"
    prompt: "Create implementation plan from these user stories"
```

**Ejemplo de uso**:
```bash
# Desde feature con tech-design existente
/raise.feature.stories raise-feature-stories

# Con path explícito
/raise.feature.stories --tech-design specs/features/raise-feature-stories/tech-design.md
```

**Output esperado** (ejemplo de una story):
```markdown
---
id: US-001
title: "Parsear Tech Design para extraer componentes"
feature_ref: F1.2
status: draft
priority: P1
estimate: S  # S/M/L
---

# US-001: Parsear Tech Design para extraer componentes

**Como** desarrollador del framework RaiSE,
**Quiero** que el comando extraiga automáticamente los componentes del tech-design,
**Para** generar stories alineadas con la arquitectura definida.

## Acceptance Criteria

- [ ] Lee frontmatter YAML del tech-design
- [ ] Extrae lista de "Componentes afectados"
- [ ] Identifica contratos/interfaces definidos
- [ ] Genera al menos 1 story por componente nuevo

## Technical Notes

- Input: `specs/features/{id}/tech-design.md`
- Parser: YAML frontmatter + Markdown sections
- Output: `specs/features/{id}/stories/US-001-*.md`
```

---

## 3. Consideraciones

| Aspecto | Decisión | Rationale |
|---------|----------|-----------|
| Granularidad de stories | 1 story por componente nuevo + 1 por modificación significativa | Balance entre atomicidad y overhead de gestión |
| Formato de archivos | Un archivo .md por story | Facilita tracking individual en Git y revisión de PRs |
| Estimación | Solo sizing (S/M/L), no horas | Alineado con metodología ágil, evita falsa precisión |
| Priorización | P1/P2/P3 basado en dependencias técnicas | Stories bloqueantes van primero |
| IDs de stories | Secuenciales por feature (US-001, US-002...) | Simple, predecible, ordenable |

**Riesgos identificados**:
- [ ] Tech Design incompleto puede generar stories vagas → Mitigación: Jidoka block si faltan secciones requeridas
- [ ] Over-decomposition en muchas stories pequeñas → Mitigación: Límite sugerido de 3-7 stories por feature
- [ ] Stories sin criterios de aceptación verificables → Mitigación: Template fuerza AC con checkboxes

---

<details>
<summary><h2>Algoritmo / Lógica</h2></summary>

```
1. LOAD tech-design.md from specs/features/{feature-id}/
2. PARSE frontmatter → extract feature metadata
3. PARSE section "Componentes afectados" → list of components

4. FOR each component:
   a. IF component.action == "nuevo":
      - CREATE story: "Implementar {component.name}"
      - PRIORITY: P1 if no dependencies, P2 otherwise
   b. IF component.action == "modificar":
      - CREATE story: "Modificar {component.name} para {change}"
      - PRIORITY: P2

5. PARSE section "Interfaz / Contrato":
   - CREATE story: "Implementar contrato de {interface}"
   - ADD acceptance criteria from contract definition

6. PARSE section "Consideraciones":
   - FOR each risk with mitigation:
     - ADD technical note to relevant story

7. GENERATE index.md with:
   - Table: ID | Title | Priority | Status | Estimate
   - Dependency graph (if applicable)

8. VALIDATE:
   - Each story has >= 2 acceptance criteria
   - No circular dependencies
   - Total stories between 3-7 (warn if outside)
```

</details>

<details>
<summary><h2>Testing Approach</h2></summary>

| Tipo | Qué cubre |
|------|-----------|
| Manual | Ejecutar comando con tech-design de raise.feature.stories y verificar stories generadas |
| Validation | Stories generadas pasan gate-stories.md |

**Casos de prueba**:
1. Tech Design completo → Genera 3-7 stories
2. Tech Design sin "Componentes afectados" → Jidoka: solicita completar sección
3. Tech Design con 10+ componentes → Warning: considerar dividir feature

</details>
