---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Testing (SDD+TDD)

> Extends [common/testing.md](../common/testing.md).

## Framework

- Unit/Integration: **Vitest** (preferred) or **Jest**
- E2E: **Playwright**

## Test Block Structure

```typescript
describe('UserService', () => {
  it('returns user when valid ID is provided', async () => {
    // Arrange
    // Act
    // Assert
  })
})
```

- `describe` blocks group by service/component/feature
- No nested `describe` beyond two levels
- Test files co-located with source: `user.service.ts` → `user.service.test.ts`

## E2E Conventions

- Use `data-testid` attributes for element targeting — never CSS or XPath
- E2E tests assert on visible content and page state, never implementation details

## Coverage Gate

- Run `vitest --coverage` to verify >= 85% branch coverage
- If coverage check blocks the workflow, review untested branches before increasing the threshold
