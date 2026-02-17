"""Global test fixtures.

Prevents test leakage into real ~/.rai/developer.yaml by redirecting
get_rai_home to a temporary directory for ALL tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_rai_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect get_rai_home to tmp_path for every test.

    Without this, any test that triggers save_developer_profile (directly
    or indirectly via process_session_close) writes to the real
    ~/.rai/developer.yaml, contaminating the developer's profile.
    """
    fake_rai_home = tmp_path / ".rai"
    monkeypatch.setattr(
        "rai_cli.onboarding.profile.get_rai_home", lambda: fake_rai_home
    )
