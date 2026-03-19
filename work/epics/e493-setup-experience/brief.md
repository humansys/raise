# Epic Brief: E493 — Developer Setup Experience

**Jira:** RAISE-493
**Target:** v2.3.0
**Labels:** dx, onboarding

## Hypothesis

If we provide guided tooling for both new-user and new-machine scenarios,
developers can go from zero to productive in under 15 minutes on any supported OS.

## Problem

Setting up a new machine for RaiSE development requires resolving 8 distinct
problems manually, each blocking the next. No guided path exists for either:

- **New user** — first time, installs from scratch
- **Existing developer, new machine** — has identity/history, needs to port it

Real-world friction points (Linux to macOS, March 2026):

1. asdf/pyenv intercepting pip/pipx
2. pipx requiring `--include-deps` (undocumented)
3. rai-cli vs raise-cli wrapper conflict
4. Developer profile not portable (`~/.rai/developer.yaml`)
5. Claude Code memory not portable (`~/.claude/`)
6. MCP servers buried in `~/.claude.json` with machine-specific paths
7. `.env` tokens not loaded by CLI (only by Claude Code MCP)
8. Three identity layers undocumented

## Success Metrics

- [ ] New user on macOS can install and run `rai --version` following docs alone
- [ ] Existing developer can port identity to new machine with 1-2 commands
- [ ] `rai doctor` detects and guides through missing setup steps
- [ ] `/rai-welcome` detects "returning developer, new machine" scenario
- [ ] `rai backlog` works from terminal without manual env var exports
- [ ] All three identity layers documented and tooling-supported

## Appetite

Medium — 6 stories, mostly CLI + docs. No deep architectural changes.

## Rabbit Holes

- Trying to unify all three identity layers into one (too much coupling)
- Building a full installer/bootstrapper (out of scope — docs + doctor suffice)
- Windows native support (WSL only for now)
