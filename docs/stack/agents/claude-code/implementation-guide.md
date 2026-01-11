# Claude MAX $100 Implementation Guide: Step-by-Step
## Complete Walkthrough for Ubuntu 24.04 + Kilocode + Claude Code + Antigravity

---

## Table of Contents
1. **Phase 1: Environment Setup** (2-3 hours)
2. **Phase 2: Cost Monitoring Foundation** (30 minutes)
3. **Phase 3: CLAUDE.md Creation** (1-2 hours)
4. **Phase 4: Prompt Caching Implementation** (1 hour)
5. **Phase 5: MCP Setup** (45 minutes - optional but recommended)
6. **Phase 6: Multi-Agent Orchestration** (1.5 hours)
7. **Phase 7: Testing & Baseline Establishment** (2 hours)

**Total time: 8.5-10 hours spread across 1-2 weeks**

---

## PHASE 1: Environment Setup (Ubuntu 24.04)

### Step 1.1: System Update
**Time: 10 minutes**

```bash
# Open terminal and update system
sudo apt update
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl git ripgrep build-essential

# Verify current Node.js (if any)
node --version
npm --version
```

**Expected output**: Shows current versions (may be old or not installed)

---

### Step 1.2: Install Node.js 20 LTS
**Time: 15 minutes**

**Option A: Using NodeSource (Recommended)**
```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x
```

**Option B: Using Snap**
```bash
sudo snap install node --classic
```

**Verify installation**:
```bash
node --version
npm --version
which npm
```

**Expected**: Both commands show versions, npm path shows `/usr/bin/npm` or `/snap/bin/npm`

---

### Step 1.3: Configure npm for Global Packages
**Time: 10 minutes**

This prevents permission issues when installing global packages.

```bash
# Create directory for global packages
mkdir -p ~/.npm-global

# Configure npm to use this directory
npm config set prefix '~/.npm-global'

# Add to PATH
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc

# Verify configuration
echo $PATH  # Should show ~/.npm-global/bin first
npm config get prefix  # Should show /home/yourusername/.npm-global
```

---

### Step 1.4: Install Claude Code
**Time: 10 minutes**

**CRITICAL**: Do NOT use sudo - this causes permission issues.

```bash
# Verify npm can install globally without sudo
npm install -g --dry-run @anthropic-ai/claude-code

# If dry-run succeeds, install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version  # Should show version number (e.g., 2.0.72)
claude doctor     # Full diagnostic info
```

**If "command not found":**
- Close terminal completely (not just new tab)
- Reopen terminal
- Try again

**If permission error**:
```bash
# Check npm prefix
npm config get prefix

# If it shows /usr/local, reconfigure it
npm config set prefix '~/.npm-global'
source ~/.bashrc

# Then try install again without sudo
npm install -g @anthropic-ai/claude-code
```

---

### Step 1.5: Create Project Directory Structure
**Time: 5 minutes**

```bash
# Create project directory
mkdir -p ~/Projects/claude-workspace
cd ~/Projects/claude-workspace

# Create subdirectories for organization
mkdir -p .claude/commands
mkdir -p .claude/agents
mkdir -p .claude/cache
mkdir -p src tests docs

# Initialize git repository
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create .gitignore
cat > .gitignore << 'EOF'
# Claude Code
.claude/cache/*
!.claude/cache/.gitkeep
node_modules/
.env
.env.local
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

touch .claude/cache/.gitkeep
git add .
git commit -m "Initial project setup"
```

---

## PHASE 2: Cost Monitoring Foundation

### Step 2.1: Access Anthropic Console
**Time: 5 minutes**

```bash
# Open in your browser
# https://console.anthropic.com

# If not logged in, authenticate with your Anthropic account
```

**In Anthropic Console:**
1. Click your workspace name (top-left)
2. Verify you're in the correct workspace
3. Note your workspace name for later

---

