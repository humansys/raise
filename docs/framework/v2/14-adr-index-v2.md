# Architecture Decision Records
## Índice de Decisiones Arquitectónicas

**Versión:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Documentar decisiones arquitectónicas del proyecto RaiSE.

> **Nota de versión 2.0:** Esta versión incorpora decisiones de alineamiento ontológico con la industria (MCP, HITL patterns, MELT framework) basado en investigación de diciembre 2025.

---

## Índice de ADRs

| ID | Título | Estado | Fecha |
|----|--------|--------|-------|
| ADR-001 | Usar Python para CLI | ✅ Accepted | 2025-12-26 |
| ADR-002 | Git como API de distribución | ✅ Accepted | 2025-12-26 |
| ADR-003 | MCP como protocolo de contexto | ✅ Accepted | 2025-12-26 |
| ADR-004 | Markdown para humanos, JSON para máquinas | ✅ Accepted | 2025-12-26 |
| ADR-005 | Local-first architecture | ✅ Accepted | 2025-12-26 |
| ADR-006 | ~~DoD fractales por fase~~ | ⚠️ Superseded by ADR-006a | 2025-12-26 |
| ADR-006a | Validation Gates por fase | ✅ Accepted | 2025-12-28 |
| ADR-007 | Guardrails over Rules | ✅ Accepted | 2025-12-28 |
| ADR-008 | Observable Workflow local | ✅ Accepted | 2025-12-28 |

---

## Template ADR

```markdown
## ADR-XXX: [Título]

### Estado
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

### Fecha
YYYY-MM-DD

### Contexto
[Situación que requirió la decisión]

### Decisión
[Lo que decidimos hacer]

### Consecuencias
**Positivas:**
- [Beneficio 1]

**Negativas:**
- [Trade-off 1]

**Neutras:**
- [Implicación neutral]

### Alternativas Consideradas
1. [Alternativa] - [Por qué no]
```

---

## ADR-001: Usar Python para CLI

### Estado
✅ Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos elegir un lenguaje para implementar raise-kit (CLI). Los criterios principales son:
- Ecosistema AI/ML maduro
- Facilidad de extensión
- Distribución cross-platform
- Velocidad de desarrollo

### Decisión
Usar **Python 3.11+** como lenguaje principal para raise-kit.

### Consecuencias

**Positivas:**
- Ecosistema AI/ML excelente (integración con libs existentes)
- Desarrollo rápido (scripts a producción)
- Comunidad amplia (contributors potenciales)
- Click + Rich = UX de CLI excelente

**Negativas:**
- Requiere Python runtime en máquina target
- Performance inferior a Go/Rust para operaciones IO-bound
- Distribución como binario requiere PyInstaller

**Neutras:**
- Typing opcional (usamos strict con mypy)

### Alternativas Consideradas

1. **Go** - Binarios estáticos, performance. Rechazado por: ecosistema AI menos maduro, desarrollo más lento.
2. **Rust** - Performance máximo. Rechazado por: curva de aprendizaje, overhead para MVP.
3. **TypeScript/Node** - Web-native. Rechazado por: dependency hell, menos afinidad con ML.

---

## ADR-002: Git como API de Distribución

### Estado
✅ Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos distribuir guardrails, katas y templates desde raise-config a proyectos individuales. Opciones:
- NPM/PyPI registry
- API REST propietaria
- Git protocol directo

### Decisión
Usar **Git protocol** (clone/pull) para distribuir contenido de raise-config.

### Consecuencias

**Positivas:**
- Platform agnostic (funciona con cualquier Git host)
- Versionado nativo (branches, tags)
- Sin infraestructura adicional
- Funciona offline después de clone inicial
- Auditoría via Git history

**Negativas:**
- No hay auto-update (requiere `raise hydrate` manual)
- Clone inicial puede ser lento para repos grandes
- No hay analytics de uso centralizado

**Neutras:**
- Requiere Git instalado (ubicuo en dev environments)

### Alternativas Consideradas

1. **NPM/PyPI** - Familiar para devs. Rechazado por: otra dependencia externa, versionado menos flexible.
2. **REST API** - Updates en tiempo real. Rechazado por: requiere infraestructura, vendor lock-in potencial.

---

## ADR-003: MCP como Protocolo de Contexto

### Estado
✅ Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos servir contexto estructurado a agentes AI. Opciones:
- Custom API REST
- Language Server Protocol (LSP)
- Model Context Protocol (MCP)

