# RAISE-570 — Scope

## Bug Definition

WHAT:      4 tests en TestGitEvidenceExtractorIntegration fallan con FileNotFoundError: 'git'
WHEN:      CI pipeline en MR o commit a dev — job `test` con imagen python:3.12-slim
WHERE:     src/raise_cli/compliance/extractors/git.py:273 (_run_git → subprocess.run(["git", ...]))
           tests/unit/compliance/extractors/test_git_integration.py (4 tests)
EXPECTED:  Los tests pasan porque git está disponible en el contenedor
Done when: Pipeline CI verde — los 4 tests que fallaban pasan en GitLab

## Failing Tests

- TestGitEvidenceExtractorIntegration.test_extract_produces_non_empty_results
- TestGitEvidenceExtractorIntegration.test_at_least_one_commit_evidence
- TestGitEvidenceExtractorIntegration.test_all_items_have_git_evidence_type
- TestGitEvidenceExtractorIntegration.test_all_items_have_required_fields

## Evidence

Job log: gitlab.com/.../jobs/13553847488
Error line: FileNotFoundError: [Errno 2] No such file or directory: 'git'
Pipelines: #2386240089 (f15ae24a), #2386241551 (12589d54)

TRIAGE:
  Bug Type:    Configuration
  Severity:    S2-Medium
  Origin:      Environment
  Qualifier:   Missing
