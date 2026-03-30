"""Entry point for ``python -m tasklib`` invocation.

Security assumptions:
- Delegates all argument parsing and validation to ``tasklib.cli.main.main()``.
- No secrets or credentials are handled in this module.
- Exit code is preserved via ``SystemExit`` so the calling process receives
  the correct status from the CLI dispatcher.

Failure behavior:
- If ``main()`` raises an unhandled exception it propagates naturally.
- The integer exit code returned by ``main()`` is forwarded to the OS via
  ``SystemExit``, ensuring non-zero codes on error paths are never swallowed.
"""

from __future__ import annotations

if __name__ == "__main__":
    from tasklib.cli.main import main

    raise SystemExit(main())
