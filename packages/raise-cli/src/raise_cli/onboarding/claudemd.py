"""Backward-compatibility shim for claudemd module.

All types have moved to raise_cli.onboarding.instructions.
"""

from raise_cli.onboarding.instructions import (
    ClaudeMdGenerator as ClaudeMdGenerator,
)
from raise_cli.onboarding.instructions import (
    InstructionsGenerator as InstructionsGenerator,
)
from raise_cli.onboarding.instructions import (
    generate_claude_md as generate_claude_md,
)
from raise_cli.onboarding.instructions import (
    generate_instructions as generate_instructions,
)