### Decisión
Usar **MCP (Model Context Protocol)** de Anthropic para servir contexto. En v2.0, raise-mcp se promueve a **componente CORE** del framework.

### Consecuencias

**Positivas:**
- Estándar de facto con 11,000+ servers registrados
- Soporte nativo en Claude, Cursor, Windsurf
- Extensible (Resources + Tools + Prompts + Sampling)
- Comunidad enterprise activa
- Primitivos bien definidos para Context Engineering

**Negativas:**
- Requiere agente MCP-compatible
- Dependencia de evolución del protocolo

**Neutras:**
- Fallback disponible a `.cursorrules` / `.claude.md` para agentes legacy

### Alternativas Consideradas

1. **Custom REST** - Control total. Rechazado por: reinventar la rueda, sin soporte nativo en agentes.
2. **LSP** - Estándar maduro de IDEs. Rechazado por: diseñado para code intelligence, no para contexto AI.

---

## ADR-004: Markdown para Humanos, JSON para Máquinas

### Estado
✅ Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos formatos para guardrails, specs y configuración. Debate entre legibilidad humana y parseo por máquinas.

### Decisión
- **Markdown** para documentos que humanos leen/editan (specs, constitution, plans)
- **JSON** para datos que máquinas consumen (guardrails.json, config)
- **YAML** para configuración human-editable (raise.yaml, agent specs)
- **MDC** para guardrails (Markdown + frontmatter YAML)
- **JSONL** para traces de Observable Workflow [NUEVO v2.0]

### Consecuencias

**Positivas:**
- Mejor experiencia para cada audiencia
- Markdown es diff-friendly en PRs
- JSON es parse-fast para runtime
- JSONL es append-only, ideal para logs
- Conversión automática posible

**Negativas:**
- Múltiples formatos para aprender
- Necesidad de tooling de conversión

**Neutras:**
- Frontmatter YAML en Markdown es patrón establecido

### Alternativas Consideradas

1. **Solo YAML** - Un formato. Rechazado por: verboso para documentos largos, menos readable.
2. **Solo JSON** - Un formato. Rechazado por: ilegible para humanos, no soporta comentarios.

---

## ADR-005: Local-First Architecture

### Estado
✅ Accepted

### Fecha
2025-12-26

### Contexto
Decisión sobre dónde procesar datos y servir contexto. Cloud vs local.

### Decisión
Arquitectura **local-first**: todo el procesamiento ocurre en la máquina del desarrollador. No hay backend cloud de RaiSE.

### Consecuencias

**Positivas:**
- Privacidad total (código nunca sale)
- Funciona offline
- No hay costos de infraestructura
- Cumplimiento de data residency automático
- Observable Workflow auditable localmente [NUEVO v2.0]

**Negativas:**
- No hay analytics centralizados
- Features colaborativas limitadas
- Sin sync automático entre máquinas

**Neutras:**
- Cada developer es responsable de su ambiente

### Alternativas Consideradas

1. **Cloud-first SaaS** - Features centralizados. Rechazado por: privacidad concerns, vendor lock-in, costos.
2. **Hybrid** - Local + optional cloud. Rechazado por: complejidad, confusión de modelo.

---

## ADR-006: DoD Fractales por Fase

### Estado
⚠️ Superseded by ADR-006a

### Fecha
2025-12-26

### Contexto
¿Cómo estructurar quality gates en el flujo de desarrollo?

### Decisión
~~Implementar **DoD (Definition of Done) fractal**: cada fase del flujo tiene su propio DoD que debe cumplirse antes de avanzar.~~

> **BREAKING CHANGE v2.0:** Este ADR ha sido supersedido por ADR-006a. El concepto de "DoD Fractal" se renombra a "Validation Gate" para alineamiento con terminología HITL estándar de la industria. La semántica se preserva; cambia solo la nomenclatura.

### Migración
- Término "DoD" → "Validation Gate"
- Término "DoD Fractal" → "Validation Gates por fase"
- Ver ADR-006a para definición actualizada

---

## ADR-006a: Validation Gates por Fase [NUEVO v2.0]

### Estado
✅ Accepted

### Fecha
2025-12-28

### Contexto
El concepto de "DoD Fractal" (ADR-006) era semánticamente correcto pero terminológicamente aislado. La investigación de ontologías Agentic AI (diciembre 2025) reveló que:
- La industria usa "Quality Gates", "Approval Gates", "Checkpoints"
- El patrón HITL (Human-in-the-Loop) es el estándar para puntos de control humano
- LangGraph usa "Conditional Edges" y "Checkpoints"
- Lean Manufacturing usa "Quality Gates" y "Pull boundaries"

