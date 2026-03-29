# Code Conventions

This document defines coding conventions derived from the provided TRD material. It covers the task management library and the architecture context subsystems referenced in the TRDs. These conventions apply across documentation, scaffold, library code, storage code, CLI code, and subsystem-aligned modules.

## File and Directory Naming (exact `src/` layout)

### Source root

All Python implementation code must live under `src/`.

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

### Package layout rules

- Use a single top-level Python package under `src/`.
- Subsystems and functional areas must be split into subpackages, not flat files at package root, when they represent distinct responsibilities.
- Required library areas from the TRD dependency chain:
  - `models/`
  - `storage/`
  - `cli/`

### File naming

Use lowercase snake_case for all Python module and package filenames.

Examples:
- `task.py`
- `task_store.py`
- `file_storage.py`
- `command_parser.py`

Do not use:
- CamelCase filenames like `TaskStore.py`
- kebab-case filenames like `task-store.py`

### Directory naming

Use lowercase snake_case for directories.

Examples:
- `models/`
- `storage/`
- `policy_eval/`
- `verifier_cluster/`

### Documentation filenames

Documentation files referenced by the TRD should use stable uppercase names when they are top-level canonical docs:

- `README.md`
- `ARCHITECTURE.md`
- `API.md` or `API_REFERENCE.md`

If documentation is split into sections, use lowercase snake_case beneath a docs folder:

```text
docs/
  architecture_overview.md
  api_reference.md
  cli_usage.md
```

### Test naming

Tests should mirror implementation structure.

```text
tests/
  models/
    test_task.py
  storage/
    test_task_store.py
  cli/
    test_commands.py
```

Rules:
- Test files must begin with `test_`
- Test module names should match the target module where practical

---

## Class and Function Naming

### General Python naming

Follow standard Python conventions:

- Classes: `PascalCase`
- Functions: `snake_case`
- Methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal members: leading underscore, e.g. `_load_tasks`

### Class naming patterns

Use nouns for classes.

Examples:
- `Task`
- `TaskStore`
- `FileTaskStore`
- `CliRunner`
- `PolicyEvaluator`
- `ConversationContext`

Avoid:
- Verb-based class names like `ManageTask`
- Generic names like `Helper`, `Manager`, `Processor` unless strongly qualified by subsystem context

### Function naming patterns

Use verb or verb phrase names for functions.

Examples:
- `create_task`
- `list_tasks`
- `save_task`
- `load_tasks`
- `evaluate_policy`
- `verify_conversation`

Boolean-returning functions should read as predicates:
- `is_complete`
- `has_permission`
- `can_execute`

### Factory and parser naming

Use explicit suffixes when intent matters:
- `from_dict`
- `to_dict`
- `parse_args`
- `build_context`
- `load_from_file`

### CLI command naming

CLI command handlers should be named with a command-oriented prefix.

Examples:
- `cmd_add`
- `cmd_list`
- `cmd_complete`

Parser builders should be explicit:
- `build_parser`
- `register_subcommands`

### Data model naming

Model classes should be singular nouns:
- `Task`
- `Conversation`
- `PolicyDecision`
- `ExecutionIdentity`

Collections should be plural in variable names:
- `tasks`
- `policies`
- `decisions`

---

## Error and Exception Patterns

### General exception rules

- Raise exceptions for invalid state, invalid input, storage failure, and policy enforcement failure.
- Do not silently swallow errors.
- Do not return mixed error types such as `False`, `None`, and exceptions for the same failure mode.

### Custom exception naming

Custom exceptions must:
- inherit from `Exception`
- end in `Error`

Examples:
- `TaskValidationError`
- `TaskNotFoundError`
- `StorageError`
- `PolicyEvaluationError`
- `VerificationError`

### Exception hierarchy pattern

Use a subsystem base exception where a subsystem has multiple error cases.

Example:

```python
class TaskLibError(Exception):
    pass

class TaskValidationError(TaskLibError):
    pass

class TaskNotFoundError(TaskLibError):
    pass
```

Subsystem examples:
- `StorageError`
- `CliError`
- `ConversationPlaneError`
- `PolicyEngineError`

### Error message conventions

Error messages should be:
- concise
- actionable
- deterministic
- free of internal-only debugging noise unless re-raised with context

Preferred:
- `Task with id '123' was not found`
- `Storage backend could not load tasks from path: /tmp/tasks.json`

Avoid:
- `Oops, something broke`
- `Error 1`
- `Bad input`

### Validation patterns

Validate at boundaries:
- CLI argument parsing
- model construction
- storage input/output
- subsystem policy entry points

Use `ValueError` only for small, local validation failures when a custom domain exception is unnecessary. Prefer domain exceptions at public package boundaries.

