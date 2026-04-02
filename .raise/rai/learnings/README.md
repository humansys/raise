# Learning Records

Records produced by the LEARN protocol (see `aspects/introspection.md`).

## Structure

```
learnings/
  {skill}/           # e.g., rai-story-design
    {work_id}/       # e.g., S1133.1
      record.yaml    # Flat YAML (~10 fields)
```

## Rules

- One record per skill execution per work item
- Rework overwrites (no append)
- Missing record = silent node or not yet executed
- Schema: see `aspects/introspection.md` Learning Record Schema section
