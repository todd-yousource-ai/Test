# Code Conventions

This document defines coding conventions derived from the provided TRD material. It covers the task management library and the architecture context subsystems explicitly present in the source documents. All conventions below are normative unless a TRD for a specific subsystem overrides them.

## File and Directory Naming

### Repository Layout

Use a `src/` layout for Python code.

```text
repo-root/
├─ src/
│  └─ tasklib/
│     ├─ __init__.py
│     ├─ models/
│     │  ├─ __init__.py
│     │  └─ task.py
│     ├─ storage/
│     │  ├─ __init__.py
│     │  └─ memory.py
│     └─ cli/
│        ├─ __init__.py
│        └─ main.py
├─ tests/
├─ README.md
├─ ARCHITECTURE.md
└─ API.md
```

### Directory Rules

- Python packages must live under `src/`.
- Package and module names must be lowercase.
- Use singular directory names for tightly scoped domain modules when they represent a single concept:
  - `models`
  - `storage`
  - `cli`
- Keep subpackage depth shallow unless a TRD explicitly requires additional nesting.
- Documentation files at repository root must use uppercase names when they are top-level canonical docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `API.md`

### File Naming Rules

- Python source files: `snake_case.py`
- Test files: `test_<unit>.py`
- Package entrypoints:
  - library root: `__init__.py`
  - CLI entry module: `main.py`
- One primary domain concept per module when practical.
- Avoid overloaded filenames such as `utils.py`, `helpers.py`, or `common.py` unless the TRD explicitly calls for them.

### Exact `src/` Layout Expectations

The minimum expected layout for the task management library is:

```text
src/
└─ tasklib/
   ├─ __init__.py
   ├─ models/
   │  ├─ __init__.py
   │  └─ task.py
   ├─ storage/
   │  ├─ __init__.py
   │  └─ memory.py
   └─ cli/
      ├─ __init__.py
      └─ main.py
```

If architecture-context subsystems are implemented in code, organize them as peer subpackages under a root package, for example:

```text
src/
└─ <root_package>/
   ├─ cal/
   ├─ cpf/
   ├─ air/
   ├─ ctx_id/
   ├─ pee/
   ├─ trustflow/
   ├─ sis/
   └─ verifier/
```

Use this only for subsystems actually implemented by the corresponding TRDs.

## Class and Function Naming

### General Python Naming

Follow standard Python naming:

- Classes: `PascalCase`
- Functions: `snake_case`
- Methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal attributes and functions: prefix with `_`

### Class Naming Rules

Use nouns for domain objects and services.

Examples:

- `Task`
- `TaskRepository`
- `InMemoryTaskStore`
- `TaskCli`
- `PolicyEvaluator`
- `ConversationContext`
- `VerifierClusterClient`

Avoid ambiguous names like:

- `Manager`
- `Processor`
- `Handler`

unless paired with a strong domain qualifier, for example:

- `TaskStorageHandler`
- `PolicyDecisionProcessor`

### Function Naming Rules

Use verb-first names for behavior.

Examples:

- `create_task`
- `list_tasks`
- `get_task`
- `delete_task`
- `evaluate_policy`
- `verify_identity`
- `resolve_context_id`

Boolean-returning functions should read as predicates:

- `is_complete`
- `has_access`
- `can_execute`
- `is_policy_compliant`

### Constructor and Factory Naming

- Use `__init__` for straightforward construction.
- Use `from_...` classmethods for alternate constructors:
  - `from_dict`
  - `from_env`
  - `from_config`

### CLI Naming

CLI command functions must map directly to user actions.

Examples:

- `add_task_command`
- `list_tasks_command`
- `complete_task_command`

If using a single dispatch function, name it:

- `main`
- `run`

## Error and Exception Patterns

### Exception Class Naming

Custom exception names must end with `Error`.

Examples:

- `TaskNotFoundError`
- `DuplicateTaskError`
- `StorageError`
- `PolicyEvaluationError`
- `VerificationError`

### Exception Hierarchy

Define narrow, domain-specific base exceptions per subsystem when needed.

Example:

