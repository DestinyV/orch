# 关键文件 — plugin-capability-optimization

## 本需求关键文件（code-architect 追加）

### 修改（含精确位置）

| 文件 | 位置 | 改动 |
|------|------|------|
| scripts/lib/stage-contracts.js | 新建 | STAGE_ORDER/STAGE_OUTPUTS/SKILL_PREREQUISITES/EXEMPT_SKILLS/EXEMPT_COMMANDS 集中导出 |
| scripts/hooks/workflow-gate.js | :39-44, :88-99, :112 | require stage-contracts；STAGE_OUTPUTS 补 3.5/5/6/9；validateOutputs(stage,reqId,state) 处理 completion-report；stdin 超时 |
| scripts/hooks/stage-gate.js | :27-79, :99-104, :163-177 | require stage-contracts；EXEMPT 命令名分离；stdin 复用 stdin.js 2s 超时 fail-open |
| scripts/hooks/session-start.js | :12-29 | 自动补偿：last_done→next_stage→前置产出检查→缺失清单/resume 建议 |
| scripts/hooks/observe.js | 新建 | instinct 观察事件追加 ~/.claude/orch-instincts/observations.jsonl，fail-open |
| scripts/hooks/observe.sh | 新建 | POSIX 薄包装 exec node observe.js |
| scripts/sync-prompt-defense.py | :23-30 | 幂等：count=0 清除 + 孤儿头清理 + 单点插入 |
| scripts/lib/verdict.js | 新建 | judgeCoverage/judgeRate/judgeAutoResolve |
| scripts/self-check.js | 新建 | 5 块自检（orchestration/agents/skills/tdd_loop/commands_hooks） |
| hooks/hooks.json | PreToolUse | 注册 suggest-compact(Edit\|Write, id pre:compact) + observe(pre/post:observe) |
| commands/self-check.md | 新建 | /self-check 命令入口 |
| agents/code-architect.md | :19, :68/81 | project-map.json；编号 0-4 连续 |
| agents/tasker.md | :13, :24 | project-map.json；GATE 降级为建议 |
| agents/conversation-analyzer.md | :4, :25-27 | 去 /hookify；Prompt Defense 去重（随 T2.3） |
| agents/tdd-guide.md | 头部 | deprecated 横幅 + 边界注记 |
| AGENTS.md | 头部+扩展表 | 25→26；注册 tdd-guide（deprecated 标注） |
| skills/design/SKILL.md | :45 | project-map.json |
| skills/workflow/references/agent-dispatch-code.md | :125, :182 | project-map.json；tdd-guide deprecated 注记 |
| skills/workflow/references/flow-execution-reference.md | :35 | tdd-guide deprecated 注记 |
| skills/execute/SKILL.md | :56 | context-inheritance-protocol.md |
| skills/spec/SKILL.md | :194 | ../design/references/diagram-trigger-rules.md |
| skills/cost/SKILL.md | :177-182 | 补 `<GATE>` |
| skills/using-orch/SKILL.md | :87-96 | 22 skill 索引 |
| skills/continuous-learning/config.json | :4 | observer.enabled=true |
| skills/{16 核心}/SKILL.md | frontmatter | description 补 TRIGGER when |
| CLAUDE.md | 钩子系统表+数量 | 8 个脚本双向一致 |
| README.md / .claude-plugin/README.md | 头部 | 22/26/14、/start-dev |
| orch-spec/context/file-map.yaml / index.json | 全文 | 目录/章节同步 |
| .gitignore | 新建 | __pycache__/ + *.pyc |
| tests/hooks-smoke.test.js | 新建 | Node 冒烟 |
| tests/test-suite.py | 追加 | GATE/引用/hooks/observer/pyc 检查 |
| spec/business-rules.md | 追加 | 北极星审查结论表 |

### 测试对齐（test-designer 产物）

| 文件 | 说明 |
|------|------|
| orch-spec/plugin-capability-optimization/tests/test-spec.md | 47 个 TC，设计已逐项对齐 |
| orch-spec/plugin-capability-optimization/tests/fixtures.json | 有效/边界/特殊值，设计取值完全一致 |
