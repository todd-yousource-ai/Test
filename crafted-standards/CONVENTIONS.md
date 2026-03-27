# Code Conventions

This document defines coding conventions derived from the provided TRD materials. It covers the task management library scaffold and the architecture subsystems identified in the architecture context. These conventions are intended to keep documentation, package structure, naming, and code patterns consistent across the full dependency chain: documentation → scaffold → model → storage → CLI.

## File and Directory Naming (exact src/ layout)

Use a `src/` layout for all Python code.

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
│     ├─ cli/
│     │  ├─ __init__.py
│     │  └─ main.py
│     └─ architecture/
│        ├─ __init__.py
│        ├─ cal/
│        │  ├─ __init__.py
│        │  └─ policy.py
│        ├─ cpf/
│        │  ├─ __init__.py
│        │  └─ filter.py
│        ├─ air/
│        │  ├─ __init__.py
│        │  └─ runtime.py
│        ├─ ctx_id/
│        │  ├─ __init__.py
│        │  └─ identity.py
│        ├─ pee/
│        │  ├─ __init__.py
│        │  └─ evaluation.py
│        ├─ trustflow/
│        │  ├─ __init__.py
│        │  └─ signals.py
│        ├─ sis/
│        │  ├─ __init__.py
│        │  └─ state.py
│        └─ verifier/
│           ├─ __init__.py
│           └─ cluster.py
├─ README.md
├─ ARCHITECTURE.md
└─ API.md
```

### Directory rules

- All importable code must live under `src/`.
- Package directories use lowercase snake_case.
- One subsystem per directory.
- Related concerns must be grouped by layer:
  - `models/` for domain entities
  - `storage/` for persistence implementations
  - `cli/` for command-line entrypoints
  - `architecture/` for architecture-level subsystem representations

### File naming rules

- Python modules use lowercase snake_case: `task.py`, `memory.py`, `main.py`.
- Avoid generic filenames like `utils.py`, `helpers.py`, or `misc.py` unless the TRD explicitly defines a shared utility layer.
- Prefer singular filenames for a single primary concept:
  - `task.py` for `Task`
  - `policy.py` for policy-related CAL logic
  - `identity.py` for CTX-ID logic
- `__init__.py` should export only the stable public surface for that package.

### Documentation naming rules

Use these exact top-level documentation filenames where present:

- `README.md`
- `ARCHITECTURE.md`
- `API.md`

Documentation filenames must be uppercase when they represent canonical project documents defined by the TRD.

## Class and Function Naming

### Classes

Use PascalCase for all classes.

Examples:

- `Task`
- `TaskRepository`
- `InMemoryTaskStorage`
- `TaskCli`
- `ConversationPlaneFilter`
- `PolicyEvaluationEngine`
- `ContextIdentity`
- `VerifierCluster`

### Functions and methods

Use snake_case for all functions and methods.

Examples:

- `create_task()`
- `list_tasks()`
- `get_task_by_id()`
- `save_task()`
- `evaluate_policy()`
- `filter_conversation_action()`
- `resolve_context_identity()`
- `verify_runtime_request()`

### Variables

Use snake_case for local variables, parameters, and module globals.

Examples:

- `task_id`
- `task_title`
- `storage_backend`
- `policy_result`
- `context_identity`

### Constants

Use UPPER_SNAKE_CASE for module-level constants.

Examples:

- `DEFAULT_STORAGE_PATH`
- `MAX_TASK_TITLE_LENGTH`
- `POLICY_DECISION_ALLOW`

### Private members

Use a single leading underscore for internal-only functions, methods, and attributes.

Examples:

- `_validate_task_title()`
- `_load_state()`
- `_policy_cache`

Do not use double-leading-underscore name mangling unless required for a specific language-level behavior.

## Error and Exception Patterns

### Exception naming

Custom exceptions must use the `Error` suffix.

Examples:

- `TaskError`
- `TaskNotFoundError`
- `StorageError`
- `CliError`
- `PolicyEvaluationError`
- `VerificationError`
- `ContextIdentityError`

### Exception hierarchy

Define narrow, domain-specific exceptions under a package-level base exception.

Example pattern:

```python
class TasklibError(Exception):
    pass


class TaskError(TasklibError):
    pass


class TaskNotFoundError(TaskError):
    pass


