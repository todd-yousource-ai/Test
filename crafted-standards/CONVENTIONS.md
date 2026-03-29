# Code Conventions

This document defines coding conventions derived from the provided TRD material. It applies to the validation task management library and to the architecture subsystems explicitly named in the architecture context.

## File and Directory Naming (exact `src/` layout)

### Required Python package layout

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

### Directory rules

- All Python source lives under `src/`.
- The top-level package for the task management library is `tasklib`.
- Subsystems and feature areas use lowercase directory names.
- Package directory names must be singular only when they represent a singular bounded concept; otherwise prefer plural category names for grouped modules:
  - `models/`
  - `storage/`
- CLI code lives in `cli/`.
- Every package directory must include `__init__.py`.

### File naming rules

- Use lowercase snake_case for all Python module filenames.
- Avoid generic filenames except where they are standard package markers:
  - allowed: `__init__.py`
  - preferred descriptive modules: `task.py`, `repository.py`, `commands.py`
- One primary responsibility per module.
- Do not encode version numbers in filenames.
- Do not use hardcoded product names in filenames beyond the package name defined by the TRD.

### Documentation naming rules

The TRD explicitly includes a documentation set. Use uppercase conventional root document names:

- `README.md`
- `ARCHITECTURE.md`
- `API.md` or `API_REFERENCE.md`

Prefer consistent all-caps for root-level canonical docs.

---

## Class and Function Naming

### General Python naming

- Classes: `PascalCase`
- Functions: `snake_case`
- Methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal helpers: leading underscore, e.g. `_load_tasks`
- Boolean-returning functions should read as predicates where practical:
  - `is_complete`
  - `has_tasks`

### Class naming rules

Use noun-based names.

Examples consistent with the TRD scope:

- `Task`
- `TaskRepository`
- `InMemoryTaskStore`
- `CliApp`
- `CreateTaskCommand`

Avoid:

- Verb-based class names like `ManageTask`
- Overly vague names like `Handler`, `Util`, `Manager` unless bounded by context

### Function naming rules

Use verb-first names for operations.

Examples:

- `create_task`
- `list_tasks`
- `get_task`
- `save_task`
- `delete_task`
- `parse_args`

For conversion and serialization helpers:

- `from_dict`
- `to_dict`
- `from_json`
- `to_json`

### CLI naming rules

CLI entrypoint and command functions should clearly describe user actions:

- `main`
- `build_parser`
- `handle_create`
- `handle_list`

Subcommands should map to simple verbs or verb-noun pairs:

- `create`
- `list`
- `complete`
- `delete`

---

## Error and Exception Patterns

### General principles

- Raise exceptions for invalid state, invalid input, and storage failures.
- Use typed exceptions instead of raw `Exception`.
- Exception names must end with `Error`.
- Keep exception hierarchy shallow and domain-focused.

### Recommended exception naming

For the task management library:

- `TaskLibError` as the package base exception
- `ValidationError` for invalid task input
- `TaskNotFoundError` when a requested task does not exist
- `StorageError` for persistence or repository failures
- `CliError` for user-facing CLI execution failures

### Exception usage rules

- Raise the most specific exception available.
- Preserve original exceptions when wrapping lower-level failures:
  - `raise StorageError("failed to save task") from exc`
- Do not silently swallow exceptions.
- Convert domain exceptions to user-readable output only at the CLI boundary.
- Do not use exceptions for normal control flow.

### Error message conventions

- Messages should be lowercase sentence fragments unless surfaced directly to end users.
- Messages should identify the failed entity or action.
- Prefer deterministic wording.

Examples:

- `task id is required`
- `task not found: 123`
- `failed to persist task`

---

## Per-Subsystem Naming Rules

## Task Management Library

### Package naming

- Root package name: `tasklib`
- Primary subpackages:
  - `models`
  - `storage`
  - `cli`

### Model naming

Model classes are singular nouns.

Examples:

- `Task`

Model modules should match the primary type they contain:

- `models/task.py` → `Task`

If multiple related value objects are needed, group only when tightly coupled.

### Storage naming

Storage abstractions should be noun-based and implementation-specific where needed.

Examples:

- `TaskRepository`
- `InMemoryTaskRepository`
- `FileTaskRepository`

Methods should use consistent CRUD-style verbs:

- `add`
- `get`
- `list`
- `update`
- `delete`

If the abstraction is persistence-oriented, `save` is also acceptable, but use one style consistently.

### CLI naming

CLI modules should reflect role:

- `cli/app.py`
- `cli/commands.py`
- `cli/parser.py`

Command handlers should be action-based:

- `handle_create`
- `handle_list`

---

## CAL — Conversation Abstraction Layer

Use the acronym exactly as provided: `CAL`.

### Naming rules

- Classes: `CalPolicyEvaluator`, `CalVerifierCluster`
- Functions: `evaluate_cal_policy`, `verify_cal_request`
- Modules: `cal_policy.py`, `cal_verifier.py`

### Semantics

Because CAL is defined as the enforcement choke point for agent-originated actions:

- Names in this subsystem should emphasize evaluation, verification, enforcement, and routing.
- Avoid generic names like `process` when a precise term exists.

Preferred verbs:

- `evaluate`
- `enforce`
- `verify`
- `authorize`
- `intercept`

Preferred nouns:

- `Policy`
- `Request`
- `Decision`
- `Verifier`
- `Context`

---

## CPF — Conversation Plane Filter

