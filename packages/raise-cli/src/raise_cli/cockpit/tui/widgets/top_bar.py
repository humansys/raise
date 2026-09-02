"""TopBar widget — tab indicators for the cockpit TUI."""

from __future__ import annotations

from textual.widgets import Static


class TopBar(Static):
    """Single-line bar showing tab indicators."""

    DEFAULT_CSS = """
    TopBar {
        dock: top;
        height: 1;
        background: $surface_warm;
        color: $foreground;
        content-align: left middle;
        padding: 0 1;
    }
    """

    def __init__(self, active_tab: int = 1) -> None:
        super().__init__()
        self._active_tab = active_tab
        self._hint: str | None = None

    def set_hint(self, text: str | None) -> None:
        """Append (or clear) a ` · {text}` suffix — additive (RAISE-16714, D-S4.5)."""
        self._hint = text
        self.refresh()

    def render(self) -> str:
        """Render tab indicators."""
        tabs = [
            ("1 sessions", 1),
            ("2 fleet", 2),
        ]
        parts: list[str] = ["rai  "]
        for label, idx in tabs:
            if idx == self._active_tab:
                parts.append(f"❮{label}❯")
            else:
                parts.append(label)
            parts.append(" · ")
        rendered = "".join(parts).removesuffix(" · ")
        if self._hint:
            rendered = f"{rendered} · {self._hint}"
        return rendered