class StorageError(TasklibError):
    pass
```

### Raise patterns

- Raise specific exceptions, not bare `Exception`.
- Use `ValueError` only for simple argument validation where no domain-specific exception exists yet.
- Convert low-level storage or parsing failures into subsystem-specific exceptions at subsystem boundaries.
- CLI code should catch domain exceptions and convert them into user-facing messages and non-zero exit behavior.

### Error message style

- Error messages must be concise and actionable.
- Include the failing identifier where useful.
- Do not embed implementation trivia in user-facing messages.

Good examples:

- `Task not found: {task_id}`
- `Invalid task title`
- `Policy evaluation denied action`
- `Context identity is missing`

Avoid:

- `Something went wrong`
- `Error in storage layer during operation`
- Stack-trace-style messaging in raised domain exceptions

### Validation pattern

Validate inputs at subsystem boundaries:

- model constructors or factory functions validate domain invariants
- storage methods validate required keys and identifiers
- CLI validates command arguments before invoking domain logic
- policy and verifier modules validate the presence of required context

## Per-Subsystem Naming Rules

## Task Management Library

### Package naming

Use `tasklib` as the root package.

### Domain model naming

Model classes should be singular nouns.

Examples:

- `Task`
- `TaskStatus` if an enum is needed

Model modules should match the primary class name in snake_case.

Examples:

- `task.py`
- `status.py`

### Storage naming

Storage interfaces and implementations must clearly distinguish abstraction from implementation.

Patterns:

- abstraction: `TaskStorage`, `TaskRepository`
- implementation: `InMemoryTaskStorage`, `FileTaskStorage`

Storage modules should reflect implementation or abstraction purpose:

- `base.py` for abstract interfaces
- `memory.py` for in-memory storage
- `file.py` for file-backed storage

### CLI naming

CLI entrypoint modules should be named `main.py` unless multiple command groups are required.

Function naming examples:

- `main()`
- `build_parser()`
- `handle_create()`
- `handle_list()`

Do not mix parsing logic, domain logic, and storage logic in one large function.

## CAL — Conversation Abstraction Layer

CAL is the enforcement choke point for all agent-originated actions. Naming must reflect its gatekeeper role.

### Class naming

Prefer names that express enforcement, routing, or evaluation.

Examples:

- `ConversationAbstractionLayer`
- `CalPolicyEvaluator`
- `CalRequest`
- `CalDecision`

### Function naming

Examples:

- `evaluate_action()`
- `enforce_policy()`
- `route_for_verification()`
- `build_cal_request()`

### Module naming

Examples:

- `policy.py`
- `requests.py`
- `decisions.py`
- `enforcement.py`

Avoid ambiguous names like `core.py` when a more specific file name is possible.

## CPF — Conversation Plane Filter

CPF names should indicate filtering, inspection, or interception.

### Class naming

Examples:

- `ConversationPlaneFilter`
- `CpfRuleSet`
- `CpfFilterResult`

### Function naming

Examples:

- `filter_action()`
- `inspect_payload()`
- `matches_rule()`

### Module naming

Examples:

- `filter.py`
- `rules.py`
- `inspection.py`

## AIR

AIR names should indicate runtime control, execution, or attestation behavior.

### Class naming

Examples:

- `AgentRuntime`
- `AirRuntimeController`
- `AirExecutionContext`

### Function naming

Examples:

- `start_runtime()`
- `stop_runtime()`
- `attest_execution()`
- `load_runtime_policy()`

### Module naming

Examples:

- `runtime.py`
- `controller.py`
- `attestation.py`

## CTX-ID

Because hyphens are not valid in Python package names, represent `CTX-ID` as `ctx_id` in code and directories.

### Class naming

Examples:

- `ContextIdentity`
- `ContextIdentityResolver`
- `ContextIdentityRecord`

### Function naming

Examples:

- `resolve_identity()`
- `parse_context_id()`
- `validate_identity_claim()`

### Module naming

Examples:

- `identity.py`
- `resolver.py`
- `claims.py`

## PEE — Policy Evaluation Engine

PEE names should indicate evaluation, decisioning, and policy execution.

### Class naming

Examples:

- `PolicyEvaluationEngine`
- `PolicyDecision`
- `PolicyRule`

### Function naming

Examples:

- `evaluate_policy()`
- `apply_rules()`
- `build_decision()`

### Module naming

Examples:

- `evaluation.py`
- `decision.py`
- `rules.py`

## TrustFlow / SIS

These two names may be separate packages or represented as adjacent subsystems under `architecture/`.

### TrustFlow naming

Use names related to trust propagation, signals, or flow state.

Examples:

- `TrustFlowEngine`
- `TrustSignal`
- `TrustFlowRecord`

Functions:

- `emit_trust_signal()`
- `propagate_trust_state()`
- `calculate_trust_score()`

Modules:

- `signals.py`
- `flow.py`
- `scoring.py`

### SIS naming

Use names related to state integration or system state.

Examples:

- `SystemIntegrityState`
- `SisStateStore`
- `SisSnapshot`

Functions:

- `capture_state()`
- `load_snapshot()`
- `validate_state_transition()`

Modules:

- `state.py`
- `snapshot.py`
- `transitions.py`

## CAL Verifier Cluster

Names should indicate verification, clustering, quorum, or validation.

### Class naming

Examples:

- `VerifierCluster`
- `VerifierNode`
- `VerificationResult`

### Function naming

Examples:

- `verify_request()`
- `collect_verdicts()`
- `check_quorum()`

### Module naming

Examples:

- `cluster.py`
- `node.py`
- `quorum.py`
- `results.py`

## Cross-Cutting Code Patterns

### Imports

- Use absolute imports from the root package.
- Keep imports grouped in this order:
  1. standard library
  2. third-party packages
  3. local package imports

Example:

```python
from dataclasses import dataclass

