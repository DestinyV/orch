#!/usr/bin/env python3
"""Batch patch all SKILL.md files with missing sections"""
import os, re

ROOT = r"E:\YYWorkSpace\projects\sdd-tdd-dev"

# (relpath, anchor_text, content_to_insert_before_anchor)
patches = [
    # HIGH
    ("skills/continuous-agent-loop/SKILL.md", "## 循环选择流程",
     "## When to Use\n\n- 需要循环执行的任务场景（批量处理、持续集成/PR 控制）\n- 需要 RFC 分解的大功能\n- 探索性并行生成（多种方案比较）\n\n## How It Works\n\n从 4 种循环模式中选择：sequential（顺序执行） / continuous-pr（CI门控） / rfc-dag（DAG拓扑排序） / infinite（探索性并行）。\n每循环有明确退出条件和质量门控。\n\n"),
    ("skills/cost-tracking/SKILL.md", "## 先决条件",
     "## When to Use\n\n- 用户询问\"花费了多少\"、\"这个会话花了多少钱\"、\"Token用量\"\n- 需要按项目/工具/日期查看成本分析\n\n## How It Works\n\n查询本地 SQLite 数据库 `~/.claude-cost-tracker/usage.db`，通过 sqlite3 执行聚合查询。\n优先使用 `cost_usd` 列（source of truth），不手动计算价格。\n\n"),
    ("skills/knowledge-continuum/SKILL.md", "## 双架构概览",
     "## When to Use\n\n- 工作流归档完成后自动触发（post-spec-archive）\n- 需要从工作流中提取模式、沉淀知识\n- 需要查看或管理 instincts（原子学习单元）\n\n## How It Works\n\n双架构并行：\n- Layer 1（Workflow Knowledge）：工作流结束后，从 .workflow-eval.json 提取决策数据，匹配 patterns/，更新 preferences/\n- Layer 2（Instinct Learning）：通过 hook 实时观察会话，自动创建原子 instincts 并置信度评分\n\n"),
    ("skills/script-writer/SKILL.md", "## 职责",
     "## When to Use\n\n- 需要进行文件搜索、批量处理、内容提取、格式校验时\n- 优先用脚本批量处理而非逐个 Read 文件\n- 简单查询用 Grep/Bash，复杂逻辑用 Python3\n\n## Output\n\n脚本输出结果（不加载整个文件到上下文）。\n\n"),
    ("skills/strategic-compact/SKILL.md", "## 何时建议 Compact",
     "## When to Use\n\n- 会话接近上下文限制（200K+ tokens）\n- 多阶段任务切换（研究 -> 计划 -> 实现 -> 测试）\n- 完成主要里程碑后开始新工作\n- 响应变慢或变得不连贯（上下文压力）\n\n## How It Works\n\n在逻辑边界建议手动 /compact，替代任意的自动 compaction。\n通过 PreToolUse(Edit/Write) 钩子追踪工具调用次数，达到阈值时触发建议。\n\n"),
    ("skills/trace/SKILL.md", "## 工作流程",
     "## When to Use\n\n- code-test 阶段测试失败，需要定位根因\n- Bug 报告需要多假设竞争式因果追踪\n- 需要区分症状和根因\n\n"),
    ("skills/using-orch/SKILL.md", "## 规则",
     "## When to Use\n\n- 首次使用 orch 插件\n- 不确定应该调用哪个 Skill\n- 需要了解各 Skill 的触发条件和用途\n\n## How It Works\n\n本技能是 orch 的入口导航，列出所有可用 Skills 及其触发条件。\n不执行具体工作流操作，仅提供索引和指引。\n\n## Output\n\nSkill 列表和触发条件说明。\n\n## Constraints\n\n- 不执行任何工作流操作\n- 仅提供索引信息\n\n"),
    # MEDIUM
    ("skills/api-contract/SKILL.md", "## 职责",
     "## When to Use\n\n- fullstack 模式下 code-design 阶段完成\n- 需要将 design.md 中的接口定义转化为正式契约文档\n- 需要审查接口命名/类型/错误处理的一致性\n\n## Output\n\n- `api-contract/api-contract.md` — 接口契约文档\n- `api-contract/review-report.md` — 六维度审查报告\n\n"),
    ("skills/code-test/SKILL.md", "## 职责",
     "## When to Use\n\n- code-execute 完成，需要执行高层测试（集成/E2E/性能）\n- 需要进行闭环验证（TEST-VERIFY -> Test -> Code -> Result）\n- 需要生成测试报告\n\n## Output\n\n- `tests/` — 集成/E2E/性能测试代码\n- `testing/testing-report.md` — 验证矩阵 + 测试结果\n\n"),
    ("skills/socratic-clarify/SKILL.md", "## 职责",
     "## When to Use\n\n- 需求描述模糊/开放/不确定时\n- 用户说\"我不太确定具体要什么\"\n- 需求不包含具体文件路径、函数名或验收标准\n\n## Output\n\n- `spec-dev/{req_id}/spec/clarification.md` — 苏格拉底澄清报告\n\n"),
    ("skills/spec-creation/SKILL.md", "## Phase 0: 苏格拉底澄清检测（前置）",
     "## When to Use\n\n- 收到新需求描述\n- 需要将模糊需求转化为 BDD 规范文档\n- 需要生成 TEST-VERIFY 和 Mock Data\n\n## Output\n\n- `spec-dev/{req_id}/spec/` — 完整规范目录（requirement.md + scenarios/*.md + data-models.md + business-rules.md + glossary.md）\n\n"),
    ("skills/test-design/SKILL.md", "## 职责",
     "## When to Use\n\n- spec-creation 已完成，需要将 TEST-VERIFY 转化为测试用例\n- 需要生成 fixtures 和测试框架代码\n\n"),
    ("skills/workflow-control/SKILL.md", "## 职责",
     "## When to Use\n\n- 新需求入口\n- 需要自动编排从需求到归档的完整流程\n- 需要中断恢复、状态追踪、效果评估\n\n"),
]

