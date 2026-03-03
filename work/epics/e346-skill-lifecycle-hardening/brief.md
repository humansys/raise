# E346: Skill Lifecycle Hardening — Brief

## Hypothesis

If we reinforce the orchestrator skills (epic-run, story-run), rename review skills for clarity, and remove language bias from code/architecture reviews, then the full skill lifecycle will be reliable, consistent, and usable across any tech stack — not just Python projects.

## Success Metrics

- Orchestrator skills (epic-run, story-run) execute all lifecycle phases without skipping gates
- Review skills use clear, canonical names (code-review, architecture-review)
- Review skills produce meaningful feedback on non-Python codebases
- Review skills are integrated into orchestrator flows at the correct points

## Appetite

- **Size:** M (4 stories, estimated 2-3 sessions)
- **Timebox:** 1 week
- **Priority:** P0 (v2.2)

## Rabbit Holes

- Avoid rewriting orchestrator logic — focus on gap analysis and patching
- Don't build multi-language test suites — validate with representative samples
- Don't change skill architecture (ADR-040 compliant already)
