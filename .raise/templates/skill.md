---
name: {{name}}
description: >
  {{description}}

license: MIT

metadata:
  raise.work_cycle: {{lifecycle}}
  raise.frequency: {{frequency}}
  raise.fase: "{{fase}}"
  raise.prerequisites: "{{prerequisites}}"
  raise.next: "{{next}}"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME={{name}} \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---

# {{title}}

## Purpose

{{purpose}}

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps exactly. Full verification at each step.

**Ha (破)**: Adapt steps based on context. Skip verification for familiar patterns.

**Ri (離)**: Create variations. Compose with other skills.

## Context

**When to use:**
- {{trigger_1}}
- {{trigger_2}}

**When to skip:**
- {{skip_1}}
- {{skip_2}}

**Inputs required:**
- {{input_1}}
- {{input_2}}

**Output:**
- {{output_1}}
- {{output_2}}

## Steps

### Step 1: {{step_1_name}}

{{step_1_description}}

```bash
# Example command
uv run raise {{example_command}}
```

**Verification:** {{step_1_verification}}

> **If you can't continue:** {{step_1_recovery}}

### Step 2: {{step_2_name}}

{{step_2_description}}

**Verification:** {{step_2_verification}}

> **If you can't continue:** {{step_2_recovery}}

## Output

| Item | Destination |
|------|-------------|
| {{output_item_1}} | {{output_dest_1}} |
| {{output_item_2}} | {{output_dest_2}} |

## Notes

{{notes}}

## References

- Previous: `/{{prerequisites}}`
- Next: `/{{next}}`
- Related: {{related}}
