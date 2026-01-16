# Claude MAX $100 Implementation Checklist & Quick Reference

## Week 1: Foundation Setup

### Environment Configuration
- [ ] Install Claude Code latest version: `brew install claude-code` or `curl -fsSL https://install.claude.ai | bash`
- [ ] Verify installation: `claude doctor`
- [ ] Update to latest version: `claude update`
- [ ] Create `.claude` directory structure in project root

### CLAUDE.md Creation
- [ ] Create `.claude/CLAUDE.md` with:
  - [ ] Project architecture overview (1,000-1,500 tokens)
  - [ ] Coding standards and conventions (500 tokens)
  - [ ] File structure and important paths (300 tokens)
  - [ ] Cost optimization notes for team
  - [ ] Common patterns and anti-patterns
- [ ] Test CLAUDE.md is loaded: Start new session and ask Claude about project

### Cost Monitoring Setup
- [ ] Access Anthropic Console: https://console.anthropic.com
- [ ] Verify Claude Code workspace exists (auto-created)
- [ ] Enable billing alerts: Settings → Billing → Workspace Limits
  - [ ] Set warning threshold: $75/month
  - [ ] Set hard limit: $100/month
- [ ] Create billing notification email: Settings → Notifications
- [ ] Add calendar reminders: Check `/cost` weekly on Mondays

### MCP Integration (Choose One Path)

**Option A: Docker MCP Toolkit (Recommended)**
- [ ] Install Docker Desktop
- [ ] Run: `docker mcp client connect claude-code`
- [ ] Verify connection: Start Claude Code and run `/mcp` command
- [ ] Enable servers you need (filesystem, git, web-search, etc.)

**Option B: Manual MCP Configuration**
- [ ] Create `.mcp.json` in project root:
```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/project/path"]
    }
  }
}
```
- [ ] Test MCP integration: `/mcp` command in Claude Code
- [ ] Verify tools appear in completions

### Ubuntu 24.04 Performance Optimization
- [ ] Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Node.js (if using npm MCP servers): `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs`
- [ ] Configure terminal for better UX: Add to `.bashrc`:
```bash
# Claude Code cost tracking
alias claude-cost='claude info | grep -i cost'
alias claude-usage='claude usage'

# Quick session commands
alias claude-plan='claude --model opus'
alias claude-build='claude --model sonnet'
alias claude-test='claude --model haiku'
```

---

## Week 2: Cost Optimization Implementation

### Prompt Caching Setup

**Priority 1: System Prompts (Implement immediately)**
- [ ] Create `.claude/system-prompts.md`:
  - [ ] Role and responsibilities (300 tokens)
  - [ ] Communication style (200 tokens)
  - [ ] Code quality standards (400 tokens)
  - [ ] Security requirements (300 tokens)
  - [ ] Performance guidelines (200 tokens)
  - **Total: ~1,400 tokens (meets minimum for caching)**

**Priority 2: Project Architecture**
- [ ] Create `.claude/architecture.md`:
  - [ ] System design overview (800 tokens)
  - [ ] Component relationships (600 tokens)
  - [ ] Data flow diagrams (400 tokens)
  - [ ] Technology stack reasoning (200 tokens)
  - **Total: ~2,000 tokens**

**Priority 3: API & Database Specs**
- [ ] Create `.claude/api-spec.md`:
  - [ ] API endpoints list (1,000 tokens)
  - [ ] Request/response formats (1,000 tokens)
  - [ ] Authentication details (300 tokens)
  - [ ] Error codes and handling (400 tokens)
  - **Total: ~2,700 tokens**

**Testing Prompt Caching**
- [ ] In first session, ask Claude to read architecture.md (creates cache)
- [ ] Check `/cost` output for `cache_creation_input_tokens`
- [ ] In follow-up session, ask similar question about same doc
- [ ] Verify `cache_read_input_tokens` appears (10x cost savings on cached portion)
- [ ] Document cache hit rate (target: 50-80% on repeated queries)

### Model Tier Strategy Implementation

