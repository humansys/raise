## Retrospective: RAISE-1152

### Summary
- Root cause: update_issue passed assignee as raw string; Jira Cloud requires `{"accountId": "..."}`
- Fix: inline normalization in update_issue + search_users in JiraClient
- Classification: Interface/S2-Medium/Code/Missing

### Process Improvement
**Prevention:** when adding CLI flags that map to external API fields, verify the target API's expected format
**Pattern:** Interface + Code + Missing → boundary format mismatch at adapter layer

### Heutagogical Checkpoint
1. Learned: Jira Cloud uses accountId exclusively for assignee. atlassian-python-api passes fields without format validation
2. Process change: first fix was over-engineered (3 methods, YAGNI create_issue changes). User caught it — KISS/YAGNI check before committing
3. Framework improvement: none needed
4. Capability gained: discipline to fix only the reported bug, not adjacent features

### Patterns
- Added: none
- Reinforced: none