from tasklib.models.task import Task
from tasklib.storage.memory import InMemoryTaskStorage
```

### Public API exposure

- Re-export only stable, intended public symbols in package `__init__.py` files.
- Do not expose internal helpers as part of package top-level imports.

Example:

```python
from tasklib.models.task import Task

__all__ = ["Task"]
```

### Data modeling

- Prefer simple, explicit Python models.
- Use `dataclass` for lightweight domain entities unless mutability or custom behavior requires a regular class.
- Keep model fields explicit and typed.

Example:

```python
from dataclasses import dataclass


@dataclass
class Task:
    id: str
    title: str
    completed: bool = False
```

### Separation of concerns

Maintain strict layer boundaries:

- models define data and invariants
- storage persists and retrieves models
- CLI orchestrates input/output only
- architecture subsystems represent enforcement and policy concepts

Do not place CLI parsing inside model classes.  
Do not place storage-specific serialization logic inside CLI handlers.  
Do not mix policy evaluation logic into unrelated storage or model modules.

### Dependency direction

Dependencies should flow inward toward domain concepts:

- `cli` may depend on `storage` and `models`
- `storage` may depend on `models`
- `models` should not depend on `cli`
- architecture subsystem packages may depend on shared models if introduced, but should avoid depending on CLI code

### Function size and responsibility

- Each function should perform one clear task.
- Prefer small composable functions over large multi-branch procedures.
- If a function name requires “and”, consider splitting it.

### Return conventions

- Return domain objects from model and storage layers.
- Return simple status codes only at CLI or process boundaries.
- Use booleans for predicates only, with names like:
  - `is_valid`
  - `has_quorum`
  - `matches_rule`

### Docstrings

Use short, direct docstrings for public modules, classes, and functions.

Examples:

```python
def create_task(title: str) -> Task:
    """Create a new task with a generated identifier."""
```

Avoid redundant docstrings that merely restate the symbol name.

### Type hints

- Use type hints on all public functions and methods.
- Type annotate model fields and return values.
- Prefer explicit container types in signatures.

Example:

```python
def list_tasks() -> list[Task]:
    ...
```

### Testing-oriented conventions

Because the TRD emphasizes dependency-chain validation and local import resolution:

- Keep package boundaries stable.
- Avoid circular imports.
- Keep module names predictable and explicit.
- Do not dynamically construct imports where static imports are sufficient.
- Ensure previously merged package paths remain valid for downstream modules.

## Naming Summary

### Use

- `snake_case` for files, functions, variables, modules, packages
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `Error` suffix for exceptions

### Avoid

- hyphens in Python package or module names
- vague filenames like `misc.py`
- generic exception types
- cross-layer leakage between CLI, storage, model, and policy subsystems