# Code Conventions

This document defines coding conventions derived from the provided TRD material. It covers the task management library and the architecture context subsystems referenced in the TRDs. All conventions below are normative unless explicitly marked as optional.

---

## File and Directory Naming (exact `src/` layout)

### Repository Layout

Use a `src/` layout for Python packages.

```text
src/
  tasklib/
    __init__.py
    models/
      __init__.py
    storage/
      __init__.py
    cli/
      __init__.py
```

### Required Package Structure

The dependency chain in the TRD must be reflected in package structure:

```text
docs -> scaffold -> model -> storage -> cli
```

Code modules must be organized so that later stages import from earlier merged stages cleanly and locally.

Recommended expanded layout:

```text
src/
  tasklib/
    __init__.py
    models/
      __init__.py
      task.py
    storage/
      __init__.py
      memory.py
    cli/
      __init__.py
      main.py
```

If architecture-context subsystems are implemented in this repository, place them under distinct subpackages:

```text
src/
  tasklib/
    cal/
      __init__.py
    cpf/
      __init__.py
    air/
      __init__.py
    ctx_id/
      __init__.py
    pee/
      __init__.py
    trustflow/
      __init__.py
    sis/
      __init__.py
    verifier/
      __init__.py
```

### File Naming Rules

- Use lowercase snake_case for all Python filenames.
- One primary concept per file.
- Do not use CamelCase filenames.
- Avoid abbreviations unless the abbreviation is defined in the TRD and is itself the subsystem name.

Examples:

- `task.py`
- `memory.py`
- `main.py`
- `policy_evaluator.py`
- `conversation_filter.py`

### Directory Naming Rules

- Use lowercase snake_case for package directories.
- Acronym-based subsystem directories should be normalized to lowercase where used as package paths.

Examples:

- `cal/`
- `cpf/`
- `air/`
- `ctx_id/`
- `pee/`
- `trustflow/`
- `sis/`

### `__init__.py` Conventions

- Every package directory must include `__init__.py`.
- Keep `__init__.py` minimal.
- Export only stable package-level symbols.
- Do not place business logic in `__init__.py`.

### Documentation File Naming

Documentation files should use uppercase canonical names when they represent top-level project docs explicitly called out in the TRD:

- `README.md`
- `ARCHITECTURE.md`
- `API_REFERENCE.md`

If additional docs are added, use uppercase snake case for top-level canonical documents.

---

## Class and Function Naming

### General Naming Style

- Classes: `PascalCase`
- Functions: `snake_case`
- Methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Module-private helpers: prefix with `_`

Examples:

```python
class Task:
    pass

def create_task():
    pass

DEFAULT_STATUS = "pending"

def _validate_title():
    pass
```

### Class Naming Rules

Use nouns for classes.

Examples:

- `Task`
- `TaskRepository`
- `InMemoryTaskStorage`
- `CliApplication`
- `PolicyEvaluator`
- `ConversationFilter`
- `VerifierCluster`

Avoid:

- `TaskManagerClass`
- `DoTask`
- `StorageThing`

### Function Naming Rules

Use verbs or verb phrases for functions.

Examples:

- `create_task`
- `list_tasks`
- `delete_task`
- `load_tasks`
- `evaluate_policy`
- `verify_conversation`
- `resolve_context_id`

Boolean-returning functions should read clearly as predicates:

- `is_completed`
- `has_policy_violation`
- `can_execute_action`

### Method Naming Rules

Instance methods should describe the operation from the object’s responsibility.

Examples:

```python
task.mark_completed()
repository.save(task)
repository.get_by_id(task_id)
filter.evaluate(action)
```

### Factory and Constructor Patterns

Where alternate construction is needed, use class methods with clear names:

- `from_dict`
- `from_json`
- `from_config`

Do not create vague factories such as:

- `build`
- `make_object`

unless the abstraction truly warrants it.

### CLI Naming Rules

CLI entry functions should be explicit:

- `main`
- `run`
- `parse_args`

Command handler functions should be action-oriented:

- `handle_create`
- `handle_list`
- `handle_delete`

---

## Error and Exception Patterns

### General Exception Rules

