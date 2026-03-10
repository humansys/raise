---
id: "ADR-034"
title: "Governance Extensibility — Schema, Parsers, and Documentation Targets"
date: "2026-02-19"
status: "Accepted"
---

# ADR-034: Governance Extensibility — Schema, Parsers, and Documentation Targets

## Context

ADR-033 established the adapter pattern for PM tool integrations (Jira, Azure DevOps).
That decision solved one concrete problem: abstracting backlog operations. However, the same
brittleness exists at a more fundamental level.

`rai memory build` and the CLI skills assume a fixed governance structure: `.raise/` directory
with specific markdown files at specific paths. This is the **RaiSE default governance schema** —
but it is treated as the only possible schema. Two problems follow:

1. **Schema brittleness:** Organizations have different governance structures. A team using
   Confluence for architecture docs, Jira for backlog, and Notion for runbooks cannot feed
   any of that into the RaiSE knowledge graph without modifying core code.

2. **Documentation target brittleness:** Publishing governance documents (`rai docs publish`)
   requires knowing where in Confluence to put each document type. That is org-specific
   hierarchy and org-specific templates. Hardcoding it means every enterprise customer
   requires a configuration workaround.

The deeper insight: **governance schemas will vary across organizations just as PM tools vary**.
The right response is the same — define the contract in core, let implementations proliferate.

Three constraints shape the decision:

1. **Open-core boundary** — the extension mechanism must be in raise-core (Apache 2.0). Specific
   adapters for enterprise governance schemas belong in raise-pro (commercial).
2. **Entry points pattern already proven** — ADR-033 demonstrated that Python entry points
   plus `Protocol` classes work well for this. Reuse the same pattern.
3. **RaiSE default governance = first plugin** — the current `.raise/` structure becomes the
   built-in reference implementation of the extension mechanism, not a special case hardcoded
   into the core.

## Decision

### 1. Three extension points, same pattern as ADR-033

`raise-core` publishes three additional `Protocol` abstractions. Each follows the same
`entry_points` discovery mechanism established in ADR-033.

---

#### `GovernanceSchemaProvider` — what governance artifacts exist and where

```python
# src/rai_cli/adapters/governance.py

from typing import Protocol, runtime_checkable

@runtime_checkable
class GovernanceSchemaProvider(Protocol):
    """Declares what governance artifacts are available in this organization and how to locate them."""

    def list_artifact_types(self) -> list[ArtifactType]: ...
    def locate(self, artifact_type: ArtifactType) -> list[ArtifactLocator]: ...
```

Entry point group: `rai.governance.schemas`

| Implementation | Source | Tier |
|---|---|---|
| `RaiSEDefaultSchema` | `.raise/` directory structure | COMMUNITY (built-in) |
| `ConfluenceGovernanceSchema` | Confluence spaces (configured) | PRO |
| `NotionGovernanceSchema` | Notion databases | Community adapter |

---

#### `GovernanceParser` — how to extract structured graph data from an artifact

```python
@runtime_checkable
class GovernanceParser(Protocol):
    """Extracts structured graph nodes from a governance artifact."""

    def can_parse(self, locator: ArtifactLocator) -> bool: ...
    def parse(self, locator: ArtifactLocator) -> list[GraphNode]: ...
```

Entry point group: `rai.governance.parsers`

| Implementation | Parses | Tier |
|---|---|---|
| `MarkdownAdrParser` | `dev/decisions/*.md` | COMMUNITY (built-in) |
| `MarkdownBacklogParser` | `.raise/governance/backlog.md` | COMMUNITY (built-in) |
| `JsonlPatternParser` | `.raise/rai/memory/*.jsonl` | COMMUNITY (built-in) |
| `JiraBacklogParser` | Jira issues via adapter | PRO |
| `ConfluenceArchParser` | Confluence architecture pages | PRO |

---

#### `DocumentationTarget` — where and how to publish governance documents

```python
@runtime_checkable
class DocumentationTarget(Protocol):
    """Publishes a governance document to a destination."""

    def can_publish(self, doc_type: DocumentType, metadata: dict) -> bool: ...
    def publish(self, doc_type: DocumentType, content: str, metadata: dict) -> PublishResult: ...
```

Entry point group: `rai.docs.targets`

| Implementation | Destination | Tier |
|---|---|---|
| `LocalMarkdownTarget` | `.raise/` subdirectory | COMMUNITY (built-in) |
| `ConfluenceTarget` | Confluence space/page hierarchy (org-configured) | PRO |

---

