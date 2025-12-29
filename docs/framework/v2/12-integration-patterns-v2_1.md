# RaiSE Integration Patterns
## Patrones de IntegraciÃ³n con el Ecosistema

**VersiÃ³n:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**PropÃ³sito:** Documentar cÃ³mo RaiSE se integra con herramientas externas via MCP y otros mecanismos.

---

## Matriz de Integraciones

| Sistema | Tipo | Mecanismo | Estado | Prioridad |
|---------|------|-----------|--------|-----------|
| GitHub | VCS | Git protocol | âœ… Soportado | P0 |
| GitLab | VCS | Git protocol | âœ… Soportado | P0 |
| Bitbucket | VCS | Git protocol | âœ… Soportado | P1 |
| Cursor | IDE | MCP + .cursorrules | âœ… Soportado | P0 |
| VS Code | IDE | MCP + extension | ðŸ“‹ Planificado | P1 |
| Claude (Anthropic) | Agent | MCP native | âœ… Soportado | P0 |
| Claude Code | Agent | MCP + CLAUDE.md | âœ… Soportado | P0 |
| GitHub Copilot | Agent | Custom Instructions | âœ… Soportado | P0 |
| OpenAI GPT | Agent | MCP (via bridge) | ðŸ”„ En desarrollo | P1 |
| Jira | PM | REST API | ðŸ“‹ Planificado | P2 |
| Linear | PM | GraphQL API | ðŸ“‹ Planificado | P2 |

---

## PatrÃ³n Principal: MCP-Native

RaiSE es **MCP-native**: el Model Context Protocol es el mecanismo primario de integraciÃ³n con agentes AI.

### Arquitectura MCP

```mermaid
flowchart TB
    subgraph Agents["AI Agents (MCP Clients)"]
        A1[Claude Desktop]
        A2[Cursor AI]
        A3[Claude Code]
        A4[OpenAI via Bridge]
    end
    
    subgraph RaiSE["raise-mcp Server"]
        R[Resources]
        T[Tools]
        P[Prompts]
    end
    
    subgraph GoldenData[".raise/ Golden Data"]
        C[constitution.md]
        G[guardrails.json]
        S[specs/]
        TR[traces/]
    end
    
    A1 & A2 & A3 & A4 -->|MCP Protocol| RaiSE
    RaiSE --> GoldenData
```

### Primitivos MCP Expuestos

#### Resources (Contexto Estructurado)

| URI | DescripciÃ³n | Formato |
|-----|-------------|---------|
| `raise://constitution` | Principios del proyecto | Markdown |
| `raise://guardrails` | Guardrails activos compilados | JSON |
| `raise://guardrails/{id}` | Guardrail especÃ­fico | Markdown |
| `raise://specs` | Lista de specs disponibles | JSON |
| `raise://specs/{id}` | Spec especÃ­fica | Markdown |
| `raise://specs/current` | Spec en trabajo actual | Markdown |
| `raise://plans/current` | Plan de implementaciÃ³n activo | Markdown |
| `raise://context` | Contexto agregado para tarea | JSON |

#### Tools (Acciones)

| Tool | DescripciÃ³n | ParÃ¡metros |
|------|-------------|------------|
| `validate_gate` | Valida artefacto contra Validation Gate | `gate_id`, `artifact_path` |
| `check_guardrail` | Verifica compliance contra guardrail | `guardrail_id`, `content` |
| `generate_artifact` | Crea artefacto desde template | `template_id`, `variables` |
| `escalate` | Solicita intervenciÃ³n del Orquestador | `reason`, `context`, `options` |
| `log_trace` | Registra acciÃ³n en Observable Workflow | `action`, `input`, `output` |

#### Prompts (Templates Reutilizables)

| Prompt | DescripciÃ³n | Variables |
|--------|-------------|-----------|
| `constitution_context` | Inyecta Constitution en contexto | - |
| `guardrail_check` | Template para verificaciÃ³n de guardrail | `guardrail_id` |
| `gate_validation` | Template para validaciÃ³n de gate | `gate_id`, `criteria` |
| `escalation_request` | Formato de solicitud HITL | `reason`, `options` |

---

## Patrones de IntegraciÃ³n por Tipo

### PatrÃ³n: VCS Provider

**Principio:** RaiSE usa Git protocol directamente, no APIs especÃ­ficas. Esto garantiza platform agnosticism.

**Interface abstracta:**
```python
class VCSProvider(Protocol):
    def clone(self, url: str, path: Path) -> None: ...
    def pull(self, path: Path, branch: str) -> None: ...
    def get_current_branch(self, path: Path) -> str: ...
    def get_remote_url(self, path: Path) -> str: ...
```

**Implementaciones:**