```python
class TaskLibError(Exception):
    pass

class TaskNotFoundError(TaskLibError):
    pass

class StorageError(TaskLibError):
    pass
```

For architecture subsystems, prefer subsystem-specific bases:

- `CalError`
- `CpfError`
- `AirError`
- `CtxIdError`
- `PeeError`
- `TrustFlowError`
- `SisError`
- `VerifierError`

### Error Handling Rules

- Raise specific exceptions, not generic `Exception`.
- Preserve original exceptions with `raise ... from exc` when wrapping lower-level failures.
- Validate inputs at subsystem boundaries.
- Fail fast on invalid state, malformed identifiers, or policy violations.
- CLI layers may convert domain exceptions into user-facing messages, but storage and model layers must raise structured exceptions.

### Error Message Style

Error messages should be:

- concise
- actionable
- domain-specific
- lowercase unless starting with an identifier or class name

Examples:

- `task with id 't-123' was not found`
- `policy evaluation denied requested action`
- `context id is missing or malformed`

Avoid:

- vague text like `something went wrong`
- implementation-leaking messages unless debugging context is explicitly needed

## Per-Subsystem Naming Rules

## Task Management Library

### Package Naming

- Root package name: `tasklib`
- Subpackages:
  - `models`
  - `storage`
  - `cli`

### Model Naming

Model classes must use singular nouns.

Examples:

- `Task`

Model modules should match the primary entity:

- `task.py` contains `Task`

Field names should be explicit and stable. Preferred examples:

- `id`
- `title`
- `description`
- `completed`

Use `completed` rather than variants like `is_done` unless the TRD defines a different field.

### Storage Naming

Storage implementations must indicate backend and responsibility.

Examples:

- `InMemoryTaskStore`
- `TaskRepository`

Module names should reflect backend or role:

- `memory.py`
- `repository.py`

Use `store` for simple persistence containers and `repository` for query-oriented abstractions.

### CLI Naming

CLI modules must reflect executable entrypoint roles.

Examples:

- `main.py`
- `commands.py`

CLI functions should include the command intent:

- `add_task`
- `list_tasks`
- `remove_task`

If command parser callbacks are separate from domain functions, suffix with `_command`.

## CAL — Conversation Abstraction Layer

### Package and Module Naming

- Package: `cal`
- Use `conversation_` and `policy_` prefixes for CAL-specific modules when naming needs extra clarity.

Examples:

- `policy_engine.py`
- `conversation_gate.py`
- `action_evaluator.py`

### Type Naming

Names in this subsystem should reflect enforcement and evaluation roles.

Examples:

- `ConversationAbstractionLayer`
- `PolicyDecision`
- `ActionRequest`
- `EvaluationResult`

### Function Naming

Functions should communicate gated execution semantics.

Examples:

- `evaluate_action`
- `authorize_request`
- `enforce_policy`
- `reject_action`

## CPF — Conversation Plane Filter

### Package and Module Naming

- Package: `cpf`

Use `filter` terminology consistently.

Examples:

- `filter_chain.py`
- `filter_rules.py`

### Type Naming

Examples:

- `ConversationPlaneFilter`
- `FilterRule`
- `FilterDecision`

### Function Naming

Examples:

- `apply_filter`
- `filter_action`
- `build_filter_context`

## AIR

### Package and Module Naming

- Package: `air`

If the full expansion is defined in future TRDs, use that exact term in public class names. Until then, prefer the acronym in code to avoid speculative naming.

Examples:

- `air_client.py`
- `air_record.py`

### Type Naming

Examples:

- `AirRecord`
- `AirRequest`
- `AirEvaluator`

### Function Naming

Examples:

- `create_air_record`
- `load_air_record`
- `evaluate_air_request`

## CTX-ID

### Package and Module Naming

Because hyphens are invalid in Python package names, represent `CTX-ID` as:

- package: `ctx_id`

Examples:

- `ctx_id.py`
- `resolver.py`
- `parser.py`

### Type Naming

Expand the acronym in class names only when the authoritative term is known. Otherwise use a stable mixed form:

- `ContextId`
- `ContextIdResolver`
- `ContextIdParser`

