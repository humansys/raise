# RaiSE Tech Stack
## Stack Tecnológico Detallado

**Versión:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**Propósito:** Documentar las tecnologías utilizadas en el desarrollo de RaiSE.

> **Nota de versión 2.0:** Esta versión incorpora raise-mcp como componente CORE, Observable Workflow stack, y alineamiento terminológico con ontología v2.0.

---

## Core Stack

| Layer | Technology | Version | Rationale | ADR |
|-------|------------|---------|-----------|-----|
| Language | Python | 3.11+ | Ecosistema AI/ML, facilidad de extensión | ADR-001 |
| CLI Framework | Click | latest | Composable, bien documentado | — |
| Terminal UI | Rich | latest | Output elegante, progress bars | — |
| HTTP Client | httpx | latest | Async support, HTTP/2 | — |
| Git Operations | GitPython | latest | Operaciones Git nativas | ADR-002 |
| YAML Parsing | PyYAML | latest | Lectura de configs | ADR-004 |
| JSON Schema | jsonschema | latest | Validación de guardrails | ADR-004 |
| Markdown | markdown-it-py | latest | Parsing de documentos | ADR-004 |
| **MCP Server** | mcp-server-python | latest | **CORE v2.0** - Context Protocol | ADR-003 |

---

## raise-mcp Stack [NUEVO v2.0]

El componente raise-mcp es ahora **CORE** del framework. Stack dedicado:

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | mcp-server-python | Implementación del protocolo |
| Transport | stdio / SSE | Comunicación con agentes |
| Resources | Custom handlers | Servir Constitution, Guardrails, Specs |
| Tools | Custom tools | validate_gate, escalate, log_trace |
| Prompts | Template engine | Katas como prompts reutilizables |

### Primitivos MCP Implementados

| Primitivo | Implementación RaiSE | Ejemplo |
|-----------|----------------------|---------|
| **Resources** | Archivos .raise/ como contexto | `raise://constitution`, `raise://guardrails` |
| **Tools** | Comandos CLI expuestos | `validate_gate`, `escalate`, `check_guardrail` |
| **Prompts** | Katas como templates | `kata://code-review`, `kata://spec-gen` |
| **Sampling** | Delegación a LLM | Cuando servidor necesita razonamiento |

---

## Observable Workflow Stack [NUEVO v2.0]

Stack para trazabilidad y auditoría (ADR-008):

| Component | Technology | Purpose |
|-----------|------------|---------|
| Trace Format | **JSONL** | Append-only, parseo línea por línea |
| Storage | Local filesystem | `.raise/traces/YYYY-MM-DD.jsonl` |
| Query | jq (CLI), Python | Análisis de traces |
| Export | CSV, OpenTelemetry | Interoperabilidad |
| Visualization | Rich tables, Plotly (opcional) | Reportes CLI |

### JSONL Schema

```jsonl
{"timestamp":"2025-12-28T10:30:00Z","session_id":"sess_abc123","action":"validate_gate","gate":"Gate-Design","result":"passed","duration_ms":2340}
{"timestamp":"2025-12-28T10:30:03Z","session_id":"sess_abc123","action":"read_resource","resource":"raise://guardrails","tokens":1500}
```

### Métricas Derivables

| Métrica | Cálculo | Benchmark |
|---------|---------|-----------|
| Re-prompting Rate | Iteraciones por task | <3 ideal |
| Escalation Rate | % tareas escaladas | 10-15% óptimo |
| Gate Pass Rate | Gates passed / total | >80% healthy |
| Token Efficiency | Tokens por output útil | Proyecto-específico |

---

## Development Tools

| Tool | Purpose | Config File |
|------|---------|-------------|
| uv | Package management | pyproject.toml |
| pytest | Testing | pytest.ini |
| ruff | Linting + formatting | ruff.toml |
| mypy | Type checking | mypy.ini |
| pre-commit | Git hooks | .pre-commit-config.yaml |

---

## Documentation Stack

