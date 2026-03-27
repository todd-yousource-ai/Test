# CONVENTIONS.md — Validation Subsystem

---

## Code Conventions

### File and Directory Naming

1. Place all validation source modules under `src/vtz/` following the pattern `src/vtz/<component>.py`.
2. Place all validation tests under `tests/vtz/` following the pattern `tests/vtz/test_<component>.py`. Every source module in `src/vtz/` must have a corresponding test file.
3. Use lowercase_snake_case for all file names. No hyphens, no camelCase (e.g., `field_validator.py`, not `fieldValidator.py` or `field-validator.py`).
4. The package root `src/vtz/__init__.py` must re-export every public validator class and function so consumers can import directly from `vtz` without knowing the internal module structure (mirrors FR-20 pattern).
5. Name modules after the single responsibility they own (e.g., `status_validator.py`, `schema_rules.py`, `constraint_checks.py`). Do not create catch-all modules named `utils.py` or `helpers.py`.

---

### Class and Function Naming

6. Use PascalCase for all class names. Validator classes must end with the suffix `Validator` (e.g., `TaskFieldValidator`, `StatusTransitionValidator`).
7. Use lowercase_snake_case for all function and method names (e.g., `validate_status`, `check_required_fields`).
8. Public validation entry-point methods must be named `validate` or prefixed with `validate_` (e.g., `validate`, `validate_status`, `validate_constraints`).
9. Private helper methods must be prefixed with a single underscore (e.g., `_check_length`, `_coerce_type`).
10. Constants must be UPPER_SNAKE_CASE and defined at module level (e.g., `MAX_TITLE_LENGTH = 256`).

---

### Error and Exception Patterns

11. Define a base exception class `ValidationError` in `src/vtz/exceptions.py`. All validation-specific exceptions must inherit from it.
12. Create granular exception subclasses for distinct failure categories (e.g., `FieldRequiredError`, `InvalidStatusError`, `ConstraintViolationError`), all inheriting from `ValidationError`.
13. Every raised exception must include a human-readable message that names the field and the violated rule. Example: `FieldRequiredError("Field 'title' is required and was None")`.
14. Never use bare `raise Exception(...)`. Always raise a `ValidationError` subclass.
15. Validators must not silently swallow exceptions. If a validator catches an exception internally for control flow, it must re-raise a `ValidationError` subclass or propagate the original.
16. Aggregate validation: when a validator checks multiple fields, collect all errors into a list and raise a single `ValidationError` whose `errors` attribute contains every individual violation, rather than failing on the first error.

---

### Import and Module Organisation

17. Use only the Python standard library. Zero external dependencies are permitted (NFR-1).
18. Order imports in three groups separated by a blank line: (1) standard library, (2) project-internal packages, (3) intra-subsystem relative imports. Sort alphabetically within each group.
19. Use absolute imports for cross-subsystem references (e.g., `from src.tasklib.status import TaskStatus`). Use relative imports only within the `vtz` package itself (e.g., `from .exceptions import ValidationError`).
20. All modules must be importable without side effects. No code may execute at import time beyond class definitions, function definitions, and constant assignments (NFR-2).
21. The `src/vtz/__init__.py` file must contain only re-exports and must not contain validation logic.

---

### Comment and Documentation Rules

22. Every public class must have a docstring describing its purpose, the fields or inputs it validates, and the exceptions it may raise (NFR-3).
23. Every public function and method must have a docstring with a one-line summary, an `Args:` section listing each parameter and its type, a `Returns:` section, and a `Raises:` section listing every `ValidationError` subclass it can raise.
24. Use inline comments only to explain *why*, never to restate *what* the code does.
25. Mark intentional design decisions or trade-offs with a `# DESIGN:` prefix comment.
26. Mark known limitations or future work with `# TODO(<author>):` followed by a tracker reference or one-line description.

---

### Validation-Specific Patterns

27. Reference status values exclusively through the status enumeration (e.g., `TaskStatus.OPEN`). Magic strings such as `"open"` or `"completed"` are forbidden anywhere in validation code (NFR-4).
28. Every validator must be a class that implements a `validate(self, data) -> None` interface. A successful validation returns `None`; a failed validation raises a `ValidationError` subclass.
29. Validators must be stateless. Configuration (e.g., allowed statuses, field constraints) must be injected via the constructor, not hard-coded in methods.
30. Compose complex validation by chaining validators through a `CompositeValidator` class that accepts an ordered list of validators and runs each in sequence, aggregating all `ValidationError` results.
31. Define validation rules as data when possible. For example, required-field checks should be driven by a list of field names, not by a separate `if` block per field.
32. Status transition validation must use an explicit adjacency mapping (e.g., `dict[TaskStatus, set[TaskStatus]]`) to define legal transitions. No implicit or hard-coded if/elif chains.
33. Validators must never mutate the input data. If normalization (e.g., stripping whitespace) is needed, perform it in a separate transformation step before validation.
34. Every validator class must be unit-testable in isolation. It must not depend on a database, network, or file system. Test files must cover: (a) valid input passes silently, (b) each distinct violation raises the correct exception subclass, and (c) aggregate mode collects all errors.
35. When validating enumerated values, compare against the enum members programmatically (e.g., `value in TaskStatus`) rather than maintaining a separate allowlist that could drift from the enum definition.