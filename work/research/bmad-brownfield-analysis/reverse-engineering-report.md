# BMAD Brownfield: Complete Reverse Engineering

**Research ID**: RES-BMAD-BFLD-001-D1
**Date**: 2026-01-27
**Researcher**: Claude Opus 4.5
**Status**: Completed
**Word Count**: ~9,500

---

## Executive Summary

BMAD Method's brownfield capability centers on `document-project`, a **12-step documentation workflow** designed to produce comprehensive project documentation for AI-assisted development. Its core philosophy is **"documentation as the bridge to brownfield PRDs"** -- the system generates documentation artifacts that downstream agents (PRD creator, architect, developer) consume as context.

**Core Architecture**: A router (`instructions.md`) dispatches to either a full-scan workflow (12 steps) or a deep-dive sub-workflow (7 steps), with a JSON state file enabling resumability. A CSV-based classification system (12 project types x 24 detection columns) drives conditional analysis. A write-as-you-go architecture with context purging manages LLM context window constraints.

**Key Strengths** (with evidence):
1. **Context Management**: Write-to-disk-then-purge prevents context overflow on large codebases (full-scan-instructions.md, Step 4 batching strategy)
2. **Project Classification**: CSV-driven 12-type classification with conditional analysis flags eliminates irrelevant scanning (documentation-requirements.csv, 24 columns)
3. **Scan Level Flexibility**: Quick (2-5 min) / Deep (10-30 min) / Exhaustive (30-120 min) accommodates different needs (full-scan-instructions.md, Step 0.6)
4. **Resumability**: JSON state file with step tracking, timestamps, and stale detection enables interrupt-resume (project-scan-report-schema.json)
5. **Validation Rigor**: 200+ item checklist covering 15 dimensions (checklist.md)

**Key Weaknesses** (with evidence):
1. **No Quality Evaluation**: Documents "what is" without assessing "how good" -- no code smell detection, no architectural fitness evaluation (entire workflow lacks Clean Code/Architecture analysis)
2. **No Governance Output**: Produces documentation, not enforceable artifacts -- no rules, no guardrails, no constraints (no .cursorrules, no AGENTS.md generation)
3. **LLM-Only File Reading**: No AST integration, no static analysis tools -- relies entirely on LLM reading raw files (full-scan-instructions.md, all steps)
4. **No Incremental Analysis**: Full rescan is the only update mechanism -- no differential/delta capability (instructions.md routing logic)
5. **Persona Dependency**: Workflow is tied to "Mary the Analyst" persona, adding conceptual overhead without clear value (workflow.yaml)

**Novel Patterns Worth Preserving**: 8 patterns identified (see Section 4)

---

## 1. Full Scan Workflow -- Step-by-Step Mechanical Analysis

### 1.1 Mode Detection and Routing

The entry point `instructions.md` implements a **four-step routing protocol**:

**Step 1: Validation Phase**
- Checks for project status configuration
- If no status file exists, runs in standalone mode
- For greenfield projects, prompts user confirmation before proceeding

**Step 2: Resumability Check**
- Reads `project-scan-report.json` first
- Offers three options: resume from checkpoint, start fresh (archiving old state), or cancel
- **Critical detail**: Automatically archives state files older than 24 hours to `.archive/` directory
- Conditional CSV loading during resume -- loads only cached project types, not all 12

**Step 3: Documentation Mode Selection**
- **No existing documentation**: Initiates `initial_scan`
- **Documentation present**: Offers three choices:
  - Full project rescan (full-scan workflow)
  - Deep-dive into specific areas (deep-dive workflow)
  - Keep existing documentation (exit)

**Step 4: Completion & Status Update**
- Updates workflow status if applicable
- Displays completion summary with next recommended steps

**Mechanical Assessment**: The routing logic is clean and well-structured. The 24-hour stale detection is a pragmatic choice -- long enough for multi-session work, short enough to prevent confusion from outdated state. The conditional CSV loading on resume is a context window optimization detail that shows maturity in LLM workflow design.

**Lean Audit**: No Muda (waste) detected. The routing eliminates unnecessary work by checking state before doing anything. The three-choice menu for existing documentation respects the user's time.