**Create Model Selection Decision Matrix**
- [ ] For each task type in your project, decide: Opus / Sonnet / Haiku
- [ ] Create `.claude/model-selection.md`:
```
# Model Selection Guide

## Opus 4.5 (5-10% of work, ~$5/MTok)
- Architecture design decisions
- Complex algorithm analysis
- Code review of critical paths
- Security architecture review
- Performance optimization strategy

## Sonnet 4.5 (60-75% of work, ~$3/MTok)
- Feature implementation from specs
- API integration development
- Database schema design
- Test suite development
- Documentation writing

## Haiku 4.5 (15-25% of work, ~$1/MTok)
- Unit test execution
- Linting and formatting
- Simple refactoring
- Documentation formatting
- Configuration updates
```

**Test Model Switching**
- [ ] Try Opus for architecture decision: Observe token consumption
- [ ] Try Sonnet for same question: Compare cost efficiency
- [ ] Try Haiku for simple formatting: Verify appropriateness
- [ ] Document cost savings for future reference

### Phase-Based Workflow Structure

**Create Phase Templates**
- [ ] `.claude/templates/plan-phase.md`:
```
# Planning Phase Template

## Problem Statement
[Single sentence describing what we're building]

## Core Requirements
- Requirement 1
- Requirement 2
- Requirement 3

## Technology Stack
- Backend: [Language/Framework]
- Database: [Type and specifics]
- Testing: [Framework]

## Potential Issues
- Issue 1 and mitigation
- Issue 2 and mitigation

## Implementation Phases
1. Phase 1: [Deliverable]
2. Phase 2: [Deliverable]
3. Phase 3: [Deliverable]
```

- [ ] `.claude/templates/implementation-phase.md`:
```
# Implementation Phase Template

## Phase [N]: [Deliverable Description]

### Objectives
- Objective 1
- Objective 2

### Success Criteria
- Criterion 1 (testable)
- Criterion 2 (testable)

### Implementation Steps
1. Step 1
2. Step 2
3. Step 3

### Files to Create/Modify
- file1.ts
- file2.ts

### Testing Strategy
- Unit tests for [components]
- Integration tests for [flows]
```

**Implement Phase Commands** (optional, advanced)
- [ ] Create bash function for `/plan` command
- [ ] Create bash function for `/implementation` command
- [ ] Create bash function for `/complete-phase` command
- [ ] Add to `.bashrc` or project setup script

---

## Week 3: Multi-Agent Architecture Integration

### Antigravity + Claude Code Handoff

**Establish Research → Implementation Flow**
- [ ] Open Antigravity for new feature
- [ ] Prompt Antigravity: "Research and plan [feature] implementation"
- [ ] Output: roadmap.md with research findings
- [ ] Copy roadmap.md to Claude Code
- [ ] Prompt Claude: "Read roadmap.md and implement following the plan"
- [ ] Measure cost difference:
  - [ ] Total cost (Antigravity + Claude) vs.
  - [ ] Cost if Claude researched + implemented directly
  - [ ] Target: 40-50% savings through division of labor

**Create Handoff Format Documentation**
- [ ] Document roadmap.md standard format for handoffs
- [ ] Document what Antigravity should deliver (research, links, patterns)
- [ ] Document what Claude Code should receive (task.md, implementation.md)
- [ ] Create checklist: "Roadmap ready for Claude Code?"

### Validation Agent Setup

**Create Review Process**
- [ ] After each major phase, schedule review session
- [ ] Use Opus model for validation (strategic, not routine)
- [ ] Create validation checklist:
  - [ ] Architecture follows project standards
  - [ ] No security vulnerabilities
  - [ ] Performance acceptable
  - [ ] Code quality meets standard
  - [ ] Test coverage adequate
- [ ] Document findings in `.claude/validations/[feature].md`
- [ ] Cost tracking: Record validation cost per feature

### Parallel Planning Strategy

**Set Up Next-Feature Planning While Implementing Current Feature**
- [ ] Week workflow:
  - [ ] Monday-Wednesday: Implement Feature A (Claude Code)
  - [ ] Tuesday-Thursday: Plan Feature B (Antigravity, free)
  - [ ] Thursday-Friday: Implement Feature B (Claude Code)
  - [ ] Savings: Eliminate context-switching delays in planning

