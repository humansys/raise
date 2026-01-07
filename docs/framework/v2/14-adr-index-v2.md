# Architecture Decision Records
## Ãndice de Decisiones ArquitectÃ³nicas

**VersiÃ³n:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**PropÃ³sito:** Documentar decisiones arquitectÃ³nicas del proyecto RaiSE.

> **Nota de versiÃ³n 2.0:** Esta versiÃ³n incorpora decisiones de alineamiento ontolÃ³gico con la industria (MCP, HITL patterns, MELT framework) basado en investigaciÃ³n de diciembre 2025.

---

## Ãndice de ADRs

| ID | TÃ­tulo | Estado | Fecha |
|----|--------|--------|-------|
| ADR-001 | Usar Python para CLI | âœ… Accepted | 2025-12-26 |
| ADR-002 | Git como API de distribuciÃ³n | âœ… Accepted | 2025-12-26 |
| ADR-003 | MCP como protocolo de contexto | âœ… Accepted | 2025-12-26 |
| ADR-004 | Markdown para humanos, JSON para mÃ¡quinas | âœ… Accepted | 2025-12-26 |
| ADR-005 | Local-first architecture | âœ… Accepted | 2025-12-26 |
| ADR-006 | ~~DoD fractales por fase~~ | âš ï¸ Superseded by ADR-006a | 2025-12-26 |
| ADR-006a | Validation Gates por fase | âœ… Accepted | 2025-12-28 |
| ADR-007 | Guardrails over Rules | âœ… Accepted | 2025-12-28 |
| ADR-008 | Observable Workflow local | âœ… Accepted | 2025-12-28 |

---

## Template ADR

```markdown
## ADR-XXX: [TÃ­tulo]

### Estado
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

### Fecha
YYYY-MM-DD

### Contexto
[SituaciÃ³n que requiriÃ³ la decisiÃ³n]

### DecisiÃ³n
[Lo que decidimos hacer]

### Consecuencias
**Positivas:**
- [Beneficio 1]

**Negativas:**
- [Trade-off 1]

**Neutras:**
- [ImplicaciÃ³n neutral]

### Alternativas Consideradas
1. [Alternativa] - [Por quÃ© no]
```

---

## ADR-001: Usar Python para CLI

### Estado
âœ… Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos elegir un lenguaje para implementar raise-kit (CLI). Los criterios principales son:
- Ecosistema AI/ML maduro
- Facilidad de extensiÃ³n
- DistribuciÃ³n cross-platform
- Velocidad de desarrollo

### DecisiÃ³n
Usar **Python 3.11+** como lenguaje principal para raise-kit.

### Consecuencias

**Positivas:**
- Ecosistema AI/ML excelente (integraciÃ³n con libs existentes)
- Desarrollo rÃ¡pido (scripts a producciÃ³n)
- Comunidad amplia (contributors potenciales)
- Click + Rich = UX de CLI excelente

**Negativas:**
- Requiere Python runtime en mÃ¡quina target
- Performance inferior a Go/Rust para operaciones IO-bound
- DistribuciÃ³n como binario requiere PyInstaller

**Neutras:**
- Typing opcional (usamos strict con mypy)

### Alternativas Consideradas

1. **Go** - Binarios estÃ¡ticos, performance. Rechazado por: ecosistema AI menos maduro, desarrollo mÃ¡s lento.
2. **Rust** - Performance mÃ¡ximo. Rechazado por: curva de aprendizaje, overhead para MVP.
3. **TypeScript/Node** - Web-native. Rechazado por: dependency hell, menos afinidad con ML.

---

## ADR-002: Git como API de DistribuciÃ³n

### Estado
âœ… Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos distribuir guardrails, katas y templates desde raise-config a proyectos individuales. Opciones:
- NPM/PyPI registry
- API REST propietaria
- Git protocol directo

### DecisiÃ³n
Usar **Git protocol** (clone/pull) para distribuir contenido de raise-config.

### Consecuencias

**Positivas:**
- Platform agnostic (funciona con cualquier Git host)
- Versionado nativo (branches, tags)
- Sin infraestructura adicional
- Funciona offline despuÃ©s de clone inicial
- AuditorÃ­a via Git history

**Negativas:**
- No hay auto-update (requiere `raise pull` manual)
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
âœ… Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos servir contexto estructurado a agentes AI. Opciones:
- Custom API REST
- Language Server Protocol (LSP)
- Model Context Protocol (MCP)

