# Coding Style (SDD+TDD)

## Naming Conventions

- **JS/TS:** camelCase for variables/functions, PascalCase for classes/components, UPPER_SNAKE_CASE for constants
- **Python:** snake_case for variables/functions, PascalCase for classes
- Booleans: prefix with `is`, `has`, `should`, or `can`

## Prohibited Patterns

- **No comment-only code** — never write code that does nothing except hold a comment. If logic is missing, implement it or remove the comment.
- **No pseudo-code** — code must compile and run. Placeholder implementations (e.g., `// TODO: implement`) are not allowed in committed code.

## SDD+TDD Conventions

- All production code must be traceable to a spec scenario (requirement.md → scenario → implementation)
- Feature flags gate new behavior; never ship speculative code paths
- Every file must declare its mode tag in its header: `// #mode: frontend` / `# mode: backend` / `# mode: fullstack`
