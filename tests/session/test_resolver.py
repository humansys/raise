"""Tests for session ID resolution logic."""

from __future__ import annotations

import pytest

from rai_cli.exceptions import RaiSessionNotFoundError
from rai_cli.session.resolver import resolve_session_id


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
