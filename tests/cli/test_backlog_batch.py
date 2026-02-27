"""Tests for batch-transition key parsing edge cases."""

from __future__ import annotations

import pytest


class TestBatchKeyParsing:
    """Parsing of comma-separated keys in batch-transition."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("RAISE-1,RAISE-2", ["RAISE-1", "RAISE-2"]),
            ("RAISE-1, RAISE-2, RAISE-3", ["RAISE-1", "RAISE-2", "RAISE-3"]),
            ("RAISE-1", ["RAISE-1"]),
            ("  RAISE-1 , RAISE-2  ", ["RAISE-1", "RAISE-2"]),
            ("RAISE-1,,RAISE-2", ["RAISE-1", "RAISE-2"]),  # empty segment skipped
            ("RAISE-1,", ["RAISE-1"]),  # trailing comma
            (",RAISE-1", ["RAISE-1"]),  # leading comma
        ],
    )
    def test_valid_keys(self, raw: str, expected: list[str]) -> None:
        result = [k.strip() for k in raw.split(",") if k.strip()]
        assert result == expected

    def test_empty_string_yields_nothing(self) -> None:
        result = [k.strip() for k in [""] if k.strip()]
        assert result == []

    def test_only_commas_yields_nothing(self) -> None:
        result = [k.strip() for k in ["", "", "", ""] if k.strip()]
        assert result == []