### Function Naming

Examples:

- `parse_context_id`
- `resolve_context_id`
- `validate_context_id`

## PEE

### Package and Module Naming

- Package: `pee`

Use `policy` or `execution` in module names if additional clarity is needed.

Examples:

- `policy_executor.py`
- `execution_context.py`

### Type Naming

Examples:

- `PeeEngine`
- `ExecutionContext`
- `PolicyExecutionResult`

### Function Naming

Examples:

- `execute_policy`
- `build_execution_context`
- `record_execution_result`

## TrustFlow

### Package and Module Naming

Represent this subsystem as:

- package: `trustflow`

Do not split the name into `trust_flow` unless a TRD explicitly requires snake-case expansion for public package naming.

Examples:

- `trustflow_graph.py`
- `trustflow_service.py`

### Type Naming

Examples:

- `TrustFlowService`
- `TrustFlowRecord`
- `TrustFlowEvaluator`

### Function Naming

Examples:

- `build_trustflow`
- `evaluate_trustflow`
- `persist_trustflow`

## SIS

### Package and Module Naming

- Package: `sis`

Until expanded by a TRD, keep acronym-based naming.

Examples:

- `sis_client.py`
- `sis_registry.py`

### Type Naming

Examples:

- `SisClient`
- `SisRecord`
- `SisRegistry`

### Function Naming

Examples:

- `register_sis_record`
- `load_sis_record`
- `verify_sis_state`

## CAL Verifier Cluster

### Package and Module Naming

Represent the verifier cluster as either:

- `verifier`
- `verifier_cluster`

Prefer `verifier_cluster` when the code models distributed coordination explicitly.

Examples:

- `verifier_cluster.py`
- `cluster_client.py`
- `node_registry.py`

### Type Naming

Examples:

- `VerifierCluster`
- `VerifierNode`
- `VerifierClusterClient`

### Function Naming

Examples:

- `verify_request`
- `select_verifier_node`
- `broadcast_verification`
- `collect_verification_results`

## Cross-Subsystem Conventions

### Acronyms in Names

- For package and module names, use lowercase snake case:
  - `ctx_id`
  - `verifier_cluster`
- For class names, preserve recognizable acronym readability:
  - `CtxIdResolver`
  - `SisRegistry`
  - `PeeEngine`
- Do not invent expanded names for acronyms unless the TRD defines them.

### Boundary Naming

Names at subsystem boundaries must describe the exchanged concept, not the implementation.

Prefer:

- `ActionRequest`
- `PolicyDecision`
- `VerificationResult`

Avoid:

- `Payload`
- `DataBlob`
- `InfoObject`

### Import Conventions

- Use absolute imports within `src/` packages.
- Import from previously defined subpackages by their package path.
- Avoid circular imports by keeping model types in `models` and storage abstractions in `storage`.

Example:

```python
from tasklib.models.task import Task
from tasklib.storage.memory import InMemoryTaskStore
```

### Test Naming

Mirror package structure in `tests/`.

Examples:

```text
tests/
├─ test_task.py
├─ storage/
│  └─ test_memory.py
└─ cli/
   └─ test_main.py
```

Test function names must describe behavior:

- `test_create_task_sets_completed_false_by_default`
- `test_list_tasks_returns_all_stored_tasks`
- `test_evaluate_policy_denies_unauthorized_action`

### Documentation Naming

Canonical docs required by the TRD should use these names:

- `README.md`
- `ARCHITECTURE.md`
- `API.md`

Section titles inside docs should use plain domain naming aligned with code:

- `Task Model`
- `Storage Layer`
- `CLI`
- `Conversation Abstraction Layer`
- `Verifier Cluster`

## Prohibited Patterns

- No hardcoded product names in code, docs, comments, or identifiers.
- No speculative expansion of undefined acronyms.
- No mixed naming styles for the same subsystem.
- No generic catch-all modules like `misc.py`.
- No generic exception raising where a domain exception is appropriate.
- No hyphens in Python package or module names.
- No abbreviations in public API names unless the TRD uses the abbreviation as the authoritative subsystem name.