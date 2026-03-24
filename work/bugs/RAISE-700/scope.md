# RAISE-700: S3776 — scaffold_skills cognitive complexity 75

WHAT:      scaffold_skills() has cognitive complexity 75 (Sonar S3776 CRITICAL)
WHEN:      Every Sonar scan; function marked # noqa: C901 as a temporary defer
WHERE:     src/raise_cli/onboarding/skills.py:176
EXPECTED:  Complexity ≤ 15; noqa comment removed; S3776 clean in Sonar
Done when: sonar list issues for humansys-demos_raise-commons shows no S3776
           at skills.py:176; all tests pass; no noqa: C901 on scaffold_skills