### Step 2.2: Set Up Billing Alerts
**Time: 15 minutes**

**In Anthropic Console:**
1. Navigate to **Settings** (left sidebar)
2. Click **Billing**
3. Under **Workspace Limits**:
   - **Monthly budget**: Set to $100 (or your actual limit)
   - **Warning threshold**: Set to $75 (75% of budget)
   - Enable **Email alerts**

4. Under **Plans & Billing**:
   - Verify **Claude MAX** is selected ($100/month)
   - Confirm payment method is valid
   - Save any changes

**Create a budget reminder**:
```bash
# Create a weekly reminder script
cat > ~/check-claude-budget.sh << 'EOF'
#!/bin/bash
echo "💰 Claude MAX Budget Check"
echo "Current date: $(date)"
echo "Check Anthropic Console at: https://console.anthropic.com"
echo "Look for: Settings → Billing → Current usage"
EOF

chmod +x ~/check-claude-budget.sh

# Add to crontab (runs every Monday at 9 AM)
(crontab -l 2>/dev/null; echo "0 9 * * 1 /home/$USER/check-claude-budget.sh | mail -s 'Claude Budget Check' your-email@example.com") | crontab -
```

---

### Step 2.3: Set Up CLI Cost Tracking
**Time: 5 minutes**

Create a cost-tracking alias in your bash profile:

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Claude Cost Tracking Aliases
alias claude-cost='echo "Check current session cost with /cost in Claude Code session"'
alias claude-usage='echo "⚠️  Run this IN a Claude Code session: /cost"'

# Function to check CLI
claude_info() {
    echo "📊 Claude Code Information:"
    claude doctor
}
EOF

# Reload shell
source ~/.bashrc

# Test aliases
claude-cost
```

---

## PHASE 3: CLAUDE.md Creation

### Step 3.1: Understand CLAUDE.md Purpose
**Time: 5 minutes**

CLAUDE.md is a special file that:
- Claude Code **automatically loads** at session start
- Provides **persistent context** across conversations
- Acts as **project memory** for coding patterns, standards, and structure
- Gets loaded **from project root and nested directories** as relevant

**File location**: `~/Projects/claude-workspace/CLAUDE.md`

---

### Step 3.2: Create Root CLAUDE.md
**Time: 30 minutes**

Create the file `CLAUDE.md` in your project root:

```bash
cat > ~/Projects/claude-workspace/CLAUDE.md << 'EOF'
# Claude.md - Project Context

## Project Overview
**Name**: [Your Project Name]
**Purpose**: Development project using Claude MAX $100 subscription for cost-optimized development

## Technology Stack
- **Runtime**: Node.js 20 LTS
- **IDE**: VSCode with Claude Code
- **Primary IDE**: Kilocode
- **Planning Tool**: Antigravity (Gemini 3 Pro)
- **OS**: Ubuntu 24.04 LTS

## Project Structure
```
.
├── .claude/                    # Claude Code configuration
│   ├── commands/              # Custom commands
│   ├── agents/                # Multi-agent definitions
│   └── cache/                 # Cached documents
├── src/                       # Source code
├── tests/                     # Test files
├── docs/                      # Documentation
├── CLAUDE.md                  # This file
└── README.md                  # Project readme
```

## Coding Standards

### File Naming
- Components: PascalCase (`UserAuth.ts`)
- Utilities: camelCase (`formatDate.ts`)
- Classes: PascalCase (`DatabaseConnection.ts`)
- Constants: UPPER_SNAKE_CASE (`API_TIMEOUT`)

### Code Style
- Line length: 100 characters max
- Indentation: 2 spaces
- Semicolons: Required
- Quotes: Double quotes for strings
- Comments: JSDoc style for functions

### Imports
Always use specific imports, not `*`:
```
✓ import { formatDate, parseDate } from './utils'
✗ import * as utils from './utils'
```

