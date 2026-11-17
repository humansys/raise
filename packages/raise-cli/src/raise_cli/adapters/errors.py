"""Adapter-specific exceptions."""

from __future__ import annotations


class AdapterSyncError(Exception):
    """Raised when a server-first write fails verification."""
