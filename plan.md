# Address Explicit TODOs and Code Smells

- [x] Enforce Type Checking and Linting
- [x] Enable stricter mypy checks in setup.cfg (e.g., warn_return_any = True, remove ignore_missing_imports if possible).
- [x] Add or improve type hints throughout the codebase.
- [x] Ensure all code passes ruff and pyright checks.

# Improve Error Handling

- [ ] Refactor error handling to avoid silent failures. Raise exceptions where appropriate or handle them in a way that surfaces issues.
- [ ] Avoid overly broad exception handling; catch specific exceptions and handle them meaningfully.

# Increase Test Coverage and Quality

- [x] Write tests for all critical paths, especially for queue/event handling and external integrations.
- [ ] Use coverage tools to identify untested code.
- [ ] Refactor tests for clarity and maintainability.

# Refactor for Modularity and Maintainability

- [ ] Decouple tightly coupled components (e.g., move sender logic to its own module).
- [ ] Break up large functions/classes into smaller, single-responsibility units.

# Documentation and Comments

- [ ] Add docstrings to all public classes and functions.
- [ ] Update and maintain doc.md as you address each item.
- [ ] Document error handling strategies and expected flows.