- [ ] Create monthly features backlog (plan all features in first week with Antigravity)
- [ ] Implementation can then proceed sequentially with no planning delays
- [ ] Measure parallelization savings

---

## Week 4: Optimization & Measurement

### Token Consumption Baseline

**For each feature type completed, record:**
- [ ] Small feature (bug fix, UI update):
  - [ ] Planning time: ____ minutes
  - [ ] Planning tokens: ____ (expected: 50-100K)
  - [ ] Implementation tokens: ____ (expected: 100-300K)
  - [ ] Review tokens: ____ (expected: 30-50K)
  - [ ] Total cost: $____

- [ ] Medium feature (new endpoint, database change):
  - [ ] Planning time: ____ minutes
  - [ ] Planning tokens: ____ (expected: 100-200K)
  - [ ] Implementation tokens: ____ (expected: 400-800K)
  - [ ] Review tokens: ____ (expected: 100-150K)
  - [ ] Total cost: $____

- [ ] Large feature (new service, major refactor):
  - [ ] Planning time: ____ minutes
  - [ ] Planning tokens: ____ (expected: 200-400K)
  - [ ] Implementation tokens: ____ (expected: 1-2M)
  - [ ] Review tokens: ____ (expected: 200-400K)
  - [ ] Total cost: $____

**Create Baseline Documentation**
- [ ] `.claude/baselines.md` with your actual costs
- [ ] Compare to expected costs in guide
- [ ] Identify optimization opportunities

### Caching Effectiveness Measurement

- [ ] Feature 1 (no caching):
  - [ ] Total tokens: ____
  - [ ] Cost: $____

- [ ] Feature 2 (with caching on system prompts + architecture):
  - [ ] Total tokens: ____
  - [ ] Cost: $____
  - [ ] Cost reduction: ___ %

- [ ] Feature 3 (with caching on all documents):
  - [ ] Total tokens: ____
  - [ ] Cost: $____
  - [ ] Cost reduction: ___ %

**Target**: 30-50% cost reduction on Feature 3 vs. Feature 1

### Budget Adherence Tracking

**Create Monthly Tracking**
- [ ] Week 1 spent: $____ / $25 budget
- [ ] Week 2 spent: $____ / $25 budget
- [ ] Week 3 spent: $____ / $25 budget
- [ ] Week 4 spent: $____ / $25 budget
- [ ] **Total spent: $____ / $100 budget**

**Adjust for Following Month**
- [ ] Did you overshoot? Reduce feature complexity or use more Haiku
- [ ] Did you undershoot? Increase feature scope or add testing/docs
- [ ] Target: 85-95% budget utilization (don't leave money unused, don't overspend)

---

## Monthly Recurring Tasks

### Monday
- [ ] Check `/cost` output (should be ~$7-10/week)
- [ ] Review Anthropic Console for spending alerts
- [ ] Plan week's features with Antigravity (free)

### Friday
- [ ] Review `/cost` for week (should total ~$15-25)
- [ ] Document completed features and actual costs
- [ ] Plan next week with Antigravity

### First Day of Month
- [ ] Reset budget tracking spreadsheet
- [ ] Review previous month's cost patterns
- [ ] Plan optimization for current month
- [ ] Adjust feature scope if needed

### End of Month
- [ ] Export Claude Console usage report
- [ ] Calculate actual vs. budgeted costs
- [ ] Document lessons learned
- [ ] Update baselines.md with real metrics
- [ ] Plan optimizations for next month

---

## Quick Command Reference

### Daily Use
```bash
# Check current session cost
/cost

# Reset conversation context
/clear

# Compress long conversations
/compact

# View MCP connections
/mcp

# Check configuration
/config
```

### Weekly Maintenance
```bash
# View historical usage
claude usage

# View detailed usage
claude usage --detailed

# Check version
claude doctor

# Update Claude Code
claude update
```

### Session Management
```bash
# Resume previous session
claude --resume

# Start with specific model
claude --model opus      # Opus 4.5
claude --model sonnet    # Sonnet 4.5 (default)
claude --model haiku     # Haiku 4.5
```

