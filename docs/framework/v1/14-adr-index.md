# Architecture Decision Records
## Índice de Decisiones Arquitectónicas

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Documentar decisiones arquitectónicas del proyecto RaiSE.

---

## Índice de ADRs

| ID | Título | Estado | Fecha |
|----|--------|--------|-------|
| ADR-001 | Usar Python para CLI | ✅ Accepted | 2025-12 |
| ADR-002 | Git como API de distribución | ✅ Accepted | 2025-12 |
| ADR-003 | MCP como protocolo de contexto | ✅ Accepted | 2025-12 |
| ADR-004 | Markdown para humanos, JSON para máquinas | ✅ Accepted | 2025-12 |
| ADR-005 | Local-first architecture | ✅ Accepted | 2025-12 |
| ADR-006 | DoD fractales por fase | ✅ Accepted | 2025-12 |

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
Necesitamos distribuir reglas, katas y templates desde raise-config a proyectos individuales. Opciones:
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
- Requiere Git instalado (ubiquo en dev environments)

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
Usar **MCP (Model Context Protocol)** de Anthropic para servir contexto.

### Consecuencias

**Positivas:**
- Estándar emergente con momentum
- Soporte nativo en Claude
- Extensible (resources + tools)
- Comunidad creciente

**Negativas:**
- Estándar joven (puede evolucionar)
- No todos los agentes soportan MCP aún
- Dependencia de decisiones de Anthropic

**Neutras:**
- Requiere implementar MCP server

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
Necesitamos formatos para reglas, specs y configuración. Debate entre legibilidad humana y parseo por máquinas.

### Decisión
- **Markdown** para documentos que humanos leen/editan (specs, constitution, plans)
- **JSON** para datos que máquinas consumen (raise-rules.json, config)
- **YAML** para configuración human-editable (raise.yaml, agent specs)
- **MDC** para reglas (Markdown + frontmatter YAML)

### Consecuencias

**Positivas:**
- Mejor experiencia para cada audiencia
- Markdown es diff-friendly en PRs
- JSON es parse-fast para runtime
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
✅ Accepted

### Fecha
2025-12-26

### Contexto
¿Cómo estructurar quality gates en el flujo de desarrollo?

### Decisión
Implementar **DoD (Definition of Done) fractal**: cada fase del flujo tiene su propio DoD que debe cumplirse antes de avanzar.

### Consecuencias

**Positivas:**
- Problemas detectados temprano
- Calidad consistente en cada fase
- Claridad sobre "qué significa done"
- Katas de validación por fase

**Negativas:**
- Overhead inicial percibido
- Necesidad de definir DoD para cada fase
- Puede sentirse burocrático en tareas pequeñas

**Neutras:**
- Requiere disciplina del equipo

### Alternativas Consideradas

1. **DoD único al final** - Simple. Rechazado por: problemas se acumulan, fix tardío es caro.
2. **Sin DoD formal** - Flexibilidad. Rechazado por: inconsistencia, "done" subjetivo.

---

*Agregar nuevo ADR al final. Mantener índice actualizado.*