### Decisión
Renombrar **DoD Fractal** a **Validation Gate**. Cada fase del flujo de valor tiene su propio Validation Gate con criterios específicos que deben pasarse antes de avanzar.

**Estructura de Validation Gates:**

| Gate | Criterio de Paso | Fase |
|------|------------------|------|
| Gate-Context | Stakeholders y restricciones claras | Discovery |
| Gate-Discovery | PRD validado | Discovery |
| Gate-Vision | Solution Vision aprobada | Vision |
| Gate-Design | Tech Design completo | Design |
| Gate-Backlog | HUs priorizadas | Planning |
| Gate-Plan | Implementation Plan verificado | Planning |
| Gate-Code | Código que pasa validaciones | Implementation |
| Gate-Deploy | Feature en producción | Deployment |

**Implementación MCP:**
```json
{
  "tool": "validate_gate",
  "parameters": {
    "gate": "Gate-Design",
    "artifact": "spec.md"
  }
}
```

### Consecuencias

**Positivas:**
- Terminología alineada con industria (HITL patterns)
- Interoperabilidad conceptual con LangGraph, CrewAI
- Onboarding más rápido (devs reconocen "gates")
- Mantiene semántica fractal (gates a múltiples niveles)
- Escalation Gates como subtipo natural

**Negativas:**
- Migración de documentación existente
- Posible confusión temporal con terminología legacy

**Neutras:**
- El concepto subyacente no cambia

### Alternativas Consideradas

1. **Mantener "DoD Fractal"** - Diferenciador único. Rechazado por: aislamiento terminológico, fricción de adopción.
2. **"Quality Gate"** - Más genérico. Rechazado por: menos específico que "Validation Gate" para contexto AI.
3. **"Checkpoint"** - LangGraph terminology. Rechazado por: conflicto potencial con Git checkpoints.

---

## ADR-007: Guardrails over Rules [NUEVO v2.0]

### Estado
✅ Accepted

### Fecha
2025-12-28

### Contexto
El término "Rule" (usado en v1.x) es semánticamente correcto pero:
- Es genérico y ambiguo (¿business rule? ¿lint rule? ¿coding rule?)
- No connota protección activa
- La industria enterprise AI converge en "Guardrail" (DSPy, LangChain, NVIDIA NeMo)

### Decisión
Renombrar **Rule** a **Guardrail** como término principal para directivas operacionales que gobiernan comportamiento de agentes y calidad de código.

**Jerarquía de Governance actualizada:**
```
Constitution (Principios inmutables)
    ↓
Guardrails (Directivas operacionales)
    ↓
Specs (Contratos de implementación)
    ↓
Validation Gates (Puntos de control)
```

**Diferenciación clave:**

| Aspecto | Constitution | Guardrail |
|---------|--------------|-----------|
| Mutabilidad | Casi nunca cambia | Cambia por proyecto/fase |
| Nivel | Filosófico | Operacional |
| Enforcement | Cultural | Automatizable |
| Ejemplo | "Humanos definen, máquinas ejecutan" | "Máximo 500 líneas por archivo" |

**Mapeo MCP:**
```json
{
  "resource": "raise://guardrails",
  "content": {
    "guardrails": [
      {"id": "GR-001", "scope": "code", "rule": "..."}
    ]
  }
}
```

### Consecuencias

**Positivas:**
- Alineamiento con terminología enterprise AI
- Connota protección activa (vs. "rule" pasivo)
- Diferenciación clara con Constitution
- Compatible con DSPy Assertions pattern

**Negativas:**
- Migración de archivos `raise-rules.json` → `guardrails.json`
- Actualización de documentación

**Neutras:**
- "Rule" permanece como alias válido en CLI (`raise rule` = `raise guardrail`)

### Alternativas Consideradas

1. **Mantener "Rule"** - Simple. Rechazado por: ambigüedad, no connota protección.
2. **"Constraint"** - Técnicamente preciso. Rechazado por: menos intuitivo, suena restrictivo.
3. **"Policy"** - Enterprise-friendly. Rechazado por: conflicto potencial con security policies.

---

## ADR-008: Observable Workflow Local [NUEVO v2.0]

### Estado
✅ Accepted

### Fecha
2025-12-28

### Contexto
Para auditar y mejorar interacciones con agentes AI, necesitamos trazabilidad. Opciones:
- Cloud telemetry (DataDog, New Relic)
- OpenTelemetry exporters
- Logs locales estructurados

