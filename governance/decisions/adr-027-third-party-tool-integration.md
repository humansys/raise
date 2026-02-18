---
id: ADR-027
title: Third-Party Tool Integration via Static Config Files
status: accepted
date: 2026-02-18
decision_makers: [emilio]
story: RAISE-173
---

# ADR-027: Third-Party Tool Integration via Static Config Files

## Context

RaiSE agents interact with third-party tools (Jira, Snyk, SonarQube, GitLab CI, Slack, etc.) through MCP servers. Each interaction requires knowledge of tool-specific configuration: project keys, workflow states, transition IDs, team identifiers, API endpoints, severity mappings, and quality gate thresholds.

Without a deterministic reference, agents must **discover this configuration at runtime** — querying APIs, parsing responses, and inferring mappings. This burns tokens, produces non-deterministic results, and creates fragile workflows that break when API responses change format.

**Problem observed with Jira MCP:**
- Querying workflow states costs ~500 tokens per call
- Team member lookup requires trial-and-error (email vs account_id vs display name)
- Transition IDs are opaque integers that must be discovered each session
- Reserved words in JQL (`RAISE` must be quoted) cause silent failures

These same problems will repeat with every new tool integration (Snyk, SonarQube, GitLab CI, etc.).

## Decision

**All third-party tool integrations MUST create a static config file at `.raise/{tool}.yaml` following the Just-in-Time External Config pattern (documented in `governance/architecture/system-design.md`).**

### Config File Structure

Every `.raise/{tool}.yaml` file MUST contain:

```yaml
# {Tool} Configuration for {project-name}
# Used by rai-cli and AI agents to interact with {Tool} without token-expensive discovery.
# Deterministic reference — agents read this instead of querying APIs each time.

# ─── Connection ─────────────────────────────────────────────────────────────
# How to reach the tool. NOT secrets — those go in environment variables.

connection:
  # Tool-specific connection info (URLs, project keys, etc.)
  # NEVER include tokens, passwords, or API keys here

# ─── Mappings ───────────────────────────────────────────────────────────────
# Tool-specific identifiers that agents need to interact correctly.

# (Tool-specific sections follow — see examples below)

# ─── Usage Notes for Agents ─────────────────────────────────────────────────
# How agents should use this config. Include gotchas and edge cases.
```

### Integration Checklist

When adding a new third-party tool:

1. **Create config file:** `.raise/{tool}.yaml` with connection, mappings, and agent usage notes
2. **Add pointer to CLAUDE.md:** One line under `## External Integrations` — name + path + what it contains
3. **Document in skills:** Skills that use the tool read the config just-in-time (not at session-start)
4. **No secrets in config:** API keys, tokens, passwords go in environment variables (`.env`, vault, CI secrets)
5. **Test the identifiers:** Verify that all IDs, keys, and mappings actually work before committing
6. **Document gotchas:** Edge cases go in the `Usage Notes for Agents` section (e.g., reserved words, identifier format quirks)

### Three-Layer Loading Pattern

```
Layer 1: CLAUDE.md (always loaded, ~1 line per tool)
  → "Snyk config: .raise/snyk.yaml — severity mappings, project IDs, ignore policies"

Layer 2: Session-start (mentions availability, does NOT load content)
  → "Snyk config available at .raise/snyk.yaml if needed"

Layer 3: Skill (reads full config just-in-time when needed)
  → story-close reads snyk.yaml to check vulnerability gate before merge
```

### Security Boundary

| Goes in `.raise/{tool}.yaml` | Goes in `.env` / secrets |
|------------------------------|-------------------------|
| Project keys, IDs | API tokens |
| Workflow states, transition IDs | OAuth secrets |
| Team member identifiers | Passwords |
| Severity mappings | Webhook secrets |
| Quality gate thresholds | Encryption keys |
| URL patterns (public) | Private endpoint URLs |

## Examples

### Existing: `.raise/jira.yaml`