### DecisiÃ³n
Usar **MCP (Model Context Protocol)** de Anthropic para servir contexto. En v2.0, raise-mcp se promueve a **componente CORE** del framework.

### Consecuencias

**Positivas:**
- EstÃ¡ndar de facto con 11,000+ servers registrados
- Soporte nativo en Claude, Cursor, Windsurf
- Extensible (Resources + Tools + Prompts + Sampling)
- Comunidad enterprise activa
- Primitivos bien definidos para Context Engineering

**Negativas:**
- Requiere agente MCP-compatible
- Dependencia de evoluciÃ³n del protocolo

**Neutras:**
- Fallback disponible a `.cursorrules` / `.claude.md` para agentes legacy

### Alternativas Consideradas

1. **Custom REST** - Control total. Rechazado por: reinventar la rueda, sin soporte nativo en agentes.
2. **LSP** - EstÃ¡ndar maduro de IDEs. Rechazado por: diseÃ±ado para code intelligence, no para contexto AI.

---

## ADR-004: Markdown para Humanos, JSON para MÃ¡quinas

### Estado
âœ… Accepted

### Fecha
2025-12-26

### Contexto
Necesitamos formatos para guardrails, specs y configuraciÃ³n. Debate entre legibilidad humana y parseo por mÃ¡quinas.

### DecisiÃ³n
- **Markdown** para documentos que humanos leen/editan (specs, constitution, plans)
- **JSON** para datos que mÃ¡quinas consumen (guardrails.json, config)
- **YAML** para configuraciÃ³n human-editable (raise.yaml, agent specs)
- **MDC** para guardrails (Markdown + frontmatter YAML)
- **JSONL** para traces de Observable Workflow [NUEVO v2.0]

### Consecuencias

**Positivas:**
- Mejor experiencia para cada audiencia
- Markdown es diff-friendly en PRs
- JSON es parse-fast para runtime
- JSONL es append-only, ideal para logs
- ConversiÃ³n automÃ¡tica posible

**Negativas:**
- MÃºltiples formatos para aprender
- Necesidad de tooling de conversiÃ³n

**Neutras:**
- Frontmatter YAML en Markdown es patrÃ³n establecido

### Alternativas Consideradas

1. **Solo YAML** - Un formato. Rechazado por: verboso para documentos largos, menos readable.
2. **Solo JSON** - Un formato. Rechazado por: ilegible para humanos, no soporta comentarios.

---

## ADR-005: Local-First Architecture

### Estado
âœ… Accepted

### Fecha
2025-12-26

### Contexto
DecisiÃ³n sobre dÃ³nde procesar datos y servir contexto. Cloud vs local.

### DecisiÃ³n
Arquitectura **local-first**: todo el procesamiento ocurre en la mÃ¡quina del desarrollador. No hay backend cloud de RaiSE.

### Consecuencias

**Positivas:**
- Privacidad total (cÃ³digo nunca sale)
- Funciona offline
- No hay costos de infraestructura
- Cumplimiento de data residency automÃ¡tico
- Observable Workflow auditable localmente [NUEVO v2.0]

**Negativas:**
- No hay analytics centralizados
- Features colaborativas limitadas
- Sin sync automÃ¡tico entre mÃ¡quinas

**Neutras:**
- Cada developer es responsable de su ambiente

### Alternativas Consideradas

1. **Cloud-first SaaS** - Features centralizados. Rechazado por: privacidad concerns, vendor lock-in, costos.
2. **Hybrid** - Local + optional cloud. Rechazado por: complejidad, confusiÃ³n de modelo.

---

## ADR-006: DoD Fractales por Fase

### Estado
âš ï¸ Superseded by ADR-006a

### Fecha
2025-12-26

### Contexto
Â¿CÃ³mo estructurar quality gates en el flujo de desarrollo?

### DecisiÃ³n
~~Implementar **DoD (Definition of Done) fractal**: cada fase del flujo tiene su propio DoD que debe cumplirse antes de avanzar.~~

> **BREAKING CHANGE v2.0:** Este ADR ha sido supersedido por ADR-006a. El concepto de "DoD Fractal" se renombra a "Validation Gate" para alineamiento con terminologÃ­a HITL estÃ¡ndar de la industria. La semÃ¡ntica se preserva; cambia solo la nomenclatura.

### MigraciÃ³n
- TÃ©rmino "DoD" â†’ "Validation Gate"
- TÃ©rmino "DoD Fractal" â†’ "Validation Gates por fase"
- Ver ADR-006a para definiciÃ³n actualizada

