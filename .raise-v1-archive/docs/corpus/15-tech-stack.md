# RaiSE Tech Stack
## Stack Tecnológico Detallado

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Documentar las tecnologías utilizadas en el desarrollo de RaiSE.

---

## Core Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Language | Python | 3.11+ | Ecosistema AI/ML, facilidad de extensión |
| CLI Framework | Click | latest | Composable, bien documentado |
| Terminal UI | Rich | latest | Output elegante, progress bars |
| HTTP Client | httpx | latest | Async support, HTTP/2 |
| Git Operations | GitPython | latest | Operaciones Git nativas |
| YAML Parsing | PyYAML | latest | Lectura de configs |
| JSON Schema | jsonschema | latest | Validación de datos |
| Markdown | markdown-it-py | latest | Parsing de documentos |

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

| Tool | Purpose |
|------|---------|
| Docusaurus | Sitio de documentación |
| Mermaid | Diagramas en Markdown |
| MkDocs (alt) | Docs desde repo |

---

## Infrastructure

| Component | Technology |
|-----------|------------|
| CI/CD | GitHub Actions |
| Package Registry | PyPI |
| Container Registry | GitHub Container Registry |
| Docs Hosting | GitHub Pages / Vercel |

---

## AI/Agent Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Context Protocol | MCP (Model Context Protocol) | Anthropic standard |
| Agent Definitions | YAML specs | Custom schema |
| Rule Distribution | Git protocol | Clone/pull based |

---

## Integrations

### IDE Support

| IDE | Integration Type | Status |
|-----|------------------|--------|
| Cursor | Native rules (.mdc) | ✅ Soportado |
| VS Code | Extension (futuro) | 📋 Planificado |
| JetBrains | Plugin (futuro) | 📋 Planificado |
| Vim/Neovim | LSP (futuro) | 📋 Planificado |

### AI Agents

| Agent | Integration | Status |
|-------|-------------|--------|
| Claude (Anthropic) | MCP native | ✅ Soportado |
| GitHub Copilot | Custom instructions | ✅ Soportado |
| Cursor AI | .cursorrules | ✅ Soportado |
| OpenAI GPT | System prompts | ✅ Soportado |
| Google Gemini | Context API | 📋 Planificado |

### VCS Providers

| Provider | Status |
|----------|--------|
| GitHub | ✅ Soportado |
| GitLab | ✅ Soportado |
| Bitbucket | ✅ Soportado |
| Azure DevOps | 📋 Planificado |

---

## Dependency Policy

### Criterios para Agregar Dependencias

1. **Necesidad clara:** ¿No podemos lograr esto con stdlib?
2. **Mantenimiento activo:** ¿Commits en últimos 6 meses?
3. **Licencia compatible:** MIT, Apache 2.0, BSD
4. **Tamaño razonable:** Evitar dependencias pesadas
5. **Security track record:** Sin CVEs críticos activos

### Update Strategy

| Tipo | Frecuencia | Automatización |
|------|------------|----------------|
| Patch versions | Semanal | Dependabot auto-merge |
| Minor versions | Mensual | PR review requerido |
| Major versions | Trimestral | Evaluación de breaking changes |

### Security Scanning

- **Tool:** Safety, Snyk
- **Frecuencia:** En cada PR + diario en main
- **Política:** Bloquear merge con CVEs críticos

---

## Build & Distribution

### Package Structure

```
raise-kit/
├── src/
│   └── raise/
│       ├── __init__.py
│       ├── cli/          # Comandos CLI
│       ├── core/         # Lógica de negocio
│       ├── git/          # Operaciones Git
│       └── mcp/          # MCP server
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

---

## Performance Targets

| Operación | Target | Medición |
|-----------|--------|----------|
| `raise init` | < 5s | Cold start |
| `raise hydrate` | < 10s | 100 reglas |
| `raise check` | < 3s | Proyecto medio |
| MCP context response | < 100ms | P95 |

---

## Compatibility Matrix

| Component | Min Version | Recommended |
|-----------|-------------|-------------|
| Python | 3.11 | 3.12 |
| Git | 2.30 | latest |
| Node (docs) | 18 | 20 LTS |

### OS Support

| OS | Status |
|----|--------|
| macOS 12+ | ✅ Soportado |
| Ubuntu 22.04+ | ✅ Soportado |
| Windows 10+ | ✅ Soportado (WSL recomendado) |

---

*Este documento se actualiza con cada cambio significativo en el stack.*
