# Code Conventions

This document defines coding conventions derived from the provided TRD materials. It applies to the Python task management library and to all referenced architectural subsystems in the injected architecture context.

## File and Directory Naming

### Required `src/` Layout

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

### Directory Rules

- Use a `src/` layout for all Python packages.
- Package and directory names must be lowercase.
- Use singular or domain-clear names for top-level subpackages:
  - `models`
  - `storage`
  - `cli`
- Avoid abbreviated directory names unless the abbreviation is explicitly defined in the architecture context.
- New subsystem directories must use the canonical subsystem acronym exactly as defined, lowercased when used as a package path:
  - `cal`
  - `cpf`
  - `air`
  - `pee`
- If a subsystem has nested components, place them under its package:
  - `src/tasklib/cal/verifier.py`
  - `src/tasklib/cal/context.py`

### File Naming Rules

- Python module files must use `snake_case.py`.
- Prefer descriptive filenames over generic names.
- Allowed examples:
  - `task.py`
  - `task_store.py`
  - `memory_store.py`
  - `command_parser.py`
  - `verifier.py`
  - `policy_evaluator.py`
- Avoid catch-all names such as:
  - `utils.py`
  - `helpers.py`
  - `misc.py`

### Recommended Module Placement

- Data entities belong in `models/`.
- Persistence and repository logic belong in `storage/`.
- Command-line entry and argument handling belong in `cli/`.
- Policy enforcement components should live in a subsystem-specific package matching the subsystem acronym.

## Class and Function Naming

### Classes

- Use `PascalCase` for all classes.
- Name classes as nouns.
- Suffix by role when helpful:
  - `Task`
  - `TaskStore`
  - `MemoryTaskStore`
  - `CliRunner`
  - `PolicyEvaluator`
  - `CalVerifier`

### Functions and Methods

- Use `snake_case` for functions and methods.
- Use verb-led names for behavior:
  - `create_task`
  - `list_tasks`
  - `mark_complete`
  - `load_tasks`
  - `evaluate_policy`
  - `verify_context`
- Predicate functions should start with `is_`, `has_`, or `can_`:
  - `is_complete`
  - `has_permission`
  - `can_execute`

### Variables

- Use `snake_case`.
- Prefer explicit domain names over short names:
  - `task_id` instead of `id_value`
  - `policy_result` instead of `result`
  - `context_id` instead of `ctx`

### Constants

- Use `UPPER_SNAKE_CASE`.
- Names must be descriptive:
  - `DEFAULT_STORAGE_PATH`
  - `MAX_TASK_TITLE_LENGTH`

## Error and Exception Patterns

### Exception Naming

- Custom exceptions must use `PascalCase` and end with `Error`.
- Examples:
  - `TaskError`
  - `TaskNotFoundError`
  - `StorageError`
  - `PolicyEvaluationError`
  - `VerificationError`

### Exception Hierarchy

- Define narrow, domain-specific exceptions under a shared base exception per subsystem when needed.
- Example pattern:

```python
class TaskLibError(Exception):
    pass

class TaskNotFoundError(TaskLibError):
    pass
```

### Raising Errors

- Raise specific exceptions, not generic `Exception`.
- Error messages must be concise, actionable, and domain-specific.
- Include identifiers where useful:
  - `"Task not found: {task_id}"`
  - `"Policy evaluation failed for context_id={context_id}"`

### Handling Errors

- Storage layers should translate low-level failures into storage-domain exceptions.
- CLI layers should catch domain exceptions and present user-facing output cleanly.
- Enforcement or verification subsystems should fail closed when policy evaluation cannot complete.

## Per-Subsystem Naming Rules

## Task Library

### Models

- Entity classes must be singular nouns:
  - `Task`
- Model modules should match the entity:
  - `task.py`
- Data fields should use explicit names:
  - `task_id`
  - `title`
  - `description`
  - `completed`

### Storage

- Storage abstractions should be named by role:
  - `TaskStore`
  - `TaskRepository`
