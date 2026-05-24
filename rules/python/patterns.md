---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Patterns (SDD+TDD)

> Extends [common/patterns.md](../common/patterns.md).

## Repository Pattern

```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: str) -> User | None: ...
    @abstractmethod
    async def save(self, user: User) -> User: ...
```

## Dependency Injection

- Use FastAPI's `Depends` for request-scoped dependencies
- Use `functools.lru_cache` or `functools.singledispatch` for module-level DI
- Avoid global mutable state — thread safety matters in async context

## Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: Literal["admin", "member"] = "member"
```

## Error Handling

- Define custom exception classes per domain
- Use middleware-level exception handlers in FastAPI to map exceptions to HTTP responses
- Log structured context; never log raw request bodies containing secrets
