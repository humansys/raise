# Evidence Catalog: Multi-Instance Jira Configuration in Open Source Tools

> Research date: 2026-03-19
> Decision context: S494.4 — extending `jira.yaml` with `instances:` section

---

## E1: jira-cli (ankitpokhrel/jira-cli)

| Field | Value |
|-------|-------|
| **Source** | [GitHub](https://github.com/ankitpokhrel/jira-cli), [Wiki](https://github.com/ankitpokhrel/jira-cli/wiki/Installation) |
| **Stars** | 5,347 |
| **Last push** | 2026-01-20 |
| **Evidence level** | High (widely used, active, Go CLI) |
| **Multi-instance approach** | **Multiple config files** |

**Key findings:**
- No native multi-instance support in a single config file
- Uses `--config/-c` flag or `JIRA_CONFIG_FILE` env var to switch between config files
- Each config file contains one instance's settings (server, auth, default project/board)
- Workaround: maintain separate `.jira-instance1.yml`, `.jira-instance2.yml` files
- Per-command switching: `jira issue list -c ./local_jira_config.yaml`

**Schema pattern:** Single-instance flat YAML, external switching via flag/env var.

---

## E2: python-jira (pycontribs/jira)

| Field | Value |
|-------|-------|
| **Source** | [GitHub](https://github.com/pycontribs/jira), [Docs](https://jira.readthedocs.io/examples.html) |
| **Stars** | 2,105 |
| **Last push** | 2026-03-18 |
| **Evidence level** | High (de facto Python Jira library) |
| **Multi-instance approach** | **Multiple client instances** |

**Key findings:**
- Library, not CLI — no config file, instances created programmatically
- Each `JIRA(server=..., basic_auth=...)` is an independent connection
- No config-level multi-instance abstraction — consumer code manages routing
- Auth is per-instance (basic, OAuth 1.0, PAT)

**Schema pattern:** N/A (programmatic). Consumer creates N client objects.

---

## E3: go-jira (go-jira/jira)

| Field | Value |
|-------|-------|
| **Source** | [GitHub](https://github.com/go-jira/jira), [Issue #138](https://github.com/go-jira/jira/issues/138) |
| **Stars** | 2,737 |
| **Last push** | 2025-11-11 |
| **Evidence level** | High (mature Go CLI) |
| **Multi-instance approach** | **Directory-hierarchy config merging** |

**Key findings:**
- `.jira.d/config.yml` files discovered by walking parent directories
- Closest config wins (override by proximity)
- Structure: `$HOME/company1/.jira.d/config.yml`, `$HOME/company2/.jira.d/config.yml`
- Running `jira` under `~/company1/` auto-discovers that instance's config
- Also supports `-e` flag for endpoint override
- Operation-specific configs: `.jira.d/foo.yml` with different endpoints per command

**Schema pattern:** Single-instance per config file, implicit routing via filesystem hierarchy.

---

## E4: terraform-provider-jira (fourplusone/terraform-provider-jira)

| Field | Value |
|-------|-------|
| **Source** | [GitHub](https://github.com/fourplusone/terraform-provider-jira), [Registry](https://registry.terraform.io/providers/fourplusone/jira/latest) |
| **Stars** | 183 |
| **Last push** | 2024-02-26 |
| **Evidence level** | Medium (niche, low activity) |
| **Multi-instance approach** | **Terraform provider aliases** |

**Key findings:**
- Standard Terraform pattern: multiple `provider "jira"` blocks with `alias`
- Each alias has its own `url`, `user`, `password`
- Resources reference instance via `provider = jira.instance2`
- Auth via env vars (`JIRA_URL`, `JIRA_USER`, `JIRA_PASSWORD`) or inline HCL

**Schema pattern:**
```hcl
provider "jira" {
  url = "https://instance1.atlassian.net"
}
provider "jira" {
  alias = "instance2"
  url   = "https://instance2.atlassian.net"
}
resource "jira_issue" "x" {
  provider = jira.instance2
}
```

**Routing:** Explicit per-resource `provider` attribute.

---

## E5: Backstage Jira Dashboard Plugin (AxisCommunications)

| Field | Value |
|-------|-------|
| **Source** | [GitHub](https://github.com/AxisCommunications/backstage-plugins/blob/main/plugins/jira-dashboard/README.md) |
| **Stars** | 40 (plugin repo) |
| **Last push** | 2026-02-24 |
| **Evidence level** | Medium (niche but well-designed pattern) |
| **Multi-instance approach** | **Named instances array + annotation routing** |

**Key findings:**
- `instances:` array in `app-config.yaml`, each with `name`, `token`, `baseUrl`
- First instance named `"default"` — backward compatible
- Entity routes to instance via annotation: `jira.com/project-key: instance-name/PROJECT`
- Slash-separated prefix: `another-instance/ABC` routes to `another-instance`
- Omitting prefix routes to `default`
- Per-instance: `token`, `baseUrl`, `apiUrl`, `headers`, `userEmailSuffix`, `cacheTtl`

**Schema pattern:**
```yaml
jiraDashboard:
  instances:
    - name: default
      token: ${JIRA_TOKEN}
      baseUrl: https://team1.atlassian.net/rest/api/3/
    - name: other
      token: ${OTHER_TOKEN}
      baseUrl: https://team2.atlassian.net/rest/api/3/
```

**Routing:** Annotation-based, `instance-name/project-key` format.

---

## E6: Jenkins Jira Plugin

| Field | Value |
|-------|-------|
| **Source** | [Jenkins Plugin](https://plugins.jenkins.io/jira/), [Atlassian Docs](https://support.atlassian.com/jira-cloud-administration/docs/how-jenkins-for-jira-works/) |
| **Stars** | N/A (Jenkins ecosystem) |
| **Last push** | Active |
| **Evidence level** | High (widely used CI integration) |
| **Multi-instance approach** | **UI-registered sites + explicit `site` parameter** |

**Key findings:**
- Multiple sites added via Jenkins UI (Manage Jenkins > Configure System)
- Each site: URL, client ID, secret
- Pipeline steps accept `site` parameter to target specific instance
- Without `site`, events go to all configured sites (broadcast)
- Limitation: "select 1 site at a time" for some operations

**Schema pattern:** Flat list of sites in Jenkins config, routing via `site` parameter in pipeline DSL.

---

## E7: Appfire ACLI (Atlassian CLI)

| Field | Value |
|-------|-------|
| **Source** | [Appfire](https://appfire.com/products/acli), [Docs](https://appfire.atlassian.net/wiki/spaces/ACLI/pages/60562817) |
| **Stars** | N/A (commercial) |
| **Last push** | Active (commercial product) |
| **Evidence level** | High (official Atlassian ecosystem tool) |
| **Multi-instance approach** | **Named aliases in properties file + regex matching** |

**Key findings:**
- `acli.properties` file with named aliases:
  ```properties
  ban = jiracloud -s https://bobswift.atlassian.net ${credentials.cloud}
  wan = jiracloud -s https://wittified.atlassian.net ${credentials.cloud}
  ```
- Regex-based matching for dynamic site discovery:
  ```properties
  ([a-z0-9]+.atlassian.net) = jiracloud -s https://$1 ${credentials.cloud}
  ```
- Exact match wins first, then regex
- Credential groups via `${credentials.cloud}` / `${credentials.server}`
- `acli-private.properties` for secrets (via include)
- Shareable config files for CI environments

**Schema pattern:** Named aliases with credential references, optional regex catch-all.

---