- Raise specific exceptions, not bare `Exception`.
- Prefer built-in exceptions when sufficient.
- Define custom exceptions only for domain-relevant failures.
- Keep exception names in `PascalCase` and end with `Error`.

Examples:

- `ValueError`
- `KeyError`
- `TaskNotFoundError`
- `PolicyEvaluationError`
- `VerificationError`

### Task Library Exception Pattern

Domain exceptions for the task library should live close to the domain package or in a shared exceptions module if one is added later.

Recommended names:

- `TaskError`
- `TaskValidationError`
- `TaskNotFoundError`
- `StorageError`

Suggested hierarchy:

```python
class TaskError(Exception):
    pass

class TaskValidationError(TaskError):
    pass

class TaskNotFoundError(TaskError):
    pass

class StorageError(TaskError):
    pass
```

### Architecture Subsystem Exception Pattern

For architecture-context subsystems, use subsystem-scoped exceptions.

Examples:

- `CalError`
- `CpfError`
- `AirError`
- `ContextIdentityError`
- `PolicyEnforcementError`
- `TrustFlowError`
- `SisError`
- `VerifierError`

### Raise Patterns

- Raise early on invalid input.
- Validate external inputs at module boundaries.
- Include actionable context in exception messages.
- Do not leak unrelated internal state in messages.

Good:

```python
raise TaskValidationError("task title must not be empty")
```

Avoid:

```python
raise Exception("bad task")
```

### Catch Patterns

- Catch exceptions only when adding context, translating errors, or handling expected control flow.
- Do not suppress errors silently.
- Do not use broad `except:` blocks.
- If translating exceptions, preserve the cause with `from`.

Example:

```python
try:
    data = storage.load(task_id)
except KeyError as exc:
    raise TaskNotFoundError(f"task '{task_id}' was not found") from exc
```

### CLI Error Handling

CLI code should convert domain exceptions into user-facing messages and non-zero exits.

- Domain layer raises structured exceptions.
- CLI layer formats messages for humans.
- Avoid embedding `sys.exit` deep in domain or storage layers.

### Validation Patterns

- Validate constructor and function inputs consistently.
- Prefer deterministic validation over implicit coercion.
- Reject invalid states rather than carrying them forward.

Examples:

- Empty title -> `TaskValidationError`
- Unknown task id -> `TaskNotFoundError`
- Unsupported action in policy layer -> `PolicyEvaluationError`

---

## Per-Subsystem Naming Rules

### Task Management Library

#### Package Names

- `models`
- `storage`
- `cli`

#### Model Naming

Model classes should be singular nouns.

Examples:

- `Task`

Model fields should be descriptive and stable.

Examples:

- `task_id`
- `title`
- `description`
- `completed`

Avoid generic names such as:

- `id`
- `name`
- `flag`

unless local scope makes them unambiguous.

#### Storage Naming

Storage classes should indicate implementation and role.

Examples:

- `InMemoryTaskStorage`
- `TaskRepository`

Storage functions should use persistence verbs:

- `save`
- `load`
- `delete`
- `list_all`
- `get_by_id`

#### CLI Naming

CLI modules and functions should reflect command intent.

Examples:

- `main.py`
- `parse_args`
- `handle_create`
- `handle_list`

---

### CAL — Conversation Abstraction Layer

Use `cal` as the package name.

#### Class Naming

Names should reflect enforcement and evaluation responsibilities.

Examples:

- `ConversationAbstractionLayer`
- `CalPolicyEvaluator`
- `CalRequest`
- `CalDecision`

#### Function Naming

Examples:

- `evaluate_action`
- `enforce_policy`
- `verify_request`
- `route_for_evaluation`

#### Data Naming

Prefer terms explicitly grounded in the architecture context:

- `conversation_id`
- `context_id`
- `action_request`
- `policy_decision`
- `trust_state`

Avoid application-layer names that obscure the CAL role.

---

### CPF — Conversation Plane Filter

Use `cpf` as the package name.

#### Class Naming

Examples:

- `ConversationPlaneFilter`
- `CpfRule`
- `CpfDecision`
- `CpfEvaluator`

#### Function Naming

Examples:

- `filter_action`
- `apply_rules`
- `reject_request`
- `allow_request`

