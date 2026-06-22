# 命名规范与约定

## 文件命名
- Skills: `skills/{skill-name}/SKILL.md`
- Agents: `agents/{agent-name}.md`
- Commands: `commands/{command-name}.md`
- 技能目录名: 单数/动词（spec, design, execute, debug）

## 输出目录
- 工作流输出: `orch-spec/{req_id}/`
- 规范: `orch-spec/{req_id}/spec/`
- 设计: `orch-spec/{req_id}/design/`
- 上下文: `orch-spec/{req_id}/req-context/`
- 主规范: `orch-spec/spec/`
- 项目上下文注册中心: `orch-spec/context/`

## 模板格式
- SKILL.md frontmatter: name + description
- Agent frontmatter: name + description + tools + model
- Command frontmatter: name + description + argument-hint

## Git
- Conventional Commit: `<type>(<scope>): <description>`
- Git Trailers: Constraint / Rejected / Directive / Spec / HARD-GATE

## 代理约束
- 所有 agents 使用 `model: inherit`（继承会话模型，无 thinking 参数冲突）
- HARD-GATE 格式: `<HARD-GATE>...</HARD-GATE>`
- 出口验证: `- [ ] 检查项`
