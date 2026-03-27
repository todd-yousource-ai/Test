# Code Conventions

## File and Directory Naming

1. Place Validation subsystem source files under `src/` using a dedicated validation package path, and keep every module filename lowercase with underscores only.  
   - Valid: `src/validation/rules.py`, `src/validation/errors.py`
   - Invalid: `src/Validation/Rules.py`, `src/validation/validationRules.py`

2. Mirror Validation source modules in tests under `tests/validation/` using the exact component name prefixed with `test_`.  
   - If source file is `src/validation/rules.py`, test file must be `tests/validation/test_rules.py`.

3. Keep the package root file limited to public API re-exports. If the Validation subsystem exposes public classes or functions, re-export them from `src/validation/__init__.py`.

4. Do not encode implementation details in filenames. Name files by responsibility, not by usage context.  
   - Use `validator.py`, `result.py`, `exceptions.py`  
   - Do not use `misc.py`, `helpers.py`, `stuff.py`

5. Separate distinct responsibilities into separate modules.  
   - Put exception types in `exceptions.py` or `errors.py`.
   - Put validation result models in `result.py`.
   - Put rule logic in `rules.py` or a clearly scoped rule module.

## Class and Function Naming

1. Name classes in `PascalCase`.  
   - Valid: `Validator`, `ValidationResult`, `ValidationError`
   - Invalid: `validator`, `validation_result`

2. Name functions and methods in `snake_case`.  
   - Valid: `validate_input`, `is_valid`, `collect_errors`
   - Invalid: `validateInput`, `IsValid`

3. Name boolean-returning functions and methods with an `is_`, `has_`, or `can_` prefix when the return type is strictly boolean.  
   - Valid: `is_valid()`, `has_errors()`

4. Name exception classes with an `Error` suffix.  
   - Valid: `ValidationError`, `RuleConfigurationError`

5. Use singular names for classes representing one validator or one rule, and plural names only for collections or registries.  
   - Valid: `Rule`, `Validator`, `RuleSet`
   - Invalid: `Rules` for a single rule object

6. If the subsystem defines public API classes or functions, ensure each public name is stable enough to be re-exported from the package root without exposing internal module structure.

7. Do not use magic string status-like values inside validation flows. If the subsystem defines validation states, outcomes, or severities, represent them with an enumeration and reference the enum everywhere in code.

## Error and Exception Patterns

1. Define Validation-specific exceptions in a dedicated module such as `src/validation/exceptions.py` or `src/validation/errors.py`.

2. Raise typed exceptions, not generic `Exception`.  
   - Valid: `raise ValidationError("field 'id' is required")`
   - Invalid: `raise Exception("bad input")`

3. Use one exception type per failure category.  
   - Input data invalid: `ValidationError`
   - Invalid validator/rule setup: `RuleConfigurationError`
   - Do not reuse one broad exception for unrelated failures.

4. Make exception messages concrete and actionable by including the invalid field, rule, or value.  
   - Valid: `"field 'email' must not be empty"`
   - Invalid: `"validation failed"`

5. Do not trigger exceptions at module import time. All validation checks that can fail must run inside callable code paths only.

6. If validation returns structured failures instead of raising immediately, use a dedicated result type and reserve exceptions for programmer errors, invalid configuration, or unrecoverable misuse.

## Import and Module Organisation

1. Use only Python standard library imports. Do not add third-party packages anywhere in the Validation subsystem.

2. Keep all modules importable without side effects. At import time, modules may only define constants, enums, classes, and functions.  
   - Do not open files
   - Do not read environment variables for execution
   - Do not register runtime hooks
   - Do not run validation logic

3. Group imports in this order:
   1. Standard library imports
   2. Local package imports

4. Use explicit imports for public API symbols.  
   - In `src/validation/__init__.py`, re-export public names directly:
     ```python
     from .validator import Validator
     from .result import ValidationResult
     ```

5. Keep internal modules internal. Only names intended for consumers may be re-exported from the package root.

6. Avoid circular imports by placing shared enums, protocols, or common result types in a dedicated low-level module such as `types.py`, `enums.py`, or `result.py`.

7. Do not require consumers to know internal module structure for core Validation API types. If a class or function is part of the public API, it must be importable from the package root.

## Comment and Documentation Rules

1. Every public class must have a docstring describing its purpose.

2. Every public function must have a docstring describing its purpose.

3. Write docstrings as purpose-first descriptions.  
   - Valid: `"""Validate input data against the configured rules."""`
   - Invalid: `"""Function for validation."""`

4. Add comments only where code intent is not obvious from names and structure. Do not restate the code line-by-line.

5. When a validation rule depends on a specific invariant, document that invariant in the class or function docstring.

6. If a module defines public API types, add a module docstring summarizing the responsibility of that module.

7. Do not use comments as a substitute for proper naming. Rename unclear variables, functions, or classes instead of explaining poor names in comments.

## Validation-Specific Patterns

1. Represent validation outcomes, severities, or statuses with an `Enum` and use that enum throughout the subsystem.  
   - Valid: `ValidationStatus.VALID`
   - Invalid: `"valid"`

2. Centralize shared validation enums in a dedicated module so all rules and validators reference the same definitions.

3. Return structured validation data from validators when multiple issues can be reported. Use a dedicated result object such as `ValidationResult` instead of returning mixed tuples, ad hoc dicts, or string lists.

4. Store individual validation issues in a dedicated type when issue details matter. Include named attributes for at least the rule or field and the message when those concepts exist.

5. Keep rule evaluation pure where possible: a rule method should inspect provided input and return or record findings without mutating unrelated global or module state.

6. Pass all required context into validation functions explicitly through parameters. Do not rely on import-time configuration or hidden module-level state.

7. Separate rule definition from rule execution.  
   - Rule classes/functions define validation logic.
   - Validator classes/functions orchestrate applying rules and collecting results.

8. When validation supports multiple rules, process them through a collection owned by the validator or rule set object rather than hard-coding scattered checks across unrelated modules.

9. Use deterministic output ordering for collected validation issues. If multiple errors are returned, preserve rule application order or another explicitly defined stable order.

10. If a validation rule checks against a fixed set of allowed values, define those values once as an enum or named constant collection in module scope. Do not repeat literal values across functions.

11. Keep package-root exports aligned with the intended public Validation API. Any public validator, result type, or core exception intended for consumers must be re-exported from `src/validation/__init__.py`.

12. Do not expose internal-only helper functions as public API. Prefix internal helpers with `_` and keep them out of package-root re-exports.

13. Ensure every public Validation API type is usable by importing directly from the subsystem package root.  
   - Target usage:
     ```python
     from validation import Validator, ValidationResult
     ```