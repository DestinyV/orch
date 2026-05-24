# orch Full-Stack SDD-TDD Development Workflow

[中文](./README_ZH.md) | English

![overview](./docs/img/overview.png)

**Quick Navigation**:
- 📖 [Usage Guide](./docs/USAGE_EN.md) - Detailed usage scenarios and steps
- 🛠️ [Best Practices](./docs/BEST_PRACTICES_EN.md) - Core principles and best practices
- 📚 [Complete Case Studies](./docs/USAGE.md) - Real project case studies
- 💻 [Skills Documentation](./skills/README_EN.md) - 9 Skills workflow documentation
- 🔧 [Installation Guide](./docs/INSTALLATION_EN.md) - Installation and troubleshooting
- 🏗️ [Technical Guide](./CLAUDE.md) - Claude architecture and design principles
- 🔀 **[Git-Worktrees Guide](./skills/execute/git-worktrees-guide.md)** - execute isolated work environment guide
- ⚡ **[Worktrees Quick Reference](./skills/execute/QUICK_REFERENCE.md)** - Daily use quick reference card

## 📌 Overview

**orch** is an enterprise-grade Claude Code plugin providing a **complete full-stack development workflow** with AI assistance. Through 11 professional skills covering the full lifecycle from requirements to archive, it helps teams quickly establish specification frameworks, conduct design planning, define test standards, decompose tasks, generate code with exception handling, verify functionality, and archive specifications. Supports frontend, backend, database, mobile, microservices, and other project types.

**Workflow**:
```
/start "需求" → /spec (Spec) → /test-design (Test Spec) ⟷ /design (Design) → /contract (Contract) → /task (Task) → /execute (Coding) → /exception (Exception) → /test (Testing) → /archive (Archive) → Complete
```

> `/test-design` and `/design` can be executed in parallel (both depend on spec output).
> `/exception` triggers automatically for backend/fullstack projects after code-execute (zero hardcoding, project convention scanning).

---

## ✨ Core Features

### 🎯 Spec-Driven Development (SDD)
- ✅ Define full-stack design specifications and reference implementations (frontend, backend, database, etc.)
- ✅ Reference implementations serve as architecture and code standards
- ✅ AI generates designs and code based on specifications
- ✅ Supports multiple tech stacks (React/Vue, Node.js/Python/Go/Java, PostgreSQL/MongoDB, etc.)

### 📋 Complete Workflow
- ✅ **Spec Stage**: Define design specifications (with TEST-VERIFY + Mock Data)
- ✅ **Design Stage**: Requirements analysis + solution design
- ✅ **Test-Design Stage**: Generate test specs, fixtures, and test templates from TEST-VERIFY
- ✅ **Task Stage**: Task decomposition + checklist definition
- ✅ **Execute Stage**: TDD code generation + multi-stage review
- ✅ **Test Stage**: High-level testing + closed-loop verification

### 🔄 Quality Assurance Mechanisms
- ✅ Spec Review: Ensure code conforms to specifications
- ✅ Quality Review: Ensure code quality standards
- ✅ TDD Implementation: RED-GREEN-REFACTOR-REVIEW four-stage TDD process
- ✅ Test Coverage: Unit tests ≥80%, full integration/E2E/performance testing
- ✅ Closed-Loop Verification: Ensure TEST-VERIFY→Test→Code→Result complete correspondence

### ⚡ Ready to Use
- ✅ Interactive questionnaire guidance (supports multiple tech stack selection)
- ✅ Automatic generation of design specifications and task checklists
- ✅ Comprehensive usage instructions and best practices
- ✅ Supports frontend, backend, database, microservices, and other project types

---

## 📦 Included 11 Skills

