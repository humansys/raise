"""Tests for SessionDoctor — diagnose, classify, execute."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

from raise_cli.session.doctor import ActionPlan, Finding, SessionDoctor


class TestFindingModel:
    """Finding is a frozen Pydantic model."""

    def test_finding_frozen(self) -> None:
        f = Finding(
            category="zombie",
            severity="warning",
            description="Zombie session detected",
            detail="S-E-260401-0900 (72h old)",
            safe_to_auto_clean=False,
            action="Review before cleaning",
        )
        assert f.category == "zombie"
        assert f.severity == "warning"
        assert f.safe_to_auto_clean is False

    def test_finding_immutable(self) -> None:
        import pytest

        f = Finding(
            category="stale_output",
            severity="info",
            description="Stale output",
            detail="26h old",
            safe_to_auto_clean=True,
            action="Remove",
        )
        with pytest.raises(Exception):  # noqa: B017, PT011
            f.category = "other"  # type: ignore[misc]


class TestActionPlanModel:
    """ActionPlan is a frozen Pydantic model."""

    def test_action_plan_frozen(self) -> None:
        plan = ActionPlan(auto_clean=[], needs_consent=[], info_only=[])
        assert plan.auto_clean == []
        assert plan.needs_consent == []
        assert plan.info_only == []


class TestDiagnoseCleanState:
    """diagnose() returns empty list when no issues."""

    def test_diagnose_clean(self, tmp_path: Path) -> None:
        # Set up minimal personal dir structure
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        sessions = personal / "sessions"
        sessions.mkdir()

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        assert findings == []


class TestDiagnoseZombie:
    """diagnose() detects zombie active-session pointers."""

    def test_zombie_no_content(self, tmp_path: Path) -> None:
        """Zombie pointer with no narrative in session dir → safe to clean."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        sessions = personal / "sessions"
        sessions.mkdir()

        # Create an old active-session pointer (>48h)
        _write_active_session_pointer(
            personal, session_id="S-E-260401-0900", hours_ago=72
        )

        # Create empty session dir (no narrative)
        (sessions / "S-E-260401-0900").mkdir()

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()

        zombies = [f for f in findings if f.category == "zombie"]
        assert len(zombies) == 1
        assert zombies[0].safe_to_auto_clean is True
        assert "72" in zombies[0].detail or "S-E-260401-0900" in zombies[0].detail

    def test_zombie_with_narrative(self, tmp_path: Path) -> None:
        """Zombie pointer with narrative content → needs consent."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        sessions = personal / "sessions"
        sessions.mkdir()

        _write_active_session_pointer(
            personal, session_id="S-E-260401-0900", hours_ago=72
        )

        # Create session dir WITH narrative
        session_dir = sessions / "S-E-260401-0900"
        session_dir.mkdir()
        (session_dir / "narrative.md").write_text("Implemented session diary publish...")

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()

        zombies = [f for f in findings if f.category == "zombie"]
        assert len(zombies) == 1
        assert zombies[0].safe_to_auto_clean is False
        assert "narrative" in zombies[0].detail.lower()

    def test_no_zombie_when_fresh(self, tmp_path: Path) -> None:
        """Active session <48h old is NOT a zombie."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        _write_active_session_pointer(
            personal, session_id="S-E-260403-1000", hours_ago=2
        )

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        zombies = [f for f in findings if f.category == "zombie"]
        assert len(zombies) == 0


