# Backend Module - AI Agent Guide

Quick reference for non-obvious patterns and conventions.

## Key Patterns

**Spiders**: Extract into `_extract_*` methods, inline calls, no redundant variables. Motorplanes = `AircraftCategory.airplane`, gliders = `AircraftCategory.glider`.

**Tests**: Update HTML samples with real data when website changes. Test with/without optional fields.

**Refactoring**: Extract commented sections → methods. Remove redundant conditionals (if field accepts None, assign directly).

- **DRY principle**: Use consistent resource names across all references. If renaming resources, update ALL references immediately. Same for entities (e.g. terraform resources) don't create something just because it may be needed in the future.

## Tools
- `uv` (not pip), `ruff`, `mypy` (strict), `pytest` (80% coverage min)