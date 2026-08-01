# 术语表（主规范库）

> 本文件汇总各需求归档的术语。新增术语以 `|` 行追加。
>
> 首个归档来源：plugin-capability-optimization（插件本体全方位能力优化）。

| 术语 | 全称 | 说明 |
|------|------|------|
| orch | Orchestra | 本插件，SDD+TDD 工作流编排 |
| SDD | Spec-Driven Development | 规范驱动开发，一切从 spec 开始 |
| TDD | Test-Driven Development | 测试驱动开发，RED→GREEN→REFACTOR→REVIEW |
| GATE | HARD-GATE | 硬性门禁，`<GATE>...</GATE>` 标记的最强阶段纪律 |
| 北极星原则 | North Star Principle | 约束=护栏非牢笼，不限制模型能力（本次最高原则） |
| 规则自决 | Rule-Based Auto-Resolve | 可裁决错误自动补偿（重试/补建/降级） |
| 白名单人工 | Whitelist Manual | 特定场景暂停等人工（需求冲突/验收不确定/HARD-GATE/跨仓库） |
| 自动流转率 | Auto-flow Rate | 不依赖人工干预的流程段占比，验收 ≥80% |
| 产出达标率 | Output Pass Rate | 二次审查达标通过率，验收 ≥90% |
| 容错自动恢复率 | Auto-recovery Rate | 中断/失败后无需人工介入的恢复率，验收 ≥80% |
| 验证闭环 | Verification Loop | 5 大块均有可运行验证用例或自检命令 |
| P0/P1/P2 | Priority Level | 探索审计的问题优先级（P0 最严重） |
| F1-F12 | Findings | 探索 C 发现的 12 项薄弱环节 |
| project-map | Project Map | 结构化项目地图 JSON，供下游阶段复用 |
| req-context | Requirement Context | 需求级上下文（单次工作流生命周期） |
| context/ | Project Context | 项目级上下文（跨需求持久） |
| frontmatter | Front Matter | Markdown 文件头部 YAML 元数据 |
| observer | Instinct Observer | instinct 学习层的会话观察（hook 级） |
| tdd-guide | TDD Guide Agent | 孤立 agent（职责被 code-reviewer 吸收） |
| STAGE_OUTPUTS | Stage Outputs | workflow-gate.js 的阶段产出校验表 |
| EXEMPT_SKILLS | Exempt Skills | stage-gate.js 的豁免 Skill 表 |
| meta-task | 元任务 | 本次需求：优化插件自身（非用户应用） |
