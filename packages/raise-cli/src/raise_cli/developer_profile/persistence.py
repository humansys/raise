"""Developer profile persistence — save to disk via stdlib atomic write."""

from __future__ import annotations

import contextlib
import logging
import os
import tempfile

import yaml

from raise_cli.developer_profile.profile import (
    DEVELOPER_PROFILE_FILE,
    DeveloperProfile,
    get_rai_home,
)

logger = logging.getLogger(__name__)


def save_developer_profile(profile: DeveloperProfile) -> None:
    """Save developer profile to ~/.rai/developer.yaml.

    Uses stdlib atomic write (NamedTemporaryFile + os.replace) with fsync
    for durability. Creates ~/.rai/ if it doesn't exist.
    """
    rai_home = get_rai_home()
    data = profile.model_dump(mode="json")
    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    target = rai_home / DEVELOPER_PROFILE_FILE
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        delete=False,
        suffix=".tmp",
    ) as fd:
        tmp_name = fd.name
        try:
            fd.write(content)
            fd.flush()
            os.fsync(fd.fileno())
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)
            raise
    os.replace(tmp_name, target)
    logger.debug("Saved developer profile: %s", target)