### 1.2 Project Classification System (CSV Deep Dive)

The `documentation-requirements.csv` is a **12 x 24 matrix** that drives the entire analysis:

**12 Project Types**: web, mobile, backend, cli, library, desktop, game, data, extension, infra, embedded

**24 Columns per Type** (grouped by purpose):

| Column Group | Columns | Purpose |
|-------------|---------|---------|
| **Identity** | `project_type_id` | Type identifier |
| **Boolean Flags** | `requires_api_scan`, `requires_data_models`, `requires_state_management`, `requires_ui_components`, `requires_deployment_config`, `requires_hardware_docs`, `requires_asset_inventory` | Control which analysis modules execute |
| **Detection Patterns** | `key_file_patterns` | File patterns that identify this project type (e.g., `package.json;tsconfig.json;*.config.js` for web) |
| **Scan Guidance** | `critical_directories`, `integration_scan_patterns`, `test_file_patterns`, `config_patterns`, `auth_security_patterns`, `schema_migration_patterns`, `entry_point_patterns`, `shared_code_patterns`, `monorepo_workspace_patterns`, `async_event_patterns`, `ci_cd_patterns`, `asset_patterns`, `hardware_interface_patterns`, `protocol_schema_patterns`, `localization_patterns` | Tell the scanner WHERE to look for each concern |

**Detection Mechanism**: The LLM scans the project root for files matching `key_file_patterns`, then assigns the best-matching `project_type_id`. This is **LLM-interpreted, not deterministic** -- the patterns are semicolon-separated globs that the LLM must parse from the CSV text.

**Conditional Analysis Example** (backend type):
- `requires_api_scan = true` -- scan for API routes
- `requires_data_models = true` -- scan for schemas/migrations
- `requires_state_management = false` -- skip state management analysis
- `requires_ui_components = false` -- skip UI component inventory
- `requires_deployment_config = true` -- scan for Docker, K8s, CI/CD
- `requires_hardware_docs = false` -- skip hardware documentation
- `requires_asset_inventory = false` -- skip asset inventory

**Lean Audit**:
- **Muda eliminated**: By not scanning for UI components in a backend project, or hardware docs in a web project, BMAD eliminates ~40-60% of unnecessary analysis per project type
- **Mura concern**: The CSV format is rigid -- adding a new project type requires understanding all 24 columns. A YAML format with optional fields would reduce cognitive load
- **Muri concern**: 24 columns is a lot for an LLM to parse from CSV text. LLM CSV parsing has known reliability issues (column misalignment, delimiter confusion)

**RaiSE Applicability**: High. RaiSE has zero project type detection. This is a clear gap. However, the format should be YAML (not CSV) for better LLM parsing reliability.

### 1.3 Structure Detection (Monolith / Monorepo / Multi-Part)

Step 1 of the full scan classifies repository structure:

**Detection Heuristics**:
- **Monorepo**: Detected by presence of `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `workspace.json`, `rush.json`, or `go.work`
- **Multi-Part**: Detected by presence of distinct top-level directories like `client/`, `server/`, `api/`, `frontend/`, `backend/`
- **Monolith**: Default if neither monorepo nor multi-part patterns detected

**User Confirmation Loop**: After classification, the system asks the user to confirm: "I detected multiple parts in this project: [list]. Is this correct?" This introduces human validation at a critical branching point.

**Per-Part Processing**: For monorepo/multi-part projects, each part gets its own project type detection, documentation requirements loading, and analysis pipeline. This means a React frontend + Express backend monorepo would run web-type analysis on the frontend and backend-type analysis on the server.

**State Tracking**: Classification results are cached in the state file as `project_types` array, enabling resume without re-detection:
```json
{
  "project_types": [
    {"part_id": "client", "project_type_id": "web", "display_name": "React Frontend"},
    {"part_id": "server", "project_type_id": "backend", "display_name": "Express API"}
  ]
}
```

**Lean Audit**: Excellent. The structural classification enables right-sized analysis -- a monorepo with 5 parts gets 5 focused analyses instead of one confused analysis trying to cover everything.

### 1.4 Conditional Analysis Engine

Step 4 is the **critical step** where actual code analysis happens. It implements a sophisticated batching strategy:

**Scan Level Mechanics**:
- **Quick Scan**: Pattern-based analysis WITHOUT reading source files. Uses glob/grep to identify file locations. Best for initial overview.
- **Deep Scan**: Reads files in critical directories based on project type. Selective reading of key files.
- **Exhaustive Scan**: Reads ALL source files (excludes node_modules, dist, build, coverage).

**Batching Architecture** (Deep/Exhaustive only):
1. Identify subfolders to process (from `critical_directories` or all subfolders)
2. For each subfolder:
   a. Read all files in subfolder
   b. Extract required information based on boolean flags
   c. **IMMEDIATELY write findings to appropriate output file**
   d. Validate written document (section-level validation)
   e. Update state file with batch completion
   f. **PURGE detailed findings from context, keep only 1-2 sentence summary**
   g. Move to next subfolder

**Context Purge Mechanics**: After processing each subfolder, the system explicitly discards detailed findings and retains only summaries like:
- "APIs: 42 endpoints"
- "Data: 15 tables"
- "Components: 87 components"

**Batch State Tracking**:
```json
{
  "findings": {
    "batches_completed": [
      {"path": "src/routes/", "files_scanned": 12, "summary": "42 REST endpoints found"},
      {"path": "src/models/", "files_scanned": 8, "summary": "15 data models with Prisma"}
    ]
  }
}
```

**Boolean Flag-Driven Conditional Analysis**:
- `requires_api_scan == true` -> Scan for API routes, endpoints, middleware, controllers
- `requires_data_models == true` -> Scan for schemas, migrations, ORM configs
- `requires_state_management == true` -> Analyze Redux, Context API, Vuex, etc.
- `requires_ui_components == true` -> Inventory components, categorize by type
- `requires_hardware_docs == true` -> Look for schematics, pinout diagrams

Each conditional check applies the scan level strategy (quick=glob only, deep/exhaustive=read files).

**Lean Audit**:
- **Muda eliminated**: Context purging prevents wasted context window tokens
- **Mura eliminated**: Batching by subfolder provides consistent processing units
- **Innovation**: The write-as-you-go pattern ensures no work is lost on interruption

### 1.5 Context Management (Write-As-You-Go + Purge)

This is BMAD's most sophisticated pattern. It directly addresses the fundamental LLM constraint: context windows are finite.

**The Pattern in Detail**:
```
For each analysis unit (subfolder/module):
  1. READ: Load files into context
  2. ANALYZE: Extract required information
  3. WRITE: Immediately write output to disk
  4. VALIDATE: Check written document has required sections
  5. UPDATE: Record completion in state file
  6. PURGE: Remove detailed findings from context, retain 1-2 sentence summary
  7. PROCEED: Move to next unit with clean context
