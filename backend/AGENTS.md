# Backend Module - AI Agent Guide

Quick reference for non-obvious patterns and conventions.

## Key Patterns

**Code**
- Don't add comments that are obvious from the code

**Tests**: 
- Use `# given` / `# when` / `# then` structure for all tests

## Tools
- `uv` (not pip), `ruff`, `mypy` (strict), `pytest` (80% coverage min)

**Creating PR**:

**BEFORE creating ANY PR, you MUST complete ALL of the following:**
1. **Linting**: Run `uv run ruff check` on all files (not only modified) and fix any issues
2. **Type checking**: Run `uv run mypy` on all files (not only modified) and fix any issues
3. **ALL tests**: Run `uv run pytest` (ALL backend tests, not just related ones) and fix any failures
4. **Verify**: All checks must pass before creating the PR

**This checklist is MANDATORY - do not skip any step.**

- Keep descriptions simple and focused on functional changes only
- Group changes by component when relevant
- Don't mention obvious things: linting fixes, test updates, pre-PR check status (expected anyway)
- Don't include implementation details that are obvious from code
- Don't mention temporary changes unless they're the main focus of the PR
- When adding reasons/justifications: only include claims that are directly supported by the code changes or commit messages. Don't make assumptions about motivations (e.g., cost optimization, architectural patterns) unless explicitly stated in the code or commit
