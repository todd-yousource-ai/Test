# tasklib API Reference

Complete public API reference for tasklib -- all public types, store methods, and CLI commands.

For the library overview and quickstart, see [README.md](README.md).
For the architecture and package layout, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Table of Contents

- [Model Layer](#model-layer)
  - [TaskStatus](#taskstatus)
  - [Task](#task)
- [Storage Layer](#storage-layer)
  - [InMemoryTaskStore](#inmemorytaskstore)
- [CLI](#cli)
  - [add command](#add-command)
  - [list command](#list-command)
  - [complete command](#complete-command)

---

## Model Layer

**Module:** `tasklib.models.task`

**Import path:** `from tasklib import Task, TaskStatus`

### TaskStatus

An enumeration representing the status of a task.

```python
class TaskStatus(enum.Enum):
    PENDING = "pending"
    DONE = "done"
```

| Value | Description |
|