Keep naming centered on filtering, rule application, and decisions.

---

### AIR

Use `air` as the package name.

Because the TRD provides only the subsystem acronym and no expanded definition, preserve the acronym in code-level names rather than inventing a long-form expansion.

#### Class Naming

Examples:

- `AirRecord`
- `AirEvaluator`
- `AirClient`

#### Function Naming

Examples:

- `create_air_record`
- `load_air_record`
- `evaluate_air_input`

---

### CTX-ID

Use `ctx_id` as the package name.

#### Class Naming

Examples:

- `ContextIdentity`
- `ContextIdResolver`
- `ContextIdRecord`

#### Function Naming

Examples:

- `resolve_context_id`
- `parse_context_id`
- `validate_context_id`

Do not use hyphens in Python identifiers.

---

### PEE

Use `pee` as the package name.

Because only the acronym is provided, preserve it consistently.

#### Class Naming

Examples:

- `PeeEngine`
- `PeePolicy`
- `PeeDecision`

#### Function Naming

Examples:

- `evaluate_policy`
- `enforce_execution`
- `compute_decision`

---

### TrustFlow / SIS

Use separate packages:

- `trustflow`
- `sis`

#### TrustFlow Naming

Examples:

- `TrustFlowState`
- `TrustFlowEvaluator`
- `advance_trustflow`

#### SIS Naming

Examples:

- `SisAdapter`
- `SisRecord`
- `sync_sis_state`

If these are implemented as a tightly coupled subsystem, keep names explicit about which side they belong to.

---

### CAL Verifier Cluster

Use `verifier` as the package name unless a more specific package path is required by implementation.

#### Class Naming

Examples:

- `CalVerifier`
- `VerifierNode`
- `VerifierCluster`
- `VerificationResult`

#### Function Naming

Examples:

- `verify_conversation`
- `verify_action`
- `aggregate_results`

Names should clearly convey verification, node coordination, and result aggregation.

---

## Additional Cross-Cutting Conventions

### Import Conventions

- Use absolute imports from the package root.
- Keep imports deterministic and dependency-order safe.
- Do not rely on implicit relative path behavior.

Example:

```python
from tasklib.models.task import Task
from tasklib.storage.memory import InMemoryTaskStorage
```

### Dependency Direction

Maintain the TRD dependency chain:

- `models` must not depend on `storage` or `cli`
- `storage` may depend on `models`
- `cli` may depend on `models` and `storage`

For architecture-context packages:

- lower-level policy or identity primitives should not depend on CLI code
- enforcement and verifier packages may depend on primitive data structures, not vice versa

### API Surface Discipline

- Keep public APIs small and explicit.
- Prefix internal helpers with `_`.
- Export stable interfaces intentionally.
- Avoid wildcard imports.

### Data Model Conventions

- Prefer explicit fields over loosely structured dictionaries.
- If serialization helpers are needed, use explicit methods such as `to_dict` and `from_dict`.
- Keep field names snake_case in Python representations.

### Naming Stability

Because this repository is intended to validate multi-step merge and import behavior:

- do not rename packages casually
- do not move public symbols between modules without updating all downstream imports
- preserve import paths once introduced unless a coordinated refactor is performed

### Abbreviation Policy

- Use abbreviations only when they are canonical in the TRD.
- For known subsystem acronyms, preserve acronym identity.
- For non-canonical concepts, spell names out for clarity.

Examples:

- Good: `CalDecision`, `CpfRule`, `ContextIdResolver`
- Avoid: `Mgr`, `Cfg`, `Obj`, `Util`

### Utility Module Rule

Do not create catch-all modules such as:

- `utils.py`
- `helpers.py`
- `common.py`

unless the contents are narrowly scoped and cohesively named. Prefer specific modules like:

- `validation.py`
- `serialization.py`
- `policy_rules.py`

---

## Summary

All code should follow these core rules:

- `src/`-based package structure
- lowercase snake_case files and directories
- `PascalCase` classes, `snake_case` functions
- specific exceptions ending in `Error`
- subsystem names preserved exactly where defined by the TRD
- dependency flow aligned with the documented merge chain
- stable imports and explicit package boundaries