### 2. Shared models in `rai_cli.adapters.governance_models`

Pydantic models are published as the shared vocabulary between core and all adapters:

```python
class ArtifactType(str, Enum):
    BACKLOG = "backlog"
    DECISION = "decision"
    VISION = "vision"
    DESIGN = "design"
    RUNBOOK = "runbook"
    # Extensible via registry

class ArtifactLocator(BaseModel):
    artifact_type: ArtifactType
    provider: str           # e.g. "confluence", "local", "jira"
    location: str           # URL, file path, or identifier
    metadata: dict = {}

class DocumentType(str, Enum):
    ADR = "adr"
    DESIGN = "design"
    ARCHITECTURE = "architecture"
    RUNBOOK = "runbook"
    # Extensible via registry

class PublishResult(BaseModel):
    success: bool
    url: str | None = None
    message: str | None = None
```

---

### 3. How `rai memory build` changes

The command moves from hardcoded path scanning to querying all registered providers and parsers:

```python
# Before (brittle — assumes .raise/ structure)
def build_graph() -> Graph:
    parse_backlog(".raise/governance/backlog.md")
    parse_decisions("dev/decisions/*.md")
    parse_patterns(".raise/rai/memory/*.jsonl")
    ...

# After (extensible — queries all registered providers)
def build_graph() -> Graph:
    graph = Graph()
    schemas = get_governance_schemas()     # entry_points("rai.governance.schemas")
    parsers = get_governance_parsers()     # entry_points("rai.governance.parsers")

    for schema in schemas:
        for locator in schema.locate_all():
            for parser in parsers:
                if parser.can_parse(locator):
                    graph.add_nodes(parser.parse(locator))
                    break  # first matching parser wins

    return graph
```

**Effect:** Installing a new parser package (e.g. `raise-jira-adapter`) immediately enriches
the knowledge graph with Jira data. No configuration changes in `rai memory build`.

---

### 4. Org-specific adapter configuration

Configuration for each installed adapter lives in `.raise/adapters/<name>.yaml`, excluded
from version control. Same convention as ADR-033:

```yaml
# .raise/adapters/confluence-governance.yaml  (not in .gitignore, org-specific)
spaces:
  decisions: "ARCH"
  vision:    "PROD"
  runbooks:  "OPS"

page_templates:
  adr:          "ADR Template"
  design:       "Design Doc Template"
  architecture: "Architecture Overview Template"

parent_pages:
  decisions: "12345678"   # Confluence page ID
  design:    "87654321"
```

---

### 5. Adapter discovery (same pattern as ADR-033)

```python
# In raise-confluence-adapter's pyproject.toml
[project.entry-points."rai.governance.schemas"]
confluence = "rai_confluence_adapter:ConfluenceGovernanceSchema"

[project.entry-points."rai.governance.parsers"]
confluence = "rai_confluence_adapter:ConfluenceArchParser"

[project.entry-points."rai.docs.targets"]
confluence = "rai_confluence_adapter:ConfluenceTarget"
```

Installing the adapter package is sufficient. No manual registration.

---

### 6. What stays in raise-core (Apache 2.0)

| Component | Location |
|---|---|
| Protocol definitions (3 extension points) | `src/rai_cli/adapters/governance.py` |
| Shared Pydantic models | `src/rai_cli/adapters/governance_models.py` |
| Entry point registries | `src/rai_cli/adapters/registry.py` |
| `RaiSEDefaultSchema` | `src/rai_cli/governance/default_schema.py` |
| All built-in markdown parsers | `src/rai_cli/governance/parsers/` |
| `LocalMarkdownTarget` | `src/rai_cli/governance/targets/local.py` |
| Updated `rai memory build` | `src/rai_cli/commands/memory.py` |

### 7. What goes in raise-pro (commercial)

| Component | Package |
|---|---|
| `ConfluenceGovernanceSchema` | `raise-confluence-adapter` |
| `ConfluenceTarget` | `raise-confluence-adapter` |
| `JiraBacklogParser` | `raise-jira-adapter` |
| `ConfluenceArchParser` | `raise-confluence-adapter` |

---

## Consequences

| Type | Impact |
|---|---|
| + | `rai memory build` becomes richer as more parsers are installed — no code changes required |
| + | Enterprise customers bring their own governance structures without forking core |
| + | Community can build parsers (Notion, Obsidian, GitHub Wiki) against stable contracts |
| + | RaiSE default governance = self-documenting reference implementation of the extension model |
| + | `rai docs publish` resolves destination from org config, not hardcoded logic |
| + | ADR-033 and ADR-034 together form a complete adapter system — PM ops + governance intelligence |
| - | `rai memory build` output now depends on which plugins are installed — behavior varies per install |
| - | Parser ordering requires a deterministic conflict resolution rule (first match wins) |
| - | Three new public API surfaces require the same versioning discipline as ADR-033 |

