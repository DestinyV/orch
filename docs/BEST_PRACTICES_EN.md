# SDD Best Practices Guide

## Core Principles

1. **Spec-First** — Everything starts from `/spec`, spec is the single source of truth
2. **Design-Driven** — `/design` design approval required before Task stage
3. **TDD Flow** — RED → GREEN → REFACTOR → REVIEW
4. **Agent Isolation** — standard mode: each Task uses independent sub-agent + worktree
5. **Two-Stage Review** — Spec review → Quality review (Lint/types/coverage)

## Stage Checklists

### Spec
- [ ] Scenarios in WHEN-THEN format
- [ ] Each Case has TEST-VERIFY acceptance criteria
- [ ] Each Case has Mock Data definition
- [ ] Frontend scenarios have BROWSER-TESTABLE

### Test Design
- [ ] TEST-VERIFY 100% mapped to Test Cases
- [ ] fixtures.json has valid/boundary/special values
- [ ] Test skeleton code is runnable

### Design
- [ ] Fullstack: database design and API contract complete
- [ ] API contract confirmed by both sides
- [ ] Design decisions have rationale and trade-offs

### Task
- [ ] Task granularity moderate (≤4h)
- [ ] Dependencies accurate and acyclic
- [ ] Test Case mapping complete

### Execute
- [ ] TDD four stages fully executed
- [ ] Coverage ≥85% (standard) / ≥60% (quick)
- [ ] No pseudo-code / empty function bodies
- [ ] Backend/fullstack called exception

### Test
- [ ] Frontend executed browser E2E tests
- [ ] Contract tests passed (fullstack)
- [ ] TEST-VERIFY → Test → Code fully corresponds

### Archive
- [ ] All conflicts marked DECISION_NEEDED
- [ ] Archive report generated
- [ ] Version number incremented correctly

## Common Anti-Patterns

- ❌ Skip design and code directly
- ❌ Modify source logic to make tests pass
- ❌ Continue to next Task without fixing issues
- ❌ Use console/print to fake implementations
- ❌ Ignore closed-loop verification (Task-test correspondence)