---

## ADR-006a: Validation Gates por Fase [NUEVO v2.0]

### Estado
âœ… Accepted

### Fecha
2025-12-28

### Contexto
El concepto de "DoD Fractal" (ADR-006) era semÃ¡nticamente correcto pero terminolÃ³gicamente aislado. La investigaciÃ³n de ontologÃ­as Agentic AI (diciembre 2025) revelÃ³ que:
- La industria usa "Quality Gates", "Approval Gates", "Checkpoints"
- El patrÃ³n HITL (Human-in-the-Loop) es el estÃ¡ndar para puntos de control humano
- LangGraph usa "Conditional Edges" y "Checkpoints"
- Lean Manufacturing usa "Quality Gates" y "Pull boundaries"

### DecisiÃ³n
Renombrar **DoD Fractal** a **Validation Gate**. Cada fase del flujo de valor tiene su propio Validation Gate con criterios especÃ­ficos que deben pasarse antes de avanzar.

**Estructura de Validation Gates:**

| Gate | Criterio de Paso | Fase |
|------|------------------|------|
| Gate-Context | Stakeholders y restricciones claras | Discovery |
| Gate-Discovery | PRD validado | Discovery |
| Gate-Vision | Solution Vision aprobada | Vision |
| Gate-Design | Tech Design completo | Design |
| Gate-Backlog | HUs priorizadas | Planning |
| Gate-Plan | Implementation Plan verificado | Planning |
| Gate-Code | CÃ³digo que pasa validaciones | Implementation |
| Gate-Deploy | Feature en producciÃ³n | Deployment |

**ImplementaciÃ³n MCP:**
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
- TerminologÃ­a alineada con industria (HITL patterns)
- Interoperabilidad conceptual con LangGraph, CrewAI
- Onboarding mÃ¡s rÃ¡pido (devs reconocen "gates")
- Mantiene semÃ¡ntica fractal (gates a mÃºltiples niveles)
- Escalation Gates como subtipo natural

**Negativas:**
- MigraciÃ³n de documentaciÃ³n existente
- Posible confusiÃ³n temporal con terminologÃ­a legacy

**Neutras:**
- El concepto subyacente no cambia

### Alternativas Consideradas

1. **Mantener "DoD Fractal"** - Diferenciador Ãºnico. Rechazado por: aislamiento terminolÃ³gico, fricciÃ³n de adopciÃ³n.
2. **"Quality Gate"** - MÃ¡s genÃ©rico. Rechazado por: menos especÃ­fico que "Validation Gate" para contexto AI.
3. **"Checkpoint"** - LangGraph terminology. Rechazado por: conflicto potencial con Git checkpoints.

---

## ADR-007: Guardrails over Rules [NUEVO v2.0]

### Estado
âœ… Accepted

### Fecha
2025-12-28

### Contexto
El tÃ©rmino "Rule" (usado en v1.x) es semÃ¡nticamente correcto pero:
- Es genÃ©rico y ambiguo (Â¿business rule? Â¿lint rule? Â¿coding rule?)
- No connota protecciÃ³n activa
- La industria enterprise AI converge en "Guardrail" (DSPy, LangChain, NVIDIA NeMo)

### DecisiÃ³n
Renombrar **Rule** a **Guardrail** como tÃ©rmino principal para directivas operacionales que gobiernan comportamiento de agentes y calidad de cÃ³digo.

**JerarquÃ­a de Governance actualizada:**
```
Constitution (Principios inmutables)
    â†“
Guardrails (Directivas operacionales)
    â†“
Specs (Contratos de implementaciÃ³n)
    â†“
Validation Gates (Puntos de control)
```

**DiferenciaciÃ³n clave:**

| Aspecto | Constitution | Guardrail |
|---------|--------------|-----------|
| Mutabilidad | Casi nunca cambia | Cambia por proyecto/fase |
| Nivel | FilosÃ³fico | Operacional |
| Enforcement | Cultural | Automatizable |
| Ejemplo | "Humanos definen, mÃ¡quinas ejecutan" | "MÃ¡ximo 500 lÃ­neas por archivo" |

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
- Alineamiento con terminologÃ­a enterprise AI
- Connota protecciÃ³n activa (vs. "rule" pasivo)
- DiferenciaciÃ³n clara con Constitution
- Compatible con DSPy Assertions pattern

**Negativas:**
- MigraciÃ³n de archivos `raise-rules.json` â†’ `guardrails.json`
- ActualizaciÃ³n de documentaciÃ³n