```yaml
projects:
  RAISE:
    name: RAISE
    category: Development
workflow:
  states:
    - name: In Progress
      id: 31
  lifecycle_mapping:
    story_start: 31
team:
  - name: Aquiles Lázaro
    identifier: "557058:890eb66c-..."
    role: devops
issue_types:
  - Sub-task   # NOT 'Subtask' — learned the hard way
```

### Template: `.raise/snyk.yaml`

```yaml
# Snyk Configuration for raise-commons
# Deterministic reference for security scanning integration.

connection:
  org_id: "{snyk-org-id}"           # from Snyk dashboard → Settings → General
  project_ids:
    raise_cli: "{project-id}"       # rai-cli Python project

severity_mapping:
  # Map Snyk severities to RaiSE quality gate actions
  critical: block     # Block merge, must fix
  high: block         # Block merge, must fix
  medium: warn        # Warn but allow merge
  low: ignore         # Log only

quality_gates:
  # Thresholds for the publish skill gate
  max_critical: 0     # Zero tolerance
  max_high: 0         # Zero tolerance
  max_medium: 5       # Allow up to 5 medium
  license_compliance: true  # Block non-compliant licenses

ignore_policies:
  # Known acceptable vulnerabilities (with justification)
  # - id: SNYK-PYTHON-XXX
  #   reason: "Test dependency only, not in production"
  #   expires: 2026-06-01

# ─── Usage Notes for Agents ─────────────────────────────────────────────────
#
# To check vulnerabilities before publish:
#   Read this file, then call snyk test with the org_id and project_id.
#   Compare results against severity_mapping and quality_gates.
#
# To add an ignore:
#   Add to ignore_policies with reason and expiry date.
#   Ignores without expiry are not allowed.
```

### Template: `.raise/sonarqube.yaml`

```yaml
# SonarQube Configuration for raise-commons
# Deterministic reference for code quality gate integration.

connection:
  server_url: "https://sonar.humansys.ai"  # Public URL, not secret
  project_key: "raise-commons"

quality_gates:
  coverage_minimum: 90          # Matches MUST-TEST-001 guardrail
  duplicated_lines_max: 3.0     # Percentage
  maintainability_rating: "A"   # A-E scale
  reliability_rating: "A"
  security_rating: "A"
  security_hotspots_reviewed: 100  # Percentage

# ─── Usage Notes for Agents ─────────────────────────────────────────────────
#
# Quality gate check in publish skill:
#   Read this file, compare against latest Sonar analysis.
#   If any threshold is violated, block publish and report which metric failed.
#
# Coverage threshold aligns with guardrails.md MUST-TEST-001.
```

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| **Discover at runtime via API** | Always fresh | Burns 500+ tokens per query, non-deterministic, fragile |
| **Hardcode in skills** | Simple | Config changes require skill updates, not portable across repos |
| **Store in memory graph** | Queryable | Static facts don't belong in accumulated knowledge graph |
| **Environment variables only** | Standard | Can't represent structured data (mappings, lists, thresholds) |
| **CLAUDE.md inline** | Always available | Wastes context tokens every session; clutters the file |

## Consequences

### Positive

- Zero-token discovery — agents read a file instead of querying APIs
- Deterministic — same config always produces same behavior
- Portable — each repo carries its own tool config (different teams, different workflows)
- Auditable — config changes are tracked in git
- Composable — add new tools by adding new `.yaml` files, one CLAUDE.md line, and skill reads

### Negative

- Config can drift from actual tool state (mitigated: agents can validate and flag)
- Manual creation required for each new tool (mitigated: templates in this ADR)
- Not auto-discovered — new team members must be told about `.raise/` (mitigated: CLAUDE.md pointer)

### Risks

- **Stale config:** Team member leaves but identifier stays in yaml → agent assigns to ghost. Mitigation: periodic reconciliation (monthly or on team change).
- **Secret leakage:** Developer puts API key in yaml instead of .env. Mitigation: `detect-secrets` pre-commit hook scans `.raise/` directory.

## References

- Pattern: Just-in-Time External Config (`governance/architecture/system-design.md`)
- Existing implementation: `.raise/jira.yaml`
- Guardrails: `MUST-SEC-001` (no secrets in code)
- Constitution: §2 (Governance as Code — config versioned in git)
