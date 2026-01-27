# Deep Research Prompt: BMAD Method Competitive Analysis

**Research ID**: RES-BMAD-COMPETE-001
**Date Created**: 2026-01-27
**Priority**: High
**Estimated Effort**: 4-6 hours of research + 3-4 hours of synthesis
**Target Outcome**: Actionable competitive intelligence for RaiSE differentiation against BMAD Method

---

## Research Objective

Investigate the BMAD Method (Breakthrough Method of Agile AI Driven Development) as a **direct competitor** to RaiSE's agentic development framework, to:

1. **Map BMAD's architecture and philosophy** with precision, identifying core design decisions and their tradeoffs
2. **Identify BMAD's strengths** that represent competitive threats to RaiSE adoption
3. **Identify BMAD's weaknesses and blind spots** that represent differentiation opportunities for RaiSE
4. **Analyze BMAD's community traction and adoption signals** to assess market positioning
5. **Compare BMAD's execution model** (LLM-as-runtime, pure prompt engineering) against RaiSE's governance-as-code approach
6. **Evaluate BMAD's validation and quality model** against RaiSE's Lean/Jidoka-based Validation Gates
7. **Extract concrete strategic recommendations** for RaiSE positioning, feature priorities, and messaging

**Core Question**: Where does BMAD Method outperform, match, or fall short compared to RaiSE -- and how should RaiSE respond strategically?

---

## Research Scope

### In Scope

1. **Architecture analysis**: Module system, agent model, workflow execution, step-file architecture, state tracking
2. **Philosophy analysis**: "AI as collaborator" thesis, progressive context building, adversarial review patterns
3. **Agent model critique**: Rich personas (named characters), YAML definitions, activation patterns, multi-agent "Party Mode"
4. **Workflow model critique**: Micro-file architecture, Just-In-Time loading, YOLO mode, dual-track (Quick Flow vs Full Planning)
5. **Validation and governance model**: Adversarial reviews, checklists, readiness gates, sprint status tracking
6. **Platform strategy**: 18+ IDE/CLI integrations, npm installer, cross-platform delivery
7. **Community and adoption signals**: GitHub activity, npm downloads, community contributions, documentation quality
8. **Scalability analysis**: Context window management, document sharding, project complexity limits
9. **Brownfield support**: How BMAD handles existing codebases vs greenfield
10. **Extension model**: Module system, BMad Builder, custom agent/workflow creation
11. **Competitive claims**: Direct and indirect positioning against similar tools

### Out of Scope

- BMAD's game development module (BMGD) specifics beyond architectural patterns
- Creative Intelligence Suite (CIS) unless it reveals transferable patterns
- Line-by-line code review of the npm CLI tool
- BMAD's pricing or commercial model (it's MIT licensed)
- Comparison with tools other than RaiSE (spec-kit comparison already done separately)

---

## Key Research Questions

### Category 1: Architecture and Execution Model

**Q1.1**: How does BMAD's "LLM-as-runtime" architecture compare to RaiSE's governance-as-code model?

**Investigate**:
- **Execution paradigm**: BMAD has no code runtime; the LLM processes XML/YAML/MD instructions as its "operating system"
  - What are the reliability implications? Can the LLM faithfully follow `workflow.xml` every time?
  - How brittle is this approach across different LLM providers and versions?
  - What happens when the LLM "optimizes" or skips steps despite explicit anti-optimization instructions?
- **State management**: BMAD tracks state in output file frontmatter (`stepsCompleted` arrays)
  - Is this reliable? What happens on LLM context window overflow?
  - Compare with RaiSE's approach to state and continuity
- **Variable resolution**: BMAD uses a custom `{config_source}:field` and `{{user_name}}` syntax resolved by the LLM
  - How reliable is LLM-driven variable resolution vs. deterministic code?
  - Error handling when variables are missing or malformed?
- **Anti-optimization enforcement**: BMAD repeatedly instructs "NEVER skip steps", "NEVER optimize", "NEVER load multiple step files"
  - Does this work in practice? Evidence of LLMs violating these constraints?
  - Is this a fundamental fragility of prompt-engineering-only frameworks?

**Look for**:
- GitHub Issues about LLM non-compliance with workflow instructions
- Reports of workflows breaking on different LLM providers
- Community discussions about reliability and consistency
- Comparisons between BMAD's approach and code-based orchestration
- Blog posts or discussions about "prompt engineering as runtime" limitations

---

**Q1.2**: How effective is BMAD's micro-file step architecture?

**Investigate**:
- **Just-In-Time loading**: Each step is a separate file, loaded one-at-a-time
  - Does this effectively manage context window limits?
  - What information is lost between steps? How is inter-step context preserved?
  - Compare with RaiSE's approach to context management
- **Step decomposition granularity**: Steps are 150-250 lines each
  - Is this the right granularity? Too fine (loss of big picture)? Too coarse?
  - How does this affect LLM reasoning about the overall workflow?
- **Mandatory sequential execution**: No parallelism, no skipping, strict ordering
  - When is this a strength (consistency)? When is this a weakness (inflexibility)?
  - How does this interact with iterative/agile development practices?
- **Append-only document building**: Documents built by appending section by section
  - Quality implications? Does the LLM lose coherence across appended sections?
  - How do later sections reference or adjust earlier sections?

**Look for**:
- Issues about step files losing context
- Discussions about workflow flexibility and customization
- Reports of document quality degradation across many steps
- Comparisons of monolithic vs. micro-file approaches for LLM workflows
- Evidence of step-file sizes and their relationship to output quality

---

**Q1.3**: What are the tradeoffs of BMAD's module system?

**Investigate**:
- **Module architecture**: Self-contained modules with `module.yaml`, dependency resolution
  - How does this compare to RaiSE's `.raise-kit` architecture?
  - What can be extended? What is locked?
  - How do modules interact? Cross-module dependencies?