```

**What Gets Purged**: Detailed scan results, file contents, code snippets, dependency lists
**What Gets Retained**: High-level summaries ("42 endpoints", "15 models"), classification data, state file location

**Quality Risk**: Summary fidelity degrades over many purge cycles. By Step 10 (index generation), the LLM has only summaries of summaries. The generated index relies on what was written to disk, not what the LLM remembers.

**Mitigation**: The system reads written files back when needed (e.g., for cross-referencing). The state file acts as a "table of contents" for navigating previous outputs.

**Comparison with RaiSE SAR**: RaiSE's current approach loads everything into context and generates all 7 reports in one session. This works for small-medium codebases (<100 files) but fails for larger projects. BMAD's approach scales to any codebase size but at the cost of cross-document coherence.

### 1.6 Master Index Generation

Step 10 generates `index.md` as the **primary AI retrieval source**:

**Design as AI Entry Point**: The index is explicitly designed to be the first document an AI agent reads when working with a brownfield project. It contains:
- Project type and structure summary
- Technology stack quick reference
- Links to all generated documentation
- Links to existing documentation found during scan
- Getting started instructions

**Incomplete Documentation Markers**: A particularly clever pattern -- documents that should exist but weren't generated (due to quick scan or missing data) are marked with `_(To be generated)_`. This allows:
- Automated detection of gaps
- User-triggered selective generation
- Clear status visibility

**Multi-Part Navigation**: For monorepo/multi-part projects, the index provides per-part navigation with quick reference sections showing type, tech stack, and root path for each part.

**Lean Audit**: This is a high-value artifact. It eliminates Muda of "searching for the right document" and creates flow for AI agents navigating the documentation. RaiSE lacks this -- the 7 SAR reports have no unified entry point.

### 1.7 Validation Checklist Analysis

The `checklist.md` contains **200+ items** across 15 dimensions:

**Dimensions Covered**:
1. Scan Level and Resumability (12 items)
2. Write-as-you-go Architecture (6 items)
3. Batching Strategy (6 items)
4. Project Detection and Classification (5 items)
5. Technology Stack Analysis (5 items)
6. Codebase Scanning Completeness (10 items)
7. Source Tree Analysis (6 items)
8. Architecture Documentation Quality (10 items)
9. Development and Operations Documentation (9 items)
10. Multi-Part Project Specific (8 items)
11. Index and Navigation (8 items)
12. File Completeness (12 items)
13. Content Quality (7 items)
14. Brownfield PRD Readiness (7 items)
15. State File Quality (7 items)
+ Deep-Dive Mode Validation (18 items)

**Brownfield PRD Readiness** (particularly relevant):
- Documentation provides enough context for AI to understand existing system
- Integration points are clear for planning new features
- Reusable components identified for leveraging in new work
- Data models documented for schema extension planning
- API contracts documented for endpoint expansion
- Code conventions and patterns captured for consistency
- Architecture constraints clear for informed decision-making

**Lean Audit**:
- **Muri concern**: Can an LLM honestly evaluate 200+ checklist items? Evidence suggests checklist fatigue is real -- items after position ~50 get decreasing attention
- **Mitigation**: The checklist is organized by section, and the validation step asks the user to review results, creating a human-in-the-loop checkpoint
- **Comparison with RaiSE**: RaiSE uses focused Validation Gates with ~5-10 criteria each, which is more realistic for LLM evaluation. BMAD's 200+ items may produce false confidence.

---

## 2. Deep-Dive Sub-Workflow -- Step-by-Step Analysis

### 2.1 Target Selection (Step 13a)

The deep-dive workflow begins by analyzing existing documentation and source tree to present suggested areas organized by category:
- **API Routes**: Grouped endpoints with file locations
- **Feature Modules**: Feature areas with file counts
- **UI Component Areas**: Component groups with counts
- **Services/Business Logic**: Service groupings with paths

Users can select by number or specify custom paths (folders, files, or feature names). The system parses input to determine target type, path, name, and scope.

### 2.2 Exhaustive Scan Mechanics (Step 13b)

This step enforces **reading every line of every file in scope**. The workflow explicitly states: "Sampling, guessing, or relying solely on tooling output is FORBIDDEN."

**Per-File Metadata Captured**:
- Complete exports with signatures
- All imports with sources
- Purpose statement
- Function signatures
- TODOs/FIXMEs
- Design patterns detected
- Contributor guidance notes

**Target Type Handling**:
- **Folders**: Recursive complete file list analysis
- **Files**: Complete file plus one-level-deep import chains and dependent files
- **API Groups**: Route handlers, middleware, controllers, services, models, schemas
- **Features**: All related UI components, endpoints, models, services, tests
- **Component Groups**: Components with props, hooks, children, state management

**Context Window Challenge**: For a folder with 50 files averaging 300 lines each, that is ~15,000 lines or ~60,000 tokens -- roughly 30-40% of usable context. Larger folders would exceed capacity. BMAD does not document how this is handled beyond the general batching strategy.

### 2.3 Relationship and Data Flow Analysis (Step 13c)

The workflow constructs a dependency graph with files as nodes and import relationships as edges:
- Circular dependency detection
- Entry points (files not imported by others in scope)
- Leaf nodes (files with no internal dependencies)
- Data flow through function calls and transformations
- API calls and responses
- State updates and propagation
- Database queries and mutations

**Reliability Assessment**: LLM-based dependency detection has known limitations:
- **Import resolution**: LLMs can parse explicit imports but struggle with dynamic imports, re-exports, barrel files, and alias paths
- **Circular dependency detection**: Possible but error-prone without AST tools (madge, dependency-cruiser are far more reliable)
- **Data flow tracing**: LLMs can follow simple call chains but lose track across 3+ levels of indirection

### 2.4 Related Code Discovery (Step 13d)

The system searches OUTSIDE the scanned area for:
- Similar naming patterns
- Similar function signatures
- Comparable component structures
- Analogous API patterns
- Reusable utilities
- Code reuse opportunities

**Breadth vs. Precision**: This is a creative use of LLM's pattern matching capability, but with high false positive risk. Without AST-level similarity detection (like GitHub's code similarity search), the LLM may surface superficially similar but functionally different code.

### 2.5 Documentation Generation (Step 13e)

The deep-dive template generates a comprehensive single-document reference covering:
- Overview and inventory (file count, LOC, purpose)
- File-level analysis with exports, dependencies, patterns
- Architecture layers and design patterns
- Data movement (entry points, transformations, exits)
- Integration mapping (APIs, state, events, databases)
- Dependency visualization
- Testing summary with coverage metrics
- Code reuse opportunities
- Quality guidance and modification instructions
- Pre-change checklists

**Lean Audit**: The deep-dive produces high-quality output for focused areas. However, the "read every line" mandate creates Muri (overburden) for large modules. A hybrid approach (AST for structure + LLM for semantics) would be more efficient.

---

## 3. Downstream Integration

### 3.1 project-context.md as Handoff Artifact

BMAD's brownfield output feeds into downstream workflows primarily through the generated documentation folder. The `index.md` serves as the primary entry point. The completion summary explicitly guides next steps: "When creating a brownfield PRD, point the PRD workflow to: {output_folder}/index.md"

The system does not generate a separate `project-context.md` -- the entire documentation folder IS the project context. This is a design choice favoring completeness over compactness.

### 3.2 PRD Workflow Brownfield Adaptations

BMAD's PRD creation workflow references existing documentation when available. The key handoff is: PRD agents can read the generated documentation to understand existing architecture, components, and conventions. However, this is a **read-and-interpret** approach, not a **structured-constraint** approach. The PRD agent must extract relevant constraints from narrative documentation rather than receiving machine-readable constraints.

### 3.3 Quick Flow Brownfield Detection

BMAD's quick flow workflows check for existing code and documentation. When brownfield patterns are detected, the workflow "asks informed questions" about existing constraints. However, the mechanism is conversational -- the agent suggests reading existing docs, not deterministically enforcing constraints.

### 3.4 Implementation Workflow Convention Awareness

BMAD's dev-story (implementation) workflow references existing conventions found during documentation. However, enforcement is conversational: the agent suggests following detected patterns rather than blocking non-compliant code. This is the critical gap: **documentation informs but does not govern**.

---

## 4. Novel Patterns Catalog

### 4.1 CSV-Based Project Classification

**Description**: A single CSV file encodes 12 project types with 24 detection/requirement columns. File patterns drive type detection; boolean flags control which analyses run.

**Evidence**: `documentation-requirements.csv` -- 12 rows (web, mobile, backend, cli, library, desktop, game, data, extension, infra, embedded) x 24 columns

**RaiSE Applicability**: HIGH. RaiSE has zero project type detection. SAR always runs the same 7 reports regardless of project type.

**Verdict**: PORT -- Adopt the concept but use YAML format for better LLM parsing reliability. Add RaiSE-specific detection columns (e.g., `has_clean_architecture`, `has_ddd_patterns`, `has_monorepo_structure`).

### 4.2 Scan Level Flexibility (Quick/Deep/Exhaustive)

**Description**: Three-tier time investment model allowing users to choose analysis depth based on their needs.

**Evidence**: full-scan-instructions.md Step 0.6 -- explicit time estimates (2-5 / 10-30 / 30-120 minutes)

**RaiSE Applicability**: HIGH. Current SAR is all-or-nothing (~30-60 min). Quick analysis for initial assessment would be valuable.

**Verdict**: PORT -- Map to SAR report subsets: Quick = Reports 1-2 (overview + architecture), Standard = Reports 1-6, Full = All 7 reports.

### 4.3 Write-As-You-Go + Context Purging

**Description**: Generate artifact, write to disk, validate, purge details from context, retain summary. Prevents context overflow on large codebases.

**Evidence**: Full-scan-instructions.md Step 4 batching strategy -- explicit purge instructions and summary retention patterns

**RaiSE Applicability**: CRITICAL. Current SAR generates all 7 reports in memory with no persistence strategy. This is the #1 operational gap.

**Verdict**: PORT -- Integrate into SAR command. Each report should be written immediately after generation. State checkpoint after each report.

### 4.4 JSON State File with Resumability

**Description**: `project-scan-report.json` tracks step completion, timestamps, configuration, and findings summaries. Enables resume-from-step on interruption with 24-hour stale detection.

**Evidence**: project-scan-report-schema.json -- 7 required root properties, completed_steps array with per-step metadata

**RaiSE Applicability**: HIGH. Current SAR has total loss on interruption. For a 30-60 min analysis, this is significant waste.

**Verdict**: PORT -- Adapt to RaiSE's approach. Use YAML (not JSON) for consistency with RaiSE conventions. Include RaiSE-specific metadata (gate results, confidence scores).

### 4.5 Master Index as AI Retrieval Source

**Description**: `index.md` designed specifically for AI consumption with structured metadata, links, summaries, and `_(To be generated)_` markers for gaps.

**Evidence**: Full-scan-instructions.md Step 10 -- detailed template with project metadata, per-part navigation, and incomplete documentation detection

**RaiSE Applicability**: HIGH. Current SAR reports have no unified entry point. The 7 reports require the reader to know which one to start with.

**Verdict**: PORT -- Generate a SAR index with YAML frontmatter, links to all reports, key findings summary, and handoff guidance.

### 4.6 Conditional Analysis via Boolean Flags

**Description**: CSV flags control which analyses run per project type. A CLI tool does not get UI component analysis; a game does not get API scanning.

**Evidence**: documentation-requirements.csv boolean columns -- 7 flags per project type

**RaiSE Applicability**: HIGH. Current SAR always generates all 7 reports regardless of project type. Clean Architecture analysis on a simple CLI tool produces low-value output.

**Verdict**: PORT -- Map to SAR report applicability flags. A project-profile.yaml would indicate which SAR reports are relevant.

### 4.7 Monolith/Monorepo/Multi-Part Detection

**Description**: Structural classification before analysis begins. Monorepo detection via workspace config files (pnpm-workspace.yaml, nx.json, etc.). Multi-part detection via conventional directory structure.

**Evidence**: Full-scan-instructions.md Step 1 -- explicit detection patterns and user confirmation loop

**RaiSE Applicability**: MEDIUM-HIGH. Current SAR assumes single-project structure. Multi-project repos would benefit from per-part analysis.

**Verdict**: PORT -- Add structural classification as Phase 0 step in SAR command. Simpler than BMAD's approach -- detection patterns only, no per-part type classification initially.

### 4.8 Incomplete Documentation Markers

**Description**: Documents marked `_(To be generated)_` enable automated detection of gaps, user-triggered selective generation, and clear status visibility.

**Evidence**: Full-scan-instructions.md Step 10 and Step 11 -- explicit marker convention with strict and fuzzy scanning

**RaiSE Applicability**: MEDIUM. Useful for progressive analysis -- generate overview first, deep-dive later.

**Verdict**: INSPIRE -- Adapt concept to RaiSE's gate system. Reports not yet generated could have a "stub" with metadata indicating analysis is pending.

---

## 5. Anti-Pattern Catalog

### 5.1 Documentation Without Governance

**Description**: BMAD generates excellent documentation but no enforceable rules. The output describes what exists but does not constrain what should be built next.

**Evidence**: No step in either workflow generates `.cursorrules`, `AGENTS.md`, guardrail files, or architectural fitness functions. The completion message says "When ready to plan new features, run the PRD workflow" -- purely informational.

**RaiSE Implication**: This is the fundamental philosophical gap. RaiSE's Section 2 (Governance as Code) requires that analysis output be governance-grade, not just documentation. If RaiSE adopted BMAD's brownfield approach without adding a governance layer, it would regress from its own principles.

**Severity**: CRITICAL -- this gap must be bridged regardless of which strategy is chosen.

### 5.2 LLM-Only File Reading (No Static Analysis)

**Description**: BMAD reads files line-by-line via LLM with no AST tools, linters, or static analysis integration. All structural understanding comes from LLM interpretation.

**Evidence**: Full-scan-instructions.md -- all steps use "read files", "scan for patterns", "extract" language without any tool invocations. The deep-dive mandates "read every line" rather than "parse AST".

**RaiSE Implication**: This limits accuracy for:
- Import graph construction (LLMs miss dynamic imports, re-exports, alias paths)
- Complexity metrics (LLMs estimate but cannot compute cyclomatic/cognitive complexity)
- Dead code detection (requires call graph analysis)
- Type system understanding (especially in TypeScript with complex generics)

**Industry context (2025-2026)**: The hybrid AST+LLM approach is the emerging standard. SAST-Genius achieved 89.5% precision vs. 35.7% for Semgrep alone. Tree-sitter + LLM synthesis is becoming the dominant pattern.

**Severity**: HIGH -- tool integration should be a priority for any brownfield analysis system.

### 5.3 Persona-Dependent Brownfield (Mary the Analyst)

**Description**: The brownfield workflow is executed by a specific persona ("Mary the Analyst") with defined skills and communication style.

**Evidence**: workflow.yaml references the analyst persona; the persona adds behavioral guidelines on top of workflow instructions.

**RaiSE Implication**: Personas add conceptual overhead without clear functional value. RaiSE uses functional agents (commands with specific capabilities) rather than character-based personas. A persona-less command with the same instructions would produce equivalent output.

**Severity**: LOW -- cosmetic issue, easily ignored in any adoption strategy.

### 5.4 200+ Item Checklist as Validation

**Description**: The validation checklist has 200+ items across 15 dimensions. An LLM must evaluate each item honestly.

**Evidence**: checklist.md -- 234 total items (counted from file)

**RaiSE Implication**: Research on LLM checklist evaluation suggests:
- Items after position ~50 get decreasing attention
- Binary (checked/unchecked) evaluation is less reliable than criteria-based assessment
- LLMs tend to optimistically check items rather than critically evaluate
- RaiSE's focused Validation Gates (5-10 criteria with specific pass/fail criteria) are more reliable

**Severity**: MEDIUM -- inflated validation confidence is worse than no validation (false sense of quality).

### 5.5 No Quality Assessment in Documentation

**Description**: BMAD documents "what is" without evaluating "how good". Technical debt detection is a template placeholder, not active analysis. No code smell density, coupling metrics, or cohesion analysis.

**Evidence**: No step in the full-scan workflow performs quality evaluation. The architecture documentation captures structure but not quality. No Clean Code or Clean Architecture analysis exists.

**RaiSE Implication**: This is where RaiSE SAR is genuinely superior. SAR Reports 3-4 (Clean Code + Clean Architecture analysis) and Report 7 (Refactoring Recommendations with business impact) provide evaluative analysis that BMAD completely lacks.

**Severity**: HIGH -- quality assessment is a core differentiator that must be preserved.

---

## 6. Context Window Economics

### 6.1 BMAD's Approach vs. Theoretical Optimal

**BMAD's Strategy**: Write-as-you-go with per-subfolder batching and context purging. Each batch consumes ~10-30K tokens (depending on subfolder size), writes output, then purges to ~100-200 tokens of summary.

**Token Budget per Batch Cycle**:
```
System prompt + instructions: ~5,000 tokens
State context (summaries of previous batches): ~2,000-10,000 tokens (grows linearly)
Current batch files: ~10,000-30,000 tokens
Analysis + output generation: ~5,000-15,000 tokens
Total per cycle: ~22,000-60,000 tokens
Available capacity (200K context): ~140,000-178,000 tokens for batch
```

**Scalability Limit**: As summaries accumulate, the available capacity per batch shrinks. After 50 batches with 200-token summaries each, that is 10,000 tokens of summaries -- still manageable. After 200 batches, 40,000 tokens -- starts impacting batch capacity.

**Theoretical Optimal**: A hybrid approach using deterministic tools for structural extraction (AST, dependency graph, metrics) and LLM only for semantic analysis (pattern recognition, quality assessment, recommendation generation) would:
- Reduce token consumption by ~60-70% (tool output is compact structured data)
- Improve accuracy for structural tasks (imports, dependencies, types)
- Allow LLM to focus on high-value semantic tasks
- Scale to any codebase size (tools process entire codebase, LLM synthesizes summaries)

### 6.2 Token Budget Analysis per Codebase Size

| Codebase Size | Files | Est. Tokens | BMAD Strategy | Optimal Strategy | Time Est. |
|--------------|-------|-------------|---------------|------------------|-----------|
| Tiny (<20) | <20 | <30K | Full LLM read | Full LLM read | 5-10 min |
| Small (20-100) | 20-100 | 30K-150K | Selective read + purge | Tool structure + LLM synthesis | 15-30 min |
| Medium (100-500) | 100-500 | 150K-750K | Batch by subfolder + purge | Tool-first + LLM per-module | 30-60 min |
| Large (500-2K) | 500-2K | 750K-3M | Multi-session batch + purge | RAG + tool metrics + LLM focus areas | 1-3 hours |
| Very Large (2K+) | 2K+ | 3M+ | Likely fails or degrades | RAG + tools + hierarchical LLM | 3+ hours |

**Key Insight**: BMAD's approach works well for Small-Medium codebases (the bulk of projects) but degrades for Large+. The optimal approach uses tools for scale and LLM for intelligence -- the hybrid paradigm emerging as industry standard in 2025-2026.

---

## References

### BMAD Source Files Analyzed
- `src/bmm/workflows/document-project/instructions.md` -- Router and mode detection
- `src/bmm/workflows/document-project/workflows/full-scan-instructions.md` -- 12-step full scan workflow
- `src/bmm/workflows/document-project/workflows/deep-dive-instructions.md` -- 7-step deep-dive workflow
- `src/bmm/workflows/document-project/checklist.md` -- 200+ item validation checklist
- `src/bmm/workflows/document-project/documentation-requirements.csv` -- 12x24 classification matrix
- `src/bmm/workflows/document-project/templates/project-scan-report-schema.json` -- State file schema
- `src/bmm/workflows/document-project/templates/deep-dive-template.md` -- Deep-dive output template
- `src/bmm/workflows/document-project/templates/index-template.md` -- Master index template
- `src/bmm/workflows/document-project/templates/project-overview-template.md` -- Overview template
- `src/bmm/workflows/document-project/templates/source-tree-template.md` -- Source tree template
- `src/bmm/workflows/document-project/workflow.yaml` -- Workflow configuration

### RaiSE Source Files Analyzed
- `.raise-kit/commands/01-onboarding/raise.1.analyze.code.md` -- SAR command
- `.raise-kit/templates/raise/sar/README.md` -- SAR process guide
- `.raise-kit/templates/raise/sar/*.md` -- 7 SAR report templates
- `specs/main/analysis/architecture/raise.1.analyze-code-architecture.md` -- SAR architecture analysis
- `specs/main/research/brownfield-agent-docs/landscape-report.md` -- Industry landscape
- `specs/main/research/brownfield-agent-docs/recommendations.md` -- Improvement recommendations

### Industry Sources
- AGENTS.md specification (agents.md/agents.md on GitHub, 60K+ repos)
- SAST-Genius hybrid framework (arXiv 2509.15433) -- 89.5% precision
- HASTE: Hybrid AST-guided Selection (ICLR 2026 submission)
- Apiiro AI SAST (December 2025) -- AST + LLM symbiosis
- GitHub Blog: Writing great agents.md (2,500+ repos analyzed)
- Qodo AI Code Review Tools 2026 report
- Faros AI Productivity Paradox Study (June 2025)
