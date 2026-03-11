---
id: "ADR-037"
title: "TierContext — Detección de tier y progressive enrichment para UX unificada"
date: "2026-02-20"
status: "Accepted"
---

# ADR-037: TierContext

## Context

ADR-033/034/035 definen los contratos de extensibilidad y la topología de deployment.
ADR-036 define la abstracción del storage del grafo. Todos asumen que el CLI puede
determinar en qué tier está operando para seleccionar el comportamiento correcto.

Hoy ese mecanismo no existe. El CLI no sabe si está en COMMUNITY, PRO, o ENTERPRISE.

Tres problemas concretos resultan de esta ausencia:

1. **No hay selección de backend.** `get_active_backend()` (ADR-036) necesita saber si
   SHARED_MEMORY está disponible para decidir entre `FilesystemGraphBackend` y
   `SupabaseGraphBackend`. Sin TierContext, esa decisión no puede tomarse.

2. **Comandos PRO-exclusivos no tienen UX clara.** Si un developer COMMUNITY corre
   `rai backlog`, ¿qué pasa? Hoy: error críptico (adapter not found). Debería ser:
   mensaje claro que explica qué haría en PRO y cómo activarlo.

3. **Progressive enrichment no tiene un mecanismo.** La promesa de UX — "mismo CLI,
   resultados más ricos en PRO" — requiere que el CLI sepa qué capabilities tiene para
   decidir si enriquecer el resultado o degradar limpiamente.

El constraint fundamental: **COMMUNITY no es un PRO degradado.** Es un tier completo
y first-class. El mecanismo de detección de tier no puede tratar COMMUNITY como "PRO
sin features" — debe tratarlo como el modo natural y predeterminado.

## Decision

### 1. Configuración en `manifest.yaml`

La presencia y contenido de la sección `backend` en `.raise/manifest.yaml` determina el tier:

```yaml
# COMMUNITY — sin sección backend (default, no requiere configuración)
ide:
  type: claude

# PRO — backend configurado en humansys.ai
ide:
  type: claude
tier: pro
backend:
  url: "https://api.humansys.ai"
  auth: token   # token en .raise/adapters/.backend-token (gitignored)

# ENTERPRISE — backend on-prem
ide:
  type: claude
tier: enterprise
backend:
  url: "https://rai.acme.com"
  auth: token
```

Si `backend` no está presente, el CLI opera en COMMUNITY sin fallback, sin error —
COMMUNITY es first-class, no degradado.

### 2. `Capability` enum — qué puede hacer el CLI

```python
# src/rai_cli/tier/capabilities.py

from enum import Enum

class Capability(str, Enum):
    # PRO capabilities
    SHARED_MEMORY = "shared_memory"         # SupabaseGraphBackend disponible
    SEMANTIC_SEARCH = "semantic_search"     # pgvector search disponible
    TEAM_AWARENESS = "team_awareness"       # quién está trabajando en qué
    JIRA_INTEGRATION = "jira_integration"   # ProjectManagementAdapter disponible
    DOCS_PUBLISH = "docs_publish"           # DocumentationTarget a Confluence

    # Enterprise capabilities
    ORG_GOVERNANCE = "org_governance"       # SkillRegistryAdapter, org policies
    AUDIT_LOGGING = "audit_logging"         # AuditAdapter activo
    SSO_AUTH = "sso_auth"                   # SAML/SSO disponible
```

### 3. `TierContext` — el mecanismo

```python
# src/rai_cli/tier/context.py

from dataclasses import dataclass, field
from typing import Literal
from pathlib import Path
from rai_cli.tier.capabilities import Capability

TierLevel = Literal["community", "pro", "enterprise"]

@dataclass
class TierContext:
    tier: TierLevel = "community"
    backend_url: str | None = None
    capabilities: set[Capability] = field(default_factory=set)
    backend_healthy: bool = True

    def has(self, capability: Capability) -> bool:
        """Returns True if the capability is available in the current tier.
        Never raises — callers use this for conditional enrichment."""
        return capability in self.capabilities

    def require_or_suggest(self, capability: Capability) -> None:
        """If capability is available, no-op.
        If not available, prints a helpful message and raises CapabilityUnavailable.
        Never prints a cryptic error — always explains what PRO/Enterprise would do."""
        if self.has(capability):
            return
        _print_upgrade_suggestion(capability, self.tier)
        raise CapabilityUnavailable(capability)

    @classmethod
    def from_manifest(cls, manifest_path: Path = Path(".raise/manifest.yaml")) -> "TierContext":
        """Load TierContext from .raise/manifest.yaml.
        Falls back to COMMUNITY if manifest is missing or has no backend section."""
        ...

    @classmethod
    def community(cls) -> "TierContext":
        """Explicit COMMUNITY context — for testing and CLI operations that don't need tier."""
        return cls(tier="community", capabilities=set())
```

