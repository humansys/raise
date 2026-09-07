---
story_id: "{STORY_ID}"
epic_ref: "{EPIC_ID}"
jira_key: "{KEY}"
size: "{XS|S|M|L}"
type: "{code|docs|analysis}"
status: "draft"
---

# Story: {title}

## User Story
As a [role],
I want [capability],
so that [benefit].

## Acceptance Criteria

### Scenario: {happy path}
```gherkin
Given [initial context]
When [action]
Then [expected outcome]
```

### Scenario: {edge case}
```gherkin
Given [context]
When [action]
Then [outcome]
```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|-----------------|
| [concrete value] | [concrete action] | [concrete result] |

## Notes
[Context, constraints, references to epic design.md]

## JTBD
[Help me {accomplish X} so I can {achieve Y}]

## ICP Segment
[Target: {role} at {company type} facing {problem}]

## Discovery Grounding
[Evidence from {research/observation/audit} showing {assumption validated}]

## PM Ownership
[{Name} ({Role})]