- **BMad Builder**: Module for creating custom agents and workflows
  - How accessible is this? What's the learning curve?
  - Compare with RaiSE's command creation process (rule 110)
- **Installation model**: `npx bmad-method install` with IDE detection
  - How seamless is this in practice? Installation failures?
  - What about updates and version management?
  - Compare with RaiSE's `transform-commands.sh` injection model

**Look for**:
- Custom modules built by the community
- Module creation tutorials or guides
- Installation issues and troubleshooting
- Discussions about extensibility and customization limits
- BMad Builder adoption and usage reports

---

### Category 2: Agent Model and Collaboration Philosophy

**Q2.1**: How effective is BMAD's "named persona" agent model?

**Investigate**:
- **Rich personas**: Each agent has a human name (Mary, John, Winston, etc.), personality traits, communication style
  - Does this improve user experience and engagement?
  - Does it improve LLM output quality?
  - Or is it cosmetic theater that adds no value?
- **Persona consistency**: Can the LLM maintain consistent persona behavior across a long session?
  - Evidence of persona bleed or inconsistency?
  - How does this behave on smaller/weaker LLMs?
- **Agent specialization**: 9 specialized agents for different roles
  - How deep is the specialization? Is "Winston the Architect" meaningfully different from a generic architecture prompt?
  - Are the YAML agent definitions sufficient to create genuine specialization?
  - Compare with RaiSE's agent model (Ontology Architect, etc.)
- **"AI as collaborator, not doer" thesis**: BMAD claims agents "guide you through structured process to bring out your best thinking"
  - Is this actually achieved in the prompts and workflows?
  - Or do the agents still end up doing the thinking for the user?
  - How does this compare to RaiSE's Heutagogy (self-directed learning) principle?

**Look for**:
- User testimonials about persona effectiveness
- Discussions about whether named agents improve outcomes
- Comparisons between generic prompts and persona-driven prompts
- Research on persona effectiveness in LLM interactions
- Community feedback on specific agents (which are most/least valued?)

---

**Q2.2**: How does BMAD's "Party Mode" (multi-agent discussion) work in practice?

**Investigate**:
- **Orchestration mechanism**: Multiple personas in one conversation, selected by relevance analysis
  - How is relevance determined? How are turns allocated?
  - Is this genuinely multi-perspective or just one LLM wearing different hats?
  - Quality of the "discussion" -- does it surface genuine tensions and tradeoffs?
- **Team definitions**: Teams bundle agents (e.g., `team-fullstack.yaml`)
  - How configurable are teams? Can users create custom teams?
  - What's the context window cost of maintaining multiple personas?
- **Creative Intelligence Suite personas**: Historical figures (Da Vinci, Jobs, De Bono)
  - Gimmick or genuinely useful for ideation?
  - How do these compare to standard brainstorming techniques?

**Look for**:
- Party Mode usage examples and outcomes
- Community opinions on multi-agent discussions
- Context window consumption data for Party Mode
- Comparisons with single-agent approaches
- Research on multi-agent LLM architectures (academic and practical)

---

**Q2.3**: How does BMAD's "adversarial review" pattern compare to RaiSE's Jidoka + Validation Gates?

**Investigate**:
- **Adversarial framing**: BMAD instructs the LLM to be "a cynical, jaded reviewer" who MUST find minimum N issues
  - Does this actually produce better reviews?
  - Or does it produce inflated issue counts with trivial findings?
  - How does "find 3-10 issues minimum" interact with genuine quality?
- **Code review workflow**: `code-review` workflow with adversarial stance
  - How thorough vs. RaiSE's approach?
  - What does it check? What does it miss?
  - How does it handle false positives?
- **Competitive framing**: "COMPETITION to outperform the original LLM"
  - Effective prompt engineering technique? Evidence?
  - Does this generalize beyond BMAD's context?
- **RaiSE comparison points**:
  - RaiSE uses Validation Gates with explicit criteria (Gate-Terminologia, Gate-Coherencia, etc.)
  - RaiSE uses Jidoka (stop-at-defects) inline in every step
  - RaiSE gates are external to workflows (separation of concerns)
  - BMAD validation is workflow-internal (checklists embedded in step files)
  - Which approach produces more reliable quality outcomes?

**Look for**:
- Adversarial review output examples
- Discussions about review quality
- False positive rates in adversarial reviews
- Research on adversarial prompting for quality assurance
- Comparisons between embedded vs. external validation approaches

---

### Category 3: Workflow and Development Process

**Q3.1**: How does BMAD's 4-phase development model compare to RaiSE's workflow?

**Investigate**:
- **Phase structure**: Analysis → Planning → Solutioning → Implementation
  - How rigid is this sequence? Can phases be skipped or reordered?
  - Is this functionally waterfall with agile labels?
  - How does "Quick Flow" (3-command path) relate to the full 4-phase path?
- **PRD workflow** (12 create steps, 13 validation steps, 5 edit steps):
  - Is this proportionate? 30 steps for a PRD seems heavy
  - Compare with RaiSE's specification approach
  - What happens for small features vs. large products?
- **Architecture workflow** (8-step collaborative facilitation):
  - How does this compare to RaiSE's tech design command?
  - Quality of the architecture outputs?
  - ADR support? Decision tracking?
- **Sprint/Story/Dev workflows**:
  - How does BMAD handle implementation planning?
  - Sprint status tracking via YAML -- effective?
  - Story creation and validation -- how thorough?
- **Quick Flow path**:
  - `/quick-spec` + `/quick-dev` -- what gets skipped?
  - Is this adequate for non-trivial features?
  - Compare with RaiSE's proportional specification approach

**Look for**:
- User experiences with the full 4-phase path
- Complaints about ceremony or overhead
- Quick Flow adoption vs. full path adoption
- Time-to-first-implementation data
- Phase skip patterns (which phases do people skip?)

---

