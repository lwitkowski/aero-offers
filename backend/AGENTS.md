# Backend Module - AI Agent Guide

Quick reference for non-obvious patterns and conventions.

## Key Patterns

**Spiders**: Extract into `_extract_*` methods, inline calls, no redundant variables. Motorplanes = `AircraftCategory.airplane`, gliders = `AircraftCategory.glider`.

**Code**
- Don't add comments that are obvious from the code
- always check ruff linter and mypy rules (via `uv`) before creating PR

**Tests**: 
- Use `# given` / `# when` / `# then` structure for all tests

## Tools
- `uv` (not pip), `ruff`, `mypy` (strict), `pytest` (80% coverage min)