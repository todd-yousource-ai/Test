"""Minimal smoke check module.

Security assumptions:
- This function performs no I/O, authentication, or external interaction.
- It returns a constant boolean value and therefore has no input-validation surface.

Failure behavior:
- Deterministic; does not intentionally raise exceptions.
- Any unexpected runtime failure surfaces naturally to the caller.
"""


def smoke_check() -> bool:
    """Return True for basic smoke-test validation."""
    return True
