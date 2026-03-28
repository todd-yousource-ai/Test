# tasklib -- API Reference

This document defines the complete public API contract for the `tasklib` library. All types, method signatures, return types, error behaviors, and CLI commands documented here are **binding** -- downstream implementation PRs must conform to this specification exactly.

## Package Re-Export Contract

The package root `tasklib/__init__.py` **must** re-export the following names:

| Name | Source Module |
|