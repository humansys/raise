# RaiSE Open Issues & Pending Decisions
## Issues Abiertos y Decisiones Pendientes

**Última Actualización:** 28 de Diciembre, 2025

---

## Issues Abiertos

### ISSUE-001: Nombre del Producto

**Status:** 🟡 Open  
**Urgencia:** Media  
**Contexto:** ¿Usar "RaiSE" o considerar alternativas por posibles conflictos de trademark?

**Opciones:**
| Opción | Pros | Cons |
|--------|------|------|
| RaiSE | Memorable, ya en uso | Posible conflicto trademark |
| SpecRise | Claro, disponible | Menos memorable |
| raise-kit | Técnico, claro | Solo describe el CLI |
| (otro) | TBD | TBD |

**Deadline:** 2025-01-15  
**Owner:** Emilio  
**Acción requerida:** Trademark search

---

### ISSUE-002: Pricing Validation

**Status:** 🟡 Open  
**Urgencia:** Baja (pre-revenue)  
**Contexto:** ¿Los puntos de precio propuestos ($29/$49/custom) son correctos?

**Opciones:**
| Opción | Pros | Cons |
|--------|------|------|
| $19/$39/custom | Lower barrier | Puede subvaluar |
| $29/$49/custom | Balance | Punto medio |
| $49/$99/custom | Higher value | Mayor barrier |

**Deadline:** 2025-Q2 (antes de launch)  
**Owner:** Emilio  
**Acción requerida:** Customer interviews

---

### ISSUE-003: GitHub Mirror Timing

**Status:** 🟡 Open  
**Urgencia:** Baja  
**Contexto:** ¿Cuándo crear el mirror público en GitHub?

**Consideraciones:**
- Community discovery mejor en GitHub
- GitLab es current home
- Necesidad de documentación pública primero

**Deadline:** 2025-02  
**Owner:** Emilio

---

### ISSUE-004: MCP Transport Default [NUEVO v2.0]

**Status:** 🟡 Open  
**Urgencia:** Media  
**Contexto:** ¿Cuál debe ser el transport default para raise-mcp?

**Opciones:**
| Opción | Pros | Cons |
|--------|------|------|
| stdio | Simple, universal | Single-session |
| SSE | Multi-session, web-friendly | Más complejo |
| Ambos (CLI flag) | Flexible | Más testing |

**Deadline:** 2025-02-01  
**Owner:** TBD  
**Acción requerida:** Evaluar patrones de uso esperados

---

### ISSUE-005: Observable Workflow Retention [NUEVO v2.0]

**Status:** 🟡 Open  
**Urgencia:** Baja  
**Contexto:** ¿Cuánto tiempo retener traces por default?

**Opciones:**
| Opción | Pros | Cons |
|--------|------|------|
| 7 días | Bajo storage | Poco histórico |
| 30 días | Balance | Default propuesto |
| 90 días | Histórico completo | Storage considerable |
| Indefinido | Máximo histórico | Gestión manual requerida |

**Deadline:** 2025-03  
**Owner:** TBD

---

## Decisiones Recientes

### DEC-007: raise-mcp Promovido a CORE [NUEVO v2.0]

**Fecha:** 2025-12-28  
**Decisión:** Promover raise-mcp de v0.3 a v0.2, haciéndolo componente CORE  
**Rationale:** 
- 11,000+ MCP servers registrados (estándar de facto)
- Soporte nativo en Claude, Cursor, Windsurf, Zed
- Context Engineering requiere integración profunda con agentes
- Primitivos MCP (Resources, Tools, Prompts) mapean perfectamente a conceptos RaiSE

**Consecuencias:**
- (+) Interoperabilidad máxima con ecosistema
- (+) Credibilidad enterprise
- (-) Dependencia de protocolo externo
- (-) v0.2 scope aumentado

**Documentado en:** ADR-003 (actualizado)

---

### DEC-006: Observable Workflow con JSONL Local [NUEVO v2.0]

**Fecha:** 2025-12-28  
**Decisión:** Implementar Observable Workflow con almacenamiento JSONL local  
**Rationale:**
- Privacy-first (principio local-first, ADR-005)
- EU AI Act requiere trazabilidad de decisiones
- JSONL es append-only, eficiente para logs
- OpenTelemetry export posible sin cloud dependency

