---
epic_id: RAISE-301
name: Agent Tool Abstraction
branch: epic/e301/agent-tool-abstraction
parent: dev
created: 2026-02-26
status: design
absorbs: [RAISE-141, RAISE-208]
---

# Epic Brief: Agent Tool Abstraction

## Hypothesis

**If** we provide abstract CLI commands for backlog management and document publishing,
**then** AI agents can operate platform-agnostic workflows without knowing Jira IDs, Confluence APIs, or adapter specifics,
**resulting in** reduced friction, faster execution, and portable governance across any PM/docs platform.

## Boundaries

- **In scope:** CLI commands, adapter implementations (Jira, Confluence), skill auto-sync, config mapping
- **Out of scope:** GitLab/Odoo adapters (deferred), bidirectional sync (Phase 2), real-time webhooks
- **Foundation:** RAISE-211 (protocols + registry), ADR-033/034, 6 research streams
