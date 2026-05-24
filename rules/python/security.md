---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Security (SDD+TDD)

> Extends [common/security.md](../common/security.md).

## SQL Injection Prevention

- **Never** use f-strings or string concatenation for SQL queries
- Use SQLAlchemy ORM / Core with bound parameters
- For raw SQL, always use `text()` with `:param` style binding

```python
# CORRECT
from sqlalchemy import text
result = await db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

## Input Sanitization

- Use Pydantic validators for input normalization and rejection of malicious payloads
- Set `max_length` on all string fields to prevent resource exhaustion

## JWT Handling

- Verify tokens with a library (PyJWT, python-jose) — never implement manual HMAC
- Validate `exp`, `iat`, `iss` claims on every request
- Rotate signing keys on a schedule; support key rotation via `jwks` endpoint

## SDD+TDD Integration

- Security scenarios from spec-creation are mapped to `@pytest.mark.security` tests
- HARD-GATE requires all security-marked tests to pass before archive