## Relationship to ADR-033

ADR-033 (ProjectManagementAdapter) is a special case of this pattern applied to backlog
operations — writing to and reading from PM tools. ADR-034 generalizes the same mechanism
to the intelligence layer: reading governance knowledge and publishing governance artifacts.

```
ADR-034 (this): General extension mechanism for governance intelligence
│
├── GovernanceSchemaProvider — locates artifacts
├── GovernanceParser         — extracts graph knowledge
├── DocumentationTarget      — publishes artifacts
│
└── ADR-033: Specific application — PM operations (create/update/transition issues)
```

The contracts are separate but follow identical structural patterns. Adapters for a given
tool (e.g. Jira) will typically implement both the ADR-033 PM contract and the ADR-034
GovernanceParser contract.

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Hardcode Confluence in core | Violates open-core boundary; ties Apache 2.0 code to commercial integration |
| Config-driven parsers (YAML rules) | Too limited for arbitrary source formats; can't handle API responses |
| Single "GovernanceAdapter" that does everything | Too coarse — schema discovery and parsing have different lifecycles and implementers |
| Hardcode Jira parser in raise-core | Pulls Jira dependency into open-source package; pollutes Apache 2.0 core |

## Extension Points Futuros

Los siguientes extension points no están en scope de esta decisión pero emergen naturalmente
del mismo patrón. Se documentan aquí para guiar diseño futuro sin over-engineerear hoy.

---

### `CodeReviewAdapter` — operaciones de pull request

```python
@runtime_checkable
class CodeReviewAdapter(Protocol):
    """Abstrae operaciones de code review (PR/MR) sobre cualquier plataforma."""

    def create_pr(self, branch: str, base: str, spec: PullRequestSpec) -> PullRequestRef: ...
    def get_pr(self, ref: PullRequestRef) -> PullRequest: ...
    def request_review(self, ref: PullRequestRef, reviewers: list[str]) -> None: ...
    def merge(self, ref: PullRequestRef, strategy: MergeStrategy) -> None: ...
```

Entry point group: `rai.adapters.codereview`

**Por qué es necesario:** `rai story-close` hoy no tiene un paso de PR automático. Crear el
PR como parte del ciclo de story-close es el siguiente paso natural — y el destino
(GitHub, GitLab, Azure DevOps, Bitbucket) varía por organización.

| Implementación | Plataforma | Tier |
|---|---|---|
| `GithubCodeReviewAdapter` | GitHub | Community |
| `GitlabCodeReviewAdapter` | GitLab | Community |
| `AzureDevOpsCodeReviewAdapter` | Azure DevOps | Community (Gustavo) |
| `BitbucketCodeReviewAdapter` | Bitbucket | raise-pro |

---

### `NotificationAdapter` — notificaciones a canales del equipo

```python
@runtime_checkable
class NotificationAdapter(Protocol):
    """Envía notificaciones a canales del equipo cuando ocurren eventos de ciclo de vida."""

    def notify(self, event: WorkflowEvent, payload: NotificationPayload) -> None: ...
    def supported_events(self) -> list[WorkflowEvent]: ...
```

Entry point group: `rai.adapters.notify`

**Por qué es necesario:** Visibilidad del equipo sin micromanagement — cuando una story
cierra, cuando Rai aprende un pattern nuevo, cuando hay un bloqueo. El canal varía:
Teams es dominante en enterprise México (banking, telco), Slack en startups.

`WorkflowEvent` incluye: `story.started`, `story.closed`, `pattern.learned`,
`story.blocked`, `epic.closed`, `memory.built`.

| Implementación | Canal | Tier |
|---|---|---|
| `TeamsNotificationAdapter` | Microsoft Teams | raise-pro (enterprise México) |
| `SlackNotificationAdapter` | Slack | raise-pro |
| `WebhookNotificationAdapter` | HTTP webhook genérico | Community |

---

### `CICDAdapter` — integración con pipelines de CI/CD

```python
@runtime_checkable
class CICDAdapter(Protocol):
    """Verifica estado de CI y puede disparar pipelines desde el CLI."""

    def get_pipeline_status(self, ref: PipelineRef) -> PipelineStatus: ...
    def trigger_pipeline(self, pipeline_id: str, params: dict) -> PipelineRef: ...
    def wait_for_completion(self, ref: PipelineRef, timeout_s: int) -> PipelineStatus: ...
```

