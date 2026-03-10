# Evidence Catalog — RES-NAMESPACE-001

## Sources

### S1: Agent Skills Specification
- **URL**: https://agentskills.io/specification
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Skill names allow only `a-z`, `0-9`, `-`. Max 64 chars. No dots, colons, underscores. Name must match parent directory name.
- **Relevance**: Eliminates dot, colon, underscore, and double-underscore as namespace separators.

### S2: Claude Code Skills Documentation
- **URL**: https://code.claude.com/docs/en/skills
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Discovery scans `.claude/skills/*/SKILL.md`. Name resolution: frontmatter `name` field > directory name. Plugin skills use `plugin-name:skill-name` qualified naming. No user-defined namespaces. Progressive disclosure: only name+description loaded at startup.
- **Relevance**: Confirms flat namespace for project skills. Only plugin mechanism provides built-in namespacing.

### S3: Claude Code Skill Best Practices
- **URL**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Same character constraints as Agent Skills spec. Reserved words: `anthropic`, `claude`.
- **Relevance**: Confirms naming constraints are enforced by Claude Code.

### S4: MCP SEP-986 — Tool Name Format
- **URL**: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/986
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: LLM APIs enforce `^[a-zA-Z0-9_-]{1,64}$`. Dots and slashes rejected by most providers.
- **Relevance**: If skills ever surface as MCP tools, dots and colons are incompatible.

### S5: MCP SEP-993 — Namespaces Proposal
- **URL**: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/993
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Proposed `__` (double underscore) as namespace separator for MCP tools. Claude Code already uses `mcp__server__tool` format.
- **Relevance**: MCP chose `__` because dots/colons/slashes fail API validation. But Agent Skills spec doesn't allow underscores.

### S6: Docker MCP Gateway — Colon to Double Underscore Migration
- **URL**: https://github.com/docker/mcp-gateway/pull/263
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Docker migrated from colon to `__` separator because colons violated tool name regex.
- **Relevance**: Real-world evidence that colon namespacing fails in practice.

### S7: GitHub Issue #15882 — Plugin Commands Always Namespaced
- **URL**: https://github.com/anthropics/claude-code/issues/15882
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Plugin skills are always namespaced as `plugin-name:skill-name`, even when no conflict exists.
- **Relevance**: Shows Claude Code's built-in namespace mechanism. Colon is reserved for this purpose.

### S8: npm Scopes Documentation
- **URL**: https://docs.npmjs.com/about-scopes/
- **Type**: Secondary
- **Evidence Level**: Very High
- **Key Finding**: `@org/package` format. Introduced to prevent name squatting. Requires org ownership.
- **Relevance**: Precedent for prefix-based namespacing. Different separator (`@`/`/`), but same pattern.

### S9: VS Code Extension Manifest
- **URL**: https://code.visualstudio.com/api/references/extension-anatomy
- **Type**: Secondary
- **Evidence Level**: Very High
- **Key Finding**: `publisher.extension` format using dot separator.
- **Relevance**: Dot separator precedent, but Agent Skills spec prohibits dots.

### S10: AGENTS.md Specification
- **URL**: https://agents.md/
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: No namespacing guidance. Addresses agent configuration, not capability naming.
- **Relevance**: No emerging standard for skill namespacing from the AGENTS.md side.

### S11: MCP Server Naming Conventions
- **URL**: https://zazencodes.com/blog/mcp-server-naming-conventions
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: `<name>-mcp` (40%), `mcp-<name>` (35%). Tools within servers use snake_case.
- **Relevance**: Prefix vs suffix patterns in ecosystem naming.

### S12: RES-SKILL-FMT-001 (Prior Research)
- **URL**: /home/emilio/Code/raise-commons/work/research/ai-ide-skill-formats/
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: AGENTS.md is the emerging standard. Claude Code uses `.claude/skills/*/SKILL.md`. Progressive disclosure model.
- **Relevance**: Confirms our skills must comply with the Agent Skills spec.

### S13: RES-SKILLS-ARCH (Prior Research)
- **URL**: /home/emilio/Code/raise-commons/work/research/skills-architecture-decision/
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: RaiSE decided `metadata.raise.*` for metadata namespacing. Skills are methodology, not tools.
- **Relevance**: Metadata namespace already uses dot convention (inside YAML, not in names).

### S14: Spec Kit Agent Skills (dceoy/speckit-agent-skills)
- **URL**: https://github.com/dceoy/speckit-agent-skills
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Agent Skills-compliant Spec Kit implementation uses dash-prefix: `speckit-specify`, `speckit-plan`, `speckit-implement`, etc. Multi-runtime support via symlinks.
- **Relevance**: Real-world precedent for dash-prefix namespacing in Claude Code skills ecosystem.

### S15: Spec Kit Antigravity Skills (compnew2006)
- **URL**: https://github.com/compnew2006/Spec-Kit-Antigravity-Skills
- **Type**: Primary
- **Evidence Level**: Medium
- **Key Finding**: Community fork uses dot-prefix: `speckit.specify`, `speckit.plan`. Placed in `.agent/skills/` (non-standard). Not compliant with Agent Skills spec.
- **Relevance**: Shows dot convention exists but is not spec-compliant. Ecosystem is split, with compliant implementations using dashes.

### S16: GitHub Spec Kit (github/spec-kit)
- **URL**: https://github.com/github/spec-kit
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Original project uses dot naming (`speckit.specify`) for legacy `.claude/commands/` files. The commands format predates the Agent Skills specification.
- **Relevance**: Origin of the dot convention — it's legacy, not the current standard.

### S17: Claude Code GitHub Issues on Naming Conflicts
- **URLs**: #14945, #15065, #15842
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Same-name skills shadow commands. Priority: enterprise > personal > project. Plugin skills get namespace via colon.
- **Relevance**: Confirms collision is a real problem. No built-in resolution beyond scope priority.
