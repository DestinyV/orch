---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Patterns (SDD+TDD)

> Extends [common/patterns.md](../common/patterns.md).

## React Hooks Pattern

- Custom hooks start with `use`, return a `UseXxxResult` interface
- Keep effects minimal; extract side-effect logic into services
- Use `useMemo`/`useCallback` only when profiling shows a bottleneck

## Service / Repository Pattern

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>
  save(user: CreateUserDto): Promise<User>
}

class ApiUserRepository implements UserRepository {
  constructor(private readonly http: HttpClient) {}
  // ...
}
```

## DTOs at API Boundaries

- Define explicit CreateDto, UpdateDto, ResponseDto for every API endpoint
- Validate with Zod schemas at the boundary; typed DTOs flow inward

## Error Boundaries

- One error boundary per route segment in frontend apps
- Fallback UI must display a user-friendly message and a retry action