**Neutras:**
- "Rule" permanece como alias vÃ¡lido en CLI (`raise rule` = `raise guardrail`)

### Alternativas Consideradas

1. **Mantener "Rule"** - Simple. Rechazado por: ambigÃ¼edad, no connota protecciÃ³n.
2. **"Constraint"** - TÃ©cnicamente preciso. Rechazado por: menos intuitivo, suena restrictivo.
3. **"Policy"** - Enterprise-friendly. Rechazado por: conflicto potencial con security policies.

---

## ADR-008: Observable Workflow Local [NUEVO v2.0]

### Estado
âœ… Accepted

### Fecha
2025-12-28

### Contexto
Para auditar y mejorar interacciones con agentes AI, necesitamos trazabilidad. Opciones:
- Cloud telemetry (DataDog, New Relic)
- OpenTelemetry exporters
- Logs locales estructurados

La investigaciÃ³n revelÃ³:
- MELT framework (Metrics, Events, Logs, Traces) es el estÃ¡ndar de observabilidad
- OpenTelemetry es vendor-neutral y ubicuo
- Local-first es principio core de RaiSE (ADR-005)
- EU AI Act requiere trazabilidad de decisiones AI

### DecisiÃ³n
Implementar **Observable Workflow** con almacenamiento local:
- Formato: **JSONL** (JSON Lines) para append-only efficiency
- UbicaciÃ³n: `.raise/traces/YYYY-MM-DD.jsonl`
- RetenciÃ³n: Configurable, default 30 dÃ­as
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
Cada interacciÃ³n MCP genera trace automÃ¡ticamente. El Orquestador puede:
1. Auditar sesiones: `raise audit --session today`
2. Medir mÃ©tricas: `raise metrics --week`
3. Exportar para anÃ¡lisis: `raise export --format csv`

### Consecuencias

**Positivas:**
- Cumplimiento EU AI Act (trazabilidad de decisiones)
- Mejora continua basada en datos (Kaizen)
- Privacy by design (datos locales)
- Sin costos de telemetrÃ­a cloud
- Compatible con OpenTelemetry si se desea exportar

**Negativas:**
- Storage local crece con uso
- No hay dashboard cloud out-of-box
- AnÃ¡lisis cross-team requiere export manual

**Neutras:**
- Overhead mÃ­nimo (<5ms por trace)

### Alternativas Consideradas

1. **Cloud telemetry** - Dashboards ricos. Rechazado por: viola ADR-005 (local-first), costos, privacy.
2. **OpenTelemetry directo** - EstÃ¡ndar. Rechazado como primario por: overkill para uso individual, pero compatible como export target.
3. **Sin observabilidad** - Simple. Rechazado por: imposibilita mejora basada en datos, no cumple EU AI Act.

---

## Changelog

### v2.0.0 (2025-12-28)

#### âš ï¸ BREAKING CHANGES
- **ADR-006 Superseded**: "DoD Fractales por Fase" â†’ ADR-006a "Validation Gates por Fase"
  - MigraciÃ³n: Reemplazar "DoD" por "Validation Gate" en toda documentaciÃ³n
  - Archivos afectados: specs, katas, configuration
- **ADR-007 Nuevo**: "Rule" â†’ "Guardrail"
  - MigraciÃ³n: `raise-rules.json` â†’ `guardrails.json`
  - CLI: `raise rule` permanece como alias de `raise guardrail`

#### âœ¨ Nuevos ADRs
- **ADR-006a**: Validation Gates por Fase (reemplazo de ADR-006)
- **ADR-007**: Guardrails over Rules
- **ADR-008**: Observable Workflow Local

#### ðŸ“ Actualizaciones
- **ADR-003**: raise-mcp promovido a componente CORE
- **ADR-004**: AÃ±adido JSONL para traces
- **ADR-005**: AÃ±adida nota sobre Observable Workflow

#### ðŸ”„ PolÃ­tica de MigraciÃ³n
Los tÃ©rminos legacy permanecen vÃ¡lidos como aliases:
- `rule` â†’ `guardrail` âœ…
- `DoD` â†’ `Validation Gate` âœ…
- `raise-rules.json` â†’ `guardrails.json` âš ï¸ (deprecated, migrar antes de v3.0)

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

*Agregar nuevo ADR al final. Mantener Ã­ndice actualizado. Cada ADR supersedido debe referenciar su reemplazo.*
