# RAISE-1299: Analysis

## Root Cause (XS — cause evident)

`DISTRIBUTABLE_SKILLS` list in `skills_base/__init__.py` is manually maintained and was not updated when 11 new skills were added to `skills_base/`. The sync/scaffold machinery works correctly — it only iterates what's in the list.

Missing 11 skills:
- rai-adapter-setup, rai-architecture-review, rai-bugfix, rai-code-audit
- rai-framework-sync, rai-publish, rai-quality-review
- rai-session-diary, rai-skill-create, rai-skillset-manage, rai-sonarqube

## Fix Approaches

A: **Add the 11 missing entries to DISTRIBUTABLE_SKILLS** — simple, direct, 1 file change. Trade-off: same gap will recur when new skills are added.

B: **Auto-discover from skills_base directory** — replace hardcoded list with `importlib.resources` scan of `rai-*` dirs in `skills_base/`. Trade-off: slightly more complex, but eliminates the class of bug permanently.

C: **Add missing entries + add a test that checks skills_base/ dirs match the list** — keeps explicit list (reviewable) but adds a guardrail. Trade-off: test needs updating when adding skills, but fails loudly if forgotten.
