# RAISE-1299: Plan

## Tasks

### T1: Guardrail test — DISTRIBUTABLE_SKILLS matches skills_base dirs (RED)
- Test that every `rai-*` dir in skills_base/ with a SKILL.md is in DISTRIBUTABLE_SKILLS
- Verify: `uv run pytest packages/raise-cli/tests/onboarding/test_skill_distribution.py -x -k "distributable"` — FAILS
- Commit: `test(RAISE-1299): guardrail — DISTRIBUTABLE_SKILLS covers all skills_base dirs`

### T2: Add 11 missing skills to DISTRIBUTABLE_SKILLS (GREEN)
- Add: rai-adapter-setup, rai-architecture-review, rai-bugfix, rai-code-audit, rai-framework-sync, rai-publish, rai-quality-review, rai-session-diary, rai-skill-create, rai-skillset-manage, rai-sonarqube
- Verify: `uv run pytest packages/raise-cli/tests/onboarding/test_skill_distribution.py -x` — PASSES
- Commit: `fix(RAISE-1299): add 11 missing skills to DISTRIBUTABLE_SKILLS`
