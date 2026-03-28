# Code Conventions

This document defines coding conventions derived from the provided TRD materials. It covers the task management library and the architecture subsystems explicitly named in the architecture context. All conventions are written to be implementation-neutral where details are not specified in the TRDs, while preserving the required structure and dependency flow.

## File and Directory Naming (exact `src/` layout)

The task management library must use a `src/` layout and preserve a dependency chain of:

`docs → scaffold → model → storage → CLI`

Exact package layout:

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

Recommended documentation layout to mirror the TRD documentation set:

```text
README.md
ARCHITECTURE.md
API.md
```

If tests are present, keep them outside `src/`:

```text
tests/
```

### Directory naming rules

- Use lowercase directory names.
- Use plural nouns for package directories that group related modules:
  - `models/`
  - `storage/`
- Use short functional names for top-level feature packages:
  - `cli/`
- Do not use hyphens in Python package or module directories.
- Do not introduce deep nesting unless the subsystem boundary is clear in the TRD.

### Module naming rules

- Use lowercase snake_case for all Python module filenames.
- Prefer noun-based modules for domain entities:
  - `task.py`
  - `task_repository.py`
- Prefer verb or role-based modules for operational helpers:
  - `create_task.py`
  - `formatter.py`
- CLI entry modules should be explicit:
  - `main.py`
  - `commands.py`
- Avoid generic names such as:
  - `utils.py`
  - `helpers.py`
  - `misc.py`

### `__init__.py` rules

- Every package directory under `src/` must include `__init__.py`.
- `__init__.py` may re-export stable public interfaces only.
- Do not place substantial business logic in `__init__.py`.

---

## Class and Function Naming

### General naming rules

- Classes: `PascalCase`
- Functions and methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal helpers: prefix with single underscore, e.g. `_validate_id`
- Exception classes: suffix with `Error`
- Abstract or protocol-style interfaces: use role-based suffixes such as `Repository`, `Store`, `Formatter`, or `Verifier`

### Class naming patterns

Use nouns for data/domain classes:

```python
class Task:
    ...
```

Use role-oriented names for behavior-bearing classes:

```python
class TaskRepository:
    ...

class TaskFormatter:
    ...
```

Use subsystem-qualified names where ambiguity is possible:

```python
class ConversationPolicyEvaluator:
    ...
class ConversationPlaneFilter:
    ...
class PolicyEnforcementEngine:
    ...
```

Avoid vague names like:

- `Manager`
- `Processor`
- `Handler`

unless the subsystem terminology in the TRD explicitly supports them.

### Function naming patterns

Functions should describe a single action clearly:

```python
def create_task(...)
def get_task(...)
def list_tasks(...)
def delete_task(...)
```

Boolean-returning functions should read as predicates:

```python
def is_complete(...)
def has_policy_violation(...)
def can_execute(...)
```

Factory-style functions should use:

```python
def from_dict(...)
def from_env(...)
def build_context(...)
```

CLI functions should reflect command semantics:

```python
def run(...)
def parse_args(...)
def cmd_add(...)
def cmd_list(...)
```

### Public API naming

- Public APIs must use stable, explicit names.
- Avoid abbreviations unless the abbreviation is a subsystem term already defined in the TRD, such as:
  - `CAL`
  - `CPF`
  - `AIR`
  - `CTX_ID`
  - `PEE`
  - `SIS`

When abbreviations from the TRD are used in code:
- Prefer full class names for readability.
- Use acronym names only where the subsystem is itself known by that acronym.

Example:

```python
class ConversationAbstractionLayer:
    ...
```

over:

```python
class CAL:
    ...
```

except where the acronym is the primary external interface.

---

## Error and Exception Patterns

### Base rules

- Raise exceptions for invalid state, invalid input, storage failures, and policy enforcement failures.
- Do not silently swallow exceptions.
- Do not return error strings in place of structured failures.
- Catch exceptions only when:
  - adding context,
  - translating infrastructure exceptions into domain exceptions,
  - or producing CLI-safe user output.

### Exception naming

All custom exceptions must end with `Error`.

Examples:

```python
class TaskError(Exception):
    pass

class TaskValidationError(TaskError):
    pass

class TaskNotFoundError(TaskError):
    pass

class StorageError(Exception):
    pass

class PolicyEvaluationError(Exception):
    pass

class PolicyDeniedError(PolicyEvaluationError):
    pass
```

### Exception hierarchy

Use subsystem-local base exceptions.

Recommended pattern:

```python
Exception
├── TaskLibError
│   ├── TaskValidationError
│   ├── TaskNotFoundError
│   └── TaskConflictError
├── StorageError
│   ├── StorageReadError
│   └── StorageWriteError
├── CliError
└── PolicyError
    ├── PolicyEvaluationError
    ├── PolicyDeniedError
    └── VerificationError
```

