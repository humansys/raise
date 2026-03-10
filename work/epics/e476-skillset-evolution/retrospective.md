# E476 Retrospective: Skillset Evolution

## Delivered

**Objective:** Separate language-specific gate configuration from core skills so RaiSE works cleanly across any tech stack.

| Milestone | Stories | Status |
|-----------|---------|--------|
| M1: Gates Configurable | S476.1 | done |
| M2: Skills Language-Agnostic | S476.1 + S476.2 | done |
| M3: Epic Complete | S476.1-5 | done |

### Key Deliverables

1. **Manifest-driven gates** — TestGate, LintGate, TypeGate, CoverageGate read commands from `.raise/manifest.yaml` with fallback to hardcoded defaults (S476.1)
2. **Language-agnostic skills** — rai-story-implement, rai-story-plan, rai-bugfix use manifest-first pattern with language detection fallback table (S476.2)
3. **raise-dev skillset** — Python-specific overlays at `.raise/skills/raise-dev/` (S476.3)
4. **raise-dev-ts skillset** — TypeScript example overlays at `.raise/skills/raise-dev-ts/` (S476.4)
5. **Skillset authoring guide** — `docs/src/content/docs/docs/guides/skillsets.mdx` (S476.5)

## What Went Well

- **Pattern reuse.** The manifest-first pattern was already proven in 5 skills. Extending it to gates (S476.1) and remaining skills (S476.2) was low-risk, high-value.
- **Risk-first sequencing.** S476.1 (Python code + TDD) went first. Once gates worked, the rest was markdown-only — zero code risk for S476.2-5.
- **Skillset system works.** `rai skill set create --empty` scaffolded correctly. CLI recognizes both skillsets. The overlay pattern is simple and extensible.
- **Documentation last.** S476.5 benefited from having real implementations (raise-dev, raise-dev-ts) to reference — no guesswork.
- **TDD discipline.** S476.1 wrote 8 tests RED-first, all passed GREEN with minimal changes. Full suite (3693 tests) stayed green throughout.

## What Could Improve

- **Skill sync across 3 locations** (.claude/, .agent/, src/raise_cli/skills_base/) is manual and error-prone. The .agent/ copy had version drift during S476.2. Consider automating with a pre-commit hook or `rai framework-sync`.
- **rai-bugfix inconsistency.** Only exists in .claude/skills/, not in skills_base or .agent/. Inconsistent with other skills.
- **Overlay duplication.** The 3-command verification block is identical across all 3 overlays in each skillset. Tolerable at 6 lines x 3 files, but an include/merge mechanism would DRY this up if more overlays are added.
- **CoverageGate coupling.** Appends `--cov` flags assuming pytest-cov. A separate `coverage_command` manifest field may be needed for true language-agnosticism.
- **Progress tracking in scope.md** was never updated from "pending" — tracking stayed manual.

## Patterns

- **Manifest-first with fallback** is now the universal pattern for all gates and all skills that invoke tooling. Priority: manifest → language detection → hardcoded defaults.
- **`shlex.split()` for command parsing** — converts manifest strings ("npm test") to argv lists (["npm", "test"]) correctly.
- **Skillset overlays are predictable** — copy structure from raise-dev, replace tool commands. Could be automated via `rai skill scaffold-overlay`.
- **Documentation stories benefit from sequencing last** — real implementations reduce guesswork.

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 5 (2 S + 3 XS) |
| Commits | 25 (story) + 3 (epic) + 5 (merges) = 33 |
| Files changed | ~30 (gate modules, test files, skill MDs, overlays, docs) |
| Tests added | 8 (S476.1 gate tests) |
| Tests total | 3693 passed |
| Code changes | S476.1 only (4 gate modules + 1 test file) |
| Markdown changes | S476.2-5 (skills, overlays, docs) |
