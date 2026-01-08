# ADR-006: DoD Fractales por Fase

**Estado:** ⚠️ Superseded by [ADR-006a](./adr-006a-validation-gates.md)  
**Fecha:** 2025-12-26  
**Autores:** Emilio (HumanSys.ai)

---

## ⚠️ AVISO DE SUPERSESIÓN

Este ADR ha sido reemplazado por **ADR-006a: Validation Gates por Fase**.

El concepto de "DoD Fractal" se renombra a "Validation Gate" para alineamiento con terminología HITL estándar de la industria. La semántica se preserva; cambia solo la nomenclatura.

### Migración Requerida

| Término Legacy | Término v2.0 |
|----------------|--------------|
| DoD | Validation Gate |
| DoD Fractal | Validation Gates por fase |

Ver [ADR-006a](./adr-006a-validation-gates.md) para definición actualizada.

---

## Contexto Original

Cada fase del Value Stream (Discovery → Design → Implementation → Deployment) requiere criterios de calidad específicos antes de avanzar.

## Decisión Original

Implementar "Definition of Done" fractales — criterios que aplican a múltiples niveles de granularidad.

---

*Este ADR se mantiene por razones históricas. Usar ADR-006a para implementación actual.*
