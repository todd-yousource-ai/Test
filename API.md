# tasklib -- API Reference

This document defines the complete public API contract for tasklib. All types, method signatures, parameters, return values, and error behaviors are specified here. Downstream PRs and consumers treat this document as the authoritative source of truth.

## Module: `tasklib.models.task`

### `TaskStatus` (Enum)

An enumeration of possible task states.

```python
class TaskStatus(enum.Enum):
    PENDING = "pending"
    DONE = "done"
```

| Value | Description |
|