| Tool | Purpose | Notes |
|------|---------|-------|
| Docusaurus | Sitio de documentación | React-based |
| Mermaid | Diagramas en Markdown | Integrado |
| MkDocs (alt) | Docs desde repo | Python-native |
| **Mintlify** (futuro) | API docs | AI-friendly |

---

## Infrastructure

| Component | Technology | Notes |
|-----------|------------|-------|
| CI/CD | GitHub Actions | Matrix testing |
| Package Registry | PyPI | wheel/sdist |
| Container Registry | GitHub Container Registry | Docker images |
| Docs Hosting | GitHub Pages / Vercel | Static hosting |

---

## AI/Agent Stack

| Component | Technology | Status | Notes |
|-----------|------------|--------|-------|
| Context Protocol | **MCP** | 🟡 CORE | Anthropic standard, 11k+ servers |
| Guardrail Distribution | Git protocol | 🟡 Active | Clone/pull based (ADR-002) |
| Agent Definitions | YAML specs | 🟡 Active | Custom schema |
| Trace Storage | JSONL local | 🟡 v2.0 | Observable Workflow |
| Fallback Context | .cursorrules, .claude.md | 🟡 Active | Agentes legacy |

---

## Integrations

### IDE Support

| IDE | Integration Type | Status | MCP Support |
|-----|------------------|--------|-------------|
| Cursor | Native .cursorrules + MCP | 🟡 Soportado | 🟡 Native |
| VS Code | Extension (futuro) | 📋 Planificado | 📋 Via extension |
| JetBrains | Plugin (futuro) | 📋 Planificado | 📋 Pendiente |
| Vim/Neovim | LSP (futuro) | 📋 Planificado | 📋 Pendiente |
| **Windsurf** | MCP native | 🟡 Soportado | 🟡 Native |
| **Zed** | MCP support | 📋 Planificado | 📋 Beta |

### AI Agents

| Agent | Integration | Status | MCP Level |
|-------|-------------|--------|-----------|
| Claude (Anthropic) | MCP native | 🟡 Soportado | Full |
| GitHub Copilot | Custom instructions | 🟡 Soportado | None |
| Cursor AI | .cursorrules + MCP | 🟡 Soportado | Full |
| OpenAI GPT | System prompts | 🟡 Soportado | None |
| Google Gemini | Context API | 📋 Planificado | None |
| **Claude Code** | MCP native | 🟡 Soportado | Full |
| **Cline** | MCP native | 🟡 Soportado | Full |

### VCS Providers

| Provider | Status |
|----------|--------|
| GitHub | 🟡 Soportado |
| GitLab | 🟡 Soportado |
| Bitbucket | 🟡 Soportado |
| Azure DevOps | 📋 Planificado |

---

## File Formats [ACTUALIZADO v2.0]

| Format | Use Case | Human-Editable | Machine-Parseable | ADR |
|--------|----------|----------------|-------------------|-----|
| Markdown (.md) | Specs, Constitution, Docs | ✅ Sí | 📋 Parsing requerido | ADR-004 |
| JSON (.json) | guardrails.json, config | ❌ No recomendado | ✅ Sí | ADR-004 |
| YAML (.yaml) | raise.yaml, agent specs | ✅ Sí | ✅ Sí | ADR-004 |
| MDC (.mdc) | Guardrails (Markdown + YAML frontmatter) | ✅ Sí | ✅ Sí | ADR-004 |
| **JSONL (.jsonl)** | Traces, Observable Workflow | ❌ No | ✅ Sí | ADR-008 |

---

## Dependency Policy

### Criterios para Agregar Dependencias

1. **Necesidad clara:** ¿No podemos lograr esto con stdlib?
2. **Mantenimiento activo:** ¿Commits en últimos 6 meses?
3. **Licencia compatible:** MIT, Apache 2.0, BSD
4. **Tamaño razonable:** Evitar dependencias pesadas
5. **Security track record:** Sin CVEs críticos activos
6. **MCP compatibility:** Priorizar libs MCP-aware [NUEVO v2.0]

