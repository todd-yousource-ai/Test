# CONVENTIONS.md — Validation Subsystem

---

## Code Conventions

### File and Directory Naming

1. Place all validation source modules under `src/vtz/` using lowercase snake_case filenames: e.g., `src/vtz/validator.py`, `src/vtz/rules.py`, `src/vtz/exceptions.py`.
2. Place all validation tests under `tests/vtz/` mirroring the source layout: each source file `src/vtz/<component>.py` must have a corresponding `tests/vtz/test_<component>.py`.
3. Never use hyphens, camelCase, or uppercase characters in file or directory names.
4. The package root `src/vtz/__init__.py` must re-export every public validator class and function so consumers can import directly from `vtz` without knowing internal module structure (per FR-20 pattern).

### Class and Function Naming

5. Name all classes in PascalCase: `FieldValidator`, `SchemaRule`, `ValidationResult`.
6. Name all functions and methods in lowercase snake_case: `validate_field`, `check_required`, `apply_rules`.
7. Prefix private/internal helpers with a single underscore: `_coerce_type`, `_normalize_value`.
8. Name validator classes with the suffix `Validator` (e.g., `StatusValidator`, `TaskFieldValidator`).
9. Name rule classes or functions with the suffix `Rule` or prefix `check_` (e.g., `NonEmptyRule`, `check_status_enum`).
10. Name exception classes with the suffix `Error` (e.g., `ValidationError`, `FieldRequiredError`).

### Error and Exception Patterns

11. Define all validation exceptions in a single module: `src/vtz/exceptions.py`.
12. Create a base exception `ValidationError(Exception)` from which every other validation exception inherits.
13. Every `ValidationError` instance must carry at least two attributes: `field` (the name of the invalid field, as `str`) and `reason` (a human-readable explanation, as `str`).
14. Never raise bare `Exception`, `ValueError`, or `TypeError` from validation logic — always raise a `ValidationError` subclass.
15. Raise `FieldRequiredError(ValidationError)` when a mandatory field is missing or `None`.
16. Raise `InvalidStatusError(ValidationError)` when a status value is not a member of the status enumeration (see rule 24).
17. Never use string formatting with user-supplied data in exception messages without explicit conversion (`str()`); never embed tracebacks in returned error payloads.

### Import and Module Organisation

18. Use only the Python standard library. Zero external dependencies are permitted (NFR-1).
19. All modules must be importable without side effects. Module-level code must contain only class definitions, function definitions, constant assignments, and imports — no I/O, no network calls, no mutable global state initialisation (NFR-2).
20. Order imports in three groups separated by a blank line: (a) standard library, (b) other project-internal packages, (c) intra-package (relative) imports.
21. Use relative imports within the `vtz` package (e.g., `from .exceptions import ValidationError`).
22. Use absolute imports when referencing other subsystems (e.g., `from tasklib import Task`).
23. Never use wildcard imports (`from module import *`) in any file except `__init__.py` re-exports.

### Comment and Documentation Rules

24. Every public class and every public function/method must have a docstring (NFR-3). Use imperative mood in the first line: `"""Validate that the status field is a member of TaskStatus."""`
25. Docstrings must follow the pattern: one-line summary, blank line, then `Args:`, `Returns:`, and `Raises:` sections where applicable.
26. Inline comments (`#`) explain *why*, not *what*. Do not restate the code in English.
27. Mark all TODO items with the format `# TODO(<owner>): <description>` — never leave anonymous TODOs.
28. Do not place commented-out code in any committed file.

### Validation-Specific Patterns

29. Reference status values exclusively through the status enumeration (e.g., `TaskStatus.PENDING`). Magic strings such as `"pending"` or `"done"` are forbidden anywhere in validation logic (NFR-4).
30. Implement every discrete validation check as a standalone, pure function or single-responsibility class that receives the value under test and returns a `ValidationResult` or raises a `ValidationError`. Do not bundle unrelated checks.
31. Define a `ValidationResult` dataclass (or named tuple) with at minimum: `is_valid: bool`, `errors: list[ValidationError]`. All validators must return this type rather than bare booleans.
32. Compose validators using a `ValidationPipeline` (or equivalent) that accepts an ordered sequence of validator callables, runs them in order, and aggregates all `ValidationError` instances into a single `ValidationResult`. Fail-fast behaviour must be opt-in, not the default.
33. Every validator function must be idempotent and free of side effects — calling it twice with the same input must produce the same result and must not mutate the input.
34. Never silently coerce or modify input data inside a validator. If coercion is needed, perform it in a separate, explicit transformation step before validation.
35. Validate at system boundaries only (API entry points, deserialization, store writes). Do not scatter ad-hoc validation checks across business-logic layers.
36. Unit tests for each validator must cover at minimum: (a) a valid input, (b) each distinct invalid-input branch, (c) `None` / missing-field handling, and (d) boundary values where applicable.
37. Parametrize repetitive test cases using `pytest.mark.parametrize` rather than duplicating test functions.