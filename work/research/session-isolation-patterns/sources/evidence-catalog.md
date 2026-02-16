# Evidence Catalog: Session Isolation Patterns

> RES-SESSION-ISO-001 | 2026-02-15
> Research Question: How do multi-agent frameworks identify and track concurrent session instances?

---

## Very High Evidence

### S1: Claude Code Official Documentation — Agent Teams
**Source**: [Agent Teams - Claude Code Docs](https://code.claude.com/docs/en/agent-teams)
**Type**: Primary (Official Documentation)
**Evidence Level**: Very High
**Key Finding**: Claude Code uses `CLAUDE_CODE_TASK_LIST_ID` env var as session isolation mechanism. Multiple instances operate on same task list via shared disk location (`~/.claude/tasks/auth-system-v2/`).
**Relevance**: Direct parallel to our `RAI_SESSION_ID` env var approach. Validates environment variable as platform-agnostic isolation mechanism.

### S2: Session Management Commands
**Source**: [Session Management Commands | Claude Code Ultimate Guide](https://deepwiki.com/FlorianBruniaux/claude-code-ultimate-guide/13.1-session-management-commands)
**Type**: Secondary (Expert Guide)
**Evidence Level**: Very High
**Key Finding**: Tasks API stores data on disk for persistence. Updates visible immediately to other sessions through filesystem.
**Relevance**: Confirms our per-session directory approach. Filesystem is sufficient for concurrency — no database needed.

### S3: SWE-MiniSandbox Architecture
**Source**: [SWE-MiniSandbox: Container-Free RL for Building SE Agents](https://arxiv.org/html/2602.11210)
**Type**: Primary (Academic Paper)
**Evidence Level**: Very High
**Key Finding**: Creates isolated terminal session per instance using mount namespaces + chroot. Each task gets private directory enforced by per-instance namespaces.
**Relevance**: Validates directory-per-session pattern at scale (35k evaluations/day). Our approach is simpler (no namespaces) but same core pattern.

---

## High Evidence

### S4: OpenCode Session Management
**Source**: [Session Management | opencode-ai/opencode](https://deepwiki.com/opencode-ai/opencode/5.2-session-management)
**Type**: Secondary (Project Documentation)
**Evidence Level**: High
**Key Finding**: Maintains session metadata (conversation state, cost, token usage). Each session has own message history and tracking.
**Relevance**: Confirms our `state.yaml` + `signals.jsonl` per-session pattern.

### S5: cc-top — PID Correlation for Claude Code
**Source**: [GitHub - nixlim/cc-top](https://github.com/nixlim/cc-top)
**Type**: Secondary (Community Tool)
**Evidence Level**: High
**Key Finding**: Maps OTLP sessions to OS processes via port fingerprinting. PID detection for monitoring.
**Relevance**: Validates that PID-based detection exists but requires external tooling. Our token protocol is simpler.

### S6: Managing Multiple Claude Code Sessions (Worktrees)
**Source**: [Managing Multiple Sessions Without Worktrees](https://blog.gitbutler.com/parallel-claude-code)
**Type**: Secondary (Engineering Blog)
**Evidence Level**: High
**Key Finding**: Git worktrees provide isolation via separate directories. Each worktree has different branch checked out.
**Relevance**: Directory isolation pattern. Our session directories mirror this at session level, not branch level.

### S7: tmux Session Lifecycle — Orphan Detection
**Source**: [Session and Window Lifecycle Commands | tmux](https://deepwiki.com/tmux/tmux/3.4-session-and-window-lifecycle-commands)
**Type**: Secondary (Project Documentation)
**Evidence Level**: High
**Key Finding**: Reference counting for safe resource management. Deferred cleanup using event timers. Notification system for lifecycle events.
**Relevance**: Pattern for our orphan detection. Reference counting = `active_sessions` list. Deferred cleanup = stale threshold check.

### S8: Defense-in-Depth Orphan Cleanup
**Source**: [fix(daemon): Add orphan process cleanup | gastown](https://github.com/steveyegge/gastown/issues/29)
**Type**: Secondary (Issue Discussion)
**Evidence Level**: High
**Key Finding**: Three-layer cleanup: (1) kill by PGID, (2) kill by TTY, (3) periodic orphan scan. Orphans occur when parent dies without cleanup.
**Relevance**: Validates our stale session detection (>24h). Need explicit cleanup, not just timeout.

### S9: Tmux Stale Session Cleanup
**Source**: [Tmux Cleanup Session Script](https://linkarzu.com/posts/terminals/tmux-cleanup/)
**Type**: Secondary (Blog Tutorial)
**Evidence Level**: High
**Key Finding**: Auto-kill sessions by comparing last activity timestamp against threshold.
**Relevance**: Direct pattern for our `is_stale()` check. Time-based detection is sufficient.

---

## Medium Evidence

### S10: Claude Squad — Multi-Instance Manager
**Source**: [GitHub - smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad)
**Type**: Tertiary (Community Tool)
**Evidence Level**: Medium
**Key Finding**: Terminal app managing multiple Claude Code instances in separate workspaces.
**Relevance**: Shows market demand for multi-session coordination. Our CLI approach enables this without external tool.

### S11: How to Run Multiple Claude Instances
**Source**: [Run Multiple Claude Instances in VS Code](https://www.arsturn.com/blog/how-to-run-multiple-claude-instances-in-vs-code-a-developers-guide)
**Type**: Tertiary (Tutorial)
**Evidence Level**: Medium
**Key Finding**: Multiple approaches: tmux, git worktrees, separate VS Code windows.
**Relevance**: Confirms workaround complexity. Our token protocol makes this native.

### S12: tmux Session Files Vulnerability
**Source**: [tmux session files vulnerable to systemd-tmpfiles](https://github.com/tmux/tmux/issues/4640)
**Type**: Secondary (Issue Discussion)
**Evidence Level**: Medium
**Key Finding**: /tmp/tmux-* directories removed after 10 days. flock prevents cleanup but not implemented.
**Relevance**: Risk for our session directories. Consider migration to XDG paths or periodic archival.

---

## Low Evidence

### S13: Orchestrate Teams of Claude Code Sessions
**Source**: [Orchestrate teams - Claude Code Docs](https://code.claude.com/docs/en/agent-teams)
**Type**: Primary (Official Docs)
**Evidence Level**: Low (Experimental Feature)
**Key Finding**: Agent teams are experimental, disabled by default. One lead + teammates.
**Relevance**: Future scope (RAISE-127 pt2). Coordination layer above isolation.

---

## Contrarian Evidence

### C1: Aider — No Explicit Session Isolation
**Search**: "Aider multiple terminal sessions concurrent state management"
**Finding**: No explicit session isolation mechanism found. Full chat history in `.aider.chat.history.md` — single file.
**Implication**: Aider doesn't support concurrent sessions on same project. Our token protocol addresses a gap Aider hasn't solved.

---

**Total Sources**: 13 (3 Very High, 6 High, 3 Medium, 1 Low)
**Confidence**: HIGH for RQ1 (session identity), HIGH for RQ3 (lifecycle), VALIDATED for RQ2 (covered in prior research)