**Q3.2**: How does BMAD handle the "documentation overhead" problem?

**Investigate**:
- **Artifact volume**: How many documents does a typical BMAD workflow produce?
  - PRD + Architecture + Epics + Stories + Sprint Status + ...
  - Total markdown lines generated for a typical feature?
  - Compare with spec-kit's 3.7:1 markdown:code ratio finding
- **Document sharding**: Large artifacts split into directories with `index.md`
  - Does this solve or merely manage the volume problem?
  - How do users navigate sharded documents?
  - Is this a sign that artifacts are too large?
- **Progressive context building**: Each phase produces context for the next
  - How much redundancy exists between phase artifacts?
  - Does information get duplicated across PRD → Architecture → Epics → Stories?
  - Is there an equivalent of RaiSE's redundancy detection opportunity?
- **YOLO mode**: Skip confirmations for rapid generation
  - Does this address the overhead problem or just hide it?
  - What's the quality tradeoff?
  - How many users prefer YOLO mode vs. interactive mode?

**Look for**:
- User complaints about documentation volume
- Discussions about "too much overhead" or "too much ceremony"
- YOLO mode adoption signals
- Document size data from real BMAD projects
- Comparisons with lighter-weight approaches

---

**Q3.3**: How does BMAD handle brownfield (existing codebase) scenarios?

**Investigate**:
- **Explicit brownfield support**: Does BMAD have brownfield-specific workflows?
  - `project-context.md` management -- what does this capture?
  - Brownfield detection and adaptation mechanisms?
  - Compare with RaiSE's brownfield-first architecture strategy
- **Codebase documentation workflow**: `document-project` workflow
  - What does this produce? How thorough?
  - Can it integrate with existing documentation?
  - How does it handle large, complex codebases?
- **Existing architecture integration**: Can BMAD work with established architecture patterns?
  - Or does it assume greenfield and impose its own patterns?
  - How does the architecture workflow handle "architecture already exists" scenarios?
- **Incremental adoption**: Can teams adopt BMAD partially?
  - Use only certain workflows? Skip certain phases?
  - Or is it all-or-nothing?

**Look for**:
- Brownfield project examples
- Issues about existing codebase integration
- Community workarounds for brownfield scenarios
- Comparison with RaiSE's brownfield-first positioning
- Documentation about `project-context.md` usage patterns

---

### Category 4: Platform Strategy and Ecosystem

**Q4.1**: What is the strategic significance of BMAD's 18+ platform support?

**Investigate**:
- **Platform list**: Claude Code, Cursor, Windsurf, Gemini CLI, GitHub Copilot, Cline, Roo, OpenCode, Codex, KiloCoder, Kiro CLI, Crush, iFlow, QwenCoder, Rovo Dev, Trae, Google Antigravity, Auggie
  - How deep is each integration? Surface-level (command format) vs. deep (native features)?
  - Which platforms have the best BMAD experience?
  - Does broad support mean shallow support?
- **Platform-agnostic source → Platform-specific install**:
  - How well does the translation work for each platform?
  - What capabilities are lost in translation?
  - Compare with RaiSE's platform approach
- **Market coverage implications**:
  - Does supporting 18+ platforms create a network effect?
  - Or does it spread effort too thin?
  - What platforms matter most for RaiSE's target audience?
- **Installer quality**: `npx bmad-method install` experience
  - How reliable? How fast?
  - Error handling? Recovery from partial installs?
  - Compare with RaiSE's injection model (`transform-commands.sh`)

**Look for**:
- Platform-specific issues and bugs
- User experiences on different platforms
- Platform adoption distribution (which platforms are most used?)
- Installation troubleshooting threads
- Community requests for new platform support

---

**Q4.2**: How does BMAD's npm packaging model compare to RaiSE's git-based distribution?

**Investigate**:
- **npm distribution**: `bmad-method` package on npmjs.com
  - Download counts and trends
  - Version history and release cadence
  - Dependency footprint
- **Installation artifact**: `_bmad/` directory with all module artifacts
  - What gets installed? Size of installation?
  - How does this interact with version control (`.gitignore`)?
  - Update mechanism? How do users get new versions?
- **Configuration model**: `config.yaml` with user preferences
  - Skill level adaptation (beginner/intermediate/expert)
  - Language preferences
  - Output folder customization
  - Compare with RaiSE's configuration approach

**Look for**:
- npm download statistics
- Version adoption patterns
- Community size indicators (GitHub stars, forks, contributors)
- Package quality signals (tests, CI, release notes)
- Discussions about distribution model preferences

---

**Q4.3**: How mature is BMAD's extension ecosystem?

**Investigate**:
- **Community modules**: Are there third-party BMAD modules?
  - What do they add? How many exist?
  - Quality and maintenance status
- **Agent customization**: How do users create custom agents?
  - BMad Builder module -- usage and adoption?
  - Community-created agents?
- **Workflow customization**: Can users modify or create workflows?
  - What's the process? What tools exist?
  - How accessible is this to non-developers?
- **Integration with external tools**: CI/CD, project management, etc.
  - Built-in integrations?
  - Community-built integrations?

**Look for**:
- Third-party modules and extensions
- Community contributions to the main repo
- Integration examples
- Customization guides and tutorials
- BMad Builder usage evidence

---

### Category 5: Quality, Governance, and Reliability

**Q5.1**: How robust is BMAD's quality assurance model?

**Investigate**:
- **Validation coverage**: What is validated vs. what is assumed correct?
  - PRD validation (13 steps) -- comprehensive or checkbox-theater?
  - Architecture validation -- depth of analysis?
  - Implementation readiness check -- what does it actually verify?
  - Story validation -- effective guard against bad stories?
- **Adversarial review effectiveness**: Does forcing minimum issue counts improve quality?
  - Risk of Goodhart's Law: When finding N issues becomes the target, does quality degrade?
  - Comparison with RaiSE's specific, criteria-based gates (Gate-Terminologia, Gate-Coherencia, etc.)
