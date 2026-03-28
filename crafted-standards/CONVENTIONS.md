# Code Conventions

This document defines coding conventions derived from the provided TRD material. It covers the task management library and the architecture context subsystems referenced in the injected architecture guidance. All conventions here are implementation-facing and intended to keep generated and hand-written code consistent across documentation, scaffold, library, storage, CLI, and policy-enforcement-related subsystems.

## File and Directory Naming (exact src/ layout)

### Source root

All Python implementation code must live under:

```text
src/
```

Primary package layout:

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

### Required package structure

The dependency chain defined in the TRD must be reflected in package organization:

- Documentation artifacts exist outside `src/`
- Scaffold establishes package directories under `src/`
- Model code lives under `src/tasklib/models/`
- Storage code lives under `src/tasklib/storage/`
- CLI code lives under `src/tasklib/cli/`

### File naming rules

Use lowercase snake_case for all Python module filenames.

Examples:

- `task.py`
- `task_store.py`
- `memory_store.py`
- `json_store.py`
- `main.py`
- `commands.py`

Do not use:

- CamelCase filenames
- hyphenated filenames
- vague names like `utils.py` unless the module is truly cross-cutting and stable

### Directory naming rules

Use lowercase snake_case for subpackages and directories.

Examples:

- `models`
- `storage`
- `cli`
- `policy`
- `identity`
- `verifier`

### Documentation filenames

Documentation files referenced by the TRD should use stable uppercase conventional names when they are top-level project docs:

- `README.md`
- `ARCHITECTURE.md`
- `API.md` or `API_REFERENCE.md`

If additional design docs are added, use snake_case or uppercase convention consistently, but do not mix styles within the same documentation tier.

### Tests

Tests should mirror package structure.

Preferred layout:

```text
tests/
  models/
    test_task.py
  storage/
    test_memory_store.py
  cli/
    test_commands.py
```

### Import path conventions

Use absolute imports from the package root.

Preferred:

```python
from tasklib.models.task import Task
from tasklib.storage.memory_store import MemoryTaskStore
```

Avoid relative imports unless required for tightly-coupled package internals.

## Class and Function Naming

### Classes

Use PascalCase for all classes.

Examples:

- `Task`
- `TaskStore`
- `MemoryTaskStore`
- `JsonTaskStore`
- `TaskRepository`
- `CliRunner`

### Abstract and interface-like classes

For protocol, base, or abstract roles, use noun-based names that describe the contract.

Examples:

- `TaskStore`
- `PolicyEvaluator`
- `VerifierCluster`

Avoid prefix-heavy names like:

- `IStorage`
- `BaseThing` unless it is truly a reusable base class

If an abstract base class is needed, acceptable patterns are:

- `TaskStore`
- `AbstractTaskStore`

Prefer the simpler domain name when the abstraction is central.

### Functions and methods

Use snake_case.

Examples:

- `create_task`
- `list_tasks`
- `mark_complete`
- `load_tasks`
- `evaluate_policy`
- `verify_identity`

Function names must be verb-led when performing actions.

Good:

- `save_task`
- `delete_task`
- `parse_args`

Avoid ambiguous names:

- `task_data`
- `handler`
- `process`

### Constants

Use UPPER_SNAKE_CASE.

Examples:

- `DEFAULT_STORAGE_PATH`
- `MAX_RETRY_COUNT`
- `CTX_ID_HEADER`

### Variables and attributes

Use lowercase snake_case.

Examples:

- `task_id`
- `created_at`
- `policy_result`
- `conversation_context`

### Boolean naming

Boolean variables and methods should read as predicates.

Examples:

- `is_complete`
- `is_allowed`
- `has_identity`
- `can_execute`

Avoid boolean names that do not imply truth value, such as:

- `complete`
- `policy`
- `identity`

### CLI command functions

CLI-facing functions should use action-oriented names tied to command semantics.

Examples:

- `cmd_add`
- `cmd_list`
- `cmd_complete`

If using a command dispatcher, keep the command registration and command implementation names aligned.

## Error and Exception Patterns

### General rules

Raise exceptions for exceptional conditions, not for normal control flow.

Errors must be:

- specific
- domain-relevant
- actionable
- named consistently

### Exception naming

All custom exception classes must end with `Error`.

Examples:

- `TaskError`
- `TaskNotFoundError`
- `StorageError`
- `PolicyEvaluationError`
- `VerificationError`

### Exception hierarchy

Use subsystem-root exceptions for grouping.

Example:

```python
class TaskLibError(Exception):
    pass

class TaskError(TaskLibError):
    pass

class TaskNotFoundError(TaskError):
    pass

class StorageError(TaskLibError):
    pass
```

For policy-related subsystems, use the same pattern:

- `CalError`
- `CpfError`
- `VerifierError`

### When to define custom exceptions

Define a custom exception when:

- callers need to distinguish a domain failure from a generic runtime failure
- a subsystem boundary needs stable error semantics
- CLI output must map exceptions to user-facing messages
- policy enforcement decisions need explicit failure classes

### Error message conventions