| Skill | Stage | Function | Output |
|-------|-------|----------|--------|
| **scripts** | Utility | 工具优先策略：Grep/Bash/Glob/Edit 优先完成文件搜索/提取/编辑/校验，仅脚本无法处理时兜底Read | 脚本化文件操作 |
| **workflow** | Orchestrator | 统一入口+流程编排：自动检测模式、串联9个Skill、HARD-GATE卡点、中断恢复 | .workflow-state.json + 全流程自动执行 |
| **spec** | Spec | Requirements analysis and spec generation, outputs BDD format spec documents (WHEN-THEN format) | spec-dev/{requirement_desc_abstract}/spec/ |
| **test-design** | Test-Design | Generate test specs, fixtures, and test templates from TEST-VERIFY | test-spec.md + fixtures.json + test-*.template |
| **design** | Design | Code design planning based on specs, generates architecture and technical solutions | spec-dev/{requirement_desc_abstract}/design/design.md |
| **contract** | Api-Contract | Interface contract definition and review (fullstack mandatory) | contract.md + review-report.md |
| **task** | Task | Converts designs to code-level task lists, supports frontend, backend, database, microservice tasks | spec-dev/{requirement_desc_abstract}/tasks/tasks.md |
| **execute** | Execute | Task execution via sub-agents, supports multi-language multi-framework, two-stage review (spec + quality), TDD process with unit tests. **v2.3.1+**: Uses git-worktree to create isolated work environments for each Task, ensuring safety, debugability, and recoverability of fix cycles | src/ + spec-dev/{requirement_desc_abstract}/execution/execution-report.md |
| **exception** | Exception | Exception scene recognition + project convention scanning + exception code generation (backend/fullstack, zero hardcoding) | src/** (with exception handling) |
| **test** | Test | High-level testing (Integration/E2E/Performance) and closed-loop verification | tests/ + spec-dev/{requirement_desc_abstract}/testing/testing-report.md |
| **archive** | Archive | Spec archiving and optimization, merges requirement specs into main spec library through scenario splitting | spec-dev/spec/ (merged main spec) |

Detailed documentation: [View skills documentation](./skills/README_EN.md)

## 🤖 Core Agents

orch includes 9 professional Agents that collaborate across various Skills:

| Agent | Responsibility | Use Cases |
|-------|---------------|-----------|
| **code-architect** | Analyzes existing codebase patterns and conventions to design functional architecture and provide complete implementation blueprints | design stage: analyzes project structure, extracts design patterns, plans architecture |
| **code-explorer** | Deep analysis of existing code implementations by tracing execution paths, mapping architecture layers, and identifying design patterns | spec and design stages: extracts architecture conventions and identifies reusable code |
| **code-executor** | Writes high-quality code based on detailed implementation tasks with TDD (RED-GREEN-REFACTOR-REVIEW) | execute stage: each Task dispatched as independent subagent in isolated git-worktree |
| **code-reviewer** | Reviews for bugs, logic errors, security vulnerabilities, and code quality issues with confidence-based filtering (≥80) | execute stages 3.3/3.4 and test stage 2: spec review + quality review |
| **archiver** | Spec archiving expert: benchmark analysis, conflict detection, smart merging, consistency verification | archive stage: dispatched for scenario comparison, merging, and consistency checks |
| **test-designer** | Converts TEST-VERIFY into test cases, defines Mock strategies, generates fixtures and test framework code | test-design stage: analyzes scenarios, designs test cases, generates test templates |
| **exception** | Project convention scanning + exception scenario identification + exception code generation with zero hardcoding | execute stage: auto-triggered for backend/fullstack Tasks to add exception handling |
| **contract-creator** | Interface contract definition and six-dimension review (completeness/naming/types/errors/conventions/database) | contract stage: fullstack mandatory, generates contract docs and review reports |
| **tasker** | Design→task decomposition + dependency analysis + parallel execution planning with Test Case mapping | task stage: decomposes design into executable tasks with dependency DAG |

---

## 🚀 Quick Start

### Prerequisites
- Claude Code installed

### Installation
```bash
1. Open Claude
2. Add marketplace: /plugin -> Marketplaces -> +Add Marketplace ->
3. Paste https://github.com/DestinyV/orch.git
4. Install plugin: /plugin -> Marketplaces -> DestinyV-marketplace Enter to select -> Browse plugins -> orch Enter to install
```

---

## 🌐 Multi-Platform Support

The SDD+TDD workflow skills are designed to be **platform-agnostic**. While primarily developed for Claude Code, the workflow concepts and skill definitions can be adapted to multiple AI coding platforms:

| Platform | Support Level | Notes |
|----------|--------------|-------|
| **Claude Code** | ✅ Full | Native skill support, full workflow |
| **OpenAI Codex** | ✅ Adaptable | Skills via context injection; see [Codex Tools Mapping](./skills/using-superpowers/references/codex-tools.md) |
| **GitHub Copilot CLI** | ✅ Adaptable | Skills via context injection; see [Copilot Tools Mapping](./skills/using-superpowers/references/copilot-tools.md) |
| **Cursor** | ✅ Adaptable | Skill content can be loaded via context prompts |
| **Gemini CLI** | ✅ Adaptable | Skills via context injection; see [Gemini Tools Mapping](./skills/using-superpowers/references/gemini-tools.md) |
| **OpenCode** | ✅ Adaptable | Skills via context injection; see [OpenCode Tools Mapping](./skills/using-superpowers/references/opencode-tools.md) |

### How Multi-Platform Works

1. **Skill Format**: All skills are defined in standard Markdown (`.md`) files with clear instructions
2. **Context Injection**: Skills can be injected as system prompts or context into any AI coding tool
3. **Tool Mapping**: Reference the `using-superpowers/references/` directory for tool mappings between platforms
4. **Workflow Portability**: The 9-stage workflow (Spec → Test-Design → Design → Api-Contract → Task → Execute → Exception-Handler → Test → Archive) is tool-agnostic and can be manually executed on any platform

### Using Skills on Other Platforms

```
# Example: Loading a skill context in any AI tool
1. Read the SKILL.md file content
2. Paste as system prompt or initial context
3. Follow the workflow steps manually
4. Reference tool mappings for platform-specific commands
```

### Platform-Specific Adaptations

- **Claude Code**: Native `/skill` commands, automatic discovery
- **Codex**: Use `spawn_agent` for sub-agent patterns, native skill discovery
- **Copilot**: Use `task` for sub-agent patterns, context injection for skills
- **Cursor**: Use chat context to load skill definitions
- **Other platforms**: Paste skill content as initial context/system prompt

For detailed tool mappings, see the `skills/using-superpowers/references/` directory.

### Usage Workflow

#### Step 0: Enter Plugin (User Action)

```bash
/orch:sdd-dev

Enter requirements as prompted
```

---

#### Step 1: Requirements Specification (User Action)

```bash
/spec
```

Interactive dialogue with the plugin for requirements analysis and confirmation:
1. Requirements analysis and initial decomposition
2. Scenario refinement and multi-round confirmation
3. Generate BDD format specifications

Output: `spec-dev/{requirement_desc_abstract}/spec/` directory
- requirement.md (Requirements document overview - **entry file**)
- scenarios/*.md (BDD scenarios - WHEN-THEN format)
- data-models.md (Data model definitions)
- business-rules.md (Business rules and constraints)
- glossary.md (Glossary)

---

#### Steps 2-7: Automatic Execution (No User Intervention Required)

After spec confirmation, subsequent steps will **execute automatically**:

**Step 2: Test Design** (Automatic, parallel with Step 3)
- Reads TEST-VERIFY and Mock Data from spec
- Generates test specifications, fixtures, and test templates
- Output: `spec-dev/{requirement_desc_abstract}/tests/` (test-spec.md + fixtures.json + test-*.template)

**Step 3: Code Design** (Automatic, parallel with Step 2)
- Reads spec documents, assigns code-architect to analyze project
- Generates design solution: `spec-dev/{requirement_desc_abstract}/design/design.md`

**Step 3.5: Api-Contract** (Automatic, fullstack only)
- Defines interface contract and conducts five-dimension review
- Output: `spec-dev/{requirement_desc_abstract}/contract/`

**Step 4: Task List** (Automatic)
- Automatically decomposes tasks based on design solution
- Generates task checklist: `spec-dev/{requirement_desc_abstract}/tasks/tasks.md`

**Step 5: Code Execution** (Automatic)
- Assigns sub-agents to each Task for parallel implementation
- **v2.3.1+**: Creates independent git worktree for each Task, isolating work environments
  - Coding and fixes all performed within worktree
  - Failed fixes can delete worktree and restart
  - Worktree commit history clearly records fix process
  - Supports cherry-pick or squash merge submission approaches
- Conducts multi-stage review (spec review + quality review)
- TDD process: RED-GREEN-REFACTOR-REVIEW
- Generates execution report: `spec-dev/{requirement_desc_abstract}/execution/execution-report.md`
- Outputs source code to `src/` directory

**Step 5.5: Exception Handling** (Automatic, backend/fullstack)
- Scans project conventions for exception patterns
- Auto-identifies exception scenarios and generates handling code
- Zero hardcoding: all conventions discovered through scanning

**Step 6: Test Verification** (Automatic)
- Conducts code quality review and high-level testing (Integration/E2E/Performance)
- Generates test reports and closed-loop verification matrix
- Generates test report: `spec-dev/{requirement_desc_abstract}/testing/testing-report.md`
- Outputs test code to `tests/` directory

**Step 7: Spec Archiving** (Automatic)
- Automatically triggers spec archiving process after all tests pass
- Assigns archiver for benchmark analysis and smart merging
- Integrates requirement specs into main spec library through scenario splitting
- Generates archive report: `spec-dev/spec/archive-log.md`
- Updates main specs: `spec-dev/spec/` (data-models, business-rules, glossary, etc.)

---

#### Overall Workflow Time Estimation

| Stage | Input | Output | Time |
|-------|-------|--------|------|
| Spec | Requirements description | spec/ | User interaction |
| Design | spec/ | design.md | Automatic |
| Task | design.md | tasks.md | Automatic |
| Execute | tasks.md | src/ + execution report | Automatic |
| Test | tasks.md | tests/ + test report | Automatic |
| Archive | spec/ | spec-dev/spec/ + archive report | Automatic |

Total time: Specification stage depends on user interaction, subsequent full workflow executes automatically (typically 2-5 minutes)

---

## 📖 Complete Documentation

- [Installation Guide](./docs/INSTALLATION_EN.md) - Detailed installation steps and troubleshooting
- [Usage Guide](./docs/USAGE_EN.md) - Detailed usage methods and common scenarios
- [Best Practices](./docs/BEST_PRACTICES_EN.md) - Full-stack SDD best practices and checklists

---

## 💡 Usage Examples

### Scenario 1: React Project - New Order Form

```bash
# 0. Enter plugin
/orch:sdd-dev
# Input requirements: Need to add order form to order management system, supporting search, sort, pagination, batch operations

# 1. Analyze requirements and generate spec
/spec
# Output: spec-dev/order-form/spec/ (requirement.md, scenarios/*.md, data-models.md, etc.)

# 2. Architecture design based on spec
/design Need to add order form
# Output: spec-dev/order-form/design/design.md

# 3. Decompose design into specific tasks
/task spec-dev/order-form/design/design.md
# Output: spec-dev/order-form/tasks/tasks.md

# 4. Execute code implementation (with two-stage review)
/execute spec-dev/order-form/tasks/tasks.md
# Output: src/... + spec-dev/order-form/execution/execution-report.md

# 5. Test verification and closed-loop check
/test spec-dev/order-form/tasks/tasks.md
# Output: tests/... + spec-dev/order-form/testing/testing-report.md
```

### Scenario 2: Vue Project - New Dashboard Component

```bash
# 0. Enter plugin
/orch:sdd-dev
# Input requirements: Need to create data dashboard supporting real-time data, multi-chart display, custom panels

# 1. Analyze requirements and generate spec
/spec
# Output: spec-dev/dashboard/spec/ (requirement.md, scenarios/*.md, etc.)

# 2. Architecture design based on spec
/design Need to create data dashboard
# Output: spec-dev/dashboard/design/design.md

# 3. Decompose design into specific tasks
/task spec-dev/dashboard/design/design.md
# Output: spec-dev/dashboard/tasks/tasks.md

# 4. Execute code implementation
/execute spec-dev/dashboard/tasks/tasks.md
# Output: src/... + spec-dev/dashboard/execution/execution-report.md

# 5. Test verification and closed-loop check
/test spec-dev/dashboard/tasks/tasks.md
# Output: tests/... + spec-dev/dashboard/testing/testing-report.md
```

---

## 🎯 Workflow Diagram

```
┌──────────────────────────────────────────────────────────┐
│  Step 0: /orch:sdd-dev Enter plugin            │
│  - Enter requirements as prompted                        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 1: /spec Requirements Analysis & Spec      │
│  - Analyze requirements and initial decomposition        │
│  - Scenario refinement and multi-round confirmation      │
│  - Output: spec-dev/{name}/spec/                          │
│    (requirement.md, scenarios/*.md, data-models.md, etc.) │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 2: /design Architecture & Technical Design   │
│  - Assign code-architect to analyze project patterns     │
│  - Conduct architecture design and technical planning    │
│  - Output: spec-dev/{name}/design/design.md               │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 3: /task Task Decomposition & Definition       │
│  - Decompose design into coding tasks                     │
│  - Define goals, deliverables, acceptance criteria        │
│  - Output: spec-dev/{name}/tasks/tasks.md                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  🔍 User Review and Confirmation                          │
│  - Review design solution and task list                   │
│  - Confirm and proceed to Execute stage                   │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 4: /execute Code Implementation & Review       │
│  - Assign code-executor sub-agents for each Task          │
│  - **v2.3.1+**: Create git-worktree isolated environments │
│    • Coding and fixes performed in worktree              │
│    • Each fix as independent commit for tracking          │
│    • Cherry-pick/squash merge to main after completion   │
│    • Clean up worktree to free resources                  │
│  - Spec review: Verify code conforms to design.md         │
│  - Quality review: Check code quality and type safety     │
│  - Output: src/ + execution-report.md                     │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 5: /test Testing & Closed-Loop Verification    │
│  - Code quality review (Lint, TypeScript strict check)    │
│  - Design and execute unit, integration, E2E tests        │
│  - Closed-loop verification (Task-Code-Test correspondence)│
│  - Output: tests/ + testing-report.md                     │
└────────────────┬─────────────────────────────────────────┘
                 │
      ✅ All tests pass, automatically triggers
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 6: /archive Spec Archiving & Optimization      │
│  - Assign archiver for spec benchmark analysis       │
│  - Integrate into main spec through scenario splitting    │
│  - Conflict detection and decision handling               │
│  - Output: spec-dev/spec/ + archive-report.md             │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  ✅ Complete!                                             │
│  - Code quality meets standards, ready for release        │
│  - Specs accumulated to enterprise spec library           │
│  - Available for future requirement reference             │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Core Principles

### ✅ Must Do
- Step 0: Use `/orch:sdd-dev` to enter plugin and input requirements
- Step 1: Run spec for requirements analysis and spec generation
- Step 2: Assign code-architect for architecture design in design stage
- Step 3: Conduct task decomposition and definition in code-task stage
- Step 4: Strictly follow task checklist for code-execute, complete spec + quality two-stage review
- Step 5: Conduct comprehensive test verification and closed-loop check
- Step 6: Automatically execute archive after tests pass, accumulate specs to enterprise spec library

### ❌ Must Not Do
- Skip Step 0 and directly call individual Skills (should use plugin entry)
- Skip design and task definition stages and directly code
- Skip spec or quality reviews in code-execute
- Modify source code logic to make tests pass
- Ignore consistency between Tasks and code
- Skip closed-loop verification in test stage
- Skip spec archiving process, preventing spec library improvement

---

## 🤝 How to Customize Workflow

Skills may have context, background, or dependency bindings with projects, so this suite of skills may not perfectly fit your scenario.

### Adjust Design and Specifications

Modify the SKILL.md files in the following Skills to adapt to your project requirements:

1. **spec** - Define project design patterns and reference component collection methods
2. **design** - Adjust design analysis dimensions and depth
3. **code-task** - Adjust task decomposition granularity and acceptance criteria

### Adjust Execution and Review

Modify prompt files in code-execute:

- `implementer-prompt.md` - Adjust code implementation style and requirements
- `spec-reviewer-prompt.md` - Adjust spec review dimensions
- `code-quality-reviewer-prompt.md` - Adjust code quality standards

### Adjust Testing Strategy

Modify test SKILL.md:

- Adjust test frameworks and tools
- Adjust test coverage requirements
- Adjust closed-loop verification standards

---

## 📝 Changelog

### v2.3.1 (2026-03-23) ✨ Git-Worktrees Isolated Work Environments
- ✅ **Worktree Isolation Mechanism** - Creates independent git worktree for each Task in code-execute
- ✅ **Safe Fix Cycle** - Failed fixes can delete worktree and restart without polluting main branch
- ✅ **Complete Fix History** - Worktree commits clearly record "problem→fix→verification" chain
- ✅ **Parallel Task Support** - Multiple Tasks execute simultaneously without git conflict risk
- ✅ **Worktree Guide** - New 465-line complete Worktree workflow guide (git-worktrees-guide.md)
- ✅ **Quick Reference Card** - QUICK_REFERENCE.md for daily use and reference
- ✅ **Implementation Summary** - IMPLEMENTATION_SUMMARY.md shows full scope of improvements
- ✅ **Constraint Updates** - New 8 key constraints + new 4 danger signals

### v2.3.0 (2026-03-23) ✨ Complete TDD Implementation
- ✅ **TDD Implementation System** - Complete Phase 2 TDD implementation (RED-GREEN-REFACTOR-REVIEW)
- ✅ **High-Level Testing System** - Complete Phase 3 integration, E2E, performance testing optimization
- ✅ **Clear Responsibilities** - code-execute handles unit tests, test handles high-level tests
- ✅ **High-Level Test Prompts** - Integration, E2E, performance test specialized design guides
- ✅ **Best Practices Update** - BEST_PRACTICES.md adds Phase 3 best practices
- ✅ **Closed-Loop Verification** - Complete TEST-VERIFY→Test→Code→Result chain

### v2.2.0 (2026-03-20)
- ✅ **Spec Archiving** - New archive skill and archiver Agent
- ✅ **Spec Accumulation** - Automatically archive verified requirement specs to enterprise main spec library
- ✅ **Scenario Splitting** - Support integration of new specs through scenario splitting and smart merging
- ✅ **Conflict Detection** - Automatic detection and handling of spec conflicts with decision suggestions
- ✅ **Spec Benchmark Analysis** - New benchmark analysis for scenarios, data models, business rules, terminology
- ✅ **Version Management** - Support spec version tracking and evolution history

### v2.1.0 (2026-03-10)
- ✅ **Full-Stack Development** - Extended support for frontend, backend, database, microservices, mobile
- ✅ **Tech Stack Expansion** - Node.js, Python, Go, Java, PostgreSQL, MongoDB, etc.
- ✅ **Database Design** - SQL/NoSQL data model design and migration scripts
- ✅ **API Design** - REST/GraphQL API specifications and validation
- ✅ **Microservices Support** - Service boundaries, communication protocols, deployment solutions
- ✅ **Multi-Framework Testing** - Jest, Pytest, JUnit, Cypress, k6, etc.
- ✅ **Complete Examples** - Full-stack examples and best practices

### v2.0.0 (2026-03-09)
- ✅ Complete refactoring to Spec-Design-TestDesign-Task-Execute-Test-Archive workflow
- ✅ 7 Core Skills: spec, design, test-design, code-task, code-execute, test, archive
- ✅ Multi-stage review mechanism and closed-loop verification
- ✅ Frontend-first support (React/Vue/Angular/Svelte)
- ✅ Complete documentation and best practices guides

### v1.0.0 (2026-02-09)
- Initial version with spec-generator, ai-planning, ai-code-execution, ai-test-creation

---

## 🎓 Learning Path

### Beginner
1. Read this README.md to understand the entire workflow
2. View [Usage Guide](./docs/USAGE_EN.md)
3. Execute `/orch:sdd-dev` to enter plugin
4. Enter requirements as prompted
5. Step through spec → design → test-design → code-task → code-execute → test → archive
6. Choose a small feature for complete workflow trial run

### 📚 Advanced Learning
1. Understand the 9 steps and 9 Agents in [Quick Start](#-quick-start)
2. Read [Best Practices](./docs/BEST_PRACTICES_EN.md) to learn best practices for each stage
3. Read [Usage Guide](./docs/USAGE_EN.md) for detailed workflow
4. Learn [Git-Worktrees Guide](./skills/execute/references/git-worktrees-guide.md) to master isolated work environments
   - Learn worktree creation, coding, fixing, merging, cleanup lifecycle
   - View real application scenarios and parallel Task management
   - Reference [Quick Reference](./skills/execute/references/quick-reference.md) for daily queries

### Team Adoption
1. Ensure team members understand SDD workflow core principles
2. Write project-specific design specs (through spec)
3. Write team best practices and coding style guides
4. Configure code-execute and test review rules
5. Train team members to use the entire workflow according to specs
6. Establish spec-design based code review process

---

## 📧 Contact

- 📖 [Documentation](./docs/)
- 🐛 [Bug Reports](https://github.com/your-org/orch-plugin/issues)
- 💬 [Discussions](https://github.com/your-org/orch-plugin/discussions)

---

## 📄 License

MIT License - See [LICENSE](./LICENSE)

---

## 🙏 Acknowledgments

This workflow is based on SDD (Spec-Driven Development) principles, combined with:
- Claude Code's AI capabilities
- Enterprise development best practices
- Frontend engineering lessons learned

Thanks to all contributors and users for their support!

---

**Make AI-assisted full-stack development standardized, efficient, and reliable!** 🚀
