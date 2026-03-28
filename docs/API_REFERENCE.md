# tasklib -- API Reference

> **Status:** This document describes the **planned** public API surface for `tasklib`. All signatures, behaviors, and examples below represent the design contract derived from [TRD-TASKLIB](../crafted-docs/TRD-TASKLIB.md). Implementation PRs must conform to these specifications.

## Table of Contents

- [TaskStatus](#taskstatus)
- [Task](#task)
- [InMemoryTaskStore](#inmemorytaskstore)
- [cli.main](#climain)
- [Exceptions](#exceptions)

---

## TaskStatus

```python
class TaskStatus(enum.Enum):
    PENDING = "pending"
    DONE = "done"
```

**Module:** `tasklib.models.task`

**Re-exported from:** `tasklib`

An enumeration representing the lifecycle state of a task.

| Member | Value | Description |
|