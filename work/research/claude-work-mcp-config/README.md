# Research: Claude Work/Cowork MCP Configuration

**Status:** Complete
**Date:** 2026-03-27
**Question:** ¿Cómo configurar MCP servers en Claude Cowork y comparte config con Claude Code?

## Navigation

- [Report](claude-work-mcp-config-report.md) — hallazgos, recomendaciones, próximos pasos
- [Evidence Catalog](sources/evidence-catalog.md) — fuentes, niveles de evidencia

## TL;DR

Claude "Work" = **Claude Cowork**, modo autónomo dentro de Claude Desktop (Feb 2026).
Config de Claude Code (`~/.claude.json`) y Cowork (`claude_desktop_config.json`) son **separadas**.
Hay un bridge no-documentado Desktop→Cowork. Para RaiSE: necesitamos `rai mcp install --target desktop`.