| Provider | Notas |
|----------|-------|
| GitHub | HTTPS y SSH, incluye GitHub Enterprise |
| GitLab | Cloud y self-hosted |
| Bitbucket | Cloud y Server |
| Azure DevOps | Via Git protocol |

---

### PatrÃ³n: IDE Integration

**Mecanismos de integraciÃ³n por IDE:**

| IDE | MCP | Archivo Config | Fallback |
|-----|-----|----------------|----------|
| Cursor | âœ… Native | `.cursorrules` | .mdc files |
| VS Code | ðŸ”„ Via extension | `settings.json` | AGENTS.md |
| JetBrains | ðŸ“‹ Planificado | `.idea/` | AGENTS.md |
| Neovim | ðŸ“‹ Planificado | `init.lua` | AGENTS.md |

**Estructura para Cursor (MCP + fallback):**
```
proyecto/
â”œâ”€â”€ .cursor/
â”‚   â””â”€â”€ rules/
â”‚       â”œâ”€â”€ guard-001-naming.mdc
â”‚       â”œâ”€â”€ guard-002-security.mdc
â”‚       â””â”€â”€ ...
â”œâ”€â”€ .raise/
â”‚   â””â”€â”€ memory/
â”‚       â”œâ”€â”€ constitution.md
â”‚       â””â”€â”€ guardrails.json
â””â”€â”€ raise.yaml  # Configura raise-mcp
```

**Estructura para Claude Code:**
```
proyecto/
â”œâ”€â”€ CLAUDE.md              # Instructions root level
â”œâ”€â”€ .raise/
â”‚   â””â”€â”€ memory/
â”‚       â””â”€â”€ constitution.md
â””â”€â”€ raise.yaml             # Configura raise-mcp
```

**Estructura universal (AGENTS.md):**
```
proyecto/
â”œâ”€â”€ AGENTS.md              # EstÃ¡ndar emergente de comunidad
â”œâ”€â”€ .raise/
â”‚   â””â”€â”€ memory/
â”‚       â””â”€â”€ constitution.md
â””â”€â”€ raise.yaml
```

---

### PatrÃ³n: Agent Integration

**Flujo MCP estÃ¡ndar:**

```mermaid
sequenceDiagram
    participant O as Orquestador
    participant A as AI Agent
    participant MCP as raise-mcp
    participant GD as Golden Data

    O->>A: Tarea de desarrollo
    A->>MCP: list_resources()
    MCP-->>A: [constitution, guardrails, specs/current]
    
    A->>MCP: read_resource("raise://constitution")
    MCP->>GD: Lee constitution.md
    GD-->>MCP: Content
    MCP-->>A: Constitution context
    
    A->>MCP: read_resource("raise://guardrails")
    MCP->>GD: Lee guardrails.json
    GD-->>MCP: Guardrails activos
    MCP-->>A: Guardrails context
    
    Note over A: Agent genera con contexto completo
    
    A->>MCP: call_tool("validate_gate", {gate: "gate-code"})
    MCP->>MCP: EvalÃºa criterios
    MCP-->>A: {status: "passed"}
    
    A-->>O: Resultado validado
```

**ConfiguraciÃ³n por agente:**

| Agente | ConexiÃ³n MCP | Config File |
|--------|--------------|-------------|
| Claude Desktop | `claude_desktop_config.json` | SecciÃ³n `mcpServers` |
| Cursor | Built-in | `.cursor/mcp.json` |
| Claude Code | AutomÃ¡tico | `raise.yaml` |
| Copilot | Via bridge | Custom Instructions |

**Ejemplo: claude_desktop_config.json**
```json
{
  "mcpServers": {
    "raise": {
      "command": "raise",
      "args": ["mcp", "--project", "/path/to/project"]
    }
  }
}
```

---

### PatrÃ³n: Observable Workflow Integration

**PropÃ³sito:** Generar traces auditables de todas las interacciones MCP.

```mermaid
flowchart LR
    A[Agent Action] -->|MCP call| B[raise-mcp]
    B -->|log_trace| C[.raise/traces/]
    C -->|raise audit| D[Report]
    D -->|export| E[SIEM/Compliance]
```

**Formato de trace (JSONL):**
```jsonl
{"trace_id":"uuid","timestamp":"ISO8601","action":"resource_read","uri":"raise://constitution","duration_ms":45,"status":"ok"}
{"trace_id":"uuid","timestamp":"ISO8601","action":"tool_call","tool":"validate_gate","input":{"gate":"gate-code"},"output":{"status":"passed"},"duration_ms":120}
```

**IntegraciÃ³n con sistemas externos:**

| Sistema | Mecanismo | Estado |
|---------|-----------|--------|
| Archivo local | JSONL nativo | âœ… Soportado |
| OpenTelemetry | OTLP export | ðŸ“‹ Planificado |
| Datadog | Log forwarding | ðŸ“‹ Planificado |
| Splunk | HEC endpoint | ðŸ“‹ Planificado |