### 4. Capability mapping por tier

```python
TIER_CAPABILITIES: dict[TierLevel, set[Capability]] = {
    "community": set(),  # COMMUNITY no tiene capabilities server-side — todo es local
    "pro": {
        Capability.SHARED_MEMORY,
        Capability.SEMANTIC_SEARCH,
        Capability.TEAM_AWARENESS,
        Capability.JIRA_INTEGRATION,
        Capability.DOCS_PUBLISH,
    },
    "enterprise": {
        # Todo lo de PRO, más:
        Capability.SHARED_MEMORY,
        Capability.SEMANTIC_SEARCH,
        Capability.TEAM_AWARENESS,
        Capability.JIRA_INTEGRATION,
        Capability.DOCS_PUBLISH,
        Capability.ORG_GOVERNANCE,
        Capability.AUDIT_LOGGING,
        Capability.SSO_AUTH,
    },
}
```

Las capabilities también se verifican contra adapters instalados:
`JIRA_INTEGRATION` requiere que `rai.adapters.pm` tenga al menos un adapter registrado.

### 5. Mensajes de upgrade — nunca errores crípticos

```python
CAPABILITY_SUGGESTIONS: dict[Capability, str] = {
    Capability.SHARED_MEMORY: (
        "Team shared memory requires RaiSE PRO.\n"
        "In PRO, `rai memory build` syncs to your team's shared knowledge graph\n"
        "and `rai memory query` searches across all team patterns.\n"
        "→ Upgrade at humansys.ai/upgrade"
    ),
    Capability.JIRA_INTEGRATION: (
        "Jira integration requires RaiSE PRO + raise-jira-adapter.\n"
        "In PRO, `rai backlog` creates and transitions Jira issues from the CLI.\n"
        "Story lifecycle (start/close) syncs automatically to your Jira board.\n"
        "→ Upgrade at humansys.ai/upgrade"
    ),
    Capability.SEMANTIC_SEARCH: (
        "Semantic search requires RaiSE PRO.\n"
        "In PRO, `rai memory query` uses vector similarity over your team graph.\n"
        "Use `--strategy keyword` for local search in COMMUNITY mode.\n"
        "→ Upgrade at humansys.ai/upgrade"
    ),
    # ...
}
```

### 6. Backend health check y degradación

Si el backend está configurado pero no está disponible, el CLI degrada a COMMUNITY
con un warning claro — no falla silenciosamente:

```python
@classmethod
def from_manifest(cls, manifest_path: Path) -> "TierContext":
    config = _load_manifest(manifest_path)

    if "backend" not in config:
        return cls.community()

    tier = config.get("tier", "pro")
    backend_url = config["backend"]["url"]

    # Check backend health
    healthy = _check_backend_health(backend_url)
    if not healthy:
        console.print(
            f"[yellow]⚠ Backend {backend_url} is not reachable.[/yellow]\n"
            f"  Running in COMMUNITY mode (local only).\n"
            f"  Team data will not be included in this session."
        )
        return cls.community()

    capabilities = _resolve_capabilities(tier)
    return cls(tier=tier, backend_url=backend_url, capabilities=capabilities, backend_healthy=True)
```

### 7. Progressive enrichment — el patrón correcto

El patrón de uso en comandos del CLI:

```python
# Pattern A: Conditional enrichment (mismo comando, resultado más rico en PRO)
def build_memory_graph(tier_context: TierContext) -> None:
    graph = _parse_local_sources()          # siempre — COMMUNITY y PRO

    if tier_context.has(Capability.JIRA_INTEGRATION):
        jira_nodes = _parse_jira_sources()  # solo en PRO — enriquece el grafo
        graph.merge(jira_nodes)

    backend = get_active_backend(tier_context)
    backend.persist(graph)                  # filesystem en COMMUNITY, Supabase en PRO


# Pattern B: Hard require (comando exclusivo de PRO — falla con mensaje claro)
def run_backlog_create(issue: IssueSpec, tier_context: TierContext) -> None:
    tier_context.require_or_suggest(Capability.JIRA_INTEGRATION)
    # Si llegamos aquí, el adapter está disponible
    adapter = get_pm_adapter()
    adapter.create_issue(issue)


# Pattern C: Feature flag inline (output diferente según tier)
def format_session_context(tier_context: TierContext) -> str:
    context = _build_local_context()

    if tier_context.has(Capability.TEAM_AWARENESS):
        team_status = _fetch_team_status()  # quién está trabajando en qué
        context += f"\n\n**Team:** {team_status}"

    return context
```

