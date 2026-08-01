# 架构决策记录 — plugin-capability-optimization

| ADR | 决策 | 理由 | 状态 |
|-----|------|------|------|
| ADR-001 | tdd-guide 保留文件 + 注册 AGENTS.md + 标注 deprecated + 划清与 code-reviewer 边界 | S4-Case2 四阶段校验机制仍以 tdd-guide 命名；fixtures 要求 {registered:true, deprecated:true, count:26} 三态并存 | accepted |
| ADR-002 | 阶段契约集中化：新建 scripts/lib/stage-contracts.js，workflow-gate/stage-gate/session-start 共用 STAGE_ORDER/STAGE_OUTPUTS/SKILL_PREREQUISITES/EXEMPT_* | F10 根因为两处阶段映射独立维护不对称；集中化消除漂移，支撑 S1"与 stage-gate 对称" | accepted |
| ADR-003 | instinct observer 激活（方案A）：implement observe.js + observe.sh wrapper + hooks.json 注册 + config.json enabled=true，不清理死配置 | 元任务目标含自主进化能力优化；北极星主张能力最大化；fixtures/TC 指向激活态 | accepted |
| ADR-004 | 自检入口 = Node 脚本 scripts/self-check.js + commands/self-check.md；plugin.json 命令目录自动发现，不改 manifest | 复用 hooks Node 基础设施；business-rules 约束2 禁止 manifest 声明 hooks/agents，命令目录自动注册 | accepted |
| ADR-005 | 北极星审查：start-dev.md:12 与 tasker.md:24 判定为 cage，降级为建议；其余 GATE 判定 guardrail 保留 | 两约束限制探索自由且为 token 时代残留；本需求明确不关注 token（规则4） | accepted |
| ADR-006 | STAGE_OUTPUTS[9] 用项目级相对路径 '../context/learnings.md' + 伪产出 'completion-report'（validateOutputs 改查 state.completion_report_generated） | continuous-learning 写项目级 context；path.join 天然归一化 '..'；completion 报告为状态标志非文件 | accepted |
| ADR-007 | sync-prompt-defense.py 改为"全量清除已有节再单次插入" | 原 re.sub count=1 只替换首匹配，重复节清不净（F5 根因）；幂等需 count=0 清除 + 孤儿头清理 | accepted |
| ADR-008 | 判定函数集中为 scripts/lib/verdict.js（judgeCoverage/judgeRate/judgeAutoResolve） | 支撑 TC-S4-03/04、TC-S6-02..07 行为断言；覆盖率以实测为准不接受自我报告（S4-Case3） | accepted |
