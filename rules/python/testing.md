---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Testing (SDD+TDD)

> Extends [common/testing.md](../common/testing.md).

## Framework

- **pytest** with `pytest-asyncio` for async test support

## Fixtures

- Use `conftest.py` for shared fixtures at each directory level
- Scope fixtures appropriately: `session` for DB connection, `function` for state isolation

```python
@pytest.fixture(scope="function")
async def db_session():
    async with get_session() as session:
        yield session
```

## Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("", 0),
    ("a b", 3),
])
def test_length(input: str, expected: int):
    assert len(input) == expected
```

## Async Test Support

```python
@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await user_service.create(db_session, ...)
    assert user.id is not None
```

## Coverage

```bash
pytest --cov=src --cov-branch --cov-fail-under=85
```
