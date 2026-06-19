# Development Workflow (SDD+TDD 13-Step)

> See [zh/development-workflow.md](../zh/development-workflow.md) for Chinese version.

## Flow Overview

```
spec → test-design + design → contract → task → execute → test → archive → continuous-learning
```

1. **spec** — Analyze requirement, produce BDD scenarios, data models, business rules
2. **test-design** — Generate test specs, fixtures, and templates from spec scenarios (parallel with step 3)
3. **design** — Architecture design, database schema, interface contracts (parallel with step 2)
4. **contract** — Formalize API contracts, review for consistency (fullstack only)
5. **task** — Decompose design into concrete implementation tasks
6. **execute** — Implement each Task in isolated git worktree with subagent
7. **test** — Integration, E2E, and performance verification
8. **archive** — Merge validated spec into master spec repository
9. **evaluate** — Measure effectiveness, token usage, gate check
10. **continuous-learning** — Extract decisions and patterns into knowledge base

## HARD-GATE Card

Between steps 7→8 and 8→9, a **HARD-GATE** evaluates quality criteria (coverage, test pass rate, spec compliance). Failure blocks the pipeline and triggers a compensation workflow.
