"""Backward-compatibility shim for claudemd module.

All types have moved to rai_cli.onboarding.instructions.
"""

from rai_cli.onboarding.instructions import (
    ClaudeMdGenerator as ClaudeMdGenerator,
    InstructionsGenerator as InstructionsGenerator,
    generate_claude_md as generate_claude_md,
    generate_instructions as generate_instructions,
)
