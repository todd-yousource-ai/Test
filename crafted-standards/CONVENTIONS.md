# CONVENTIONS.md — Validation Subsystem

---

## Code Conventions

### File and Directory Naming

1. Place all validation source modules under `src/vtz/` following the pattern `src/vtz/<component>.py`.
2. Name test files to mirror source files exactly: `tests/vtz/test_<component>.py`.
3. Use lowercase snake_case for all file names. Never use hyphens, camelCase, or uppercase letters in file or directory names.
4. Each validation concern (e.g., schema validation, status validation, field constraints) must reside in its own module file. Do not combine unrelated validators into a single file.
5. The package root `src/vtz/__init__.py` must re-export every public validator class and function so consumers can import directly from `vtz` without knowing internal module structure (mirrors FR-20 pattern).

---

### Class and Function Naming

6. Name validator classes as `<Subject>Validator` using PascalCase (e.g., `TaskFieldValidator`, `StatusTransitionValidator`).
7. Name validation functions as `validate_<subject>` using snake_case (e.g., `validate_status`, `validate_task_fields`).
8. Name custom exception classes as `<Subject>ValidationError` using PascalCase (e.g., `StatusValidationError`, `FieldValidationError`).
9. Prefix private/internal helper functions and methods with a single underscore (e.g., `_check_required_field`).
10. Never use generic names like `check`, `process`, or `run` for public validation functions. Every name must specify what is being validated.

---

### Error and Exception Patterns

11. Define a base exception `ValidationError` in `src/vtz/exceptions.py`. All validation-specific exceptions must inherit from it.
12. Every raised `ValidationError` must include a human-readable message that names the invalid field or value and explains why it failed.
13. Never return `True`/`False` from a validation function to signal failure. Raise a `ValidationError` subclass on invalid input; return `None` (implicitly) on success.
14. Catch and re-raise third-party or unexpected errors as `ValidationError` with the original exception chained using `raise ValidationError(...) from err`.
15. Never use bare `except:` or `except Exception:` without re-raising. Catch only the specific exception types the validator is designed to handle.

---

### Import and Module Organisation

16. Use only the Python standard library. No external/third-party dependencies are permitted anywhere in the validation subsystem (NFR-1).
17. Use absolute imports rooted at the package level (e.g., `from vtz.exceptions import ValidationError`). Never use relative imports.
18. All modules must be importable without side effects. Module-level code must contain only class definitions, function definitions, constant assignments, and imports—nothing else (NFR-2).
19. Import the `TaskStatus` enumeration (or equivalent status enum) and reference status values exclusively through it. Hard-coded status strings such as `"open"`, `"done"`, or `"in_progress"` are forbidden (NFR-4).
20. Group imports in this order, separated by blank lines: (a) standard library, (b) project-internal modules. There is no third-party group because external dependencies are prohibited.
21. The `__init__.py` of the `vtz` package must explicitly list all public names in an `__all__` variable.

---

### Comment and Documentation Rules

22. Every public class must have a docstring immediately after the class statement describing its purpose, the inputs it validates, and the exceptions it may raise (NFR-3).
23. Every public function must have a docstring immediately after the `def` statement describing its purpose, parameters, return value, and raised exceptions (NFR-3).
24. Use Google-style docstring format with `Args:`, `Returns:`, and `Raises:` sections.
25. Do not use inline comments to explain *what* code does. Use inline comments only to explain *why* a non-obvious decision was made.
26. Mark deliberate design trade-offs or deviations with `# DESIGN:` comments. Mark known limitations with `# TODO:` comments that include a tracking reference or explanation.

---

### Validation-Specific Patterns

27. Every validator must be stateless. Validator classes must not store mutable instance state between calls. Construct them, call them, discard them—or implement validators as pure functions.
28. Validate status values by comparing against the `TaskStatus` enumeration members. A status value that is not a member of the enum must raise `StatusValidationError`.
29. Implement a `validate_task` function (or `TaskValidator` class with a `validate` method) that orchestrates all field-level and status-level validations for a `Task` object in a single call.
30. Each atomic validation rule (e.g., "title must be a non-empty string", "status must be a valid enum member") must be implemented as its own function so it can be tested and composed independently.
31. When multiple fields are invalid, collect all `ValidationError` instances and raise a single aggregate `ValidationError` whose message lists every failure. Do not fail on the first invalid field and hide subsequent errors.
32. Status transition validation must accept `(current_status, new_status)` and enforce an explicit allow-list of valid transitions defined as a constant `dict[TaskStatus, set[TaskStatus]]`. Transitions not in the allow-list must raise `StatusValidationError`.
33. Never silently coerce, strip, or modify input data inside a validator. Validators inspect and reject; they never transform.
34. Write at least one test per validation rule in the corresponding `tests/vtz/test_<component>.py` file, covering: (a) a valid input that passes, (b) an invalid input that raises the expected `ValidationError` subclass, and (c) an edge case (e.g., empty string, `None`, boundary value).