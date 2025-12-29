# RaiSE Tech Stack
## Stack TecnolÃ³gico Detallado

**VersiÃ³n:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**PropÃ³sito:** Documentar las tecnologÃ­as utilizadas en el desarrollo de RaiSE.

> **Nota de versiÃ³n 2.0:** Esta versiÃ³n incorpora raise-mcp como componente CORE, Observable Workflow stack, y alineamiento terminolÃ³gico con ontologÃ­a v2.0.

---

## Core Stack

| Layer | Technology | Version | Rationale | ADR |
|-------|------------|---------|-----------|-----|
| Language | Python | 3.11+ | Ecosistema AI/ML, facilidad de extensiÃ³n | ADR-001 |
| CLI Framework | Click | latest | Composable, bien documentado | â€” |
| Terminal UI | Rich | latest | Output elegante, progress bars | â€” |
| HTTP Client | httpx | latest | Async support, HTTP/2 | â€” |
| Git Operations | GitPython | latest | Operaciones Git nativas | ADR-002 |
| YAML Parsing | PyYAML | latest | Lectura de configs | ADR-004 |
| JSON Schema | jsonschema | latest | ValidaciÃ³n de guardrails | ADR-004 |
| Markdown | markdown-it-py | latest | Parsing de documentos | ADR-004 |
| **MCP Server** | mcp-server-python | latest | **CORE v2.0** - Context Protocol | ADR-003 |

---

## raise-mcp Stack [NUEVO v2.0]

El componente raise-mcp es ahora **CORE** del framework. Stack dedicado:

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | mcp-server-python | ImplementaciÃ³n del protocolo |
| Transport | stdio / SSE | ComunicaciÃ³n con agentes |
| Resources | Custom handlers | Servir Constitution, Guardrails, Specs |
| Tools | Custom tools | validate_gate, escalate, log_trace |
| Prompts | Template engine | Katas como prompts reutilizables |

### Primitivos MCP Implementados

| Primitivo | ImplementaciÃ³n RaiSE | Ejemplo |
|-----------|----------------------|---------|
| **Resources** | Archivos .raise/ como contexto | `raise://constitution`, `raise://guardrails` |
| **Tools** | Comandos CLI expuestos | `validate_gate`, `escalate`, `check_guardrail` |
| **Prompts** | Katas como templates | `kata://code-review`, `kata://spec-gen` |
| **Sampling** | DelegaciÃ³n a LLM | Cuando servidor necesita razonamiento |

---

## Observable Workflow Stack [NUEVO v2.0]

Stack para trazabilidad y auditorÃ­a (ADR-008):

| Component | Technology | Purpose |
|-----------|------------|---------|
| Trace Format | **JSONL** | Append-only, parseo lÃ­nea por lÃ­nea |
| Storage | Local filesystem | `.raise/traces/YYYY-MM-DD.jsonl` |
| Query | jq (CLI), Python | AnÃ¡lisis de traces |
| Export | CSV, OpenTelemetry | Interoperabilidad |
| Visualization | Rich tables, Plotly (opcional) | Reportes CLI |

### JSONL Schema

```jsonl
{"timestamp":"2025-12-28T10:30:00Z","session_id":"sess_abc123","action":"validate_gate","gate":"Gate-Design","result":"passed","duration_ms":2340}
{"timestamp":"2025-12-28T10:30:03Z","session_id":"sess_abc123","action":"read_resource","resource":"raise://guardrails","tokens":1500}
```

### MÃ©tricas Derivables

| MÃ©trica | CÃ¡lculo | Benchmark |
|---------|---------|-----------|
| Re-prompting Rate | Iteraciones por task | <3 ideal |
| Escalation Rate | % tareas escaladas | 10-15% Ã³ptimo |
| Gate Pass Rate | Gates passed / total | >80% healthy |
| Token Efficiency | Tokens por output Ãºtil | Proyecto-especÃ­fico |

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
| Docusaurus | Sitio de documentaciÃ³n | React-based |
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
| Context Protocol | **MCP** | âœ… CORE | Anthropic standard, 11k+ servers |
| Guardrail Distribution | Git protocol | âœ… Active | Clone/pull based (ADR-002) |
| Agent Definitions | YAML specs | âœ… Active | Custom schema |
| Trace Storage | JSONL local | âœ… v2.0 | Observable Workflow |
| Fallback Context | .cursorrules, .claude.md | âœ… Active | Agentes legacy |

---

## Integrations

### IDE Support

| IDE | Integration Type | Status | MCP Support |
|-----|------------------|--------|-------------|
| Cursor | Native .cursorrules + MCP | âœ… Soportado | âœ… Native |
| VS Code | Extension (futuro) | ðŸ“‹ Planificado | ðŸ”„ Via extension |
| JetBrains | Plugin (futuro) | ðŸ“‹ Planificado | ðŸ“‹ Pendiente |
| Vim/Neovim | LSP (futuro) | ðŸ“‹ Planificado | ðŸ“‹ Pendiente |
| **Windsurf** | MCP native | âœ… Soportado | âœ… Native |
| **Zed** | MCP support | ðŸ“‹ Planificado | ðŸ”„ Beta |

### AI Agents