### Translation rules

- Model layer raises domain errors.
- Storage layer translates backend-specific exceptions into storage errors.
- CLI layer catches known exceptions and renders concise user-facing messages.
- Policy subsystems translate low-level verification or identity failures into policy-domain exceptions.

### Error message rules

- Messages must be actionable and concise.
- Include identifiers when available.
- Do not include secrets, cryptographic material, or internal policy details in error text.

Preferred:

```python
raise TaskNotFoundError(f"Task not found: {task_id}")
```

Avoid:

```python
raise Exception("Something went wrong")
```

### Validation rules

Validate at subsystem boundaries:
- input parsing,
- model construction,
- storage writes,
- policy evaluation requests,
- CLI argument handling.

Use `ValueError` only for small internal helpers. Use custom exceptions for public and subsystem-facing boundaries.

---

## Per-Subsystem Naming Rules

## Task Management Library

The task management library is the reference implementation for the validation pipeline and must preserve explicit dependency ordering.

### Package naming

Use the root package:

```text
tasklib
```

Subpackages:

- `tasklib.models`
- `tasklib.storage`
- `tasklib.cli`

### Model naming

- Domain entities use singular nouns:
  - `Task`
- Validation-focused errors use entity-prefixed names:
  - `TaskValidationError`
  - `TaskNotFoundError`
- Serialization helpers should be explicit:
  - `to_dict`
  - `from_dict`

Do not use plural class names such as `Tasks`.

### Storage naming

Storage code should use repository or store terminology consistently.

Preferred:

- `TaskRepository`
- `InMemoryTaskRepository`
- `FileTaskRepository`

Methods:

- `save_task`
- `get_task`
- `list_tasks`
- `delete_task`

If CRUD-style naming is used, use it consistently across the interface:
- `create`
- `read`
- `list`
- `update`
- `delete`

Do not mix both styles arbitrarily within the same abstraction.

### CLI naming

CLI command functions should mirror user verbs:

- `add`
- `list`
- `show`
- `remove`
- `complete`

Python function names should be command-safe and explicit:

- `cmd_add`
- `cmd_list`
- `cmd_show`

CLI modules should separate:
- argument parsing,
- command dispatch,
- output formatting.

Preferred file split:

```text
src/tasklib/cli/
  main.py
  commands.py
  formatters.py
```

---

## CAL — Conversation Abstraction Layer

The TRD identifies CAL as the enforcement choke point for all agent-originated action. Naming must reflect gatekeeping and evaluation semantics.

### Class naming

Preferred names:

- `ConversationAbstractionLayer`
- `ConversationActionRequest`
- `ConversationActionResult`
- `ConversationPolicyEvaluator`
- `ConversationVerifier`

Avoid generic names such as `LayerManager` or `ActionHandler`.

### Function naming

Use evaluation and enforcement verbs:

- `evaluate_action`
- `authorize_action`
- `verify_request`
- `enforce_policy`
- `resolve_context`

Boolean predicates:

- `is_action_allowed`
- `has_required_identity`

### Module naming

Preferred module names:

- `conversation_abstraction_layer.py`
- `policy_evaluator.py`
- `verifier.py`
- `action_request.py`

If acronym-based modules are necessary, use lowercase:
- `cal.py`

Prefer full names in modules intended for broad use.

---

## CPF — Conversation Plane Filter

CPF is identified as a key component beneath CAL. Even where detailed behavior is not specified, naming must preserve filter semantics.

### Class naming

Preferred names:

- `ConversationPlaneFilter`
- `PlaneFilterRule`
- `PlaneFilterDecision`

### Function naming

Use filter-oriented verbs:

- `filter_request`
- `apply_filter`
- `match_rule`
- `reject_request`
- `allow_request`

### Error naming

Preferred exceptions:

- `ConversationPlaneFilterError`
- `FilterRuleError`
- `FilterDeniedError`

### Module naming

Preferred modules:

- `conversation_plane_filter.py`
- `filter_rules.py`
- `filter_decision.py`

---

## AIR

AIR is named as a key component in the architecture context and should keep acronym-stable naming where expanded naming is unavailable from the TRD.

### Naming rule

Because no expansion is provided in the source text, preserve the acronym in public interfaces.

Preferred names:

- `AIRContext`
- `AIRRequest`
- `AIRVerifier`
- `AIRPolicyAdapter`

Module names:

- `air.py`
- `air_context.py`
- `air_verifier.py`

Do not invent an expanded form not present in the TRD.

---

## CTX-ID

CTX-ID is explicitly named in the architecture context and must be normalized for code while retaining its source identity.

### Identifier normalization

Because hyphens are invalid in Python identifiers:
- Use `CTX_ID` for constants and symbolic references.
- Use `CtxId` or `ContextId` for class names depending on whether the type is acronym-preserving or readability-first.
- Use `ctx_id` for variables, fields, and parameters.