class TestDiagnoseStaleOutput:
    """diagnose() detects stale session-output.yaml."""

    def test_stale_output_detected(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        # Create old session-output.yaml
        output = personal / "session-output.yaml"
        output.write_text("summary: old session")
        # Set mtime to 26h ago
        old_time = time.time() - (26 * 3600)
        import os

        os.utime(output, (old_time, old_time))

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()

        stale = [f for f in findings if f.category == "stale_output"]
        assert len(stale) == 1
        assert stale[0].safe_to_auto_clean is True

    def test_fresh_output_not_flagged(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        output = personal / "session-output.yaml"
        output.write_text("summary: fresh session")
        # mtime is now — should NOT be flagged

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        stale = [f for f in findings if f.category == "stale_output"]
        assert len(stale) == 0


class TestDiagnoseRetention:
    """diagnose() detects session dirs beyond retention limit."""

    def test_retention_exceeded(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        sessions = personal / "sessions"
        sessions.mkdir()

        # Create 23 session dirs (limit is 20)
        for i in range(23):
            d = sessions / f"S-E-2603{i:02d}-1000"
            d.mkdir()

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()

        retention = [f for f in findings if f.category == "retention"]
        assert len(retention) == 1
        assert "23" in retention[0].detail
        assert retention[0].safe_to_auto_clean is False  # needs consent

    def test_within_retention(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        sessions = personal / "sessions"
        sessions.mkdir()

        for i in range(18):
            (sessions / f"S-E-2603{i:02d}-1000").mkdir()

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        retention = [f for f in findings if f.category == "retention"]
        assert len(retention) == 0


class TestClassify:
    """classify() separates findings by risk."""

    def test_classify_separates(self) -> None:
        auto = Finding(
            category="stale_output",
            severity="info",
            description="Stale output",
            detail="26h old",
            safe_to_auto_clean=True,
            action="Remove",
        )
        consent = Finding(
            category="zombie",
            severity="warning",
            description="Zombie with narrative",
            detail="has content",
            safe_to_auto_clean=False,
            action="Review",
        )

        doctor = SessionDoctor(Path("/tmp/fake"))
        plan = doctor.classify([auto, consent])

        assert auto in plan.auto_clean
        assert consent in plan.needs_consent
        assert plan.info_only == []


class TestExecute:
    """execute() only cleans authorized items."""

    def test_execute_skips_without_consent(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        # Create stale output
        output = personal / "session-output.yaml"
        output.write_text("old data")
        old_time = time.time() - (26 * 3600)
        import os

        os.utime(output, (old_time, old_time))

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        plan = doctor.classify(findings)

        # Execute with empty consent — nothing should be cleaned
        cleaned = doctor.execute(plan, consent=set())
        assert cleaned == []
        assert output.exists()  # still there

    def test_execute_cleans_with_consent(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        output = personal / "session-output.yaml"
        output.write_text("old data")
        old_time = time.time() - (26 * 3600)
        import os

        os.utime(output, (old_time, old_time))

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        plan = doctor.classify(findings)

        # Execute with stale_output consent
        cleaned = doctor.execute(plan, consent={"stale_output"})
        assert len(cleaned) >= 1
        assert not output.exists()

    def test_execute_auto_clean_always_runs(self, tmp_path: Path) -> None:
        """Auto-clean items run even without explicit consent for their category."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        output = personal / "session-output.yaml"
        output.write_text("old data")
        old_time = time.time() - (26 * 3600)
        import os

        os.utime(output, (old_time, old_time))

        doctor = SessionDoctor(tmp_path)
        findings = doctor.diagnose()
        plan = doctor.classify(findings)

        # auto_clean items should run with auto_clean=True consent
        cleaned = doctor.execute(plan, consent={"auto"})
        assert len(cleaned) >= 1
        assert not output.exists()


# --- Helpers ---


def _write_active_session_pointer(
    personal_dir: Path, session_id: str, hours_ago: float
) -> None:
    """Write an active-session JSON pointer with a past start time."""
    from datetime import timedelta

    from raise_cli.session.index import ActiveSessionPointer

    started = datetime.now() - timedelta(hours=hours_ago)
    pointer = ActiveSessionPointer(id=session_id, name="test", started=started)
    pointer_path = personal_dir / "active-session"
    pointer_path.write_text(pointer.model_dump_json() + "\n")
