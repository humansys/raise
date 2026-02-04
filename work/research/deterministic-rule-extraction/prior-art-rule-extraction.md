# Prior Art: Brownfield Rule/Pattern Extraction from Codebases

**Author**: RaiSE Research
**Date**: 2026-01-24
**Status**: Complete
**Confidence Level**: HIGH (evidence-based with extensive web research)

---

## Executive Summary

This document catalogs existing approaches, tools, and projects that extract rules, patterns, or conventions from existing codebases. The goal is to identify concrete, adoptable methodologies for RaiSE's deterministic rule extraction workflow.

**Key Findings**:

1. **BMAD-METHOD** provides the most comprehensive brownfield analysis workflow with automated codebase documentation
2. **Cursor's self-improving rules** system demonstrates practical auto-evolution of coding guidelines
3. **Tabnine/Refact.ai** show fine-tuning approaches for learning team-specific patterns
4. **Aider's CONVENTIONS.md** pattern offers a simple, effective manual-plus-AI hybrid
5. **Academic specification mining** provides theoretical foundations for automated extraction
6. **EditorConfig tools** demonstrate practical inference of style from existing code

**Applicability to RaiSE**: Multiple approaches can be combined for a layered extraction strategy.

---

## Table of Contents

1. [AI-Powered Development Frameworks](#1-ai-powered-development-frameworks)
2. [IDE/Editor Rule Systems](#2-ideeditor-rule-systems)
3. [AI Code Assistants with Learning](#3-ai-code-assistants-with-learning)
4. [Static Analysis & Linting](#4-static-analysis--linting)
5. [Academic Research Approaches](#5-academic-research-approaches)
6. [Code Intelligence Platforms](#6-code-intelligence-platforms)
7. [Synthesis: Applicability to RaiSE](#7-synthesis-applicability-to-raise)

---

## 1. AI-Powered Development Frameworks

### 1.1 BMAD-METHOD (Breakthrough Method for Agile AI-Driven Development)

**Source**: [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | [Documentation](https://docs.bmad-method.org/)

**Approach**: BMAD provides a complete workflow for brownfield codebase analysis through its `*document-project` task. The system scans the entire codebase and generates comprehensive documentation about its current state.

**How Pattern Discovery Works**:
1. **Intelligent Document Discovery**: Analyzes existing codebase structure
2. **Pattern Extraction**: Identifies architecture patterns, code organization, and design patterns
3. **Business Rule Extraction**: Extracts logic from the codebase
4. **Integration Point Mapping**: Identifies external APIs and services

**Automation Level**: High automation with human validation. The document-project workflow uses AI agents to scan and analyze, but humans review generated documentation.

**Input Analyzed**:
- Source code files
- Project structure
- Dependencies and imports
- Documentation files
- Configuration files

**Output Format**: Structured Markdown documents:
- `project-context.md` - High-level project overview, purpose, technologies, key patterns
- `architecture-overview.md` - System architecture, component relationships, data flow
- `code-standards.md` - Coding conventions, patterns, style guidelines extracted from existing code

**Key Innovation**: Automatic field type detection (brownfield vs greenfield) based on codebase analysis during `*workflow-init`. No special brownfield configuration required.

**Codebase Flattener Tool**: BMAD includes a tool that aggregates the entire codebase into a single XML file for AI model consumption:
```bash
npx bmad-method flatten --input /path/to/source --output my-project.xml
```

**Applicability to RaiSE**:
- **HIGH** - The document-project workflow pattern directly maps to RaiSE's brownfield analysis needs
- The structured output format (project-context, architecture, code-standards) aligns with RaiSE's artifact-based approach
- Could adopt the two-workflow approach: PRD-First for large codebases, Document-First for smaller projects

**References**:
- [Brownfield Development Guide](https://docs.bmad-method.org/how-to/brownfield/)
- [Document Existing Project](https://docs.bmad-method.org/how-to/brownfield/document-existing-project/)
- [Medium: Greenfield vs Brownfield in BMAD](https://medium.com/@visrow/greenfield-vs-brownfield-in-bmad-method-step-by-step-guide-89521351d81b)

---

### 1.2 OpenSpec (Spec-Driven Development)

**Source**: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | [openspec.dev](https://openspec.dev/)

**Approach**: OpenSpec is explicitly "brownfield-first" - designed for working on mature, existing codebases (1->n) rather than exclusively new projects (0->1).

**How Pattern Discovery Works**:
- AI assistant generates specification files based on requirements AND existing codebase
- Two-folder model separates current truth (`openspec/specs/`) from proposed updates (`openspec/changes/`)
- Diffs are explicit and manageable across features

**Automation Level**: AI-assisted generation with human review. You don't create specification files manually - the AI generates them based on requirements and existing codebase analysis.

**Key Insight**: "Most SDD tools assume greenfield (0→1) development. OpenSpec excels at existing codebase modification (1→n), especially when changes span multiple specifications."

**Best Practice for Brownfield**:
- Start with one new feature to get comfortable
- Gradually build specs as you modify existing code
- Don't try to generate specs for entire legacy codebase upfront (waste of time)
- Specs accumulate organically through real work

**Applicability to RaiSE**:
- **MEDIUM** - The "organic accumulation" philosophy aligns with RaiSE's incremental approach
- The two-folder model (current vs proposed) could inform RaiSE's rule versioning strategy
- Less directly applicable as OpenSpec focuses on specs, not rules

**References**:
- [OpenSpec Deep Dive](https://redreamality.com/garden/notes/openspec-guide/)
- [Martin Fowler: SDD Tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

---

### 1.3 Kiro AI (AWS)

**Source**: [kiro.dev](https://kiro.dev/) | [AWS Documentation](https://aws.amazon.com/documentation-overview/kiro/)

**Approach**: Kiro operates as an intelligent development partner that analyzes existing codebases, understands architectural patterns, and generates documentation.

**How Pattern Discovery Works**:
1. **Automated Analysis Phase**: Examines codebases to identify architectural patterns, dependencies, and modernization opportunities
2. **Visual Diagram Generation**: Creates diagrams illustrating system dependencies and data flows
3. **Technical Debt Assessment**: Identifies areas where modernization delivers greatest impact

**Automation Level**: High automation for analysis, human approval for actions.

**Input Analyzed**:
- Complete codebase structure
- Dependencies
- Behavioral patterns

**Output Format**:
- Design documents
- Data flow diagrams (Mermaid)
- TypeScript interfaces
- Database schemas
- API endpoints

**Key Features**:
- **Specs**: Artifacts that facilitate planning, refactoring, and understanding system behavior
- **Steering Files**: Markdown files providing persistent knowledge about project conventions
- **Autonomous Agent**: Maintains comprehensive understanding of codebase and patterns

**Limitations Noted**: Some users reported Kiro struggled to analyze existing code and conventions, missed reusable components, and had rigid task-list execution.

**Applicability to RaiSE**:
- **MEDIUM** - The steering files concept aligns with RaiSE's rule-based guidance
- Automated analysis generates documentation that could feed rule extraction
- Less applicable for deterministic rule extraction specifically

**References**:
- [DEV: Introducing Kiro](https://dev.to/aws-builders/introducing-kiro-an-ai-ide-that-thinks-like-a-developer-42jp)
- [AWS Blog: Agentic Cloud Modernization](https://aws.amazon.com/blogs/migration-and-modernization/agentic-cloud-modernization-accelerating-modernization-with-aws-mcps-and-kiro/)

---

## 2. IDE/Editor Rule Systems

### 2.1 Cursor Rules & Self-Improving Rules

**Source**: [Cursor Documentation](https://docs.cursor.com/context/rules) | [cursorrules.org](https://cursorrules.org/)

**Approach**: Cursor uses `.mdc` rules (markdown-based config files) that guide the AI assistant. The innovative "self-improvement rule" enables automatic rule evolution based on codebase growth.

**How Pattern Discovery Works**:

1. **Manual Definition**: Users define rules in `.cursor/rules/` files
2. **Auto-Generation**: `/Generate Cursor Rules` command creates rules from existing codebase
3. **Self-Improvement Loop**: `self-improvement.mdc` file enables feedback-powered rule evolution

**Self-Improving Rules System**:
```markdown
# cursor-rules.mdc
- Teaches Cursor how to process, format, and locate rules
- Provides a playbook of project structure

# self-improvement.mdc
- Tells Cursor to analyze codebase over time
- Learn from recurring patterns
- Recommend or evolve new rules
```

**Automation Level**: Hybrid - manual initial setup with automated evolution.

**Input Analyzed**:
- Project structure
- Detected tech stack
- Recurring patterns in code
- PR comments and reviewer feedback

**Output Format**: `.mdc` files (Markdown with metadata)

**Key Innovation**: "Your codebase can start teaching itself, and it only takes one file to unlock that capability."

**Best Practices for Ongoing Refinement**:
- Watch PR comments - repeated issues become rule candidates
- Track onboarding questions - confusion indicates missing rules
- Update rules after large-scale refactors

**Community Resources**:
- [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) - 📄 Configuration files collection
- [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) - Generates MDC rules using Exa semantic search + LLM
- [AndreRatzenberger/cursor-rules](https://github.com/AndreRatzenberger/cursor-rules) - Auto-analysis with `onboard project` command

**Applicability to RaiSE**:
- **HIGH** - Self-improving rules pattern directly applicable
- The feedback loop (PR comments -> rule candidates) aligns with continuous improvement
- Could adopt the `cursor-rules.mdc` + `self-improvement.mdc` pattern for RaiSE rules

**References**:
- [SashiDo Blog: Cursor Self-Improving Rules](https://www.sashido.io/en/blog/cursor-self-improving-rules)
- [Cursor Forum: Auto-Rule Generation](https://forum.cursor.com/t/how-to-force-your-cursor-ai-agent-to-always-follow-your-rules-using-auto-rule-generation-techniques/80199)

---

### 2.2 Claude Code / CLAUDE.md System

**Source**: [Anthropic Engineering Blog](https://www.anthropic.com/engineering/claude-code-best-practices) | [HumanLayer Blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

**Approach**: CLAUDE.md is a markdown file that Claude automatically reads at the start of each session, holding project-specific instructions, structure, conventions, and workflows.

**How Pattern Discovery Works**:

1. **Auto-Generation via /init**: Run `/init` command and Claude generates a starter CLAUDE.md based on project structure and detected tech stack
2. **Progressive Disclosure**: Tell Claude how to find information rather than including everything upfront
3. **Custom Commands**: Encode repeatable processes in `.claude/commands/` as markdown files

**Automation Level**: Semi-automated - `/init` provides starting point, humans refine.

**Input Analyzed**:
- Project structure
- Detected technology stack
- Existing documentation

**Output Format**: `CLAUDE.md` file with:
- Project's WHY, WHAT, and HOW
- Conventions and workflows
- Style guidelines
- Links to detailed documentation

**Key Insight**: "Less (instructions) is more. Keep the contents of your CLAUDE.md concise and universally applicable."

**Skill Evaluation System**: Runs on every prompt submission and intelligently suggests which skills Claude should activate.

**Applicability to RaiSE**:
- **HIGH** - The `/init` auto-generation pattern maps to `raise.rules.generate`
- Progressive disclosure aligns with RaiSE's token efficiency goals
- Custom commands pattern already adopted in RaiSE

**References**:
- [Builder.io: Complete Guide to CLAUDE.md](https://www.builder.io/blog/claude-md-guide)
- [Dometrain: Creating Perfect CLAUDE.md](https://dometrain.com/blog/creating-the-perfect-claudemd-for-claude-code/)

---

### 2.3 Aider (AI Pair Programming)

**Source**: [aider.chat](https://aider.chat/) | [GitHub](https://github.com/Aider-AI/aider)

**Approach**: Aider uses a `CONVENTIONS.md` file to define coding conventions in Markdown, which Aider forwards to the LLM.

**How Pattern Discovery Works**:
- **Manual Definition**: Users create CONVENTIONS.md with coding standards
- **Automatic Loading**: Configure in `.aider.conf.yml`: `read: CONVENTIONS.md`
- **Linting Integration**: Aider can auto-run linter/tests on changes, sending errors back to LLM

**Automation Level**: Manual convention definition, automated enforcement.

**Input Analyzed**:
- Entire git repository (creates a "map" of codebase)
- Symbol definitions via ctags
- CONVENTIONS.md file

**Output Format**: Code changes following conventions

**Key Innovation**: "Repo map" gives LLM understanding of entire codebase structure using ctags symbol extraction.

**Effect of CONVENTIONS.md**:
- With CONVENTIONS.md: GPT correctly used httpx and provided type hints
- Without: GPT used requests and skipped types

**Applicability to RaiSE**:
- **MEDIUM** - CONVENTIONS.md pattern is simple and effective but manual
- The ctags-based repo map approach could inform RaiSE's codebase understanding
- Linting feedback loop pattern is adoptable

**References**:
- [Aider: Specifying Coding Conventions](https://aider.chat/docs/usage/conventions.html)
- [Aider: ctags for Codebase Understanding](https://aider.chat/docs/ctags.html)

---

### 2.4 Windsurf AI IDE

**Source**: [windsurf.com](https://windsurf.com/) | [Codeium](https://codeium.com/windsurf)

**Approach**: Windsurf uses deep codebase indexing and a "Memories" system for persistent context.

**How Pattern Discovery Works**:
1. **Indexing Engine**: Retrieves context from entire codebase, not just recent files
2. **Memories System**:
   - User-generated memories (rules) - explicitly defined
   - Automatically generated memories - created based on interactions

**Automation Level**: High automation for memory generation from interactions.

**Cascade Feature**: "Remembers important things about your codebase and workflow"

**Codemaps (New Feature)**: AI-annotated structured maps of code showing structure, data flow, and dependencies in real-time for each task.

**Key Insight**: "The core goal is to help engineers and AI build a shared understanding of the same codebase, reducing quality slippage caused by rapid changes with low understanding."

**Applicability to RaiSE**:
- **MEDIUM** - Memories system concept aligns with RaiSE's rule persistence
- Codemaps could inform RaiSE's codebase visualization approach
- Less applicable for deterministic extraction

**References**:
- [Cognition: Windsurf Codemaps](https://cognition.ai/blog/codemaps)
- [DataCamp: Windsurf Tutorial](https://www.datacamp.com/tutorial/windsurf-ai-agentic-code-editor)

---

### 2.5 Cline AI (.clinerules)

**Source**: [cline.bot](https://cline.bot/) | [GitHub](https://github.com/cline/cline)

**Approach**: Cline supports `.clinerules` files and MCP server generation for custom tools.

**How Pattern Discovery Works**:
- **Codebase Analysis**: Analyzes file structure and source code ASTs
- **Regex Searches**: Runs searches to understand patterns
- **MCP Server Generation**: Can create custom tools tailored to workflow

**Automation Level**: Semi-automated - AI analyzes codebase, humans approve actions.

**Key Feature**: "Thanks to the Model Context Protocol, Cline can extend its capabilities through custom tools. Just ask Cline to 'add a tool' and it will handle everything."

**Repomix MCP Server**: Packages local code directory into consolidated XML file for AI analysis:
- Analyzes codebase structure
- Extracts relevant code content
- Generates comprehensive report with metrics, file tree, formatted code

**Applicability to RaiSE**:
- **MEDIUM** - MCP server generation pattern could inform RaiSE tooling
- Repomix-style codebase consolidation useful for analysis
- .clinerules less structured than RaiSE's guardrail format

**References**:
- [Repomix MCP Server](https://repomix.com/guide/mcp-server)
- [Cline Blog: Essential MCP Servers](https://cline.bot/blog/supercharge-your-cline-workflow-7-essential-mcp-servers)

---

## 3. AI Code Assistants with Learning

### 3.1 Tabnine (Enterprise Context Engine)

**Source**: [tabnine.com](https://www.tabnine.com/)

**Approach**: Tabnine's Enterprise Context Engine learns organization's unique architecture, frameworks, and coding standards.

**How Pattern Discovery Works**:
1. **Read Access to Repository**: AI studies existing codebase
2. **Pattern Identification**: Identifies preferences and patterns unique to team
3. **Incremental Learning**: Learns from coding style, frequently used functions, variable naming conventions
4. **Acceptance/Rejection Learning**: Models adapt based on suggestions accepted or rejected

**Automation Level**: Fully automated learning, human feedback via acceptance/rejection.

**Input Analyzed**:
- Existing codebase
- Code repository (with granted access)
- User interactions (acceptance/rejection of suggestions)

**Output Format**: Personalized code completions

**Key Insight**: "Projects of significant size have an 'internal language' comprised of internal services, frameworks, and libraries with their APIs and idiomatic patterns."

**Enterprise Features**:
- AI models connected to enterprise code repository
- Generate consistent code based on best practices, naming conventions, styles
- Private models fine-tuned on organization's code

**Applicability to RaiSE**:
- **LOW** - Tabnine is completion-focused, not rule extraction
- The "internal language" concept validates RaiSE's approach to capturing team patterns
- Fine-tuning approach less applicable to deterministic rule extraction

**References**:
- [Tabnine Blog: Introducing Teams](https://www.tabnine.com/blog/introducing-tabnine-for-teams/)
- [Tabnine Blog: AI Pair Programming Use Cases](https://www.tabnine.com/blog/ai-pair-programming-with-tabnine-top-4-use-cases/)

---

### 3.2 Refact.ai (Fine-Tuning on Codebase)

**Source**: [refact.ai](https://refact.ai/) | [GitHub](https://github.com/smallcloudai/refact-vscode)

**Approach**: Refact.ai uses fine-tuning on codebase to improve suggestion quality tailored to specific coding patterns.

**How Pattern Discovery Works**:
1. **Pre-training Foundation**: Models learn syntax, patterns, high-level concepts
2. **Fine-tuning Objective**: Predict next token according to YOUR coding style
3. **Selective Training**: Can imitate coding style of specific experts by uploading only their files

**Automation Level**: Automated fine-tuning with human curation of training data.

**Input Analyzed**:
- Coding style
- Patterns
- Typical API usage
- Tech stack
- Documentation

**Output Format**: Fine-tuned completion model

**Key Innovation**: "It is possible to imitate the coding style of specific experts on your team. You can achieve this by selectively uploading the files that represent the desired coding style."

**Knowledge Organization**: "Organizes experience into the knowledge base for quick collaboration across your team."

**Applicability to RaiSE**:
- **LOW** - Fine-tuning is model-level, not rule-level
- The "selective expert imitation" concept could inform rule curation
- RAG approach (repo-level awareness) more directly applicable

**References**:
- [Refact.ai Blog: Open-Source Fine-Tuning](https://refact.ai/blog/2023/open-source-fine-tuning-with-refact/)
- [Refact Documentation: Context](https://docs.refact.ai/features/context/)

---

### 3.3 Amazon CodeGuru

**Source**: [AWS CodeGuru](https://aws.amazon.com/codeguru/)

**Approach**: CodeGuru uses rule mining and supervised ML models trained on Amazon codebase and best practices.

**How Pattern Discovery Works**:
1. **Rule Mining**: Mines Amazon codebases using search techniques and locality sensitive models
2. **Cross-Reference with Documentation**: Compares code changes against documentation data
3. **Pattern Recognition**: Creates new rules based on code changes that improve quality
4. **Code Inconsistency Detection**: During review, uses data mining + ML to detect inconsistencies

**Automation Level**: Fully automated analysis, human review of recommendations.

**Input Analyzed**:
- Source code
- Pull request diffs
- Application dependencies
- Code repositories
- Customer code for customization

**Output Format**: Review recommendations, profiling insights

**Training Data Sources**:
- Major open source projects
- Amazon codebase (massive scale)
- Customer feedback as labels

**Key Insight**: "For code inconsistencies, the models are trained during either the full or incremental code review. These models utilize data mining and machine learning techniques to build the dataset, highlight the reason for the code patterns, and make recommendations customized to the customer's code."

**Applicability to RaiSE**:
- **MEDIUM** - Rule mining approach is directly relevant
- Cross-referencing code with documentation aligns with RaiSE's artifact-based approach
- Commercial/cloud-only limits direct adoption

**References**:
- [AWS CodeGuru Reviewer FAQs](https://aws.amazon.com/codeguru/reviewer/faqs/)
- [AWS Tutorial: Review Source Code](https://aws.amazon.com/tutorials/review-source-code-using-amazon-codeguru-reviewer/)

---

### 3.4 GitHub Copilot Workspace

**Source**: [GitHub Copilot](https://github.com/features/copilot) | [GitHub Next](https://githubnext.com/projects/copilot-workspace)

**Approach**: Copilot Workspace reads codebase and generates specifications with current vs desired state.

**How Pattern Discovery Works**:
1. **Codebase Reading**: Reads entire codebase
2. **Specification Generation**: Creates bullet-point lists for current state and desired state
3. **Context Retrieval**: Uses RAG + vector database for context-aware suggestions
4. **Semantic Code Search**: Index enables natural language questions about design patterns

**Automation Level**: Highly automated analysis with human plan approval.

**Input Analyzed**:
- Complete codebase
- Issue descriptions
- PR comments
- Repository history

**Output Format**: Specification documents, implementation plans

**Key Features**:
- Can answer "What design patterns are used in this repository?"
- Provides code examples and links for each pattern found
- Enterprise codebase indexing for deeper understanding

**Note**: Technical preview was sunset on May 30th, 2025.

**Applicability to RaiSE**:
- **MEDIUM** - RAG + vector database approach relevant for codebase understanding
- Pattern question-answering capability could inform rule discovery
- Specification format (current vs desired) useful for change management

**References**:
- [GitHub Docs: Explore a Codebase](https://docs.github.com/en/copilot/tutorials/explore-a-codebase)
- [GitHub Blog: Copilot Understanding Code](https://github.blog/ai-and-ml/github-copilot/how-github-copilot-is-getting-better-at-understanding-your-code/)

---

### 3.5 Greptile

**Source**: [greptile.com](https://www.greptile.com/)

**Approach**: Greptile builds a complete graph of codebase to understand how code changes affect other parts.

**How Pattern Discovery Works**:
1. **Graph Generation**: Creates detailed graph of functions, variables, classes, files, directories
2. **Connection Understanding**: Maps how all elements are connected
3. **Rule Learning**: Learns team's coding standards by reading every engineer's PR comments
4. **Reaction Tracking**: Tracks reactions to learn what comments are useful
5. **Rule Inference**: Infers new rules from comments, replies, and reactions

**Automation Level**: Fully automated learning from team interactions.

**Input Analyzed**:
- Complete codebase
- PR comments from all engineers
- Reactions to comments
- Code changes and their effects

**Output Format**: Context-aware code reviews

**Key Insight**: "Greptile learns your team's coding standards by reading every engineer's PR comments, and learns what types of comments your team finds useful by tracking reactions. As you use it, it infers new rules and idiosyncrasies about your team and your codebase."

**Semantic Search Challenge**: "Semantic search on codebases works better if you first translate the code to natural language before generating embedding vectors."

**Applicability to RaiSE**:
- **HIGH** - PR comment -> rule inference pattern directly applicable
- Graph-based codebase understanding could inform rule relationships
- Reaction tracking for rule quality assessment is innovative

**References**:
- [Greptile Blog: Semantic Codebase Search](https://www.greptile.com/blog/semantic-codebase-search)
- [Greptile Docs: Graph-based Context](https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context)

---

## 4. Static Analysis & Linting

### 4.1 Semgrep Rule Generation

**Source**: [semgrep.dev](https://semgrep.dev/) | [Autogrep Research](https://lambdasec.github.io/AutoGrep-Automated-Generation-and-Filtering-of-Semgrep-Rules-from-Vulnerability-Patches/)

**Approach**: Multiple approaches exist for Semgrep rule generation, from manual to LLM-automated.

**How Pattern Discovery Works**:

**Manual/Semi-Automated (Native)**:
1. **Structure Mode**: UI-based rule writing editor that guides the process
2. **Advanced Mode**: YAML editor with Semgrep syntax
3. **Pattern Syntax**: Expressive matching with metavariables

**Automated (Autogrep - Research)**:
1. **Rule Generation Pipeline**: Analyzes vulnerability patches from source repositories
2. **LLM Pattern Extraction**: Uses LLM to extract code patterns
3. **Rule Filtering System**: Validates through multiple quality checks

**Automation Level**: Ranges from manual to fully automated (Autogrep).

**Autogrep Results**:
- Filtering pipeline removed 71.15% of overly specific rules
- Removed 10.75% of duplicates
- Analyzed 39,931 patches

**Key Use Case**: "Automating institutional knowledge using Semgrep. This has several benefits, including teaching new members about coding patterns in an automatic way."

**Applicability to RaiSE**:
- **HIGH** - Semgrep rule format is well-established and RaiSE-compatible
- Autogrep's LLM-based extraction directly applicable
- Institutional knowledge automation aligns with RaiSE goals

**References**:
- [Semgrep: Write Custom Rules](https://semgrep.dev/docs/semgrep-code/editor)
- [Semgrep Blog: Writing Rules Methodology](https://semgrep.dev/blog/2020/writing-semgrep-rules-a-methodology/)

---

### 4.2 ESLint Config Inference

**Source**: [ESLint](https://eslint.org/) | [Prettier-ESLint](https://github.com/prettier/prettier-eslint)

**Approach**: ESLint supports configuration inference and popular style guide adoption.

**How Pattern Discovery Works**:
1. **Interactive Init**: `eslint --init` asks questions about project
2. **Style Guide Adoption**: Choose from Airbnb, Google, Standard
3. **Prettier Integration**: prettier-eslint infers prettierOptions from eslintConfig

**Automation Level**: Semi-automated - interactive setup, then automated enforcement.

**Key Feature**: "Once prettier-eslint has found the eslintConfig, the prettierOptions are inferred from the eslintConfig."

**Applicability to RaiSE**:
- **LOW** - ESLint is style-focused, not behavioral patterns
- Interactive init pattern could inform rule setup flow
- Style guide adoption pattern applicable for convention selection

---

### 4.3 EditorConfig Tools (Style Inference)

**Source**: [EditorConfig](https://editorconfig.org/) | [editorconfig-tools](https://github.com/notslang/editorconfig-tools)

**Approach**: editorconfig-tools can INFER settings from existing code and generate EditorConfig file.

**How Pattern Discovery Works**:
```bash
# Infer .editorconfig from existing files
editorconfig-tools infer ./* ./lib/**/* ./test/**/* > .editorconfig
```

**Automation Level**: Fully automated inference.

**Input Analyzed**:
- Indentation (tabs vs spaces, width)
- Line endings
- Final newline
- Trailing whitespace
- Charset

**Output Format**: `.editorconfig` file

**Visual Studio IntelliCode**: Can also infer code styles from existing code and create EditorConfig with preferences predefined.

**Applicability to RaiSE**:
- **MEDIUM** - Direct pattern inference from code is the exact goal
- Limited to formatting rules, not behavioral patterns
- The CLI approach (`infer` command) is a good UX pattern

**References**:
- [npm: editorconfig-tools](https://www.npmjs.com/package/editorconfig-tools)
- [Andrew Lock: IntelliCode EditorConfig](https://andrewlock.net/generating-editorconfig-files-automatically-using-intellicode/)

---

### 4.4 Qodo (formerly Codium)

**Source**: [qodo.ai](https://www.qodo.ai/)

**Approach**: Qodo provides rules customization and enforcement with organization-specific standards.

**How Pattern Discovery Works**:
1. **Team-Level Policies**: Define standards once, apply across teams
2. **15+ Specialized Agents**: Automate tasks like bug detection, test coverage, documentation
3. **Multi-Repo Context**: Shared context across organization repositories

**Automation Level**: Automated enforcement of manually defined rules.

**Key Feature**: "Standards and governance are built in – Qodo enforces your coding standards, architecture rules, and compliance policies on every change."

**Applicability to RaiSE**:
- **LOW** - Enforcement-focused rather than extraction
- Team-level policy pattern aligns with RaiSE organizational rules
- Agent specialization concept applicable to RaiSE agents

---

## 5. Academic Research Approaches

### 5.1 Specification Mining

**Source**: Various academic papers and the book "Mining Software Specifications: Methodologies and Applications"

**Approach**: Automatically derive models that capture system behavior from traces or source code.

**Key Techniques**:

1. **Grammar Inference**: Learn state machines from execution traces
2. **Partial Order Mining**: Extract temporal patterns from logs
3. **Static Program Analysis**: Path-aware analysis for pattern extraction
4. **Abstract Interpretation**: Sound approximation of program behavior

**Automation Level**: Fully automated extraction, human interpretation of results.

**Applications**:
- Program comprehension
- Testing
- Anomaly detection
- Debugging (faulty behavior abstraction)

**Key Research**: "Efficient mining of iterative patterns for software specification discovery" - mines frequent patterns from program traces.

**Applicability to RaiSE**:
- **MEDIUM** - Theoretical foundations for automated extraction
- Temporal pattern mining could inform workflow rule extraction
- State machine learning applicable to process rules

**References**:
- [ACM: Efficient Mining of Iterative Patterns](https://dl.acm.org/doi/abs/10.1145/1281192.1281243)
- [Amazon: Mining Software Specifications Book](https://www.amazon.com/Mining-Software-Specifications-Methodologies-Applications/dp/1439806268)

---

### 5.2 API Usage Pattern Mining (MAPO, Precise)

**Source**: [MAPO Paper](https://www.researchgate.net/publication/225213921_MAPO_Mining_and_Recommending_API_Usage_Patterns) | Various ACM papers

**Approach**: Mine common API usage patterns from open source repositories.

**MAPO (Mining API usage Pattern from Open source)**:
- Mines patterns showing which API methods are frequently called together
- Extracts sequential rules for usage scenarios
- Recommends patterns and associated code snippets

**Precise (Automatic Parameter Recommendation)**:
- Mines existing codebases
- Uses abstract usage instance representation
- Builds parameter usage database
- Generates candidates by concretizing instances adaptively

**Automation Level**: Fully automated mining.

**Key Insight**: "A mined pattern describes that in a certain usage scenario, some API methods are frequently called together and their usages follow some sequential rules."

**Applicability to RaiSE**:
- **MEDIUM** - API usage pattern extraction directly applicable
- Sequential rule discovery for workflow patterns
- Pattern + code snippet pairing useful for rule examples

---

### 5.3 Code Clone Detection for Pattern Finding

**Source**: Various research including [Amain](https://github.com/CGCL-codes/Amain)

**Approach**: Repurpose clone detection techniques for pattern discovery.

**Key Techniques**:

1. **AST-Based**: Transform code to AST, find identical subtrees
2. **Markov Chain Models**: Transform AST to Markov chains for similarity measurement
3. **Multi-Graph Networks**: Combine AST, CFG, DFG for comprehensive analysis

**Amain Approach**:
- Transforms complex tree into simple Markov chains
- Measures distance of all states
- Scales to big code (evaluated on Google Code Jam, BigCloneBench)

**Applicability to RaiSE**:
- **LOW** - Clone detection is similarity-focused, not pattern extraction
- Multi-graph representation (AST+CFG+DFG) could inform comprehensive analysis
- Scalability techniques applicable to large codebases

---

### 5.4 KaiBRE (Business Rule Extraction)

**Source**: [Datamatics KaiBRE](https://www.datamatics.com/resources/case-studies/demos/modernize-legacy-code-with-kaibre)

**Approach**: Agentic AI-powered solution for extracting business rules from legacy code.

**How Pattern Discovery Works**:
1. **Smart Analyzers**: Find redundancies, dead code, inconsistent branching, hidden data connections
2. **Business Logic Extraction**: Decipher complex business logic from aging codebases
3. **Rule Set Generation**: Turn sprawling codebases into organized, usable rule sets

**Automation Level**: Fully automated extraction.

**Target**: Large, multi-module legacy applications (COBOL, VB)

**Output Format**: Clear, actionable rules ready for modern implementation

**Applicability to RaiSE**:
- **MEDIUM** - Business rule extraction is analogous to coding convention extraction
- Legacy code handling techniques relevant for brownfield
- Commercial product limits direct adoption

---

## 6. Code Intelligence Platforms

### 6.1 Sourcegraph CLI (src)

**Source**: [Sourcegraph](https://sourcegraph.com/docs/cli)

**Approach**: Universal code search with structural pattern matching.

**How Pattern Discovery Works**:
```bash
src search 'lang:go func.*error'
src search 'repo:github.com/org/repo patternType:structural func :[name](:[args])'
```

**Structural Search**: Uses Comby syntax, language-aware via `lang:` keyword

**Applicability to RaiSE**:
- **LOW** - Search-focused rather than extraction
- Structural search syntax could inform pattern specification
- Requires Sourcegraph instance

---

### 6.2 DeepSeek Coder

**Source**: [DeepSeek-Coder GitHub](https://github.com/deepseek-ai/DeepSeek-Coder)

**Approach**: Open-source code model trained on project-level corpus with dependency parsing.

**How Pattern Discovery Works**:
1. **Project-Level Training**: Trained on 87% code + 13% natural language
2. **Dependency Parsing**: Parses file dependencies to rearrange positions
3. **Cross-File Understanding**: 16K-128K context enables project-level comprehension

**Capabilities**:
- Interpreting code logic
- Identifying potential bugs or inefficiencies
- Providing optimization suggestions
- Summarizing codebases or diffs

**Applicability to RaiSE**:
- **LOW** - Model-level capability, not tool for extraction
- Long context enables comprehensive codebase analysis
- Could power LLM-based rule extraction

---

## 7. Synthesis: Applicability to RaiSE

### 7.1 Direct Adoption Candidates

| Approach | Source | Adoption Path |
|----------|--------|---------------|
| **Self-improving rules** | Cursor | Create `rule-evolution.md` meta-rule for automatic refinement |
| **Document-project workflow** | BMAD | Adapt for `raise.rules.generate` brownfield analysis phase |
| **PR comment -> rule inference** | Greptile | Extract rules from code review patterns |
| **CONVENTIONS.md pattern** | Aider | Simple bootstrap for manual convention capture |
| **EditorConfig inference CLI** | editorconfig-tools | Template for style pattern inference |
| **Autogrep LLM extraction** | Semgrep research | LLM-based pattern extraction pipeline |

### 7.2 Indirect Inspiration

| Concept | Source | Application |
|---------|--------|-------------|
| Two-folder model (current/proposed) | OpenSpec | Rule versioning strategy |
| Steering files | Kiro | Persistent guidance documents |
| Enterprise Context Engine | Tabnine | Organization-level pattern learning |
| Graph-based codebase context | Greptile | Rule relationship mapping |
| Temporal pattern mining | Academic | Workflow rule extraction |
| API usage pattern mining | MAPO | Integration pattern extraction |

### 7.3 Recommended Layered Strategy for RaiSE

**Layer 1: Bootstrap (Manual + AI-Assisted)**
- Adopt Aider's CONVENTIONS.md pattern for initial manual capture
- Use Claude's `/init` pattern to auto-generate starter rules

**Layer 2: Deterministic Extraction (CLI Tools)**
- Use ast-grep/ripgrep pipeline for structural pattern extraction
- Apply Semgrep for security and best practice patterns
- Use editorconfig-tools pattern for style inference

**Layer 3: Learning & Evolution (AI-Powered)**
- Adopt Cursor's self-improving rules pattern
- Implement Greptile's PR comment -> rule inference
- Use BMAD's document-project workflow for comprehensive analysis

**Layer 4: Validation & Quality**
- Apply Autogrep's filtering pipeline (remove overly specific, duplicate rules)
- Use Qodo's multi-repo context for organizational consistency
- Implement feedback loops (acceptance/rejection tracking)

### 7.4 Key Takeaways

1. **Hybrid approaches work best**: No single tool solves brownfield rule extraction. Combining manual bootstrap, deterministic CLI tools, and AI-powered learning yields best results.

2. **Self-improvement is key**: Cursor and Greptile demonstrate that rules should evolve with the codebase, not remain static.

3. **Team behavior is signal**: PR comments, code review patterns, and acceptance/rejection of suggestions are rich sources for rule inference.

4. **Start small, grow organically**: OpenSpec's advice applies - don't try to extract everything upfront. Let rules accumulate through real work.

5. **Determinism requires tool discipline**: All tools in the CLI section produce deterministic output when properly configured. This is essential for reproducible rule extraction.

---

## Appendix A: Tool Comparison Matrix

| Tool/System | Extraction Type | Automation | Determinism | Applicability |
|-------------|-----------------|------------|-------------|---------------|
| BMAD document-project | Full codebase | High | N/A (AI) | HIGH |
| Cursor self-improving | Convention evolution | High | N/A (AI) | HIGH |
| Greptile PR learning | Team patterns | High | N/A (AI) | HIGH |
| Aider CONVENTIONS.md | Manual conventions | Low | N/A | MEDIUM |
| ast-grep | Structural patterns | High | HIGH | HIGH |
| Semgrep | Security patterns | High | HIGH | HIGH |
| EditorConfig inference | Style patterns | High | HIGH | MEDIUM |
| Tabnine | Code completions | High | N/A (model) | LOW |
| CodeGuru | Code quality | High | N/A (ML) | MEDIUM |
| Kiro steering files | Persistent guidance | Low | N/A | MEDIUM |

---

## References

### AI Development Frameworks
- [BMAD-METHOD Documentation](https://docs.bmad-method.org/)
- [OpenSpec Guide](https://redreamality.com/garden/notes/openspec-guide/)
- [Kiro Documentation](https://kiro.dev/)

### IDE/Editor Systems
- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [Cursor Self-Improving Rules Blog](https://www.sashido.io/en/blog/cursor-self-improving-rules)
- [awesome-cursorrules Repository](https://github.com/PatrickJS/awesome-cursorrules)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Aider Conventions Documentation](https://aider.chat/docs/usage/conventions.html)
- [Windsurf Codemaps](https://cognition.ai/blog/codemaps)
- [Cline Documentation](https://cline.bot/)

### AI Code Assistants
- [Tabnine for Teams](https://www.tabnine.com/blog/introducing-tabnine-for-teams/)
- [Refact.ai Fine-Tuning Blog](https://refact.ai/blog/2023/open-source-fine-tuning-with-refact/)
- [Amazon CodeGuru FAQs](https://aws.amazon.com/codeguru/reviewer/faqs/)
- [GitHub Copilot Tutorials](https://docs.github.com/en/copilot/tutorials/explore-a-codebase)
- [Greptile Codebase Search](https://www.greptile.com/blog/semantic-codebase-search)

### Static Analysis
- [Semgrep Rule Writing](https://semgrep.dev/docs/semgrep-code/editor)
- [Autogrep Research](https://lambdasec.github.io/AutoGrep-Automated-Generation-and-Filtering-of-Semgrep-Rules-from-Vulnerability-Patches/)
- [editorconfig-tools npm](https://www.npmjs.com/package/editorconfig-tools)
- [Qodo Documentation](https://www.qodo.ai/)

### Academic Research
- [MAPO: Mining API Usage Patterns](https://www.researchgate.net/publication/225213921_MAPO_Mining_and_Recommending_API_Usage_Patterns)
- [Mining Software Specifications Book](https://www.amazon.com/Mining-Software-Specifications-Methodologies-Applications/dp/1439806268)
- [Amain: AST-based Markov Chains](https://github.com/CGCL-codes/Amain)

### Business Rule Extraction
- [KaiBRE by Datamatics](https://www.datamatics.com/resources/case-studies/demos/modernize-legacy-code-with-kaibre)

---

**Document Status**: Complete
**Last Updated**: 2026-01-24
**Next Review**: After implementation of recommended approaches
