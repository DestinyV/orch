# Security Guidelines (SDD+TDD)

## Mandatory Checks (Pre-Commit)

- [ ] No hardcoded secrets (API keys, passwords, tokens, connection strings)
- [ ] All user inputs validated at system boundaries
- [ ] Parameterized queries for all database operations
- [ ] Output sanitized for XSS prevention
- [ ] Error responses do not leak stack traces or internal paths

## SDD+TDD Security Integration

- Security scenarios are part of spec-creation: every spec MUST include security acceptance criteria
- Security test cases are generated during test-design alongside functional tests
- HARD-GATE evaluates security test pass rate before allowing archive

## Secret Handling

- Use environment variables or a secrets manager (e.g., Vault, AWS Secrets Manager)
- Validate required secrets exist at application startup — fail fast
- `.env` files are NEVER committed; add to `.gitignore` at project root