- **Cross-artifact consistency**: Does BMAD check that PRD → Architecture → Epics → Stories are aligned?
  - Implementation readiness gate -- how thorough?
  - Compare with RaiSE's Gate-Trazabilidad (traceability)
- **Semantic coherence**: Does BMAD enforce terminology consistency?
  - Compare with RaiSE's Glosario and Gate-Terminologia
  - Is there an equivalent of RaiSE's ontological coherence checking?

**Look for**:
- Quality outcomes from BMAD workflows (user reports)
- Validation bypass or failure reports
- Cross-artifact consistency issues
- Terminology or semantic drift in BMAD outputs
- Comparisons between BMAD validation and other approaches

---

**Q5.2**: How does BMAD handle failure modes and error recovery?

**Investigate**:
- **Workflow interruption**: What happens when a workflow is interrupted mid-execution?
  - State recovery from frontmatter -- reliable?
  - Can workflows be resumed? From which point?
  - What information is lost on interruption?
- **LLM hallucination in workflows**: What happens when the LLM generates incorrect workflow artifacts?
  - Are there guardrails against hallucinated architecture decisions?
  - How are incorrect PRD sections detected and corrected?
  - Compare with RaiSE's Jidoka (stop-at-defects) approach
- **Context window exhaustion**: What happens when artifacts exceed context limits?
  - Document sharding as mitigation -- effective?
  - What degrades first? What breaks?
  - How does BMAD handle very large projects?
- **LLM provider changes**: How resilient is BMAD to model updates?
  - Instructions that work on Claude 3.5 but not Claude Opus 4.5?
  - Prompt sensitivity across providers?
  - Testing strategy for prompt compatibility?

**Look for**:
- Bug reports about workflow failures
- Recovery and resume issues
- Context window problems
- Cross-model compatibility issues
- Discussions about prompt fragility

---

**Q5.3**: Does BMAD exhibit "Governance Theater" vs. genuine governance?

**Investigate**:
- **Checklist-based validation**: Every workflow has a `checklist.md`
  - Are these checklists genuinely verified or just listed?
  - Can the LLM "check" items without actually verifying them?
  - Compare with RaiSE's executable Validation Gates
- **Sprint status tracking**: YAML-based sprint status
  - Manually updated by LLM → is it accurate?
  - Does anyone actually use this for project management?
  - Compare with real project management tool integration
- **"NEVER/ALWAYS" instruction patterns**: BMAD heavily uses absolute constraints
  - "NEVER skip steps", "ALWAYS halt at menus", "NEVER optimize"
  - How reliably do LLMs follow absolute constraints?
  - Is this governance or hope?
- **Audit trail**: Does BMAD produce traceable decision records?
  - Compare with RaiSE's ADR system
  - Can you trace why a specific architectural decision was made?
  - Is there a rationale chain from requirements to implementation?

**Look for**:
- Discussions about governance effectiveness
- Examples of checklist bypass or failure
- Sprint status accuracy reports
- Decision traceability in BMAD projects
- Comparisons between prompt-based and code-based governance

---

### Category 6: Community, Adoption, and Market Position

**Q6.1**: What is BMAD's community traction and adoption trajectory?

**Investigate**:
- **GitHub metrics**: Stars, forks, watchers, contributors, issue activity
  - Growth trajectory (plot over time if possible)
  - Contributor diversity (one person or community?)
  - Issue resolution speed and quality
  - PR acceptance patterns
- **npm metrics**: Downloads, dependents, version history
  - Weekly/monthly download trends
  - Version adoption (are users on latest?)
  - Competing packages in the same space?
- **Community channels**: Discord, Reddit, blog, social media
  - Active community? Size?
  - Quality of discussions?
  - Maintainer responsiveness?
- **Documentation and learning resources**:
  - Quality of docs site (website/ directory)
  - Tutorials, how-tos, examples
  - Video content, conference talks?
  - Compare with RaiSE's documentation approach

**Look for**:
- GitHub star count and growth rate
- npm download trends
- Community Discord/Slack member counts
- Blog posts about BMAD (by users, not just maintainer)
- Conference talk mentions
- Social media sentiment (Twitter/X, Reddit, HN)

---

**Q6.2**: How does BMAD position itself against competitors?

**Investigate**:
- **Direct positioning**: Does BMAD explicitly compare itself to other tools?
  - Mentioned competitors in README, docs, or marketing?
  - What claims does it make?
  - How accurate are these claims?
- **Indirect positioning**: What unique value does BMAD emphasize?
  - "Traditional AI tools do the thinking for you" -- who is this attacking?
  - "Expert collaborators" framing -- how distinctive is this?
  - "Breakthrough" in the name -- what breakthrough?
- **Target audience overlap with RaiSE**:
  - Solo developers using AI tools -- shared audience?
  - Enterprise teams -- does BMAD target this? How?
  - Brownfield teams -- does BMAD address this?
- **Feature comparison matrix**:
  - BMAD vs. RaiSE feature-by-feature
  - Where does BMAD clearly win?
  - Where does RaiSE clearly win?
  - Where is it ambiguous?

**Look for**:
- BMAD's positioning statements
- User comparisons of BMAD with other tools
- "Why I chose BMAD over X" blog posts
- Discussions about BMAD's unique value proposition
- Feature requests that reveal perceived gaps vs. competitors

---

**Q6.3**: Who is behind BMAD and what is the sustainability trajectory?

**Investigate**:
- **Maintainer**: Brian "BMad" Madison / BMad Code, LLC
  - Solo project or team?
  - Background and credibility?
  - Commit frequency and consistency?
  - Long-term sustainability concerns?
- **Business model**: MIT license, open source
  - How is development funded?
  - Is there a commercial version or services?
  - Sustainability of open source only?
