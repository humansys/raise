# Story Scope: RAISE-199 — Docs site: v2.1.0 release prep

**Jira:** [RAISE-199](https://humansys.atlassian.net/browse/RAISE-199)
**Epic:** RAISE-144 (Engineering Health — rolling)
**Size:** S
**Priority:** Before 2.1.0 publish
**Branch:** `story/raise-199/docs-v210-release-prep` (from `v2`)

## Problem

Docs site (docs.raiseframework.ai) reflects v2.0.0 content. v2.1.0 ships
significant new features with zero documentation.

## In Scope

### CLI Reference (`docs/src/content/docs/docs/cli/index.mdx` + ES mirror)

New commands to document:

| Command | Description |
|---------|-------------|
| `rai init --ide <name>` | Multi-IDE support (antigravity, cursor, claude) |
| `rai session context --sections <list>` | Load task-relevant context priming |
| `rai memory query --format compact` | Compact/semantic output format |
| `rai memory reinforce --vote 1\|0\|-1 --from STORY` | Pattern reinforcement signal |

### Memory concept page (`docs/src/content/docs/docs/concepts/memory.mdx` + ES)

- Temporal decay scoring (half-life, recency vs keyword relevance)
- Pattern reinforcement loop (Wilson score, +1/0/-1 votes)
- `rai memory reinforce` usage example

### Getting Started / Index (`docs/src/content/docs/docs/index.mdx` + ES)

- Update feature highlights to reflect 2.1.0 capabilities

## Out of Scope

- New guides or tutorials
- Redesign of docs structure
- Changelog page (separate story if needed)

## Files to Modify

```
docs/src/content/docs/docs/cli/index.mdx          # CLI reference EN
docs/src/content/docs/es/docs/cli/index.mdx        # CLI reference ES
docs/src/content/docs/docs/concepts/memory.mdx     # Memory concept EN
docs/src/content/docs/es/docs/concepts/memory.mdx  # Memory concept ES
docs/src/content/docs/docs/index.mdx               # Landing EN
docs/src/content/docs/es/docs/index.mdx            # Landing ES
```

## Done When

- [ ] CLI Reference lists all new commands from v2.1.0
- [ ] Memory page explains scoring + reinforcement loop
- [ ] EN and ES pages in sync
- [ ] `npm run build` in `docs/` passes without errors
- [ ] Docs deploy succeeds
