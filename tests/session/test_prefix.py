"""Tests for developer prefix registry."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from raise_cli.session.prefix import PrefixEntry, PrefixRegistry


class TestPrefixRegistryEmpty:
    """Tests for creating and loading empty registries."""

    def test_load_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        """Loading from nonexistent file should return empty registry."""
        registry = PrefixRegistry.load(tmp_path / "prefixes.yaml")
        assert registry.prefixes == {}

    def test_empty_registry_has_no_prefixes(self) -> None:
        """New registry should have no prefixes."""
        registry = PrefixRegistry(prefixes={})
        assert len(registry.prefixes) == 0


class TestPrefixRegistryRegister:
    """Tests for registering new developer prefixes."""

    def test_register_new_prefix(self) -> None:
        """Registering a new prefix should add it to the registry."""
        registry = PrefixRegistry(prefixes={})
        actual = registry.register("E", "Emilio Osorio")
        assert actual == "E"
        assert "E" in registry.prefixes
        assert registry.prefixes["E"].name == "Emilio Osorio"

    def test_register_sets_date(self) -> None:
        """Registration date should use provided date or default to today."""
        registry = PrefixRegistry(prefixes={})
        fixed_date = date(2026, 3, 22)
        registry.register("E", "Emilio Osorio", registered_on=fixed_date)
        assert registry.prefixes["E"].registered == fixed_date

    def test_register_existing_same_name_is_idempotent(self) -> None:
        """Registering the same prefix+name should be idempotent."""
        registry = PrefixRegistry(
            prefixes={
                "E": PrefixEntry(name="Emilio Osorio", registered=date(2026, 1, 1))
            }
        )
        actual = registry.register("E", "Emilio Osorio")
        assert actual == "E"
        # Should not change the registration date
        assert registry.prefixes["E"].registered == date(2026, 1, 1)


class TestPrefixRegistryCollision:
    """Tests for prefix collision detection and resolution."""

    def test_collision_detected(self) -> None:
        """Different developer with same prefix should trigger collision."""
        registry = PrefixRegistry(
            prefixes={
                "E": PrefixEntry(name="Eduardo Pérez", registered=date(2026, 1, 1))
            }
        )
        with pytest.raises(ValueError, match="already registered"):
            registry.register("E", "Emilio Osorio")

    def test_resolve_collision_suggests_extended(self) -> None:
        """Should suggest extended prefix based on last name initial."""
        registry = PrefixRegistry(
            prefixes={
                "E": PrefixEntry(name="Eduardo Pérez", registered=date(2026, 1, 1))
            }
        )
        suggested = registry.resolve_collision("E", "Emilio Osorio")
        assert suggested == "EO"

    def test_resolve_collision_single_name(self) -> None:
        """Should handle single-name developers (no last name)."""
        registry = PrefixRegistry(
            prefixes={"E": PrefixEntry(name="Eduardo", registered=date(2026, 1, 1))}
        )
        suggested = registry.resolve_collision("E", "Emilio")
        # No last name to use, fallback to E2
        assert suggested == "E2"


class TestPrefixRegistryRoundtrip:
    """Tests for YAML serialization roundtrip."""

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        """Save then load should produce equivalent registry."""
        original = PrefixRegistry(
            prefixes={
                "E": PrefixEntry(name="Emilio Osorio", registered=date(2026, 3, 22)),
                "J": PrefixEntry(name="Juan Pérez", registered=date(2026, 3, 25)),
            }
        )
        path = tmp_path / "prefixes.yaml"
        original.save(path)
        loaded = PrefixRegistry.load(path)
        assert loaded.prefixes == original.prefixes

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Save should create parent directories if needed."""
        path = tmp_path / "nested" / "dir" / "prefixes.yaml"
        registry = PrefixRegistry(
            prefixes={"E": PrefixEntry(name="Emilio", registered=date(2026, 1, 1))}
        )
        registry.save(path)
        assert path.exists()
