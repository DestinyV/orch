#!/usr/bin/env python3
"""Batch patch all agent files with missing standard sections"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (filename, anchor, content_to_insert)
patches = [
    ("api-contract-creator.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:contract-creator\", prompt=\"...\")` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:contract-creator\",\n  prompt=\"将 design.md 中的接口定义转化为接口契约文档，执行六维度审查\"\n)\n```\n\n## 输出\n\n- `contract.md` — 接口契约文档\n- `review-report.md` — 六维度审查报告\n\n"),
    ("code-architect.md", "## 核心流程",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:code-architect\", prompt=\"...\")` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:code-architect\",\n  prompt=\"对需求进行架构蓝图分析，输出 design.md\"\n)\n```\n\n## 约束\n\n<HARD-GATE>禁止跳过 project-context.md 直接设计 | 设计必须覆盖所有 spec 场景</HARD-GATE>\n\n"),
    ("code-executor.md", "## 核心流程",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:executor\", prompt=\"...\", run_in_background=true)` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:executor\",\n  prompt=\"实现 Task-N，遵循 TDD 流程 (RED-GREEN-REFACTOR-REVIEW)\"\n)\n```\n\n"),
    ("code-explorer.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:code-explorer\", prompt=\"扫描 src/ 提取架构模式\", run_in_background=true)` 派遣。\n\n## 工作流程\n\n1. 接收扫描目标（目录/模式/关键词）\n2. 使用工具优先策略搜索（Grep > Python3 > Read）\n3. 汇总结果返回\n\n"),
    ("code-reviewer.md", "## 多视角审查方法",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:code-reviewer\", prompt=\"...\")` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:code-reviewer\",\n  prompt=\"对 src/ 执行两阶段审查（规范+质量）\"\n)\n```\n\n## 约束\n\n<HARD-GATE>standard 模式必须通过 Agent 派遣 | confidence < 80 的问题不报告</HARD-GATE>\n\n"),
    ("code-tasker.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:tasker\", prompt=\"...\")` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:tasker\",\n  prompt=\"将 design.md 拆解为可执行 Task 清单\"\n)\n```\n\n## 约束\n\n<HARD-GATE>每个 Task 必须有 provides/consumes 声明 | 依赖关系必须无环（DAG）</HARD-GATE>\n\n"),
    ("code-tester.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:tester\", prompt=\"...\", run_in_background=false)` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:tester\",\n  prompt=\"执行高层测试（集成/E2E/性能）并返回测试报告\"\n)\n```\n\n"),
    ("exception-handler.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:exception\", prompt=\"...\")` 在 code-execute 内部自动触发。\n\n```\nAgent(\n  subagent_type=\"orch:exception\",\n  prompt=\"扫描 src/ 识别异常场景并生成异常处理代码\"\n)\n```\n\n"),
    ("knowledge-curator.md", "## 核心原则",
     "## 角色\n\n知识复利引擎执行专家。执行知识识别到沉淀到提炼到刷新到自适应全流程。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:knowledge-curator\", prompt=\"执行知识复利流程\", run_in_background=false)` 派遣。\n\n## 输出\n\n- `patterns/pattern-index.json` — 更新频次和最后使用时间\n- `patterns/*.md` — 更新历史教训\n- `user-preferences/preferences.json` — 更新 always_check\n\n"),
    ("spec-archiver.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:archiver\", prompt=\"...\")` 派遣。\n\n```\nAgent(\n  subagent_type=\"orch:archiver\",\n  prompt=\"将测试通过的规范归档到主规范库\"\n)\n```\n\n## 输出\n\n- `spec-dev/spec/archive-log.md` — 归档日志\n\n## 约束\n\n<HARD-GATE>全部测试通过后才允许归档 | 冲突时需用户确认合并策略</HARD-GATE>\n\n"),
    ("socratic-clarifier.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:clarifier\", prompt=\"...\")` 在 scoring 时调用。\n\n## 工作流程\n\n1. 读取访谈记录\n2. 评分各维度清晰度\n3. 提取本体实体\n4. 返回 JSON 评分结果\n\n## 约束\n\n<HARD-GATE>必须使用 Opus 模型 | temperature 必须为 0.1 | 必须输出 JSON 格式</HARD-GATE>\n\n"),
    ("test-designer.md", "## 工作流程",
     "## 角色\n\n测试设计专家。从 TEST-VERIFY 生成测试用例、fixtures 和测试框架代码。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:test-designer\", prompt=\"...\", run_in_background=true)` 派遣。\n\n## 输出\n\n- `tests/test-spec-creation.md` — 测试规范\n- `tests/fixtures.json` — 测试数据\n- `tests/test-*.template` — 测试框架代码\n\n## 约束\n\n<HARD-GATE>每条 TEST-VERIFY 必须映射到至少一个测试用例 | fixtures.json 必须可解析</HARD-GATE>\n\n"),
    ("test-verifier.md", "## 职责",
     "## 调用方式\n\n通过 `Agent(subagent_type=\"orch:test-verifier\", prompt=\"...\")` 派遣。\n\n## 工作流程\n\n1. 读取验收标准清单\n2. 确定每条标准的证据级别\n3. 独立运行验证命令\n4. 输出结构化验证报告\n\n"),
    ("tracer.md", "## 核心方法",
     "## 角色\n\n因果追踪专家。通过多假设竞争式分析定位根因。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:debug\", prompt=\"分析 Bug 根因\")` 派遣。\n\n## 约束\n\n<HARD-GATE>至少生成 2 个竞争假设 | 每个假设必须有正反证据 | 必须有收敛或分离判断</HARD-GATE>\n\n"),
    ("workflow-control.md", "## 职责",
     "## 调用方式\n\n通过 `Skill(\"orch:workflow\", args=\"{requirement_desc}\")` 调用（不是 Agent 派遣）。\n\n## 输出\n\n- `.workflow-state.json` — 状态追踪\n- `.workflow-eval.json` — 效果评估 + Token 用量\n\n## 约束\n\n<HARD-GATE>禁止跳过阶段 | 禁止在正式流程前执行代码探索</HARD-GATE>\n\n"),
]

# ECC-imported agents that need Role/How/Out/Gates/Call from scratch
ecc_agents = {
    "code-simplifier.md": "## 角色\n\n代码简化专家。通过重构简化复杂代码，保持功能不变。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:code-simplifier\", prompt=\"简化代码\")` 派遣。\n\n## 输出\n\n简化后的代码（通过 Edit/Write 输出）。\n\n## 约束\n\n<HARD-GATE>不能改变代码功能 | 不能删除错误处理 | 必须保持测试通过</HARD-GATE>\n\n",
    "comment-analyzer.md": "## 角色\n\n代码注释分析专家。评估注释的准确性、完整性和可维护性。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:comment-analyzer\", prompt=\"分析注释质量\")` 派遣。\n\n## 输出\n\n注释分析报告（过时/冗余/缺失/误导性注释清单）。\n\n## 约束\n\n<HARD-GATE>只分析注释，不分析代码逻辑 | 不修改代码</HARD-GATE>\n\n",
    "conversation-analyzer.md": "## 角色\n\n对话分析专家。从会话中提取模式和见解。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:conversation-analyzer\", prompt=\"分析本次会话中的决策模式\")` 派遣。\n\n## 输出\n\n对话分析报告（决策点/模式/异常）。\n\n## 约束\n\n<HARD-GATE>不保留个人身份信息 | 仅提取可复用的模式</HARD-GATE>\n\n",
    "doc-updater.md": "## 角色\n\n文档更新专家。根据代码变更同步更新文档。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:doc-updater\", prompt=\"更新与变更相关的文档\")` 派遣。\n\n## 输出\n\n更新后的文档文件。\n\n## 约束\n\n<HARD-GATE>不修改代码 | 文档变更必须与代码变更对应</HARD-GATE>\n\n",
    "e2e-runner.md": "## 角色\n\nE2E 测试执行专家。运行端到端测试并验证浏览器行为。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:e2e-runner\", prompt=\"执行 @e2e 测试并报告结果\")` 派遣。\n\n## 输出\n\nE2E 测试结果报告（通过/失败/截图）。\n\n## 约束\n\n<HARD-GATE>必须使用 Playwright | 0 failures 才能声明通过</HARD-GATE>\n\n",
    "harness-optimizer.md": "## 角色\n\n工作流调优专家。分析工作流执行数据并优化配置。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:harness-optimizer\", prompt=\"分析 .workflow-eval.json 并提供优化建议\")` 派遣。\n\n## 输出\n\n优化建议报告。\n\n## 约束\n\n<HARD-GATE>只读不写 | 不修改工作流配置</HARD-GATE>\n\n",
    "loop-operator.md": "## 角色\n\n自主循环操作专家。管理循环执行、监视停滞、介入干预。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:loop-operator\", prompt=\"执行批量处理循环\")` 派遣。\n\n## 输出\n\n循环执行报告（每轮结果/状态/退出原因）。\n\n## 约束\n\n<HARD-GATE>必须有退出条件 | 停滞超时自动上报</HARD-GATE>\n\n",
    "planner.md": "## 角色\n\n实现规划专家。将需求转化为可执行的实施计划。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:planner\", prompt=\"制定实现计划\")` 派遣。\n\n## 输出\n\n实施计划（步骤/文件/依赖/验收标准）。\n\n## 约束\n\n<HARD-GATE>计划必须可执行 | 每步必须有验收标准</HARD-GATE>\n\n",
    "pr-test-analyzer.md": "## 角色\n\nPR 测试分析专家。评估 PR 的测试覆盖充分性。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:pr-test-analyzer\", prompt=\"分析 PR 的测试覆盖\")` 派遣。\n\n## 输出\n\n测试覆盖分析报告。\n\n## 约束\n\n<HARD-GATE>只分析不修改 | 覆盖率不达标必须标记</HARD-GATE>\n\n",
    "refactor-cleaner.md": "## 角色\n\n代码清理专家。识别并移除死代码和冗余逻辑。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:refactor-cleaner\", prompt=\"清理死代码\")` 派遣。\n\n## 输出\n\n清理后的代码（通过 Edit/Write 输出）。\n\n## 约束\n\n<HARD-GATE>不能删除有引用的代码 | 必须编译通过</HARD-GATE>\n\n",
    "silent-failure-hunter.md": "## 角色\n\n静默失败检测专家。识别被静默吞噬的错误和异常。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:silent-failure-hunter\", prompt=\"检测代码中的静默失败\")` 派遣。\n\n## 输出\n\n静默失败报告（位置/类型/修复建议）。\n\n## 约束\n\n<HARD-GATE>只报告不修改 | 必须标注置信度</HARD-GATE>\n\n",
    "spec-creation.md": "## 角色\n\n规范生成专家。通过交互式问卷生成 BDD 规范文档。\n\n## 调用方式\n\n通过 `Skill(\"orch:spec\", args=\"{requirement}\")` 调用（不是 Agent 派遣）。\n\n## 输出\n\n`spec-dev/{req_id}/spec/` — 完整规范目录。\n\n## 约束\n\n<HARD-GATE>每个场景至少 1 个异常 Case | standard 模式必须有 TEST-VERIFY</HARD-GATE>\n\n",
    "tdd-guide.md": "## 角色\n\nTDD 流程引导专家。确保遵循 RED-GREEN-REFACTOR-REVIEW 循环。\n\n## 调用方式\n\n通过 `Agent(subagent_type=\"orch:tdd-guide\", prompt=\"引导 TDD 流程\")` 派遣。\n\n## 输出\n\nTDD 流程状态报告（各阶段日志）。\n\n## 约束\n\n<HARD-GATE>不能跳过 RED 阶段 | 覆盖率不能低于 85%</HARD-GATE>\n\n",
}

# Apply ECC patches (insert after frontmatter)
for fname, insert in ecc_agents.items():
    fp = os.path.join(ROOT, "agents", fname)
    content = open(fp, encoding="utf-8").read()
    if "## 角色" in content:
        print(f"SKIP {fname}: already has Role")
        continue
    parts = content.split("---", 2)
    if len(parts) >= 3:
        new_content = parts[0] + "---" + parts[1] + "---\n\n" + insert + parts[2].lstrip()
        open(fp, "w", encoding="utf-8").write(new_content)
        print(f"OK   {fname}")
    else:
        print(f"SKIP {fname}: no frontmatter")

# Apply regular patches
for fname, anchor, insert in patches:
    fp = os.path.join(ROOT, "agents", fname)
    content = open(fp, encoding="utf-8").read()
    if anchor not in content:
        print(f"SKIP {fname}: anchor not found")
        continue
    new_content = content.replace(anchor, insert + anchor, 1)
    if new_content != content:
        open(fp, "w", encoding="utf-8").write(new_content)
        print(f"OK   {fname}")
    else:
        print(f"SKIP {fname}: no change")

print("\nDone")
