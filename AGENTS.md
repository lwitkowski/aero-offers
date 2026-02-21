# Agent Guidelines

For project structure, APIs, and local development setup see [README.md](./README.md) and [docs/](./docs/).

## Questions vs Requests
- **Answer questions, don't implement**: When the user asks "how to", "how do I", "what's the best way to", or similar, provide an answer first. Do NOT implement or edit files unless explicitly asked to do so.
- **Ask before implementing**: If the request is ambiguous (e.g., "add X" could mean explain or implement), ask which the user wants before making changes.

## Git Operations
- **NEVER commit without explicit permission**: When asked to "prepare commit message" or similar, only output the message text. Do NOT run `git commit`. Wait for explicit instruction like "commit this" or "make the commit".
- **NEVER push without explicit approval**: After committing, stop and show the diff for review. Wait for the user to approve before pushing.
- **NEVER run destructive git commands** (`push --force`, `reset --hard`, `rebase`, branch deletion) without explicit user approval.

## Commit Messages
- **Imperative mood**: Start with a verb (e.g., "Add", "Fix", "Remove", "Migrate")
- **Concise**: One line, describe what changed, not why. Then empty line, then a list of detailed highlights if that makes everything more clear
- **Group related changes**: Use commas to list multiple related changes (e.g., "Add X, remove Y, update Z")
- **No period**: Don't end with a period