### Preferred naming

Classes:
- `ContextId`
- `ContextIdentity`
- `CtxIdResolver`

Functions:
- `resolve_ctx_id`
- `validate_context_id`
- `attach_context_id`

Modules:
- `context_id.py`
- `ctx_id_resolver.py`

Avoid:
- `ctx-id.py`
- `CTX-ID.py`

---

## PEE — Policy Enforcement Engine

PEE is identified as a key component and should be named with enforcement semantics.

### Class naming

Preferred names:

- `PolicyEnforcementEngine`
- `PolicyDecision`
- `PolicyDecisionContext`
- `PolicyEnforcementResult`

### Function naming

Use decisive verbs:

- `evaluate_policy`
- `enforce`
- `deny`
- `allow`
- `build_decision_context`

### Error naming

Preferred exceptions:

- `PolicyEnforcementError`
- `PolicyDeniedError`
- `PolicyContextError`

### Module naming

Preferred modules:

- `policy_enforcement_engine.py`
- `policy_decision.py`
- `decision_context.py`

---

## TrustFlow / SIS

The architecture context names `TrustFlow/SIS` as a key component. Since the exact relationship is not fully specified, naming should preserve both terms without inventing semantics.

### Naming rule

- Use `TrustFlow` and `SIS` as distinct code identifiers unless the TRD later defines a merged abstraction.
- If a combined abstraction is required, prefer `TrustFlowSIS`.

### Preferred names

Classes:
- `TrustFlow`
- `SISVerifier`
- `TrustFlowRecord`
- `TrustFlowSISBridge`

Functions:
- `verify_trust_flow`
- `sync_sis_state`
- `record_trust_event`

Modules:
- `trustflow.py`
- `sis_verifier.py`
- `trustflow_sis.py`

Do not replace these with generic trust or identity names that lose the TRD terminology.

---

## CAL Verifier Cluster

The verifier cluster should use verifier and cluster terminology consistently.

### Class naming

Preferred names:

- `CALVerifierCluster`
- `VerifierNode`
- `VerifierQuorum`
- `VerificationResult`

### Function naming

- `verify`
- `verify_request`
- `collect_verifications`
- `reach_quorum`
- `aggregate_results`

### Error naming

- `VerificationError`
- `VerifierUnavailableError`
- `QuorumNotReachedError`

### Module naming

- `cal_verifier_cluster.py`
- `verifier_node.py`
- `verification_result.py`

---

## Cross-Subsystem Conventions

### Import conventions

- Use absolute imports within `src/`.
- Imports must follow dependency direction.
- Higher-level modules may depend on lower-level modules, but not the reverse.

For the task management library:

- `cli` may import from `storage` and `models`
- `storage` may import from `models`
- `models` must not import from `storage` or `cli`

### Dependency boundary naming

If an abstraction is shared across subsystem boundaries, name it by its role, not its implementation:

Preferred:
- `TaskRepository`
- `PolicyEvaluator`
- `Verifier`

Avoid:
- `JsonThing`
- `DefaultManager`

### Data type naming

- Request/response objects should use suffixes:
  - `Request`
  - `Response`
  - `Result`
  - `Decision`
- Persistent or domain records should use:
  - `Record`
  - `Entry`
  - `Task`

### Acronym handling

When a subsystem acronym is defined in the TRD:
- preserve the acronym in module-level documentation and subsystem references,
- prefer readable expanded class names if the expansion is known,
- preserve the acronym when no reliable expansion is provided.

Examples:
- `ConversationAbstractionLayer` for CAL
- `PolicyEnforcementEngine` for PEE
- `AIRVerifier` for AIR

### Documentation naming

Required top-level documentation files should use exact uppercase names where specified:

- `README.md`
- `ARCHITECTURE.md`
- `API.md`

If generated docs mirror subsystem packages, use lowercase snake_case file naming inside docs directories.

---

## Prohibited Patterns

- Hardcoded product names not present as generic subsystem terminology in the TRDs
- Hyphenated Python module filenames
- Circular imports across `models`, `storage`, and `cli`
- Catch-all `except Exception:` without re-raising or translation
- Generic modules like `utils.py` when a domain-specific name is possible
- Generic class names like `Manager`, `Handler`, or `Processor` without clear subsystem meaning
- Silent policy denials without a structured decision or error outcome

---

## Minimum Naming Checklist

Before merging code, verify:

- File names are lowercase snake_case
- Package layout matches `src/` conventions
- Classes are `PascalCase`
- Functions and methods are `snake_case`
- Exceptions end with `Error`
- Subsystem names match TRD terminology
- Acronyms are only expanded when the TRD provides the expansion
- Imports follow the required dependency chain
- CLI naming mirrors command verbs
- Policy and verification components use explicit enforcement vocabulary