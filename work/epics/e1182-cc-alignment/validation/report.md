# E1134 CC-Alignment: Validation Report

**Generated:** automatically by `validate.py`
**Skills discovered:** 38
**Auto-invocable:** 25 | **Disabled:** 13

## Summary: Before / After

| Metric | Before | After | Target | Status |
|--------|--------|-------|--------|--------|
| Description avg length | ~300 chars | 85 chars | <100 chars | PASS |
| Descriptions <=100 chars | 0% | 35/38 (92%) | 100% | FAIL |
| Descriptions <=250 chars | 0% | 38/38 (100%) | 100% | PASS |
| Verb-first descriptions | — | 33/38 (87%) | 100% | FAIL |
| Auto-invocable desc budget | ~10,500 chars | 2,247 chars | <2,600 chars | PASS |
| `allowed-tools` coverage | 0/35 (0%) | 35/38 (92%) | 100% | FAIL |
| `disable-model-invocation` | 0/35 (0%) | 13/38 (34%) | >=13 side-effect | PASS |

## Dimension 1: Descriptions (S1134.1)

- Average length: **85 chars** (before: ~300)
- Within 100-char target: **35/38**
- Within 250-char hard limit: **38/38**
- Verb-first: **33/38**
- Auto-invocable budget: **2,247 chars** (before: ~10,500)

**Skills exceeding 100 chars:**

- `rai-sonarqube`: 196 chars
- `rai-adapter-setup`: 158 chars
- `rai-epic-research`: 149 chars

## Dimension 2: allowed-tools (S1134.2)

- Coverage: **35/38**
- Bare `Bash` (unrestricted): **5** skills
- `Bash(...)` glob patterns: **23** skills

**Skills missing `allowed-tools`:**

- `rai-adapter-setup`
- `rai-epic-research`
- `rai-sonarqube`

## Dimension 3: Invocation Control (S1134.3)

- `disable-model-invocation: true`: **13/38**
- Auto-invocable: **25/38**

**Disabled skills:**

- `rai-bugfix`
- `rai-discover`
- `rai-epic-close`
- `rai-epic-run`
- `rai-epic-start`
- `rai-framework-sync`
- `rai-mcp-add`
- `rai-mcp-remove`
- `rai-publish`
- `rai-session-close`
- `rai-story-close`
- `rai-story-run`
- `rai-story-start`

## Per-Skill Detail

| Skill | Desc Len | Verb-1st | allowed-tools | Bare Bash | Disabled |
|-------|----------|----------|---------------|-----------|----------|
| `rai-adapter-setup` | 158 | N | **N** | N | N |
| `rai-architecture-review` | 82 | Y | Y | N | N |
| `rai-bugfix` | 85 | Y | Y | Y | Y |
| `rai-code-audit` | 75 | Y | Y | N | N |
| `rai-debug` | 87 | Y | Y | Y | N |
| `rai-discover` | 86 | Y | Y | N | Y |
| `rai-docs-update` | 72 | Y | Y | N | N |
| `rai-doctor` | 71 | Y | Y | N | N |
| `rai-epic-close` | 83 | N | Y | N | Y |
| `rai-epic-design` | 82 | Y | Y | N | N |
| `rai-epic-docs` | 76 | Y | Y | N | N |
| `rai-epic-plan` | 78 | Y | Y | N | N |
| `rai-epic-research` | 149 | N | **N** | N | N |
| `rai-epic-run` | 78 | Y | Y | Y | Y |
| `rai-epic-start` | 77 | Y | Y | N | Y |
| `rai-framework-sync` | 74 | Y | Y | N | Y |
| `rai-mcp-add` | 74 | Y | Y | N | Y |
| `rai-mcp-remove` | 74 | Y | Y | N | Y |
| `rai-mcp-status` | 73 | Y | Y | N | N |
| `rai-problem-shape` | 84 | Y | Y | N | N |
| `rai-project-create` | 80 | Y | Y | N | N |
| `rai-project-onboard` | 89 | Y | Y | N | N |
| `rai-publish` | 78 | Y | Y | N | Y |
| `rai-quality-review` | 81 | Y | Y | N | N |
| `rai-research` | 88 | N | Y | N | N |
| `rai-session-close` | 75 | N | Y | N | Y |
| `rai-session-start` | 82 | Y | Y | N | N |
| `rai-skill-create` | 83 | Y | Y | N | N |
| `rai-skillset-manage` | 75 | Y | Y | N | N |
| `rai-sonarqube` | 196 | Y | **N** | N | N |
| `rai-story-close` | 70 | Y | Y | N | Y |
| `rai-story-design` | 80 | Y | Y | N | N |
| `rai-story-implement` | 71 | Y | Y | Y | N |
| `rai-story-plan` | 80 | Y | Y | N | N |
| `rai-story-review` | 86 | Y | Y | N | N |
| `rai-story-run` | 79 | Y | Y | Y | Y |
| `rai-story-start` | 62 | Y | Y | N | Y |
| `rai-welcome` | 69 | Y | Y | N | N |

## Epic Done Criteria Checklist

- [P] All skills have description <250 chars (target <100): **PASS** (38/38 <=250, 35/38 <=100)
- [F] All skills declare allowed-tools: **FAIL** (35/38)
- [P] Side-effect skills have disable-model-invocation: **PASS** (13 disabled)
- [F] Before/after report shows improvement across all metrics: **FAIL**
- [P] No skill content/instructions changed — metadata only: **PASS** (verified by diff)
- [ ] Retrospective completed: **PENDING**
