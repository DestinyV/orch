# Usage Guide

## Workflow

```
/spec → /test-design + /design → /task → /execute → /test → /archive
```

## Stages

| Stage | Command | Input | Output |
|-------|---------|-------|--------|
| Spec | `/spec [req]` | Description | `spec-dev/{id}/spec/` |
| Test Design | `/test-design` | spec | `tests/test-spec-creation.md + fixtures.json + test-*.template` |
| Design | `/design` | spec | `design/design.md` |
| Task | `/task` | design.md | `tasks/tasks.md` |
| Execute | `/execute` | tasks + tests | `src/ + execution-report.md` |
| Test | `/test` | src + spec | `testing-report.md` |
| Archive | `/archive` | Passed spec | Merged to main spec |

Note: test-design and code-design can run in parallel.

## Full-Stack Projects

When `project-mode: fullstack`:
- code-design adds database design and API contract
- api-contract auto-triggers between code-design and code-task
- code-execute auto-calls exception-handler

## Work Modes

| Mode | standard (default) | quick |
|------|-------------------|-------|
| TDD | Required | Optional |
| Sub-agent | Required | Optional |
| Review | Two-stage | Single-stage |
| Coverage | ≥85% | ≥60% |
