"""Detail Panel widget — branch, pipeline, commits, dirty/behind."""

from __future__ import annotations

from rich.markup import escape
from textual.widgets import Static

from raise_cli.cockpit.tui.services import ExpandedDetail, phase_glyph
from raise_cli.cockpit.tui.theme import (
    MARKUP_ERROR,
    MARKUP_MUTED,
    MARKUP_PAUSED,
    MARKUP_WORKING,
)

_PHASE_COLORS: dict[str, str] = {
    "passed": MARKUP_WORKING,
    "done": MARKUP_WORKING,
    "running": MARKUP_PAUSED,
    "pending": MARKUP_MUTED,
    "skipped": MARKUP_MUTED,
    "failed": MARKUP_ERROR,
    "cancelled": MARKUP_ERROR,
}


class DetailPanel(Static):
    """Detail view for the selected worktree."""

    DEFAULT_CSS = """
    DetailPanel {
        padding: 1 2;
        color: $foreground;
    }
    """

    def __init__(self) -> None:
        super().__init__(classes="section")
        self.border_title = "Detail"
        self._data: dict[str, object] = {}
        self._worktree_id: str = ""
        self._branch: str = ""
        self._expanded_data: ExpandedDetail | None = None

    def set_worktree(
        self,
        worktree_id: str,
        branch: str,
        preview: dict[str, object],
    ) -> None:
        """Update the detail panel with worktree data."""
        self._worktree_id = worktree_id
        self._branch = branch
        self._data = preview
        self.refresh()

    def clear_selection(self) -> None:
        """Clear the detail panel."""
        self._worktree_id = ""
        self._branch = ""
        self._data = {}
        self.refresh()

    def set_expanded(self, data: ExpandedDetail) -> None:
        """Store expanded-view data — render() switches to the full report.

        Additive (RAISE-16714, D-S4.4): split-view fields are left
        untouched, so ``clear_expanded()`` reveals the same content that
        was there before expanding.
        """
        self._expanded_data = data
        self.refresh()

    def clear_expanded(self) -> None:
        """Drop expanded-view data — render() reverts to the split content."""
        self._expanded_data = None
        self.refresh()

    def render(self) -> str:
        """Render detail view — expanded report when set, else the split view."""
        if self._expanded_data is not None:
            return self._render_expanded(self._expanded_data)

        if not self._worktree_id:
            return "Select a session to see details"

        lines: list[str] = [
            f"{self._worktree_id}",
            f"  branch:  {self._branch}",
        ]

        dirty = self._data.get("dirty_count", 0)
        behind = self._data.get("behind_count", 0)
        commits = self._data.get("commits", [])
        path_exists = self._data.get("path_exists", True)

        if not path_exists:
            lines.append("  ✗ path not found")
            return "\n".join(lines)

        lines.append(f"  dirty:   {dirty} file{'s' if dirty != 1 else ''}")
        lines.append(f"  behind:  {behind} commit{'s' if behind != 1 else ''}")

        if isinstance(commits, list) and commits:
            lines.append("")
            lines.append("  recent commits:")
            for c in commits[:3]:
                lines.append(f"    {c}")

        return "\n".join(lines)

    def _render_expanded(self, data: ExpandedDetail) -> str:
        """Full-screen situation report (RAISE-16714, D-S4.4).

        Pipeline track with per-phase glyphs, ≥5 commits, branch/dirty/
        behind status, and the MR link — with truthful placeholders when
        runs/commits/remote are absent.
        """
        wt = escape(data.worktree_id)
        br = escape(data.branch)
        lines: list[str] = [
            f"{wt} · {br}",
            "──────────────────────────────────────",
        ]

        if data.phases:
            lines.append(
                f"Pipeline: {escape(data.pipeline_name)} · {escape(data.issue_id)} · {escape(data.run_status)}"
            )
            track = "   ".join(
                f"[{_PHASE_COLORS.get(p.status, MARKUP_MUTED)}]{phase_glyph(p.status)}"
                f"[/{_PHASE_COLORS.get(p.status, MARKUP_MUTED)}] {p.id}"
                for p in data.phases
            )
            lines.append(f"  {track}")
        else:
            lines.append(f"[{MARKUP_MUTED}]no pipeline runs[/{MARKUP_MUTED}]")
        lines.append("")

        target = f" → {escape(data.merge_target)}" if data.merge_target else ""
        lines.append(f"Branch: {br}{target}")
        if not data.path_exists:
            lines.append(f"  [{MARKUP_ERROR}]✗ path not found[/{MARKUP_ERROR}]")
        else:
            dirty_s = "s" if data.dirty_count != 1 else ""
            behind_s = "s" if data.behind_count != 1 else ""
            lines.append(
                f"  dirty: {data.dirty_count} file{dirty_s}"
                f" · behind: {data.behind_count} commit{behind_s}"
            )
        lines.append("")

        if data.commits:
            lines.append("Recent commits:")
            lines.extend(f"  {escape(c)}" for c in data.commits)
        else:
            lines.append(f"[{MARKUP_MUTED}]no commits[/{MARKUP_MUTED}]")
        lines.append("")

        if data.mr_url:
            lines.append(f"MR: {data.mr_url}")
        else:
            lines.append(f"[{MARKUP_MUTED}]no MR link[/{MARKUP_MUTED}]")

        return "\n".join(lines)
