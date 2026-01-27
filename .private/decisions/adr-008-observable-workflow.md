# ADR-008: Observable Workflow Local

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-28  
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

Para auditar y mejorar interacciones con agentes AI, necesitamos trazabilidad. Opciones:
- Cloud telemetry (DataDog, New Relic)
- OpenTelemetry exporters
- Logs locales estructurados

La investigación reveló:
- MELT framework (Metrics, Events, Logs, Traces) es el estándar de observabilidad
- OpenTelemetry es vendor-neutral y ubicuo
- Local-first es principio core de RaiSE (ADR-005)
- EU AI Act requiere trazabilidad de decisiones AI

## Decisión

Implementar **Observable Workflow** con almacenamiento local:

| Aspecto | Decisión |
|---------|----------|
| Formato | JSONL (JSON Lines) |
| Ubicación | `.raise/traces/YYYY-MM-DD.jsonl` |
| Retención | Configurable, default 30 días |
| Acceso | CLI (`raise audit`) y recursos MCP |

### Schema de Trace

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

### Principio: Observable by Default

Cada interacción MCP genera trace automáticamente. El Orquestador puede:

1. **Auditar sesiones:** `raise audit --session today`
2. **Medir métricas:** `raise metrics --week`
3. **Exportar para análisis:** `raise export --format csv`

### Métricas Derivadas

| Métrica | Fórmula | Insight |
|---------|---------|---------|
| Re-prompting Rate | prompts con retry / total prompts | Calidad de contexto |
| Escalation Rate | escalations / total gates | Madurez del agente |
| Token Efficiency | output útil / input tokens | ROI de contexto |
| Gate Pass Rate | gates passed / gates attempted | Calidad de specs |

## Consecuencias

### Positivas
- Cumplimiento EU AI Act (trazabilidad de decisiones)
- Mejora continua basada en datos (Kaizen)
- Privacy by design (datos locales)
- Sin costos de telemetría cloud
- Compatible con OpenTelemetry si se desea exportar

### Negativas
- Storage local crece con uso
- No hay dashboard cloud out-of-box
- Análisis cross-team requiere export manual

### Neutras
- Overhead mínimo (<5ms por trace)

## Alternativas Consideradas

1. **Cloud telemetry** - Dashboards ricos. Rechazado por: viola ADR-005 (local-first), costos, privacy.
2. **OpenTelemetry directo** - Estándar. Rechazado como primario por: overkill para uso individual, pero compatible como export target.
3. **Sin observabilidad** - Simple. Rechazado por: imposibilita mejora basada en datos, no cumple EU AI Act.

## Implementación MCP

```json
{
  "tool": "log_trace",
  "parameters": {
    "action": "validate_gate",
    "gate": "Gate-Design",
    "result": "passed"
  }
}
```

## Referencias

- [ADR-005](./adr-005-local-first.md) — Local-first principle
- [13-security-compliance-v2.md](../13-security-compliance-v2.md) — EU AI Act compliance
- [10-system-architecture-v2.md](../10-system-architecture-v2.md) — Arquitectura Observable

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
