"""Shared test fixtures for raise-server tests."""

from __future__ import annotations

import uuid

import pytest


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def member_id() -> uuid.UUID:
    return uuid.uuid4()