for relpath, anchor, insert in patches:
    fp = os.path.join(ROOT, relpath)
    content = open(fp, encoding="utf-8").read()
    if anchor not in content:
        print(f"SKIP {relpath}: anchor not found")
        continue
    if "## When to Use" in content and "When" in insert:
        print(f"SKIP {relpath}: already has When to Use")
        continue
    new_content = content.replace(anchor, insert + anchor, 1)
    if new_content != content:
        open(fp, "w", encoding="utf-8").write(new_content)
        print(f"OK   {relpath}")

# Append Output/Constraints for files that need them at the end
appends = {
    "skills/context-budget/SKILL.md": """

## Output

Context Budget Report — 包含组件开销分解、问题清单、Top 优化建议。

## Constraints

- 不读取实际文件内容（仅统计大小）
- 不修改任何配置（仅报告）
- 标记问题但不下结论（保留用户判断权）
""",
    "skills/token-budget-advisor/SKILL.md": """

## Output

按用户选择的深度级别提供的回答（25% Essential / 50% Moderate / 75% Detailed / 100% Exhaustive）。

## Constraints

- 用户指定深度后立即响应，不再提问
- 会话内保持同一级别
- 不估算实际模型定价（由 cost-tracking 负责）
- 不读取文件内容（只基于启发式估算）
""",
    "skills/trace/SKILL.md": """

## Constraints

- 不直接修改代码（仅分析）
- 每个假设必须有正反证据
- 输出必须包含具体的验证步骤
""",
    "skills/continuous-agent-loop/SKILL.md": """

## Output

选定循环模式后的执行结果。

## Constraints

- 每循环必须有明确退出条件
- 失败必须可检测且可阻断
- 循环必须有进展指标（不空转）
- 不允许无限制循环（必须有硬限制）
- 不允许静默失败（每轮必须验证）
""",
    "skills/strategic-compact/SKILL.md": """

## Output

compact 建议提示（不修改文件，仅输出建议）。

## Constraints

- 仅在逻辑边界提出建议，不强制
- 实现中途不 compact（丢失关键状态的风险）
- 不自动执行 compact（用户决定）
""",
    "skills/cost-tracking/SKILL.md": """

## Output

成本查询结果（今日/总计/按项目/按工具/按日期的 SQL 查询输出）。

## Constraints

- 优先使用 `cost_usd` 列（source of truth）
- 数据库不存在时不编造数据
- 不硬编码模型定价
""",
}

for relpath, append in appends.items():
    fp = os.path.join(ROOT, relpath)
    content = open(fp, encoding="utf-8").read()
    section_name = append.strip().split("\n")[0].strip()
    if section_name in content:
        print(f"SKIP {relpath}: already has {section_name}")
        continue
    content += append
    open(fp, "w", encoding="utf-8").write(content)
    print(f"OK   {relpath} (append)")

print("\nDone")