Entry point group: `rai.adapters.cicd`

**Por qué es necesario:** El gate de calidad antes de story-close hoy es manual (`pytest`,
`pyright`, `ruff`). Con un `CICDAdapter`, `rai story-close` puede verificar que el pipeline
de CI pasó antes de hacer merge — sin salir del flujo de Rai. Es el último eslabón para
un ciclo completamente observable.

| Implementación | Plataforma | Tier |
|---|---|---|
| `GithubActionsAdapter` | GitHub Actions | Community |
| `GitlabCIAdapter` | GitLab CI/CD | Community |
| `AzurePipelinesAdapter` | Azure Pipelines | Community (Gustavo) |
| `JenkinsCIAdapter` | Jenkins (on-prem) | raise-pro (enterprise) |

---

---

### `TriggerAdapter` — vectores de invocación de Rai

Los adapters anteriores manejan *qué hace* Rai. Este maneja *desde dónde* le llega el trabajo.
Hoy Rai solo se invoca desde el CLI. A medida que el producto madura, los eventos externos
deben poder iniciar flujos de Rai sin intervención manual.

```python
@runtime_checkable
class TriggerAdapter(Protocol):
    """Normaliza eventos externos a WorkflowEvent — la capa de entrada de Rai."""

    def listen(self, handler: Callable[[WorkflowTrigger], None]) -> None: ...
    def to_trigger(self, raw_event: dict) -> WorkflowTrigger: ...
```

Entry point group: `rai.adapters.trigger`

```python
class WorkflowTrigger(BaseModel):
    source: str                        # "jira", "github", "slack", "schedule"
    event_type: str                    # "issue.assigned", "pr.reviewed", "cron.daily"
    payload: dict
    suggested_skill: str | None = None # opcional: qué skill debería manejar esto
    context: dict = {}
```

**Patrón inspirado en:** OpenClaw's Channel Adapter — normaliza WhatsApp, Telegram, Discord
a un `UnifiedMessage` antes de llegar al agente. Mismo principio: la lógica de plataforma
no contamina el core.

| Implementación | Trigger | Caso de uso | Tier |
|---|---|---|---|
| `JiraWebhookTrigger` | Issue asignado | "Dame contexto de esta story" | PRO |
| `GitHubWebhookTrigger` | PR reviewed/merged | "Analiza el feedback de este PR" | PRO |
| `SlackTrigger` | Mensaje @rai | "¿Cuál es el estado de RAISE-207?" | PRO |
| `TeamsTrigger` | Mensaje @rai | Mismo caso, canal enterprise | raise-pro |
| `ScheduledTrigger` | Cron | "Resumen diario del equipo" | PRO |

**Nota:** Este adapter no requiere cambios en el core del agente — el `WorkflowTrigger`
normalizado se mapea a una invocación de skill existente. Es solo la capa de entrada.

---

**Nota sobre secuencia:** `CodeReviewAdapter` primero — desbloquea `rai story-close` completo.
`NotificationAdapter` segundo — habilita visibilidad de equipo (PRO dogfooding).
`TriggerAdapter` tercero — habilita workflows event-driven (requiere infraestructura PRO).
`CICDAdapter` cuarto — cierra el loop de calidad, requiere adopción previa del flujo.

---

## Open Questions

1. Should `ArtifactType` and `DocumentType` be extensible enums or string registries?
   (Current draft: extensible via a registry — not Python `Enum`, to allow third-party values)
2. When two parsers both `can_parse` the same locator, first-registered wins. Should there
   be an explicit priority field in the Protocol?
3. Should `rai memory build` warn when a provider returns locators that no parser can handle?
4. **Supply chain risk en el ecosistema de adapters:** OpenClaw tuvo 230 skills maliciosos en
   ClawHub (Feb 2026) — backdoors y infostealers distribuidos como skills legítimos. A medida
   que el ecosistema de adapters de RaiSE crezca, necesitaremos una política de verificación.
   Opciones: firma de paquetes PyPI, review manual para entrada a raise-pro, allowlist para
   enterprise. Diseñar antes de abrir el ecosistema públicamente.

---

*Status: Accepted*
*Created: 2026-02-19 (SES-223)*
*Supersedes: None*
*Extends: ADR-033 (Open-Core Adapter Architecture)*
*Validated by: dogfooding requirement — humansys.ai team + Coppel enterprise pilot*