Error messages should be concise and include the failed entity and reason.

Good:

- `Task with id '123' was not found`
- `Storage backend could not persist task data`
- `Policy evaluation denied action 'read_data'`

Avoid:

- `Something went wrong`
- `Bad input`
- `Failed`

### Wrapping lower-level exceptions

Wrap low-level exceptions at subsystem boundaries while preserving cause.

Preferred:

```python
try:
    data = json.loads(raw)
except ValueError as exc:
    raise StorageError("Stored task data is not valid JSON") from exc
```

### CLI exception handling

CLI code should catch domain exceptions near the entrypoint and translate them into:

- human-readable messages
- deterministic exit codes
- no raw tracebacks unless in debug mode

### Validation failures

Validation failures should raise domain-specific `...Error` types rather than returning sentinel values like `None` or `False` when the caller needs error detail.

## Per-Subsystem Naming Rules

## Task Management Library

### Package naming

Use `tasklib` as the package root for the task management library.

### Domain model names

Core task entities should use simple, singular nouns.

Examples:

- `Task`
- `TaskStatus`
- `TaskStore`

Collection-returning functions may use pluralized terms in variable names, not class names.

Examples:

- `tasks`
- `task_items`

### Model field names

Task model field names should be explicit and stable.

Preferred names:

- `task_id`
- `title`
- `description`
- `is_complete`
- `created_at`
- `updated_at`

Avoid overloaded or abbreviated names:

- `id`
- `desc`
- `done`
- `ts`

### Storage naming

Storage implementations should be named as `<Backend><DomainContract>`.

Examples:

- `MemoryTaskStore`
- `JsonTaskStore`
- `FileTaskStore`

Not:

- `TaskStorageImpl`
- `StoreManager`

### Storage method names

Use CRUD-like naming where appropriate.

Examples:

- `add_task`
- `get_task`
- `list_tasks`
- `update_task`
- `delete_task`

If the store is append-only or immutable, reflect that explicitly in naming.

### CLI naming

CLI modules and functions must align with the task domain.

Examples:

- `commands.py`
- `parser.py`
- `main.py`
- `build_parser`
- `run_cli`

Command names should be short, verb-based, and user-readable:

- `add`
- `list`
- `complete`
- `remove`

## Documentation Subsystem

### Documentation names

Documents named in the TRD should remain canonical:

- `README.md`
- `ARCHITECTURE.md`
- API reference document with a stable explicit name

### Section naming

Documentation section titles should use title case and clear subsystem names.

Examples:

- `Purpose and Scope`
- `Architecture Overview`
- `API Reference`
- `Storage Layer`
- `CLI Interface`

### Cross-reference naming

When code and docs refer to the same concept, use the same noun phrase in both places. Do not rename concepts between documentation and implementation.

## Scaffold Subsystem

### Scaffold package names

Scaffolded directories must match final importable package names exactly. Do not scaffold placeholder names that differ from runtime package names.

### Scaffold file names

Scaffold files should use final names, not transitional names like:

- `temp_model.py`
- `new_storage.py`
- `sample_cli.py`

### Generated code markers

If generated code needs marking, use comments that identify generated sections without embedding tool-specific branding.

Example:

```python
# Generated scaffold: extend as needed.
```

## Model Subsystem

### Entity naming

Use singular nouns for entities and enums or constants for categorical values.

Examples:

- `Task`
- `TaskStatus`

### Constructor and factory naming

Prefer direct constructors unless a factory conveys domain meaning.

Examples:

- `Task(...)`
- `Task.from_dict(...)`
- `Task.to_dict()`

### Serialization naming

Use `to_dict` / `from_dict` for plain mapping conversion.

Use `to_json` / `from_json` only when the method directly handles JSON text.

## Storage Subsystem

### Contract naming

A storage contract should be named after the domain plus responsibility.

Examples:

- `TaskStore`
- `PolicyStore`
- `IdentityStore`

### Backend naming

Backend-specific implementations should prefix the storage contract with the backend or persistence strategy.

Examples:

- `MemoryTaskStore`
- `FilePolicyStore`
- `SqlIdentityStore`

### Persistence helper naming

Internal helpers should be descriptive.

Examples:

- `_load_from_disk`
- `_write_snapshot`
- `_next_task_id`

Avoid generic private helpers like `_handle_data`.

## CLI Subsystem

### Entry point naming

CLI entry modules should use one of:

- `main.py`
- `__main__.py`

### Parser naming

Argument parser builders should use:

- `build_parser`
- `configure_parser`

Execution wrappers should use:

- `main`
- `run_cli`

### Command handler naming

Command handlers should clearly map to commands.

Examples:

- `handle_add`
- `handle_list`
- `handle_complete`

If abbreviated command prefixes are used, apply them consistently across all commands.

## CAL — Conversation Abstraction Layer

### Subsystem naming

Use the acronym exactly as documented for subsystem labels: `CAL`.

In code, module names should be lowercase:

- `cal/`
- `cal/policy_evaluator.py`
- `cal/verifier.py`

Classes should expand meaning where helpful:

- `ConversationAbstractionLayer`
- `CalPolicyEvaluator`
- `CalVerifierCluster`

### Responsibility naming

Because CAL is the enforcement choke point for agent-originated actions, names in this subsystem must reflect gating and enforcement semantics.

Preferred verbs:

- `evaluate`
- `enforce`
- `authorize`
- `verify`
- `deny`

Avoid vague verbs like:

- `do`
- `run`
- `check` when a stronger domain verb is available

### Action naming

Anything representing an agent-originated operation should use explicit action nouns.

Examples:

- `tool_call`
- `data_read`
- `api_invocation`
- `agent_handoff`

### Evaluation result naming

Use explicit result names:

- `policy_decision`
- `evaluation_result`
- `denial_reason`

Avoid generic names like `result` at subsystem boundaries.

## CPF — Conversation Plane Filter

### Acronym handling

Use `CPF` in documentation labels and lowercase `cpf` in file and package names.

Examples:

- `cpf/filter.py`
- `CpfFilter`
- `CpfDecision`

### Filter and rule naming

Rules and filters should use names that describe the filtered subject or policy dimension.

Examples:

- `ActionFilter`
- `IdentityFilter`
- `ContextRule`
- `ConversationRuleSet`

Avoid implementation-only names like:

- `RuleProcessor`
- `FilterManager`

unless orchestration is truly their primary role.

## AIR

### Naming style

Use `AIR` in docs and `air` in package/module names.

Examples:

- `air/record.py`
- `AirRecord`
- `AirEvaluator`

Where the acronym refers to a record, report, or representation, the class name should include the domain noun rather than using the acronym alone.

Avoid:

- `AIRObj`
- `AIRData`

## CTX-ID

### Identifier naming

For context identity concepts, normalize the hyphenated document label into code-safe snake_case or PascalCase.

Examples:

- package/module: `ctx_id`
- class: `CtxId`
- value object: `ContextIdentity`

### Field names

Use explicit names such as:

- `context_id`
- `parent_context_id`
- `conversation_id`

Avoid raw `ctx` abbreviations in public interfaces unless required by protocol compatibility.

## PEE

### Execution and enforcement naming

Use names that emphasize execution policy and evaluation.

Examples:

- `PeeEngine`
- `ExecutionPolicy`
- `PolicyExecutionResult`

Package/module names should be lowercase:

- `pee/engine.py`
- `pee/policy.py`

## TrustFlow / SIS

### Slash-delimited subsystem normalization

When a subsystem is named with a slash in documentation, split it into distinct code-safe package names if implemented separately.

Examples:

- `trustflow/`
- `sis/`

If implemented as one combined subsystem, use a combined package name only when required by architecture constraints:

- `trustflow_sis/`

Prefer separate namespaces over collapsed ambiguous names.

### Class naming

Examples:

- `TrustFlowCoordinator`
- `SisAdapter`
- `TrustStatement`

## CAL Verifier Cluster

### Cluster naming

Use names that distinguish cluster-wide orchestration from single verifier components.

Examples:

- `CalVerifier`
- `CalVerifierNode`
- `CalVerifierCluster`

### Verification method naming

Use verbs like:

- `verify`
- `attest`
- `validate_signature`
- `validate_policy_state`

Avoid overloading `check` for cryptographic or policy verification responsibilities.

## Policy and Identity Conventions

### Policy objects

Policy-related classes should use the suffix `Policy` only for actual policy definitions or executable policy units.

Examples:

- `ExecutionPolicy`
- `ConversationPolicy`

Do not use `Policy` for generic config holders.

### Identity objects

Identity-related classes should use precise nouns.

Examples:

- `AgentIdentity`
- `OperatorIdentity`
- `CryptographicIdentity`
- `IdentityVerifier`

Avoid names like:

- `IdentityManager`
- `IdentityHelper`

unless they truly coordinate multiple identity operations.

## Cross-Subsystem Consistency Rules

### Acronyms in code

For subsystem acronyms:

- keep documentation labels in their canonical uppercase form
- use lowercase for modules and packages
- use PascalCase in class names

Examples:

- doc: `CAL`
- module: `cal`
- class: `CalVerifierCluster`

### Boundary object naming

Objects crossing subsystem boundaries should use explicit suffixes when helpful:

- `Request`
- `Response`
- `Result`
- `Decision`
- `Record`

Examples:

- `PolicyDecision`
- `VerificationResult`
- `TaskCreateRequest`

### Avoid generic manager naming

Do not default to `Manager`, `Helper`, `Processor`, or `Util` in public APIs unless the class truly represents orchestration of heterogeneous responsibilities.

Prefer domain-specific names.

### One concept, one name

If a concept is introduced in documentation, keep the same term in:

- package names
- class names
- method names
- CLI commands
- error names

Do not alternate between synonyms like `task item`, `entry`, and `record` for the same domain object unless they are intentionally different types.

### Dependency-chain naming alignment

Because the implementation pipeline depends on earlier merged layers, downstream code must import upstream modules using their final stable names. Do not rename model or storage contracts after downstream packages depend on them.