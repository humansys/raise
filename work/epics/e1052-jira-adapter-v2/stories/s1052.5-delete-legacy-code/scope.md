# S1052.5 — Delete Legacy Code

**Epic:** E1052 (Jira Adapter v2)
**Type:** cleanup (absorbs S1052.4)
**Size:** S

## Objective

Remove all legacy Jira adapter code now superseded by PythonApiJiraAdapter (S1052.3):

- AcliJiraAdapter + AcliBridge (raise-pro)
- JiraSyncHook (raise-pro)
- providers/jira/ directory (raise-pro)
- BacklogHook (raise-cli)
- Associated tests and docs
- Entry point cleanup in both pyproject.toml files
- Unify optional deps under [atlassian]

## Acceptance Criteria

- [ ] All listed files deleted
- [ ] Entry points updated
- [ ] No broken imports across codebase
- [ ] Full test suite passes
- [ ] Linting + type checks pass
