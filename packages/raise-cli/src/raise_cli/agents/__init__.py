"""Built-in agent configuration package.

Contains YAML config files for the 5 Tier-1 built-in agents:
  - claude.yaml     (Claude Code)
  - cursor.yaml     (Cursor 2.4+)
  - windsurf.yaml   (Windsurf)
  - copilot.yaml    (GitHub Copilot — has CopilotPlugin)
  - antigravity.yaml (Antigravity)

Usage:
    from importlib.resources import files
    agents_pkg = files("raise_cli.agents")
    claude_yaml = (agents_pkg / "claude.yaml").read_text(encoding="utf-8")
"""
