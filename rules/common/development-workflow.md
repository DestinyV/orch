# Development Workflow (SDD+TDD 10-Step)

> See [zh/development-workflow.md](../zh/development-workflow.md) for Chinese version.

## Flow Overview

```
spec-creation → test-design + code-design → api-contract → code-task → code-execute → code-test → spec-archive → knowledge-continuum
```

1. **spec-creation** — Analyze requirement, produce BDD scenarios, data models, business rules
2. **test-design** — Generate test specs, fixtures, and templates from spec scenarios (parallel with step 3)
3. **code-design** — Architecture design, database schema, interface contracts (parallel with step 2)
4. **api-contract** — Formalize API contracts, review for consistency (fullstack only)
5. **code-task** — Decompose design into concrete implementation tasks
6. **code-execute** — Implement each Task in isolated git worktree with subagent
7. **code-test** — Integration, E2E, and performance verification
8. **spec-archive** — Merge validated spec into master spec repository
9. **evaluate** — Measure effectiveness, token usage, gate check
10. **knowledge-continuum** — Extract decisions and patterns into knowledge base

## HARD-GATE Card

Between steps 7→8 and 8→9, a **HARD-GATE** evaluates quality criteria (coverage, test pass rate, spec compliance). Failure blocks the pipeline and triggers a compensation workflow.
