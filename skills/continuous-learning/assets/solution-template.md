# Solution Templates

Choose template matching the problem_type track (see `references/solution-schema.yaml`).

---

## Bug Track Template

Use for: `build_error`, `test_failure`, `runtime_error`, `performance_issue`, `database_issue`, `security_issue`, `ui_bug`, `integration_issue`, `logic_error`

```markdown
---
title: [Clear problem title]
date: [YYYY-MM-DD]
category: [category/]
module: [Module or area]
problem_type: [schema enum]
component: [Component]
severity: [critical|high|medium|low]
tags: [keyword-one, keyword-two]
---

# [Clear problem title]

## Problem
[1-2 sentence description]

## Symptoms
- [Observable symptom]

## What Didn't Work
- [Failed attempts]

## Solution
[The fix that worked, with code snippets]

## Why This Works
[Root cause explanation]

## Prevention
- [Concrete practice or guardrail]
```

## Knowledge Track Template

Use for: `best_practice`, `documentation_gap`, `workflow_issue`, `developer_experience`, `architecture_pattern`, `design_pattern`, `tooling_decision`, `convention`

```markdown
---
title: [Clear title]
date: [YYYY-MM-DD]
category: [category/]
module: [Module or area]
problem_type: [schema enum]
component: [Component]
severity: [critical|high|medium|low]
applies_when:
  - [Condition where this applies]
tags: [keyword-one, keyword-two]
---

# [Clear title]

## Context
[What situation prompted this guidance]

## Guidance
[The practice or recommendation with examples]

## Why This Matters
[Rationale and impact]

## When to Apply
- [Conditions or situations]

## Examples
[Concrete before/after or usage examples]
```