- **Roadmap**: What's planned for BMAD's future?
  - Announced features or directions?
  - Version history trajectory (v6.0.0-Beta.2 -- how fast is iteration?)
  - Alignment with AI tooling evolution?
- **Risk assessment**: What happens if the maintainer stops?
  - Bus factor?
  - Forkability?
  - Community depth for continuity?

**Look for**:
- Maintainer's public profiles and history
- Commit history patterns
- Roadmap documents or discussions
- Business model hints
- Community sustainability indicators

---

### Category 7: Head-to-Head Comparison (BMAD vs. RaiSE)

**Q7.1**: Where does BMAD clearly outperform RaiSE?

**Investigate critically and honestly**:
- **Platform breadth**: 18+ platforms vs. RaiSE's narrower support
  - Is this a meaningful advantage or spread too thin?
  - Which platforms matter most to target users?
- **Installation experience**: `npx install` vs. script-based injection
  - First-time user experience comparison
  - Time to first useful output
- **Agent richness**: Named personas with personalities vs. functional agents
  - User engagement and satisfaction
  - Output quality differences
- **Quick Flow**: Lightweight path for simple tasks
  - Does RaiSE have an equivalent minimal path?
  - Is this important for adoption?
- **Test architecture knowledge base**: 30+ specialized documents
  - Does RaiSE have equivalent depth in any domain?
  - How valuable is this domain knowledge?
- **Multi-agent Party Mode**: No RaiSE equivalent
  - Is this genuinely useful or a gimmick?
  - Should RaiSE consider something similar?

**Be honest about threats to RaiSE. This is competitive intelligence, not cheerleading.**

---

**Q7.2**: Where does RaiSE clearly outperform BMAD?

**Investigate with evidence**:
- **Governance-as-Code vs. Prompt-as-Governance**:
  - RaiSE: Rules, gates, and constraints as versionable, testable code artifacts
  - BMAD: Governance embedded in prompts and checklists (LLM-dependent)
  - Which is more reliable? More auditable? More evolvable?
- **Lean principles and Jidoka**:
  - RaiSE: Systematic waste elimination, stop-at-defects, observable workflow
  - BMAD: No explicit Lean foundation; "adversarial review" is not Jidoka
  - Is BMAD's 30-step PRD workflow "Muda" (waste)?
- **Ontological coherence**:
  - RaiSE: Canonical terminology (Glosario), semantic validation, ADR traceability
  - BMAD: No terminology governance; no semantic coherence checking
  - Does this matter for real projects?
- **Brownfield-first architecture**:
  - RaiSE: Explicit brownfield support as strategic differentiator
  - BMAD: Primarily greenfield-oriented
  - Market size of brownfield vs. greenfield projects
- **Evidence-based methodology**:
  - RaiSE: Constitution, glosario, katas -- coherent intellectual framework
  - BMAD: Agile/Scrum terminology but no explicit methodology foundation
  - Which approach creates more trustworthy outcomes?
- **Simplicity and focus**:
  - RaiSE: "Simplicity over completeness" principle
  - BMAD: Complex module system, many agents, many workflows, many modes
  - Is BMAD over-engineered? Does complexity become a burden?

**Be evidence-based. RaiSE advantages must be demonstrable, not assumed.**

---

**Q7.3**: What should RaiSE adopt, adapt, or reject from BMAD?

**For each BMAD feature/pattern, evaluate**:

- **ADOPT (take as-is or with minor adaptation)**:
  - Which BMAD patterns are genuinely good ideas that RaiSE lacks?
  - Can they be adopted without violating RaiSE principles?
  - Implementation effort vs. value

- **ADAPT (transform to fit RaiSE philosophy)**:
  - Which BMAD ideas are good in concept but flawed in execution?
  - How would RaiSE implement them differently?
  - What would a "Lean" version of these features look like?

- **REJECT (explicitly not adopt, with rationale)**:
  - Which BMAD patterns contradict RaiSE principles?
  - Why are they wrong or suboptimal?
  - What is RaiSE's alternative answer to the same problem?

**Specific candidates to evaluate**:
1. Named persona agents (Mary, John, Winston...)
2. Party Mode (multi-agent discussions)
3. Adversarial review pattern (minimum N issues)
4. Micro-file step architecture (Just-In-Time loading)
5. YOLO mode (skip confirmations)
6. Quick Flow (lightweight path)
7. Module system with `module.yaml`
8. npm installer with IDE detection
9. Document sharding (`shard-doc.xml`)
10. Sprint status YAML tracking
11. TestArch knowledge base
12. Team definitions for multi-agent sessions
13. Competitive framing in prompts ("COMPETITION to outperform...")
14. CSV-based domain/project type classification
15. Skill-level-adaptive agent behavior

---

### Category 8: Strategic Implications

**Q8.1**: What is BMAD's most dangerous competitive threat to RaiSE?

**Investigate**:
- **Adoption velocity**: Is BMAD growing faster than RaiSE?
  - If so, why? What's driving adoption?
  - Can RaiSE match or counter this?
- **Platform lock-in**: Does BMAD's wide platform support create switching costs?
  - If users start with BMAD, what's the migration cost to RaiSE?
  - How sticky is BMAD's workflow and artifact format?
- **Community network effects**: Does BMAD have community momentum?
  - Community-created modules, agents, workflows?
  - Word-of-mouth and recommendation patterns?
- **AI tool ecosystem alignment**: Is BMAD better aligned with where AI tools are headed?
  - IDE-first vs. framework-first?
  - Prompt engineering vs. code-based governance?
  - Which approach has more future upside?

---

**Q8.2**: What positioning should RaiSE take relative to BMAD?

**Investigate positioning options**:

- **Option A: "Professional grade BMAD"**
  - RaiSE as the enterprise/professional version with real governance
  - Message: "BMAD is a toy; RaiSE is production"
  - Risk: Alienating BMAD's community; arrogant positioning

