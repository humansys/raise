# RaiSE Open Issues & Pending Decisions
## Issues Abiertos y Decisiones Pendientes

**Última Actualización:** 27 de Diciembre, 2025

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

## Decisiones Recientes

### DEC-001: Fork de spec-kit desde upstream

**Fecha:** 2025-12-26  
**Decisión:** Hacer fork del upstream principal (github/spec-kit), no del intermedio  
**Rationale:** Mayor actividad, menor bus factor, community más grande  
**Consecuencias:**
- (+) Acceso a últimos cambios
- (+) Posibilidad de contribuir upstream
- (-) Más divergencia para tracking

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

### DEC-003: Python para CLI

**Fecha:** 2025-12-26  
**Decisión:** Usar Python 3.11+ para raise-kit  
**Rationale:** Ecosistema AI/ML, velocidad de desarrollo  
**Documentado en:** ADR-001

---

## Proceso para Nuevos Issues

1. Agregar en sección "Issues Abiertos"
2. Usar formato consistente
3. Asignar owner y deadline
4. Mover a "Decisiones Recientes" cuando se resuelva

---

*Este documento se revisa semanalmente.*
