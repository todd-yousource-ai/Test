# Code Conventions

## File and Directory Naming

1. Place all Validation subsystem source files under `src/` using a single lowercase module name per file.
   - Valid: `src/validation/rules.py`, `src/validation/errors.py`
   - Invalid: `src/validation/ValidationRules.py`, `src/validation/rule-set.py`

2. Name every Python source file with lowercase snake_case only.
   - Use letters, numbers, and underscores only.
   - Do not use hyphens, spaces, or mixed case in filenames.

3. Mirror the source layout in tests under `tests/validation/`.
   - If the source file is `src/validation/rules.py`, the test file must be `tests/validation/test_rules.py`.
   - If the source file is `src/validation/engine.py`, the test file must be `tests/validation/test_engine.py`.

4. Keep the package root reserved for public API re-exports only.
   - Re-export Validation subsystem public classes and functions from `src/validation/__init__.py`.
   - Do not implement validation logic directly in `__init__.py`.

5. Expose public Validation API types at the package root so callers do not need internal module paths.
   - Consumers should be able to import public symbols as `from validation import Validator` rather than `from validation.engine import Validator`.

6. Do not create files whose only purpose is to execute setup logic at import time.
   - Module files may define constants, classes, functions, and exceptions.
   - Module files must not perform registration, I/O, environment reads with side effects, or runtime validation when imported.

## Class and Function Naming

1. Name classes with PascalCase.
   - Valid: `Validator`, `ValidationError`, `RuleSet`
   - Invalid: `validator`, `validation_error`, `Rule_set`

2. Name functions and methods with snake_case.
   - Valid: `validate_value`, `run_rules`, `is_valid`
   - Invalid: `validateValue`, `RunRules`

3. Name module-level constants with UPPER_SNAKE_CASE.
   - Valid: `DEFAULT_MESSAGE`, `MAX_ERRORS`
   - Invalid: `defaultMessage`, `MaxErrors`

4. Suffix exception classes with `Error`.
   - Valid: `ValidationError`, `RuleConfigurationError`
   - Invalid: `ValidationException`, `InvalidRule`

5. Prefix boolean-returning helpers with `is_`, `has_`, or `can_` when their purpose is predicate evaluation.
   - Valid: `is_valid_identifier`, `has_required_fields`
   - Invalid: `valid_identifier`, `required_fields_present`

6. Use names that encode validation role explicitly.
   - Use `Validator` for objects that execute validation.
   - Use `Rule` for objects or functions that represent a single validation rule.
   - Use `ValidationResult` for returned structured validation outcomes.
   - Use `ValidationError` for raised exceptions and per-failure objects only when they represent errors.

7. Public API names must be stable and root-exported.
   - If a class or function is intended for external use, define it in an internal module and re-export it from `validation.__init__`.

## Error and Exception Patterns

1. Raise dedicated exception types for Validation subsystem failures.
   - Define subsystem-specific exceptions in a dedicated module such as `src/validation/errors.py`.
   - Do not raise generic `Exception` from validation code.

2. Use `ValueError` only for simple internal argument contract violations when no subsystem-specific exception adds clarity.
   - Prefer `ValidationError` for actual validation failures exposed by the subsystem.

3. Keep exception messages deterministic and actionable.
   - Include the failing field, rule, or value category.
   - Do not include nondeterministic text such as memory addresses or object reprs unless required.

4. Separate validation results from exceptional failures.
   - Return structured validation outcomes for expected invalid input when the API is designed to collect failures.
   - Raise exceptions only for misuse, invalid configuration, or unrecoverable validation execution errors.

5. Do not use magic strings for status-like values in validation flow.
   - Represent statuses with an enumeration.
   - Reference the enumeration everywhere in the codebase instead of comparing raw strings.

6. If the subsystem defines a validation status enum, compare and assign only enum members.
   - Valid: `if result.status is ValidationStatus.INVALID:`
   - Invalid: `if result.status == "invalid":`

## Import and Module Organisation

1. Use only Python standard library imports.
   - Do not add third-party packages to implement validation behavior, typing helpers, or utilities.

2. Keep every module importable with zero side effects.
   - Do not open files, read stdin, write logs, mutate global registries, or execute validation at import time.

3. Organize imports in three groups, separated by one blank line:
   1. Standard library imports
   2. Internal package imports
   3. Local relative imports, if used

4. Prefer absolute imports within the Validation subsystem when importing public internal modules.
   - Valid: `from validation.errors import ValidationError`
   - Use relative imports only when they improve clarity within tightly scoped package internals.

5. Do not import from test modules or from application entrypoints inside validation modules.

6. Keep cyclic imports out of the public API path.
   - If two modules need shared types, extract those types into a separate module such as `types.py`, `models.py`, or `errors.py`.

7. Package root exports must be explicit.
   - In `src/validation/__init__.py`, import and re-export each public symbol intentionally.
   - Do not use wildcard imports to assemble the public API.

## Comment and Documentation Rules

1. Add a docstring to every public class and every public function.
   - The docstring must describe the purpose of the class or function.
   - This applies to all symbols re-exported from `validation.__init__`.

2. Write docstrings as direct purpose statements.
   - Valid: `"""Validate a mapping against the configured rules."""`
   - Invalid: `"""This function does validation stuff."""`

3. Do not use comments to restate obvious code.
   - Remove comments like `# increment counter` above `count += 1`.

4. Use comments only for one of these cases:
   - Explaining a non-obvious validation rule
   - Explaining why a standard-library-only implementation was chosen
   - Documenting an invariant that must be preserved

5. Keep inline comments on the line they explain and make them specific.
   - Valid: `# Preserve declaration order so error output is deterministic.`
   - Invalid: `# important`

6. Document any public enum used for validation statuses with a docstring that defines what each status represents.

## Validation-Specific Patterns

1. Centralize shared validation statuses in a single enumeration type.
   - Define statuses such as valid/invalid/pending only as enum members if the subsystem requires them.
   - Never duplicate the same status values as string literals in validators, results, tests, or error handling.

2. Represent validation output consistently.
   - If validation returns results instead of raising immediately, use a dedicated result type such as `ValidationResult`.
   - Include status as an enum member, not a string.

3. Keep rule evaluation pure when possible.
   - A rule function or method should derive its result from input arguments only.
   - Do not perform network access, file access, or process-level mutation inside a validation rule.

4. Make validation ordering deterministic.
   - Apply rules in a stable, defined order.
   - Do not depend on unordered iteration when collecting errors or generating result summaries.

5. Separate rule definition from rule execution.
   - Store reusable rule logic in rule-focused modules such as `rules.py`.
   - Keep orchestration logic in validator-focused modules such as `engine.py` or `validator.py`.

6. Use dedicated types for reusable validation concepts.
   - Put exception types in `errors.py`.
   - Put enum types in `enums.py` or `status.py`.
   - Put public result models in `models.py` or `results.py`.

7. Keep validation APIs explicit about failure mode.
   - Methods that raise on invalid input should use names such as `validate_or_raise`.
   - Methods that return structured outcomes should use names such as `validate` or `check`.

8. Ensure tests assert enum usage, not raw string status values.
   - Valid: `assert result.status is ValidationStatus.VALID`
   - Invalid: `assert result.status == "valid"`

9. If a validator supports multiple rules, pass rules as explicit constructor or function arguments rather than implicit module registration.
   - This preserves import-time side-effect freedom.

10. Do not hide public validation symbols behind internal module knowledge.
    - If `Validator`, `ValidationResult`, or `ValidationStatus` are public, re-export them from `validation.__init__.py`.