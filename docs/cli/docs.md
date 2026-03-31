---
title: rai docs
description: Publish and retrieve governance documentation via adapters.
---

Manage governance documentation via `DocumentationTarget` adapters (e.g., Confluence). Publish governance artifacts and retrieve/search remote documentation.

## `rai docs publish`

Publish a governance artifact to a documentation target.

| Argument | Description |
|----------|-------------|
| `ARTIFACT_TYPE` | Governance artifact type, e.g. `roadmap`, `adr` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--title` | | Page title (defaults to artifact type) |
| `--target` | `-t` | Target name override (auto-detect if omitted) |

```bash
rai docs publish roadmap
rai docs publish adr --title "ADR-001: Graph Architecture"
```

---

## `rai docs get`

Retrieve a page from the documentation target.

| Argument | Description |
|----------|-------------|
| `IDENTIFIER` | Page ID on the remote target (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--target` | `-t` | Target name override |

```bash
rai docs get 12345678
```

---

## `rai docs search`

Search documentation pages on the remote target.

| Argument | Description |
|----------|-------------|
| `QUERY` | Search query (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--limit` | `-n` | Max results. Default: `10` |
| `--target` | `-t` | Target name override |

```bash
rai docs search "architecture decisions"
rai docs search "roadmap" -n 5
```

**See also:** [`rai adapter`](adapter.md/
