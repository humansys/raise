"""Developer prefix registry for session identity.

Manages the mapping of single/multi-character prefixes to developers.
The registry lives in `.raise/rai/sessions/prefixes.yaml` (committed to git)
and enables zero-conflict session ID generation across developers.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel


class PrefixEntry(BaseModel, frozen=True):
    """A registered developer prefix."""

    name: str
    registered: date


class PrefixRegistry(BaseModel):
    """Registry of developer prefixes for session ID generation."""

    prefixes: dict[str, PrefixEntry]

    def register(
        self, prefix: str, name: str, *, registered_on: date | None = None
    ) -> str:
        """Register a developer prefix.

        If the prefix is already registered to the same developer (by name),
        this is a no-op (idempotent). If registered to a different developer,
        raises ValueError.

        Args:
            prefix: Developer prefix (e.g., "E").
            name: Developer full name (e.g., "Emilio Osorio").
            registered_on: Registration date. Defaults to today.

        Returns:
            The registered prefix (same as input on success).

        Raises:
            ValueError: If prefix is already registered to a different developer.
        """
        existing = self.prefixes.get(prefix)
        if existing is not None:
            if existing.name == name:
                return prefix
            raise ValueError(
                f"Prefix {prefix!r} already registered to {existing.name!r}. "
                f"Use {self.resolve_collision(prefix, name)!r} instead."
            )
        self.prefixes[prefix] = PrefixEntry(
            name=name, registered=registered_on or date.today()
        )
        return prefix

    def resolve_collision(self, prefix: str, name: str) -> str:
        """Suggest an extended prefix when a collision is detected.

        Uses the first letter of the last name. Falls back to prefix + "2"
        if the developer has a single name.

        Args:
            prefix: Colliding prefix.
            name: Developer full name.

        Returns:
            Suggested extended prefix.
        """
        parts = name.strip().split()
        if len(parts) >= 2:
            return f"{prefix}{parts[-1][0].upper()}"
        return f"{prefix}2"

    @classmethod
    def load(cls, path: Path) -> PrefixRegistry:
        """Load registry from a YAML file.

        Returns an empty registry if the file does not exist.

        Args:
            path: Path to prefixes.yaml.

        Returns:
            Loaded or empty PrefixRegistry.
        """
        if not path.exists():
            return cls(prefixes={})
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            return cls(prefixes={})
        entries: dict[str, PrefixEntry] = {}
        for key, value in raw.items():
            entries[str(key)] = PrefixEntry.model_validate(value)
        return cls(prefixes=entries)

    def save(self, path: Path) -> None:
        """Save registry to a YAML file.

        Creates parent directories if needed.

        Args:
            path: Path to prefixes.yaml.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            key: {"name": entry.name, "registered": str(entry.registered)}
            for key, entry in self.prefixes.items()
        }
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
