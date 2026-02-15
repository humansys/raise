---
id: "ADR-028"
title: "Entity Schema Design - Entity Properties for Sync Metadata"
date: "2026-02-14"
status: "Accepted"
epic: "E-DEMO"
---

# ADR-028: Entity Schema Design - Entity Properties for Sync Metadata

## Contexto

Sync metadata (last sync time, RaiSE IDs, sync status) necesita persistirse en JIRA para rastrear qué ha sido sincronizado y detectar cambios. Opciones:

1. **JIRA Entity Properties:** 32KB JSON storage per issue/epic, JQL-queryable
2. **JIRA Custom Fields:** User-visible fields, configurable per project
3. **External Database:** SQLite/PostgreSQL separado tracking sync state
4. **Comments/Labels:** Metadata in comments or labels (abusive)

Tensiones:
- **Visibility:** Entity properties son invisibles para usuarios (good para metadata interna)
- **Performance:** Custom fields afectan JIRA UI performance con muchos fields
- **Queryability:** Entity properties son JQL-queryable (filtrar por sync state)
- **Portability:** External DB requiere mantener dos fuentes de verdad

**Research foundation:** `/work/research/jira-bidirectional-sync/` (32 sources, Very High evidence)

## Decisión

**Use JIRA Entity Properties for sync metadata. Store RaiSE-specific data as JSON in entity properties, invisible to JIRA users but queryable via JQL.**

**Schema (Full Granularity):**
```json
{
  "rai_sync": {
    "epic_id": "E-DEMO",
    "story_id": "S-DEMO.1",
    "task_id": "T-DEMO.1.1",        // Only for JIRA subtasks
    "last_sync_at": "2026-02-14T10:30:00Z",
    "sync_version": "1",
    "rai_branch": "demo/atlassian-webinar",
    "local_path": "/home/emilio/Code/raise-commons",

    // Task-specific metadata (for subtasks)
    "task_status": "in_progress",   // pending, in_progress, done
    "task_blocked": false,
    "estimated_sp": 0.5,

    // Forge-ready metadata
    "sync_direction": "push",       // push, pull, bidirectional (V3)
    "last_modified_by": "rai"       // rai, jira (for conflict detection)
  }
}
```

**Entity property key:** `com.humansys.raise.sync` (namespaced to avoid collisions)

**Storage location in JIRA:**
- Issue entity properties: `/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}`
- Epic entity properties: Same endpoint (epics are issues in JIRA)

**Idempotency check:**
```python
# Before creating issue, check if already synced
props = jira.get_issue_property(issue_key, "com.humansys.raise.sync")
if props and props["rai_sync"]["epic_id"] == local_epic_id:
    # Already synced, skip creation
    return
```

**Forge Intelligence Support:**

Entity properties enable cross-project intelligence in Rai in Forge (V3):

1. **Stable cross-project IDs:** `epic_id`, `story_id`, `task_id` are RaiSE-internal (E-DEMO works across all projects)
2. **Metadata aggregation:** Forge queries JIRA entity properties across all org projects
3. **Pattern recognition:** `estimated_sp` vs `actual_sp` → velocity patterns
4. **Blocker detection:** `task_blocked` + `blocker_reason` → systemic blockers
5. **Sync direction tracking:** `last_modified_by` → who changed what (conflict detection)

**Example Forge query:**
```jql
// Find all OAuth tasks blocked across organization
project in (PROJ1, PROJ2, PROJ3)
AND issue.property[com.humansys.raise.sync].rai_sync.task_id ~ "oauth"
AND issue.property[com.humansys.raise.sync].rai_sync.task_blocked = true
```

This returns all blocked OAuth tasks across projects → Forge analyzes patterns → recommends solutions.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Invisible to JIRA users (no UI clutter) |
| ✅ Positivo | 32KB storage per entity (sufficient for metadata) |
| ✅ Positivo | JQL-queryable (filter synced vs unsynced items) |
| ✅ Positivo | No JIRA admin configuration required (works out-of-box) |
| ✅ Positivo | Namespaced key prevents collisions with other apps |
| ⚠️ Negativo | Requires API calls to read/write (but necessary for sync anyway) |
| ⚠️ Negativo | Not visible in JIRA UI (debugging harder) — mitigated by CLI query command |
| ⚠️ Negativo | 32KB limit (sufficient for metadata, but not unlimited) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| **Custom Fields** | Visible to users (UI clutter). Requires JIRA admin configuration. Affects JIRA performance with many fields. |
| **External Database (SQLite/PostgreSQL)** | Two sources of truth (local DB + JIRA). Sync state could drift. Added complexity. |
| **Comments** | Abusive use of comments feature. Not queryable efficiently. Pollutes issue history. |
| **Labels** | Limited to single strings (no structured data). Not invisible (users see labels). |
| **Description Embedding** | Fragile (users can edit descriptions). Not queryable. Parser complexity. |

---

<details>
<summary><strong>Referencias</strong></summary>

**Research:**
- `/work/research/jira-bidirectional-sync/recommendation.md` - Entity properties best practice (HIGH confidence, 32 sources)
- [Jira entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/) - Official docs (Very High evidence)

**Key findings from research:**
- **32 KB JSON storage:** Sufficient for metadata (our schema ~200 bytes)
- **JQL-queryable:** Can filter issues by entity property values
- **No JIRA performance impact:** Entity properties don't affect UI rendering
- **Standard practice:** Exalate, Unito, Zapier all use entity properties for sync metadata

**Implementation:**
- Property key: `com.humansys.raise.sync` (namespaced to Humansys domain)
- Schema version: `sync_version: "1"` (allows schema evolution)
- Read endpoint: `GET /rest/api/3/issue/{issueIdOrKey}/properties/com.humansys.raise.sync`
- Write endpoint: `PUT /rest/api/3/issue/{issueIdOrKey}/properties/com.humansys.raise.sync`

**JQL query examples:**
```jql
# Find all issues synced from RaiSE
issue.property[com.humansys.raise.sync].rai_sync.epic_id is not EMPTY

# Find issues synced from specific epic
issue.property[com.humansys.raise.sync].rai_sync.epic_id = "E-DEMO"
```

**CLI query command (future):**
```bash
rai backlog sync-status --provider jira
# Shows: Epic E-DEMO → 5 stories synced, last sync 2h ago
```

</details>
