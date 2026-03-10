---
id: "ADR-033"
title: "Open-Core Adapter Architecture — Plugin contracts for PM, Repo, and Notify integrations"
date: "2026-02-19"
status: "Accepted"
---

# ADR-033: Open-Core Adapter Architecture

## Context

The Coppel demo (2026-02-19) validated the need for a Jira integration as a core part of the
value proposition: governance that produces traceable artefacts in the PM tool the team already
uses, without replacing it.

Simultaneously, a community contributor (Gustavo) expressed intent to build an Azure DevOps
adapter. And the commercial roadmap (raise-pro) requires a licensed Jira adapter with
enterprise capabilities (team memory, org-level governance trails).

Three constraints shape the decision:

1. **CLI-first philosophy** — adapters must be lightweight CLI tools, not MCP servers.
   Low context overhead, deterministic, no inference required for the adapter layer itself.
2. **Open-core model** — raise-core is MIT-licensed and public. raise-pro is commercial and
   private. The boundary must be clean from day one.
3. **We don't build everything** — the ecosystem builds adapters; we define the contract and
   build the ones that matter most commercially.

## Decision

### 1. Core defines Protocol interfaces — adapters implement them

`raise-core` publishes abstract contracts as Python `Protocol` classes.
No concrete adapter implementation lives in raise-core.

```python
# src/rai_cli/adapters/protocols.py

from typing import Protocol, runtime_checkable

@runtime_checkable
class ProjectManagementAdapter(Protocol):
    """Contract for PM tool integrations (Jira, Azure DevOps, Linear, etc.)"""

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    def update_issue(self, ref: IssueRef, fields: dict) -> IssueRef: ...
    def transition_issue(self, ref: IssueRef, transition: str) -> IssueRef: ...
    def get_issue(self, ref: IssueRef) -> Issue: ...
    def link_issues(self, source: IssueRef, target: IssueRef, link_type: str) -> None: ...
    def log_work(self, ref: IssueRef, time_spent: str, comment: str | None) -> None: ...
```

Pydantic models for `IssueSpec`, `IssueRef`, and `Issue` are published in
`rai_cli.adapters.models` — shared vocabulary between core and all adapters.

### 2. Discovery via Python entry points

Adapters self-register. `rai` discovers them at runtime without configuration.

```toml
# In raise-azuredevops-adapter's pyproject.toml (community package)
[project.entry-points."rai.adapters.pm"]
azure_devops = "rai_azuredevops_adapter:AzureDevOpsAdapter"
```

```python
# In raise-core — adapter registry
from importlib.metadata import entry_points

def get_pm_adapters() -> dict[str, type]:
    return {
        ep.name: ep.load()
        for ep in entry_points(group="rai.adapters.pm")
    }
```

Installing an adapter package is sufficient for `rai` to find it. No manual configuration.

### 3. Three adapter categories (only PM in-scope now)

| Group | Entry point key | In-scope now |
|-------|----------------|--------------|
| Project Management | `rai.adapters.pm` | ✅ Yes |
| Repository | `rai.adapters.repo` | ❌ Later |
| Notification | `rai.adapters.notify` | ❌ Later |

PM is prioritised because it is directly validated by Coppel and required for the pilot.

### 4. Distribution model

| Package | Visibility | License | Maintains |
|---------|-----------|---------|-----------|
| `rai-cli` (raise-core) | Public | MIT | Emilio |
| `raise-jira-adapter` | Private | Commercial | Emilio (raise-pro) |
| `raise-azuredevops-adapter` | Public | MIT | Gustavo (community) |
| `raise-linear-adapter` | Public | MIT | Community |

raise-pro depends on raise-core via `pip install rai-cli>=2.0.2`.
Community adapters depend on raise-core the same way.

### 5. Existing Jira integration

The partial Jira integration built for the Coppel demo is **not discarded**.
It is refactored into `raise-jira-adapter` (raise-pro) following the `ProjectManagementAdapter`
protocol. Nothing from that implementation moves to raise-core except the contracts and models.

### 6. `rai` CLI surface

```bash
rai adapters list          # show installed adapters and their status
rai adapters check jira    # validate credentials and connectivity
```

Configuration (credentials, project keys) lives in `.raise/adapters/<name>.yaml`,
excluded from version control via `.gitignore`.

## Consequences

| Type | Impact |
|------|--------|
| + | Community can build adapters independently against a stable contract |
| + | raise-pro Jira adapter is commercially defensible — same contract, better implementation |
| + | raise-core stays clean — no concrete PM dependency |
| + | Gustavo can start raise-azuredevops-adapter with a published Protocol |
| + | Entry points = zero configuration for the user |
| - | Protocol versioning must be managed carefully — breaking changes affect all adapters |
| - | `rai.adapters.models` is a public API — requires same care as the CLI interface |

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| MCP servers for adapters | Violates CLI-first philosophy; heavy context overhead |
| Adapters bundled in raise-core | Pollutes open-source core with commercial/proprietary integrations |
| Manual config (adapters.yaml lists adapters) | More friction than entry points; non-standard pattern |
| Abstract base classes (ABC) instead of Protocol | Protocol enables structural typing without inheritance; cleaner for community packages |

## Open Questions

1. Protocol versioning — how do we signal breaking changes to community adapter maintainers?
2. Should `rai init` prompt to install a PM adapter if none is detected?
3. Credential storage — `.raise/adapters/<name>.yaml` or system keychain?

---

*Status: Accepted*
*Created: 2026-02-19 (SES-222)*
*Validated by: Coppel demo — Anthony Lopez, Francisco Valenzuela (2026-02-19)*
