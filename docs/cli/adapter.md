---
title: rai adapter
description: Inspect and validate registered adapters.
---

Inspect and validate registered adapters. Adapters connect RaiSE to external services (Jira, Confluence, GitHub, etc.) via typed Protocol contracts.

## `rai adapter list`

List all registered adapters by entry point group. Shows each group with its registered adapters and source package.

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai adapter list
rai adapter list --format json
```

---

## `rai adapter check`

Validate adapters against their Protocol contracts. Loads each registered adapter and checks compliance via `isinstance()` against its `@runtime_checkable` Protocol.

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai adapter check
rai adapter check --format json
```

---

## `rai adapter validate`

Validate a declarative YAML adapter config. Checks that the YAML file conforms to `DeclarativeAdapterConfig` schema.

| Argument | Description |
|----------|-------------|
| `FILE` | Path to YAML adapter config file (**required**) |

```bash
rai adapter validate .raise/adapters/github.yaml
```

---

## `rai adapter status`

Show configuration status for known adapters. Checks that required config files exist and environment variables are set.

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai adapter status
rai adapter status --format json
```

**See also:** [`rai backlog`](backlog.md/, [`rai docs`](docs.md/