Use the acronym exactly as provided: `CPF`.

### Naming rules

- Classes: `CpfFilter`, `CpfRuleSet`
- Functions: `apply_cpf_filter`, `load_cpf_rules`
- Modules: `cpf_filter.py`, `cpf_rules.py`

### Semantics

Names in this subsystem should reflect filtering and rule application.

Preferred verbs:

- `filter`
- `apply`
- `screen`
- `match`

Preferred nouns:

- `Filter`
- `Rule`
- `RuleSet`
- `Condition`

---

## AIR

Use the acronym exactly as provided: `AIR`.

### Naming rules

Because the expansion is not defined in the provided content, preserve the acronym in type and module names instead of inventing a long-form expansion.

- Classes: `AirRecord`, `AirEvaluator`, `AirContext`
- Functions: `build_air_record`, `evaluate_air_context`
- Modules: `air_record.py`, `air_context.py`

### Semantics

- Do not create unofficial expanded names.
- Prefer acronym-preserving identifiers for consistency with the TRD source.

---

## CTX-ID

`CTX-ID` contains a hyphen in the architecture source. Python identifiers cannot contain hyphens.

### Naming rules

- Convert `CTX-ID` to `ctx_id` in filenames and functions.
- Convert `CTX-ID` to `CtxId` in classes.

Examples:

- `ctx_id.py`
- `CtxIdResolver`
- `resolve_ctx_id`

### Semantics

Names should emphasize context identity and resolution.

Preferred verbs:

- `resolve`
- `assign`
- `validate`

Preferred nouns:

- `ContextId`
- `Identity`
- `Binding`

---

## PEE

Use the acronym exactly as provided: `PEE`.

### Naming rules

- Classes: `PeeEngine`, `PeeEvaluator`
- Functions: `run_pee_evaluation`, `build_pee_input`
- Modules: `pee_engine.py`, `pee_evaluator.py`

### Semantics

Without further expansion in the provided content, preserve the acronym and avoid inventing alternate names.

---

## TrustFlow / SIS

The architecture context lists `TrustFlow/SIS` together. Treat them as distinct naming domains joined by integration.

### Naming rules

#### TrustFlow

- Classes: `TrustFlowGraph`, `TrustFlowEvaluator`
- Functions: `build_trust_flow`, `evaluate_trust_flow`
- Modules: `trust_flow.py`, `trust_flow_graph.py`

#### SIS

- Classes: `SisAdapter`, `SisRecord`
- Functions: `sync_with_sis`, `load_sis_record`
- Modules: `sis_adapter.py`, `sis_record.py`

### Integration naming

For modules spanning both:

- `trustflow_sis_bridge.py`
- `TrustFlowSisBridge`
- `sync_trust_flow_to_sis`

### Semantics

- Use `trust_flow` as the snake_case form of `TrustFlow`.
- Use `sis` lowercase in modules and functions.
- Avoid slash characters in identifiers.

---

## CAL Verifier Cluster

This name is a specialized CAL component.

### Naming rules

- Classes: `CalVerifierCluster`, `VerifierNode`
- Functions: `build_verifier_cluster`, `select_verifier_node`
- Modules: `cal_verifier_cluster.py`, `verifier_node.py`

### Semantics

Names should reflect distributed verification responsibilities.

Preferred verbs:

- `verify`
- `select`
- `dispatch`
- `aggregate`

Preferred nouns:

- `Cluster`
- `Node`
- `Verifier`
- `Result`

---

## Cross-Subsystem Rules

### Acronym handling

- Preserve architecture acronyms from the TRD in class names using `PascalCase` acronym form:
  - `CAL` → `Cal...`
  - `CPF` → `Cpf...`
  - `AIR` → `Air...`
  - `PEE` → `Pee...`
  - `SIS` → `Sis...`
- In filenames and function names, use lowercase snake_case:
  - `cal_policy.py`
  - `cpf_filter.py`
  - `air_context.py`

### Hyphen and slash normalization

When architecture names contain non-identifier characters:

- Hyphen (`-`) becomes underscore in file/function names and is removed via word casing in class names:
  - `CTX-ID` → `ctx_id`, `CtxId`
- Slash (`/`) indicates composition or integration, not a literal identifier:
  - `TrustFlow/SIS` → separate identifiers or an explicit bridge name

### Import conventions

Because the TRD validates dependency-chain imports across merged work:

- Prefer absolute imports within `src/` packages.
- Imports must resolve against locally mirrored package structure before CI.
- Do not rely on implicit relative execution context.

Preferred:

```python
from tasklib.models.task import Task
```

Avoid:

```python
from ..models.task import Task
```

unless there is a clear package-internal reason and consistency is maintained.

### Dependency ordering in code organization

The TRD explicitly defines a dependency chain:

- docs → scaffold → model → storage → CLI

Reflect this in implementation dependencies:

- `models` must not depend on `storage` or `cli`
- `storage` may depend on `models`
- `cli` may depend on `models` and `storage`
- documentation examples must match implemented public APIs

### Public API exposure

- Re-export only stable, intended public symbols in package `__init__.py`.
- Keep internal helpers out of package root exports.
- Public API names should match documentation names exactly.

### Naming stability

Because the TRD is intended to validate an end-to-end pipeline:

- Do not rename modules, packages, or public classes casually once introduced.
- Prefer additive changes over churn in public identifiers.
- Keep documentation, scaffold, and imports synchronized.