# Multi-Instance Jira Configuration: Pattern Synthesis

> Research date: 2026-03-19
> Decision context: S494.4 — extending `jira.yaml` with `instances:` section
> Sources: 7 tools analyzed (see `sources/evidence-catalog.md`)

---

## 1. Convergent Patterns

### Pattern A: Named Instances (strongest convergence)

**Used by:** Backstage Jira Dashboard, Terraform (via aliases), Jenkins (via sites), ACLI (via aliases)

The dominant pattern across tools that explicitly support multi-instance is a **named list of instances**, each with its own URL and credentials:

```yaml
instances:
  - name: default    # or "primary" — backward-compatible fallback
    url: https://team1.atlassian.net
    auth: ...
  - name: other
    url: https://team2.atlassian.net
    auth: ...
```

**Key properties:**
- One instance is marked as `default` (explicit name or first-in-list)
- Each instance is self-contained (URL + auth + optional settings)
- Backward compatibility: single-instance configs work without `instances:` key

**Evidence strength:** High (4/7 tools converge on this, including the most mature ones)

### Pattern B: Explicit Project-to-Instance Routing

**Used by:** Backstage (annotation prefix), Terraform (provider attribute), Jenkins (site parameter), ACLI (alias on command line)

No tool discovered uses automatic project-to-instance discovery. Routing is always **explicit**:

| Tool | Routing Mechanism |
|------|-------------------|
| Backstage | `instance-name/project-key` in entity annotation |
| Terraform | `provider = jira.alias` on each resource |
| Jenkins | `site: "name"` parameter in pipeline step |
| ACLI | Alias name as command prefix |
| go-jira | Filesystem directory determines instance |
| jira-cli | Config file flag determines instance |

**Evidence strength:** Very High (7/7 tools use explicit routing, 0/7 use discovery)

### Pattern C: Per-Instance Auth (no global state mutation)

**Used by:** All 7 tools

Every tool keeps auth credentials scoped to the instance/connection:

- python-jira: each `JIRA()` object has its own auth
- Backstage: each instance entry has its own `token`
- Terraform: each provider block has its own `user`/`password`
- ACLI: credential groups referenced per alias

**No tool mutates global auth state to switch instances.**

**Evidence strength:** Very High (7/7 tools converge)

---

## 2. Divergent Approaches (less common)

### Directory-Hierarchy Discovery (go-jira only)
- Config discovered by walking parent directories
- Elegant for developer workflows but not portable to project-level config files
- Not applicable to our use case (we have one config per project)

### Multiple Config Files (jira-cli only)
- Separate files per instance, switched via flag/env var
- Simple but doesn't scale — user must remember which file maps to which instance
- Not applicable (we want one `jira.yaml`)

### Regex-Based Matching (ACLI only)
- Powerful for large enterprises with many sites
- Over-engineered for our 2-instance case
- Interesting for future if we scale to many instances

---

## 3. Common Pitfalls Documented

1. **No default instance defined** — tools that require explicit routing on every operation become verbose. Backstage and Terraform both have a "default" concept to avoid this.

2. **Credential leakage in shared configs** — ACLI addresses this with separate `acli-private.properties` via include. Backstage uses `${ENV_VAR}` substitution. Credential separation is table stakes.

3. **Broadcast behavior** — Jenkins sends events to ALL configured sites when no `site` parameter given. This is surprising and causes duplicate data. Explicit routing is safer than broadcast.

4. **Breaking backward compatibility** — All tools that added multi-instance later had to maintain single-instance config as valid. Migration path matters.

---

## 4. Recommendation for `jira.yaml`

### Schema Design

Based on convergent patterns (A + B + C), the recommended schema is:

```yaml
# jira.yaml — multi-instance configuration
instances:
  - name: humansys              # named instance (used for routing)
    url: https://humansys.atlassian.net
    user_env: JIRA_USER_HUMANSYS
    token_env: JIRA_TOKEN_HUMANSYS
    default: true               # fallback when no instance specified

  - name: rai-agent
    url: https://rai-agent.atlassian.net
    user_env: JIRA_USER_RAI
    token_env: JIRA_TOKEN_RAI

# Project-to-instance routing (explicit mapping)
projects:
  RAISE: humansys
  RAI: humansys
  AGENT: rai-agent

# Backward compatibility: if no `instances:` key, treat
# top-level url/user_env/token_env as single default instance
```

### Design Rationale

| Decision | Rationale | Evidence |
|----------|-----------|----------|
| Named instances array | Strongest convergence (4/7 tools) | E4, E5, E6, E7 |
| Explicit project mapping | 7/7 tools use explicit routing, 0/7 use discovery | All |
| `default: true` flag | Avoids broadcast pitfall (E6), reduces verbosity | E5, E6 |
| `*_env` for credentials | Credential separation (E7 pattern), no secrets in config | E5, E7 |
| Backward-compatible fallback | Migration path required (pitfall #4) | E5 |
| No regex matching | Over-engineered for 2 instances; revisit if needed | E7 |

### Auth Strategy

- **Per-instance env vars** (not global state mutation) — convergent across all 7 tools
- Config stores env var *names*, not values
- Runtime resolves `os.environ[instance.token_env]` per request
- No connection pooling needed at our scale

### Routing Strategy

- **Explicit project-to-instance mapping** in `projects:` section
- Lookup: `projects.get(project_key)` -> instance name -> instance config
- Unknown project -> default instance (with warning log)
- No discovery, no broadcast
