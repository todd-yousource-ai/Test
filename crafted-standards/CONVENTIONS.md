# CONVENTIONS.md — Validation Subsystem

---

## Code Conventions

### File and Directory Naming

1. All validation source files must reside under `src/vtz/` following the pattern `src/vtz/<component>.py`.
2. All validation test files must mirror the source tree under `tests/vtz/` following the pattern `tests/vtz/test_<component>.py`.
3. File names must use lowercase `snake_case` exclusively. No hyphens, no camelCase, no uppercase letters in file or directory names.
4. Each validation concern (e.g., schema validation, field validation, status validation) must occupy its own module file. Do not combine unrelated validation logic in a single file.
5. The package root `src/vtz/__init__.py` must re-export the subsystem's public API classes and functions at the top level so consumers can import directly from `vtz` without knowing internal module structure.

---

### Class and Function Naming

6. Classes must use `PascalCase` (e.g., `FieldValidator`, `StatusValidationError`).
7. Functions and methods must use `snake_case` (e.g., `validate_status`, `check_required_fields`).
8. Validator classes must be suffixed with `Validator` (e.g., `TaskFieldValidator`, `SchemaValidator`).
9. Validation functions that return a boolean must be prefixed with `is_` or `has_` (e.g., `is_valid_status`, `has_required_fields`).
10. Validation functions that raise on failure must be prefixed with `validate_` or `check_` (e.g., `validate_task_data`, `check_status_transition`).
11. Constants must use `UPPER_SNAKE_CASE` and be defined at module level (e.g., `MAX_TITLE_LENGTH`, `REQUIRED_FIELDS`).

---

### Error and Exception Patterns

12. All validation exceptions must inherit from a single base exception class named `ValidationError`, defined in `src/vtz/exceptions.py`.
13. Each distinct validation failure category must have its own exception subclass (e.g., `FieldValidationError`, `StatusValidationError`, `SchemaValidationError`).
14. Every exception instance must carry a human-readable `message` attribute and a machine-readable `code` string attribute (e.g., `code="MISSING_REQUIRED_FIELD"`).
15. Validation functions must never catch and silently swallow exceptions. If a validation step fails, either raise the appropriate `ValidationError` subclass or return a structured error result—never return `None` to signal failure.
16. When multiple validation errors are detected in a single pass, collect them into a list and raise a `ValidationError` whose `errors` attribute contains all individual error objects. Do not short-circuit on the first failure unless explicitly documented.

---

### Import and Module Organisation

17. Only Python standard library modules may be imported. Zero external dependencies are permitted (NFR-1).
18. All modules must be importable without side effects. Module-level code must be limited to class definitions, function definitions, constant assignments, and imports. No I/O, no computation, no registration calls at import time (NFR-2).
19. Intra-subsystem imports must use explicit relative imports (e.g., `from .exceptions import ValidationError`).
20. Cross-subsystem imports must use absolute imports rooted at `src` (e.g., `from tasklib import Task`).
21. Status values must be referenced exclusively via their enumeration members throughout all validation code. Hard-coded status strings (magic strings) are forbidden (NFR-4). Example: use `TaskStatus.COMPLETE`, never the string `"complete"`.
22. Import statements must be grouped in the standard order: (1) standard library, (2) cross-subsystem absolute imports, (3) intra-subsystem relative imports—separated by a single blank line between each group.

---

### Comment and Documentation Rules

23. Every public class, method, and function must have a docstring describing its purpose, parameters, return value, and exceptions raised (NFR-3).
24. Docstrings must follow the format:
    ```python
    def validate_status(status: TaskStatus) -> bool:
        """Check whether the given status is a valid TaskStatus member.

        Args:
            status: The status value to validate.

        Returns:
            True if the status is valid.

        Raises:
            StatusValidationError: If the status is not a recognised member.
        """
    ```
25. Inline comments must explain *why*, not *what*. Do not restate the code in English.
26. TODO comments must include a tracking reference (e.g., `# TODO(VTZ-42): support custom status enums`).
27. Private helpers (prefixed with `_`) must still carry a one-line docstring.

---

### Validation-Specific Patterns

28. Every validator must implement a callable interface with the signature `validate(data) -> ValidationResult` or raise a `ValidationError`. Do not mix return-based and exception-based signalling within the same validator class.
29. `ValidationResult` must be a dataclass (or named tuple) with at minimum two fields: `is_valid: bool` and `errors: list[ValidationError]`.
30. Status validation must always resolve status values through the project's status enumeration. Any comparison against a raw string must be flagged as a defect.
31. Validators must be stateless. All inputs must be passed as arguments; no validator may cache prior results or mutate shared state.
32. Composite validation (running multiple validators in sequence) must be implemented through a `ValidationPipeline` class that accepts an ordered list of validators and executes them in sequence, aggregating all `ValidationError` instances before returning or raising.
33. Field-level validators must declare which field(s) they validate via a `fields` class attribute (a tuple of field name strings). This enables introspection and pipeline composition.
34. Boundary values (e.g., max lengths, allowed ranges) must be defined as module-level constants, never as inline literals inside validation logic.
35. Every validation rule must have a corresponding unit test in `tests/vtz/test_<component>.py` covering at minimum: one valid input, one invalid input, and one edge-case input.
36. Validators must not perform type coercion. If the input type is wrong, raise `FieldValidationError` with a message identifying the expected type. Validation observes; it does not transform.