### Wrapping lower-level exceptions

Wrap infrastructure exceptions with subsystem context while preserving the original error.

Preferred pattern:

```python
try:
    data = path.read_text()
except OSError as exc:
    raise StorageError(f"Failed reading storage file: {path}") from exc
```

### Policy and enforcement failures

For enforcement-oriented subsystems, policy denial and system failure must be distinguishable:
- use a denial/result object or explicit domain exception for policy denial
- use exceptions for evaluation failures, corruption, or unavailable dependencies

---

## Per-Subsystem Naming Rules

## Task management library

### Package naming

Use these package names for the TRD-defined chain:
- `models`
- `storage`
- `cli`

Optional shared package names:
- `exceptions`
- `utils`
- `types`

### Model naming

Model modules should map 1:1 to primary entities where possible.

Examples:
- `models/task.py` → `Task`
- `models/task_status.py` → `TaskStatus`

Naming rules:
- entity names are singular
- enums use singular type names
- DTO-like conversion methods use `to_dict` / `from_dict`

### Storage naming

Storage implementations should make backend explicit in the class name.

Examples:
- `TaskStore` for abstract/interface role
- `FileTaskStore` for file-backed implementation
- `MemoryTaskStore` for in-memory implementation

Module names should reflect both entity and role:
- `task_store.py`
- `file_task_store.py`

Storage methods should use consistent verbs:
- `save`
- `load`
- `list`
- `delete`
- `update`

Avoid mixing synonyms like `fetch`, `get_all`, `read_all`, `retrieve_all` for the same abstraction unless the distinctions are intentional and documented.

### CLI naming

CLI modules should be organized by command or parser responsibility:
- `main.py`
- `parser.py`
- `commands.py`

Command names should be short, verb-oriented, and lowercase:
- `add`
- `list`
- `complete`

Handler methods should map directly to command names.

---

## CAL — Conversation Abstraction Layer

### Naming scope

CAL-aligned modules are enforcement and evaluation modules that mediate all agent-originated actions.

### Package and module naming

Use the subsystem acronym only when the acronym is the canonical architectural term in the TRD. Expand on first use in docs; code may use the acronym consistently if the package is clearly scoped.

Examples:
- `cal/`
- `cal/policy_evaluator.py`
- `cal/conversation_context.py`
- `cal/verifier.py`

Prefer descriptive expanded names inside the subsystem:
- `ConversationContext`
- `PolicyEvaluationRequest`
- `PolicyEvaluationResult`

### Class naming

Use names that express enforcement responsibility:
- `ConversationAbstractionLayer`
- `PolicyEvaluator`
- `ConversationVerifier`
- `ActionGate`

### Function naming

Use verbs aligned to policy flow:
- `evaluate_action`
- `verify_request`
- `build_context_id`
- `enforce_policy`

Avoid ambiguous verbs like:
- `handle`
- `process`
- `run`

unless context is highly localized.

### Data naming

Request/response object names should be explicit:
- `PolicyEvaluationRequest`
- `PolicyEvaluationResult`
- `VerifierDecision`

IDs derived from context should end in `Id` only if they are class/type names, and `_id` if they are fields/variables:
- class: `ContextId`
- variable: `context_id`

---

## CPF — Conversation Plane Filter

### Package naming

Use:
- `cpf/`
or a nested package under `cal/` if implemented as a CAL component:
- `cal/cpf/`

Choose one pattern and apply it consistently.

### Class naming

Use filter and gate terminology:
- `ConversationPlaneFilter`
- `ActionFilterRule`
- `FilterDecision`

### Function naming

Recommended verbs:
- `filter_action`
- `allow_action`
- `deny_action`
- `match_rule`

### Rule naming

Rules should use noun-based names with a `Rule` suffix:
- `ToolInvocationRule`
- `DataReadRule`
- `ApiInvocationRule`
- `AgentHandoffRule`

---

## AIR

The TRD lists AIR as a key component but does not expand the acronym. Conventions must therefore remain neutral and structure-focused.

### Naming rule

Where acronym expansion is unspecified in the TRD:
- package names may use the canonical acronym
- class and function names must prefer role-based descriptive naming over guessed expansion

Examples:
- `air/registry.py`
- `air/adapter.py`
- `ActionRegistry`
- `IdentityResolver`
- `resolve_identity`

Avoid inventing expanded terminology not defined by the TRD.

---

## CTX-ID

The TRD identifies CTX-ID as a key component.

### Package naming

Because hyphens are invalid in Python package names, convert acronym packages to lowercase snake_case:
- `ctx_id/`

### Class naming

Use explicit context identity names:
- `ContextId`
- `ContextIdGenerator`
- `ContextIdentityRecord`

### Function naming

