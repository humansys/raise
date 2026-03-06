"""Backward-compatibility shim for claudemd module.

All types have moved to rai_cli.onboarding.instructions.
"""

from rai_cli.onboarding.instructions import (
    ClaudeMdGenerator as ClaudeMdGenerator,
)
from rai_cli.onboarding.instructions import (
    InstructionsGenerator as InstructionsGenerator,
)
from rai_cli.onboarding.instructions import (
    generate_claude_md as generate_claude_md,
)
from rai_cli.onboarding.instructions import (
    generate_instructions as generate_instructions,
)