- **Option B: "Lean alternative to BMAD"**
  - RaiSE as the simpler, more focused, less ceremonious option
  - Message: "BMAD over-engineers; RaiSE eliminates waste"
  - Risk: BMAD's breadth may appeal more to beginners

- **Option C: "Complementary, not competitive"**
  - RaiSE focuses on governance/quality; BMAD focuses on workflow
  - Message: "Use both -- BMAD for flow, RaiSE for quality"
  - Risk: Confusing positioning; unclear value proposition

- **Option D: "Different philosophy, different audience"**
  - RaiSE targets brownfield teams with Lean culture
  - BMAD targets greenfield solo devs with agile aspirations
  - Message: "Choose based on your context"
  - Risk: Limiting market by conceding segments to BMAD

**Evaluate each option against RaiSE's constitution and principles**

---

**Q8.3**: What is the 6-month and 12-month competitive outlook?

**Investigate**:
- **BMAD trajectory**: Where is BMAD heading based on recent commits, issues, discussions?
  - New features in development?
  - Platform additions?
  - Module ecosystem growth?
- **RaiSE trajectory**: Based on current roadmap and research findings
  - Where can RaiSE accelerate?
  - Where should RaiSE invest defensively?
  - Where should RaiSE ignore BMAD and focus on unique strengths?
- **Market evolution**: How is the agentic development tool market evolving?
  - New entrants?
  - Platform consolidation?
  - User preference shifts?
  - LLM capability improvements that change the game?
- **Convergence/divergence**: Will BMAD and RaiSE converge or diverge over time?
  - Are they solving the same problem differently?
  - Or solving different problems with similar tools?

---

## Research Sources

### Primary Sources (Highest Value)

1. **BMAD GitHub Repository**: `https://github.com/bmad-code-org/BMAD-METHOD`
   - README, docs, source code (agents, workflows, tasks, templates)
   - Issues (open and closed) -- bugs, feature requests, limitations
   - Pull requests -- what's being added/changed/rejected
   - Discussions -- community conversations
   - Stars, forks, contributors -- adoption signals
   - Commit history -- development velocity and patterns

2. **npm Package**: `bmad-method`
   - Download statistics and trends
   - Version history and release notes
   - Dependent packages
   - Package quality metrics

3. **BMAD Documentation Site**: (website/ directory or published docs)
   - Tutorials, how-tos, concepts, references
   - Quality and completeness assessment
   - Gap analysis vs. user needs

4. **Community Channels**:
   - Discord server (if exists)
   - Reddit mentions
   - Hacker News discussions
   - Twitter/X mentions
   - Dev.to, Medium articles
   - YouTube videos/tutorials

### Secondary Sources

5. **Competitor Landscape**:
   - Spec-kit (already analyzed -- `specs/main/research/speckit-critiques/`)
   - Other agentic development frameworks (Aider, Mentat, SWE-Agent, Devon, etc.)
   - AI coding tool documentation (Claude Code, Cursor, Windsurf)

6. **Academic/Theoretical**:
   - Research on prompt engineering reliability
   - Studies on multi-agent LLM systems
   - Context window management strategies
   - Software engineering methodology comparisons

7. **Industry Analysis**:
   - AI coding tool market reports
   - Developer survey data (Stack Overflow, JetBrains)
   - Agentic development trend analyses
   - Conference talks on AI-assisted development

8. **RaiSE Internal Sources**:
   - Constitution: `docs/framework/v2.1/model/00-constitution-v2.md`
   - Glosario: `docs/framework/v2.1/model/20-glossary-v2.1.md`
   - Spec-kit critique results: `specs/main/research/speckit-critiques/`
   - Differentiation strategy: `specs/main/research/speckit-critiques/differentiation-strategy.md`
   - Architecture decisions: `docs/framework/v2.1/adrs/`

---

## Analysis Framework

For each BMAD feature, pattern, or design decision, evaluate:

### Competitive Assessment
- [ ] **Threat Level**: No threat / Minor / Moderate / Significant / Critical
- [ ] **RaiSE Equivalent**: None / Weaker / Comparable / Stronger
- [ ] **User Impact**: Cosmetic / Convenience / Productivity / Quality / Reliability
- [ ] **Time Sensitivity**: Can wait / Should address in 6 months / Must address now

### Quality Assessment (Apply RaiSE Lean Audit)
- [ ] **Muda (Waste)**: Does this feature eliminate waste or create it?
- [ ] **Mura (Unevenness)**: Is this feature consistently useful or situational?
- [ ] **Muri (Overburden)**: Does this feature add cognitive/process burden?

### Strategic Assessment
- [ ] **Adopt / Adapt / Reject**: Should RaiSE take, transform, or ignore this?
- [ ] **Alignment with RaiSE Constitution**: Supports / Neutral / Contradicts
- [ ] **Implementation Feasibility**: Easy / Moderate / Hard / Requires architecture change
- [ ] **Differentiation Impact**: Makes RaiSE stronger / Merely matches BMAD / Distracts from core

---

## Synthesis Requirements

### Deliverable 1: BMAD Competitive Analysis Report

**Format**: Markdown document (~6-8K words)