| Agent | Integration | Status | MCP Level |
|-------|-------------|--------|-----------|
| Claude (Anthropic) | MCP native | âœ… Soportado | Full |
| GitHub Copilot | Custom instructions | âœ… Soportado | None |
| Cursor AI | .cursorrules + MCP | âœ… Soportado | Full |
| OpenAI GPT | System prompts | âœ… Soportado | None |
| Google Gemini | Context API | ðŸ“‹ Planificado | None |
| **Claude Code** | MCP native | âœ… Soportado | Full |
| **Cline** | MCP native | âœ… Soportado | Full |

### VCS Providers

| Provider | Status |
|----------|--------|
| GitHub | âœ… Soportado |
| GitLab | âœ… Soportado |
| Bitbucket | âœ… Soportado |
| Azure DevOps | ðŸ“‹ Planificado |

---

## File Formats [ACTUALIZADO v2.0]

| Format | Use Case | Human-Editable | Machine-Parseable | ADR |
|--------|----------|----------------|-------------------|-----|
| Markdown (.md) | Specs, Constitution, Docs | âœ… SÃ­ | ðŸ”„ Parsing requerido | ADR-004 |
| JSON (.json) | guardrails.json, config | âŒ No recomendado | âœ… SÃ­ | ADR-004 |
| YAML (.yaml) | raise.yaml, agent specs | âœ… SÃ­ | âœ… SÃ­ | ADR-004 |
| MDC (.mdc) | Guardrails (Markdown + YAML frontmatter) | âœ… SÃ­ | âœ… SÃ­ | ADR-004 |
| **JSONL (.jsonl)** | Traces, Observable Workflow | âŒ No | âœ… SÃ­ | ADR-008 |

---

## Dependency Policy

### Criterios para Agregar Dependencias

1. **Necesidad clara:** Â¿No podemos lograr esto con stdlib?
2. **Mantenimiento activo:** Â¿Commits en Ãºltimos 6 meses?
3. **Licencia compatible:** MIT, Apache 2.0, BSD
4. **TamaÃ±o razonable:** Evitar dependencias pesadas
5. **Security track record:** Sin CVEs crÃ­ticos activos
6. **MCP compatibility:** Priorizar libs MCP-aware [NUEVO v2.0]

### Update Strategy

| Tipo | Frecuencia | AutomatizaciÃ³n |
|------|------------|----------------|
| Patch versions | Semanal | Dependabot auto-merge |
| Minor versions | Mensual | PR review requerido |
| Major versions | Trimestral | EvaluaciÃ³n de breaking changes |
| **MCP protocol** | Con cada release | EvaluaciÃ³n de features |

### Security Scanning

- **Tool:** Safety, Snyk
- **Frecuencia:** En cada PR + diario en main
- **PolÃ­tica:** Bloquear merge con CVEs crÃ­ticos

---

## Build & Distribution

### Package Structure [ACTUALIZADO v2.0]

```
raise-kit/
â”œâ”€â”€ src/
â”‚   â””â”€â”€ raise/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ cli/              # Comandos CLI
â”‚       â”‚   â”œâ”€â”€ check.py
â”‚       â”‚   â”œâ”€â”€ pull.py
â”‚       â”‚   â”œâ”€â”€ gate.py       # [NUEVO] Validation Gates
â”‚       â”‚   â”œâ”€â”€ audit.py      # [NUEVO] Observable Workflow
â”‚       â”‚   â””â”€â”€ guardrail.py  # [RENOMBRADO] antes: rule.py
â”‚       â”œâ”€â”€ core/             # LÃ³gica de negocio
â”‚       â”‚   â”œâ”€â”€ constitution.py
â”‚       â”‚   â”œâ”€â”€ guardrails.py # [RENOMBRADO] antes: rules.py
â”‚       â”‚   â”œâ”€â”€ gates.py      # [NUEVO] Validation Gates
â”‚       â”‚   â””â”€â”€ traces.py     # [NUEVO] Observable Workflow
â”‚       â”œâ”€â”€ git/              # Operaciones Git
â”‚       â””â”€â”€ mcp/              # MCP server [CORE v2.0]
â”‚           â”œâ”€â”€ server.py
â”‚           â”œâ”€â”€ resources.py
â”‚           â”œâ”€â”€ tools.py
â”‚           â””â”€â”€ prompts.py
â”œâ”€â”€ tests/
â”œâ”€â”€ pyproject.toml
â””â”€â”€ README.md
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
| `raise gate` | < 2s | Validacion de gate |
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
| macOS 12+ | âœ… Soportado |
| Ubuntu 22.04+ | âœ… Soportado |
| Windows 10+ | âœ… Soportado (WSL recomendado) |

---

## Changelog

### v2.1.0 (2025-12-28)
- **NUEVO**: raise-mcp Stack (componente CORE)
- **NUEVO**: Observable Workflow Stack (JSONL traces)
- **NUEVO**: Primitivos MCP documentados
- **RENOMBRADO**: rules.py â†’ guardrails.py
- **ACTUALIZADO**: Package structure con nuevos mÃ³dulos
- **ACTUALIZADO**: Distribution channels incluye MCP Registry
- **ACTUALIZADO**: Performance targets para gate y audit
- **ACTUALIZADO**: IDE support con Windsurf, Zed
- **ACTUALIZADO**: Agent support con Claude Code, Cline

### v1.0.0 (2025-12-27)
- Release inicial

---

*Este documento se actualiza con cada cambio significativo en el stack. Referencias cruzadas: [14-adr-index-v2.md](./14-adr-index-v2.md)*
