# ADR-002: Git como API de Distribución

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-26  
**Autores:** Emilio (HumanSys.ai)

---

## Contexto

Necesitamos distribuir guardrails, katas y templates desde raise-config a proyectos individuales. Opciones:
- NPM/PyPI registry
- API REST propietaria
- Git protocol directo

## Decisión

Usar **Git protocol** (clone/pull) para distribuir contenido de raise-config.

## Consecuencias

### Positivas
- Platform agnostic (funciona con cualquier Git host)
- Versionado nativo (branches, tags)
- Sin infraestructura adicional
- Funciona offline después de clone inicial
- Auditoría via Git history

### Negativas
- No hay auto-update (requiere `raise hydrate` manual)
- Clone inicial puede ser lento para repos grandes
- No hay analytics de uso centralizado

### Neutras
- Requiere Git instalado (ubicuo en dev environments)

## Alternativas Consideradas

1. **NPM/PyPI** - Familiar para devs. Rechazado por: otra dependencia externa, versionado menos flexible.
2. **REST API** - Updates en tiempo real. Rechazado por: requiere infraestructura, vendor lock-in potencial.

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
