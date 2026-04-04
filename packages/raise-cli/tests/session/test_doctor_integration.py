"""Integration tests — SessionDoctor full lifecycle against real filesystem."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from raise_cli.session.doctor import SessionDoctor
from raise_cli.session.index import ActiveSessionPointer, write_active_session


def _setup_project(tmp_path: Path) -> Path:
    """Create minimal project structure."""
    personal = tmp_path / ".raise" / "rai" / "personal"
    personal.mkdir(parents=True)
    (personal / "sessions").mkdir()
    return tmp_path


class TestDoctorLifecycle:
    """Full lifecycle: diagnose → classify → execute."""

    def test_clean_state_no_findings(self, tmp_path: Path) -> None:
        """Fresh project has no issues."""
        project = _setup_project(tmp_path)
        doctor = SessionDoctor(project)

        findings = doctor.diagnose()
        assert findings == []

        plan = doctor.classify(findings)
        assert plan.auto_clean == []
        assert plan.needs_consent == []

    def test_stale_output_lifecycle(self, tmp_path: Path) -> None:
        """Stale output detected → classified as auto-clean → cleaned."""
        project = _setup_project(tmp_path)
        personal = project / ".raise" / "rai" / "personal"

        # Create stale output
        output = personal / "session-output.yaml"
        output.write_text("summary: old session data\n")
        old_time = time.time() - (26 * 3600)
        os.utime(output, (old_time, old_time))

        doctor = SessionDoctor(project)

        # 1. Diagnose
        findings = doctor.diagnose()
        assert len(findings) == 1
        assert findings[0].category == "stale_output"
        assert findings[0].safe_to_auto_clean is True

        # 2. Classify
        plan = doctor.classify(findings)
        assert len(plan.auto_clean) == 1
        assert len(plan.needs_consent) == 0

        # 3. Execute with auto consent
        cleaned = doctor.execute(plan, consent={"auto"})
        assert len(cleaned) == 1
        assert not output.exists()

    def test_zombie_with_narrative_needs_consent(self, tmp_path: Path) -> None:
        """Zombie with narrative → needs consent → not cleaned without it."""
        project = _setup_project(tmp_path)
        personal = project / ".raise" / "rai" / "personal"

        # Create old active session pointer
        started = datetime.now() - timedelta(hours=72)
        pointer = ActiveSessionPointer(
            id="S-E-260401-0900", name="test", started=started
        )
        write_active_session(pointer, project_root=project)

        # Create session dir with narrative
        session_dir = personal / "sessions" / "S-E-260401-0900"
        session_dir.mkdir()
        (session_dir / "narrative.md").write_text(
            "Implemented session diary publish with Confluence integration."
        )

        doctor = SessionDoctor(project)

        # 1. Diagnose
        findings = doctor.diagnose()
        zombies = [f for f in findings if f.category == "zombie"]
        assert len(zombies) == 1
        assert zombies[0].safe_to_auto_clean is False

        # 2. Classify
        plan = doctor.classify(findings)
        assert len(plan.needs_consent) == 1
        assert len(plan.auto_clean) == 0

        # 3. Execute without consent — nothing cleaned
        cleaned = doctor.execute(plan, consent=set())
        assert cleaned == []

        # Pointer still exists
        from raise_cli.session.index import read_active_session

        assert read_active_session(project_root=project) is not None

        # 4. Execute WITH consent — now cleaned
        cleaned = doctor.execute(plan, consent={"zombie"})
        assert len(cleaned) == 1
        assert read_active_session(project_root=project) is None

    def test_multiple_findings_mixed(self, tmp_path: Path) -> None:
        """Multiple issues: some auto-clean, some need consent."""
        project = _setup_project(tmp_path)
        personal = project / ".raise" / "rai" / "personal"
        sessions = personal / "sessions"

        # 1. Stale output (auto-clean)
        output = personal / "session-output.yaml"
        output.write_text("old data")
        old_time = time.time() - (26 * 3600)
        os.utime(output, (old_time, old_time))

        # 2. Retention exceeded (needs consent)
        for i in range(23):
            (sessions / f"S-E-2603{i:02d}-1000").mkdir()

        doctor = SessionDoctor(project)
        findings = doctor.diagnose()

        # Should have at least stale + retention
        categories = {f.category for f in findings}
        assert "stale_output" in categories
        assert "retention" in categories

        plan = doctor.classify(findings)
        assert len(plan.auto_clean) >= 1  # stale output
        # retention is info severity → goes to info_only (not needs_consent)
        assert len(plan.info_only) >= 1  # retention

        # Execute only auto — stale cleaned, dirs preserved
        doctor.execute(plan, consent={"auto"})
        assert not output.exists()
        assert len(list(sessions.iterdir())) == 23  # dirs untouched
