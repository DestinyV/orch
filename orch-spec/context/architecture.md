# 架构

## 整体分层

```
├── skills/          # 22 个 Skills（工作流核心单元）
├── agents/          # 26 个 Agents（子代理派遣）
├── commands/        # 14 个斜杠命令
├── hooks/           # 钩子注册表（SessionStart/PreCompact/Stop）
├── scripts/         # 运行时脚本（hooks + lib）
├── config/          # 项目栈配置
├── schemas/         # JSON Schema（工作流状态/评估）
├── docs/            # 文档
├── references/      # 多平台工具映射
├── rules/           # 代码规则（common/typescript/python/zh）
└── orch-spec/       # 工作流输出目录
    ├── context/     # 项目级上下文注册中心
    ├── spec/        # 主规范库
    └── {req_id}/    # 各需求目录
```

## 工作流编排

```
/start-dev → Skill("orch:workflow")
  → clarify (可选)
  → spec (三层上下文检索)
  → test-design + design（并行）
  → contract (fullstack)
  → task
  → execute (TDD)
  → test (集成/E2E/性能)
  → archive (合并到主规范 + 同步上下文)
  → evaluation (三维度九指标)
  → continuous-learning (四维沉淀)
```

## 上下文双层次

- **项目级** `orch-spec/context/` — 跨需求持久，Layer 1 按关键词匹配
- **需求级** `orch-spec/{req_id}/req-context/` — 单次工作流，阶段间传递

## 平台适配

多平台：Claude Code / Cursor / Gemini CLI / OpenCode / Codex / CodeBuddy
