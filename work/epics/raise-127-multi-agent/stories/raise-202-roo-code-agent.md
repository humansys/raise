# RAISE-202: Roo Code agent support (LiteLLM-compatible)

**JIRA:** [RAISE-202](https://humansys.atlassian.net/browse/RAISE-202)
**Epic:** RAISE-127 (Multi-Agent Support)
**Branch:** `story/raise-202/roo-code-agent`
**Created:** 2026-02-19

---

## In Scope

- `roo.yaml` agent config (`name`, `agent_type`, `skills_dir`, `instructions_file`, `detection_markers`)
- Instructions template for `.roo/rules/raise.md`
- `rai init --agent roo` scaffolds `.roo/skills/` and `.roo/rules/raise.md`
- Validate all 26 public skills work in `.roo/skills/` without transformation
- RooPlugin if Roo-specific skill/instruction transformations are needed
- Add `roo` to `rai init --detect` detection markers (`.roo/`, `.rooignore`)
- Documentation: minimum model recommendation for LiteLLM users

## Out of Scope

- LiteLLM configuration (client-side, not RaiSE's responsibility)
- Roo Code custom modes support (future, if needed)
- `.agents/skills/` cross-agent path (already supported by existing infra)
- Mode-specific skill variants (`skills-{modeSlug}/`)
- MEMORY.md placement for Roo Code (future, when Roo has equivalent)

## Done Criteria

- [ ] `rai init --agent roo` creates `.roo/skills/` with all 26 public skills
- [ ] `rai init --agent roo` creates `.roo/rules/raise.md` with instructions
- [ ] `rai init --detect` detects Roo Code if `.roo/` dir exists
- [ ] `rai skill list` works from a Roo Code project
- [ ] All tests pass, pyright clean, coverage ≥ 90%
- [ ] Retrospective complete