**Consecuencias:**
- (+) Compliance EU AI Act
- (+) No vendor lock-in de telemetría
- (+) Privacy total
- (-) No hay dashboard cloud out-of-box
- (-) Análisis cross-team requiere export manual

**Documentado en:** ADR-008

---

### DEC-005: Renombrar DoD → Validation Gate [NUEVO v2.0]

**Fecha:** 2025-12-28  
**Decisión:** Adoptar "Validation Gate" como término principal, supersediendo "DoD Fractal"  
**Rationale:**
- Terminología HITL (Human-in-the-Loop) estándar en la industria
- LangGraph, CrewAI usan conceptos similares
- "Gate" es inmediatamente comprensible
- El concepto de fractalidad se preserva en documentación

**Consecuencias:**
- (+) Onboarding más rápido
- (+) Interoperabilidad conceptual
- (-) Migración de documentación existente

**Documentado en:** ADR-006a

---

### DEC-004: Renombrar Rule → Guardrail [NUEVO v2.0]

**Fecha:** 2025-12-28  
**Decisión:** Adoptar "Guardrail" como término principal para directivas operacionales  
**Rationale:**
- Alineamiento con terminología enterprise AI (DSPy, LangChain, NVIDIA NeMo)
- "Guardrail" connota protección activa (vs. "rule" pasivo)
- Diferenciación clara con "Constitution" (principios vs. operaciones)

**Consecuencias:**
- (+) Resonancia con audiencia enterprise
- (+) Claridad conceptual
- (-) Migración de archivos `raise-rules.json` → `guardrails.json`

**Documentado en:** ADR-007

---

### DEC-003: Python para CLI

**Fecha:** 2025-12-26  
**Decisión:** Usar Python 3.11+ para raise-kit  
**Rationale:** Ecosistema AI/ML, velocidad de desarrollo  
**Documentado en:** ADR-001

---

### DEC-002: Enfoque secuencial para corpus

**Fecha:** 2025-12-27  
**Decisión:** Generar corpus documento por documento en orden específico  
**Rationale:** Asegurar coherencia, cada documento construye sobre anteriores  
**Consecuencias:**
- (+) Terminología consistente
- (+) Referencias cruzadas correctas
- (-) Más lento que batch

---

### DEC-001: Fork de spec-kit desde upstream

**Fecha:** 2025-12-26  
**Decisión:** Hacer fork del upstream principal (github/spec-kit), no del intermedio  
**Rationale:** Mayor actividad, menor bus factor, community más grande  
**Consecuencias:**
- (+) Acceso a últimos cambios
- (+) Posibilidad de contribuir upstream
- (-) Más divergencia para tracking

---

## Decisiones de Ontología v2.0 [NUEVO]

Resumen de decisiones terminológicas para referencia rápida:

| Término v1.0 | Término v2.0 | Decisión | ADR |
|--------------|--------------|----------|-----|
| Rule | Guardrail | Renombrar | ADR-007 |
| DoD / DoD Fractal | Validation Gate | Renombrar | ADR-006a |
| (nuevo) | Escalation Gate | Añadir | — |
| (nuevo) | Observable Workflow | Añadir | ADR-008 |
| Constitution | Constitution | **Mantener** | — |
| Kata | Kata | **Mantener** | — |
| raise-mcp | raise-mcp (CORE) | Promover | ADR-003 |

**Política de aliases:** Los términos v1.0 permanecen válidos como aliases durante v2.x

---

## Proceso para Nuevos Issues

1. Agregar en sección "Issues Abiertos"
2. Usar formato consistente
3. Asignar owner y deadline
4. Mover a "Decisiones Recientes" cuando se resuelva
5. **Crear ADR si la decisión es arquitectónica** [NUEVO v2.0]

---

## Changelog

### 2025-12-28
- NUEVO: ISSUE-004 (MCP Transport Default)
- NUEVO: ISSUE-005 (Observable Workflow Retention)
- NUEVO: DEC-004 a DEC-007 (decisiones ontología v2.0)
- NUEVO: Sección "Decisiones de Ontología v2.0"

### 2025-12-27
- Issues y decisiones iniciales

---

*Este documento se revisa semanalmente. Ver [14-adr-index-v2.md](./14-adr-index-v2.md) para decisiones arquitectónicas formales.*
