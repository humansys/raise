# Retrospective: RAISE-1300

## Summary
- Root cause: Config generator merged workflow states and issue types from all selected projects into global sections, amplified by Jira's shared workflow schemes
- Fix approach: Moved workflow_states and issue_types into per-project entries in the projects dict; removed global merge helpers
- Classification: Interface/S2-Medium/Design/Incorrect

## Process Improvement
**Prevention:** Config generators should preserve per-entity structure from discovery rather than merging into global blobs. Merging loses provenance and makes the output noisy when upstream APIs share schemes across entities.
**Pattern:** Interface + Design + Incorrect → config generator design assumed clean per-entity data from API, but shared schemes contaminate results.

## Heutagogical Checkpoint
1. Learned: Jira's `/project/{key}/statuses` returns all statuses in the workflow scheme, not just those actively used by the project. Shared schemes = shared noise.
2. Process change: When designing config generators, default to per-entity structure and let the consumer decide whether to merge.
3. Framework improvement: None — fix is self-contained in config gen.
4. Capability gained: Understanding of Jira workflow scheme sharing and its impact on discovery data fidelity.

## Patterns
- Added: PAT-E-728 (per-entity config gen structure over global merge)
- Reinforced: none evaluated
