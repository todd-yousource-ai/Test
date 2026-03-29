# tasklib

**tasklib** is a deliberately simple Python task management library whose sole purpose is to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain -- from documentation through scaffold to working code -- with real merges at each step. It is not a production system.

## Package Structure

The library follows a standard Python package layout under `src/`:

```
src/
  tasklib/
    __init__.py          -- package root, re-exports public API (Task, InMemoryTaskStore)
    models/
      __init__.py
      task.py            -- Task dataclass and TaskStatus enumeration
    storage/
      __init__.py
      store.py           -- InMemoryTaskStore
    cli.py               -- CLI entry point
```

## Installation

tasklib uses **only the Python standard library**. There are no third-party dependencies and no `pip install` step is required. Any Python 3.10+ interpreter can run it directly from the source tree.

## Usage Examples

### 1. Creating a Task

Create a `Task` with a title and inspect its auto-populated fields:

```python
from tasklib.models.task import Task, TaskStatus

task = Task(title="Write unit tests")

print(task.id)          # e.g. "a1b2c3d4-..." (auto-generated UUID string)
print(task.title)       # "Write unit tests"
print(task.status)      # TaskStatus.PENDING (default)
print(task.created_at)  # e.g. datetime(2026, 3, 26, 14, 30, 0, ...) (auto-populated)
```

The `id` field is a UUID string assigned automatically at creation. The `status` field defaults to `TaskStatus.PENDING`. The `created_at` field is set to the current UTC datetime when the task is instantiated.

### 2. Using InMemoryTaskStore

Use `InMemoryTaskStore` to add, list, complete, and delete tasks:

```python
from tasklib import Task, InMemoryTaskStore

store = InMemoryTaskStore()

# Add a task -- returns the newly created Task
task = store.add("Deploy to staging")
print(task.id)      # auto-generated UUID string
print(task.title)   # "Deploy to staging"
print(task.status)  # TaskStatus.PENDING

# List all tasks
all_tasks = store.list_all()
print(len(all_tasks))  # 1

# Complete a task -- transitions status to COMPLETE
completed = store.complete(task.id)
print(completed.status)  # TaskStatus.COMPLETE

# Retrieve a single task by ID
fetched = store.get(task.id)
print(fetched.title)  # "Deploy to staging"

# Delete a task
store.delete(task.id)
print(len(store.list_all()))  # 0
```

### 3. CLI Invocation

The CLI is runnable as a Python module via `python -m tasklib.cli`. It supports three subcommands: `add`, `list`, and `complete`.

```bash
# Add a task
$ python -m tasklib.cli add "Fix login bug"
Created task: a1b2c3d4-5678-9abc-def0-1234567890ab -- Fix login bug

# List all tasks
$ python -m tasklib.cli list
a1b2c3d4-5678-9abc-def0-1234567890ab  PENDING  Fix login bug

# Complete a task
$ python -m tasklib.cli complete a1b2c3d4-5678-9abc-def0-1234567890ab
Completed task: a1b2c3d4-5678-9abc-def0-1234567890ab -- Fix login bug
```

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) -- layered dependency design and build order
- [API.md](API.md) -- complete API reference for all public types, methods, and CLI commands