**Structure**:
```markdown
# BMAD Method: Competitive Analysis for RaiSE

## Executive Summary
- BMAD in one paragraph
- Top 3 competitive threats to RaiSE
- Top 3 differentiation opportunities for RaiSE
- Recommended strategic posture

## 1. Architecture Deep Dive

### 1.1 LLM-as-Runtime Model
- How it works
- Strengths and weaknesses
- Reliability assessment
- Comparison with RaiSE

### 1.2 Micro-File Step Architecture
- Design and rationale
- Effectiveness analysis
- Context window management
- Implications for RaiSE

### 1.3 Module System
- Architecture and extensibility
- Community adoption
- Comparison with RaiSE's approach

## 2. Agent Model Analysis

### 2.1 Named Persona Agents
- Effectiveness assessment
- User experience impact
- Quality impact

### 2.2 Multi-Agent Party Mode
- Design and execution
- Practical value
- Competitive significance

### 2.3 Adversarial Review Pattern
- Mechanism and effectiveness
- Comparison with Jidoka/Validation Gates
- Lessons for RaiSE

## 3. Workflow and Process Comparison

### 3.1 4-Phase Development Model
- Structure analysis
- Agile compatibility
- Overhead assessment

### 3.2 Quick Flow vs Full Planning
- Dual-track strategy analysis
- User adoption patterns
- Implications for RaiSE

### 3.3 Documentation Overhead
- Artifact volume analysis
- Redundancy assessment
- Lean evaluation

## 4. Platform and Ecosystem

### 4.1 18+ Platform Strategy
- Breadth vs depth analysis
- Platform quality assessment
- Market coverage implications

### 4.2 npm Distribution Model
- Adoption metrics
- User experience
- Comparison with RaiSE

### 4.3 Extension Ecosystem
- Community health
- Module availability
- Growth trajectory

## 5. Quality and Governance

### 5.1 Validation Model Assessment
- Coverage and depth
- Reliability analysis
- Governance theater risk

### 5.2 Failure Mode Analysis
- Known failure modes
- Recovery mechanisms
- Robustness comparison with RaiSE

## 6. Community and Adoption

### 6.1 Traction Metrics
- Quantitative data
- Growth trajectory
- Community health

### 6.2 Market Positioning
- BMAD's positioning strategy
- Audience overlap with RaiSE
- Competitive dynamics

## 7. Head-to-Head: BMAD vs RaiSE

### 7.1 BMAD Advantages (Honest Assessment)
- [Ranked list with evidence]

### 7.2 RaiSE Advantages (Evidence-Based)
- [Ranked list with evidence]

### 7.3 Neutral / Context-Dependent
- [Features where neither clearly wins]

## 8. Strategic Recommendations

### 8.1 Adopt from BMAD
- [Features/patterns to take with rationale]

### 8.2 Adapt from BMAD
- [Features/patterns to transform with RaiSE spin]

### 8.3 Reject from BMAD
- [Features/patterns to explicitly not adopt, with rationale]

### 8.4 Competitive Response
- Positioning recommendation
- Feature prioritization impact
- Messaging strategy

## References
[Categorized by source type]
```

---

### Deliverable 2: Feature-by-Feature Comparison Matrix

**Format**: Markdown table + detailed notes (~3-4K words)

**Structure**:
```markdown
# BMAD vs RaiSE: Feature Comparison Matrix

## Summary Matrix

| Capability | BMAD | RaiSE | Verdict | Notes |
|-----------|------|-------|---------|-------|
| Agent Model | Named personas (9) | Functional agents | ? | ... |
| Workflow Engine | LLM-as-runtime | Code+Prompts | ? | ... |
| Validation | Adversarial + Checklists | Gates + Jidoka | ? | ... |
| Platform Support | 18+ IDEs | Focused set | BMAD | ... |
| Brownfield | Limited | First-class | RaiSE | ... |
| Governance | Prompt-based | Code-based | RaiSE | ... |
| Lean Principles | None explicit | Core foundation | RaiSE | ... |
| Quick Path | Quick Flow | ? | ? | ... |
| Multi-Agent | Party Mode | None | BMAD | ... |
| Documentation | Heavy | Lean target | ? | ... |
| Extension | Modules + Builder | raise-kit | ? | ... |
| Installation | npx install | Script injection | ? | ... |
| Terminology | None | Canonical Glosario | RaiSE | ... |
| Decision Records | None explicit | ADR system | RaiSE | ... |
| Test Knowledge | TestArch (30+ docs) | None | BMAD | ... |
| Skill Adaptation | 3 levels | None | BMAD | ... |
| YOLO Mode | Yes | None | ? | ... |
| Sprint Tracking | YAML-based | None | BMAD | ... |
| Sharding | shard-doc.xml | None | BMAD | ... |
| Methodology Base | Agile/Scrum labels | Lean/Heutagogy | RaiSE | ... |

## Detailed Notes per Capability
[Per-row analysis with evidence and recommendations]
```

---

### Deliverable 3: Strategic Response Recommendations

**Format**: Markdown document (~3-4K words)

**Structure**:
```markdown
# RaiSE Strategic Response to BMAD Method

## Positioning Recommendation
- Recommended posture: [A/B/C/D from Q8.2]
- Rationale
- Messaging framework

## Immediate Actions (Next 30 Days)
1. [Action with rationale]
2. [Action with rationale]
3. [Action with rationale]

## Medium-Term Response (3-6 Months)
1. [Feature/initiative with rationale]
2. [Feature/initiative with rationale]
3. [Feature/initiative with rationale]

## Long-Term Strategy (6-12 Months)
1. [Strategic direction with rationale]
2. [Strategic direction with rationale]

## Features to Prioritize (Informed by BMAD Analysis)
| Priority | Feature | BMAD Threat It Addresses | Effort | Impact |
|----------|---------|--------------------------|--------|--------|
| P0 | ... | ... | ... | ... |
| P1 | ... | ... | ... | ... |
| P2 | ... | ... | ... | ... |

## Features to De-Prioritize
| Feature | Why De-Prioritize | BMAD Comparison |
|---------|-------------------|-----------------|
| ... | ... | ... |

## Messaging Against BMAD
- For BMAD users considering RaiSE: [Message]
- For new users choosing between BMAD and RaiSE: [Message]
- For RaiSE users aware of BMAD: [Message]

## Risks of Inaction
- [Risk 1 with probability and impact]
- [Risk 2 with probability and impact]

## Open Questions for Further Research
- [Question 1]
- [Question 2]
```

---

## Success Criteria

This research will be successful if it produces:

