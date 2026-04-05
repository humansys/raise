# RAISE-1300: Analysis

## Root Cause (S — 5 Whys)

1. **Why** does the generated config have states from unrelated projects? → `_merge_workflows()` merges all states from selected projects into one global list
2. **Why** does merging produce noise? → Jira's `/project/{key}/statuses` returns ALL statuses in the workflow **scheme**, which is often shared across many projects
3. **Why** is the scheme shared? → Jira Cloud uses workflow schemes at instance level; projects using the same scheme see all its statuses
4. **Why** doesn't the generator filter? → Design assumed each project's workflow data would be clean; didn't account for shared schemes
5. **Root cause:** The generator was designed with a global merge model (`workflow:` at top level) instead of per-project model (`projects.{KEY}.workflow_states:` and `projects.{KEY}.issue_types:`)

## Evidence
- `_merge_workflows()` line 22-33: iterates selected keys but unions all states into a single deduped list
- `_merge_issue_types()` line 36-46: same pattern for issue types
- Output puts `workflow` and `issue_types` at config root level (lines 98-122)
- Hand-curated `jira.yaml` also has global workflow, but it's manually cleaned

## Fix Approach

Move workflow states and issue types into the **per-project section** of the generated config. Remove the global merge helpers.

**Before:**
```yaml
workflow:
  states: [merged from all projects]
  status_mapping: {global}
issue_types: [merged from all projects]
```

**After:**
```yaml
projects:
  RAISE:
    instance: humansys
    name: RAISE
    workflow_states:
      - name: Backlog
        category: new
    issue_types:
      - name: Story
        subtask: false
  RTEST:
    instance: humansys
    name: RaiSE Test
    workflow_states:
      - name: Backlog
        category: new
```

This gives each project its own clean workflow/issue type list. The consumer (human or adapter-setup skill) can then decide what to keep per project.

**Impact:** `JiraConfig` uses `extra="allow"`, so per-project extra fields pass through. No schema changes needed. Existing tests need updating to expect the new structure.
