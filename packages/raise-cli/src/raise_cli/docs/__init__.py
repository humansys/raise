"""Documentation orchestration module.

High-level operations over documentation targets:
- migrate: bulk bootstrap filesystem → remote (Confluence)

Lower-level adapters live in raise_cli.adapters (composite_docs, filesystem_docs,
confluence_adapter).

Story: S1700.6.1 | Epic: E1700 Adapter Migration Path
"""
