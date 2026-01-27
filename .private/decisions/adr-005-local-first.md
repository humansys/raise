# ADR-005: Local-First Architecture

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-26  
**Actualizado:** 2025-12-28 (nota sobre Observable Workflow)  
**Autores:** Emilio (HumanSys.ai)

---

## Contexto

Decisión sobre dónde procesar datos y servir contexto. Cloud vs local.

## Decisión

Arquitectura **local-first**: todo el procesamiento ocurre en la máquina del desarrollador. No hay backend cloud de RaiSE.

**Principio fundamental:** Los datos del usuario nunca salen de su máquina sin consentimiento explícito.

## Consecuencias

### Positivas
- Privacidad total (código nunca sale)
- Funciona offline
- No hay costos de infraestructura
- Cumplimiento de data residency automático
- Observable Workflow auditable localmente [v2.0]

### Negativas
- No hay analytics centralizados
- Features colaborativas limitadas
- Sin sync automático entre máquinas

### Neutras
- Cada developer es responsable de su ambiente

## Implicaciones para Observable Workflow

El ADR-008 (Observable Workflow) se diseñó específicamente para respetar local-first:
- Traces almacenados en `.raise/traces/` (local)
- Sin telemetría cloud por defecto
- Export opcional a OpenTelemetry si usuario lo desea

## Alternativas Consideradas

1. **Cloud-first SaaS** - Features centralizados. Rechazado por: privacidad concerns, vendor lock-in, costos.
2. **Hybrid** - Local + optional cloud. Rechazado por: complejidad, confusión de modelo.

## Referencias

- [ADR-008](./adr-008-observable-workflow.md) — Observable Workflow respeta local-first
- [13-security-compliance-v2.md](../13-security-compliance-v2.md) — Implicaciones de seguridad

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
