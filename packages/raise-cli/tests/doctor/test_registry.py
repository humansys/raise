"""Tests for doctor check registry."""

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.doctor.registry import CheckRegistry


class FakeCheck:
    """Minimal DoctorCheck for testing."""

    check_id = "fake-env"
    category = "environment"
    description = "Fake environment check"
    requires_online = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="all good",
            )
        ]


class FakeOnlineCheck:
    check_id = "fake-mcp"
    category = "mcp"
    description = "Fake MCP check"
    requires_online = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="connected",
            )
        ]


class TestCheckRegistry:
    def test_register_and_list(self) -> None:
        registry = CheckRegistry()
        registry.register(FakeCheck())
        assert len(registry.checks) == 1
        assert registry.checks[0].check_id == "fake-env"

    def test_protocol_conformance(self) -> None:
        assert isinstance(FakeCheck(), DoctorCheck)

    def test_rejects_non_conformant(self) -> None:
        registry = CheckRegistry()
        registry.register("not a check")  # type: ignore[arg-type]
        assert len(registry.checks) == 0

    def test_get_checks_for_category(self) -> None:
        registry = CheckRegistry()
        registry.register(FakeCheck())
        registry.register(FakeOnlineCheck())
        env_checks = registry.get_checks_for_category("environment")
        assert len(env_checks) == 1
        assert env_checks[0].check_id == "fake-env"

    def test_discover_loads_entry_points(self) -> None:
        """Discover should not crash even with no checks registered."""
        registry = CheckRegistry()
        registry.discover()
        # No assertions on count — depends on installed entry points
