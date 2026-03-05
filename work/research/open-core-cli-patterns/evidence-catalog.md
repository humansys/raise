# Evidence Catalog: Open-Core CLI Patterns

## Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 1 | [Docker CLI Plugin Architecture (DeepWiki)](https://deepwiki.com/docker/cli/3-plugin-architecture) | Primary | Very High | Docker uses separate binaries with `docker-` prefix. Plugins appear as native commands. Discovery via filesystem directories, not code. Commercial plugins (Scout) install alongside OSS ones seamlessly. |
| 2 | [click-plugins (PyPI)](https://pypi.org/project/click-plugins/) | Primary | High | Python ecosystem standard for CLI plugin discovery via setuptools entry_points. BrokenCommand pattern for graceful degradation. Used by GDAL, Rasterio, Fiona. |
| 3 | [click-plugins (GitHub)](https://github.com/click-contrib/click-plugins) | Primary | High | Core decorator `@with_plugins(iter_entry_points('group'))` on click.group(). Failed plugins become BrokenCommand, don't crash CLI. Plugins register in any subgroup. |
| 4 | [Terraform CLI-driven workflow (HashiCorp)](https://developer.hashicorp.com/terraform/enterprise/run/cli) | Primary | Very High | Same binary, same commands (plan, apply). Behavior changes based on backend config (local vs Cloud vs Enterprise). No separate "enterprise commands" — enterprise is a backend, not a command set. |
| 5 | [Pulumi OSS vs Cloud (Pulumi docs)](https://www.pulumi.com/docs/iac/concepts/pulumi-cloud/) | Primary | Very High | Same CLI binary, Apache 2.0. Commercial features activate via backend choice and `pulumi policy` packs. Local policy execution is OSS, centralized management is Cloud. |
| 6 | [GitLab CLI glab (GitLab docs)](https://docs.gitlab.com/cli/) | Primary | High | Single OSS binary (MIT). Premium features (Duo AI) gated by server-side license, not CLI code. CLI itself is fully open source. |
| 7 | [dbt Core vs Cloud CLI (dbt Labs)](https://www.getdbt.com/blog/a-closer-look-at-the-newly-launched-dbt-cloud-cli) | Primary | High | Two separate binaries: `dbt` (Core, OSS) and `dbt` (Cloud CLI, thin wrapper over Cloud APIs). Same command names but different execution backends. Caused user confusion. |
| 8 | [Click Entry Points docs](https://click.palletsprojects.com/en/stable/entry-points/) | Primary | Very High | Official Click documentation on entry point pattern for distributing CLI plugins across packages. |
| 9 | [Open-core model (Wikipedia)](https://en.wikipedia.org/wiki/Open-core_model) | Secondary | Medium | Open-core = free core + proprietary add-ons. Enterprise features typically: scalability, integrations, security, SSO. Plugin architecture is the standard mechanism. |
| 10 | RaiSE codebase: `registry.py` + `adapters.py` | Primary (internal) | Very High | Already has entry_point discovery for 5 adapter groups. `rai adapters list/check` validates them. Pattern is established and working. |
| 11 | RaiSE codebase: existing `backlog.py` | Primary (internal) | Very High | 4 commands (auth/pull/push/status) hard-import `rai_pro.*`. Fail with "rai-pro required" if not installed. No graceful degradation — just crash. |

## Patterns Identified

### Pattern A: "Same Command, Different Backend" (Terraform, Pulumi)
- Same CLI binary, same commands
- Commercial features activate via configuration (backend, license)
- CLI code is 100% OSS
- Commercial value is in the server/service, not the CLI

### Pattern B: "Plugin Discovery" (Docker, click-plugins, RaiSE existing)
- Core CLI discovers extensions via filesystem or entry points
- Plugins register commands that appear native
- Failed/missing plugins degrade gracefully (BrokenCommand or skip)
- Commercial plugins are just another package providing entry points

### Pattern C: "Separate Binary" (dbt Core vs Cloud CLI)
- Different packages, different binaries
- Same command names but different execution
- Caused confusion — dbt community documented migration pain
- NOT recommended for new projects

### Pattern D: "Server-Side Gating" (GitLab glab)
- CLI is 100% OSS
- Premium features gated by server-side license check
- CLI sends the request, server decides if allowed
- Clean separation but requires server infrastructure