---

### PatrÃ³n: Project Management (Futuro)

**Estado:** Planificado para v0.4+

**Flujo bidireccional:**
```mermaid
flowchart LR
    A[RaiSE Spec] -->|sync| B[Jira/Linear]
    B -->|sync| A
    C[Gate Status] -->|webhook| D[Issue Transition]
```

**Capacidades planificadas:**
- Sincronizar specs â†’ issues
- Importar issues â†’ specs
- Mapear Validation Gates â†’ workflow states
- Actualizar estado bidireccional
- Generar reportes de compliance

---

## APIs

### APIs Externas Consumidas

| API | PropÃ³sito | Auth | Requerido |
|-----|-----------|------|-----------|
| Git protocol | Clone/pull repos | SSH/HTTPS | âœ… SÃ­ |
| GitHub API | Metadata (opcional) | Token | âŒ No |
| GitLab API | Metadata (opcional) | Token | âŒ No |

**Principio:** RaiSE funciona sin APIs externas. Git protocol es suficiente.

### APIs Expuestas

#### raise-mcp (MCP Server)

| MÃ©todo MCP | DescripciÃ³n |
|------------|-------------|
| `list_resources` | Lista recursos disponibles |
| `read_resource` | Lee recurso especÃ­fico |
| `list_tools` | Lista tools disponibles |
| `call_tool` | Ejecuta herramienta |
| `list_prompts` | Lista prompts disponibles |
| `get_prompt` | Obtiene prompt con variables |

**AutenticaciÃ³n:** Local only (no auth required)

**Transporte:** stdio (estÃ¡ndar MCP)

#### raise-kit CLI

La CLI no expone APIs HTTP. InteracciÃ³n via comandos:
```bash
raise check --format json      # Output estructurado
raise kata --output report.json
raise audit --format jsonl     # Observable Workflow export
raise mcp                      # Inicia MCP server
```

---

## Extensibilidad

### Crear Nueva IntegraciÃ³n MCP

1. **Definir Resources** adicionales en `raise.yaml`
2. **Implementar Tools** custom si necesario
3. **Registrar** en configuraciÃ³n MCP
4. **Documentar** en este archivo

**Ejemplo: Resource custom**
```yaml
# raise.yaml
mcp:
  custom_resources:
    - uri: "raise://custom/metrics"
      handler: "metrics_handler"
      description: "Project metrics"
```

### Plugin System (v1.0+)

```yaml
# raise.yaml
plugins:
  - name: raise-jira
    version: "^1.0"
    config:
      instance: https://company.atlassian.net
      project: PROJ
  
  - name: raise-datadog
    version: "^1.0"
    config:
      api_key: ${DATADOG_API_KEY}
      traces: true
```

---

## Compatibilidad y Fallbacks

### Matriz de Compatibilidad

| Agente | MCP Native | Fallback 1 | Fallback 2 |
|--------|------------|------------|------------|
| Claude Desktop | âœ… | - | - |
| Claude Code | âœ… | CLAUDE.md | - |
| Cursor | âœ… | .cursorrules | AGENTS.md |
| Copilot | âŒ | Custom Instructions | AGENTS.md |
| GPT-4 | ðŸ”„ Bridge | System prompt | AGENTS.md |

### Fallback Strategy

```mermaid
flowchart TD
    A[Agent detectado] --> B{Soporta MCP?}
    B -->|SÃ­| C[Conectar raise-mcp]
    B -->|No| D{Tiene config nativa?}
    D -->|SÃ­| E[Usar .cursorrules / CLAUDE.md]
    D -->|No| F[Generar AGENTS.md]
    
    C --> G[Context Engineering completo]
    E --> H[Context parcial]
    F --> H
```

**Comando de generaciÃ³n de fallback:**
```bash
raise export --format cursorrules  # Genera .cursorrules
raise export --format claude       # Genera CLAUDE.md
raise export --format agents       # Genera AGENTS.md
```

---

## Changelog

### v2.1.0 (2025-12-28)
- MCP promovido a patrÃ³n principal de integraciÃ³n
- TerminologÃ­a: rules â†’ guardrails, DoD â†’ Validation Gates
- NUEVO: Primitivos MCP detallados (Resources, Tools, Prompts)
- NUEVO: PatrÃ³n Observable Workflow Integration
- NUEVO: Matriz de compatibilidad y fallbacks
- NUEVO: Comando `raise export` para fallbacks
- Tools actualizados: `validate_dod` â†’ `validate_gate`, `check_rules` â†’ `check_guardrail`
- AÃ±adido soporte OpenAI via bridge

---

*Este documento se actualiza con cada nueva integraciÃ³n. Referencias: [10-system-architecture.md](./10-system-architecture.md), [11-data-architecture.md](./11-data-architecture.md).*
