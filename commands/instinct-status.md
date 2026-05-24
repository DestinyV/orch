---
name: instinct-status
description: 展示当前项目的 instinct（项目级 + 全局），按领域分组，显示置信度和观察统计。
---

# Instinct Status Command (SDD+TDD 适配版)

显示 SDD+TDD 知识复利引擎 v2（continuous-learning）已学习的 instincts，包含项目级和全局，按领域分组。

## 实现

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" status
```

或通过知识复利引擎的 homunculus 目录直接读取：
- 项目级：`~/.local/share/knc-homunculus/projects/{project-id}/instincts/`
- 全局级：`~/.local/share/knc-homunculus/instincts/`

## 用法

```
/instinct-status
/instinct-status --verbose      # 显示完整 instinct 内容和观察历史
/instinct-status --domain testing  # 仅显示 testing 领域
/instinct-status --min-confidence 0.7  # 仅显示置信度 ≥ 0.7
```

## 输出格式

```
==============================================================
  INSTINCT STATUS - orch v2
==============================================================

  Project: my-project (a1b2c3d4e5f6)
  Project instincts: 8
  Global instincts:  4
  Total: 12

## PROJECT-SCOPED (my-project)
### TESTING (3)
  ███████░░░  70%  test-fixtures-before-mock [project]
            trigger: when writing test files
  █████████░  90%  coverage-threshold-85 [project]
            trigger: when execute completes

### WORKFLOW (2)
  █████░░░░░  50%  spec-first-approach [project]
            trigger: when starting new feature

## GLOBAL (all projects)
### SECURITY (2)
  ██████████  95%  validate-user-input [global]
            trigger: when handling user input
### CODE-STYLE (2)
  ██████░░░░  60%  prefer-named-exports [global]
            trigger: when creating modules
```

## 集成

SDD+TDD 的 instinct 系统通过以下方式学习：
- **Hook 观察**：`hooks/observe.sh` 在 PreToolUse/PostToolUse 时捕获行为模式
- **会话提炼**：`execute` 和 `test` 执行后自动沉淀经验
- **知识复利**：`continuous-learning` 在 `archive` 后自动循环提炼

显示当前活跃的 instinct 快照。