## Testing Requirements
- Unit tests for all utilities and services
- Integration tests for API endpoints
- Minimum coverage: 80%
- Test command: `npm test`

## Git Workflow
- Branch naming: `feature/name` or `fix/name`
- Commits: Conventional format (`feat:`, `fix:`, `docs:`)
- Merge strategy: Squash commits for clean history
- Protect main branch - PR required

## Cost Optimization Rules
**These rules help stay within $100/month budget:**

1. **Model Selection**:
   - Opus 4.5: Architecture, critical reviews only (5-10% of work)
   - Sonnet 4.5: Main implementation (60-75% of work)
   - Haiku 4.5: Testing, validation, linting (15-25% of work)

2. **Context Management**:
   - Use `/clear` when starting unrelated task
   - Use `/compact` after 50K tokens in conversation
   - Reference specific files with `@file.ts` instead of broad scanning
   - Never copy-paste entire files; ask Claude to read specific sections

3. **Session Practice**:
   - New session per feature (resets 5-hour rolling window)
   - Use phase-based approach: Plan → Implement → Test → Review
   - Each phase gets its own clear task definition

4. **Documentation References**:
   - Keep architecture.md updated (used for context)
   - Keep api-spec.md current (reused across requests)
   - Maintain CHANGELOG.md (reviewed during planning)

## Important Commands

### Claude Code Commands
- `/cost` - Check current session cost
- `/clear` - Reset conversation context
- `/compact` - Compress conversation history
- `/plan` - Start planning phase
- `/mcp` - View MCP server connections

### Bash Aliases (from .bashrc)
```bash
claude-cost        # Reminder to check /cost in session
claude-usage       # Show current usage info
claude-plan        # Use Opus for planning (from shell)
claude-build       # Use Sonnet for implementation
claude-test        # Use Haiku for testing
```

### Common Workflows
```bash
# Start new feature development
cd ~/Projects/claude-workspace
claude

# Within Claude session:
# 1. Use Antigravity to research and plan (do this first!)
# 2. Paste roadmap.md from Antigravity into Claude Code
# 3. /plan to get implementation plan
# 4. Implement in phases
# 5. /compact if conversation gets long
# 6. /clear when starting new unrelated task
```

## File References
When working on specific features, read these first:
- **For API work**: Read `docs/api-spec.md`
- **For testing**: Read `docs/testing-guide.md`
- **For architecture**: Read `docs/architecture.md`

**Ask Claude Code**: "Please read ./docs/architecture.md and ./docs/api-spec.md before starting"

## Known Issues & Workarounds
[Add specific to your project as discovered]