### 8. Inyección en comandos CLI

`TierContext` se construye una vez al inicio de cada comando y se pasa down:

```python
# En el CLI entry point (Typer/Click command)
@app.command()
def memory_build(ctx: typer.Context) -> None:
    tier_context = TierContext.from_manifest()
    build_memory_graph(tier_context)
```

No es un singleton global — se construye por invocación de comando. Esto permite
testear comandos con cualquier tier sin efectos secundarios.

## Consequences

| Tipo | Impacto |
|------|---------|
| + | `get_active_backend()` (ADR-036) puede seleccionar el backend correcto |
| + | Comandos PRO-exclusivos muestran mensajes claros en COMMUNITY |
| + | Progressive enrichment tiene un mecanismo explícito y testeable |
| + | Backend unreachable degrada limpiamente a COMMUNITY con warning |
| + | TierContext es inyectable — fácil de testear con tier mock |
| + | COMMUNITY es first-class — sin degradación silenciosa |
| - | Todos los comandos que usan capabilities necesitan recibir `TierContext` |
| - | Backend health check agrega latencia al inicio de comandos (mitigable con cache) |
| - | `manifest.yaml` se convierte en un archivo de configuración más crítico |

## The Design Principle: Progressive Enrichment

La alternativa rechazada fue **feature gating** — comandos que fallan con error en COMMUNITY.
El feature gating crea dos experiencias divergentes y confunde a developers que upgradean.

El principio adoptado es **progressive enrichment**:

```
COMMUNITY: rai memory query "auth patterns"
           → returns local patterns (fast, offline, always works)

PRO:       rai memory query "auth patterns"
           → returns local + team patterns + semantic results
           (same command, richer results, no workflow change)
```

Para comandos que son genuinamente exclusivos de PRO (rai backlog, rai search semántico),
el mensaje de `require_or_suggest` explica el valor de PRO — no solo "feature not available".
Es marketing contextual, no un error.

## Relationship to other ADRs

```
ADR-035: Backend Deployment Topology — define qué adapters corren dónde
ADR-036: KnowledgeGraphBackend — usa TierContext para seleccionar el backend
ADR-037 (this): TierContext — el mecanismo que hace coherente el modelo de tiers
```

## Alternatives Considered

| Alternativa | Razón para rechazar |
|-------------|---------------------|
| Implicit tier detection (solo por adapter presence) | Frágil — instalar un adapter no implica tener el backend configurado correctamente |
| Environment variables para tier | Menos portable que manifest.yaml; difícil de gitignore selectivamente |
| Hard feature gating (error en COMMUNITY) | Crea experiencias divergentes; confunde al developer que upgradeará |
| Singleton global TierContext | Dificulta el testing; side effects en comandos paralelos |
| Checked en runtime per-call (sin cache) | Health check por cada operación agrega latencia inaceptable |

## Open Questions

1. **Cache de health check:** El backend health check debería cachearse por sesión del CLI
   (no por invocación de comando) para evitar latencia acumulada. ¿Proceso daemon ligero
   o simple TTL cache en filesystem?

2. **Capability discovery vs. config:** ¿Debería el backend reportar sus capabilities
   (`GET /capabilities`) para que el CLI no asuma capacidades según el tier declarado?
   Más flexible, más complejo.

3. **`rai tier status` command:** ¿Vale la pena un comando que muestre el tier activo,
   backend health, y capabilities disponibles? Útil para onboarding y debugging.

---

*Status: Accepted*
*Created: 2026-02-20 (SES-224)*
*Extends: ADR-035 (Backend Deployment Topology), ADR-036 (KnowledgeGraphBackend)*
*Implemented by: RAISE-211 Story 5*
*Enables: UX unificada COMMUNITY/PRO/Enterprise — mismo CLI, resultados más ricos en PRO*