### Monitoring & Alerts
```bash
# On Linux, set daily alert
0 18 * * * "claude usage | grep total" | mail -s "Claude Daily Cost" you@example.com

# Or check interactively every Sunday
watch -n 60 'claude info | grep -i cost'
```

---

## Troubleshooting Quick Fixes

### Problem: Session already used 150K tokens without major output
**Diagnosis**: Inefficient conversation, likely re-scanning same files
**Solution**:
```bash
/compact                              # Compress conversation
# Or start new session
/clear
# Then ask specific question about specific file
@src/core/auth.ts "refactor login"   # Reference specific file
```
**Prevention**: Use file references (@file), be specific in prompts

### Problem: Daily cost >$10
**Diagnosis**: Using Opus too much or inefficient queries
**Solution**:
```bash
# Switch to Sonnet for implementation tasks
claude --model sonnet

# Review recent high-cost operations
claude usage --detailed

# Check what files were referenced (use @file instead of scanning)
```
**Prevention**: Use model selection matrix, implement prompt caching

### Problem: Week cost >$30
**Diagnosis**: Scope creep, too many concurrent tasks
**Solution**:
1. Switch to Haiku for testing and validation
2. Use Antigravity (free) for planning remaining features
3. Pause implementation until cost normalizes
4. Resume next Monday with fresh budget allocation
**Prevention**: Track daily costs, enforce phase-based approach

### Problem: Cache not working (no `cache_read_input_tokens`)
**Diagnosis**: Prompt too short (<1,024 tokens) or content changed
**Solution**:
```bash
# Verify CLAUDE.md is large enough
wc -w ~/.claude/CLAUDE.md    # Should be >1024 tokens
# If not, expand with more detail

# Or check if content changed (invalidates cache)
# Ensure system prompts and architecture docs never change during session
```
**Prevention**: Keep system prompts in separate, immutable file

---

## Success Metrics

### By End of Week 1
- [ ] Claude Code installed and configured
- [ ] CLAUDE.md created and tested
- [ ] Cost monitoring alerts active
- [ ] MCP integration working
- [ ] Can track `/cost` after each session

### By End of Month 1
- [ ] 8-12 features completed
- [ ] Total spend: $80-100
- [ ] Prompt caching baseline established
- [ ] Model tier strategy documented
- [ ] Phase-based workflow running smoothly
- [ ] 20-30% cost savings vs. baseline

### By End of Month 3
- [ ] 15-20 features per month sustainable
- [ ] Multi-agent workflow (Antigravity → Claude → Review) established
- [ ] 50-60% cost savings through optimization
- [ ] Reusable caching infrastructure in place
- [ ] Team documentation complete
- [ ] Predictable $80-100/month spend

### Long-term (6+ months)
- [ ] 20-30 features per month
- [ ] 70-80% cost reduction vs. naive usage
- [ ] Multi-agent system fully automated
- [ ] New features can be planned in parallel with implementation
- [ ] Reusable spec templates
- [ ] Mentoring new team members on cost optimization

---

## Support & Escalation

### Questions on Cost Accounting
- Check Claude Console: https://console.anthropic.com/billing
- Run: `claude usage --detailed`
- Review: `/cost` command output in each session

### Questions on Model Performance
- Test in low-cost exploration (use Haiku)
- Compare output quality vs. cost
- Document findings in `.claude/model-selection.md`

### Need More Documentation
- Official Claude Docs: https://docs.anthropic.com
- Claude Code Docs: https://code.claude.com/docs
- This guide (saved as claude-cost-guide.md)

### Budget Crisis (exceeded $100)
1. Contact Anthropic support: https://console.anthropic.com/support
2. Request temporary limit increase if needed
3. Implement emergency cost controls:
   - Only use Haiku for remainder of month
   - Pause feature development
   - Use only Antigravity (Gemini) for planning
   - Resume after month reset

---

**Document Version**: 1.0
**Last Updated**: January 2026
**For Claude MAX Users**: $100/month plan
**Stack**: Ubuntu 24.04 + Kilocode + Claude Code + Antigravity
