---
description: 代码审查 — 本地未暂存变更或 GitHub PR。使用 code-reviewer agent 执行两阶段审查（规范审查 + 质量审查）。
argument-hint: "[pr-number | pr-url | blank for local review]"
---

# Code Review (SDD+TDD 适配版)

> 调用 `code-reviewer` agent 执行两阶段审查：**规范审查**（是否符合 design.md 架构约定） + **质量审查**（类型/安全/性能/最佳实践）。

**输入**: $ARGUMENTS

---

## 模式选择

如果 `$ARGUMENTS` 包含 PR number、PR URL 或 `--pr`：
→ **PR Review Mode**

否则：
→ **Local Review Mode**

---

## 本地审查模式

### Phase 1 — GATHER

```bash
git diff --name-only HEAD
```

如无变更，停止："Nothing to review."

### Phase 2 — DISPATCH REVIEWER

派遣 `code-reviewer` agent 执行审查：

```bash
Agent(
  subagent_type="orch:code-reviewer",
  prompt="执行两阶段审查。第一阶段：规范审查 — 检查代码是否符合 design.md 架构约定。第二阶段：质量审查 — 类型检查、安全审计、性能分析、最佳实践检查。使用置信度评分（≥80 才报告）。"
)
```

### Phase 3 — TWO-STAGE REVIEW

#### 第一阶段：规范审查

检查代码是否符合 SDD+TDD 设计的架构约定：

- 引用 `orch-spec/{req}/design/design.md` 中的关键架构决策
- **组件一致性**：是否按设计实现了关键模块
- **命名规范**：文件/函数/类型命名是否符合规范
- **结构合规**：目录结构、模块划分是否与设计一致
- **接口对齐**：API 签名、数据模型是否与设计一致

#### 第二阶段：质量审查

**Security Issues (CRITICAL):**
- 硬编码凭据、API key、token
- SQL 注入、XSS 漏洞
- 缺少输入验证
- 不安全的依赖
- Path traversal

**Code Quality (HIGH):**
- 函数 > 50 行
- 文件 > 800 行
- 嵌套深度 > 4 级
- 缺少错误处理
- console.log 残留
- TODO/FIXME 注释
- 缺少公开 API 的 JSDoc

**Best Practices (MEDIUM):**
- 可变模式检查（优先不可变）
- 代码/注释中的 emoji 使用
- 新代码缺少测试
- 可访问性问题（a11y）

### Phase 4 — CONFIDENCE FILTER

遵循 code-reviewer agent 的置信度评分规则：

| 分值 | 含义 |
|------|------|
| 0-24 | 完全不确定，不报告 |
| 25-49 | 不确定，不报告（可能风格问题） |
| 50-79 | 中等确定，仅标记（不阻断） |
| 80-100 | 高度确定，必须报告 |

**仅报告置信度 ≥ 80 的问题。**

### Phase 5 — REPORT

```
## 规范审查结果
- [PASS/FAIL] 架构一致性
- [PASS/FAIL] 命名规范
- [PASS/FAIL] 结构合规
- [PASS/FAIL] 接口对齐

## 质量审查结果
### CRITICAL
<findings or "None">

### HIGH
<findings or "None">

### MEDIUM
<findings or "None">

Decision: APPROVE | REQUEST CHANGES | BLOCK
```

CRITICAL 或 HIGH 问题阻断提交。安全漏洞绝不批准。

---

## PR 审查模式

### Phase 1 — FETCH PR

```bash
gh pr view <NUMBER> --json number,title,body,author,baseRefName,headRefName,changedFiles,additions,deletions
gh pr diff <NUMBER>
```

### Phase 2 — CONTEXT

1. 读取项目规范：`CLAUDE.md`, `orch-spec/{req}/design/design.md`
2. 审查工件：检查 `.claude/prds/`, `.claude/plans/`, `.claude/reviews/`
3. PR 意图：解析 PR description 中的目标、关联 issue、测试计划
4. 变更分类：按类型分组（source, test, config, docs）

### Phase 3 — REVIEW

读取每个变更文件的完整内容（不仅仅是 diff hunk）。应用7维度检查清单：

| 维度 | 检查项 |
|------|--------|
| **Correctness** | 逻辑错误、off-by-one、null 处理、边界情况、竞态条件 |
| **Type Safety** | 类型不匹配、不安全转换、`any` 滥用、缺少泛型 |
| **Pattern Compliance** | 匹配项目约定（命名、文件结构、错误处理、导入） |
| **Security** | 注入、认证缺口、密钥暴露、SSRF、path traversal、XSS |
| **Performance** | N+1 查询、缺少索引、无限循环、内存泄漏、大 payload |
| **Completeness** | 缺少测试、缺少错误处理、不完整迁移、缺少文档 |
| **Maintainability** | 死代码、魔法数字、深层嵌套、不明确命名、缺少类型 |

### Phase 4 — VALIDATE

```bash
# 根据项目类型运行
npm run typecheck 2>/dev/null || npx tsc --noEmit     # TypeScript
npm run lint 2>/dev/null || npm test                   # Lint + Tests
npm run build 2>/dev/null                              # Build
```

### Phase 5 — DECIDE

| 条件 | 决策 |
|------|------|
| 零 CRITICAL/HIGH + 验证通过 | **APPROVE** |
| 仅 MEDIUM/LOW + 验证通过 | **APPROVE** with comments |
| 任何 HIGH 或验证失败 | **REQUEST CHANGES** |
| 任何 CRITICAL | **BLOCK** |

### Phase 6 — PUBLISH

```bash
gh pr review <NUMBER> --approve/--request-changes/--comment --body "<summary>"
```

---

## 边界情况

- **无 `gh` CLI**: 降级为本地审查，跳过 GitHub 发布。警告用户。
- **分支分歧**: 审查前建议 `git fetch origin && git rebase origin/<base>`。
- **大 PR (>50 文件)**: 警告审查范围。优先关注 source 变更，然后是测试，最后是配置/文档。