## Recent Context (Updated Weekly)
- Last updated: [Current date]
- Current focus: [What you're working on]
- Budget status: [X%] of $100 monthly budget used
- Next planned features: [List]

EOF

# Verify file was created
cat ~/Projects/claude-workspace/CLAUDE.md | head -20
```

**Expected**: File created with ~150 lines of context

---

### Step 3.3: Create Architecture Documentation
**Time: 30 minutes**

This will be cached and reused:

```bash
cat > ~/Projects/claude-workspace/docs/architecture.md << 'EOF'
# Architecture Document

## System Design
[Describe your project architecture - basic structure for now]

### High-Level Components
1. **Frontend/UI Layer**: [Your UI framework]
2. **API Layer**: [Your API structure]
3. **Service Layer**: [Business logic]
4. **Data Layer**: [Database/storage]

## Technology Decisions
- **Node.js 20**: Latest LTS, good for development velocity
- **VS Code + Claude Code**: Seamless AI integration
- **Git**: Version control and team collaboration

## Scalability Considerations
[Will add as project evolves]

## Performance Guidelines
- API response time: <500ms for most endpoints
- Database query timeout: 5 seconds
- Cache TTL: 5 minutes default

## Security Considerations
- Validate all inputs
- Use environment variables for secrets
- Follow OWASP guidelines
- Regular security audits

EOF

echo "✅ Architecture file created"
```

---

### Step 3.4: Test CLAUDE.md Loading
**Time: 10 minutes**

```bash
# Start Claude Code in your project
cd ~/Projects/claude-workspace
claude

# In Claude Code session, ask:
# "What's in my CLAUDE.md file? Read it first."

# Claude should respond with your CLAUDE.md content
# This verifies it's loading correctly
```

---

## PHASE 4: Prompt Caching Implementation

### Step 4.1: Understand Caching Strategy
**Time: 5 minutes**

You'll cache these documents to reuse them across multiple requests:

| Document | Size | Cache Hits Expected | Savings |
|----------|------|-------------------|---------|
| CLAUDE.md | 3K | 50+ per month | 90% on cached portion |
| architecture.md | 4K | 30+ per month | 90% on cached portion |
| api-spec.md | 5K | 25+ per month | 90% on cached portion |
| system-prompts.md | 2K | 100+ per month | 90% on cached portion |

---

### Step 4.2: Create Cacheable System Prompts
**Time: 15 minutes**

```bash
cat > ~/Projects/claude-workspace/.claude/system-prompts.md << 'EOF'
# System Prompts for Caching

## Your Role
You are an expert software engineer helping develop a project using Claude MAX ($100/month budget).
Your goal is to deliver high-quality code efficiently, minimizing token costs while maintaining excellence.

## Code Quality Standards
- Write clean, readable code following project conventions
- Include comprehensive error handling
- Write unit tests for all business logic
- Document complex algorithms with comments
- Follow DRY (Don't Repeat Yourself) principle

## Communication Style
- Be concise but thorough
- Explain trade-offs clearly
- Ask clarifying questions when requirements are ambiguous
- Provide cost estimates for complex changes

## Cost-Conscious Development
- Prefer simpler solutions when equally effective
- Batch related changes together (reduces round trips)
- Suggest prompt caching opportunities when patterns repeat
- Alert on context window usage to prevent waste

## Token Management
- Use specific file references (@file.ts) instead of broad scans
- Ask to read docs once, then reference them by name
- Start new sessions for unrelated work
- Use /compact when conversation exceeds 50K tokens

EOF

echo "✅ System prompts created (2K tokens, will be cached)"
```

---

### Step 4.3: Create API Specification (Cacheable)
**Time: 30 minutes**

```bash
cat > ~/Projects/claude-workspace/docs/api-spec.md << 'EOF'
# API Specification

## Overview
Your project API endpoints and their specifications.

## Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh token

### Users
- `GET /users/:id` - Get user by ID
- `PUT /users/:id` - Update user
- `DELETE /users/:id` - Delete user

### Data
- `GET /data` - List all data
- `POST /data` - Create new data
- `GET /data/:id` - Get specific data
- `PUT /data/:id` - Update data
- `DELETE /data/:id` - Delete data

## Error Handling
All errors return JSON format:
```json
{
  "error": "Error code",
  "message": "Human-readable message",
  "details": {}
}
```

## Rate Limiting
- 100 requests per minute per API key
- 10,000 requests per day per API key

## Authentication
Use Bearer tokens in Authorization header:
```
Authorization: Bearer <token>
```

EOF

echo "✅ API spec created (4K tokens, will be cached)"
```

---

### Step 4.4: Implement Caching in Sessions
**Time: 10 minutes**

**How to use caching in Claude Code sessions:**

First request (creates cache):
```
I'll be working on [your feature] and will reference these documents multiple times.
Please read and cache:
1. ./.claude/system-prompts.md
2. ./docs/architecture.md
3. ./docs/api-spec.md

Then start with: [your actual request]
```

Second and subsequent requests (uses cache):
```
Reference system-prompts.md, architecture.md, and api-spec.md from cache.
[Your new request]
```

Claude will automatically use cached versions after first request (90% cost savings on those documents).

---

## PHASE 5: MCP Setup (Optional but Recommended)

### Step 5.1: Understand MCP Servers
**Time: 5 minutes**

MCP (Model Context Protocol) servers give Claude Code access to external tools:
- **File operations**: Browse, read, modify files
- **Git operations**: Commit, branch, merge
- **Web search**: Research capability
- **Database access**: Query your database
- **Custom tools**: Your own integrations

---

### Step 5.2: Add Essential MCP Servers
**Time: 25 minutes**

```bash
# Navigate to project
cd ~/Projects/claude-workspace

# Add filesystem MCP (local file access)
claude mcp add --transport stdio filesystem \
  npx -y @modelcontextprotocol/server-filesystem /home/$USER/Projects/claude-workspace

# Add git MCP (version control)
claude mcp add --transport stdio git \
  npx -y @modelcontextprotocol/server-git /home/$USER/Projects/claude-workspace

# Add web search MCP (research)
claude mcp add --transport http web-search \
  https://mcp.example.com/web-search

# Verify MCP servers added
cat ~/.claude.json | grep mcpServers

# IMPORTANT: Restart Claude Code to load new MCP servers
# Exit any running Claude Code session (Ctrl+C)
# Then start fresh: claude
```

**In Claude Code, verify MCP:**
```
/mcp
```

Should show your configured servers with checkmarks.

---

### Step 5.3: Common MCP Setup Issues
**Time: 10 minutes**

**Issue**: "Command not found" for MCP
```bash
# Solution: Ensure npx is installed
npm install -g npx

# Then try MCP command again
claude mcp add --transport stdio filesystem \
  npx -y @modelcontextprotocol/server-filesystem /your/path
```

**Issue**: MCP not loading after restart
```bash
# Solution: Verify configuration
cat ~/.claude.json  # Check for errors
claude doctor       # Full diagnostics

# Clear and restart
pkill -f claude
sleep 2
claude
/mcp  # Should show servers now
```

---

## PHASE 6: Multi-Agent Orchestration

### Step 6.1: Understanding the 2-Agent Pattern
**Time: 10 minutes**

For your $100 budget, use the simplest effective pattern:

**Agent 1: Antigravity (Gemini 3 Pro)**
- Role: Research, planning, documentation discovery
- Cost: FREE
- Output: roadmap.md, research.md, task.md

**Agent 2: Claude Code (Claude Sonnet/Opus)**
- Role: Implementation, code generation, testing
- Cost: ~$3/MTok
- Input: roadmap.md from Antigravity

---

### Step 6.2: Create Agent Handoff Template
**Time: 15 minutes**

```bash
cat > ~/Projects/claude-workspace/.claude/agent-handoff-template.md << 'EOF'
# Multi-Agent Handoff Template

## Agent 1: Antigravity (Planning Phase)
**Time**: 1-2 hours
**Cost**: FREE
**Task**: Research and planning

### Instructions for Antigravity:
1. Research [feature requirement]
2. Explore existing patterns in [domain]
3. List recommended libraries/approaches
4. Create implementation roadmap
5. Identify potential risks
6. Output: roadmap.md with recommendations

### Output Template:
```
# Feature Roadmap

## Requirements Analysis
- Requirement 1: [Description]
- Requirement 2: [Description]

## Recommended Approach
- Pattern: [Name]
- Libraries: [List]
- Complexity: [Low/Medium/High]

## Implementation Steps
1. Step 1: [Deliverable]
2. Step 2: [Deliverable]
3. Step 3: [Deliverable]

## Potential Risks
- Risk 1: [Mitigation]
- Risk 2: [Mitigation]

## Files to Create/Modify
- file1.ts
- file2.ts
```

---

## Agent 2: Claude Code (Implementation Phase)
**Time**: 2-4 hours
**Cost**: $1.50-3.00
**Task**: Implementation from roadmap

### Instructions for Claude Code:
1. Read roadmap.md from Antigravity
2. Read ./docs/architecture.md (cached)
3. Implement following phase approach:
   - Phase 1: Setup/scaffolding (30 min)
   - Phase 2: Core implementation (2-3 hours)
   - Phase 3: Testing (1 hour)

### Expected Output:
- Implemented features per roadmap
- Unit tests (minimum 80% coverage)
- Integration tests
- Documentation updates

EOF

echo "✅ Handoff template created"
```

---

### Step 6.3: Set Up Multi-Agent Workflow
**Time: 30 minutes**

**Create the coordination document:**

```bash
cat > ~/Projects/claude-workspace/.claude/MULTI_AGENT_PLAN.md << 'EOF'
# Multi-Agent Coordination Plan

## Active Features

### Feature 1: [Name]
- **Status**: Planning
- **Agent**: Antigravity (Phase 1)
- **Deadline**: [Date]
- **Roadmap**: Not yet created
- **Progress**: 0%

### Feature 2: [Name]
- **Status**: Waiting
- **Agent**: [TBD]
- **Deadline**: [Date]
- **Progress**: 0%

## Agent Schedule

### This Week
- **Mon-Tue**: Antigravity plans features 1-3 (FREE)
- **Tue-Fri**: Claude Code implements feature 1 (PAID)
- **Fri**: Antigravity plans next week's features (FREE)

### Next Week
- **Mon-Thu**: Claude Code implements features 2-3 (PAID)
- **Thu-Fri**: Review and optimization

## Budget Tracking
- **Week 1 Budget**: $25
- **Week 1 Spent**: $0
- **Month Budget Remaining**: $100

## Communication Log
- [Date]: Initialized multi-agent workflow

EOF

echo "✅ Agent coordination plan created"
```

---

### Step 6.4: Start Your First Multi-Agent Task
**Time**: 30 minutes setup, then actual work

**Step 1: Open Antigravity**
```
Go to: https://antigravity.google/
Start new session
```

**Step 2: Give Antigravity research task**
```
Task: "Research [your first feature requirement]

Please:
1. Explain what this feature should do
2. List similar features in existing projects
3. Recommend libraries or patterns
4. Outline implementation steps
5. Identify any complexity points

Format your response as a roadmap ready for Claude Code"
```

**Step 3: Copy Antigravity output**
```
- Copy the roadmap Gemini generates
- Paste into: .claude/feature-roadmap.md
- Commit to git: git add . && git commit -m "feat: add roadmap for [feature]"
```

**Step 4: Open Claude Code**
```bash
cd ~/Projects/claude-workspace
claude
```

**Step 5: Give Claude Code the roadmap**
```
# In Claude Code:
Please read ./docs/architecture.md and ./.claude/feature-roadmap.md

Then implement [feature] following:
1. Phase 1 (30 min): Setup scaffolding
2. Phase 2 (2-3 hours): Core implementation
3. Phase 3 (1 hour): Testing

Start with Phase 1. Use Sonnet model (not Opus).
```

**Expected result**:
- ~30 minutes: Antigravity creates free roadmap
- ~3-4 hours: Claude Code implements from roadmap
- **Total cost**: $1.50-2.50 per feature

---

## PHASE 7: Testing & Baseline Establishment

### Step 7.1: Measure First Feature Cost
**Time**: During first feature (already included above)

```bash
# At START of feature work (after first Claude Code command):
# Record initial state
echo "=== Feature 1 Cost Baseline ===" > ~/cost-baseline.txt
date >> ~/cost-baseline.txt
echo "Starting session" >> ~/cost-baseline.txt

# During feature work, in Claude Code:
/cost

# Record the output

# After feature complete:
/cost

# Record final output
echo "Feature 1 complete" >> ~/cost-baseline.txt

# Calculate cost difference
echo "Cost for feature 1: [output_tokens * price]" >> ~/cost-baseline.txt
```

---

### Step 7.2: Create Monthly Tracking Sheet
**Time**: 15 minutes

```bash
cat > ~/Projects/claude-workspace/MONTHLY_TRACKING.md << 'EOF'
# Monthly Cost Tracking - January 2026

## Features Completed

| Feature | Date | Planning Cost | Implementation Cost | Testing Cost | Review Cost | Total | Model Usage |
|---------|------|---------------|-------------------|--------------|-------------|-------|-------------|
| Feature 1 | Jan 11 | FREE (Antigravity) | $X | $Y | $Z | $TOTAL | Opus/Sonnet/Haiku |
| Feature 2 | Jan 18 | FREE | $ | $ | $ | $ | |

## Weekly Summary

### Week 1 (Jan 6-12)
- **Planned**: 2 features
- **Completed**: 1 feature
- **Cost**: $[amount]
- **Budget remaining**: $[amount]
- **Status**: ✅ On track / ⚠️ Over / ✓ Under

### Week 2 (Jan 13-19)
- **Planned**: 2 features
- **Completed**: 0 features
- **Cost**: $0
- **Budget remaining**: $[amount]
- **Status**: Pending

## Optimization Notes
- Caching effectiveness: [percentage]
- Most expensive feature: [Feature name] at $X
- Cheapest feature: [Feature name] at $X
- Model distribution: Opus: 10%, Sonnet: 70%, Haiku: 20%

## Lessons Learned
[Will add as month progresses]

EOF

echo "✅ Tracking sheet created"
```

---

### Step 7.3: Establish Team Practices
**Time**: 15 minutes

Create a checklist you'll follow for every feature:

```bash
cat > ~/Projects/claude-workspace/FEATURE_CHECKLIST.md << 'EOF'
# Feature Development Checklist

## Before Starting Feature

- [ ] Research completed in Antigravity (FREE)
- [ ] roadmap.md created and reviewed
- [ ] /cost tracked at start of session
- [ ] Correct model selected (Opus/Sonnet/Haiku)
- [ ] Related docs cached (CLAUDE.md, architecture.md, api-spec.md)

## During Implementation

- [ ] Phase 1: Setup/scaffolding complete
- [ ] Phase 2: Core logic implemented
- [ ] Phase 3: Unit tests written (80%+ coverage)
- [ ] Code reviewed for style compliance
- [ ] /cost checked at 50K token mark
- [ ] /compact used if conversation >75K tokens

## Before Completion

- [ ] All tests passing (`npm test`)
- [ ] No console errors or warnings
- [ ] Code follows CLAUDE.md style guide
- [ ] Final /cost recorded
- [ ] Feature cost logged in MONTHLY_TRACKING.md
- [ ] Git commit with conventional format

## Post-Completion

- [ ] Code review (use Opus, 5-10% of feature cost)
- [ ] Documentation updated
- [ ] MULTI_AGENT_PLAN.md updated
- [ ] Next feature queued with Antigravity

EOF

echo "✅ Feature checklist created"
```

---

### Step 7.4: Complete First Week Setup Verification
**Time**: 15 minutes

```bash
# Verify everything is set up
echo "🔍 Verification Checklist:"

# 1. Check Claude Code
echo -n "✓ Claude Code installed: "
claude --version

# 2. Check CLAUDE.md exists and loads
echo -n "✓ CLAUDE.md exists: "
[ -f CLAUDE.md ] && echo "Yes" || echo "No"

# 3. Check cost monitoring set up
echo "✓ Cost monitoring:"
echo "  - Check Anthropic Console: https://console.anthropic.com"
echo "  - Settings → Billing → Verify alerts at $75"

# 4. Check documentation files
echo -n "✓ docs/architecture.md exists: "
[ -f docs/architecture.md ] && echo "Yes" || echo "No"

echo -n "✓ docs/api-spec.md exists: "
[ -f docs/api-spec.md ] && echo "Yes" || echo "No"

# 5. Check git
echo -n "✓ Git repository initialized: "
[ -d .git ] && echo "Yes" || echo "No"

# 6. Check agent coordination
echo -n "✓ MULTI_AGENT_PLAN.md exists: "
[ -f .claude/MULTI_AGENT_PLAN.md ] && echo "Yes" || echo "No"

echo ""
echo "✅ All setup complete! Ready to start development."
echo ""
echo "Next steps:"
echo "1. Start with Antigravity for feature research"
echo "2. Copy roadmap to .claude/feature-roadmap.md"
echo "3. Open Claude Code: cd ~/Projects/claude-workspace && claude"
echo "4. Begin Phase 1: Setup and scaffolding"
```

---

## QUICK REFERENCE COMMANDS

### Daily Development
```bash
# Start working on a feature
cd ~/Projects/claude-workspace
claude

# Check current session cost (in Claude Code)
/cost

# Reset context (starting new task)
/clear

# Compress conversation (after 50K tokens)
/compact

# View available MCP tools
/mcp
```

### Cost Management
```bash
# Check monthly spending (in browser)
https://console.anthropic.com/billing

# View usage details
claude usage --detailed

# System info
claude doctor
```

### Git Workflow
```bash
# After completing feature
git status
git add .
git commit -m "feat: implement [feature name]"
git push

# View commit history
git log --oneline
```

### Antigravity Workflow
```
1. Go to https://antigravity.google/
2. Ask for research/planning on feature
3. Copy roadmap output
4. Paste into .claude/feature-roadmap.md
5. Commit: git add . && git commit -m "docs: add roadmap for [feature]"
6. Switch to Claude Code with roadmap
```

---

## TROUBLESHOOTING

### "Claude Code command not found"
```bash
# Verify installation
npm list -g @anthropic-ai/claude-code

# Reinstall if needed
npm install -g @anthropic-ai/claude-code

# Close and reopen terminal
exit
# Open new terminal window
claude --version
```

### "Permission denied" installing globally
```bash
# Check npm prefix
npm config get prefix

# If it shows /usr/local, reconfigure
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Try install again (no sudo!)
npm install -g @anthropic-ai/claude-code
```

### Spending too much too fast ($10+/day)
```bash
# Check what's consuming tokens
# In Anthropic Console: https://console.anthropic.com

# Immediate actions:
# 1. Switch to Sonnet instead of Opus for implementation
# 2. Use /compact after every 50K tokens
# 3. Enable prompt caching (reference docs instead of rereading)
# 4. Use /clear for new tasks (avoid long conversations)

# For next week:
# Plan features in Antigravity (FREE) before coding
# Batch related changes together
# Use Haiku for testing/validation
```

### MCP servers not showing up
```bash
# After adding MCP:
# MUST restart Claude Code completely

# Exit session
Ctrl+C

# Start fresh
claude

# Check MCP
/mcp
```

---

## SUCCESS CRITERIA

By end of Week 1, you should have:
- ✅ Claude Code installed and authenticated
- ✅ CLAUDE.md created with project context
- ✅ Cost monitoring alerts configured
- ✅ Prompt caching strategy implemented
- ✅ MCP servers configured (optional but recommended)
- ✅ Multi-agent workflow documented
- ✅ First feature completed and cost tracked
- ✅ Monthly tracking sheet started

By end of Month 1, you should achieve:
- ✅ 8-12 features completed
- ✅ Total spend: $80-100
- ✅ Prompt caching showing 30-40% savings
- ✅ Multi-agent workflow established (Antigravity + Claude Code)
- ✅ Reliable cost predictions for different feature types
- ✅ Team understands cost-optimization patterns

---

**This implementation guide covers everything needed to get your Claude MAX $100 subscription fully optimized and operational within 8-10 hours of setup time.**