### Update Strategy

| Tipo | Frecuencia | Automatización |
|------|------------|----------------|
| Patch versions | Semanal | Dependabot auto-merge |
| Minor versions | Mensual | PR review requerido |
| Major versions | Trimestral | Evaluación de breaking changes |
| **MCP protocol** | Con cada release | Evaluación de features |

### Security Scanning

- **Tool:** Safety, Snyk
- **Frecuencia:** En cada PR + diario en main
- **Política:** Bloquear merge con CVEs críticos

---

## Build & Distribution

### Package Structure [ACTUALIZADO v2.0]

```
raise-kit/
├── src/
│   └── raise/
│       ├── __init__.py
│       ├── cli/              # Comandos CLI
│       │   ├── check.py
│       │   ├── pull.py
│       │   ├── gate.py       # [NUEVO] Validation Gates
│       │   ├── audit.py      # [NUEVO] Observable Workflow
│       │   └── guardrail.py  # [RENOMBRADO] antes: rule.py
│       ├── core/             # Lógica de negocio
│       │   ├── constitution.py
│       │   ├── guardrails.py # [RENOMBRADO] antes: rules.py
│       │   ├── gates.py      # [NUEVO] Validation Gates
│       │   └── traces.py     # [NUEVO] Observable Workflow
│       ├── git/              # Operaciones Git
│       └── mcp/              # MCP server [CORE v2.0]
│           ├── server.py
│           ├── resources.py
│           ├── tools.py
│           └── prompts.py
├── tests/
├── pyproject.toml
└── README.md
```

### Distribution Channels

| Channel | Format | Target |
|---------|--------|--------|
| PyPI | wheel/sdist | Python users |
| Homebrew | formula | macOS users |
| Binary | PyInstaller | Users sin Python |
| Docker | image | CI/CD pipelines |
| **MCP Registry** | server config | MCP-native agents [NUEVO] |

---

## Performance Targets [ACTUALIZADO v2.1]

| Operacion | Target | Medicion |
|-----------|--------|----------|
| `raise init` | < 5s | Cold start |
| `raise pull` | < 10s | 100 guardrails |
| `raise kata` | Variable | Depende de kata (interactivo) |
| `raise check` | < 3s | Proyecto medio |
| `raise gate` | < 2s | Validación de gate |
| `raise audit` | < 5s | 1 semana de traces |
| MCP context response | < 100ms | P95 |
| **Trace logging** | < 5ms | Por evento |

---

## Compatibility Matrix

| Component | Min Version | Recommended | Notes |
|-----------|-------------|-------------|-------|
| Python | 3.11 | 3.12 | Type hints, performance |
| Git | 2.30 | latest | Sparse checkout |
| Node (docs) | 18 | 20 LTS | Docusaurus |
| **MCP Protocol** | 2024.11 | latest | raise-mcp compatibility |

### OS Support

| OS | Status |
|----|--------|
| macOS 12+ | 🟡 Soportado |
| Ubuntu 22.04+ | 🟡 Soportado |
| Windows 10+ | 🟡 Soportado (WSL recomendado) |

---

## Changelog

### v2.1.0 (2025-12-28)
- **NUEVO**: raise-mcp Stack (componente CORE)
- **NUEVO**: Observable Workflow Stack (JSONL traces)
- **NUEVO**: Primitivos MCP documentados
- **RENOMBRADO**: rules.py → guardrails.py
- **ACTUALIZADO**: Package structure con nuevos módulos
- **ACTUALIZADO**: Distribution channels incluye MCP Registry
- **ACTUALIZADO**: Performance targets para gate y audit
- **ACTUALIZADO**: IDE support con Windsurf, Zed
- **ACTUALIZADO**: Agent support con Claude Code, Cline

### v1.0.0 (2025-12-27)
- Release inicial

---

*Este documento se actualiza con cada cambio significativo en el stack. Referencias cruzadas: [14-adr-index-v2.md](./14-adr-index-v2.md)*