La investigación reveló:
- MELT framework (Metrics, Events, Logs, Traces) es el estándar de observabilidad
- OpenTelemetry es vendor-neutral y ubicuo
- Local-first es principio core de RaiSE (ADR-005)
- EU AI Act requiere trazabilidad de decisiones AI

### Decisión
Implementar **Observable Workflow** con almacenamiento local:
- Formato: **JSONL** (JSON Lines) para append-only efficiency
- Ubicación: `.raise/traces/YYYY-MM-DD.jsonl`
- Retención: Configurable, default 30 días
- Acceso: CLI (`raise audit`) y recursos MCP

**Schema de trace:**
```json
{
  "timestamp": "2025-12-28T10:30:00Z",
  "session_id": "sess_abc123",
  "gate": "Gate-Design",
  "action": "validate_gate",
  "agent": "claude-3.5-sonnet",
  "input_tokens": 1500,
  "output_tokens": 800,
  "result": "passed",
  "escalated": false,
  "context_resources": ["raise://constitution", "raise://guardrails"],
  "duration_ms": 2340
}
```

**Principio Observable by Default:**
Cada interacción MCP genera trace automáticamente. El Orquestador puede:
1. Auditar sesiones: `raise audit --session today`
2. Medir métricas: `raise metrics --week`
3. Exportar para análisis: `raise export --format csv`

### Consecuencias

**Positivas:**
- Cumplimiento EU AI Act (trazabilidad de decisiones)
- Mejora continua basada en datos (Kaizen)
- Privacy by design (datos locales)
- Sin costos de telemetría cloud
- Compatible con OpenTelemetry si se desea exportar

**Negativas:**
- Storage local crece con uso
- No hay dashboard cloud out-of-box
- Análisis cross-team requiere export manual

**Neutras:**
- Overhead mínimo (<5ms por trace)

### Alternativas Consideradas

1. **Cloud telemetry** - Dashboards ricos. Rechazado por: viola ADR-005 (local-first), costos, privacy.
2. **OpenTelemetry directo** - Estándar. Rechazado como primario por: overkill para uso individual, pero compatible como export target.
3. **Sin observabilidad** - Simple. Rechazado por: imposibilita mejora basada en datos, no cumple EU AI Act.

---

## Changelog

### v2.0.0 (2025-12-28)

#### ⚠️ BREAKING CHANGES
- **ADR-006 Superseded**: "DoD Fractales por Fase" → ADR-006a "Validation Gates por Fase"
  - Migración: Reemplazar "DoD" por "Validation Gate" en toda documentación
  - Archivos afectados: specs, katas, configuration
- **ADR-007 Nuevo**: "Rule" → "Guardrail"
  - Migración: `raise-rules.json` → `guardrails.json`
  - CLI: `raise rule` permanece como alias de `raise guardrail`

#### ✨ Nuevos ADRs
- **ADR-006a**: Validation Gates por Fase (reemplazo de ADR-006)
- **ADR-007**: Guardrails over Rules
- **ADR-008**: Observable Workflow Local

#### 📝 Actualizaciones
- **ADR-003**: raise-mcp promovido a componente CORE
- **ADR-004**: Añadido JSONL para traces
- **ADR-005**: Añadida nota sobre Observable Workflow

#### 🔄 Política de Migración
Los términos legacy permanecen válidos como aliases:
- `rule` → `guardrail` ✅
- `DoD` → `Validation Gate` ✅
- `raise-rules.json` → `guardrails.json` ⚠️ (deprecated, migrar antes de v3.0)

### v1.0.0 (2025-12-27)
- Release inicial con ADR-001 a ADR-006

---

## Referencias Cruzadas

| Documento | ADRs Relevantes |
|-----------|-----------------|
| [10-system-architecture-v2.md](./10-system-architecture-v2.md) | ADR-003, ADR-005, ADR-006a, ADR-008 |
| [11-data-architecture-v2.md](./11-data-architecture-v2.md) | ADR-004, ADR-008 |
| [12-integration-patterns-v2.md](./12-integration-patterns-v2.md) | ADR-003 |
| [13-security-compliance-v2.md](./13-security-compliance-v2.md) | ADR-005, ADR-008 |
| [20-glossary-v2.md](./20-glossary-v2.md) | ADR-006a, ADR-007 |

---

*Agregar nuevo ADR al final. Mantener índice actualizado. Cada ADR supersedido debe referenciar su reemplazo.*
