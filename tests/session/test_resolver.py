"""Tests for session ID resolution logic."""

from __future__ import annotations

import pytest

from raise_cli.exceptions import RaiSessionNotFoundError
from raise_cli.session.resolver import (
    _normalize_session_id,
    resolve_session_id,
    resolve_session_id_optional,
)


class TestResolveSessionId:
    """Tests for resolve_session_id function."""

    def test_returns_flag_when_provided(self) -> None:
        """resolve_session_id returns --session flag value when provided."""
        result = resolve_session_id(session_flag="SES-177", env_var=None)
        assert result == "SES-177"

    def test_flag_takes_priority_over_env_var(self) -> None:
        """resolve_session_id prioritizes --session flag over RAI_SESSION_ID."""
        result = resolve_session_id(session_flag="SES-177", env_var="SES-999")
        assert result == "SES-177"

    def test_returns_env_var_when_flag_missing(self) -> None:
        """resolve_session_id returns RAI_SESSION_ID when --session not provided."""
        result = resolve_session_id(session_flag=None, env_var="SES-178")
        assert result == "SES-178"

    def test_raises_error_when_both_missing(self) -> None:
        """resolve_session_id raises RaiSessionNotFoundError when both sources missing."""
        with pytest.raises(RaiSessionNotFoundError, match="No session ID provided"):
            resolve_session_id(session_flag=None, env_var=None)

    def test_normalizes_numeric_only_flag(self) -> None:
        """resolve_session_id normalizes '177' to 'SES-177' from flag."""
        result = resolve_session_id(session_flag="177", env_var=None)
        assert result == "SES-177"

    def test_normalizes_numeric_only_env_var(self) -> None:
        """resolve_session_id normalizes '178' to 'SES-178' from env var."""
        result = resolve_session_id(session_flag=None, env_var="178")
        assert result == "SES-178"

    def test_normalizes_lowercase_prefix(self) -> None:
        """resolve_session_id normalizes 'ses-177' to 'SES-177'."""
        result = resolve_session_id(session_flag="ses-177", env_var=None)
        assert result == "SES-177"

    def test_handles_empty_string_flag(self) -> None:
        """resolve_session_id treats empty string flag as None."""
        result = resolve_session_id(session_flag="", env_var="SES-178")
        assert result == "SES-178"

    def test_handles_empty_string_env_var(self) -> None:
        """resolve_session_id treats empty string env var as None."""
        with pytest.raises(RaiSessionNotFoundError):
            resolve_session_id(session_flag=None, env_var="")

    def test_strips_whitespace_from_flag(self) -> None:
        """resolve_session_id strips whitespace from flag value."""
        result = resolve_session_id(session_flag="  SES-177  ", env_var=None)
        assert result == "SES-177"

    def test_strips_whitespace_from_env_var(self) -> None:
        """resolve_session_id strips whitespace from env var value."""
        result = resolve_session_id(session_flag=None, env_var="  SES-178  ")
        assert result == "SES-178"


class TestNormalizeSessionIdPathTraversal:
    """CWE-23 regression tests: session IDs must not contain path traversal."""

    def test_rejects_dotdot_in_session_id(self) -> None:
        """_normalize_session_id rejects '..' path traversal."""
        with pytest.raises(ValueError, match="path traversal"):
            _normalize_session_id("../../../etc/passwd")

    def test_rejects_forward_slash_in_session_id(self) -> None:
        """_normalize_session_id rejects forward slashes."""
        with pytest.raises(ValueError, match="path traversal"):
            _normalize_session_id("SES-177/../../etc")

    def test_rejects_backslash_in_session_id(self) -> None:
        """_normalize_session_id rejects backslashes."""
        with pytest.raises(ValueError, match="path traversal"):
            _normalize_session_id("SES-177\\..\\..\\etc")

    def test_rejects_dotdot_via_resolve_session_id(self) -> None:
        """resolve_session_id propagates traversal rejection from flag."""
        with pytest.raises(ValueError, match="path traversal"):
            resolve_session_id(session_flag="../escape", env_var=None)

    def test_rejects_dotdot_via_env_var(self) -> None:
        """resolve_session_id propagates traversal rejection from env var."""
        with pytest.raises(ValueError, match="path traversal"):
            resolve_session_id(session_flag=None, env_var="../escape")

    def test_rejects_dotdot_via_resolve_optional(self) -> None:
        """resolve_session_id_optional propagates traversal rejection."""
        with pytest.raises(ValueError, match="path traversal"):
            resolve_session_id_optional(session_flag=None, env_var="../escape")

    def test_accepts_valid_session_id(self) -> None:
        """Valid session IDs are not rejected."""
        assert _normalize_session_id("SES-177") == "SES-177"
        assert _normalize_session_id("177") == "SES-177"
        assert _normalize_session_id("ses-42") == "SES-42"


class TestNormalizeNewFormat:
    """Tests for new timestamp-based session ID format (S-{prefix}-{YYMMDD}-{HHMM})."""

    def test_new_format_passthrough(self) -> None:
        """New format S-{prefix}-{YYMMDD}-{HHMM} should pass through uppercased."""
        result = _normalize_session_id("S-E-260322-1430")
        assert result == "S-E-260322-1430"

    def test_new_format_lowercase_passthrough(self) -> None:
        """Lowercase new format should be uppercased."""
        result = _normalize_session_id("s-e-260322-1430")
        assert result == "S-E-260322-1430"

    def test_new_format_multi_char_prefix(self) -> None:
        """Multi-character prefix should work."""
        result = _normalize_session_id("S-EO-260322-1430")
        assert result == "S-EO-260322-1430"

    def test_new_format_via_resolve(self) -> None:
        """New format should work through resolve_session_id."""
        result = resolve_session_id(
            session_flag="S-E-260322-1430", env_var=None
        )
        assert result == "S-E-260322-1430"

    def test_new_format_via_env_var(self) -> None:
        """New format should work via RAI_SESSION_ID env var."""
        result = resolve_session_id(
            session_flag=None, env_var="S-E-260322-1430"
        )
        assert result == "S-E-260322-1430"

    def test_legacy_format_still_works(self) -> None:
        """Legacy SES-NNN format should still be accepted."""
        result = _normalize_session_id("SES-177")
        assert result == "SES-177"