1. **Accurate Competitive Map**:
   - [ ] BMAD architecture fully documented and understood
   - [ ] At least 15 distinct BMAD features/patterns analyzed
   - [ ] Strengths and weaknesses evidence-based (not opinion-based)
   - [ ] At least 5 head-to-head comparisons with clear verdicts

2. **Honest Threat Assessment**:
   - [ ] At least 3 genuine competitive threats identified
   - [ ] Each threat assessed for severity and urgency
   - [ ] No "RaiSE is better at everything" confirmation bias
   - [ ] BMAD strengths acknowledged where real

3. **Actionable Differentiation**:
   - [ ] At least 5 "Adopt" recommendations with implementation guidance
   - [ ] At least 5 "Adapt" recommendations with RaiSE spin
   - [ ] At least 5 "Reject" decisions with clear rationale
   - [ ] Feature prioritization updated based on competitive analysis

4. **Strategic Clarity**:
   - [ ] Clear positioning recommendation (A/B/C/D)
   - [ ] 30-day, 3-month, 6-month action plans
   - [ ] Messaging framework for competitive situations
   - [ ] Open questions identified for further research

5. **Evidence-Based**:
   - [ ] All claims supported by source data
   - [ ] Quantitative data where available (stars, downloads, etc.)
   - [ ] Community sentiment validated (not assumed)
   - [ ] Counterarguments and limitations acknowledged

---

## Timeline

**Week 1**:
- Days 1-2: BMAD GitHub repository deep dive (source code, docs, issues, PRs, discussions)
- Day 3: npm metrics + community channels + social media sentiment
- Day 4: Head-to-head comparison analysis (architecture, agents, workflows, governance)
- Day 5: Initial synthesis and gap identification

**Week 2**:
- Days 1-2: Deep dive on top competitive threats (validate with evidence)
- Day 3: Strategic response formulation
- Day 4: Feature comparison matrix + recommendations
- Day 5: Report writing + deliverables

**Total**: ~8-10 working days for thorough research + synthesis + strategy

---

## Output Location

**Deliverables saved to**:
```
specs/main/research/bmad-competitive-analysis/
├── competitive-analysis.md               # Deliverable 1 (~6-8K words)
├── feature-comparison-matrix.md          # Deliverable 2 (~3-4K words)
├── strategic-response.md                 # Deliverable 3 (~3-4K words)
└── sources/
    ├── github-analysis/                  # Repo metrics, issues, PRs
    ├── community-signals/                # Social media, discussions
    ├── architecture-notes/               # Technical deep-dive notes
    └── head-to-head/                     # Direct comparison data
```

---

## Meta: How to Use This Prompt

### For AI Research Agent

If executing this research with an AI agent:

1. **Read this prompt completely**
2. **Start with BMAD GitHub repo** (README, source code, docs, issues, discussions)
3. **Map BMAD's architecture systematically** (don't skip anything in `src/`)
4. **Collect quantitative data** (stars, downloads, contributors, issue counts)
5. **Analyze community sentiment** (social media, blog posts, discussions)
6. **Build comparison matrix** feature by feature against RaiSE
7. **Apply RaiSE Lean Audit** (Muda, Mura, Muri) to every BMAD feature
8. **Be brutally honest** about BMAD advantages over RaiSE
9. **Generate strategic recommendations** grounded in evidence
10. **Validate** against success criteria before finalizing

### For Human Researcher

If executing manually:

1. **Allocate 2-3 hour blocks** for focused research
2. **Start with BMAD's `src/` directory** -- read agent YAML, workflow steps, tasks
3. **Install BMAD** (`npx bmad-method install`) and try it firsthand
4. **Run at least 2 workflows** to experience the UX
5. **Compare side-by-side** with RaiSE equivalent commands
6. **Document your experience** -- friction points, surprises, impressions
7. **Check community channels** (Discord, Reddit, etc.)
8. **Talk to BMAD users** if possible
9. **Maintain intellectual honesty** -- resist confirmation bias
10. **Focus on what RaiSE can learn** as much as what RaiSE does better

---

## Related RaiSE Context

**Current state**: RaiSE has already analyzed spec-kit and identified differentiation strategy

**Key Documents**:
- **Spec-kit critique taxonomy**: `specs/main/research/speckit-critiques/critique-taxonomy.md`
- **Differentiation strategy**: `specs/main/research/speckit-critiques/differentiation-strategy.md`
- **MCP vs CLI+Skills analysis**: `specs/main/research/mcp-vs-cli-skills/`
- **Rules vs Skills architecture**: `specs/main/research/rules-vs-skills-architecture/`
- **Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`
- **Glosario**: `docs/framework/v2.1/model/20-glossary-v2.1.md`

**RaiSE Principles to Apply**:
- **§2. Governance as Code**: Evaluate BMAD's prompt-based governance vs. RaiSE's code-based governance
- **§3. Evidence-Based**: Every competitive assessment must be backed by evidence
- **§7. Lean (Jidoka + Muda/Mura/Muri)**: Apply Lean lens to BMAD's processes
- **§8. Observable Workflow**: Compare observability and traceability models

**Key Questions for RaiSE**:
- Is BMAD solving the same problem as RaiSE? Or a different problem?
- Where has BMAD already solved problems RaiSE is still working on?
- Where has BMAD made design decisions that RaiSE should learn from?
- Where has BMAD made mistakes that RaiSE can avoid?
- What does BMAD's existence and approach tell us about the market?

---

**Research Start Date**: [YYYY-MM-DD]
**Research End Date**: [YYYY-MM-DD]
**Researcher**: [Name/Agent ID]
**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed

---

*This research prompt is part of the RaiSE Framework evolution (Feature 012: Raise Commands Research), aimed at understanding the competitive landscape and identifying both threats and opportunities from the BMAD Method for RaiSE's strategic positioning in the agentic development framework market.*
