---
title: rai discover
description: Codebase discovery and analysis — scan, analyze, build graph, detect drift.
---

Codebase discovery and analysis commands. Extract code symbols, analyze architecture, build the knowledge graph, and detect drift.

## `rai discover scan`

Scan a directory and extract code symbols (classes, functions, methods, interfaces, module docstrings). Supports Python, TypeScript, JavaScript, PHP, Svelte, and C#.

| Argument | Description |
|----------|-------------|
| `PATH` | Directory to scan. Default: `.` |

| Flag | Short | Description |
|------|-------|-------------|
| `--language` | `-l` | Language: `python`, `typescript`, `javascript`, `php`, `svelte`, `csharp` (auto-detect if not set) |
| `--output` | `-o` | Output format: `human`, `json`, `summary`. Default: `human` |
| `--pattern` | `-p` | Glob pattern for files |
| `--exclude` | `-e` | Patterns to exclude (repeatable) |

```bash
# Scan current directory (auto-detect languages)
rai discover scan

# Scan Python files only
rai discover scan src/ --language python

# JSON output for piping
rai discover scan src/ -l python -o json

# Exclude tests
rai discover scan . --exclude "**/test_*" --exclude "**/__tests__/**"
```

---

## `rai discover analyze`

Analyze scan results with confidence scoring and module grouping. All analysis is deterministic — no AI inference required.

| Flag | Short | Description |
|------|-------|-------------|
| `--input` | `-i` | Path to scan result JSON (reads stdin if not provided) |
| `--output` | `-o` | Output format: `human`, `json`, `summary`. Default: `human` |
| `--category-map` | `-c` | YAML file with custom path-to-category mappings |

```bash
# Analyze from file
rai discover analyze --input scan-result.json

# Pipe from scan
rai discover scan src/ -l python -o json | rai discover analyze

# Summary only
rai discover analyze --input scan-result.json --output summary
```

---

## `rai discover build`

Build unified graph with discovered components. Integrates validated components into the knowledge graph.

| Flag | Short | Description |
|------|-------|-------------|
| `--input` | `-i` | Path to validated components JSON |
| `--project-root` | `-r` | Project root directory. Default: `.` |
| `--output` | `-o` | Output format: `human`, `json`, `summary`. Default: `human` |

```bash
# Build with default input
rai discover build

# Build with custom input
rai discover build --input my-components.json
```

---

## `rai discover drift`

Check for architectural drift against baseline components. Compares scanned code against validated baseline to detect files in wrong locations, naming violations, and missing documentation.

| Argument | Description |
|----------|-------------|
| `PATH` | Directory to scan for drift. Default: `src/` |

| Flag | Short | Description |
|------|-------|-------------|
| `--project-root` | `-r` | Project root directory. Default: `.` |
| `--output` | `-o` | Output format: `human`, `json`, `summary`. Default: `human` |

```bash
# Check entire project
rai discover drift

# Check specific directory
rai discover drift src/new_module/

# JSON output
rai discover drift --output json
```

**Exit codes:** 0 no drift, 1 drift warnings found.

**See also:** [`rai graph build`](cli/graph.md)
