---
title: CLI Reference
description: Complete reference for all RaiSE CLI commands — flags, options, and examples.
---

Complete reference for the `rai` command-line interface. Commands are organized in workflow order — from project setup through release.

## Global Options

These options are available on all commands:

| Flag | Short | Description |
|------|-------|-------------|
| `--version` | `-V` | Show version and exit |
| `--format` | `-f` | Output format: `human`, `json`, or `table` |
| `--verbose` | `-v` | Increase verbosity (`-v`, `-vv`, `-vvv`) |
| `--quiet` | `-q` | Suppress non-error output |
| `--help` | | Show help and exit |

## Command Groups

| Group | Description |
|-------|-------------|
| [init](init.md/ | Initialize a RaiSE project |
| [session](session.md/ | Manage working sessions |
| [graph](graph.md/ | Build, query, and manage the knowledge graph |
| [pattern](pattern.md/ | Manage learned patterns |
| [signal](signal.md/ | Emit lifecycle and telemetry signals |
| [backlog](backlog.md/ | Manage backlog items via adapters |
| [skill](skill.md/ | Manage RaiSE skills and skill sets |
| [discover](discover.md/ | Codebase discovery and analysis |
| [adapter](adapter.md/ | Inspect and validate adapters |
| [mcp](mcp.md/ | Manage MCP servers |
| [gate](gate.md/ | Discover and run workflow gates |
| [doctor](doctor.md/ | Diagnose setup and auto-fix issues |
| [docs](docs.md/ | Publish and retrieve documentation |
| [artifact](artifact.md/ | Manage skill artifacts |
| [release](release.md/ | Release management |
| [info](info.md/ | Display package information |
| [profile](profile.md/ | View developer profile |
