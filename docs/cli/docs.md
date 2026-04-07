---
title: rai docs
description: Publish and retrieve governance documentation via adapters.
---

Manage governance documentation via `DocumentationTarget` adapters (filesystem, Confluence, or both). Publish artifacts and retrieve/search remote documentation.

## `rai docs publish`

Publish an artifact to a documentation target.

| Argument | Description |
|----------|-------------|
| `ARTIFACT_TYPE` | Artifact type, e.g. `roadmap`, `adr`, `epic-docs`, `session-diary` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--title` | | Page title (defaults to artifact type) |
| `--file` | `-f` | Read content from file (skips `governance/` convention) |
| `--path` | `-p` | Local file path for filesystem target (used with `--stdin`) |
| `--stdin` | | Read content from stdin (requires `--path`) |
| `--parent` | | Parent page ID — overrides routing config |
| `--target` | `-t` | Target name override (auto-detect if omitted) |

**Content sources** (priority order):

1. `--file PATH` — read from an existing file
2. `--stdin` — read from stdin (pipe or heredoc), requires `--path`
3. `governance/{type}.md` — default convention

```bash
# Publish from governance convention
rai docs publish roadmap
rai docs publish adr --title "ADR-001: Graph Architecture"

# Publish from any file
rai docs publish epic-docs --title "E1064: Pipeline Engine" --file /tmp/epic-docs.md

# Override parent page (Confluence)
rai docs publish session-diary --title "Session Diary — 2026-04-06" --file /tmp/diary.md --parent 3067674642

# Publish from stdin
cat design.md | rai docs publish design --title "Auth Design" --path docs/design.md --stdin
```

**Routing:** When publishing to Confluence, the adapter resolves the parent page from `.raise/confluence.yaml` routing config. The `--parent` flag overrides this. See [Configuring Integrations](../guides/configuring-integrations.md) for routing setup.

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