Use:
- `generate_context_id`
- `parse_context_id`
- `validate_context_id`

### Variable naming

Always use `context_id`, never `ctxid`, `ctx_id` in public API fields unless matching an external schema exactly.

---

## PEE

The TRD lists PEE as a key component without expansion.

### Naming rule

As with AIR, do not invent long-form terminology not present in the TRD.

Use:
- `pee/`
- `pee/evaluator.py`
- `pee/engine.py`

Prefer descriptive class names based on role:
- `EvaluationEngine`
- `ExecutionEvaluator`
- `PolicyEngine`

Function examples:
- `evaluate`
- `evaluate_context`
- `compute_decision`

---

## TrustFlow / SIS

The TRD presents this as a paired architectural term.

### Package naming

If implemented as separate packages:
- `trustflow/`
- `sis/`

If implemented as a coupled subsystem:
- `trustflow_sis/`

Do not use slashes in code identifiers.

### Class naming

Use trust and signal-oriented nouns:
- `TrustFlowCoordinator`
- `SignalIntegrityService`
- `TrustDecision`

### Function naming

Use:
- `compute_trust`
- `emit_signal`
- `validate_signal`
- `merge_trust_inputs`

---

## CAL Verifier Cluster

### Package naming

Use:
- `verifier_cluster/`
or nested:
- `cal/verifier_cluster/`

### Class naming

Use cluster-aware naming only for distributed or grouped verification concerns:
- `VerifierCluster`
- `VerifierNode`
- `ClusterDecisionAggregator`

Single-node verification code should not be named `Cluster`.

### Function naming

Use:
- `verify`
- `verify_batch`
- `aggregate_decisions`
- `select_verifier_node`

---

## Cross-subsystem naming rules

### Acronyms in code

- Preserve canonical architecture acronyms when they are defined in the TRD.
- In filenames and packages, use lowercase snake_case:
  - `ctx_id`
  - `verifier_cluster`
- In class names, use PascalCase with readable acronym handling:
  - `ContextId`
  - `CalVerifier`
  - `CpfRule`

Do not create inconsistent forms like:
- `CTXID`
- `calVerifier`
- `Verifiercluster`

### Boundary object naming

Use suffixes consistently:
- `Request`
- `Response`
- `Result`
- `Record`
- `Config`

Examples:
- `PolicyEvaluationRequest`
- `PolicyEvaluationResult`
- `StorageConfig`

### Interface and implementation naming

If abstract roles are used:
- abstract/base type: `TaskStore`
- implementation: `FileTaskStore`

Do not prefix interfaces with `I`.

Avoid:
- `ITaskStore`

### Enum naming

Enum classes use singular nouns in PascalCase:
- `TaskStatus`
- `PolicyDecision`

Enum values use `UPPER_SNAKE_CASE`:
- `PENDING`
- `COMPLETE`
- `ALLOW`
- `DENY`

### Boolean field naming

Boolean properties and variables should read naturally:
- `is_complete`
- `is_allowed`
- `has_identity`
- `can_execute`

Avoid:
- `complete_flag`
- `allowed_status`

---

## Additional code patterns

### Public API stability

Public APIs should use explicit names and avoid shorthand.
Prefer:
- `list_tasks()`
over:
- `ls()`

### Import style

Use absolute imports within the package unless a local relative import is materially clearer.

Preferred:
```python
from tasklib.models.task import Task
```

Use relative imports sparingly within tightly-coupled package internals:
```python
from .task import Task
```

### Single responsibility by module

Each module should have one primary responsibility.
Examples:
- `models/task.py` defines task model behavior
- `storage/file_task_store.py` defines file-backed persistence
- `cli/parser.py` defines argument parsing

### Deterministic naming across dependency chain

Because the TRD emphasizes merge ordering and import resolution across dependent PRs:
- do not rename exported classes or modules casually
- keep module paths stable once introduced
- avoid temporary aliases in merged code

### Backward-safe extension pattern

When extending a subsystem:
- add new modules rather than overloading unrelated existing modules
- preserve constructor and method names where possible
- introduce new optional parameters with explicit names

### Documentation alignment

Names used in:
- README
- architecture docs
- API reference
- code
- CLI help

must match exactly for exported classes, modules, commands, and major subsystem terms.

---

## Summary rules

- Use `src/` layout with one top-level package.
- Use lowercase snake_case for files and directories.
- Use PascalCase for classes and snake_case for functions.
- Use explicit, role-based names; avoid vague helpers.
- Custom exceptions end in `Error`.
- Distinguish policy denial from system failure.
- Preserve TRD-defined subsystem acronyms without inventing undefined expansions.
- Keep names stable across the docs → scaffold → model → storage → CLI dependency chain.