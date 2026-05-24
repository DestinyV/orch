---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Coding Style (SDD+TDD)

> Extends [common/coding-style.md](../common/coding-style.md).

## Strict Mode Required

- `tsconfig.json` must enable `strict: true`
- No `any` type — use `unknown` and narrow with type guards
- Prefer `interface` over `type` for object shapes that may be extended

## Functional over Class

- Prefer pure functions and composable utilities over class instances
- Use classes only when lifecycle or state encapsulation is strictly necessary
- Avoid inheritance; use composition and dependency injection

## Import Discipline

- Sort imports: external → internal, absolute → relative
- No barrel imports (`index.ts`) that re-export deep dependency trees
- Use `import type` for type-only imports (isolatedModules compat)

## Mode Tag

Every TS/TSX file must start with a mode comment:

```typescript
// #mode: frontend
```

Allowed modes: `frontend`, `backend`, `fullstack`, `shared`