- Concrete implementations should include backend type:
  - `MemoryTaskStore`
  - `FileTaskStore`
- Storage methods should reflect CRUD intent:
  - `add_task`
  - `get_task`
  - `list_tasks`
  - `delete_task`
  - `update_task`

### CLI

- CLI command handlers should use command verbs:
  - `add_command`
  - `list_command`
  - `complete_command`
- Parser-building functions should be explicit:
  - `build_parser`
  - `register_commands`
- Entry-point functions should be named:
  - `main`

## CAL — Conversation Abstraction Layer

- Use the acronym `CAL` in class names and `cal` in module/package names.
- Components should be named by enforcement role:
  - `CalPolicyEvaluator`
  - `CalRequest`
  - `CalDecision`
  - `CalVerifier`
- Functions should reflect gating behavior:
  - `evaluate_action`
  - `verify_request`
  - `enforce_policy`

## CPF — Conversation Plane Filter

- Use `CPF` in class names and `cpf` in modules.
- Filter-related classes should use nouns:
  - `CpfFilter`
  - `CpfRule`
  - `CpfDecision`
- Functions should describe filtering operations:
  - `filter_action`
  - `apply_rule`
  - `reject_request`

## AIR

- Preserve the acronym as defined in class names and use lowercase in file paths.
- Prefer names tied to representation or runtime records:
  - `AirRecord`
  - `AirIdentity`
  - `AirResolver`
- Behavior names should be explicit:
  - `resolve_identity`
  - `load_record`
  - `validate_record`

## CTX-ID

- In Python identifiers, convert `CTX-ID` to `CtxId` for class names and `ctx_id` for variables, fields, and modules.
- Examples:
  - `CtxId`
  - `CtxIdGenerator`
  - `ctx_id.py`
  - `current_ctx_id`
- Never use a hyphen in Python identifiers.

## PEE

- Use `PEE` in class names and `pee` in modules.
- Names should center on evaluation and execution control:
  - `PeeEngine`
  - `PeePolicy`
  - `PeeResult`
- Function names should be action-oriented:
  - `evaluate_policy`
  - `execute_check`
  - `build_result`

## TrustFlow / SIS

- When a subsystem includes a slash in documentation naming, split into separate code-safe identifiers.
- Use:
  - `TrustFlow` / `trustflow`
  - `Sis` / `sis`
- If implemented together, combine explicitly:
  - `TrustflowSisBridge`
  - `trustflow_sis_bridge.py`
- Do not use `/` in filenames, package names, or identifiers.

## CAL Verifier Cluster

- Treat this as a named component under the CAL subsystem.
- Use names such as:
  - `CalVerifierCluster`
  - `ClusterVerifierNode`
  - `VerifierQuorum`
- Module examples:
  - `verifier_cluster.py`
  - `verifier_node.py`

## General Naming Rules for Documented Acronyms

- Preserve documented acronyms in class names when they are canonical subsystem identifiers.
- Use lowercase package/module names for those acronyms.
- For mixed-format identifiers from documentation:
  - Replace hyphens with underscores in variables and filenames.
  - Convert to `PascalCase` in class names.
  - Remove punctuation that is invalid in Python identifiers.

## Additional Code Patterns

### Imports

- Use absolute imports within the package.
- Imports must resolve from previously merged package structure.
- Example:

```python
from tasklib.models.task import Task
from tasklib.storage.task_store import TaskStore
```

### Public API Exposure

- Re-export intentionally public symbols through package `__init__.py` only when needed.
- Do not expose internal helpers as part of the package API by default.

### Separation of Concerns

- Models must not contain CLI logic.
- CLI code must not implement storage directly.
- Storage must not depend on CLI packages.
- Enforcement and verification components must remain isolated by subsystem boundary where possible.

### Documentation Alignment

- Names used in code must align with names used in README, architecture, and API reference.
- If documentation uses a canonical subsystem acronym, code must preserve that acronym consistently using Python-safe formatting rules.