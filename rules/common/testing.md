# Testing Requirements (SDD+TDD)

## TDD Cycle: RED → GREEN → REFACTOR → REVIEW

Mandatory sequence for every unit of work:

1. **RED** — Write a failing test that describes the desired behavior
2. **GREEN** — Write the minimal implementation to pass
3. **REFACTOR** — Clean up without changing behavior; re-run tests
4. **REVIEW** — Multi-phase review (lint → spec compliance → architecture)

## Coverage Requirements

- Overall coverage: **>= 85%** (measured by branch coverage)
- Critical paths (auth, payments, data export): >= 95%
- No mocking of business logic — mock only external boundaries (APIs, databases, filesystem)

## Test Structure

- One assertion per test case
- Use AAA pattern (Arrange-Act-Assert)
- Test names must read as a sentence describing the expected outcome
- E2E tests must reference `data-testid` attributes, never CSS class or XPath selectors

## HARD-GATE Enforcement

- If coverage drops below the threshold, the workflow **HARD-GATE** blocks progression to the next phase
- See `workflow` skill for gate override procedures
