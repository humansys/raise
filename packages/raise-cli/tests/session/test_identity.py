"""Tests for session identity — timestamp-based ID generation."""

from __future__ import annotations

from datetime import datetime

from raise_cli.session.identity import generate_session_id


class TestGenerateSessionId:
    """Tests for generate_session_id function."""

    def test_format_matches_spec(self) -> None:
        """ID should match S-{prefix}-{YYMMDD}-{HHMM} format."""
        now = datetime(2026, 3, 22, 14, 30, 0)
        result = generate_session_id("E", now=now)
        assert result == "S-E-260322-1430"

    def test_deterministic_with_injected_time(self) -> None:
        """Same input should always produce same output."""
        now = datetime(2026, 1, 1, 0, 0, 0)
        result1 = generate_session_id("E", now=now)
        result2 = generate_session_id("E", now=now)
        assert result1 == result2 == "S-E-260101-0000"

    def test_multi_char_prefix(self) -> None:
        """Should work with multi-character prefixes."""
        now = datetime(2026, 3, 22, 9, 5, 0)
        result = generate_session_id("EO", now=now)
        assert result == "S-EO-260322-0905"

    def test_default_now_uses_current_time(self) -> None:
        """Without now param, should use current time."""
        result = generate_session_id("E")
        assert result.startswith("S-E-")
        # Format: S-E-YYMMDD-HHMM → 4 parts separated by -
        parts = result.split("-")
        assert len(parts) == 4
        assert len(parts[2]) == 6  # YYMMDD
        assert len(parts[3]) == 4  # HHMM
