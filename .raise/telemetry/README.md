# RaiSE Telemetry

Local storage for Observable Workflow telemetry events.

## Files

| File | Purpose |
|------|---------|
| `events.jsonl` | Skill lifecycle events (start, complete, artifacts) |

## Event Schema

```json
{
  "event": "skill_completed",
  "skill": "research",
  "session_id": "abc123",
  "timestamp": "2026-01-31T14:30:00-06:00"
}
```

## Event Types

| Event | Description |
|-------|-------------|
| `skill_started` | Skill execution began |
| `skill_completed` | Skill execution finished |
| `artifact_created` | File written during skill execution |
| `gate_validated` | Gate validation completed (future) |

## Usage

```bash
# View recent events
tail -20 events.jsonl | jq .

# Count events by type
cat events.jsonl | jq -r '.event' | sort | uniq -c

# Filter by skill
cat events.jsonl | jq 'select(.skill == "research")'
```

## Privacy

- Telemetry is LOCAL only (gitignored)
- No PII or secrets stored
- Session IDs are Claude Code internal IDs

---

*Part of RaiSE Observable Workflow (Constitution §8)*
