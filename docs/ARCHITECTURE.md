# tasklib -- Architecture

> **Scope:** This document describes the architecture of the `tasklib` package -- a validation-focused task management library. tasklib is not a production system; it exists to prove end-to-end dependency chain closure in the Crafted Dev Agent build pipeline.

## 1. Package Structure

tasklib follows a standard Python `src/` layout with three submodules:

```
src/
  tasklib/
    __init__.py          -- package root, re-exports public API
    models/
      __init__.py
      task.py            -- Task dataclass and TaskStatus enumeration
    storage/
      __init__.py
      store.py           -- InMemoryTaskStore
    cli.py               -- CLI entry point
```

### Submodule Overview

| Submodule | Primary File | Responsibility |
|