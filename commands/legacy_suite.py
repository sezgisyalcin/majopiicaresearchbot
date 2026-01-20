from __future__ import annotations

"""Legacy command suite merged from prior Majopiica Research Bot iterations.

This module intentionally keeps the prior command implementations largely intact,
while registering them onto the shared bot instance.

Key guarantees:
- No references to 'bottany' packages.
- No 'We love Kevy' footer text.
"""

from typing import Any


def register_legacy_suite(bot: Any, data_dir: str) -> None:
    # Provide expected globals for the legacy code.
    g = {
        '__name__': 'majopiica_researchbot.commands.legacy_suite_impl',
        '__package__': None,
        'BOT': bot,
        'DATA_DIR': data_dir,
    }
    # Execute the legacy command definitions in a controlled namespace.
    exec(_LEGACY_CODE, g, g)


_LEGACY_CODE = r