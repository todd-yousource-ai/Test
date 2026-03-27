# tasklib -- Architecture

This document describes the layered architecture of tasklib, the five-layer dependency chain, package layout, dependency rules, and key design decisions.

## Overview

tasklib is structured as a linear dependency chain where each layer depends only on the layers below it. The architecture is intentionally simple -- it exists to validate the Crafted Dev Agent build pipeline, not to solve a complex domain problem.

## Five-Layer Dependency Chain

The library is delivered as five sequential PRs, each representing one layer. Every layer depends on the successful merge of the layer immediately before it:

```
┌─────────────────┐
│   1. Docs        │   README.md, ARCHITECTURE.md, API.md
├─────────────────┤
        ↓
┌─────────────────┐
│   2. Scaffold    │   Package directories and __init__.py files
├─────────────────┤
        ↓
┌─────────────────┐
│   3. Models      │   Task dataclass, TaskStatus enum
├─────────────────┤
        ↓
┌─────────────────┐
│   4. Storage     │   InMemoryTaskStore
├─────────────────┤
        ↓
┌─────────────────┐
│   5. CLI         │   Command-line interface (cli.py)
└─────────────────┘
```

**Docs → Scaffold → Models → Storage → CLI**

Each arrow represents a merge-gate dependency: the downstream layer cannot begin until the upstream layer has been merged successfully.

## Layer Responsibilities

| Layer | PR | Responsibility | Outputs |
|