# E11: Monorepo Consolidation — Design

## Gemba (Current State)

```
raise-commons/ (GitLab)                  ← framework repo
├── src/raise_cli/                       ← CLI + library (root package)
├── src/raise_core/                      ← protocols, models
├── src/raise_pro/                       ← PRO extensions
├── src/raise_server/                    ← server
├── pyproject.toml                       ← single package: raise-cli
└── .gitlab-ci.yml

/home/emilio/Code/rai/ (GitHub)          ← personal instance
├── src/rai_agent/
│   ├── daemon/          (20 files)      ← PRODUCT
│   ├── knowledge/       (9 files)       ← PRODUCT
│   ├── scaleup/         (14 files)      ← PRIVATE
│   └── inference.py                     ← PRODUCT
└── pyproject.toml
```

## Target State

```
raise-commons/ (GitLab)                  ← monorepo
├── packages/
│   ├── raise-core/
│   │   ├── src/raise_core/
│   │   └── pyproject.toml               ← independent package
│   ├── raise-cli/
│   │   ├── src/raise_cli/
│   │   └── pyproject.toml               ← depends on raise-core
│   ├── rai-agent/
│   │   ├── src/rai_agent/
│   │   │   ├── daemon/    (20 files)
│   │   │   ├── knowledge/ (9 files)
│   │   │   └── inference.py
│   │   └── pyproject.toml               ← depends on raise-cli
│   ├── raise-pro/
│   │   ├── src/raise_pro/
│   │   └── pyproject.toml               ← depends on raise-cli
│   └── raise-server/
│       ├── src/raise_server/
│       └── pyproject.toml               ← depends on raise-pro
├── pyproject.toml                        ← uv workspace root
├── docker/
│   └── rai-agent/
│       ├── Dockerfile
│       └── docker-compose.yml
└── .gitlab-ci.yml                        ← workspace-aware

/home/emilio/Code/rai/ (GitHub)           ← personal instance (cleaned)
├── src/rai_agent/
│   └── scaleup/         (14 files)       ← domain-specific only
├── pyproject.toml                         ← depends on rai-agent package
└── .raise/
```

## Package Dependency Direction

```
raise-core
  ↑
raise-cli ←── raise-pro
  ↑              ↑
rai-agent    raise-server
```

Rule: dependencies flow upward only. No cycles. No reverse deps.

## uv Workspace Configuration

```toml
# raise-commons/pyproject.toml (workspace root)
[tool.uv.workspace]
members = [
    "packages/raise-core",
    "packages/raise-cli",
    "packages/rai-agent",
    "packages/raise-pro",
    "packages/raise-server",
]
```

Each member has its own `pyproject.toml` with independent version and deps.
`uv sync` resolves all workspace members together.

## rai-agent pyproject.toml

```toml
[project]
name = "rai-agent"
version = "0.1.0"
description = "Autonomous personal agent on RaiSE infrastructure"
license = "Apache-2.0"
dependencies = [
    "raise-cli",
    "fastapi[standard]>=0.115",
    "claude-agent-sdk==0.1.48",
    "pydantic>=2.0",
    "structlog>=24.0",
    "cryptography>=43.0",
]

[project.optional-dependencies]
telegram = ["python-telegram-bot>=20.0", "telegramify-markdown~=1.1"]
gchat = []
scheduling = ["apscheduler>=4.0.0a5", "aiosqlite>=0.20", "sqlalchemy>=2.0"]
```

## Jira Structure (final)

```
humansys.atlassian.net
├── STRAT: Initiatives (STRAT-24..28) ↔ Objectives
└── RAISE: All development
    ├── component: raise-community (framework OSS)
    ├── component: raise-pro (commercial)
    └── component: rai-agent (agent OSS)

rai-agent.atlassian.net (→ rai-jinkoniwashi.atlassian.net)
├── RAI: Personal agent backlog (migrated epics labeled)
└── LIFE: Personal life management
```

## Key Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Monorepo over multi-repo | 5-dev team, cross-repo overhead > benefit |
| 2 | uv workspaces | AutoGen pattern, native Python tooling |
| 3 | Single RAISE Jira project | Eliminates cross-project linking friction |
| 4 | Components for packages | Filterable in boards, Easy Agile compatible |
| 5 | Selective CI/CD per package | Only publish changed packages |
| 6 | Phase 4 only after Phase 2-3 verified | Irreversible personal repo cleanup |
