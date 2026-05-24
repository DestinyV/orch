---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Coding Style (SDD+TDD)

> Extends [common/coding-style.md](../common/coding-style.md).

## Standards

- Follow **PEP 8** — 4-space indentation, 100-char line limit
- Use **type hints** on all function signatures (Python 3.10+ syntax preferred)
- Format with **black**, sort imports with **isort**, lint with **ruff**

## Data Classes

- Use `@dataclass` for DTOs and value objects
- Use `frozen=True` for immutable data objects
- Use `NamedTuple` for simple key-value containers

## FastAPI Patterns

- Route handlers depend on services via type-annotated parameters (fastapi.Depends)
- Validate request bodies with Pydantic v2 models
- Return Pydantic models from route handlers — FastAPI serializes automatically

## Mode Tag

Every Python file must start with a mode comment:

```python
# mode: backend
```

Allowed modes: `backend`, `fullstack`, `shared`, `script`
