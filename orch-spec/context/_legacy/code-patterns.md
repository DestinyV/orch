# 代码模式

## Skill 模式
- 每个 Skill 对应一个工作流阶段（职责单一）
- skill 内 `SKILL.md` 含: 做什么 / 为什么 / 验证
- 具体代码由 references/ 或 agents/ 负责，不在 skill 内写执行代码

## Agent 模式
- 每个 Agent 一个 `.md` 文件，frontmatter + markdown 内容
- Agent prompt 定义在 dispatch 时传入，不在 agent 文件内硬编码
- 优先 `model: inherit`，无思考参数冲突风险

## 上下文模式
- 五步检索: project-context → 历史 spec → req-context → AI 知识库/项目 wiki → 项目探索
- 需求级上下文: req-context/ 在步骤1 生成，各阶段逐步填充
- 项目级上下文: archive 步骤6 同步沉淀

## 脚本优先策略
- 简单查询: Grep/Bash
- 批量处理: Python3 脚本
- 兜底: Read（大模型直接读取）
